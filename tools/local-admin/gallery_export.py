"""Publish only explicitly hearted notebook previews. Private records never leave admin/."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / 'admin/.gallery-hearts.json'
PUBLIC = ROOT / 'submissions/gallery.json'

def publish(hearts, push=True):
    if not isinstance(hearts, list) or len(hearts) > 1000:
        raise ValueError('Invalid heart selection')
    index = json.loads((ROOT / 'admin/_review/index.json').read_text())
    selected = {tuple(json.loads(key)) for key in hearts}
    entries, accepted = [], []
    student_ids = {s['student'] for w in index['weeks'] for s in w['submissions']}
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
            if key not in selected: continue
            record = json.loads((ROOT / 'admin/_review' / item['id'] / 'submission.json').read_text())
            if not record.get('notebook'): continue
            cells = [{k: cell[k] for k in ('cell_type', 'source', 'outputs', 'execution_count') if k in cell} for cell in record['notebook']['cells']]
            runs = [{'cell': run['cell'], 'outputs': [o for o in run['outputs'] if o.get('metadata', {}).get('local_widget_preview')]} for run in record['replay']['cells']]
            public_id = hashlib.sha256(json.dumps(key).encode()).hexdigest()[:20]
            entries.append(clean({'id': public_id, 'week': week['week'], 'student_name': record['student_name'] or 'Student', 'student_reading': record['student_reading'] or '', 'title': record['title'], 'notebook': {'cells': cells}, 'replay': {'cells': runs}, 'attachments': []}))
            accepted.append(json.dumps(list(key), ensure_ascii=False, separators=(',', ':')))
    # Basic credential guard: do not publish a literal bearer token or common API secret.
    body = json.dumps({'updated': datetime.now().astimezone().isoformat(), 'submissions': entries}, ensure_ascii=False)
    if re.search(r'Bearer\s+[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{25,}', body):
        raise ValueError('Possible API credential detected; publication stopped.')
    PUBLIC.parent.mkdir(exist_ok=True)
    PUBLIC.write_text(body)
    STATE.write_text(json.dumps(accepted, ensure_ascii=False))
    if push:
        paths = ['submissions/gallery.json']
        subprocess.run(['git', 'add', '--', *paths], cwd=ROOT, check=True)
        if subprocess.run(['git', 'diff', '--cached', '--quiet', '--', *paths], cwd=ROOT).returncode:
            subprocess.run(['git', 'commit', '--only', '-m', 'Update hearted student gallery', '--', *paths], cwd=ROOT, check=True, capture_output=True)
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=ROOT, check=True, capture_output=True, timeout=60)
    return {'count': len(entries), 'hearts': accepted}
