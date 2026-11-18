const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {webcrypto,pbkdf2Sync,createCipheriv,randomBytes}=require('node:crypto');
const {decryptQuiz}=require('../../weeks/week-08/quiz.js');
const root=path.resolve(__dirname,'../..');
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
test('published quiz package matches the teacher private notebook',async t=>{
 const privateFile=path.join(root,'admin/.course-private/week08/quiz-source.json');
 if(!fs.existsSync(privateFile)){t.skip('Private course source is not in this checkout');return;}
 const source=JSON.parse(fs.readFileSync(privateFile,'utf8'));
 const payload=JSON.parse(fs.readFileSync(path.join(root,'weeks/week-08/quiz-01.enc.json'),'utf8'));
 const opened=await decryptQuiz(payload,source.passphrase,webcrypto);
 assert.equal(opened.text,fs.readFileSync(path.join(root,'admin/.course-private/week08/quiz-01.ipynb'),'utf8'));
 assert.equal(opened.notebook.cells.filter(c=>c.cell_type==='code').length,6);
 assert.equal(fs.existsSync(path.join(root,'weeks/week-08/quiz-01.ipynb')),false);
 const page=fs.readFileSync(path.join(root,'weeks/week-08/quiz.html'),'utf8');
 const script=fs.readFileSync(path.join(root,'weeks/week-08/quiz.js'),'utf8');
 assert.ok(!page.includes(source.passphrase)&&!script.includes(source.passphrase));
 for(const [,question] of source.questions)assert.ok(!page.includes(question)&&!script.includes(question));
});
