"""Verify saved outputs, portable scripts, download bundles and timer behavior."""
from pathlib import Path
import contextlib, csv, io, json, re, subprocess, sys, tempfile, types, zipfile

ROOT=Path(__file__).resolve().parents[2]
cells_run=0
for week in range(7,15):
    folder=ROOT/f'weeks/week-{week:02}'
    nb=json.loads((folder/'practice.ipynb').read_text())
    scope={}
    for cell in nb['cells']:
        if cell['cell_type']!='code':continue
        source=''.join(cell['source']);stream=io.StringIO()
        with contextlib.redirect_stdout(stream):exec(source,scope)
        saved=''.join(''.join(o.get('text','')) for o in cell['outputs'])
        if saved:assert stream.getvalue()==saved,(week,source)
        cells_run+=1
    with zipfile.ZipFile(folder/'starter-files.zip') as pack:
        assert pack.testzip() is None
        assert all(name.startswith(f'week-{week:02}/') and '..' not in name for name in pack.namelist())
        if week==12:assert f'week-{week:02}/click_model.py' in pack.namelist()
    if week in [7,8,9,10]:
        with (folder/'student-menu.csv').open() as file:assert len(list(csv.DictReader(file)))==24

# The visible trace must match the actual Python call-loop output.
lecture=(ROOT/'weeks/week-09/lecture.html').read_text()
payload=json.loads(re.search(r'<script type="application/json" id="lesson-data">(.*?)</script>',lecture,re.S)[1])
nb=json.loads((ROOT/'weeks/week-09/practice.ipynb').read_text())
loop=next(c for c in nb['cells'] if c['cell_type']=='code' and c['source'].startswith('for budget in [500, 700, 1000]'))
expected=''.join(o.get('text','') for o in loop['outputs']).strip()
assert payload['trace'][-1]['output'].strip()==expected

script=ROOT/'weeks/week-10/budget_tool.py'
for value,expected in [('150','Onigiri'),('abc','whole number'),('-1','zero or more')]:
    result=subprocess.run([sys.executable,str(script)],input=value+'\n',text=True,capture_output=True,cwd=tempfile.gettempdir())
    assert result.returncode==0 and expected in result.stdout,(value,result.stdout,result.stderr)
with (ROOT/'weeks/week-11/detected-boxes.csv').open() as file:
    boxes=list(csv.DictReader(file))
assert boxes and all(0<=int(b['x'])<1200 and int(b['w'])>0 for b in boxes)

# Exercise Python GUI callback logic without opening a window.
real_tk=sys.modules.get('tkinter');sys.modules['tkinter']=types.ModuleType('tkinter')
model=types.ModuleType('click_model');exec((ROOT/'weeks/week-12/click_model.py').read_text(),model.__dict__)
sys.modules['click_model']=model
game=types.ModuleType('game_test');exec((ROOT/'weeks/week-12/click_game.py').read_text(),game.__dict__)
class FakeRoot:
    def __init__(self):self.jobs={};self.index=0
    def after(self,delay,callback):self.index+=1;self.jobs[self.index]=callback;return self.index
    def after_cancel(self,job):self.jobs.pop(job,None)
class FakeWidget:
    def config(self,**kwargs):self.values=kwargs
    def place(self,**kwargs):self.position=kwargs
    def place_forget(self):self.hidden=True
game.root=FakeRoot();game.status=FakeWidget();game.target=FakeWidget()
game.start();assert len(game.root.jobs)==1
game.start();assert len(game.root.jobs)==1
game.on_hit();assert game.score==1 and len(game.root.jobs)==1
game.seconds_left=1;game.root.jobs.clear();game.tick()
assert game.seconds_left==0 and game.timer is None and game.target.hidden
game.on_hit();assert game.score==1
if real_tk:sys.modules['tkinter']=real_tk
print(f'PASS: {cells_run} worked cells, 8 starter packs, portable CLI inputs, cached boxes and single-timer game callbacks.')
