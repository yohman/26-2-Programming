"""Team credits, submitted variants, and next-day refreshes must preserve the work."""
from pathlib import Path
from unittest.mock import patch
import json,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/local-admin'))
import gallery_export as gallery
import gallery_teams as teams
import review

roster={
 '1111111111':{'name':'高谷 柚希','reading':'TAKAYA YUZUKI','kana':'たかや ゆずき'},
 '2222222222':{'name':'馬塲 信吾','reading':'BABA SHINGO','kana':'ばば しんご'},
 '3333333333':{'name':'井上 太陽','reading':'INOUE HINATA','kana':'いのうえ ひなた'},
 '4444444444':{'name':'杉浦 琉生','reading':'SUGIURA RYUUSEI','kana':'すぎうら りゅうせい'}}

def notebook(header,result='sun'):
 return {'cells':[{'cell_type':'markdown','source':header},
                  {'cell_type':'code','source':'weather','outputs':[{'output_type':'stream','name':'stdout','text':result}],'execution_count':1}]}

assert teams.declared_members(notebook('メンバー：しんご、ゆずき、ひなた'),roster)==set(list(roster)[:3])
assert teams.declared_members(notebook('氏名：高谷柚希・馬場信吾・井上太陽'),roster)==set(list(roster)[:3])
assert teams.declared_members(notebook('メンバー: sugiura ryusei'),roster)=={'4444444444'}
assert teams.declared_members(notebook('#### メンバー\n\n高谷柚希 馬場信吾 井上太陽\n\n#### 機能'),roster)==set(list(roster)[:3])
# A first name shared by two roster entries is never guessed.
ambiguous=dict(roster);ambiguous['5555555555']={'name':'別の 太陽','reading':'OTHER HINATA','kana':'べつの ひなた'}
assert '3333333333' not in teams.declared_members(notebook('メンバー：ひなた'),ambiguous)

with tempfile.TemporaryDirectory() as directory:
 root=Path(directory);admin=root/'admin';output=admin/'_review';output.mkdir(parents=True)
 folder=admin/'week07';old=folder/'2026_COURSE_7_20261118201647';old.mkdir(parents=True)
 for student in list(roster)[:2]:(old/f'{student}_1_1_old.ipynb').write_text('{}')
 archive=folder/'2026_COURSE_7_20261119080000.zip'
 with zipfile.ZipFile(archive,'w') as package:package.writestr('1111111111_1_1_new.ipynb','{}')
 before=archive.read_bytes();review.extract_new_exports(folder);assert archive.read_bytes()==before
 chosen=review.latest_student_files(folder)
 assert chosen['1111111111'][0].name.endswith('new.ipynb')
 assert chosen['2222222222'][0].name.endswith('old.ipynb')
 review.extract_new_exports(folder) # Repeat refresh keeps originals intact.
 bike=admin/'week08'/'2026_COURSE_9_20261126115142';bike.mkdir(parents=True)
 assert review.submission_week(bike.parent)==9
 (admin/'.unipa-assignment-weeks.json').write_text(json.dumps({'2026_COURSE_9':8}))
 assert review.submission_week(bike.parent)==8 and review.submission_week(folder)==7
 # The declared third author gets credit without a separate submission.
 (admin/'roster.csv').write_text('学籍番号,学生氏名,学生氏名_英語,学生氏名_カナ\n'+''.join(f"{sid},{p['name']},{p['reading']},{p['kana']}\n" for sid,p in roster.items()))
 def index_for(filename,authors=True,third=False,week=7):
  items=[]
  for i,student in enumerate(list(roster)[:3 if third else 2]):
   identity=f'private-{week}-{i}-{filename}';target=output/identity;target.mkdir(exist_ok=True)
   item={'id':identity,'student':student,'file':f'{student}_1_1_{filename}.ipynb'};items.append(item)
   nb=notebook('メンバー：しんご、ゆずき、ひなた' if authors else '# Updated umbrella report','sun' if i==0 else 'rain')
   record={'notebook':nb,'student_name':roster[student]['name'],'student_reading':roster[student]['reading'],'title':'Umbrella forecast','replay':{'cells':[]}}
   (target/'submission.json').write_text(json.dumps(record))
  (output/'index.json').write_text(json.dumps({'weeks':[{'week':week,'submissions':items}]}))
  return items
 items=index_for('old')
 key=json.dumps([7,items[0]['student'],items[0]['file']],separators=(',',':'))
 state=admin/'.gallery-hearts.json';state.write_text(json.dumps([key]))
 public=root/'submissions/gallery.json';featured=root/'submissions/featured.json'
 with patch.multiple(gallery,ROOT=root,STATE=state,PUBLIC=public,FEATURED=featured):
  first=gallery.publish([key],push=False)
  project=json.loads(public.read_text())['submissions'][0]
  assert first['count']==1 and first['submissions']==2
  assert len(project['members'])==3 and len(project['variants'])==2
  assert {p['name'] for p in project['members']}=={r['name'] for sid,r in roster.items() if sid!='4444444444'}
  old_id=project['id'];old_aliases=set(project['submission_ids'])
  files=[json.loads((root/v['notebook_path']).read_text()) for v in project['variants']]
  assert {nb['cells'][1]['outputs'][0]['text'] for nb in files}=={'sun','rain'}
  # New filenames tomorrow retain group URL, old links, membership and the heart.
  index_for('updated',False,True);second=gallery.publish([key],push=False)
  project=json.loads(public.read_text())['submissions'][0]
  assert project['id']==old_id and old_aliases<=set(project['submission_ids'])
  assert project['submission_count']==3 and len(project['members'])==3 and len(project['variants'])==2
  assert project['featured'] and second['featured']==1
  assert 'updated.ipynb' in json.loads(state.read_text())[0]
  gallery.publish([],push=False)
  assert not json.loads(public.read_text())['submissions'][0]['featured']
  empty_items=index_for('empty-third',True,True)
  empty_record=output/empty_items[-1]['id']/'submission.json'
  damaged=json.loads(empty_record.read_text());damaged['notebook']=None;empty_record.write_text(json.dumps(damaged))
  gallery.publish([],push=False)
  damaged_group=json.loads(public.read_text())['submissions'][0]
  unreadable=[v for v in damaged_group['variants'] if v.get('preview_status')=='unreadable']
  assert damaged_group['has_notebook'] and damaged_group['submission_count']==3 and len(damaged_group['members'])==3
  assert len(unreadable)==1 and unreadable[0]['notebook_path'] is None and unreadable[0]['has_notebook'] is False
  index_for('bike',week=8)
  gallery.publish([],push=False,only_week=8)
  later=json.loads(public.read_text())['submissions']
  assert later[0]==damaged_group
  assert later[1]['week']==8 and len(later[1]['members'])==3 and len(later[1]['variants'])==2


