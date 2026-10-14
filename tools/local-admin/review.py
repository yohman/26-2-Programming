#!/usr/bin/env python3
"""Local-only submission index, isolated notebook replay and loopback review server.

Run using admin/.venv/bin/python tools/local-admin/review.py --serve
Never modifies student originals. All generated data lives in ignored admin/_review.
"""
import argparse
import ast
import contextlib
import csv
import hashlib
import html
import io
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

ROOT = Path(__file__).resolve().parents[2]
ADMIN = ROOT / 'admin'
OUTPUT = ADMIN / '_review'
UI = Path(__file__).parent
LOCK = threading.Lock()


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
    allowed = {'csv', 'folium', 'branca', 'pandas', 'numpy', 'datetime', 'json', 'math', 'pathlib', 'IPython'}
    # Capture common display()/IFrame outputs without starting a Jupyter kernel.
    import types
    display_module = types.ModuleType('IPython.display')
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
    display_module.display, display_module.IFrame = display, LocalFrame
    ipython = types.ModuleType('IPython'); ipython.display = display_module
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
                    raise PermissionError('Package installation skipped; Folium is already installed.')
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


def replay(notebook, files, folder, digest):
    target = OUTPUT / digest
    report = target / 'replay.json'
    if report.exists():
        return json.loads(report.read_text())
    target.mkdir(parents=True, exist_ok=True)
    notices, aliases = [], {}
    # UNIPA names include ID + attachment ordinals. Restore aliases only in a job copy.
    for path in files:
        original = re.sub(r'^\d+_\d+_\d+_', '', path.name)
        aliases.setdefault(original, []).append(path)
    code = '\n'.join(source(cell) for cell in notebook['cells'] if cell.get('cell_type') == 'code')
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
        (work / 'job.json').write_text(json.dumps({'notebook': notebook}, ensure_ascii=False))
        command = ['/usr/bin/sandbox-exec', '-p', sandbox_profile(work), str(Path(sys.executable).absolute()), '-B', str(Path(__file__).resolve()), '--worker', 'job.json']
        try:
            process = subprocess.run(command, cwd=work, env={'PATH': '/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE': '1'}, capture_output=True, text=True, timeout=40)
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
        if student in roster and roster[student] != name:
            conflicts.add(student)
        roster[student] = name
    for student in conflicts:
        del roster[student]
        notes.append('Conflicting roster names; ID left unmatched: ' + student)
    return roster, notes


def prepare():
    roster, roster_notes = read_roster()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name in ['index.html', 'admin.js', 'admin.css']:
        shutil.copy2(UI / name, ADMIN / name)
    weeks, total = [], 0
    for folder in sorted(ADMIN.iterdir()):
        match = re.fullmatch(r'week[-_]?0?(\d+)', folder.name)
        if not folder.is_dir() or not match:
            continue
        week = int(match[1]); groups = {}
        for file in sorted(folder.iterdir()):
            match = re.match(r'^(\d{8,12})_', file.name)
            if match and file.is_file():
                groups.setdefault(match[1], []).append(file)
        submissions = []
        for student, files in groups.items():
            notebooks = [file for file in files if file.suffix.lower() == '.ipynb']
            for file in notebooks or [None]:
                notebook = json.loads(file.read_text(encoding='utf-8-sig')) if file else None
                identity = (str(file) if file else str(folder / student))
                digest = hashlib.sha256(('review-v3:' + identity + ''.join(hashlib.sha256(f.read_bytes()).hexdigest() for f in files)).encode()).hexdigest()[:20]
                destination = OUTPUT / digest; destination.mkdir(exist_ok=True)
                execution = replay(notebook, files, folder, digest) if notebook else {'cells': [], 'notes': ['No notebook submitted.'], 'generated': []}
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
                record = {'id': digest, 'week': week, 'student': student, 'student_name': roster.get(student), 'title': title, 'file': file.name if file else None, 'notebook': notebook, 'attachments': assets, 'replay': execution}
                (destination / 'submission.json').write_text(json.dumps(record, ensure_ascii=False))
                counts = {key: sum(c['status'] == key for c in execution['cells']) for key in ['ok', 'error', 'skipped']}
                submissions.append({'id': digest, 'student': student, 'student_name': roster.get(student), 'title': title, 'file': record['file'], 'attachments': len(files), 'saved_outputs': sum(bool(c.get('outputs')) for c in (notebook or {}).get('cells', [])), 'execution': counts, 'notes': execution['notes']})
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
        path = Path(self.translate_path(self.path)).resolve()
        if not self.allowed() or not path.is_relative_to(ROOT) or any(part in {'.git', '.venv'} for part in path.relative_to(ROOT).parts):
            self.send_error(403); return
        return super().do_GET()

    def list_directory(self, path):
        self.send_error(403, 'Directory listing disabled')

    def do_POST(self):
        if not self.allowed() or self.path != '/__admin/refresh' or self.headers.get('Origin') not in {'http://127.0.0.1:8766', 'http://localhost:8766'} or self.headers.get('X-Admin-Request') != 'refresh':
            self.send_error(403); return
        if not LOCK.acquire(blocking=False):
            self.send_error(409, 'Review preparation already running'); return
        try:
            prepare(); self.send_response(200); self.end_headers(); self.wfile.write(b'OK')
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
