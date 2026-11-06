(() => {
 const query=new URLSearchParams(location.search),main=document.getElementById('course-page');
 if(!query.has('p')&&Date.now()<Date.parse(document.body.dataset.release)){main.innerHTML='<h1>Coming soon / 公開前</h1><p>'+document.body.dataset.release.replace('T',' ').replace('+09:00',' JST')+'</p>';}
 main.hidden=false;
 function language(value){document.documentElement.dataset.language=value;document.documentElement.lang=value;document.getElementById('language-toggle').textContent=value==='ja'?'EN':'日本語';try{localStorage.setItem('programming-language',value);}catch{}}
 let initial='ja';try{initial=localStorage.getItem('programming-language')==='en'?'en':'ja';}catch{}language(initial);
 document.getElementById('language-toggle').onclick=()=>language(document.documentElement.lang==='ja'?'en':'ja');
 try{const back=document.querySelector('.lecture-header a'),url=new URL(query.get('return')||back.href,location.href);if(url.origin===location.origin&&/\/(agenda|index)\.html$/.test(url.pathname))back.href=url.href;}catch{}
 if(query.has('p'))document.querySelectorAll('a[href]').forEach(link=>{const url=new URL(link.href,location.href);if(url.origin===location.origin&&url.pathname.endsWith('.html')){url.searchParams.set('p','');link.href=url.href;}});
})();
