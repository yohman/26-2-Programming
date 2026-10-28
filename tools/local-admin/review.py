#!/usr/bin/env python3
"""Local-only submission index, isolated notebook replay and loopback review server.

Run using admin/.venv/bin/python tools/local-admin/review.py --serve
Never modifies student originals. Private replays live in ignored admin/_review;
explicitly hearted notebook exports are published separately to submissions/gallery.json.
"""
import argparse
import ast
import contextlib
import csv
import hashlib
import html
import io
import inspect
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unicodedata
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[2]
ADMIN = ROOT / 'admin'
OUTPUT = ADMIN / '_review'
UI = Path(__file__).parent
LOCK = threading.Lock()
API_CACHE = OUTPUT / 'api-cache'
PUBLIC_APIS = {
    'api.open-meteo.com': ('/v1/forecast',),
    'archive-api.open-meteo.com': ('/v1/archive',),
    'rss.applemarketingtools.com': ('/api/v2/',),
    'itunes.apple.com': ('/search',),
    'jsonplaceholder.typicode.com': ('/posts', '/users', '/todos'),
    'pokeapi.co': ('/api/v2/pokemon/', '/api/v2/type/', '/api/v2/pokemon-form/'),
    'ja.wikipedia.org': ('/api/rest_v1/page/summary/',),
}


def public_api(url):
    if not isinstance(url, str) or len(url) > 3000:
        return False
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError:
        return False
    return (parsed.scheme == 'https' and port in {None, 443}
            and not parsed.username and not parsed.password and not parsed.fragment
            and any(parsed.path.startswith(prefix) for prefix in PUBLIC_APIS.get(parsed.hostname, ()))
            and not re.search(r'(?:key|token|secret|password|email)=', parsed.query, re.I))


def api_urls(notebook):
    """Resolve only literal URL construction. Never execute submitted code here."""
    urls, values = set(), {}
    def value(node, env):
        if isinstance(node, ast.Constant): return node.value
        if isinstance(node, ast.Name): return env[node.id]
        if isinstance(node, ast.Dict): return {value(k, env): value(v, env) for k, v in zip(node.keys, node.values)}
        if isinstance(node, (ast.List, ast.Tuple)): return [value(v, env) for v in node.elts]
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add): return value(node.left, env) + value(node.right, env)
        if isinstance(node, ast.JoinedStr): return ''.join(str(value(v.value, env)) if isinstance(v, ast.FormattedValue) else v.value for v in node.values)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            args = [value(v, env) for v in node.args]
            if node.func.id == 'urlencode': return urlencode(*args)
            if node.func.id == 'quote': return quote(*args)
            if node.func.id == 'range' and all(isinstance(v, int) for v in args):
                result = range(*args)
                if len(result) <= 500: return list(result)
        raise ValueError('Not a literal expression')
    def scan(nodes, env):
        for node in nodes:
            if isinstance(node, ast.Assign):
                try:
                    resolved = value(node.value, env)
                    for target in node.targets:
                        if isinstance(target, ast.Name): env[target.id] = resolved
                except (ValueError, KeyError, TypeError): pass
            if isinstance(node, ast.For) and isinstance(node.target, ast.Name):
                try:
                    items = value(node.iter, env)
                    if len(items) <= 500:
                        for item in items: scan(node.body, dict(env, **{node.target.id: item}))
                except (ValueError, KeyError, TypeError): pass
                continue
            for item in ast.walk(node):
                candidate = item if isinstance(item, ast.JoinedStr) else item.args[0] if isinstance(item, ast.Call) and item.args and (getattr(item.func, 'id', '') in {'urlopen', 'Request', 'get_json'} or getattr(item.func, 'attr', '') == 'urlopen') else None
                if candidate is not None:
                    try:
                        url = value(candidate, env)
                        if public_api(url): urls.add(url)
                    except (ValueError, KeyError, TypeError): pass
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') != 'code': continue
        try: scan(ast.parse('\n'.join(line for line in source(cell).splitlines() if not line.lstrip().startswith(('%', '!')))).body, values)
        except (SyntaxError, RecursionError): pass
    return sorted(urls)[:500]


