"""Preserve submissions and hearts while merging only identical published work."""
from pathlib import Path
from unittest.mock import patch
import copy,json,sys,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/local-admin'))
import gallery_export as gallery
import review


def notebook(value='same',count=1):
    return {'cells':[{'cell_type':'markdown','source':'# Weather report'},
                     {'cell_type':'code','source':'weather','execution_count':count,
                      'outputs':[{'output_type':'execute_result','execution_count':count,
                                  'metadata':{},'data':{'text/plain':value}}]}]}


def entry(number,week=7,value='same',count=1):
    return {'id':str(number).zfill(20),'week':week,'featured':False,'has_notebook':True,
            'student_name':f'Name {number}','student_reading':'','notebook':notebook(value,count)}

first,second=entry(1),entry(2,count=8)
second['featured']=True
projects=gallery.group_identical([first,second,entry(3,value='different result'),entry(4,week=6)])
assert len(projects)==3
assert projects[0]['submission_ids']==[first['id'],second['id']]
assert projects[0]['submission_count']==2 and projects[0]['featured']
assert [person['name'] for person in projects[0]['submitters']]==['Name 1','Name 2']
different=entry(5);different['notebook']['cells'][0]['source']='# Different explanation'
assert len(gallery.group_identical([entry(1),different]))==2
missing=[dict(entry(n),has_notebook=False) for n in [6,7]]
assert len(gallery.group_identical(missing))==2

with tempfile.TemporaryDirectory() as directory:
    root=Path(directory);admin=root/'admin';output=admin/'_review';output.mkdir(parents=True)
    export=admin/'week08/2026_COURSE_7_20261118201647';export.mkdir(parents=True)
    students=['1111111111','2222222222']
    for index,student in enumerate(students):
        (export/f'{student}_1_1_weather.ipynb').write_text(json.dumps(notebook(count=index+1)))
    old={'week':3,'students':1,'submissions':[{'student':'3333333333'}]}
    (output/'index.json').write_text(json.dumps({'weeks':[old]}))
    with patch.multiple(review,ROOT=root,ADMIN=admin,OUTPUT=output,API_CACHE=output/'api-cache'), \
         patch.object(review,'read_roster',return_value=({s:{'name':f'Name {i}','reading':''} for i,s in enumerate(students)},[])), \
         patch.object(review,'replay',return_value={'cells':[],'notes':[],'generated':[]}):
        prepared=review.prepare(7)
    assert [week['week'] for week in prepared['weeks']]==[3,7]
    assert prepared['weeks'][0]['submissions']==old['submissions']
    # Publish this fixture's weather records only; the old week's real files are absent.
    weather=prepared['weeks'][1];(output/'index.json').write_text(json.dumps({'weeks':[weather]}))
    selected=json.dumps([7,students[1],f'{students[1]}_1_1_weather.ipynb'],separators=(',',':'))
    state=admin/'.gallery-hearts.json';state.write_text(json.dumps([selected]))
    public=root/'submissions/gallery.json';featured=root/'submissions/featured.json'
    with patch.multiple(gallery,ROOT=root,STATE=state,PUBLIC=public,FEATURED=featured):
        result=gallery.publish([selected],push=False)
    assert result['count']==1 and result['submissions']==2 and result['featured']==1
    record=json.loads(public.read_text())['submissions'][0]
    assert record['submission_count']==2 and len(record['submission_ids'])==2
    assert record['featured'] and record['submission_ids'][1] in json.loads(featured.read_text())['ids']
    downloaded=json.loads((root/record['notebook_path']).read_text())
    assert downloaded['nbformat']==4 and downloaded['cells'][1]['outputs'][0]['data']['text/plain']=='same'
    assert downloaded['metadata']['kernelspec']['name']=='python3'
    assert all(student not in public.read_text() for student in students)
print('PASS: strict grouping, distinct results/text kept, aliases and hearts preserved, assignment-week routing, old previews retained, valid Colab files.')
