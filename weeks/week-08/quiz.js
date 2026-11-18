/* Password-unlocked notebook download; the question text is not bundled in this script. */
(() => {
  async function decryptQuiz(payload, passphrase, cryptoApi = globalThis.crypto) {
    if (payload.version !== 1 || payload.algorithm !== 'AES-GCM' || payload.kdf !== 'PBKDF2') throw new Error('Unsupported quiz package');
    const bytes = value => Uint8Array.from(atob(value), char => char.charCodeAt(0));
    const material = await cryptoApi.subtle.importKey('raw', new TextEncoder().encode(passphrase), 'PBKDF2', false, ['deriveKey']);
    const key = await cryptoApi.subtle.deriveKey({name:'PBKDF2', salt:bytes(payload.salt), iterations:payload.iterations, hash:'SHA-256'}, material, {name:'AES-GCM', length:256}, false, ['decrypt']);
    const data = await cryptoApi.subtle.decrypt({name:'AES-GCM', iv:bytes(payload.iv)}, key, bytes(payload.ciphertext));
    const text = new TextDecoder().decode(data), notebook = JSON.parse(text);
    if (notebook.nbformat !== 4 || !Array.isArray(notebook.cells)) throw new Error('Invalid notebook');
    return {text, notebook};
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {decryptQuiz};
  if (typeof document === 'undefined') return;
  const root = document.querySelector('[data-quiz-lock]');
  if (!root) return;
  const form = root.querySelector('form'), input = root.querySelector('input[type="password"]');
  const submit = form.querySelector('button'), status = root.querySelector('[data-quiz-status]');
  const content = root.querySelector('[data-quiz-unlocked]'), download = root.querySelector('[data-quiz-download]');
  const message = (ja,en) => {
    const jp=document.createElement('span'), eng=document.createElement('span');
    jp.className='ja';jp.textContent=ja;eng.className='en';eng.textContent=en;status.replaceChildren(jp,eng);
  };
  let objectUrl = null;
  form.addEventListener('submit', async event => {
    event.preventDefault(); submit.disabled=true; message('確認中…','Opening…');
    let payload;
    try {
      const response = await fetch('quiz-01.enc.json', {cache:'no-cache'});
      if (!response.ok) throw new Error('Download unavailable');
      payload = await response.json();
    } catch (_) {
      message('問題ファイルを取得できません。もう一度試してください。','Could not fetch the quiz. Please try again.');
      submit.disabled=false;return;
    }
    try {
      const result = await decryptQuiz(payload, input.value);
      input.value='';form.hidden=true;
      objectUrl = URL.createObjectURL(new Blob([result.text], {type:payload.mime}));
      download.href=objectUrl;download.download=payload.filename;
      root.querySelector('[data-quiz-preview]').innerHTML=result.notebook.cells.filter(cell=>cell.cell_type==='markdown').map(cell=>'<section>'+markdownHtml(Array.isArray(cell.source)?cell.source.join(''):cell.source)+'</section>').join('');
      content.hidden=false;message('開きました。Notebookをダウンロードしてください。','Ready. Download your notebook.');
      download.focus();
    } catch (_) {
      message('パスワードが違います。もう一度入力してください。','Incorrect password. Please try again.');
      submit.disabled=false;input.focus();
    }
  });
  window.addEventListener('pagehide',()=>{if(objectUrl)URL.revokeObjectURL(objectUrl);});
})();
