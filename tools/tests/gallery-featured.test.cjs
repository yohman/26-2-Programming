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
