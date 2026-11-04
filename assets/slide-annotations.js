/* Local, per-slide ink. No uploads, external dependencies, or changes to slide content. */
(() => {
  const view=document.getElementById('slides-view');
  const slides=[...document.querySelectorAll('[data-slide]')];
  const stage=view?.querySelector('.slide-stage');
  if(!stage||!slides.length)return; // The scheduled-release screen has no slides.
  const key='programming-slide-ink-v1:'+location.pathname.replace(/^.*\/weeks\//,'weeks/');
  const colours=['#c83249','#315876','#202a31','#28774f','#f1b82d'];
  let ink={},mode=false,tool='pen',colour=colours[0],width=3,current=null,saveFailed=false;
  const canvases=new Map();
  const ja=()=>document.documentElement.dataset.language!=='en';
  const currentSlide=()=>slides.find(slide=>!slide.hidden);
  const slideKey=slide=>String(slides.indexOf(slide)+1);
  const strokes=slide=>ink[slideKey(slide)]||[];
  function validStroke(stroke){
    if(!stroke||typeof stroke!=='object')return false;
    if(stroke.tool==='clear')return true;
    return ['pen','highlight','erase'].includes(stroke.tool)&&colours.includes(stroke.colour)&&
      Number.isFinite(stroke.width)&&stroke.width>0&&stroke.width<=0.2&&
      Array.isArray(stroke.points)&&stroke.points.length>0&&stroke.points.length<=5000&&
      stroke.points.every(p=>Array.isArray(p)&&p.length===2&&p.every(n=>Number.isFinite(n)&&n>=0&&n<=1));
  }
  try{
    const saved=JSON.parse(localStorage.getItem(key)||'{}');
    for(let n=1;n<=slides.length;n++){
      const list=saved[n];
      if(Array.isArray(list)&&list.every(validStroke))ink[n]=list;
    }
  }catch{saveFailed=true;}
  const toggle=document.createElement('button');
  toggle.type='button';toggle.className='annotation-toggle';toggle.setAttribute('aria-pressed','false');
  toggle.textContent='✎';toggle.title='Draw / 描く (D)';
  toggle.setAttribute('aria-label','Draw on slides');
  const tools=document.createElement('div');
  tools.className='annotation-tools';tools.id='annotation-tools';tools.hidden=true;
  tools.setAttribute('role','toolbar');tools.setAttribute('aria-label','Slide drawing tools');
  const icon=(attributes,glyph,label,title=label)=>'<button type="button" '+attributes+' aria-label="'+label+'" title="'+title+'"><span aria-hidden="true">'+glyph+'</span></button>';
  tools.innerHTML=
    '<div class="annotation-tool-group">'+
    icon('data-ink-tool="pen" aria-pressed="true"','✎','Pen','Pen / ペン')+
    icon('data-ink-tool="highlight" aria-pressed="false"','▰','Highlighter','Highlighter / 蛍光ペン')+
    icon('data-ink-tool="erase" aria-pressed="false"','⌫','Eraser','Eraser / 消しゴム')+'</div>'+
    '<div class="annotation-colours" role="group" aria-label="Ink colours">'+
    colours.map((value,i)=>icon('class="ink-swatch" data-ink-colour="'+value+'" style="--ink-colour:'+value+'" aria-pressed="'+(i===0)+'"','●',
      ['Red ink','Blue ink','Black ink','Green ink','Yellow ink'][i],['Red / 赤','Blue / 青','Black / 黒','Green / 緑','Yellow / 黄'][i])).join('')+'</div>'+
    '<div class="annotation-widths" role="group" aria-label="Line width">'+
    [2,3,6].map((value,i)=>icon('data-ink-width="'+value+'" style="--ink-dot:'+[5,8,12][i]+'px" aria-pressed="'+(value===3)+'"','●',
      ['Thin stroke','Medium stroke','Thick stroke'][i],['Thin / 細','Medium / 中','Thick / 太'][i])).join('')+'</div>'+
    icon('data-ink-undo','↶','Undo drawing','Undo / 元に戻す')+
    icon('data-ink-clear','⌧','Clear slide drawing','Clear this slide / このスライドを消去')+
    '<span class="annotation-status" role="status"></span>';
  const undo=tools.querySelector('[data-ink-undo]'),clear=tools.querySelector('[data-ink-clear]');
  const status=tools.querySelector('.annotation-status');
  toggle.setAttribute('aria-controls',tools.id);
  view.querySelector('.slide-controls').insertBefore(toggle,document.getElementById('slide-fullscreen'));
  stage.before(tools);
  function persist(){
    try{localStorage.setItem(key,JSON.stringify(ink));saveFailed=false;}catch{saveFailed=true;}
  }
  function refreshControls(){
    const slide=currentSlide(),list=slide?strokes(slide):[];
    undo.disabled=!list.length;
    const lastClear=list.map(s=>s.tool).lastIndexOf('clear');
    clear.disabled=!list.slice(lastClear+1).some(s=>s.tool!=='erase');
    const message=saveFailed?
      (ja()?'保存できません。再読み込みで消える場合があります。':'Cannot save. Ink may be lost on reload.'):
      (ja()?'このブラウザに保存 · Escで終了':'Saved in this browser · Esc to finish');
    status.textContent=saveFailed?'!':'✓';status.title=message;status.setAttribute('aria-label',message);
    tools.querySelectorAll('[data-ink-colour]').forEach(button=>{button.disabled=tool==='erase';});
    view.dataset.inkTool=tool;
  }
  function drawStroke(ctx,stroke,w,h){
    if(stroke.tool==='clear'){ctx.clearRect(0,0,w,h);return;}
    ctx.save();
    ctx.globalCompositeOperation=stroke.tool==='erase'?'destination-out':'source-over';
    ctx.globalAlpha=stroke.tool==='highlight'?0.25:1;
    ctx.strokeStyle=stroke.colour;ctx.fillStyle=stroke.colour;
    ctx.lineWidth=stroke.width*w;ctx.lineJoin='round';ctx.lineCap='round';
    if(stroke.points.length===1){
      const p=stroke.points[0];ctx.beginPath();ctx.arc(p[0]*w,p[1]*h,ctx.lineWidth/2,0,Math.PI*2);ctx.fill();
    }else{
      ctx.beginPath();stroke.points.forEach((p,i)=>{if(i)ctx.lineTo(p[0]*w,p[1]*h);else ctx.moveTo(p[0]*w,p[1]*h);});ctx.stroke();
    }
    ctx.restore();
  }
  function render(slide=currentSlide()){
    if(!slide||slide.hidden)return;
    const canvas=canvases.get(slide),rect=slide.getBoundingClientRect();
    if(!rect.width||!rect.height)return;
    const ratio=Math.min(window.devicePixelRatio||1,2);
    const w=Math.round(rect.width*ratio),h=Math.round(rect.height*ratio);
    if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}
    const ctx=canvas.getContext('2d');
    ctx.setTransform(ratio,0,0,ratio,0,0);ctx.clearRect(0,0,rect.width,rect.height);
    strokes(slide).forEach(stroke=>drawStroke(ctx,stroke,rect.width,rect.height));
    if(current?.slide===slide)drawStroke(ctx,current.stroke,rect.width,rect.height);
  }
  function finish(){
    if(!current)return;
    const {slide,stroke,canvas,pointer}=current;
    current=null;
    ink[slideKey(slide)]=[...strokes(slide),stroke];
    if(canvas.hasPointerCapture(pointer))canvas.releasePointerCapture(pointer);
    persist();render(slide);refreshControls();
  }
  function position(canvas,event){
    const rect=canvas.getBoundingClientRect();
    return [Math.max(0,Math.min(1,(event.clientX-rect.left)/rect.width)),
      Math.max(0,Math.min(1,(event.clientY-rect.top)/rect.height))];
  }
  slides.forEach(slide=>{
    const canvas=document.createElement('canvas');canvas.className='slide-ink';
    canvas.setAttribute('aria-hidden','true');slide.classList.add('has-slide-ink');slide.append(canvas);canvases.set(slide,canvas);
    canvas.addEventListener('pointerdown',event=>{
      if(!mode||event.button!==0||current)return;
      event.preventDefault();event.stopPropagation();
      const rect=canvas.getBoundingClientRect();
      const size=tool==='highlight'?width*6:tool==='erase'?width*9:width;
      current={slide,canvas,pointer:event.pointerId,stroke:{tool,colour,width:size/rect.width,points:[position(canvas,event)]}};
      canvas.setPointerCapture(event.pointerId);render(slide);
    });
    canvas.addEventListener('pointermove',event=>{
      if(!current||current.canvas!==canvas||current.pointer!==event.pointerId)return;
      event.preventDefault();event.stopPropagation();
      const coalesced=event.getCoalescedEvents?.();
      for(const sample of coalesced?.length?coalesced:[event]){
        const point=position(canvas,sample),last=current.stroke.points.at(-1);
        if(Math.hypot(point[0]-last[0],point[1]-last[1])>0.0005&&current.stroke.points.length<5000)current.stroke.points.push(point);
      }
      render(slide);
    });
    canvas.addEventListener('pointerup',event=>{
      if(current?.pointer!==event.pointerId)return;
      const point=position(canvas,event);
      if(current.stroke.points.length<5000)current.stroke.points.push(point);
      event.preventDefault();event.stopPropagation();finish();
    });
    canvas.addEventListener('pointercancel',finish);
    canvas.addEventListener('lostpointercapture',finish);
    ['touchstart','touchmove','touchend'].forEach(name=>canvas.addEventListener(name,event=>{
      if(mode){event.stopPropagation();if(event.cancelable)event.preventDefault();}
    },{passive:false}));
    new ResizeObserver(()=>render(slide)).observe(slide);
  });
  function setMode(value){
    finish();mode=value;tools.hidden=!mode;view.classList.toggle('is-annotating',mode);
    toggle.setAttribute('aria-pressed',String(mode));
    toggle.textContent=mode?'×':'✎';
    toggle.setAttribute('aria-label',mode?'Finish drawing':'Draw on slides');
    toggle.title=mode?'Finish drawing / 描画を終了 (Esc)':'Draw / 描く (D)';
    refreshControls();render();
  }
  toggle.onclick=()=>setMode(!mode);
  tools.querySelectorAll('[data-ink-tool]').forEach(button=>button.onclick=()=>{
    finish();tool=button.dataset.inkTool;
    tools.querySelectorAll('[data-ink-tool]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
    refreshControls();
  });
  tools.querySelectorAll('[data-ink-colour]').forEach(button=>button.onclick=()=>{
    colour=button.dataset.inkColour;
    tools.querySelectorAll('[data-ink-colour]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
  });
  tools.querySelectorAll('[data-ink-width]').forEach(button=>button.onclick=()=>{
    width=Number(button.dataset.inkWidth);
    tools.querySelectorAll('[data-ink-width]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
  });
  undo.onclick=()=>{finish();const slide=currentSlide();if(!slide)return;ink[slideKey(slide)]=strokes(slide).slice(0,-1);persist();render();refreshControls();};
  clear.onclick=()=>{finish();const slide=currentSlide();if(!slide)return;ink[slideKey(slide)]=[...strokes(slide),{tool:'clear'}];persist();render();refreshControls();};
  view.addEventListener('lecture:slidechange',()=>{finish();render();refreshControls();});
  const slideVisibility=new MutationObserver(()=>{finish();render();refreshControls();});
  slides.forEach(slide=>slideVisibility.observe(slide,{attributes:true,attributeFilter:['hidden']}));
  new MutationObserver(refreshControls).observe(document.documentElement,{attributes:true,attributeFilter:['data-language']});
  document.addEventListener('keydown',event=>{
    if(event.target.closest('input,textarea,select,[contenteditable="true"]')||event.ctrlKey||event.metaKey||event.altKey)return;
    if(event.key.toLowerCase()==='d'){event.preventDefault();event.stopImmediatePropagation();setMode(!mode);}
    if(event.key==='Escape'&&mode){event.preventDefault();event.stopImmediatePropagation();setMode(false);toggle.focus();}
    if(event.key==='z'&&mode&&!undo.disabled){event.preventDefault();undo.click();}
  },true);
  window.addEventListener('blur',finish);
  window.addEventListener('pagehide',finish);
  refreshControls();render();
})();
