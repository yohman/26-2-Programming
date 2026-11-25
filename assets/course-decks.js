/* Python examples: built Python outputs and explicitly labelled JS simulations. */
(() => {
  const query=new URLSearchParams(location.search),body=document.body;
  if(!query.has('p')&&Date.now()<Date.parse(body.dataset.release)){
    document.querySelector('main').innerHTML='<section class="slide"><h1>Week '+body.dataset.week+'</h1><p>'+body.dataset.release.replace('T',' ').replace('+09:00',' JST')+' 公開 / Available</p></section>';
    document.getElementById('language-toggle').hidden=true;return;
  }
  const view=document.getElementById('slides-view'),stage=view.querySelector('.slide-stage');
  const slides=[...document.querySelectorAll('[data-slide]')],data=JSON.parse(document.getElementById('lesson-data').textContent);
  const previous=document.getElementById('previous-slide'),next=document.getElementById('next-slide');
  document.querySelectorAll('input[type="number"]').forEach(input=>input.required=true);
  let index=0;const cleanup=[];const model=window.CourseModels;
  function language(value){document.documentElement.dataset.language=value;document.documentElement.lang=value;const b=document.getElementById('language-toggle');b.textContent=value==='ja'?'EN':'日本語';b.setAttribute('aria-label',value==='ja'?'Switch to English':'日本語に切り替える');controls.label();try{localStorage.setItem('programming-language',value);}catch{}}
  function jumpControls() {
    const count=document.getElementById('slide-count'), group=count.parentElement;
    group.classList.add('course-slide-nav');
    document.documentElement.classList.add('course-slide-navigation');
    const arrows={
      first:'M5 5v14M18 6l-6 6 6 6', previous:'M15 6l-6 6 6 6',
      next:'M9 6l6 6-6 6', last:'M19 5v14M6 6l6 6-6 6'
    };
    const icon=key=>'<svg viewBox="0 0 24 24" width="19" height="19" aria-hidden="true"><path d="'+arrows[key]+'" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    const first=document.createElement('button'),last=document.createElement('button');
    for (const [button,key] of [[first,'first'],[previous,'previous'],[next,'next'],[last,'last']]) {
      button.type='button';
      button.innerHTML=icon(key);
      if (key==='first'||key==='last') button.id=key+'-slide';
    }
    group.prepend(first);
    group.append(last);
    first.addEventListener('click',()=>show(0));
    last.addEventListener('click',()=>show(slides.length-1));

    const slot=document.createElement('div');
    slot.className='slide-jump-slot';
    slot.innerHTML='<button type="button" class="slide-count-trigger" aria-controls="slide-jump-form" aria-expanded="false"></button><form id="slide-jump-form" class="slide-number-entry" hidden><input type="text" inputmode="numeric" enterkeyhint="go" autocomplete="off" spellcheck="false" required><button type="submit">↵</button></form>';
    const trigger=slot.querySelector('button'),form=slot.querySelector('form'),input=form.querySelector('input'),go=form.querySelector('button');
    count.replaceWith(slot);
    trigger.append(count);
    function label(){
      const ja=document.documentElement.lang==='ja';
      for (const [button,title] of [[first,ja?'最初のスライド':'First slide'],[previous,ja?'前のスライド':'Previous slide'],[next,ja?'次のスライド':'Next slide'],[last,ja?'最後のスライド':'Last slide'],[trigger,(ja?'番号を入力して移動：':'Jump to slide: ')+count.textContent],[go,ja?'移動':'Go to slide']]) {
        button.setAttribute('aria-label',title);
        button.title=title;
      }
      input.setAttribute('aria-label',ja?'スライド番号':'Slide number');
    }
    function close(focus=false){
      if(form.hidden)return;
      form.hidden=true;trigger.hidden=false;
      trigger.setAttribute('aria-expanded','false');
      input.setCustomValidity('');
      if(focus)trigger.focus({preventScroll:true});
    }
    trigger.addEventListener('click',()=>{
      input.value=String(index+1);
      trigger.hidden=true;form.hidden=false;
      trigger.setAttribute('aria-expanded','true');
      input.focus({preventScroll:true});input.select();
    });
    input.addEventListener('input',()=>input.setCustomValidity(''));
    form.addEventListener('submit',event=>{
      event.preventDefault();
      const value=input.value.trim().normalize('NFKC');
      const target=Number(value);
      if(!/^\d+$/.test(value)||target<1||target>slides.length){
        input.setCustomValidity(document.documentElement.lang==='ja'?'1〜'+slides.length+'の番号を入力してください。':'Enter a slide number from 1 to '+slides.length+'.');
        input.reportValidity();
        return;
      }
      close(true);show(target-1);
    });
    form.addEventListener('keydown',event=>{
      if(event.key==='Escape'){event.preventDefault();event.stopPropagation();close(true);}
    });
    slot.addEventListener('focusout',event=>{
      if(event.relatedTarget&&!slot.contains(event.relatedTarget))close();
    });
    document.addEventListener('pointerdown',event=>{if(!slot.contains(event.target))close();});
    return {label,render(){
      close();
      first.disabled=previous.disabled=index===0;last.disabled=next.disabled=index===slides.length-1;
      const digits=Math.max(2,String(slides.length).length);
      count.textContent=String(index+1).padStart(digits,'0')+' / '+slides.length;
      label();
    }};
  }
  const controls=jumpControls();
  function show(value){
    cleanup.forEach(fn=>fn());
    index=Math.max(0,Math.min(slides.length-1,Math.trunc(value)));
    slides.forEach((s,i)=>s.hidden=i!==index);
    controls.render();
    const url=new URL(location.href);
    url.searchParams.set('slide',index+1);history.replaceState(null,'',url);
    stage.scrollTop=0;window.scrollTo({top:0,behavior:'instant'});
    view.dispatchEvent(new CustomEvent('lecture:slidechange',{detail:{index}}));
  }
  function highlight(code){
    if(code.closest('pre')?.dataset.language==='shell')return;
    const source=code.textContent,pattern=/(#[^\n]*)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|\b(def|return|for|while|in|if|else|elif|break|continue|True|False|None|import|from|as|with|and|not|try|except|global)\b|\b(print|range|len|append|input|int|float|list|dict|open|enumerate|affordable|remaining|large_boxes|hit|tick_state|get|boxplot|rectangle|after|main|assert)\b|\b(\d+(?:\.\d+)?)\b/g;
    let pos=0;code.replaceChildren();for(const match of source.matchAll(pattern)){code.append(document.createTextNode(source.slice(pos,match.index)));const token=document.createElement('span');token.className=match[1]?'syntax-comment':match[2]?'syntax-string':match[3]?'syntax-keyword':match[4]?'syntax-function':'syntax-number';token.textContent=match[0];code.append(token);pos=match.index+match[0].length;}code.append(document.createTextNode(source.slice(pos)));
  }
  document.querySelectorAll('pre[data-language="python"] code').forEach(highlight);
  document.querySelectorAll('[data-run]').forEach((button,i)=>{const output=button.closest('.lesson-code').nextElementSibling;output.id='run-output-'+i;button.setAttribute('aria-controls',output.id);button.onclick=()=>{output.hidden=!output.hidden;button.setAttribute('aria-expanded',String(!output.hidden));};});
  const pyList=items=>'['+items.map(item=>JSON.stringify(item)).join(', ')+']';
  function updateCode(root,source){const code=root.querySelector('[data-demo-code] code');code.textContent=source;highlight(code);}
  function valid(root){return [...root.querySelectorAll('input')].every(input=>input.reportValidity());}
  document.querySelectorAll('[data-demo="budget"]').forEach(root=>{
    const run=()=>{if(!valid(root))return;const budget=Number(root.querySelector('[data-budget]').value),timeInput=root.querySelector('[data-minutes]'),minutes=timeInput?Number(timeInput.value):Infinity;updateCode(root,'budget = '+budget+(timeInput?'\nmax_minutes = '+minutes:'')+'\nfor item in menu:\n    if item["price"] <= budget'+(timeInput?' and item["minutes"] <= max_minutes':'')+':\n        print(item["name"])');root.querySelector('[data-demo-output]').textContent=model.affordable(data.menu,budget,minutes).join('\n')||'(no printed output / 候補0件)';};root.querySelector('[data-demo-run]').onclick=run;run();
  });
  document.querySelectorAll('[data-demo="vending"]').forEach(root=>{
    let coins=[];const render=()=>{const state=model.vending(coins);root.querySelector('[data-paid]').textContent='¥'+state.paid+' / ¥150';root.querySelector('[data-demo-output]').textContent=state.lines.join('\n');root.querySelectorAll('[data-coin]').forEach(b=>b.disabled=state.paid>=150);updateCode(root,'coins = '+JSON.stringify(coins)+'\npaid = 0\nindex = 0\nwhile paid < 150 and index < len(coins):\n    paid += coins[index]\n    index += 1\n    print("Paid:", paid)\nif paid >= 150:\n    print("Change:", paid - 150)\nelse:\n    print("Due:", 150 - paid)');};root.querySelectorAll('[data-coin]').forEach(b=>b.onclick=()=>{coins.push(Number(b.dataset.coin));render();});root.querySelector('[data-reset]').onclick=()=>{coins=[];render();};render();
  });
  document.querySelectorAll('[data-demo="call"]').forEach(root=>{
    let step=0;const render=()=>{if(!valid(root))return;const b=Number(root.querySelector('[data-call-budget]').value),p=Number(root.querySelector('[data-call-price]').value),r=model.remaining(b,p);const frames=['argument','local','return','caller'];root.querySelectorAll('[data-frame]').forEach(el=>el.classList.toggle('active',el.dataset.frame===frames[step]));updateCode(root,'def remaining(budget, price):\n    balance = budget - price\n    return balance\n\nresult = remaining('+b+', '+p+')\nprint(result)');const states=['arguments: '+b+', '+p,'inside function:\nbudget = '+b+'\nprice = '+p+'\nbalance = '+r,'return '+r+' → caller','caller: result = '+r+'\nprinted output: '+r];root.querySelector('[data-demo-output]').textContent=states[step];root.querySelector('[data-step]').disabled=step===3;};root.querySelector('[data-step]').onclick=()=>{step=Math.min(3,step+1);render();};root.querySelector('[data-reset]').onclick=()=>{step=0;render();};root.querySelectorAll('input').forEach(i=>i.addEventListener('change',()=>{step=0;render();}));render();
  });
  document.querySelectorAll('[data-trace]').forEach(root=>{
    let step=0;const code=root.querySelector('code'),source=code.textContent;code.replaceChildren(...source.split('\n').map((line,i)=>{const el=document.createElement('span');el.className='trace-line';el.dataset.line=i;el.textContent=line+'\n';return el;}));const render=()=>{const state=data.trace[step];root.querySelector('[data-trace-phase]').textContent=String(step+1)+' / '+data.trace.length+' · '+state.phase;root.querySelector('[data-trace-state]').textContent=state.state;root.querySelector('[data-trace-output]').textContent=state.output;root.querySelectorAll('[data-line]').forEach(el=>el.classList.toggle('active',Number(el.dataset.line)===state.line));root.querySelector('[data-trace-next]').disabled=step===data.trace.length-1;};root.querySelector('[data-trace-next]').onclick=()=>{step++;render();};root.querySelector('[data-trace-reset]').onclick=()=>{step=0;render();};render();
  });
  document.querySelectorAll('[data-demo="boxes"]').forEach(root=>{
    const render=()=>{if(!valid(root))return;const x=Number(root.querySelector('[data-box-x]').value),minimum=Number(root.querySelector('[data-box-area]').value),boxes=[{x,y:30,w:80,h:90},{x:180,y:50,w:60,h:70},{x:320,y:25,w:100,h:110}],kept=model.largeBoxes(boxes,minimum),layer=root.querySelector('[data-box-layer]');layer.replaceChildren(...kept.map(b=>{const rect=document.createElementNS('http://www.w3.org/2000/svg','rect');for(const [k,v] of Object.entries({x:b.x,y:b.y,width:b.w,height:b.h,fill:'none',stroke:'#315876','stroke-width':3}))rect.setAttribute(k,v);return rect;}));updateCode(root,'boxes = '+JSON.stringify(boxes).replace(/"([xywh])":/g,'"$1": ')+'\nkept = large_boxes(boxes, '+minimum+')\nprint(len(kept))');root.querySelector('[data-demo-output]').textContent=kept.length+' boxes\nFictional coordinates / 架空の説明用座標';};root.querySelectorAll('input').forEach(i=>i.addEventListener('input',render));render();
  });
  document.querySelectorAll('[data-demo="game"]').forEach(root=>{
    let score=0,seconds=0,timer=null;const target=root.querySelector('[data-game-target]');const render=()=>{root.querySelector('[data-game-status]').textContent='Score: '+score+' · Time: '+seconds;target.hidden=seconds<=0;};const stop=()=>{if(timer!==null){clearInterval(timer);timer=null;root.querySelector('[data-demo-output]').textContent='Paused on slide change / スライド移動で停止';}};cleanup.push(stop);root.querySelector('[data-game-start]').onclick=()=>{stop();score=0;seconds=20;target.style.left='40%';target.style.top='40%';render();root.querySelector('[data-demo-output]').textContent='Python rule: hit(score, seconds_left)';timer=setInterval(()=>{seconds=model.tick(seconds);render();if(!seconds){clearInterval(timer);timer=null;root.querySelector('[data-demo-output]').textContent='Finished · score = '+score;}},1000);};target.onclick=()=>{score=model.hit(score,seconds);target.style.left=(5+Math.random()*75)+'%';target.style.top=(5+Math.random()*60)+'%';render();root.querySelector('[data-demo-output]').textContent='click → hit → score = '+score;};render();
  });
  previous.onclick=()=>show(index-1);next.onclick=()=>show(index+1);
  document.addEventListener('keydown',event=>{if(event.target.closest('input,textarea,select,button,[contenteditable="true"]')||event.ctrlKey||event.metaKey||event.altKey||view.classList.contains('is-annotating'))return;if(['ArrowLeft','ArrowRight'].includes(event.key)){event.preventDefault();show(index+(event.key==='ArrowRight'?1:-1));}});
  const full=document.getElementById('slide-fullscreen');function sync(){full.setAttribute('aria-pressed',String(document.fullscreenElement===view||view.classList.contains('is-fullscreen-fallback')));}full.onclick=async()=>{if(document.fullscreenElement===view)await document.exitFullscreen();else if(view.classList.contains('is-fullscreen-fallback'))view.classList.remove('is-fullscreen-fallback');else try{await view.requestFullscreen();}catch{view.classList.add('is-fullscreen-fallback');}sync();};document.addEventListener('fullscreenchange',sync);document.addEventListener('keydown',e=>{if(e.key==='Escape'){view.classList.remove('is-fullscreen-fallback');sync();}});
  document.getElementById('language-toggle').onclick=()=>language(document.documentElement.lang==='ja'?'en':'ja');try{language(localStorage.getItem('programming-language')==='en'?'en':'ja');}catch{language('ja');}
  const back=document.getElementById('lecture-return');try{const url=new URL(query.get('return')||back.href,location.href);if(url.origin===location.origin&&/\/(agenda|index)\.html$/.test(url.pathname))back.href=url.href;}catch{}
  if(query.get('embed')==='1'){body.classList.add('lecture-embedded');document.querySelector('.lecture-header').hidden=true;document.querySelectorAll('.lesson-links a').forEach(a=>a.target='_top');}
  if(query.has('p'))document.querySelectorAll('a[href]').forEach(link=>{const u=new URL(link.href,location.href);if(u.origin===location.origin&&u.pathname.endsWith('.html')){u.searchParams.set('p','');link.href=u.href;}});
  show((Number(query.get('slide'))||1)-1);
})();
