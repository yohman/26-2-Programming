"""Run both Week 7 notebooks in a real Jupyter kernel, including input loops.

Run with a Python environment containing nbclient and ipykernel.
The course notebooks themselves require no additional package installation.
"""
from pathlib import Path
import copy
import json
import shutil
import sys
import tempfile

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import weather_hackathon as lesson

fixture = json.loads((ROOT / 'weeks/week-07/weather-response.json').read_text())
hourly = fixture['hourly']
forecast = [dict(time=time, temp=temp, rain=rain) for time, temp, rain in zip(
    hourly['time'], hourly['temperature_2m'], hourly['precipitation_probability'])
    if temp is not None and rain is not None]
expected_count = sum(h['temp'] >= 10 and h['rain'] <= 30 for h in forecast)
warmer_count = sum(h['temp'] >= 11 and h['rain'] <= 30 for h in forecast)


def displayed_values(cell):
    return [o['data']['text/plain'] for o in cell['outputs'] if o['output_type'] == 'execute_result']


def displayed_html(cell):
    return [o['data']['text/html'] for o in cell['outputs'] if 'text/html' in o.get('data', {})]


with tempfile.TemporaryDirectory() as directory:
    work = Path(directory)
    # Student code stays unchanged. Only input and the network are controlled by QA.
    setup = nbformat.v4.new_code_cell('''from unittest.mock import patch
from urllib.error import URLError
qa_answers = iter(["?", "show", "warmer", "quit"])
input = lambda prompt: next(qa_answers)
qa_network = patch("urllib.request.urlopen", side_effect=URLError("offline QA"))
qa_network.start()''')
    for filename in ['practice.ipynb', 'challenge-starter.ipynb']:
        shutil.copy(ROOT / 'weeks/week-07/weather-response.json', work)
        original = nbformat.read(ROOT / 'weeks/week-07' / filename, as_version=4)
        notebook = copy.deepcopy(original)
        notebook.cells.insert(0, setup)
        NotebookClient(notebook, timeout=30, kernel_name='python3',
                       resources={'metadata': {'path': str(work)}}).execute()
        actual = notebook.cells[1:]
        for saved, executed in zip(original.cells, actual):
            if saved.cell_type != 'code':
                continue
            assert not any(o.output_type == 'error' for o in executed.outputs)
            if filename == 'practice.ipynb' and 'interactive' not in saved.metadata.get('tags', []):
                assert displayed_values(executed) == displayed_values(saved), saved.source
                assert displayed_html(executed) == displayed_html(saved), saved.source
        filter_cell = next(c for c in actual if c.cell_type == 'code' and c.source == lesson.FILTER_CODE)
        assert displayed_values(filter_cell) == [str(expected_count)]
        loop = next(c for c in actual if c.cell_type == 'code' and c.source == lesson.WHILE_CODE)
        boards = displayed_html(loop)
        assert len(boards) == 2
        for board, count in zip(boards, [expected_count, warmer_count]):
            assert f'{count} / {len(forecast)} hours match' in board
            assert board.count('<td style="padding:7px 8px">') == len(forecast)
        if filename == 'challenge-starter.ipynb':
            load = next(c for c in actual if c.cell_type == 'code' and c.source == lesson.LIVE_LOAD)
            assert 'Saved JSON' in ''.join(o.get('text', '') for o in load.outputs)
            assert displayed_values(load) == ['24']
        print('PASS: real Jupyter execution:', filename)
    # Run the actual displayed API cell against Open-Meteo with a clean kernel.
    live = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(lesson.API_EXAMPLE)])
    NotebookClient(live, timeout=30, kernel_name='python3',
                   resources={'metadata': {'path': str(work)}}).execute()
    assert displayed_values(live.cells[0]) == ['24']
    print('PASS: real Jupyter API request returned 24 hours')
