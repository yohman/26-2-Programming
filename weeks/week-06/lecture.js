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
    if(code.closest('.lecture-cell-output'))return;
    const source=code.textContent;
    const pattern=/(#[^\n]*)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|\b(for|while|in|if|else|elif|break|True|False|import|as|with)\b|\b(print|range|format|len|append|input|int|randint|sleep|read_csv|head|isna|sum|copy|sort_values|contains|iterrows|mean|round|between|to_datetime|tz_convert|dropna|scatter|show|get|raise_for_status|open|write|to_string|save|Map|CircleMarker|add_to)\b|\b(\d+(?:_\d+)*(?:\.\d+)?)\b/g;
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
  function controls(root,html){
    root.innerHTML='<div class="simulation-controls">'+html+'</div><p class="state-readout" role="status"></p><pre aria-live="polite"></pre>';
    return {status:root.querySelector('.state-readout'),output:root.querySelector('pre')};
  }
  function numberInput(root,min,max){
    const field=root.querySelector('input'),value=Number(field.value);
    if(field.value.trim()===''||!Number.isInteger(value)||value<min||value>max)return null;
    return value;
  }
  document.querySelectorAll('[data-simulation]').forEach(root=>{
    const kind=root.dataset.simulation;
    if(kind==='boss'){
      const {status,output}=controls(root,'<button data-run>▶ HIT</button><button data-reset>↶ RESET</button>');
      let hp=3,lines=[];
      function reset(){hp=3;lines=[];status.textContent='HP ● ● ● · 3 > 0 → True';output.textContent='';root.querySelector('[data-run]').disabled=false;}
      root.querySelector('[data-run]').onclick=()=>{
        if(hp<=0)return;
        lines.push('HIT!');hp--;
        status.textContent='HP '+('● '.repeat(hp))+('○ '.repeat(3-hp))+' · '+hp+' > 0 → '+(hp>0?'True':'False');
        if(hp===0){lines.push('CLEAR!');root.querySelector('[data-run]').disabled=true;}
        output.textContent=lines.join('\n');
      };
      root.querySelector('[data-reset]').onclick=reset;reset();
    }
    if(kind==='beat'){
      const {status,output}=controls(root,'<label>'+bi('上限','Limit')+' <input aria-label="Beat limit" type="number" min="1" max="10" value="4"></label><button data-reset>'+bi('リセット','Reset')+'</button><button data-step>'+bi('次の一行','Next line')+'</button><button data-run>'+bi('最後まで','Run to end')+'</button>');
      let count=1,phase='check',limit=4,lines=[],steps=0;
      function reset(){count=1;phase='check';steps=0;lines=[];limit=numberInput(root,1,10);output.textContent='';if(limit!==null)updateExample(root,/while count <= \d+:/,'while count <= '+limit+':');status.textContent=limit===null?text('1〜10の整数を入力','Enter an integer from 1 to 10'):'count = 1';root.querySelectorAll('[data-step],[data-run]').forEach(b=>{b.disabled=limit===null;});}
      function step(){
        if(phase==='done'||limit===null)return;
        if(phase==='check'){
          const pass=count<=limit;status.textContent='count='+count+' · '+count+' <= '+limit+' → '+(pass?'True':'False');
          phase=pass?'print':'finish';
        }else if(phase==='print'){lines.push(count+' beat');status.textContent='print('+count+')';phase='update';}
        else if(phase==='update'){count+=1;status.textContent='count += 1 → '+count;phase='check';}
        else{lines.push('Drop!');status.textContent=text('条件がFalse。本体は実行せず、ループの後へ。','False: skip the body and continue after the loop.');phase='done';root.querySelectorAll('[data-step],[data-run]').forEach(b=>{b.disabled=true;});}
        output.textContent=lines.join('\n');steps++;
      }
      root.querySelector('[data-reset]').onclick=reset;
      root.querySelector('input').oninput=reset;
      root.querySelector('input').onchange=reset;
      root.querySelector('[data-step]').onclick=step;
      root.querySelector('[data-run]').onclick=()=>{while(phase!=='done'&&steps<40&&limit!==null)step();};
      reset();
    }
    if(kind==='threshold'){
      const {status,output}=controls(root,'<label>'+bi('しきい値','Threshold')+' <input aria-label="Total threshold" type="number" min="0" max="100" value="10"></label><button data-run>▶ '+bi('実行する','Run')+'</button>');
      root.querySelector('[data-run]').onclick=()=>{
        const limit=numberInput(root,0,100);
        if(limit===null){status.textContent=text('0〜100の整数を入力','Enter an integer from 0 to 100');return;}
        updateExample(root,/while total <= \d+:/,'while total <= '+limit+':');
        let total=0,num=1;const lines=[];
        while(total<=limit&&num<=20){const before=total;total+=num;lines.push(before+' + '+num+' = '+total);num++;}
        output.textContent=lines.join('\n')+'\nprint(total): '+total;
        status.textContent='total='+total+' · num='+num+' · '+total+' <= '+limit+' → False';
      };
    }
    if(kind==='timer'){
      const {status,output}=controls(root,'<label>'+bi('秒数','Seconds')+' <input aria-label="Timer seconds" type="number" min="1" max="10" value="3"></label><button data-run>▶ '+bi('開始','Start')+'</button><button data-stop>'+bi('停止','Stop')+'</button>');
      root.querySelector('[data-run]').onclick=()=>{
        stopTimer();const limit=numberInput(root,1,10);
        if(limit===null){status.textContent=text('1〜10の整数を入力','Enter an integer from 1 to 10');return;}
        updateExample(root,/totalsecs = \d+/,'totalsecs = '+limit);
        timerRoot=root;let secs=0;const lines=[];output.textContent='';root.querySelector('[data-run]').disabled=true;
        function tick(){
          if(secs>=limit){lines.push('Timer finished!');output.textContent=lines.join('\n');timer=null;status.textContent='secs='+secs+' · False';root.querySelector('[data-run]').disabled=false;return;}
          secs++;lines.push(String(secs));output.textContent=lines.join('\n');status.textContent='secs='+secs+' · time.sleep(1)';timer=setTimeout(tick,1000);
        }
        tick();
      };
      root.querySelector('[data-stop]').onclick=stopTimer;
    }
    if(kind==='password'){
      const {status,output}=controls(root,'<label>Code word: <input aria-label="Code word" type="text" autocomplete="off" placeholder="secret"></label><button data-run>'+bi('入力する','Submit')+'</button><button data-reset>'+bi('リセット','Reset')+'</button>');
      let done=false,lines=[];
      function reset(){done=false;lines=[];output.textContent='';status.textContent='password != "secret" → True';root.querySelector('[data-run]').disabled=false;root.querySelector('input').value='';}
      root.querySelector('[data-run]').onclick=()=>{
        if(done)return;const value=root.querySelector('input').value;
        done=value==='secret';lines.push('Code word: '+value,done?'Welcome!':'Try again');
        output.textContent=lines.join('\n');status.textContent='password != "secret" → '+(done?'False':'True');root.querySelector('[data-run]').disabled=done;
      };
      root.querySelector('[data-reset]').onclick=reset;reset();
    }
    if(kind==='guess'){
      const {status,output}=controls(root,'<label>Guess: <input aria-label="Guess" type="number" min="1" max="100" value="50"></label><button data-run>'+bi('予想する','Guess')+'</button><button data-reset>'+bi('新しいゲーム','New game')+'</button>');
      let number,attempts,lines;
      function reset(){number=Math.floor(Math.random()*100)+1;attempts=0;lines=[];output.textContent='';status.textContent=text('1〜100の秘密の数を一度だけ決めました。','One secret number chosen from 1 to 100.');root.querySelector('[data-run]').disabled=false;}
      root.querySelector('[data-run]').onclick=()=>{
        const guess=numberInput(root,1,100);if(guess===null){status.textContent=text('1〜100の整数を入力','Enter an integer from 1 to 100');return;}
        attempts++;const message=guess<number?'Higher':guess>number?'Lower':'Correct! '+attempts+' guesses';
        lines.push(guess+': '+message);output.textContent=lines.join('\n');
        status.textContent='attempts='+attempts+(guess===number?' · break':' · while True');
        root.querySelector('[data-run]').disabled=guess===number;
      };
      root.querySelector('[data-reset]').onclick=reset;reset();
    }
    root.querySelectorAll('input').forEach(input=>input.addEventListener('keydown',event=>{
      if(event.key==='Enter'){event.preventDefault();root.querySelector('[data-run]').click();}
    }));
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
