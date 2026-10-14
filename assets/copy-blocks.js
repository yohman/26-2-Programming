/* Shared plain-text copy controls, including dynamically rendered content. */
(() => {
  const selector='pre, #request-url, .application-example > code, textarea, #csv-output, .csv-table-scroll';
  const japanese=()=>(document.documentElement.dataset.language||document.documentElement.lang)!=='en';
  const label=()=>japanese()?'コピー':'Copy';
  const icon='<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="8" y="8" width="12" height="13"/><path d="M16 8V3H3v13h5"/></svg>';
  function plainText(target) {
    if(target instanceof HTMLTextAreaElement)return target.value;
    const table=target.matches('#csv-output, .csv-table-scroll')?target.querySelector('table'):null;
    if(table)return [...table.rows].map(row=>[...row.cells].map(cell=>cell.textContent.trim()).join('\t')).join('\n');
    const code=target.matches('pre')?target.querySelector('code'):null;
    if(code)return code.textContent;
    const clone=target.cloneNode(true);clone.querySelectorAll('.block-copy').forEach(button=>button.remove());return clone.textContent;
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
      // Counter the block's own scrolling without changing its layout or content.
      const pin=()=>{button.style.transform=`translate(${host.scrollLeft}px, ${host.scrollTop}px)`;};
      host.addEventListener('scroll',pin,{passive:true});
      pin();
    });
  }
  function start() {
    install();let scheduled=false;
    new MutationObserver(()=>document.querySelectorAll('.block-copy:not([data-copied])').forEach(button=>{button.title=label();button.setAttribute('aria-label',label());})).observe(document.documentElement,{attributes:true,attributeFilter:['lang','data-language']});
    new MutationObserver(()=>{if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;install();});}).observe(document.body,{childList:true,subtree:true});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();
