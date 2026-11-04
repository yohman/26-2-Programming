(() => {
  const query=new URLSearchParams(location.search),main=document.getElementById('report-main');
  if(!query.has('p')&&Date.now()<Date.parse('2026-11-05T12:00:00+09:00')){
    main.innerHTML='<h1>Week 06</h1><p>11月5日 12:00 JST 公開 / Available November 5 at noon JST.</p>';
  }
  main.hidden=false;
  const button=document.getElementById('report-language');
  function language(value){
    document.documentElement.dataset.language=value;document.documentElement.lang=value;
    button.textContent=value==='ja'?'EN':'日本語';button.setAttribute('aria-label',value==='ja'?'Switch to English':'日本語に切り替える');
    try{localStorage.setItem('programming-language',value);}catch{}
  }
  let initial='ja';try{initial=localStorage.getItem('programming-language')==='en'?'en':'ja';}catch{}
  language(initial);button.onclick=()=>language(document.documentElement.lang==='ja'?'en':'ja');
  if(query.has('p'))document.querySelectorAll('a[href]').forEach(link=>{
    const url=new URL(link.href,location.href);
    if(url.origin===location.origin&&url.pathname.endsWith('.html')){url.searchParams.set('p','');link.href=url.href;}
  });
  if(location.hash)document.getElementById(location.hash.slice(1))?.scrollIntoView();
})();
