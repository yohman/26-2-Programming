/* Teacher-paced scenes: animation never advances the slide or starts audio. */
(() => {
  const scenes=[...document.querySelectorAll('.story-scene[data-slide]')];
  if(!scenes.length)return;
  const ja=()=>document.documentElement.dataset.language!=='en';
  const say=(j,e)=>ja()?j:e;
  function activate(){
    scenes.forEach(scene=>scene.classList.toggle('is-story-active',!scene.hidden));
  }
  const visibility=new MutationObserver(activate);
  scenes.forEach(scene=>visibility.observe(scene,{attributes:true,attributeFilter:['hidden']}));
  document.querySelectorAll('[data-story-open]').forEach(button=>{
    const scene=button.closest('.story-scene'),target=button.dataset.storyOpen;
    const parts=[...scene.querySelectorAll('[data-story-reveal="'+target+'"]')];
    parts.forEach((part,i)=>{part.id='story-'+target+'-'+i;});
    button.setAttribute('aria-controls',parts.map(part=>part.id).join(' '));
    button.onclick=()=>{
      const open=button.getAttribute('aria-expanded')!=='true';
      button.setAttribute('aria-expanded',String(open));
      parts.forEach(part=>{part.hidden=!open;});
      if(target==='python-code')scene.classList.toggle('is-story-coded',open);
    };
  });
  const contrast=document.querySelector('.story-contrast');
  contrast?.querySelectorAll('[data-story-contrast]').forEach(button=>button.onclick=()=>{
    const correct=button.dataset.storyContrast==='contrast';
    contrast.classList.toggle('is-story-solved',correct);
    contrast.querySelectorAll('[data-story-contrast]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
    contrast.querySelector('.story-feedback').textContent=correct?
      say('好みの違い。「一方で」というwhile。これはループではない。','Different tastes. Here while means whereas. No loop yet.'):
      say('二人は好みについて話している。同時に行う動作は書いてある？','They are talking about preferences. Does this describe two simultaneous actions?');
  });
  const glitch=document.querySelector('.story-glitch');
  if(glitch){
    let round=0;
    const play=glitch.querySelector('[data-story-round]'),reset=glitch.querySelector('[data-story-round-reset]');
    const tape=glitch.querySelector('.round-tape'),reply=glitch.querySelector('.glitch-response');
    play.onclick=()=>{
      if(round>=5)return;
      round++;
      const entry=document.createElement('li');
      entry.textContent=round===4?'04 · FROZEN':String(round).padStart(2,'0')+' · +10';
      if(round===4)entry.className='round-frozen';
      tape.append(entry);glitch.classList.toggle('is-story-glitch',round===4);
      reply.textContent=round===4?'MINA: So this is the “once” bit?':round===5?'KAI: See? Only once in a while.':'MINA: One more round.';
      play.disabled=round===5;reset.hidden=round!==5;
    };
    reset.onclick=()=>{round=0;tape.replaceChildren();reply.textContent='MINA: Once in a while?!';play.disabled=false;reset.hidden=true;glitch.classList.remove('is-story-glitch');};
  }
  const rule=document.querySelector('.story-rule');
  rule?.querySelectorAll('[data-story-boundary]').forEach(button=>button.onclick=()=>{
    const stop=button.dataset.storyBoundary==='stop';
    rule.querySelectorAll('[data-story-boundary]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
    rule.querySelector('.story-feedback').textContent=stop?
      say('20%は「20%を超える」ではない。ここで止める。','20 is not above 20. This is where we stop.'):
      say('aboveは「より大きい」。20 > 20は成り立つ？','Above means greater than. Is 20 > 20 true?');
  });
  const loop=document.querySelector('.story-loop');
  if(loop){
    let battery=50;
    const play=loop.querySelector('[data-story-battery-play]'),reset=loop.querySelector('[data-story-battery-reset]');
    const number=loop.querySelector('[data-story-battery]'),verdict=loop.querySelector('[data-story-verdict]');
    const reply=loop.querySelector('.battery-dialogue'),history=loop.querySelector('.battery-history');
    play.onclick=()=>{
      if(battery<=20)return;
      const before=battery;battery-=10;
      const line=document.createElement('span');line.textContent=before+' > 20 ✓ · PLAY';history.append(line);
      number.textContent=String(battery);
      verdict.textContent=battery>20?'TRUE':'FALSE';
      loop.classList.toggle('is-story-stopped',battery<=20);
      loop.classList.remove('is-battery-tick');void loop.offsetWidth;loop.classList.add('is-battery-tick');
      reply.textContent=battery>20?'MINA: One more?':'MINA: The rule says stop.';
      if(battery<=20){
        const stop=document.createElement('span');stop.textContent='20 > 20 ✕ · STOP';history.append(stop);play.disabled=true;
      }
    };
    reset.onclick=()=>{battery=50;number.textContent='50';verdict.textContent='TRUE';reply.textContent='MINA: One more?';history.replaceChildren();play.disabled=false;loop.classList.remove('is-story-stopped','is-battery-tick');};
  }
  activate();
})();
