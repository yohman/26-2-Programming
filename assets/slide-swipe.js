/* One-finger navigation; leave controls, code, vertical scroll, and ink alone. */
(() => {
  const view=document.getElementById('slides-view');
  const stage=view?.querySelector('.slide-stage');
  const previous=document.getElementById('previous-slide');
  const next=document.getElementById('next-slide');
  if(!stage||!previous||!next)return;
  let start=null;
  const blocked=()=>view.classList.contains('is-annotating')||window.getSelection()?.isCollapsed===false;
  stage.style.touchAction='pan-y pinch-zoom';
  stage.addEventListener('touchstart',event=>{
    start=null;
    if(event.touches.length!==1||blocked()||event.target.closest('a,button,input,textarea,select,summary,pre,code,canvas,.dataframe-output,[contenteditable="true"]'))return;
    const finger=event.touches[0];
    start={id:finger.identifier,x:finger.clientX,y:finger.clientY,time:event.timeStamp};
  },{passive:true});
  stage.addEventListener('touchmove',event=>{if(event.touches.length!==1)start=null;},{passive:true});
  stage.addEventListener('touchcancel',()=>{start=null;},{passive:true});
  stage.addEventListener('touchend',event=>{
    const from=start;start=null;
    if(!from||event.touches.length||blocked())return;
    const finger=[...event.changedTouches].find(t=>t.identifier===from.id);
    if(!finger)return;
    const dx=finger.clientX-from.x,dy=finger.clientY-from.y;
    if(Math.abs(dx)<65||Math.abs(dx)<Math.abs(dy)*1.6||event.timeStamp-from.time>1000)return;
    const button=dx<0?next:previous;
    if(!button.disabled)button.click();
  },{passive:true});
})();
