"""Verify saved outputs, portable scripts, download bundles and timer behavior."""
from pathlib import Path
import ast, contextlib, csv, html, io, json, re, subprocess, sys, tempfile, types, zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from weather_hackathon import execute_cell
cells_run=0
for week in range(9,15):
    folder=ROOT/f'weeks/week-{week:02}'
    nb=json.loads((folder/'practice.ipynb').read_text())
    scope={}
    for cell in nb['cells']:
        if cell['cell_type']!='code':continue
        source=''.join(cell['source']);stream=io.StringIO()
        if 'interactive' in cell.get('metadata',{}).get('tags',[]):
            answers=iter(['show','warmer','quit'])
            scope['input']=lambda prompt:next(answers)
        rich=[]
        if 'notebook-display' in cell.get('metadata',{}).get('tags',[]):
            scope['HTML']=lambda value:value
            scope['display']=rich.append
        source=source.replace('from IPython.display import HTML, display\n','')
        value=None
        with contextlib.redirect_stdout(stream),contextlib.chdir(folder):
            if week==9:
                printed,value=execute_cell(source,scope)
                stream.write(printed)
            else:exec(source,scope)
        saved_values=[o['data']['text/plain'] for o in cell['outputs'] if o['output_type']=='execute_result']
        if week==9:assert saved_values==([] if value is None else [repr(value)]),(source,saved_values,value)
        expected_html=[o['data']['text/html'] for o in cell.get('outputs',[]) if o.get('data',{}).get('text/html')]
        if expected_html:assert rich[-1]==expected_html[-1]

        saved=''.join(''.join(o.get('text','')) for o in cell['outputs'])
        if saved:assert stream.getvalue()==saved,(week,source)
        cells_run+=1
    with zipfile.ZipFile(folder/'starter-files.zip') as pack:
        assert pack.testzip() is None
        assert all(name.startswith(f'week-{week:02}/') and '..' not in name for name in pack.namelist())
        if week==10:
            assert set(pack.namelist())=={'week-10/'+n for n in ('hello.py','tiny.py','spinner.py','dot.py','emoji.py','train.py','route.py','rain.py','skyline.py','signal.py','launch.py')}
            for name in pack.namelist():
                assert pack.read(name)==(ROOT/'weeks'/name).read_bytes()
        if week==12:assert f'week-{week:02}/click_model.py' in pack.namelist()

# The visible trace must match the actual Python call-loop output.
lecture=(ROOT/'weeks/week-09/lecture.html').read_text()
flow=re.findall(r'data-slide data-ink-id="w9-fn-([^"]+)"',lecture)
assert len(flow)==26
assert flow[:6]==['recap','quiz','quiz-clock','quiz-save','mori-corner','open']
assert flow[-1]=='try'
assert flow[8:11]==['call','execution','argument']
assert flow[12:20]==['double','even','text-bar','pokemon','earthquakes','bikes','japan-age','week7']
assert 'data-seconds="600"' in lecture and 'Mori’s Corner' in lecture
assert re.findall(r'data-quake-count="(\d+)"',lecture)==['38','6','2']
assert all(sprite in lecture for sprite in ['sprites/pokemon/25.png','sprites/pokemon/shiny/25.png'])
assert '06:00</output>' in lecture
assert 'A: Without AI' in lecture and 'B: AI allowed' in lecture and 'submit once to UNIPA' in lecture
week9=(ROOT/'weeks/week-09/challenge.html').read_text()
homework=week9.split('id="homework"',1)[1]
assert 'Two processing steps' in homework and 'Three test cases' in homework
assert 'Stretch ideas (optional)' in homework and 'No API, pandas, or charting library is required' in homework
outline=json.loads((ROOT/'weeks/week-09/challenge-starter.ipynb').read_text())
assert any('Boundary or no-match case' in cell['source'] for cell in outline['cells'])
payload=json.loads(re.search(r'<script id="lesson-data" type="application/json">(.*?)</script>',lecture,re.S)[1])
nb=json.loads((ROOT/'weeks/week-09/practice.ipynb').read_text())
loop=next(c for c in nb['cells'] if c['cell_type']=='code' and '\nfor student in names:' in c['source'])
expected=ast.literal_eval(loop['outputs'][0]['data']['text/plain'])
assert [result for _,result in payload['nameTrace']]==expected

# Every displayed code example runs on its own and matches a notebook cell.
assert '使うデータを見る' not in lecture
notebook_sources={c['source'] for c in nb['cells'] if c['cell_type']=='code'}
for snippet in re.findall(r'<pre data-language="python"><code>(.*?)</code></pre>',lecture,re.S):
    snippet=html.unescape(snippet)
    assert snippet.startswith('# ') and snippet in notebook_sources
    execute_cell(snippet,{})

