"""Execute the exact web tutorial samples against recorded API data."""
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlparse, parse_qs
import ast, copy, hashlib, io, json, sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import weather_hackathon as lesson
import weather_examples as guide
folder=ROOT/'weeks/week-07'
weather=json.loads((folder/'weather-response.json').read_text())
source=json.loads((folder/'weather-source.json').read_text())
recorded=json.loads((folder/'weather-examples.json').read_text())
for code in [lesson.METEO_CODE,lesson.READ_CODE,lesson.LOCATION_CODE,lesson.WEATHER_CODE]:
    assert not any(isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.Lambda)) for node in ast.walk(ast.parse(code)))
assert source['meteo_sha256']==hashlib.sha256(lesson.METEO_CODE.encode()).hexdigest()
assert source['hashes']==[hashlib.sha256(code.encode()).hexdigest() for code in [lesson.LOCATION_CODE,lesson.WEATHER_CODE]]
assert not any((folder/name).exists() for name in ['challenge-starter.ipynb','practice.ipynb','starter-files.zip','week-07-in-class-logic-review.ipynb'])

calls=[]
def tutorial_open(url,timeout):
    calls.append(url)
    response=source['location_response'] if 'geocoding-api' in url else (weather if len(calls)==1 else source['location_weather'])
    return io.BytesIO(json.dumps(response).encode())
scope={}
with patch('urllib.request.urlopen',side_effect=tutorial_open):
    printed,result=lesson.execute_cell(lesson.METEO_CODE,scope)
    assert printed=='' and result==weather['daily'] and len(calls)==1
    printed,result=lesson.execute_cell(lesson.READ_CODE,scope)
    assert printed=='' and result==(weather['daily']['time'][1],weather['daily']['temperature_2m_max'][1],weather['daily']['precipitation_probability_max'][1])
    printed,result=lesson.execute_cell(lesson.LOCATION_CODE,scope)
    assert printed=='' and result==('Kashiwa','Chiba','Japan')
    printed,result=lesson.execute_cell(lesson.WEATHER_CODE,scope)
    assert printed=='' and result==source['location_weather']['daily']
params=parse_qs(urlparse(calls[-1]).query)
assert params['past_days']==['1'] and params['forecast_days']==['3'] and params['timezone']==['auto']
assert all(len(values)==4 for values in result.values())
# A different city must change the lookup, not stay fixed to Kashiwa coordinates.
calls.clear()
with patch('urllib.request.urlopen',side_effect=tutorial_open):
    lesson.execute_cell(lesson.LOCATION_CODE.replace('city = "Kashiwa"','city = "Tokyo"'),{})
assert parse_qs(urlparse(calls[0]).query)['name']==['Tokyo']

for example in guide.EXAMPLES:
    saved=recorded['examples'][example['id']]
    assert saved['sha256']==hashlib.sha256(example['code'].encode()).hexdigest()
    assert not any(isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.Lambda)) for node in ast.walk(ast.parse(example['code'])))
    requests=iter(saved['requests']);answers=iter(saved['inputs'])
    def recorded_open(url,timeout):
        request=next(requests)
        assert url==request['url']
        return io.BytesIO(json.dumps(request['response']).encode())
    scope={'weather':copy.deepcopy(weather),'json':json,'urlencode':lesson.urlencode,'urlopen':recorded_open,'input':lambda prompt:next(answers)}
    printed,value=lesson.execute_cell(example['code'],scope)
    assert value is None and printed==saved['output'],example['id']
    assert next(requests,None) is None and next(answers,None) is None
    if example['id']=='cities':
        assert len(saved['requests'])==6
        expected=[]
        for n in range(0,6,2):
            city=saved['requests'][n]['response']['results'][0]['name']
            data=saved['requests'][n+1]['response']['daily']
            expected.append(f'{city} {data["time"][2]} {data["precipitation_probability_max"][2]} %')
        assert printed.strip().splitlines()==expected
# Missing values must never masquerade as a dry day.
missing=copy.deepcopy(weather)
missing['daily']['precipitation_probability_max'][1]=None
missing['daily']['rain_sum'][0]=None
for snippet in [guide.TODAY,guide.YESTERDAY]:
    printed,_=lesson.execute_cell(snippet,{'weather':missing,'place':source['location']})
    assert 'unavailable' in printed
# Exercise the rainy branches even if Kashiwa's snapshot happens to be dry.
rainy=copy.deepcopy(weather)
rainy['daily']['precipitation_probability_max'][1]=70
rainy['daily']['rain_sum'][0]=2.5
rainy['daily']['showers_sum'][0]=0.4
assert 'umbrella' in lesson.execute_cell(guide.TODAY,{'weather':rainy,'place':source['location']})[0]
assert '2.9 mm' in lesson.execute_cell(guide.YESTERDAY,{'weather':rainy,'place':source['location']})[0]
# The optional loop handles invalid choices and exits.
answers=iter(['bad','2','q'])
printed,_=lesson.execute_cell(guide.REPEAT,{'weather':weather,'input':lambda prompt:next(answers)})
assert 'Please enter' in printed and weather['daily']['time'][2] in printed
for filename in ['challenge.html','lecture.html','weather-code.html']:
    text=(folder/filename).read_text()
    assert '2026-11-12T12:00:00+09:00' in text
    assert 'practice.ipynb' not in text and 'starter-files.zip' not in text
    assert 'challenge-starter.ipynb' not in text
    assert ' download' not in text
    assert 'weather-code.html' in text or filename=='weather-code.html'
panel=(ROOT/'content/weeks/07-logic-loops.md').read_text()
assert panel.count('{notebook}')==0 and '{fundamentals}' not in panel
assert 'weather-code.html' in panel
assert 'while is optional' in panel
assert 'blank notebook' in panel
assert 'Create your own notebook from scratch' in (folder/'challenge.html').read_text()
page=(folder/'weather-code.html').read_text()
assert page.index('href="#data"') < page.index('href="#city"')
print('PASS: web tutorial, one-request first example, no provided notebook/downloads, real API outputs, missing/rainy cases and optional loop.')
