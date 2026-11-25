"""Check the preserved assessment and re-run every published bicycle example.

Run with admin/.venv/bin/python. The no-pandas route also runs under system Python.
"""
from pathlib import Path
import ast, collections, contextlib, csv, importlib.util, io, json, re, subprocess, sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import bicycle_week as lesson
folder = ROOT/'weeks/week-08'
private = ROOT/'admin/.course-private/week08/quiz-source.json'
payload = json.loads((folder.parent/'week-09/quiz-01.enc.json').read_text())
assert not (folder/'quiz-01.ipynb').exists()
assert payload['algorithm']=='AES-GCM' and payload['iterations']>=250000
if private.exists():
    import quiz_package
    config=json.loads(private.read_text())
    quiz=json.loads(quiz_package.decrypt(payload,config['passphrase']))
    answers=[c for c in quiz['cells'] if c['cell_type']=='code']
    assert len(answers)==6 and all(not ''.join(c['source']).strip() and not c['outputs'] for c in answers)
    archive=ROOT/'2025 Material/Week08/小テスト①.ipynb'
    if archive.exists():
        old=json.loads(archive.read_text())['cells']
        originals=[''.join(c['source']).strip() for c in old if c['cell_type']=='markdown' and not ''.join(c['source']).startswith('## 小テスト')]
        normalize=lambda text:re.sub(r'\s+',' ',text).strip()
        assert list(map(normalize,originals))==list(map(normalize,[text for _,text in config['questions']]))
with (folder/'bike.csv').open(encoding='cp932', newline='') as f:
    rows = list(csv.DictReader(f))
assert len(rows)==10054
nb = json.loads((folder/'bicycle-theft-guide.ipynb').read_text())
code = [c for c in nb['cells'] if c['cell_type']=='code']
# Run all ten standard-library cells in a clean interpreter, including ASCII art.
script = 'import ast, contextlib, io, json, sys\nscope={}\nfor c in json.load(sys.stdin):\n tree=ast.parse(c["source"]); stream=io.StringIO()\n with contextlib.redirect_stdout(stream):\n  value=None\n  if tree.body and isinstance(tree.body[-1],ast.Expr):\n   exec(compile(ast.Module(body=tree.body[:-1],type_ignores=[]),"<student>","exec"),scope)\n   value=eval(compile(ast.Expression(tree.body[-1].value),"<student>","eval"),scope)\n  else:exec(compile(tree,"<student>","exec"),scope)\n saved=c["outputs"]\n actual=[]\n if stream.getvalue():actual.append(stream.getvalue())\n if value is not None:actual.append(repr(value))\n expected=[o["text"] if o["output_type"]=="stream" else o["data"]["text/plain"] for o in saved]\n assert actual==expected,(actual,expected)\nprint("PASS: 10 cells work without pandas, saved outputs match")'
r = subprocess.run(['/usr/bin/python3','-I','-c',script],input=json.dumps(code[:10]),text=True,capture_output=True,cwd=folder)
assert r.returncode==0, r.stderr
print(r.stdout.strip())
assert ast.literal_eval(code[0]['outputs'][0]['data']['text/plain'])==len(rows)
lock = collections.Counter(r['施錠関係'] for r in rows)
assert ast.literal_eval(code[2]['outputs'][0]['data']['text/plain'])==dict(lock)
assert sum(lock.values())==len(rows) and lock=={'施錠せず':6879,'施錠した':3175}
assert ast.literal_eval(code[3]['outputs'][0]['data']['text/plain'])==sum(r['市区町村（発生地）']=='柏市' for r in rows)
expected = collections.Counter(r['市区町村（発生地）'] for r in rows).most_common(5)
assert ast.literal_eval(code[4]['outputs'][0]['data']['text/plain'])==expected
# Formatting is checked against independent counts, including bar start positions.
by_source = {cell['source']: cell for cell in code}
pretty = by_source[lesson.RANK_PRETTY]['outputs'][0]['text'].splitlines()[2:]
assert [line.strip() for line in pretty] == [f"{count:,}件  {place}" for place,count in expected]
bars = by_source[lesson.BARS]['outputs'][0]['text'].splitlines()
assert bars[::2] == [f"{place} ({count:,}件)" for place,count in expected]
assert bars[1::2] == ['#' * (count//100) for place,count in expected]
# The saved frame and browser animation frames must match the actual Python frames.
from unittest.mock import patch
import bicycle_ascii
stream=io.StringIO()
with contextlib.redirect_stdout(stream), patch('IPython.display.clear_output') as clear, patch('time.sleep'):
    exec(bicycle_ascii.ANIMATION,{})
assert clear.call_count==16
assert stream.getvalue() == ''.join(frame+'\n' for frame in bicycle_ascii.FRAMES)*4
assert by_source[bicycle_ascii.ANIMATION]['outputs'][0]['text']==bicycle_ascii.FRAMES[-1]+'\n'
print('PASS: readable ranking, left-aligned bars, 16 Python animation frames match the display')
# The pandas alternative must give the same ranking; the chart uses those exact lock counts.
import matplotlib
matplotlib.use('Agg')
scope = {}; import matplotlib.pyplot as plt
with contextlib.chdir(folder):
    exec(lesson.PANDAS,scope)
    assert list(scope['df']['市区町村（発生地）'].value_counts().head(5).items())==expected
    exec(lesson.PLOT.replace('plt.show()',''),scope)
    assert [p.get_height() for p in plt.gca().patches]==[6879,3175]
    assert plt.gca().get_xlabel()=='Lock status'
    plt.close('all')
lecture = (folder/'lecture.html').read_text()
assert lecture.count('data-slide data-ink-id=')==24
assert 'data-ink-id="w8-bike-quiz' not in lecture
assert 'data-release="2026-11-19T12:00:00+09:00"' in lecture
assert not any(x in lecture for x in ['student-menu.csv','remaining(','def count_places','earthquakes'])
assert lecture.index('w8-bike-review') < lecture.index('w8-bike-cctv-01') < lecture.index('w8-bike-police-source') < lecture.index('w8-bike-data')
assert lecture.count('class="camera-frame"')==6
assert (folder/'challenge.html').read_text().index('000074746.csv') < (folder/'challenge.html').read_text().index('2. 空のNotebook')
assert (folder/'bicycle-lock-status.png').read_bytes().startswith(b'\x89PNG')
print('PASS: six unanswered quiz questions; CSV counts, rankings, pandas chart and Week 8 release gate verified')
