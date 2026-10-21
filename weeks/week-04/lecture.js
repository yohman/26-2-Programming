const slides=[...document.querySelectorAll('[data-slide]')];
const stage=document.querySelector('.slide-stage');
const view=document.getElementById('slides-view');
const previous=document.getElementById('previous-slide'),next=document.getElementById('next-slide');
const fullscreen=document.getElementById('slide-fullscreen');
const query=new URLSearchParams(location.search),embedded=query.get('embed')==='1';
let index=0,gameResult=null;
if(embedded) {
  document.body.classList.add('lecture-embedded');
  previous.textContent='‹';next.textContent='›';
  previous.setAttribute('aria-label','前のスライド / Previous slide');
  next.setAttribute('aria-label','次のスライド / Next slide');
}
function language(value) {
  document.documentElement.dataset.language=value;document.documentElement.lang=value;
  const toggle=document.getElementById('language-toggle');toggle.textContent=value==='ja'?'EN':'日本語';
  toggle.setAttribute('aria-label',value==='ja'?'Switch to English':'日本語に切り替える');
  try{localStorage.setItem('programming-language',value);}catch(_){}
  showGameResult();
}
let savedLanguage='ja';try{savedLanguage=localStorage.getItem('programming-language')==='en'?'en':'ja';}catch(_){}
language(savedLanguage);
document.getElementById('language-toggle').addEventListener('click',()=>language(document.documentElement.lang==='ja'?'en':'ja'));
window.addEventListener('storage',event=>{if(event.key==='programming-language')language(event.newValue==='en'?'en':'ja');});
try {
  const destination=new URL(query.get('return')||'../../agenda.html?open=04#week-04',location.href);
  if(query.has('p'))destination.searchParams.set('p','');
  if(destination.origin===location.origin && /\/(?:index|agenda)\.html$/.test(destination.pathname))document.getElementById('lecture-return').href=destination.href;
}catch(_){}
document.querySelectorAll('pre code').forEach(code=>{
  if(code.closest('.lecture-cell-output'))return;
  const source=code.textContent;
  const pattern=/(#[^\n]*)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|\b(if|elif|else|and|or|not|in|import|while|break|True|False)\b|\b(print|input|int|float|len|list|map)\b|\b(\d+(?:\.\d+)?)\b/g;
  let position=0;code.replaceChildren();
  for(const match of source.matchAll(pattern)) {
    code.append(document.createTextNode(source.slice(position,match.index)));
    const token=document.createElement('span');
    token.className=match[1]?'syntax-comment':match[2]?'syntax-string':match[3]?'syntax-keyword':match[4]?'syntax-function':'syntax-number';
    token.textContent=match[0];code.append(token);position=match.index+match[0].length;
  }
  code.append(document.createTextNode(source.slice(position)));
});
function showSlide(value) {
  index=Math.max(0,Math.min(slides.length-1,value));
  slides.forEach((slide,i)=>slide.hidden=i!==index);
  document.getElementById('slide-count').textContent=String(index+1).padStart(2,'0')+' / '+slides.length;
  previous.disabled=index===0;next.disabled=index===slides.length-1;stage.scrollTop=0;
  const url=new URL(location.href);url.searchParams.set('slide',index+1);history.replaceState(null,'',url);
}
previous.addEventListener('click',()=>showSlide(index-1));next.addEventListener('click',()=>showSlide(index+1));
document.addEventListener('keydown',event=>{
  if(event.target.closest('input,textarea,select'))return;
  if(['ArrowLeft','ArrowRight'].includes(event.key)){event.preventDefault();showSlide(index+(event.key==='ArrowRight'?1:-1));}
  if(event.key==='Escape'){view.classList.remove('is-fullscreen-fallback');updateFullscreen();}
});
let touch=null;
stage.addEventListener('touchstart',event=>{
  if(event.touches.length!==1 || event.target.closest('button,a'))return;
  touch={x:event.touches[0].clientX,y:event.touches[0].clientY};
},{passive:true});
stage.addEventListener('touchend',event=>{
  if(!touch || !event.changedTouches.length)return;
  const dx=event.changedTouches[0].clientX-touch.x,dy=event.changedTouches[0].clientY-touch.y;touch=null;
  if(Math.abs(dx)>60 && Math.abs(dx)>Math.abs(dy)*1.5)showSlide(index+(dx<0?1:-1));
},{passive:true});
stage.addEventListener('touchcancel',()=>touch=null,{passive:true});
function updateFullscreen(){fullscreen.setAttribute('aria-pressed',String(document.fullscreenElement===view || view.classList.contains('is-fullscreen-fallback')));}
fullscreen.addEventListener('click',async()=>{
  if(document.fullscreenElement===view)await document.exitFullscreen();
  else if(view.classList.contains('is-fullscreen-fallback'))view.classList.remove('is-fullscreen-fallback');
  else {try{await view.requestFullscreen();}catch(_){view.classList.add('is-fullscreen-fallback');}}
  updateFullscreen();
});
document.addEventListener('fullscreenchange',updateFullscreen);
document.querySelectorAll('[data-reveal]').forEach((button,i)=>{
  const cell=button.closest('.lecture-notebook-cell'),output=cell.nextElementSibling;
  output.id='example-output-'+i;button.setAttribute('aria-controls',output.id);
  button.addEventListener('click',()=>{output.hidden=!output.hidden;button.setAttribute('aria-expanded',String(!output.hidden));});
});
function showGameResult() {
  if(!gameResult)return;
  const {player,computer,branch}=gameResult,en=document.documentElement.lang==='en';
  const names={'グー':'Rock','チョキ':'Scissors','パー':'Paper'};
  const outcomes=en?{draw:'Draw!',win:'You win!',lose:'Computer wins!'}:{draw:'あいこ！',win:'あなたの勝ち！',lose:'コンピュータの勝ち！'};
  document.getElementById('janken-result').textContent=(en?'You: '+names[player]+' / Computer: '+names[computer]:'あなた：'+player+' / 相手：'+computer)+'　'+outcomes[branch];
  document.getElementById('janken-rule').textContent=branch==='draw'?'player == computer  # True':branch==='win'?'player == "'+player+'" and computer == "'+computer+'"  # True':'else:';
}
document.querySelectorAll('[data-hand]').forEach(button=>button.addEventListener('click',()=>{
  const player=button.dataset.hand,computer=['グー','チョキ','パー'][Math.floor(Math.random()*3)];
  const win=(player==='グー'&&computer==='チョキ')||(player==='チョキ'&&computer==='パー')||(player==='パー'&&computer==='グー');
  gameResult={player,computer,branch:player===computer?'draw':win?'win':'lose'};showGameResult();
}));
showSlide(Math.max(0,(Number(query.get('slide'))||1)-1));

