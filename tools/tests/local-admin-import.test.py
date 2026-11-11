"""Saved GitHub pages must yield notebook JSON without page/account metadata."""
from pathlib import Path
import importlib.util,json,tempfile

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('review',ROOT/'tools/local-admin/review.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
notebook={'nbformat':4,'cells':[{'cell_type':'markdown','source':'\n# My report'},{'cell_type':'code','source':'len([1, 2])','outputs':[]}]}
with tempfile.TemporaryDirectory() as directory:
    file=Path(directory)/'report.ipynb'
    file.write_text(json.dumps(notebook))
    recovered,note=review.read_notebook(file)
    assert recovered==notebook and note is None
    page={'payload':{'codeViewBlobLayoutRoute.StyledBlob':{'rawLines':json.dumps(notebook,indent=2).splitlines()}},'account':'must remain private'}
    original='<html><script type="application/json">'+json.dumps(page)+'</script><script>throw new Error("never run")</script></html>'
    file.write_text(original)
    recovered,note=review.read_notebook(file)
    assert recovered==notebook and 'saved GitHub page' in note
    assert 'must remain private' not in json.dumps(recovered)
    assert file.read_text()==original
    file.write_text('<html>Not a notebook</html>')
    try: review.read_notebook(file)
    except ValueError: pass
    else: raise AssertionError('A page without notebook JSON was accepted')
print('PASS: notebook and saved-GitHub imports, metadata isolation, invalid-file handling and untouched originals.')