# A corrupt/empty group upload cannot become the default or inherit a teammate's path.
valid={'id':'a'*20,'week':7,'title':'Weather radar','has_notebook':True,'featured':False,'student_name':'高谷 柚希','student_reading':'','notebook':{'cells':[{'cell_type':'code','source':'weather','outputs':[]}]}}
invalid={'id':'b'*20,'week':7,'title':'Empty upload','has_notebook':False,'featured':False,'student_name':'馬塲 信吾','student_reading':'','notebook':{'cells':[{'cell_type':'markdown','source':'No preview available'}]}}
context={valid['id']:{'student':'1111111111','authors':{'1111111111','2222222222'}},invalid['id']:{'student':'2222222222','authors':set()}}
group=teams.group_projects([invalid,valid],context,roster,[],gallery.notebook_fingerprint)[0]
assert group['_primary_id']==valid['id'] and group['has_notebook']
assert group['submission_count']==2 and len(group['members'])==2

# A team member's unrelated second notebook keeps a separate entry.
team=dict(valid,id='c'*20,week=8)
copy=dict(team,id='d'*20,student_name='馬塲 信吾')
extra=dict(team,id='e'*20,title='Independent report',notebook=notebook('# Separate idea','another result'))
context={
 team['id']:{'student':'1111111111','authors':{'1111111111','2222222222'}},
 copy['id']:{'student':'2222222222','authors':{'1111111111','2222222222'}},
 extra['id']:{'student':'1111111111','authors':set()},
}
prior=[{'id':team['id'],'week':8,'members':[{'name':roster[s]['name']} for s in ['1111111111','2222222222']]}]
projects=teams.group_projects([team,copy,extra],context,roster,prior,gallery.notebook_fingerprint)
assert [len(group['_sources']) for group in projects]==[2,1]
assert len(projects[1]['members'])==1
independent=dict(extra,id='f'*20,student_name=roster['3333333333']['name'],
                 notebook=notebook('# Updated independent work','changed output'))
context[independent['id']]={'student':'3333333333','authors':set()}
verified=teams.group_projects([extra,independent],context,roster,[],gallery.notebook_fingerprint,
                             verified_groups=[(extra['id'],independent['id'])])
assert len(verified)==1 and len(verified[0]['members'])==2

print('PASS: author names/kana/roman variants, no ambiguous-name guesses, latest ZIP selection, full member credits, distinct versions, stable links and hearts across tomorrow’s refresh.')
