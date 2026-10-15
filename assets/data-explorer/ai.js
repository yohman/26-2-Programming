let worker,host,language='ja',busy=false,result=null;
let inputText='この映画が大好き！もう一度見たい。';
let message='idle',download=null,errorMessage='';
const say=(ja,en)=>language==='en'?en:ja;
const examples=[
  ['好き','Positive','この映画が大好き！もう一度見たい。'],
  ['がっかり','Negative','楽しみにしていたのに、つまらなくてがっかりした。'],
  ['事実だけ','Neutral','この映画は金曜日に公開されます。'],
  ['皮肉？','Sarcasm?','最高だね。また電車が遅れた。'],
  ['English','English','The food was amazing, but the service was terrible.']
];
const labelText=label=>({positive:say('Positive · 肯定的','Positive'),neutral:say('Neutral · 中立','Neutral'),negative:say('Negative · 否定的','Negative')}[label]||label);
function element(tag,text,className) {
  const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(className)el.className=className;return el;
}
export function mountAI(target,locale) {
  if(host===target && language===locale && target.childElementCount)return;
  host=target;language=locale;draw();
}
function updateStatus() {
  const status=host.querySelector('.ai-status');
  status.textContent=message==='error'?say('読み込めませんでした。ネット接続を確認して、もう一度実行してください。','Could not load the model. Check your connection and try again.'):
    message==='loading'?say('モデルを読み込み中… 初回は少し時間がかかります。','Loading the model… The first run can take a while.'):
    message==='running'?say('この端末で分析中…','Analyzing on this device…'):
    message==='done'?say('この端末で実行しました。文章はAIサーバーに送っていません。','Computed on this device. Your text was not sent to an AI server.'):
    say('実行すると初回のみ約135 MBのモデルをダウンロードします。','The first run downloads a model of approximately 135 MB.');
  const progress=host.querySelector('.ai-progress');progress.hidden=message!=='loading';
  if(message==='error' && errorMessage)status.textContent+=' ('+errorMessage+')';
  if(download && message==='loading'){progress.value=download.progress;progress.setAttribute('aria-label',say('モデルのダウンロード','Model download'));status.textContent+=' '+download.progress+'%';}
  else progress.removeAttribute('value');
  host.querySelector('.ai-run').disabled=busy;
  host.querySelector('.ai-run').textContent=busy?say('処理中…','Working…'):say('AIで分析する ▶','Analyze with AI ▶');
  host.querySelector('.ai-cancel').hidden=!busy;
}
function run() {
  const text=inputText.trim();if(!text || busy)return;
  busy=true;result=null;download=null;message=worker?'running':'loading';drawResults();updateStatus();
  try {
    if(!worker) {
      worker=new Worker(new URL('./ai-worker.js?v=20261015',import.meta.url),{type:'module'});
      worker.onmessage=event=>{
        const data=event.data;
        if(data.type==='progress'){download=data;message='loading';updateStatus();}
        else if(data.type==='ready'||data.type==='running'){message='running';updateStatus();}
        else if(data.type==='result') {busy=false;message='done';result={model:data.model,input:data.input,predictions:data.output};drawResults();updateStatus();}
        else if(data.type==='error')fail(data);
      };
      worker.onerror=fail;
    }
    worker.postMessage({type:'analyze',text});
  }catch(_){fail();}
}
function fail(error){errorMessage=error?.message||'';worker?.terminate();worker=null;busy=false;message='error';updateStatus();}
function draw() {
  host.replaceChildren();
  const form=element('form',undefined,'ai-form');
  const label=element('label',say('まず、どんな文章に見える？（200文字まで）','First, how would you read this sentence? (200 characters max)'));label.htmlFor='ai-text';
  const textarea=element('textarea');textarea.id='ai-text';textarea.rows=3;textarea.maxLength=200;textarea.value=inputText;
  textarea.addEventListener('input',()=>{inputText=textarea.value;host.querySelector('.ai-edit-note').hidden=!result || inputText===result.input;});
  const choices=element('div',undefined,'ai-examples');
  examples.forEach(([ja,en,text])=>{
    const button=element('button',say(ja,en));button.type='button';
    button.addEventListener('click',()=>{inputText=text;textarea.value=text;host.querySelector('.ai-edit-note').hidden=!result || inputText===result.input;textarea.focus();});choices.append(button);
  });
  const actions=element('div',undefined,'ai-actions');
  const button=element('button',undefined,'ai-run');button.type='submit';
  const cancel=element('button',say('中止','Cancel'),'ai-cancel');cancel.type='button';cancel.addEventListener('click',()=>{worker?.terminate();worker=null;busy=false;message='idle';download=null;updateStatus();});actions.append(button,cancel);
  const note=element('p',undefined,'ai-status');note.setAttribute('role','status');note.setAttribute('aria-live','polite');
  const progress=element('progress',undefined,'ai-progress');progress.max=100;
  const editor=element('div',undefined,'ai-editor');editor.append(textarea);
  form.append(label,editor,choices,actions,note,progress);form.addEventListener('submit',event=>{event.preventDefault();run();});host.append(form);
  const edited=element('p',say('文章を変更しました。もう一度分析してください。','Text changed. Analyze again to update the result.'),'ai-edit-note');edited.hidden=!result || inputText===result.input;host.append(edited);
  const results=element('div',undefined,'ai-results');results.setAttribute('aria-live','polite');host.append(results);
  const tip=element('aside',undefined,'ai-tip');tip.append(element('strong','Try this'),element('p',say('「好き」を「嫌い」に変える。皮肉な文章を入れる。AIの判定は、自分の読み方と一致する？','Change “love” to “hate.” Try sarcasm. Does the prediction match your reading?')));host.append(tip);
  host.append(element('p',say('これはチャットではなく、文章の分類モデルです。スコアはモデルの予測で、正答率や書いた人の本当の気持ちではありません。日本語・英語に対応しますが、皮肉や文脈を読み違えることがあります。','This is a text classifier, not a chatbot. Scores are model predictions—not accuracy or the writer’s true feelings. It supports Japanese and English but can misread sarcasm and context.'),'subtle'));
  const source=element('p',undefined,'subtle');
  const link=element('a',say('モデルの説明 ↗','About the model ↗'));link.href='https://huggingface.co/lxyuan/distilbert-base-multilingual-cased-sentiments-student';link.target='_blank';link.rel='noopener';source.append(link,document.createTextNode(say(' · APIキー不要 · 初回はネット接続が必要 · モデルはブラウザーにキャッシュされます。',' · No API key · Internet needed for initial download · Model cached in the browser.')));host.append(source);
  drawResults();updateStatus();
}
function drawResults() {
  const results=host.querySelector('.ai-results');results.replaceChildren();
  if(!result){results.append(element('p',say('文章を選び、自分で予想してから実行しよう。','Choose a sentence, make your prediction, then run it.'),'subtle'));return;}
  const predictions=(Array.isArray(result.predictions[0])?result.predictions[0]:result.predictions).slice().sort((a,b)=>b.score-a.score);
  const chart=element('div',undefined,'ai-chart');chart.append(element('h3',say('AIの予測','AI prediction')));
  const quote=element('p',result.input,'ai-input-quote');chart.append(quote);
  predictions.forEach(prediction=>{
    const row=element('div',undefined,'ai-score');
    const label=element('span',labelText(prediction.label));
    const track=element('div',undefined,'ai-score-track'),fill=element('div',undefined,'ai-score-fill');
    fill.dataset.label=prediction.label;fill.style.width=(prediction.score*100)+'%';track.append(fill);
    row.append(label,track,element('strong',(prediction.score*100).toFixed(1)+'%'));chart.append(row);
  });results.append(chart);
  const details=element('details',undefined,'ai-json');details.open=true;details.append(element('summary',say('同じ結果をJSONで見る','The same result as JSON')));
  const pre=element('pre'),code=element('code');
  const raw=JSON.stringify(result,null,2),pattern=/"(?:\\.|[^"\\])*"(?=\s*:)|"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|\b(?:true|false|null)\b/g;
  let offset=0;
  for(const match of raw.matchAll(pattern)) {
    code.append(document.createTextNode(raw.slice(offset,match.index)));
    const token=match[0],key=token.startsWith('"') && /^\s*:/.test(raw.slice(match.index+token.length));
    code.append(element('span',token,key?'json-key':token.startsWith('"')?'json-string':/^[-\d]/.test(token)?'json-number':'json-literal'));
    offset=match.index+token.length;
  }
  code.append(document.createTextNode(raw.slice(offset)));pre.append(code);details.append(pre);
  details.append(element('p',say('predictionsはリスト。一つの辞書にはlabel（文字列）とscore（小数）が入っている。','predictions is a list. Each dictionary has a label (string) and a score (float).'),'subtle'));results.append(details);
  host.querySelector('.ai-edit-note').hidden=inputText===result.input;
}
