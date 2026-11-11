"""Heart saves must stay fast while Git is blocked, preserve choices, and retry."""
from pathlib import Path
from unittest.mock import patch
import json,sys,tempfile,threading,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/local-admin'))
import gallery_export as gallery
from heart_publication import HeartPublisher

def wait_until(check,timeout=3):
    limit=time.monotonic()+timeout
    while not check():
        if time.monotonic()>limit:raise AssertionError('Background publication did not finish')
        time.sleep(.005)

with tempfile.TemporaryDirectory() as directory:
    root=Path(directory);(root/'admin/_review').mkdir(parents=True);(root/'submissions').mkdir()
    key_a=json.dumps([6,'111111111111','a.ipynb'],separators=(',',':'))
    key_b=json.dumps([5,'222222222222','b.ipynb'],separators=(',',':'))
    index={'weeks':[{'week':6,'submissions':[{'student':'111111111111','file':'a.ipynb'}]},{'week':5,'submissions':[{'student':'222222222222','file':'b.ipynb'}]}]}
    (root/'admin/_review/index.json').write_text(json.dumps(index))
    state=root/'admin/.gallery-hearts.json';state.write_text(json.dumps([key_b]))
    public=root/'submissions/gallery.json';public.write_text('notebook content must remain untouched')
    featured=root/'submissions/featured.json'
    with patch.multiple(gallery,ROOT=root,STATE=state,PUBLIC=public,FEATURED=featured):
        entered=threading.Event();release=threading.Event();calls=[]
        def publish():
            calls.append(1);entered.set();assert release.wait(3)
        service=HeartPublisher(gallery.save_hearts,publish,root/'admin/outbox.json',gallery.write_json_atomic,delay=.01,retry=.01)
        try:
            start=time.monotonic();service.save({'changes':{key_a:True}})
            assert time.monotonic()-start<.25
            assert entered.wait(1)
            start=time.monotonic();response=service.save({'changes':{key_a:False}})
            assert time.monotonic()-start<.25
            assert response['hearts']==[key_b]
            assert json.loads(state.read_text())==[key_b]
            assert public.read_text()=='notebook content must remain untouched'
            assert json.loads(featured.read_text())['ids']==[gallery.public_id(json.loads(key_b))]
            assert '222222222222' not in featured.read_text()
            release.set();wait_until(lambda:service.status()['state']=='idle')
            assert len(calls)==2 and service.status()['published']==2
        finally:release.set();service.close()
        attempts=[]
        def flaky():
            attempts.append(1)
            if len(attempts)==1:raise OSError('network offline')
        service=HeartPublisher(gallery.save_hearts,flaky,root/'admin/retry.json',gallery.write_json_atomic,delay=.01,retry=.01)
        try:
            service.save({'changes':{key_a:True}});wait_until(lambda:len(attempts)==2 and service.status()['state']=='idle')
            assert set(json.loads(state.read_text()))=={key_a,key_b}
        finally:service.close()
        gallery.write_json_atomic(root/'admin/resume.json',{'revision':4,'published':3})
        resumed=threading.Event();service=HeartPublisher(gallery.save_hearts,resumed.set,root/'admin/resume.json',gallery.write_json_atomic,delay=.01)
        try:wait_until(lambda:resumed.is_set() and service.status()['published']==4)
        finally:service.close()
        with patch.object(gallery,'push_files') as push:
            gallery.publish_featured();assert push.call_args.args[0]==['submissions/featured.json']
        for number,week in enumerate(index['weeks']):
            item=week['submissions'][0];item['id']=f'record-{number}'
            folder=root/'admin/_review'/item['id'];folder.mkdir()
            record={'notebook':{'cells':[{'cell_type':'code','source':f'print("{item["student"]}")','outputs':[],'execution_count':None}]},'replay':{'cells':[]},'student_name':'Example','student_reading':'','title':'Example report'}
            (folder/'submission.json').write_text(json.dumps(record))
        (root/'admin/_review/index.json').write_text(json.dumps(index))
        exported=gallery.publish([key_b],push=False)
        assert exported['count']==2 and exported['featured']==1
        assert '222222222222' not in public.read_text()
        assert json.loads(featured.read_text())['ids']==[gallery.public_id(json.loads(key_b))]

print('PASS: nonblocking durable saves, last selection wins, prior hearts preserved, tiny public IDs, retry and restart recovery.')
