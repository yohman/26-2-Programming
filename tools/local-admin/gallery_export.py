"""Export every submission; hearts mark featured work. Private records stay in admin/."""
import hashlib
import csv
import json
from pathlib import Path
import re
import subprocess
import os
import tempfile
import threading
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / 'admin/.gallery-hearts.json'
PUBLIC = ROOT / 'submissions/gallery.json'
FEATURED = ROOT / 'submissions/featured.json'
PUBLICATION_LOCK = threading.Lock()

def write_json_atomic(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as file:
        json.dump(value, file, ensure_ascii=False)
        temporary = file.name
    os.replace(temporary, path)


def public_id(key):
    return hashlib.sha256(json.dumps(tuple(key)).encode()).hexdigest()[:20]


def save_hearts(request):
    index = json.loads((ROOT / 'admin/_review/index.json').read_text())
    previous = json.loads(STATE.read_text()) if STATE.exists() else []
    if isinstance(request, dict):
        changes = request.get('changes')
        if not isinstance(changes, dict) or len(changes) > 1000 or any(type(v) is not bool for v in changes.values()):
            raise ValueError('Invalid heart changes')
        selected = set(previous)
        for key, enabled in changes.items():
            selected.add(key) if enabled else selected.discard(key)
        hearts = list(selected)
    else: hearts = request
    if not isinstance(hearts, list) or len(hearts) > 1000:
        raise ValueError('Invalid heart selection')
    selected = set()
    for key in hearts:
        value = json.loads(key)
        if not isinstance(value, list) or len(value) != 3 or type(value[0]) is not int or not all(isinstance(v, str) for v in value[1:]):
            raise ValueError('Invalid submission identity')
        selected.add(tuple(value))
    accepted, ids, count = [], [], 0
    for week in index['weeks']:
        for item in week['submissions']:
            count += 1
            key = (week['week'], item['student'], item['file'] or '')
            if key in selected:
                accepted.append(json.dumps(list(key), ensure_ascii=False, separators=(',', ':')))
                ids.append(public_id(key))
    previous_ids = None
    try: previous_ids = json.loads(FEATURED.read_text())['ids']
    except (OSError, ValueError, KeyError): pass
    changed = set(previous) != set(accepted) or sorted(ids) != previous_ids
    if changed:
        write_json_atomic(STATE, accepted)
        write_json_atomic(FEATURED, dict(updated=datetime.now().astimezone().isoformat(), ids=sorted(ids)))
    return dict(count=count, featured=len(accepted), hearts=accepted, changed=changed)


def push_files(paths, message):
    with PUBLICATION_LOCK:
        subprocess.run(['git', 'add', '--', *paths], cwd=ROOT, check=True)
        if subprocess.run(['git', 'diff', '--cached', '--quiet', '--', *paths], cwd=ROOT).returncode:
            subprocess.run(['git', 'commit', '--only', '-m', message, '--', *paths], cwd=ROOT, check=True, capture_output=True)
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=ROOT, check=True, capture_output=True, timeout=60)


def publish_featured():
    push_files(['submissions/featured.json'], 'Update featured student work')



