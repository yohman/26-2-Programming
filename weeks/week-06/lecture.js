/* Python examples are simulated explicitly in JavaScript, never evaluated as code. */
(() => {
  const query=new URLSearchParams(location.search);
  const preview=query.has('p');
  if(!preview && Date.now()<Date.parse('2026-11-05T12:00:00+09:00')){
    document.getElementById('language-toggle').hidden=true;
    document.querySelector('main').innerHTML='<section class="slide"><h1>Week 06</h1><p>11月5日 12:00 JST 公開 / Available November 5 at noon JST.</p><a href="../../agenda.html">授業予定 / Agenda</a></section>';
    return;
  }
  const slides=[...document.querySelectorAll('[data-slide]')];
  const view=document.getElementById('slides-view'),stage=document.querySelector('.slide-stage');
  const previous=document.getElementById('previous-slide'),next=document.getElementById('next-slide');
  let index=0,timer=null,timerRoot=null;
  const isJa=()=>document.documentElement.dataset.language!=='en';
  const text=(ja,en)=>isJa()?ja:en;
  const bi=(ja,en)=>'<span class="ja">'+ja+'</span><span class="en">'+en+'</span>';
  function setLanguage(value){
    document.documentElement.dataset.language=value;
    document.documentElement.lang=value;
    const button=document.getElementById('language-toggle');
    button.textContent=value==='ja'?'EN':'日本語';
    button.setAttribute('aria-label',value==='ja'?'Switch to English':'日本語に切り替える');
    try{localStorage.setItem('programming-language',value);}catch{}
  }
  function stopTimer(){
    if(timer!==null){
      clearTimeout(timer);timer=null;
      timerRoot.querySelector('pre').textContent+='\n'+text('停止しました','Stopped');
      timerRoot.querySelector('[data-run]').disabled=false;
    }
  }
  function showSlide(value){
    stopTimer();
    index=Math.max(0,Math.min(slides.length-1,value));
    slides.forEach((slide,i)=>{slide.hidden=i!==index;});
    previous.disabled=index===0;next.disabled=index===slides.length-1;
    document.getElementById('slide-count').textContent=String(index+1).padStart(2,'0')+' / '+slides.length;
    const url=new URL(location.href);url.searchParams.set('slide',index+1);
    history.replaceState(null,'',url);
    stage.scrollTop=0;window.scrollTo(0,0);
    view.dispatchEvent(new CustomEvent('lecture:slidechange',{detail:{index}}));
  }
  function highlight(code){
    if(code.closest('.lecture-cell-output')||code.closest('pre')?.dataset.language==='markdown')return;
    const source=code.textContent;
    const pattern=/(#[^\n]*)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|\b(for|while|in|if|else|elif|break|True|False|import|as|with)\b|\b(print|range|format|len|append|input|int|randint|sleep|DictReader|list|float|pop|sample|read_csv|head|info|describe|isna|sum|copy|sort_values|contains|iterrows|mean|round|between|to_datetime|tz_convert|dropna|scatter|show|get|raise_for_status|open|write|to_string|save|Map|CircleMarker|add_to)\b|\b(\d+(?:_\d+)*(?:\.\d+)?)\b/g;
    let position=0;code.replaceChildren();
    for(const match of source.matchAll(pattern)){
      code.append(document.createTextNode(source.slice(position,match.index)));
      const token=document.createElement('span');
      token.className=match[1]?'syntax-comment':match[2]?'syntax-string':match[3]?'syntax-keyword':match[4]?'syntax-function':'syntax-number';
      token.textContent=match[0];code.append(token);position=match.index+match[0].length;
    }
    code.append(document.createTextNode(source.slice(position)));
  }
  document.querySelectorAll('pre code').forEach(highlight);
  function updateExample(root,pattern,replacement){
    const code=root.closest('[data-slide]').querySelector('.lecture-notebook-cell code');
    code.textContent=code.textContent.replace(pattern,replacement);highlight(code);
  }
  document.querySelectorAll('[data-reveal]').forEach((button,i)=>{
    const output=button.closest('.lecture-notebook-cell').nextElementSibling;
    output.id='output-'+i;button.setAttribute('aria-controls',output.id);
    button.onclick=()=>{output.hidden=!output.hidden;button.setAttribute('aria-expanded',String(!output.hidden));};
  });
  const students=JSON.parse(document.getElementById('class-roster').textContent);
  let picked=students.slice(0,3),waiting=[],queueLines=[];
  const queue=document.querySelector('[data-review-queue]');
  function renderQueue(){
    queue.querySelector('[data-queue-names]').replaceChildren(...waiting.map(name=>{
      const item=document.createElement('span');item.textContent=name;return item;
    }));
    queue.querySelector('[data-queue-state]').textContent='len(waiting) = '+waiting.length+' → '+(waiting.length>0?'True':'False');
    queue.querySelector('[data-queue-output]').textContent=queueLines.join('\n');
    queue.querySelector('[data-queue-next]').disabled=waiting.length===0;
  }
  function resetQueue(){
    waiting=[...picked];queueLines=[];
    const code=queue.closest('[data-slide]').querySelector('.lecture-notebook-cell code');
    code.textContent='waiting = '+JSON.stringify(picked)+'\nwhile len(waiting) > 0:\n    name = waiting.pop(0)\n    print(f"{name}さん、どうぞ！")';
    highlight(code);renderQueue();
  }
  document.querySelector('[data-review-draw]').onclick=()=>{
    const pool=[...students];picked=[];
    while(picked.length<3)picked.push(pool.splice(Math.floor(Math.random()*pool.length),1)[0]);
    document.querySelector('[data-review-picked]').replaceChildren(...picked.map(name=>{
      const item=document.createElement('span');item.textContent=name;return item;
    }));
    resetQueue();
  };
  queue.querySelector('[data-queue-next]').onclick=()=>{
    if(!waiting.length)return;
    queueLines.push(waiting.shift()+'さん、どうぞ！');renderQueue();
  };
  queue.querySelector('[data-queue-reset]').onclick=resetQueue;resetQueue();
  const welcome=document.querySelector('[data-review-welcome]');
  welcome.querySelector('[data-welcome-run]').onclick=()=>{
    const name=welcome.querySelector('input').value;
    welcome.querySelector('pre').textContent=students.includes(name)?'Welcome back, '+name+'!':name==='Yoh'?'先生、説明は短めに！':'ゲストですね。ようこそ！';
  };
  const chat=document.querySelector('[data-review-chat]');
  let chatDone=false,chatLines=[];
  function resetChat(){
    chatDone=false;chatLines=[];chat.querySelector('input').value='Hinata';
    chat.querySelector('pre').textContent='';chat.querySelector('[data-chat-state]').textContent='name != "q" → True';chat.querySelector('[data-chat-run]').disabled=false;
  }
  chat.querySelector('[data-chat-run]').onclick=()=>{
    if(chatDone)return;
    const name=chat.querySelector('input').value;
    chatDone=name==='q';
    if(!chatDone)chatLines.push('Hello, '+name+'!');
    chat.querySelector('pre').textContent=chatLines.join('\n');
    chat.querySelector('[data-chat-state]').textContent='name != "q" → '+(chatDone?'False':'True');
    chat.querySelector('[data-chat-run]').disabled=chatDone;
  };
  chat.querySelector('[data-chat-reset]').onclick=resetChat;resetChat();
  for(const root of [welcome,chat])root.querySelector('input').addEventListener('keydown',event=>{
    if(event.key==='Enter'){event.preventDefault();root.querySelector('button').click();}
  });
  try{
    const destination=new URL(query.get('return')||'../../agenda.html?open=06#week-06',location.href);
    if(destination.origin===location.origin&&/\/(agenda|index)\.html$/.test(destination.pathname)){
      if(preview)destination.searchParams.set('p','');document.getElementById('lecture-return').href=destination.href;
    }
  }catch{}
  document.addEventListener('click',event=>{
    const link=event.target.closest('a[href]');if(!preview||!link)return;
    const url=new URL(link.href,location.href);
    if(url.origin===location.origin&&url.pathname.endsWith('.html')){url.searchParams.set('p','');link.href=url.href;}
  },true);
  previous.onclick=()=>showSlide(index-1);next.onclick=()=>showSlide(index+1);
  document.addEventListener('keydown',event=>{
    if(event.target.closest('input,textarea,select,button,summary,a')||event.ctrlKey||event.metaKey||event.altKey)return;
    if(event.key==='ArrowLeft'||event.key==='ArrowRight'){event.preventDefault();showSlide(index+(event.key==='ArrowRight'?1:-1));}
  });
  const fullscreen=document.getElementById('slide-fullscreen');
  const syncFullscreen=()=>fullscreen.setAttribute('aria-pressed',String(document.fullscreenElement===view||view.classList.contains('is-fullscreen-fallback')));
  fullscreen.onclick=async()=>{
    if(document.fullscreenElement===view)await document.exitFullscreen();
    else if(view.classList.contains('is-fullscreen-fallback'))view.classList.remove('is-fullscreen-fallback');
    else{try{await view.requestFullscreen();}catch{view.classList.add('is-fullscreen-fallback');}}
    syncFullscreen();
  };
  document.addEventListener('fullscreenchange',syncFullscreen);
  document.addEventListener('keydown',event=>{if(event.key==='Escape'){view.classList.remove('is-fullscreen-fallback');syncFullscreen();}});
  document.getElementById('language-toggle').onclick=()=>setLanguage(isJa()?'en':'ja');
  window.addEventListener('storage',event=>{if(event.key==='programming-language')setLanguage(event.newValue==='en'?'en':'ja');});
  if(query.get('embed')==='1'){document.body.classList.add('lecture-embedded');document.querySelector('.lecture-header').hidden=true;}
  try{setLanguage(localStorage.getItem('programming-language')==='en'?'en':'ja');}catch{setLanguage('ja');}
  showSlide((Number(query.get('slide'))||1)-1);
})();
