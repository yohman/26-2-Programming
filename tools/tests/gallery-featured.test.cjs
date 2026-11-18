const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync(require('node:path').join(__dirname,'../../assets/gallery.js'),'utf8').split('function assignmentTitle')[0];
function context(fetch){const ctx=vm.createContext({document:{getElementById:()=>({})},fetch,Set,Date,renderGallery:()=>{}});vm.runInContext(source,ctx);return ctx;}
test('the small selection feed overrides old flags, including removing the last heart',async()=>{
 const a='a'.repeat(20),b='b'.repeat(20);let ids=[b];
 const ctx=context(async()=>({ok:true,json:async()=>({ids})}));
 vm.runInContext(`galleryVersion='loaded';galleryRecords=[{id:'${a}',featured:true},{id:'${b}',featured:false}]`,ctx);
 await vm.runInContext('updateFeatured()',ctx);
 assert.equal(vm.runInContext('JSON.stringify(galleryRecords.map(r=>r.featured))',ctx),'[false,true]');
 ids=[];await vm.runInContext('updateFeatured()',ctx);
 assert.equal(vm.runInContext('JSON.stringify(galleryRecords.map(r=>r.featured))',ctx),'[false,false]');
});
test('a missing new feed preserves the legacy gallery until it is available',async()=>{
 const ctx=context(async()=>({ok:false,status:404}));
 vm.runInContext("galleryRecords=[{id:'old',featured:true}]",ctx);await vm.runInContext('updateFeatured()',ctx);
 assert.equal(vm.runInContext('galleryRecords[0].featured',ctx),true);
});
test('a heart on any identical submission features the grouped project',async()=>{
 const a='a'.repeat(20),b='b'.repeat(20);
 const ctx=context(async()=>({ok:true,json:async()=>({ids:[b]})}));
 vm.runInContext(`galleryRecords=[{id:'${a}',submission_ids:['${a}','${b}'],featured:false}]`,ctx);
 await vm.runInContext('updateFeatured()',ctx);
 assert.equal(vm.runInContext('galleryRecords[0].featured',ctx),true);
});
const gallerySource=fs.readFileSync(require('node:path').join(__dirname,'../../assets/gallery.js'),'utf8');
test('Colab links use committed notebook paths and reject outside paths',()=>{
 const helper=gallerySource.slice(gallerySource.indexOf('function colabURL'),gallerySource.indexOf('const featuredBadge'));
 const ctx=vm.createContext({});vm.runInContext(helper,ctx);
 assert.equal(vm.runInContext(`colabURL({notebook_path:'submissions/notebooks/${'a'.repeat(20)}.ipynb'})`,ctx),`https://colab.research.google.com/github/yohman/26-2-Programming/blob/main/submissions/notebooks/${'a'.repeat(20)}.ipynb`);
 for(const path of ['https://other.example/a.ipynb','../admin/private.ipynb','submissions/notebooks/bad.ipynb']){
  ctx.path=path;assert.equal(vm.runInContext('colabURL({notebook_path:path})',ctx),null);
 }
});
test('notebooks load on demand, share requests, and survive refreshed gallery records',async()=>{
 const helper=gallerySource.slice(gallerySource.indexOf('async function loadNotebook'),gallerySource.indexOf('function downloadableNotebook'));
 let requests=[];
 const ctx=vm.createContext({Map,Promise,Error,fetch:async path=>{requests.push(path);return {ok:true,json:async()=>path.endsWith('.ipynb')?{cells:[{cell_type:'code',source:'weather'}]}:{cells:[{cell:0,outputs:[]}]}}}});
 vm.runInContext('const notebookLoads=new Map();'+helper,ctx);
 vm.runInContext("var a={id:'same',notebook_path:'one.ipynb',replay_path:'preview.json'};var b={...a}",ctx);
 assert.equal(requests.length,0);
 await vm.runInContext('Promise.all([loadNotebook(a),loadNotebook(b)])',ctx);
 assert.equal(requests.length,2);
 assert.equal(vm.runInContext('a.notebook.cells[0].source',ctx),'weather');
 assert.equal(vm.runInContext('b.notebook.cells[0].source',ctx),'weather');
 await vm.runInContext('loadNotebook({...b,notebook:undefined,replay:undefined})',ctx);
 assert.equal(requests.length,2);
});
