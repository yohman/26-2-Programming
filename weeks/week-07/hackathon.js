/* A clock based on a deadline, so it stays accurate across slide changes. */
(function(root){
  'use strict';
  const remaining=(state,now)=>Math.max(0,state.deadline===null?state.remainingMs:state.deadline-now);
  const reset=durationMs=>({durationMs,remainingMs:durationMs,deadline:null});
  const start=(state,now)=>({...state,deadline:now+remaining(state,now)});
  const pause=(state,now)=>({...state,remainingMs:remaining(state,now),deadline:null});
  const format=milliseconds=>{const seconds=Math.ceil(Math.max(0,milliseconds)/1000);return String(Math.floor(seconds/60)).padStart(2,'0')+':'+String(seconds%60).padStart(2,'0');};
  const api={remaining,reset,start,pause,format};
  if(typeof module!=='undefined'&&module.exports){module.exports=api;return;}
  root.WeatherHackathon=api;
  if(typeof document==='undefined')return;
  const isJapanese=()=>document.documentElement.lang==='ja';
  document.querySelectorAll('[data-countdown]').forEach(clock=>{
    const duration=clock.querySelector('[data-clock-duration]'),toggle=clock.querySelector('[data-clock-toggle]');
    const output=clock.querySelector('[data-clock]'),status=clock.querySelector('[data-clock-status]');
    const multiplier=clock.dataset.unit==='minutes'?60000:1000;
    const key='programming:w7-weather:'+clock.dataset.countdown;
    const initial=reset(Number(clock.dataset.seconds)*1000);
    let state=initial;
    function restore(value){
      try{const saved=JSON.parse(value);if(saved&&Number.isFinite(saved.durationMs)&&saved.durationMs>=1000&&saved.durationMs<=10800000&&Number.isFinite(saved.remainingMs)&&saved.remainingMs>=0&&(saved.deadline===null||Number.isFinite(saved.deadline)))state=saved;}catch{}
    }
    try{restore(localStorage.getItem(key));}catch{}
    function save(){try{localStorage.setItem(key,JSON.stringify(state));}catch{}}
    function render(){
      const left=remaining(state,Date.now());
      if(left===0&&state.deadline!==null){state={...state,remainingMs:0,deadline:null};save();}
      const running=state.deadline!==null;
      output.textContent=format(left);
      clock.classList.toggle('time-up',left===0);
      toggle.textContent=running?'Ⅱ':'▶';
      toggle.setAttribute('aria-label',running?'Pause / 一時停止':'Start / 開始');
      toggle.setAttribute('aria-pressed',String(running));
      toggle.disabled=left===0;
      duration.disabled=running;
      if(document.activeElement!==duration)duration.value=String(state.durationMs/multiplier);
      const message=left===0?(isJapanese()?'時間です':'Time is up'):running?(isJapanese()?'進行中':'Running'):(isJapanese()?'開始／再開できます':'Ready / paused');
      if(status.textContent!==message)status.textContent=message;

    }
    toggle.addEventListener('click',()=>{state=state.deadline===null?start(state,Date.now()):pause(state,Date.now());save();render();});
    clock.querySelector('[data-clock-reset]').addEventListener('click',()=>{state=reset(state.durationMs);save();render();});
    const updateDuration=()=>{if(!duration.validity.valid)return;state=reset(Number(duration.value)*multiplier);save();render();};
    duration.addEventListener('input',updateDuration);
    duration.addEventListener('change',updateDuration);
    window.addEventListener('storage',event=>{if(event.key===key){state=initial;restore(event.newValue);render();}});
    new MutationObserver(render).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
    setInterval(render,250);render();
  });
})(typeof globalThis==='undefined'?this:globalThis);
