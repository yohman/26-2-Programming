const assert=require('node:assert/strict');
const test=require('node:test');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const models=require('../../assets/course-models.js');
const root=path.resolve(__dirname,'../..');
const menu=[{name:'Onigiri',price:150,minutes:3},{name:'Sandwich',price:320,minutes:5},{name:'Curry',price:550,minutes:12},{name:'Udon',price:450,minutes:10}];
test('budget, coin and game boundaries are explicit',()=>{
 assert.deepEqual(models.affordable(menu,149),[]);
 assert.deepEqual(models.affordable(menu,150),['Onigiri']);
 assert.deepEqual(models.affordable(menu,500,5),['Onigiri','Sandwich']);
 assert.deepEqual(models.affordable([],1000),[]);
 assert.deepEqual(models.vending([100,50,100]),{paid:150,lines:['Paid: 100','Paid: 150','Change: 0']});
 assert.deepEqual(models.vending([100]),{paid:100,lines:['Paid: 100','Due: 50']});
 assert.equal(models.vending([100,100]).lines.at(-1),'Change: 50');
 assert.equal(models.hit(5,0),5);assert.equal(models.hit(5,1),6);assert.equal(models.tick(0),0);
 assert.equal(models.inside(10,10,10,10,30,30),true);assert.equal(models.inside(9,10,10,10,30,30),false);
 assert.equal(models.largeBoxes([{w:80,h:90},{w:60,h:70}],5000).length,1);
});
test('all eight new lecture and challenge pages preserve their release gates',()=>{
 const script=fs.readFileSync(path.join(root,'assets/course-decks.js'),'utf8');
 for(let week=7;week<=14;week++){
  const folder=path.join(root,'weeks/week-'+String(week).padStart(2,'0'));
  const source=fs.readFileSync(path.join(folder,'lecture.html'),'utf8');
  const release=source.match(/data-release="([^"]+)"/)[1];
  const main={innerHTML:''},toggle={hidden:false};
  const clock={now:()=>Date.parse('2026-11-06T00:00:00+09:00'),parse:Date.parse};
  const ctx={URLSearchParams,Date:clock,location:{search:''},document:{body:{dataset:{release,week}},querySelector:()=>main,getElementById:()=>toggle}};
  vm.runInNewContext(script,ctx);
  assert.match(main.innerHTML,/Available/);assert.equal(toggle.hidden,true);
  assert.ok(fs.readFileSync(path.join(folder,'challenge.html'),'utf8').includes('data-release="'+release+'"'));
  assert.ok(source.includes('slide-annotations.js'));assert.ok(source.includes('slide-swipe.js'));
 }
});
