const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {webcrypto,pbkdf2Sync,createCipheriv,randomBytes}=require('node:crypto');
const {decryptQuiz}=require('../../weeks/week-08/quiz.js');
const root=path.resolve(__dirname,'../..');
const browser={document:{addEventListener(){}}};
vm.runInNewContext(fs.readFileSync(path.join(root,'assets/site.js'),'utf8'),browser);
function fixture(text,password){
 const salt=randomBytes(16),iv=randomBytes(12),iterations=250000;
 const key=pbkdf2Sync(password,salt,iterations,32,'sha256'),cipher=createCipheriv('aes-256-gcm',key,iv);
 const ciphertext=Buffer.concat([cipher.update(text),cipher.final(),cipher.getAuthTag()]);
 return {version:1,algorithm:'AES-GCM',kdf:'PBKDF2',iterations,salt:salt.toString('base64'),iv:iv.toString('base64'),ciphertext:ciphertext.toString('base64')};
}
test('browser quiz decrypts only with the correct password',async()=>{
 const text=JSON.stringify({nbformat:4,cells:[{cell_type:'code',source:'',outputs:[]}]}),payload=fixture(text,'test-only-passphrase');
 assert.equal((await decryptQuiz(payload,'test-only-passphrase',webcrypto)).text,text);
 await assert.rejects(()=>decryptQuiz(payload,'incorrect',webcrypto));
 const damaged={...payload,ciphertext:Buffer.from('corrupt payload').toString('base64')};
 await assert.rejects(()=>decryptQuiz(damaged,'test-only-passphrase',webcrypto));
});
test('quiz preview separates consecutive fences from prose and preserves code whitespace',()=>{
 const fence='`'.repeat(3);
 const markdown=['## Example','Before',fence+'python','for n in range(2):','    print(n)','','    print(n + 1)',fence,'Between',fence,'<b>text only</b>','  indented',fence,'After'].join('\r\n');
 const result=browser.markdownHtml(markdown);
 assert.equal((result.match(/<pre class="code-block"/g)||[]).length,2);
 assert.match(result,/<h3>Example<\/h3><p>Before<\/p><pre/);
 assert.match(result,/aria-label="python code"/);
 assert.match(result,/<\/span>\(n\)\n\n    <span/);
 assert.match(result,/<\/pre><p>Between<\/p><pre[^>]*><code>&lt;b&gt;text only&lt;\/b&gt;\n  indented<\/code><\/pre><p>After<\/p>/);
 assert.doesNotMatch(result,/\x60{3}|<b>/);
});
test('public quiz archive matches the clean original and preserves A/B blanks',async t=>{
 const privateFile=path.join(root,'admin/.course-private/week08/quiz-source.json');
 if(!fs.existsSync(privateFile)){t.skip('Private course source is not in this checkout');return;}
 const source=JSON.parse(fs.readFileSync(privateFile,'utf8'));
 const payload=JSON.parse(fs.readFileSync(path.join(root,'weeks/week-09/quiz-01.enc.json'),'utf8'));
 const archive=fs.readFileSync(path.join(root,'weeks/week-09/quiz-01.ipynb'),'utf8');
 const opened=await decryptQuiz(payload,source.passphrase,webcrypto);
 assert.deepEqual(JSON.parse(archive),opened.notebook);
 assert.equal(opened.text,fs.readFileSync(path.join(root,'admin/.course-private/week08/quiz-01.ipynb'),'utf8'));
 assert.equal(payload.filename,'week09_quiz.ipynb');
 assert.equal(opened.notebook.cells.filter(c=>c.cell_type==='code').length,12);
 assert.ok(opened.notebook.cells[0].source.includes('2026年11月26日'));
 const questions=opened.notebook.cells.filter(c=>c.cell_type==='markdown'&&c.source.startsWith('## 小テスト①問題'));
 assert.equal(questions.length,6);
 assert.ok(source.questions.every(([id,text],i)=>questions[i].source.endsWith('\n\n'+text)));
 for (const question of questions) {
  const index=opened.notebook.cells.indexOf(question);
  const [a,b]=opened.notebook.cells.slice(index+1,index+3);
  assert.deepEqual([a,b].map(cell=>cell.cell_type),['code','code']);
  assert.deepEqual([a,b].map(cell=>cell.metadata.tags[0]),['quiz-round-a','quiz-round-b']);
  assert.match(a.source,/^# A: AIなし \/ Without AI\s*$/);
  assert.match(b.source,/^# B: AIあり \/ AI-assisted\s*$/);
  assert.ok([a,b].every(cell=>cell.execution_count===null&&cell.outputs.length===0));
 }
 const codeBlocks=questions.flatMap(cell=>browser.markdownHtml(cell.source).match(/<pre class="code-block"/g)||[]);
 assert.equal(codeBlocks.length,10);
 assert.equal(fs.existsSync(path.join(root,'weeks/week-08/quiz-01.ipynb')),false);
 assert.equal(fs.existsSync(path.join(root,'weeks/week-08/quiz-01.enc.json')),false);
 const page=fs.readFileSync(path.join(root,'weeks/week-09/quiz.html'),'utf8');
 assert.ok(page.includes('data-release="2026-11-26T13:15:00+09:00"'));
 assert.match(page,/href="quiz-01\.ipynb" download="week09_quiz\.ipynb"/);
 assert.match(page,/quiz-archive\.js/);
 assert.doesNotMatch(page,/data-quiz-lock|type="password"|quiz-01\.enc\.json/);
 const script=fs.readFileSync(path.join(root,'weeks/week-09/quiz-archive.js'),'utf8');
 assert.ok(!page.includes(source.passphrase)&&!script.includes(source.passphrase)&&!archive.includes(source.passphrase));
 for(const [,question] of source.questions)assert.ok(!page.includes(question)&&!script.includes(question));
});
test('archive previews questions with code fences and does not fetch while locked',async()=>{
 const folder=path.join(root,'weeks/week-09');
 const script=fs.readFileSync(path.join(folder,'quiz-archive.js'),'utf8');
 const notebook=JSON.parse(fs.readFileSync(path.join(folder,'quiz-01.ipynb'),'utf8'));
 const download={href:'https://example.org/course/weeks/week-09/quiz-01.ipynb'};
 const preview={innerHTML:'',removeAttribute(name){assert.equal(name,'aria-busy');}};
 let fetched=0;
 const context={document:{querySelector:()=>null},markdownHtml:browser.markdownHtml,
  fetch:async href=>{assert.equal(href,download.href);fetched++;return {ok:true,json:async()=>notebook};}};
 await vm.runInNewContext(script,context);
 assert.equal(fetched,0);
 context.document.querySelector=()=>({querySelector:s=>s==='.quiz-download'?download:preview});
 await vm.runInNewContext(script,context);
 assert.equal(fetched,1);
 assert.equal((preview.innerHTML.match(/<pre class="code-block"/g)||[]).length,10);
 assert.match(preview.innerHTML,/secret combo/);
 assert.doesNotMatch(preview.innerHTML,/\x60{3}|# A: AIなし \/ Without AI\n/);
});
