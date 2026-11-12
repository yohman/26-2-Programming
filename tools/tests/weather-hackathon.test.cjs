const test=require('node:test');
const assert=require('node:assert/strict');
const clock=require('../../weeks/week-07/hackathon.js');
test('countdown uses a deadline, survives reload, pauses and resumes without drift',()=>{
 let state=clock.reset(60000);
 state=clock.start(state,1000);
 assert.equal(clock.remaining(state,11000),50000);
 const restored=JSON.parse(JSON.stringify(state));
 assert.equal(clock.remaining(restored,31000),30000);
 state=clock.pause(restored,31000);
 assert.equal(clock.remaining(state,81000),30000);
 state=clock.start(state,81000);
 assert.equal(clock.remaining(state,96000),15000);
 assert.equal(clock.remaining(state,120000),0);
 assert.equal(clock.format(clock.remaining(state,120000)),'00:00');
 assert.equal(clock.format(1),'00:01');
 assert.equal(clock.format(3600000),'60:00');
 assert.deepEqual(clock.reset(90000),{durationMs:90000,remainingMs:90000,deadline:null});
});
