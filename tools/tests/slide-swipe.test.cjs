const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const handlers={};let ink=false,selection=false,nextCount=0,previousCount=0;
const stage={style:{},addEventListener(name,handler){handlers[name]=handler;}};
const view={querySelector(){return stage;},classList:{contains(){return ink;}}};
const next={disabled:false,click(){nextCount++;}},previous={disabled:false,click(){previousCount++;}};
const document={getElementById(id){return {'slides-view':view,'next-slide':next,'previous-slide':previous}[id];}};
vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'../../assets/slide-swipe.js'),'utf8'),{document,window:{getSelection:()=>({isCollapsed:!selection})}});
const touch=(x,y,id=1)=>({clientX:x,clientY:y,identifier:id});
function swipe({dx=-120,dy=5,interactive=false,duration=200,multi=false,cancel=false}={}){
 handlers.touchstart({touches:[touch(200,100)],target:{closest:()=>interactive},timeStamp:100});
 if(multi)handlers.touchmove({touches:[touch(180,100),touch(200,120,2)]});
 if(cancel)handlers.touchcancel();
 handlers.touchend({touches:[],changedTouches:[touch(200+dx,100+dy)],timeStamp:100+duration});
}
swipe();assert.equal(nextCount,1);
swipe({dx:120});assert.equal(previousCount,1);
for(const options of [{dy:180},{dx:30},{interactive:true},{duration:1500},{multi:true},{cancel:true}])swipe(options);
assert.equal(nextCount,1);assert.equal(previousCount,1);
ink=true;swipe();ink=false;selection=true;swipe();selection=false;
assert.equal(nextCount,1);
next.disabled=true;swipe();assert.equal(nextCount,1);next.disabled=false;
swipe();assert.equal(nextCount,2);
assert.equal(stage.style.touchAction,'pan-y pinch-zoom');
console.log('PASS: swipe direction, vertical/short/slow gesture rejection, controls, pinch, cancel, ink, selection, boundaries, and recovery.');
