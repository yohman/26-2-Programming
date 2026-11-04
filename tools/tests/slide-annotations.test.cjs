const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const source=fs.readFileSync(path.join(__dirname,'../../assets/slide-annotations.js'),'utf8');
const context={colours:['#c83249','#315876','#202a31','#28774f','#f1b82d']};
vm.createContext(context);
for(const name of ['validStroke','drawStroke']){
  const match=source.match(new RegExp('  function '+name+'\\([^]*?\\n  \\}'));
  assert(match,name+' exists');
  vm.runInContext(match[0],context);
}
const pen={tool:'pen',colour:'#c83249',width:0.006,points:[[0.1,0.2],[0.5,0.2]]};
assert(context.validStroke(pen));
assert(context.validStroke({tool:'clear'}));
assert(!context.validStroke({...pen,colour:'not-a-colour'}));
assert(!context.validStroke({...pen,width:NaN}));
assert(!context.validStroke({...pen,points:[[Infinity,0]]}));
assert(!context.validStroke({...pen,points:[[0,-1]]}));
assert(!context.validStroke({...pen,points:[]}));
assert(!context.validStroke(null));

const calls=[];
const ctx={
  save(){},restore(){},beginPath(){},moveTo(){},lineTo(){},arc(){},
  stroke(){calls.push({kind:'stroke',operation:this.globalCompositeOperation,alpha:this.globalAlpha,width:this.lineWidth});},
  fill(){calls.push({kind:'dot',width:this.lineWidth});},
  clearRect(){calls.push({kind:'clear'});}
};
context.drawStroke(ctx,pen,500,300);
assert.deepEqual(calls.pop(),{kind:'stroke',operation:'source-over',alpha:1,width:3});
context.drawStroke(ctx,{...pen,tool:'highlight'},500,300);
assert.equal(calls.pop().alpha,0.25);
context.drawStroke(ctx,{...pen,tool:'erase'},500,300);
assert.equal(calls.pop().operation,'destination-out');
context.drawStroke(ctx,{...pen,points:[[0.1,0.2]]},500,300);
assert.equal(calls.pop().kind,'dot');
context.drawStroke(ctx,{tool:'clear'},500,300);
assert.equal(calls.pop().kind,'clear');
console.log('PASS: saved-ink validation, pen, transparent highlighter, eraser, dots, and clear.');