def cache_api(url):
    """Trusted GET fetcher with an explicit host/path allowlist and no redirects."""
    from urllib.request import build_opener, HTTPRedirectHandler
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs): return None
    path = API_CACHE / (hashlib.sha256(url.encode()).hexdigest() + '.json')
    if path.exists(): return json.loads(path.read_text())
    if not public_api(url): return None
    try:
        request = Request(url, headers={'User-Agent': 'ProgrammingCourseLocalReview/1.0', 'Accept': 'application/json'})
        with build_opener(NoRedirect).open(request, timeout=12) as response:
            raw = response.read(4_000_001)
            if len(raw) > 4_000_000: return None
            data = json.loads(raw)
        record = {'url': url, 'fetched_at': datetime.now().astimezone().isoformat(), 'data': data}
        path.write_text(json.dumps(record, ensure_ascii=False))
        return record
    except (OSError, ValueError): return None


def source(cell):
    value = cell.get('source', '')
    return ''.join(value) if isinstance(value, list) else value


def worker(job):
    """Runs only inside the OS sandbox, with per-cell guards and time limits."""
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (25, 25))
    payload = json.loads(Path(job).read_text())
    namespace = {'__name__': '__main__'}
    results = []
    allowed = {'csv', 'folium', 'branca', 'pandas', 'numpy', 'datetime', 'json', 'math', 'pathlib', 'IPython', 'urllib', 'matplotlib', 'zoneinfo', 'uuid', 'ipywidgets'}
    # urllib can only return pre-fetched, allowlisted JSON. The OS sandbox still denies network.
    import urllib.request
    def cached_urlopen(request, *args, **kwargs):
        url = request.full_url if isinstance(request, urllib.request.Request) else str(request)
        record = payload.get('api_responses', {}).get(url)
        if record is None:
            raise OSError('No approved cached response for this URL; network remains disabled.')
        return io.BytesIO(json.dumps(record['data'], ensure_ascii=False).encode())
    urllib.request.urlopen = cached_urlopen
    # Capture common display()/IFrame outputs without starting a Jupyter kernel.
    import types
    import base64
    def embed_local_images(markup):
        def replace(match):
            src = html.unescape(match.group(2))
            if urlsplit(src).scheme or src.startswith('//'): return match.group(0)
            path = (Path.cwd() / unquote(src)).resolve()
            if not path.is_relative_to(Path.cwd()) or path.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.gif', '.webp'}: return match.group(0)
            if not path.is_file(): return '<span style="color:#777">画像未提出：' + html.escape(src) + '</span>'
            mime = 'jpeg' if path.suffix.lower() in {'.jpg', '.jpeg'} else path.suffix[1:].lower()
            return match.group(0).replace(match.group(1) + match.group(2) + match.group(1), '"data:image/' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode() + '"', 1)
        return re.sub(r'<img\b[^>]*\bsrc\s*=\s*([\"\x27])(.*?)\1[^>]*>', replace, str(markup), flags=re.I)
    display_module = types.ModuleType('IPython.display')
    class LocalHTML:
        def __init__(self, data='', **kwargs): self.data = data
        def _repr_html_(self): return embed_local_images(self.data)
    class LocalImage:
        def __init__(self, data=None, url=None, filename=None, **kwargs):
            self.data, self.url, self.filename = data, url, filename
        def _repr_html_(self):
            import base64
            if self.filename:
                path = Path(self.filename).resolve()
                if not path.is_relative_to(Path.cwd()): raise PermissionError('Only local job images are supported.')
                data = path.read_bytes()
            elif isinstance(self.data, bytes): data = self.data
            else: return '<p>Remote image not replayed; see submitted HTML output.</p>'
            return '<img alt="Notebook image" src="data:image/png;base64,' + base64.b64encode(data).decode() + '">'
    class LocalFrame:
        def __init__(self, src, **kwargs):
            self.src = src
        def _repr_html_(self):
            path = Path(unquote(urlsplit(str(self.src)).path)).resolve()
            if not path.is_relative_to(Path.cwd()) or path.suffix.lower() != '.html':
                raise PermissionError('Only generated local HTML frames are supported.')
            return path.read_text()
    def display(*values):
        for value in values:
            if hasattr(value, '_repr_html_'):
                result['outputs'].append({'output_type': 'display_data', 'data': {'text/html': value._repr_html_()}})
            else:
                result['outputs'].append({'output_type': 'display_data', 'data': {'text/plain': repr(value)}})
    display_module.display, display_module.IFrame, display_module.HTML = display, LocalFrame, LocalHTML
    display_module.Image = LocalImage
    namespace['display'] = display
    # A bounded offline adapter, not a live Jupyter widget kernel. Each choice
    # runs inside the same OS sandbox, then switches pre-rendered HTML locally.
    widgets = types.ModuleType('ipywidgets')
    class LocalDropdown:
        def __init__(self, options=(), value=None, description='', **kwargs):
            items = list(options.items()) if isinstance(options, dict) else list(options)
            if not items or len(items) > 20: raise ValueError('Offline dropdown supports 1–20 choices.')
            self.options = [(str(item[0]), item[1]) if isinstance(item, (tuple, list)) and len(item) == 2 else (str(item), item) for item in items]
            self.value = value if value is not None else self.options[0][1]
            self.description = description
    def local_interact(function, **controls):
        if len(controls) != 1 or not isinstance(next(iter(controls.values())), LocalDropdown):
            raise PermissionError('Offline widget preview supports one Dropdown only.')
        name, control = next(iter(controls.items()))
        options, panels = [], []
        for index, (label, value) in enumerate(control.options):
            start = len(result['outputs'])
            try:
                function(**{name: value})
                outputs = result['outputs'][start:]
                content = ''.join(o.get('data', {}).get('text/html', '') for o in outputs)
                if not content: content = '<pre>' + html.escape(str(outputs)) + '</pre>'
            except Exception as error:
                content = '<p>' + html.escape(type(error).__name__ + ': ' + str(error)) + '</p>'
            finally:
                del result['outputs'][start:]
            selected = value == control.value
            options.append('<option value="' + str(index) + '"' + (' selected' if selected else '') + '>' + html.escape(label) + '</option>')
            panels.append('<section data-widget-choice="' + str(index) + '"' + ('' if selected else ' hidden') + '>' + content + '</section>')
        markup = '<div><label style="display:block;margin:12px 0;font:16px sans-serif">' + html.escape(control.description) + ' <select onchange="this.closest(\'div\').querySelectorAll(\'[data-widget-choice]\').forEach(p=>p.hidden=p.dataset.widgetChoice!==this.value)">' + ''.join(options) + '</select></label>' + ''.join(panels) + '</div>'
        result['outputs'].append({'output_type': 'display_data', 'metadata': {'local_widget_preview': True}, 'data': {'text/html': markup}})
        result['message'] = 'Dropdown choices pre-rendered in the offline sandbox; this is a local reconstruction, not saved student output.'
    widgets.Dropdown, widgets.interact = LocalDropdown, local_interact
    sys.modules['ipywidgets'] = widgets
    # Jupyter exposes display() globally. Resolve Windows-only absolute paths
    # solely to an exact-name attachment already copied into this student's job.
    import builtins
    def local_open(file, *args, **kwargs):
        if isinstance(file, str) and re.match(r'^[A-Za-z]:[\\/]', file):
            candidate = Path.cwd() / re.split(r'[\\/]', file)[-1]
            if candidate.is_file(): file = candidate
        return builtins.open(file, *args, **kwargs)
    namespace['open'] = local_open
    ipython = types.ModuleType('IPython'); ipython.display = display_module
    ipython.get_ipython = lambda: None
    ipython.version_info = (8, 0)
    sys.modules['IPython'] = ipython
    sys.modules['IPython.display'] = display_module
    forbidden = {'eval', 'exec', 'compile', 'getattr', 'setattr', 'delattr', 'globals', 'locals', 'vars', 'input', '__import__', 'breakpoint', 'help'}
    for index, cell in enumerate(payload['notebook']['cells']):
        if cell.get('cell_type') != 'code':
            continue
        code = source(cell)
        result = {'cell': index, 'status': 'ok', 'outputs': []}
        stdout = io.StringIO()
        try:
            lines = code.splitlines()
            installs = [line for line in lines if re.match(r'^\s*%pip\s+install\s+', line)]
            if installs:
                code = '\n'.join(line for line in lines if line not in installs)
                result['message'] = 'Package-install line skipped; preinstalled packages used. Remaining code unchanged.'
                if not code.strip():
                    raise PermissionError('Package installation skipped; preinstalled review packages used.')
            if any(line.lstrip().startswith(('%', '!')) for line in code.splitlines()):
                raise PermissionError('Shell / notebook magic skipped.')
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    if any(alias.name.split('.')[0] not in allowed for alias in node.names):
                        raise PermissionError('Import is not allowed in offline review.')
                if isinstance(node, ast.ImportFrom) and (node.level or (node.module or '').split('.')[0] not in allowed):
                    raise PermissionError('Import is not allowed in offline review.')
                if isinstance(node, ast.Name) and (node.id in forbidden or node.id.startswith('__')):
                    raise PermissionError('Dynamic execution / introspection is not allowed.')
                if isinstance(node, ast.Attribute) and node.attr.startswith('_'):
                    raise PermissionError('Private attribute access is not allowed.')
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stdout):
                value = None
                if tree.body and isinstance(tree.body[-1], ast.Expr):
                    expression = tree.body.pop()
                    exec(compile(tree, '<submission>', 'exec'), namespace)
                    value = eval(compile(ast.Expression(expression.value), '<submission>', 'eval'), namespace)
                else:
                    exec(compile(tree, '<submission>', 'exec'), namespace)
                if value is not None:
                    if hasattr(value, '_repr_html_'):
                        result['outputs'].append({'output_type': 'display_data', 'data': {'text/html': value._repr_html_()}})
                    else:
                        result['outputs'].append({'output_type': 'execute_result', 'data': {'text/plain': repr(value)[:100000]}})
                if 'matplotlib.pyplot' in sys.modules:
                    import base64
                    plt = sys.modules['matplotlib.pyplot']
                    for number in plt.get_fignums():
                        image = io.BytesIO(); plt.figure(number).savefig(image, format='png', bbox_inches='tight', dpi=110)
                        result['outputs'].append({'output_type': 'display_data', 'data': {'image/png': base64.b64encode(image.getvalue()).decode()}})
                    plt.close('all')
        except Exception as error:
            result['status'] = 'skipped' if isinstance(error, PermissionError) else 'error'
            result['message'] = type(error).__name__ + ': ' + str(error)
        if stdout.getvalue():
            result['outputs'].insert(0, {'output_type': 'stream', 'text': stdout.getvalue()[:100000]})
        results.append(result)
    Path('result.json').write_text(json.dumps(results, ensure_ascii=False))


