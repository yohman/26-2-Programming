const test=require('node:test'),assert=require('node:assert/strict'),crypto=require('node:crypto').webcrypto;
const groups=require('../local-admin/admin-groups.js');
const {create}=require('../local-admin/heart-sync.js');
const sid=['1111111111','2222222222','3333333333'];
function fakeTimers(){return {setTimeout(){return 1;},clearTimeout(){}};}
test('private and public identity hashes agree for Japanese notebook filenames',async()=>{
 assert.equal(await groups.publicID(7,sid[0],'天気.ipynb',crypto),'70de14b9c8bcce4e657a');
});
test('the admin uses gallery teams, all member names and distinct notebook versions',async()=>{
 const sources=sid.map((student,i)=>({id:String(i+1).repeat(20),student,file:'weather.ipynb',student_name:'Student '+i,student_reading:''}));
 const ids=await Promise.all(sources.map(source=>groups.publicID(7,source.student,source.file,crypto)));
 const people=sources.map(source=>({name:source.student_name,reading:''}));
 const project={id:'a'.repeat(20),week:7,title:'Weather team',members:people,submission_ids:[...ids,'f'.repeat(20)],notebook_path:'submissions/notebooks/'+ids[2]+'.ipynb',
  variants:[{id:ids[0],submitters:people.slice(0,2),has_notebook:true},{id:ids[2],submitters:people.slice(2),has_notebook:true}]};
 const model=await groups.build({weeks:[{week:7,students:3,submissions:sources}]},{submissions:[project]},crypto);
 const week=model.weeks[0],group=week.groups[0];assert.equal(week.groups.length,1);assert.equal(group.submission_count,3);
 assert.deepEqual(group.members,people);assert.equal(group.primary_id,sources[2].id);assert.equal(group.heart_keys.length,3);
 assert.deepEqual(group.variants[0].source_ids,sources.slice(0,2).map(source=>source.id));assert.equal(group.variants.length,2);
 assert.ok(!group.unpublished);assert.ok(groups.isSelected(group,new Set([groups.keyFor(sources[1],7)])));
});
test('one group click clears every member heart and keeps other groups selected',async()=>{
 const record={heart_keys:['member A','member B','member C']};let sent;
 const sync=create({initial:['member B','member C','another team'],timers:fakeTimers(),send:async changes=>{sent=changes;return {hearts:['another team']};}});
 sync.setMany(groups.changesFor(record,sync.values));
 assert.deepEqual([...sync.values],['another team']);assert.ok(!groups.isSelected(record,sync.values));
 await sync.flush();assert.deepEqual(sent,{'member A':false,'member B':false,'member C':false});
 sync.setMany(groups.changesFor(record,sync.values));assert.deepEqual(new Set(sync.values),new Set(['another team','member A']));
 sync.stop();
});
