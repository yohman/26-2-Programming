"""Exercise actual notebook cells against a failed API and a fresh response."""
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError
import contextlib, io, json, sys, tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import weather_hackathon as lesson

fixture=json.loads((ROOT/'weeks/week-07/weather-response.json').read_text())
starter=json.loads((ROOT/'weeks/week-07/challenge-starter.ipynb').read_text())
code=[''.join(c['source']) for c in starter['cells'] if c['cell_type']=='code']
assert code[0]==lesson.LIVE_LOAD and code[1]==lesson.NORMALIZE
assert {c.get('metadata',{}).get('checkpoint') for c in starter['cells'] if 'solo-check' in c.get('metadata',{}).get('tags',[])}=={'A','B'}

with tempfile.TemporaryDirectory() as directory,contextlib.chdir(directory):
    Path('weather-response.json').write_text(json.dumps(fixture))
    scope={};output=io.StringIO()
    with patch('urllib.request.urlopen',side_effect=URLError('classroom offline')),contextlib.redirect_stdout(output):
        exec(lesson.LIVE_LOAD,scope);exec(lesson.NORMALIZE,scope)
    assert 'Saved JSON' in output.getvalue()
    assert len(scope['forecast'])==24
    assert scope['forecast'][0]['time']==fixture['hourly']['time'][0]
    live=json.loads(json.dumps(fixture));live['hourly']['temperature_2m'][0]=27.5
    with patch('urllib.request.urlopen',return_value=io.BytesIO(json.dumps(live).encode())),contextlib.redirect_stdout(io.StringIO()):
        exec(lesson.LIVE_LOAD,scope);exec(lesson.NORMALIZE,scope)
    saved=json.loads(Path('weather-response.json').read_text())
    assert saved['hourly']['temperature_2m'][0]==27.5
    assert saved['_source']['url'].startswith('https://api.open-meteo.com/v1/forecast?')
    assert scope['forecast'][0]['temp']==27.5
    exec(lesson.VISUAL_SETUP,scope)
    boards=[]
    scope.update(max_rain=30,min_temp=10,HTML=lambda value:value,display=boards.append)
    answers=iter(['?', 'show','warmer','quit'])
    scope['input']=lambda prompt:next(answers)
    with contextlib.redirect_stdout(io.StringIO()):exec(lesson.WHILE_CODE,scope)
    assert scope['min_temp']==11 and scope['command']=='quit'
    assert '<table' in boards[-1] and 'hours match' in boards[-1]
    scope['min_temp']=50;answers=iter(['show','quit']);output=io.StringIO()
    with contextlib.redirect_stdout(output):exec(lesson.WHILE_CODE,scope)
    assert 'No matching hours' in output.getvalue()
    assert '0 / 24 hours match' in boards[-1] and 'No hours match' in boards[-1]
print('PASS: real starter cells handle offline/live data, preserve the used JSON, repeat input and terminate on quit.')