def sandbox_profile(work):
    # No network or personal files; writes are confined to this disposable job.
    paths = ['/System', '/usr', '/bin', '/private/var/db/dyld', '/Library/Apple', '/opt/homebrew', str(Path(sys.base_prefix).resolve()), str(Path(sys.prefix).resolve()), str(UI), str(work)]
    quote = lambda value: json.dumps(str(value))
    reads = '(literal "/") ' + ' '.join('(subpath ' + quote(path) + ')' for path in paths)
    return '(version 1)(deny default)(allow process-exec)(allow sysctl-read)(allow mach-lookup)(allow file-read-metadata)(allow file-read* ' + reads + ' (literal "/dev/null") (literal "/dev/urandom"))(allow file-write* (subpath ' + quote(work) + ') (literal "/dev/null"))'


def replay(notebook, files, folder, digest, api_responses=None):
    target = OUTPUT / digest
    report = target / 'replay.json'
    if report.exists():
        return json.loads(report.read_text())
    target.mkdir(parents=True, exist_ok=True)
    notices, aliases = [], {}
    if api_responses:
        times = sorted(record['fetched_at'] for record in api_responses.values())
        notices.append('Controlled public API cache: ' + str(len(api_responses)) + ' response(s), fetched ' + times[0] + ' to ' + times[-1] + '. Re-fetched data, not the student’s original response. Network disabled during replay.')
    # UNIPA names include ID + attachment ordinals. Restore aliases only in a job copy.
    for path in files:
        original = re.sub(r'^\d+_\d+_\d+_', '', path.name)
        aliases.setdefault(original, []).append(path)
    code = '\n'.join(source(cell) for cell in notebook['cells'] if cell.get('cell_type') == 'code')
    if re.search(r'[A-Za-z]:\\\\', code):
        notices.append('Windows absolute file paths may resolve to an exact-name attachment in this student’s temporary job only. Original paths and files are unchanged.')
    wanted = set(re.findall(r'[\"\x27]([^\"\x27\n]+\.csv)[\"\x27]', code))
    datafiles = [path for path in files if path.suffix.lower() in {'.csv', '.txt'}]
    with tempfile.TemporaryDirectory(prefix='job-', dir=OUTPUT) as temporary:
        work = Path(temporary).resolve()
        for name, matches in aliases.items():
            if len(matches) == 1:
                shutil.copy2(matches[0], work / name)
            else:
                notices.append('Ambiguous attachment name: ' + name)
        for name in wanted:
            destination = work / Path(name).name
            if not destination.exists() and len(datafiles) == 1:
                shutil.copy2(datafiles[0], destination)
                notices.append('Replay CSV alias: ' + datafiles[0].name + ' → ' + destination.name)
            elif not destination.exists():
                notices.append('Missing / ambiguous CSV: ' + name)
        (work / 'job.json').write_text(json.dumps({'notebook': notebook, 'api_responses': api_responses or {}}, ensure_ascii=False))
        command = ['/usr/bin/sandbox-exec', '-p', sandbox_profile(work), str(Path(sys.executable).absolute()), '-B', str(Path(__file__).resolve()), '--worker', 'job.json']
        try:
            process = subprocess.run(command, cwd=work, env={'PATH': '/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE': '1', 'MPLBACKEND': 'Agg', 'MPLCONFIGDIR': str(work / 'mpl-cache')}, capture_output=True, text=True, timeout=40)
            if not (work / 'result.json').exists():
                raise RuntimeError((process.stderr or process.stdout or 'Execution did not complete (exit ' + str(process.returncode) + ')')[-1600:])
            cells = json.loads((work / 'result.json').read_text())
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
            cells = []
            notices.append('Replay unavailable: ' + str(error))
        # Preserve generated HTML separately, never replace a student submission.
        generated = []
        for path in work.glob('*.html'):
            name = 'generated-' + path.name
            shutil.copy2(path, target / name)
            generated.append(str((target / name).relative_to(ADMIN)))
    result = {'cells': cells, 'notes': notices, 'generated': generated}
    report.write_text(json.dumps(result, ensure_ascii=False))
    return result


