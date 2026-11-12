"""Verify web tutorial code as students enter it into a new blank Jupyter notebook.

This creates only temporary QA notebooks; no starter notebook is distributed.
"""
from pathlib import Path
import json,sys,tempfile
import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import weather_hackathon as lesson
folder=ROOT/'weeks/week-07'
weather=json.loads((folder/'weather-response.json').read_text())
source=json.loads((folder/'weather-source.json').read_text())
codes=[lesson.METEO_CODE,lesson.READ_CODE,lesson.LOCATION_CODE,lesson.WEATHER_CODE,lesson.FOR_CODE]
expected=[source['meteo_output'],source['read_output'],source['outputs'][0][0]['data']['text/plain'],source['outputs'][1][0]['data']['text/plain']]
with tempfile.TemporaryDirectory() as directory:
    setup=nbformat.v4.new_code_cell('''import io,json
from unittest.mock import patch
qa_responses=iter('''+repr([weather,source['location_response'],source['location_weather']])+''')
qa_network=patch("urllib.request.urlopen", side_effect=lambda *a, **k: io.BytesIO(json.dumps(next(qa_responses)).encode()))
qa_network.start()''')
    notebook=nbformat.v4.new_notebook(cells=[setup]+[nbformat.v4.new_code_cell(code) for code in codes])
    NotebookClient(notebook,timeout=30,kernel_name='python3',resources={'metadata':{'path':directory}}).execute()
    for cell,value in zip(notebook.cells[1:5],expected):
        assert cell.outputs[0]['data']['text/plain']==value
    assert all(not any(o.output_type=='error' for o in cell.outputs) for cell in notebook.cells)
    assert notebook.cells[-1].outputs[0]['text']==lesson.execute_cell(lesson.FOR_CODE,{'weather':source['location_weather']})[0]
    print('PASS: a new blank Jupyter notebook reproduces all displayed API, indexing, city and loop outputs.')
assert not (folder/'challenge-starter.ipynb').exists()
