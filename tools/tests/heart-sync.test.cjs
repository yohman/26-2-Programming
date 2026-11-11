const test=require('node:test'),assert=require('node:assert/strict');
const {create}=require('../local-admin/heart-sync.js');
function timers(){let id=0;const jobs=new Map();return {setTimeout(fn){jobs.set(++id,fn);return id;},clearTimeout(id){jobs.delete(id);},jobs};}
test('rapid on/off and another selection stay immediate while a save is blocked',async()=>{
 const clock=timers(),requests=[];let resolve,stored;
 const sync=create({timers:clock,send:changes=>{requests.push(changes);return new Promise(r=>resolve=r);},persist:(values,pending)=>stored={values,pending}});
 sync.toggle('A');assert.deepEqual([...sync.values],['A']);
 const first=sync.flush();
 sync.toggle('A');sync.toggle('B');
 assert.deepEqual([...sync.values],['B']);assert.equal(requests.length,1);
 assert.deepEqual(stored.pending,{A:false,B:true});
 resolve({hearts:['A'],sync:{state:'publishing'}});await first;
 assert.deepEqual([...sync.values],['B']);
 const second=sync.flush();assert.deepEqual(requests[1],{A:false,B:true});
 resolve({hearts:['B'],sync:{state:'pending'}});await second;
 assert.deepEqual(stored.pending,{});assert.deepEqual([...sync.values],['B']);assert.equal(sync.busy,false);sync.stop();
});
test('save failure retains the intended selection and survives navigation/reload',async()=>{
 const clock=timers();let stored,status;
 const sync=create({timers:clock,send:async()=>{throw new Error('offline');},persist:(values,pending)=>stored={values,pending},onStatus:s=>status=s});
 sync.toggle('A');await sync.flush();assert.deepEqual([...sync.values],['A']);assert.ok(status.error);assert.equal(clock.jobs.size,1);
 sync.stop();
 const restored=create({initial:['B'],pending:stored.pending,timers:clock,send:async changes=>({hearts:['A','B'],sync:{state:'idle'}})});
 assert.deepEqual(new Set(restored.values),new Set(['A','B']));await restored.flush();assert.deepEqual(restored.pending,{});restored.stop();
});
test('server updates preserve unsaved local choices without repeated redraws',()=>{
 let paints=0;const sync=create({initial:['B'],timers:timers(),send:async()=>{},onChange:()=>paints++});
 sync.toggle('A');sync.accept(['B','C']);assert.deepEqual(new Set(sync.values),new Set(['A','B','C']));
 const before=paints;sync.accept(['B','C']);assert.equal(paints,before);sync.stop();
});