def read_roster():
    path = ADMIN / 'roster.csv'
    if not path.exists():
        return {}, ['roster.csv not found; student IDs shown.']
    raw = path.read_bytes()
    for encoding in ['utf-8-sig', 'cp932']:
        try:
            rows = list(csv.reader(io.StringIO(raw.decode(encoding))))
            break
        except UnicodeError:
            continue
    else:
        return {}, ['roster.csv encoding is unsupported.']
    normalize = lambda value: unicodedata.normalize('NFKC', value).strip()
    header_index = next((i for i, row in enumerate(rows) if '学籍番号' in [normalize(v) for v in row] and any(normalize(v) in {'学生氏名', '氏名'} for v in row)), None)
    if header_index is None:
        return {}, ['roster.csv: 学籍番号 / 学生氏名 columns not found.']
    headers = [normalize(v) for v in rows[header_index]]
    id_column = headers.index('学籍番号')
    name_column = headers.index('学生氏名') if '学生氏名' in headers else headers.index('氏名')
    roman_column = next((i for i, value in enumerate(headers) if value in {'学生氏名_英語', '氏名_英語', 'Roman name'}), None)
    kana_column = next((i for i, value in enumerate(headers) if value in {'学生氏名_カナ', '氏名_カナ', 'フリガナ'}), None)
    roster, conflicts, notes = {}, set(), []
    for row in rows[header_index + 1:]:
        if len(row) <= max(id_column, name_column):
            continue
        student = normalize(row[id_column]).lstrip("'")
        if re.fullmatch(r'\d{8,12}\.0', student):
            student = student[:-2]
        name = row[name_column].strip()
        if not re.fullmatch(r'\d{8,12}', student) or not name:
            continue
        roman = normalize(row[roman_column]) if roman_column is not None and len(row) > roman_column else ''
        kana = normalize(row[kana_column]) if kana_column is not None and len(row) > kana_column else ''
        hiragana = ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in kana)
        if roman in {'-', 'なし'}:
            roman = ''
        if student in roster and roster[student]['name'] != name:
            conflicts.add(student)
        roster[student] = {'name': name, 'reading': roman or hiragana}
    for student in conflicts:
        del roster[student]
        notes.append('Conflicting roster names; ID left unmatched: ' + student)
    return roster, notes


