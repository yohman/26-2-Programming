/* Shared plain-text copy controls, including dynamically rendered content. */
(() => {
  const selector='pre, #request-url, .application-example > code, textarea, #csv-output, .csv-table-scroll';
  const japanese=()=>(document.documentElement.dataset.language||document.documentElement.lang)!=='en';
  const label=()=>japanese()?'コピー':'Copy';
  const icon='<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="8" y="8" width="12" height="13"/><path d="M16 8V3H3v13h5"/></svg>';
  const wrapIcon='<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16M4 10h12a4 4 0 0 1 0 8h-6m3-3-3 3 3 3M4 15h3"/></svg>';
  function labelWrap(button){
    const wrapped=button.getAttribute('aria-pressed')==='true';
    button.setAttribute('aria-label',japanese()?'コードの折り返し':'Wrap code lines');
    button.title=japanese()?(wrapped?'折り返しを解除':'折り返す'):(wrapped?'Unwrap lines':'Wrap lines');
  }
  function plainText(target) {
    if(target instanceof HTMLTextAreaElement)return target.value;
    const table=target.matches('#csv-output, .csv-table-scroll')?target.querySelector('table'):null;
    if(table)return [...table.rows].map(row=>[...row.cells].map(cell=>cell.textContent.trim()).join('\t')).join('\n');
    const code=target.matches('pre')?target.querySelector('code'):null;
    if(code)return code.textContent;
    const clone=target.cloneNode(true);clone.querySelectorAll('.block-copy, .block-wrap').forEach(button=>button.remove());return clone.textContent;
  }
  async function write(text) {
    if(navigator.clipboard?.writeText) {try{await navigator.clipboard.writeText(text);return;}catch(_){} }
    const active=document.activeElement,field=document.createElement('textarea');field.value=text;field.className='copy-fallback';field.setAttribute('data-no-copy','');document.body.append(field);field.select();
    const ok=document.execCommand('copy');field.remove();active?.focus({preventScroll:true});if(!ok)throw new Error('Clipboard unavailable');
  }
  function install() {
    document.querySelectorAll(selector).forEach(target=>{
      if(target.matches('[data-no-copy]') || target.closest('[data-no-copy]'))return;
      const host=target instanceof HTMLTextAreaElement?target.parentElement:target;
      if(!host)return;
      let button=host.querySelector(':scope > .block-copy');
      if(button)return;
      host.classList.add('copyable-block');
      if(target instanceof HTMLTextAreaElement)host.classList.add('copyable-editor');
      if(target.matches('#csv-output, .csv-table-scroll'))host.classList.add('copyable-table');
      button=document.createElement('button');button.type='button';button.className='block-copy';button.innerHTML=icon;button.title=label();button.setAttribute('aria-label',label());
      button.addEventListener('click',async event=>{
        event.preventDefault();event.stopPropagation();
        try{await write(plainText(target));button.textContent='✓';button.title=japanese()?'コピーしました':'Copied';button.setAttribute('aria-label',button.title);button.dataset.copied='true';}
        catch(_){button.textContent='!';button.title=japanese()?'コピーできませんでした。テキストを選択してコピーしてください。':'Copy failed. Select and copy the text manually.';button.setAttribute('aria-label',button.title);}
        setTimeout(()=>{button.innerHTML=icon;button.title=label();button.setAttribute('aria-label',label());delete button.dataset.copied;},1600);
      });
      host.append(button);
      let wrap;
      if(target.matches('pre')&&target.closest('#slides-view')&&(target.hasAttribute('data-language')||target.querySelector('code'))){
        host.classList.add('copyable-code');
        wrap=document.createElement('button');
        wrap.type='button';wrap.className='block-wrap';wrap.innerHTML=wrapIcon;
        wrap.setAttribute('aria-pressed','false');labelWrap(wrap);
        wrap.addEventListener('click',event=>{
          event.preventDefault();event.stopPropagation();
          const wrapped=host.classList.toggle('is-code-wrapped');
          wrap.setAttribute('aria-pressed',String(wrapped));
          labelWrap(wrap);
          if(wrapped)host.scrollLeft=0;
          pin();
        });
        host.append(wrap);
      }
      // Counter the block's own scrolling without changing its layout or content.
      const pin=()=>{
        const offset='translate('+host.scrollLeft+'px, '+host.scrollTop+'px)';
        button.style.transform=offset;
        if(wrap)wrap.style.transform=offset;
      };
      host.addEventListener('scroll',pin,{passive:true});
      pin();
    });
  }
  function start() {
    install();let scheduled=false;
    new MutationObserver(()=>{
      document.querySelectorAll('.block-copy:not([data-copied])').forEach(button=>{button.title=label();button.setAttribute('aria-label',label());});
      document.querySelectorAll('.block-wrap').forEach(labelWrap);
    }).observe(document.documentElement,{attributes:true,attributeFilter:['lang','data-language']});
    new MutationObserver(()=>{if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;install();});}).observe(document.body,{childList:true,subtree:true});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();
