"""Verify the single starter in real Jupyter, with recorded and live responses."""
from pathlib import Path
import ast,copy,json,sys,tempfile
import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import weather_hackathon as lesson
folder=ROOT/'weeks/week-07'
weather=json.loads((folder/'weather-response.json').read_text())
source=json.loads((folder/'weather-source.json').read_text())
original=nbformat.read(folder/'challenge-starter.ipynb',as_version=4)
nbformat.validate(original)
assert sum(cell.cell_type=='code' for cell in original.cells)==2
with tempfile.TemporaryDirectory() as directory:
    setup=nbformat.v4.new_code_cell('''import io,json
from unittest.mock import patch
qa_responses=iter('''+repr([source['location_response'],weather])+''')
qa_network=patch("urllib.request.urlopen", side_effect=lambda *a, **k: io.BytesIO(json.dumps(next(qa_responses)).encode()))
qa_network.start()''')
    notebook=copy.deepcopy(original)
    notebook.cells.insert(0,setup)
    NotebookClient(notebook,timeout=30,kernel_name='python3',resources={'metadata':{'path':directory}}).execute()
    for saved,actual in zip(original.cells,notebook.cells[1:]):
        if saved.cell_type=='code':
            assert [o.get('data') for o in actual.outputs]==[o.get('data') for o in saved.outputs]
            assert not any(o.output_type=='error' for o in actual.outputs)
    print('PASS: real Jupyter reproduces both saved expression outputs exactly.')
    live=copy.deepcopy(original)
    NotebookClient(live,timeout=45,kernel_name='python3',resources={'metadata':{'path':directory}}).execute()
    codes=[cell for cell in live.cells if cell.cell_type=='code']
    assert "Kashiwa" in codes[0].outputs[0]['data']['text/plain']
    daily=ast.literal_eval(codes[1].outputs[0]['data']['text/plain'])
    assert len(daily['time'])==4 and len(daily['temperature_2m_max'])==4
    assert all(not any(o.output_type=='error' for o in cell.outputs) for cell in codes)
    print('PASS: unchanged student notebook fetches a city and four daily weather rows from the live API.')