def prepare():
    roster, roster_notes = read_roster()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    API_CACHE.mkdir(exist_ok=True)
    worker_version = hashlib.sha256(inspect.getsource(worker).encode()).hexdigest()
    for name in ['index.html', 'admin.js', 'admin.css']:
        shutil.copy2(UI / name, ADMIN / name)
    weeks, total = [], 0
    for folder in sorted(ADMIN.iterdir()):
        match = re.fullmatch(r'week[-_]?0?(\d+)', folder.name)
        if not folder.is_dir() or not match:
            continue
        week = int(match[1]); groups = {}
        # UNIPA exports may be kept inside their timestamped extraction folder.
        for file in sorted(folder.rglob('*')):
            match = re.match(r'^(\d{8,12})_', file.name)
            if match and file.is_file():
                groups.setdefault(match[1], []).append(file)
        submissions = []
        for student, files in groups.items():
            notebooks = [file for file in files if file.suffix.lower() == '.ipynb']
            for file in notebooks or [None]:
                invalid = None
                try:
                    notebook = json.loads(file.read_text(encoding='utf-8-sig')) if file else None
                    if notebook is not None and (not isinstance(notebook, dict) or not isinstance(notebook.get('cells'), list)): raise ValueError('Missing notebook cells')
                except (ValueError, UnicodeError) as error:
                    notebook = None; invalid = 'Notebook could not be read; upload may still be incomplete: ' + str(error)
                urls = api_urls(notebook) if notebook else []
                responses = {}
                if urls:
                    with ThreadPoolExecutor(max_workers=4) as pool:
                        for response in pool.map(cache_api, urls):
                            if response: responses[response['url']] = response
                identity = (str(file) if file else str(folder / student))
                digest = hashlib.sha256(('review-v5:' + worker_version + identity + ''.join(hashlib.sha256(f.read_bytes()).hexdigest() for f in files) + json.dumps(responses, sort_keys=True)).encode()).hexdigest()[:20]
                destination = OUTPUT / digest; destination.mkdir(exist_ok=True)
                execution = replay(notebook, files, folder, digest, responses) if notebook else {'cells': [], 'notes': [invalid or 'No notebook submitted.'], 'generated': []}
                assets = []
                for attached in files:
                    entry = {'name': attached.name, 'path': str(attached.relative_to(ADMIN)), 'type': attached.suffix[1:].upper(), 'bytes': attached.stat().st_size}
                    if attached.suffix.lower() in {'.csv', '.txt'}:
                        try:
                            with attached.open(encoding='utf-8-sig', newline='') as stream:
                                reader = csv.reader(stream); rows = list(reader)
                            entry['table'] = {'headers': rows[0] if rows else [], 'rows': rows[1:101], 'total': max(0, len(rows)-1)}
                        except (UnicodeError, csv.Error):
                            entry['table_error'] = 'Could not decode as UTF-8 CSV.'
                    assets.append(entry)
                title = next((re.sub(r'^#+\s*', '', source(c).splitlines()[0]).strip() for c in (notebook or {}).get('cells', []) if c.get('cell_type') == 'markdown' and source(c).strip()), file.name if file else 'Images / attachments only')
                record = {'id': digest, 'week': week, 'student': student, 'student_name': roster.get(student, {}).get('name'), 'student_reading': roster.get(student, {}).get('reading'), 'title': title, 'file': file.name if file else None, 'notebook': notebook, 'attachments': assets, 'replay': execution}
                (destination / 'submission.json').write_text(json.dumps(record, ensure_ascii=False))
                counts = {key: sum(c['status'] == key for c in execution['cells']) for key in ['ok', 'error', 'skipped']}
                submissions.append({'id': digest, 'student': student, 'student_name': record['student_name'], 'student_reading': record['student_reading'], 'title': title, 'file': record['file'], 'attachments': len(files), 'saved_outputs': sum(bool(c.get('outputs')) for c in (notebook or {}).get('cells', [])), 'execution': counts, 'notes': execution['notes']})
                total += 1
        weeks.append({'week': week, 'students': len(groups), 'submissions': submissions})
    submitted_ids = {submission['student'] for week in weeks for submission in week['submissions']}
    manifest = {'generated': datetime.now().astimezone().isoformat(), 'weeks': weeks, 'roster': {'matched': len(submitted_ids & roster.keys()), 'unmatched': sorted(submitted_ids - roster.keys()), 'notes': roster_notes}}
    (OUTPUT / 'index.json').write_text(json.dumps(manifest, ensure_ascii=False))
    print('Prepared', total, 'submission previews.', flush=True)
    return manifest


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def allowed(self):
        return self.headers.get('Host') in {'127.0.0.1:8766', 'localhost:8766'}

    def do_GET(self):
        if self.allowed() and self.path == '/__admin/hearts':
            state = ADMIN / '.gallery-hearts.json'
            body = json.dumps({'hearts': json.loads(state.read_text()) if state.exists() else None}).encode()
            self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers(); self.wfile.write(body); return
        path = Path(self.translate_path(self.path)).resolve()
        if not self.allowed() or not path.is_relative_to(ROOT) or any(part in {'.git', '.venv'} for part in path.relative_to(ROOT).parts):
            self.send_error(403); return
        return super().do_GET()

    def list_directory(self, path):
        self.send_error(403, 'Directory listing disabled')

    def do_POST(self):
        if self.path == '/__admin/gallery':
            if not self.allowed() or self.headers.get('Origin') not in {'http://127.0.0.1:8766', 'http://localhost:8766'} or self.headers.get('X-Admin-Request') != 'gallery':
                self.send_error(403); return
            if not LOCK.acquire(blocking=False): self.send_error(409, 'Another update is running'); return
            try:
                from gallery_export import publish
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length < 250000: raise ValueError('Invalid request size')
                result = publish(json.loads(self.rfile.read(length)))
                self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers(); self.wfile.write(json.dumps(result).encode())
            except Exception as error:
                self.send_error(500, 'Gallery update failed; retry the heart action. ' + type(error).__name__)
            finally: LOCK.release()
            return
        if not self.allowed() or self.path != '/__admin/refresh' or self.headers.get('Origin') not in {'http://127.0.0.1:8766', 'http://localhost:8766'} or self.headers.get('X-Admin-Request') != 'refresh':
            self.send_error(403); return
        if not LOCK.acquire(blocking=False):
            self.send_error(409, 'Review preparation already running'); return
        try:
            prepare()
            state = ADMIN / '.gallery-hearts.json'
            if state.exists():
                from gallery_export import publish
                publish(json.loads(state.read_text()))
            self.send_response(200); self.end_headers(); self.wfile.write(b'OK')
        except Exception:
            self.send_error(500, 'Import or public gallery update failed; retry refresh.')
        finally:
            LOCK.release()

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        super().end_headers()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker')
    parser.add_argument('--serve', action='store_true')
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
    else:
        prepare()
        if args.serve:
            print('Local admin: http://127.0.0.1:8766/admin/', flush=True)
            ThreadingHTTPServer(('127.0.0.1', 8766), Handler).serve_forever()