# Actual standalone Python must produce precisely the frames replayed in the browser.
ascii_folder=ROOT/'weeks/week-10'
ascii_deck=(ascii_folder/'lecture.html').read_text()
manifest=json.loads((ROOT/'tools/course-flow-manifest.json').read_text())
assert ascii_deck.count(' data-slide data-ink-id=')==next(w['slides'] for w in manifest if w['week']==10)
ascii_flow=re.findall(r'data-slide data-ink-id="w10-ascii-([^"]+)"',ascii_deck)
assert ascii_flow[:2]==['save','run']
assert ascii_flow[4:11]==['frame','loop','timer','train','parameters','route','challenge']
ascii_challenge=(ascii_folder/'challenge.html').read_text()
ascii_agenda=(ROOT/'content/weeks/10-systems.md').read_text()
ascii_payload=lambda page:json.loads(re.search(r'<script type="application/json" id="ascii-data">(.*?)</script>',page,re.S)[1])
for page in (ascii_deck,ascii_challenge,ascii_agenda):
    assert not re.search(r'budget_tool|student-menu|challenge-starter\.ipynb',page)
    assert '2026-12-03T12:00:00+09:00' in page and 'ascii.py' in page
assert 'id="first-file"' in ascii_challenge and 'id="homework"' in ascii_challenge
assert ascii_payload(ascii_deck)==ascii_payload(ascii_challenge)
clear='\x1b[2J\x1b[H'
assert 'w10-ascii-skyline' in ascii_deck and 'w10-ascii-launch' in ascii_deck
assert 'data-ascii-play="200"' in ascii_deck and 'data-ascii-play="800"' in ascii_deck
for name,separator,frame_count in [('tiny',clear,12),('spinner','\r',12),('dot','\r',12),('emoji','\r',6),
                                   ('train','\r',18),('route',clear,3),('rain',clear,9),('signal',clear,4),('launch',clear,10)]:
    script=ascii_folder/(name+'.py')
    code=script.read_text().rstrip()
    assert html.escape(code) in ascii_challenge
    assert (f'data-ascii-demo="{name}"' if name=='tiny' else html.escape('def flight_frame' if name=='launch' else code)) in ascii_deck
    result=subprocess.check_output([sys.executable,str(script)],cwd=tempfile.gettempdir(),timeout=6)
    pictures=result.decode().split(separator)[1:]
    if separator=='\r':pictures[-1]=pictures[-1].rstrip('\n')
    assert pictures==ascii_payload(ascii_deck)[name]['frames'] and len(pictures)==frame_count
    if name=='launch':
        assert 'READY' in pictures[0] and 'LIFTOFF' in pictures[1] and 'ORBIT REACHED' in pictures[-1]
        for picture in pictures:
            lines=picture.splitlines()
            center=len(lines[-1])//2
            nose=next(y for y,line in enumerate(lines) if '^' in line)
            assert [line.ljust(center+4)[center-3:center+4] for line in lines[nose:nose+5]]==[
                '   ^   ', '  / \\  ', '  |o|  ', ' /___\\ ', '   *   ',
            ]
    if name=='signal':
        assert all(frame.count('(*)')==1 for frame in pictures)
    if name=='route':
        assert [next(line[2:] for line in picture.splitlines() if line.startswith('> ')) for picture in pictures]==['Campus','Library','Station']
        assert all(picture.count('> ')==1 for picture in pictures)
    if name=='tiny':
        assert {'🙂','😮'}=={frame.splitlines()[-1][-1] for frame in pictures}
        assert [i for i,frame in enumerate(pictures) if frame.splitlines()[1].index('.')==7+i]==list(range(12))
    if name=='spinner':assert pictures==['|','/','-','\\']*3
    if name=='dot':assert pictures==[' '*i+'.' for i in range(12)]
    if name=='emoji':assert pictures==['🙂','😮','😄']*2
    assert len(set(pictures))>=3
variants=ascii_payload(ascii_deck)
train_code=(ascii_folder/'train.py').read_text().rstrip().rsplit('\n',1)[0]
for key,steps,delay in [('train-short',8,0.12),('train-slow',18,0.25)]:
    variant=subprocess.check_output([sys.executable,'-c',train_code+f'\nanimate_train({steps}, {delay})'],timeout=6)
    pictures=variant.decode().rstrip('\n').split('\r')[1:]
    assert variants[key]=={'frames':pictures,'delay':round(1000*delay)}
    assert pictures==variants['train']['frames'][:steps]
skyline=subprocess.check_output([sys.executable,str(ascii_folder/'skyline.py')],cwd=tempfile.gettempdir(),timeout=2).decode()
assert len(skyline.splitlines())==7 and skyline.count('[#]')==22
assert html.escape(skyline.rstrip('\n')) in ascii_challenge
assert subprocess.check_output([sys.executable,str(ascii_folder/'hello.py')],timeout=3)==b'Hello, terminal!\n'

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
print(f'PASS: {cells_run} worked cells, 6 starter packs, portable CLI inputs, cached boxes and single-timer game callbacks.')
