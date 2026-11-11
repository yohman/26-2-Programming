/* A clock based on a deadline, so it stays accurate across slide changes. */
(function(root){
  'use strict';
  const remaining=(state,now)=>Math.max(0,state.deadline===null?state.remainingMs:state.deadline-now);
  const reset=durationMs=>({durationMs,remainingMs:durationMs,deadline:null});
  const start=(state,now)=>({...state,deadline:now+remaining(state,now)});
  const pause=(state,now)=>({...state,remainingMs:remaining(state,now),deadline:null});
  const format=milliseconds=>{const seconds=Math.ceil(Math.max(0,milliseconds)/1000);return String(Math.floor(seconds/60)).padStart(2,'0')+':'+String(seconds%60).padStart(2,'0');};
  const selectHours=(forecast,maxRain,minTemp)=>forecast.filter(hour=>hour.rain!==null&&hour.temp!==null&&hour.rain<=maxRain&&hour.temp>=minTemp);
  function weatherBoard(forecast,chosen,minTemp,maxRain){
    const escape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const rows=[...chosen,...forecast.filter(hour=>!chosen.includes(hour))].map(hour=>{const match=chosen.includes(hour);return '<tr style="background:'+(match?'#dceee2':'#f1f3f2')+'"><td>'+escape(hour.time.replace('T',' '))+'</td><td>'+Number(hour.temp).toFixed(1)+'</td><td>'+hour.rain+'%</td><td>'+(match?'✓ Match / 合う':'— / 合わない')+'</td></tr>';}).join('');
    return '<div class="weather-board"><strong>'+chosen.length+' / '+forecast.length+' hours match · 条件に合う時間</strong><p>Temperature ≥ '+escape(minTemp)+'°C · Precipitation ≤ '+escape(maxRain)+'% · Japan time · Matches first / 合う時間を先に表示</p><div class="weather-board-scroll"><table><thead><tr><th>Time / 時刻</th><th>°C</th><th>Rain %</th><th>Your rule / 条件</th></tr></thead><tbody>'+rows+'</tbody></table></div>'+(chosen.length?'':'<p>No hours match. Try another setting. / 条件を変えて試そう。</p>')+'</div>';
  }
  const api={remaining,reset,start,pause,format,selectHours,weatherBoard};
  if(typeof module!=='undefined'&&module.exports){module.exports=api;return;}
  root.WeatherHackathon=api;
  if(typeof document==='undefined')return;
  const isJapanese=()=>document.documentElement.lang==='ja';
  const payload=document.getElementById('lesson-data');
  const data=payload?JSON.parse(payload.textContent):{};
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
  function highlight(code,source){
    const pattern=/("[^"]*")|\b(for|in|if|and|from|import)\b|\b(print|len|display|HTML|weather_board)\b|\b(-?\d+(?:\.\d+)?)\b/g;
    code.replaceChildren();let pos=0;
    for(const match of source.matchAll(pattern)){
      code.append(document.createTextNode(source.slice(pos,match.index)));
      const span=document.createElement('span');span.className=match[1]?'syntax-string':match[2]?'syntax-keyword':match[3]?'syntax-function':'syntax-number';span.textContent=match[0];code.append(span);pos=match.index+match[0].length;
    }
    code.append(document.createTextNode(source.slice(pos)));
  }
  document.querySelectorAll('[data-weather-demo]').forEach(demo=>{
    const code=demo.querySelector('[data-weather-code]');
    const rain=demo.querySelector('[data-rain]'),temp=demo.querySelector('[data-temp]');
    function run(){
      if(!rain.reportValidity()||!temp.reportValidity())return;
      const maxRain=Number(rain.value),minTemp=Number(temp.value);
      const source=data.weatherDemo.replace(/^max_rain = .*$/m,'max_rain = '+maxRain).replace(/^min_temp = .*$/m,'min_temp = '+minTemp);
      highlight(code,source);
      const hours=selectHours(data.weather,maxRain,minTemp);
      demo.querySelector('[data-weather-board]').innerHTML=weatherBoard(data.weather,hours,minTemp,maxRain);
    }
    demo.querySelector('[data-weather-run]').addEventListener('click',run);run();
  });
})(typeof globalThis==='undefined'?this:globalThis);