def notebook_fingerprint(entry):
    """Group only equal authored cells, attachments and saved results, within a week.

    Execution counters and cell metadata do not change the submitted work.
    Different text, code, input results, charts, or images remain separate.
    """
    if not entry['has_notebook']:
        return entry['id']
    cells = []
    for cell in entry['notebook']['cells']:
        content = {key: cell[key] for key in ('cell_type', 'source', 'outputs', 'attachments') if key in cell}
        source = content.get('source', '')
        content['source'] = ''.join(source) if isinstance(source, list) else source
        content['outputs'] = [{key: value for key, value in output.items() if key not in ('execution_count', 'metadata')}
                              for output in content.get('outputs', [])]
        cells.append(content)
    return hashlib.sha256(json.dumps(cells, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def group_identical(entries):
    projects = {}
    for entry in entries:
        key = (entry['week'], notebook_fingerprint(entry))
        if key not in projects:
            entry['submission_ids'] = []
            entry['submitters'] = []
            entry['submission_count'] = 0
            projects[key] = entry
        project = projects[key]
        project['submission_ids'].append(entry['id'])
        person = {'name': entry['student_name'], 'reading': entry['student_reading']}
        if person not in project['submitters']:
            project['submitters'].append(person)
        project['submission_count'] += 1
        project['featured'] = project['featured'] or entry['featured']
    return list(projects.values())


def public_notebook(entry):
    cells = []
    for cell in entry['notebook']['cells']:
        result = {'cell_type': cell['cell_type'], 'metadata': {}, 'source': cell.get('source', '')}
        if 'attachments' in cell:
            result['attachments'] = cell['attachments']
        if cell['cell_type'] == 'code':
            result.update(execution_count=cell.get('execution_count'), outputs=cell.get('outputs', []))
        cells.append(result)
    return {'nbformat': 4, 'nbformat_minor': 4, 'metadata': {
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python'}}, 'cells': cells}


def publish(hearts, push=True):
    if not isinstance(hearts, list) or len(hearts) > 1000:
        raise ValueError('Invalid heart selection')
    index = json.loads((ROOT / 'admin/_review/index.json').read_text())
    selected = {tuple(json.loads(key)) for key in hearts}
    entries, accepted = [], []
    student_ids = {s['student'] for w in index['weeks'] for s in w['submissions']}
    roster = ROOT / 'admin/roster.csv'
    if roster.exists():
        with roster.open(encoding='utf-8-sig', newline='') as stream:
            student_ids.update(value.strip().lstrip("'") for row in csv.reader(stream) for value in row
                               if re.fullmatch(r'\d{8,12}', value.strip().lstrip("'")))
    def clean(value):
        if isinstance(value, dict): return {key: clean(item) for key, item in value.items()}
        if isinstance(value, list): return [clean(item) for item in value]
        if not isinstance(value, str): return value
        for student in student_ids: value = value.replace(student, '[ID]')
        value = re.sub(r'(?:/Users/[^/\s\"\x27]+|[A-Za-z]:[\\/](?:Users|ユーザー)[\\/][^\\/\s\"\x27]+)', '[local]', value)
        return value
    for week in index['weeks']:
        for item in week['submissions']:
            key = (week['week'], item['student'], item['file'] or '')
            record = json.loads((ROOT / 'admin/_review' / item['id'] / 'submission.json').read_text())
            notebook = record.get('notebook') or {'cells': [{'cell_type': 'markdown', 'source': 'Notebookのプレビューはありません。 / No notebook preview is available.'}]}
            cells = [{k: cell[k] for k in ('cell_type', 'source', 'outputs', 'execution_count', 'attachments') if k in cell} for cell in notebook['cells']]
            runs = [{'cell': run['cell'], 'outputs': [o for o in run['outputs'] if o.get('metadata', {}).get('local_widget_preview')]} for run in record['replay']['cells']]
            entry_id = public_id(key)
            entries.append(clean({'id': entry_id, 'week': week['week'], 'featured': key in selected, 'has_notebook': bool(record.get('notebook')), 'student_name': record['student_name'] or 'Student', 'student_reading': record['student_reading'] or '', 'title': re.sub(r'^\d{8,12}_\d+_\d+_', '', record['title']), 'notebook': {'cells': cells}, 'replay': {'cells': runs}, 'attachments': []}))
            if key in selected:
                accepted.append(json.dumps(list(key), ensure_ascii=False, separators=(',', ':')))
    submission_count = len(entries)
    entries = group_identical(entries)
    for entry in entries:
        if entry['has_notebook']:
            entry['notebook_path'] = 'submissions/notebooks/' + entry['id'] + '.ipynb'
    entries.sort(key=lambda entry: (entry['week'], not entry['featured']))
    # Basic credential guard: do not publish a literal bearer token or common API secret.
    body = json.dumps({'updated': datetime.now().astimezone().isoformat(), 'submissions': entries}, ensure_ascii=False)
    if re.search(r'Bearer\s+[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{25,}', body):
        raise ValueError('Possible API credential detected; publication stopped.')
    PUBLIC.parent.mkdir(exist_ok=True)
    for entry in entries:
        if entry['has_notebook']:
            path = ROOT / entry['notebook_path']
            write_json_atomic(path, public_notebook(entry))
    PUBLIC.write_text(body)
    STATE.write_text(json.dumps(accepted, ensure_ascii=False))
    save_hearts(accepted)
    if push:
        push_files(['submissions/gallery.json', 'submissions/featured.json', 'submissions/notebooks'], 'Update student gallery')
    return {'count': len(entries), 'submissions': submission_count, 'featured': len(accepted), 'hearts': accepted}
