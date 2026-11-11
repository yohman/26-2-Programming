/* A clock based on a deadline, so it stays accurate across slide changes. */
(function(root){
  'use strict';
  const remaining=(state,now)=>Math.max(0,state.deadline===null?state.remainingMs:state.deadline-now);
  const reset=durationMs=>({durationMs,remainingMs:durationMs,deadline:null});
  const start=(state,now)=>({...state,deadline:now+remaining(state,now)});
  const pause=(state,now)=>({...state,remainingMs:remaining(state,now),deadline:null});
  const format=milliseconds=>{const seconds=Math.ceil(Math.max(0,milliseconds)/1000);return String(Math.floor(seconds/60)).padStart(2,'0')+':'+String(seconds%60).padStart(2,'0');};
  const selectHours=(forecast,maxRain,minTemp)=>forecast.filter(hour=>hour.rain!==null&&hour.temp!==null&&hour.rain<=maxRain&&hour.temp>=minTemp);
  const phaseFor=(state,now)=>{const left=remaining(state,now),elapsed=state.durationMs-left;return left===0?'complete':elapsed<state.durationMs/6?'solo-a':elapsed<state.durationMs*.75?'team':'solo-b';};
  function weatherBoard(forecast,chosen,minTemp,maxRain){
    const escape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const rows=[...chosen,...forecast.filter(hour=>!chosen.includes(hour))].map(hour=>{const match=chosen.includes(hour);return '<tr style="background:'+(match?'#dceee2':'#f1f3f2')+'"><td>'+escape(hour.time.replace('T',' '))+'</td><td>'+Number(hour.temp).toFixed(1)+'</td><td>'+hour.rain+'%</td><td>'+(match?'✓ Match / 合う':'— / 合わない')+'</td></tr>';}).join('');
    return '<div class="weather-board"><strong>'+chosen.length+' / '+forecast.length+' hours match · 条件に合う時間</strong><p>Temperature ≥ '+escape(minTemp)+'°C · Precipitation ≤ '+escape(maxRain)+'% · Japan time · Matches first / 合う時間を先に表示</p><div class="weather-board-scroll"><table><thead><tr><th>Time / 時刻</th><th>°C</th><th>Rain %</th><th>Your rule / 条件</th></tr></thead><tbody>'+rows+'</tbody></table></div>'+(chosen.length?'':'<p>No hours match. Try another setting. / 条件を変えて試そう。</p>')+'</div>';
  }
  const api={remaining,reset,start,pause,format,selectHours,phaseFor,weatherBoard};
  if(typeof module!=='undefined'&&module.exports){module.exports=api;return;}
  root.WeatherHackathon=api;
  if(typeof document==='undefined')return;
  const isJapanese=()=>document.documentElement.lang==='ja';
  const payload=document.getElementById('lesson-data');
  const data=payload?JSON.parse(payload.textContent):{};
  document.querySelectorAll('[data-countdown]').forEach(clock=>{
    const duration=clock.querySelector('[data-clock-duration]'),toggle=clock.querySelector('[data-clock-toggle]');
    const output=clock.querySelector('[data-clock]'),status=clock.querySelector('[data-clock-status]');
    const phase=clock.closest('[data-slide]')?.querySelector('[data-build-phase]');
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
      if(phase){
        const current=phaseFor(state,Date.now());phase.dataset.phase=current;
        const messages={
          'solo-a':['自力チェックA · AIを閉じて、予想とfor＋ifを書く','SOLO CHECK A · close AI; predict and write for + if'],
          team:['チーム制作 · AIは部分的な相談に。自分で確かめる','TEAM BUILD · limited AI help; test the result yourself'],
          'solo-b':['自力チェックB · AIを閉じて、指定された変更を書く','SOLO CHECK B · close AI and code the announced change'],
          complete:['保存して、全チーム発表へ','Save your work; every team gives a demo']
        };
        phase.textContent=messages[current][isJapanese()?0:1];
      }
    }
    toggle.addEventListener('click',()=>{state=state.deadline===null?start(state,Date.now()):pause(state,Date.now());save();render();});
    clock.querySelector('[data-clock-reset]').addEventListener('click',()=>{state=reset(state.durationMs);save();render();if(clock.dataset.countdown==='build')document.dispatchEvent(new CustomEvent('hackathon:reset-build'));});
    const updateDuration=()=>{if(!duration.validity.valid)return;state=reset(Number(duration.value)*multiplier);save();render();};
    duration.addEventListener('input',updateDuration);
    duration.addEventListener('change',updateDuration);
    window.addEventListener('storage',event=>{if(event.key===key){state=initial;restore(event.newValue);render();}});
    new MutationObserver(render).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
    setInterval(render,250);render();
  });
  const reveal=document.querySelector('[data-solo-reveal]'),prompt=document.querySelector('[data-solo-prompt]');
  if(reveal&&prompt){
    let task=null;try{task=JSON.parse(localStorage.getItem('programming:w7-weather:solo-prompt'));}catch{}
    function showTask(){if(!task||!Number.isFinite(task.temp)||!Number.isFinite(task.rain))return;prompt.hidden=false;prompt.textContent=isJapanese()?'自力チェックB：気温が'+task.temp+'°C以上、降水確率が'+task.rain+'%以下の時間を選び、件数も表示する。実行前の予想、自分で変えたコード、結果と理由を各自のNotebookへ。':'SOLO CHECK B: select hours with temperature ≥ '+task.temp+'°C and rain probability ≤ '+task.rain+'%. Also print the count. Keep your prediction, own code change, result and explanation in your notebook.';}
    reveal.addEventListener('click',()=>{task={temp:[5,10,15,20][Math.floor(Math.random()*4)],rain:[10,30,50][Math.floor(Math.random()*3)]};try{localStorage.setItem('programming:w7-weather:solo-prompt',JSON.stringify(task));}catch{}showTask();});
    document.addEventListener('hackathon:reset-build',()=>{task=null;prompt.hidden=true;try{localStorage.removeItem('programming:w7-weather:solo-prompt');}catch{}});
    new MutationObserver(showTask).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});showTask();
  }
  function highlight(code,source){
    const pattern=/("[^"]*")|\b(for|in|if|and)\b|\b(print)\b|\b(-?\d+(?:\.\d+)?)\b/g;
    code.replaceChildren();let pos=0;
    for(const match of source.matchAll(pattern)){
      code.append(document.createTextNode(source.slice(pos,match.index)));
      const span=document.createElement('span');span.className=match[1]?'syntax-string':match[2]?'syntax-keyword':match[3]?'syntax-function':'syntax-number';span.textContent=match[0];code.append(span);pos=match.index+match[0].length;
    }
    code.append(document.createTextNode(source.slice(pos)));
  }
  document.querySelectorAll('[data-weather-demo]').forEach(demo=>{
    const code=demo.querySelector('[data-weather-code]'),output=demo.querySelector('[data-weather-output]');
    const rain=demo.querySelector('[data-rain]'),temp=demo.querySelector('[data-temp]');
    function run(){
      if(!rain.reportValidity()||!temp.reportValidity())return;
      const maxRain=Number(rain.value),minTemp=Number(temp.value);
      const source='max_rain = '+maxRain+'\nmin_temp = '+minTemp+'\nchosen = []\nfor hour in forecast:\n    if hour["rain"] <= max_rain and hour["temp"] >= min_temp:\n        chosen.append(hour)\n# Display the hours selected by your code';
      highlight(code,source);
      const hours=selectHours(data.weather,maxRain,minTemp);
      demo.querySelector('[data-weather-board]').innerHTML=weatherBoard(data.weather,hours,minTemp,maxRain);
      output.textContent=hours.map(hour=>hour.time+' '+Number(hour.temp).toFixed(1)+' °C '+hour.rain+' %').join('\n')||'(no printed output / 条件に合う時間はありません)';
    }
    demo.querySelector('[data-weather-run]').addEventListener('click',run);run();
  });
})(typeof globalThis==='undefined'?this:globalThis);
