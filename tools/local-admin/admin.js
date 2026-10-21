/* Local review UI. Student HTML is confined to opaque-origin sandboxed frames. */
const localAdmin = ['127.0.0.1','localhost','[::1]'].includes(location.hostname);
const adminRoot = document.getElementById('admin-content');
let manifest, currentSubmission, selectedMode='saved', selectedTab='notebook';
const params=new URLSearchParams(location.search);
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const joined=value=>Array.isArray(value)?value.join(''):value||'';
const fileURL=path=>'./'+path.split('/').map(encodeURIComponent).join('/');
const heartsStorageKey='programming-admin-hearts-v1';
let hearts=new Set();
try { hearts=new Set(JSON.parse(localStorage.getItem(heartsStorageKey)||'[]')); } catch {}
let publishing=false;
async function publishHearts(next) {
  if(publishing)throw new Error('公開更新中です。少し待ってから操作してください。');
  publishing=true;
  const status=document.getElementById('admin-status');
  status.textContent='公開ギャラリーを更新・送信中…';
  try {
    const response=await fetch('/__admin/gallery',{method:'POST',headers:{'Content-Type':'application/json','X-Admin-Request':'gallery'},body:JSON.stringify([...next])});
    if(!response.ok)throw new Error('公開更新に失敗しました。同じハートをもう一度押して再試行してください。');
    const result=await response.json();
    status.textContent='公開ギャラリー：'+result.count+'作品 · 送信済み（GitHub Pages反映まで少し時間がかかります）';
  } finally {publishing=false;}
}
// Generated preview IDs change after a re-import; the original submission identity does not.
const heartKey=(record,week=record.week)=>JSON.stringify([Number(week),record.student,record.file||'']);
function heartButton(record,week=record.week,onChange=()=>{}) {
  const button=document.createElement('button');
  button.className='submission-heart';
  const update=()=>{
    const selected=hearts.has(heartKey(record,week));
    button.setAttribute('aria-pressed',String(selected));
    button.setAttribute('aria-label',selected?'公開ギャラリーから外す':'公開ギャラリーに追加');
    button.innerHTML='<span aria-hidden="true">'+(selected?'♥':'♡')+'</span> '+(selected?'公開中':'公開する');
  };
  update();
  button.onclick=async()=>{
    const key=heartKey(record,week),next=new Set(hearts);
    next.has(key)?next.delete(key):next.add(key);
    button.disabled=true;
    try { await publishHearts(next);hearts=next;try{localStorage.setItem(heartsStorageKey,JSON.stringify([...next]));}catch{}update();onChange(); }
    catch(error){document.getElementById('admin-status').textContent=error.message;}
    finally{button.disabled=false;}
  };
  return button;
}
const policy="default-src 'none'; script-src 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com https://code.jquery.com https://maxcdn.bootstrapcdn.com; style-src 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com https://maxcdn.bootstrapcdn.com https://fonts.googleapis.com; img-src data: blob: https://raw.githubusercontent.com/PokeAPI/sprites/ https://tile.openstreetmap.org https://*.tile.openstreetmap.org https://*.basemaps.cartocdn.com https://server.arcgisonline.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com; font-src data: https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; frame-src about: data: blob:; connect-src 'none'; form-action 'none'; base-uri 'none'";
function outputElement(output) {
  const wrapper=document.createElement('div');wrapper.className='review-output';
  const data=output.data||{};
  if(data['text/html']) {
    const original=joined(data['text/html']);
    // OSM's volunteer tile server rejects opaque-origin iframe requests.
    const preview=original.replace(/https:\/\/(?:\{s\}\.|[abc]\.)?tile\.openstreetmap\.org\/\{z\}\/\{x\}\/\{y\}\.png/g,'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}');
    if(preview!==original){const note=document.createElement('p');note.className='review-legend';note.textContent='背景のみプレビュー用に置換。原本・コード・地震データは変更していません。 ';const credit=document.createElement('a');credit.href='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer';credit.target='_blank';credit.rel='noopener';credit.textContent='© Esri World Topo Map · 出典';note.append(credit);wrapper.append(note);}
    const frame=document.createElement('iframe');frame.sandbox='allow-scripts';frame.referrerPolicy='no-referrer';frame.loading='lazy';frame.title='Notebook HTML output';
    frame.srcdoc='<meta http-equiv="Content-Security-Policy" content="'+esc(policy)+'">'+preview;wrapper.append(frame);
  } else if(data['text/markdown']) {
    const section=document.createElement('div');section.className='review-markdown';section.innerHTML=markdownHtml(joined(data['text/markdown']));section.querySelectorAll('a').forEach(a=>{if(!['http:','https:'].includes(new URL(a.href,location.href).protocol))a.removeAttribute('href');a.target='_blank';a.rel='noopener';});wrapper.append(section);
  } else if(data['application/vnd.jupyter.widget-view+json']) {
    const note=document.createElement('p');note.className='review-warning';note.textContent='この操作にはJupyterのPythonカーネルが必要です。保存済みのHTML・画像・テキスト出力は、ほかのCellで確認できます。';wrapper.append(note);
  } else if(data['image/png']||data['image/jpeg']) {
    const image=document.createElement('img');const type=data['image/png']?'png':'jpeg';image.src='data:image/'+type+';base64,'+joined(data['image/'+type]);image.alt='Notebook output';wrapper.append(image);
  } else {
    const pre=document.createElement('pre');pre.textContent=joined(output.text||data['text/plain'])||(output.ename?output.ename+': '+output.evalue:'Unsupported output format');wrapper.append(pre);
  }
  return wrapper;
}
function cellsFor(record) {
  const replay=new Map(record.replay.cells.map(cell=>[cell.cell,cell]));
  return (record.notebook?.cells||[]).map((cell,index)=>({cell,index,run:replay.get(index),outputs:selectedMode==='saved'?cell.outputs||[]:replay.get(index)?.outputs||[]}));
}
function renderResults(record) {
  const host=document.createElement('div'),cells=cellsFor(record);
  const recovered=record.replay.cells.flatMap(cell=>cell.outputs.filter(o=>o.metadata?.local_widget_preview));
  const htmlOutputs=cells.flatMap(cell=>cell.outputs.filter(o=>o.data?.['text/html']).map(output=>({output,index:cell.index})));
  const latest=htmlOutputs.at(-1);
  host.innerHTML='<p class="review-legend">'+(selectedMode==='saved'?'提出時にNotebookに保存されていた出力。':'元コードをローカルで再実行した出力。CSVの別名対応・スキップ・エラーは下記に記載。原本の修正ではありません。')+'</p>';
  if(selectedMode==='saved'&&recovered.length){const label=document.createElement('h3');label.textContent='インタラクティブHTML';const note=document.createElement('p');note.className='review-legend';note.textContent='保存済みWidgetは単独では表示できないため、提出コードからローカルで再現。選択肢を切り替えられます。';host.append(label,note);recovered.forEach(output=>host.append(outputElement(output)));}
  if(latest){const label=document.createElement('h3');label.textContent='最後のHTML出力 · Cell '+(latest.index+1);host.append(label,outputElement(latest.output));}
  else {const p=document.createElement('p');p.textContent='この表示にはHTML出力がありません。「Notebook」で各Cellを確認できます。';host.append(p);}
  cells.filter(cell=>cell.outputs.some(o=>!o.data?.['text/html'])).forEach(cell=>{
    const details=document.createElement('details');details.className='review-cell';details.open=cell.outputs.some(o=>o.data?.['image/png']||o.data?.['image/jpeg']) || cell.outputs.reduce((n,o)=>n+joined(o.text||o.data?.['text/plain']).length,0)<5000;details.innerHTML='<summary>Cell '+(cell.index+1)+' · 出力</summary>';
    cell.outputs.filter(o=>!o.data?.['text/html']).forEach(output=>details.append(outputElement(output)));host.append(details);
  });
  if(selectedMode==='replay') {
    const notices=[...record.replay.notes,...record.replay.cells.filter(c=>c.message).map(c=>'Cell '+(c.cell+1)+': '+c.message)];
    notices.forEach(note=>{const p=document.createElement('p');p.className='review-warning';p.textContent=note;host.append(p);});
  }
  if(!record.notebook)record.attachments.filter(a=>['PNG','JPG','JPEG'].includes(a.type)).forEach(a=>{const image=document.createElement('img');image.src=fileURL(a.path);image.style.maxWidth='100%';host.append(image);});
  return host;
}
function renderNotebook(record) {
  if(!record.notebook)return renderAttachments(record);
  const host=document.createElement('div');host.className='review-notebook';
  cellsFor(record).forEach(({cell,index,run,outputs})=>{
    if(cell.cell_type==='markdown') {const section=document.createElement('section');section.className='review-markdown';section.innerHTML=markdownHtml(joined(cell.source).replace(/^(\s*)\* /gm,'$1- '));section.querySelectorAll('a').forEach(a=>{if(!['http:','https:'].includes(new URL(a.href,location.href).protocol)){a.removeAttribute('href');}a.target='_blank';a.rel='noopener noreferrer';});host.append(section);return;}
    const section=document.createElement('section');section.className='notebook-code-cell';
    const count=selectedMode==='saved'?cell.execution_count:null;
    section.setAttribute('aria-label','Cell '+(index+1)+' · '+(cell.cell_type==='code'?'Python':'Raw'));
    section.innerHTML='<div class="notebook-input"><span class="notebook-prompt" title="'+(selectedMode==='saved'?'提出時の実行番号':'ローカル再実行')+'">['+esc(count??' ')+']</span><pre class="review-code"><code>'+notebookCodeHtml(joined(cell.source))+'</code></pre></div>';
    const outputHost=document.createElement('div');outputHost.className='notebook-cell-outputs';
    const reconstructed=selectedMode==='saved'&&outputs.some(o=>o.data?.['application/vnd.jupyter.widget-view+json'])?(run?.outputs||[]).filter(o=>o.metadata?.local_widget_preview):[];
    outputs.filter(o=>!reconstructed.length||(!o.data?.['application/vnd.jupyter.widget-view+json']&&!joined(o.data?.['text/plain']).startsWith('<function '))).forEach(output=>outputHost.append(outputElement(output)));
    if(reconstructed.length){const note=document.createElement('p');note.className='notebook-replay-note';note.textContent='Widget表示：提出コードからローカルで再現（保存済み出力ではありません）。';outputHost.append(note);reconstructed.forEach(output=>outputHost.append(outputElement(output)));}
    if(selectedMode==='replay'&&run?.message){const note=document.createElement('p');note.className='review-warning';note.textContent=run.message;outputHost.append(note);}
    section.append(outputHost);host.append(section);
  });return host;
}
function notebookCodeHtml(source) {
  // Tokenize before escaping so entities and HTML inside Python strings stay intact.
  const tokens=/(#[^\n]*|(?:[fFrRuUbB]{0,2})(?:"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')|\b(?:def|return|if|elif|else|for|while|in|import|from|as|with|try|except|class|pass|not|and|or|lambda)\b|\b(?:print|input|type|int|float|str|bool|len|range|display)\b|\b(?:True|False|None)\b|\b\d+(?:\.\d+)?\b)/g;
  let html='',offset=0;
  for(const match of source.matchAll(tokens)) {
    const token=match[0];
    const kind=token.startsWith('#')?'comment':/^[fFrRuUbB]*["']/.test(token)?'string':/^\d/.test(token)?'number':/^(True|False|None)$/.test(token)?'constant':/^(print|input|type|int|float|str|bool|len|range|display)$/.test(token)?'function':'keyword';
    html+=esc(source.slice(offset,match.index))+'<span class="syntax-'+kind+'">'+esc(token)+'</span>';offset=match.index+token.length;
  }
  return html+esc(source.slice(offset));
}
function renderAttachments(record) {
  const host=document.createElement('div');host.className='attachment-list';
  record.attachments.forEach(file=>{
    const details=document.createElement('details');details.innerHTML='<summary>'+esc(file.name)+' · '+esc(file.type)+'</summary><a download href="'+esc(fileURL(file.path))+'">原本をダウンロード</a>';
    if(file.table){const label=document.createElement('p');label.textContent=file.table.total.toLocaleString()+'行（先頭100行を表示）';details.append(label);const table=document.createElement('div');table.className='attachment-table';table.innerHTML='<table><thead><tr>'+file.table.headers.map(x=>'<th>'+esc(x)+'</th>').join('')+'</tr></thead><tbody>'+file.table.rows.map(row=>'<tr>'+row.map(x=>'<td>'+esc(x)+'</td>').join('')+'</tr>').join('')+'</tbody></table>';details.append(table);}
    if(['PNG','JPG','JPEG'].includes(file.type)){const image=document.createElement('img');image.src=fileURL(file.path);image.style.maxWidth='100%';details.append(image);}
    host.append(details);
  });return host;
}
function notebookNavigation(records,id,href) {
  const index=records.findIndex(record=>record.id===id);
  const nav=document.createElement('nav');nav.className='notebook-navigation';nav.setAttribute('aria-label','Notebook navigation');
  const item=(record,label)=>record?'<a href="'+esc(href(record))+'"><span>'+label+'</span><small>'+esc(record.student_name||record.title)+'</small></a>':'<span class="notebook-nav-disabled" aria-disabled="true">'+label+'</span>';
  nav.innerHTML=item(records[index-1],'← 前へ')+'<span class="notebook-nav-count">'+(index+1)+' / '+records.length+'</span>'+item(records[index+1],'次へ →');
  return nav;
}
function renderSubmission(record) {
  currentSubmission=record;
  adminRoot.innerHTML='<a href="?week='+record.week+'#submission-'+esc(record.id)+'">← Week '+String(record.week).padStart(2,'0')+' の一覧</a><header class="submission-heading"><p class="student-name">'+esc(record.student_name||('名簿未一致 · '+record.student))+'</p>'+(record.student_reading?'<span class="student-reading">'+esc(record.student_reading)+'</span>':'')+'<p>学籍番号：'+esc(record.student)+'</p><h2>'+esc(record.title)+'</h2><p>'+esc(record.file||'Notebookなし')+'</p></header><div class="submission-actions"><button data-mode="saved" aria-pressed="'+(selectedMode==='saved')+'">提出時の出力</button><button data-mode="replay" aria-pressed="'+(selectedMode==='replay')+'">ローカル再実行</button></div><nav class="review-tabs"><button data-tab="results" aria-pressed="'+(selectedTab==='results')+'">結果</button><button data-tab="notebook" aria-pressed="'+(selectedTab==='notebook')+'">Notebook</button><button data-tab="files" aria-pressed="'+(selectedTab==='files')+'">添付ファイル</button></nav><div id="submission-body"></div>';
  document.getElementById('submission-body').append(selectedTab==='files'?renderAttachments(record):selectedTab==='notebook'?renderNotebook(record):renderResults(record));
  adminRoot.querySelector('.submission-actions').prepend(heartButton(record));
  adminRoot.querySelector('.review-tabs').prepend(adminRoot.querySelector('[data-tab="notebook"]'));
  const entries=manifest.weeks.find(week=>week.week===record.week)?.submissions||[];
  const navigation=()=>notebookNavigation(entries,record.id,item=>'?week='+record.week+'&id='+item.id);
  adminRoot.querySelector('.submission-heading').before(navigation());
  adminRoot.append(navigation());
  adminRoot.querySelectorAll('[data-mode]').forEach(button=>button.onclick=()=>{selectedMode=button.dataset.mode;renderSubmission(record);});
  adminRoot.querySelectorAll('[data-tab]').forEach(button=>button.onclick=()=>{selectedTab=button.dataset.tab;renderSubmission(record);});
}
function renderWeek(week) {
  const data=manifest.weeks.find(w=>w.week===week);
  adminRoot.innerHTML='<div class="admin-toolbar"><h2>Week '+String(week).padStart(2,'0')+' · '+(data?data.students+'人 / '+data.submissions.length+'プレビュー':'未取り込み')+'</h2><input id="student-search" placeholder="氏名・学籍番号・ファイル名で検索" aria-label="Search submissions"></div><div class="submission-grid"></div>';
  const cards=query=>{const host=adminRoot.querySelector('.submission-grid');host.replaceChildren();(data?.submissions||[]).filter(s=>((s.student_name||'')+' '+(s.student_reading||'')+' '+s.student+' '+s.title+' '+s.file).toLowerCase().includes(query.toLowerCase())).forEach(s=>{const card=document.createElement('article');card.className='submission-card';card.id='submission-'+s.id;card.innerHTML='<span class="student-name" title="学籍番号：'+esc(s.student)+'">'+esc(s.student_name||('名簿未一致 · '+s.student))+'</span>'+(s.student_reading?'<span class="student-reading">'+esc(s.student_reading)+'</span>':'')+'<h3>'+esc(s.title)+'</h3><p>'+s.attachments+'添付 · 保存済み出力 '+s.saved_outputs+' Cell<br>再実行 '+s.execution.ok+' Cell · エラー '+s.execution.error+' · スキップ '+s.execution.skipped+'</p><a class="admin-button" href="?week='+week+'&id='+s.id+'">課題をプレビュー →</a>';host.append(card);});};cards('');
  const search=adminRoot.querySelector('input');
  const filter=document.createElement('button');
  filter.className='heart-filter';filter.setAttribute('aria-pressed','false');
  const controls=document.createElement('div');controls.className='admin-filters';
  search.replaceWith(controls);controls.append(search,filter);
  let heartedOnly=false;
  const redraw=()=>{
    cards(search.value);
    filter.textContent='♥ のみ ('+(data?.submissions||[]).filter(s=>hearts.has(heartKey(s,week))).length+')';
    filter.setAttribute('aria-pressed',String(heartedOnly));
    adminRoot.querySelectorAll('.submission-card').forEach(card=>{
      const record=data.submissions.find(s=>'submission-'+s.id===card.id);
      if(heartedOnly&&!hearts.has(heartKey(record,week))){card.remove();return;}
      card.prepend(heartButton(record,week,redraw));
    });
    if(!adminRoot.querySelector('.submission-card')){
      const empty=document.createElement('p');empty.className='review-legend';
      empty.textContent=heartedOnly?'紹介候補がありません。各課題の♡で追加できます。':'一致する課題がありません。';
      adminRoot.querySelector('.submission-grid').append(empty);
    }
  };
  filter.onclick=()=>{heartedOnly=!heartedOnly;redraw();};
  search.oninput=redraw;redraw();
  const note=document.createElement('p');note.className='review-legend';note.textContent='♥ の作品は氏名付きで公開されます。外すと公開ギャラリーから削除されます（GitHub Pages反映には少し時間がかかります）。';
  adminRoot.querySelector('.admin-toolbar').after(note);
}
async function loadAdmin() {
  if(!localAdmin){document.querySelector('main').textContent='Local access only.';return;}
  const response=await fetch('_review/index.json',{cache:'no-store'});if(!response.ok)throw new Error('レビューの取り込みが必要です。');manifest=await response.json();
  const week=Number(params.get('week'))||manifest.weeks.at(-1)?.week||1;
  document.getElementById('admin-weeks').innerHTML=Array.from({length:14},(_,i)=>{const number=i+1,data=manifest.weeks.find(w=>w.week===number);return '<a href="?week='+number+'"'+(number===week?' aria-current="page"':'')+'><strong>'+String(number).padStart(2,'0')+'</strong><small>'+(data?data.students+'人':'未取り込み')+'</small></a>';}).join('');
  document.getElementById('admin-status').textContent='更新：'+new Date(manifest.generated).toLocaleString('ja-JP');
  if(manifest.roster)document.getElementById('admin-status').textContent+=' · 名簿一致 '+manifest.roster.matched+'人 / 未一致 '+manifest.roster.unmatched.length+'人'+(manifest.roster.notes.length?' · '+manifest.roster.notes.join(' / '):'');
  if(params.get('id')){
    let id=params.get('id');if(!/^[a-f0-9]{20}$/.test(id))throw new Error('Invalid submission ID');
    const entries=manifest.weeks.flatMap(w=>w.submissions);
    if(!entries.some(s=>s.id===id)){
      const replacement=manifest.weeks.find(w=>w.week===week)?.submissions.find(s=>s.student===currentSubmission?.student && s.file===currentSubmission?.file);
      if(replacement){id=replacement.id;params.set('id',id);history.replaceState(null,'','?'+params);}
      else {params.delete('id');history.replaceState(null,'','?'+params);renderWeek(week);return;}
    }
    const response=await fetch('_review/'+id+'/submission.json',{cache:'no-store'});if(!response.ok)throw new Error('Submission not found');renderSubmission(await response.json());
  }else renderWeek(week);
}
document.addEventListener('DOMContentLoaded',()=>{
  if(!adminRoot)return;
  (async()=>{
    const response=await fetch('/__admin/hearts',{cache:'no-store'});
    if(!response.ok)throw new Error('Adminサーバーを更新してください。');
    const state=await response.json();
    if(state.hearts!==null)hearts=new Set(state.hearts);
    await loadAdmin();
    if(state.hearts===null&&hearts.size)await publishHearts(hearts);
  })().catch(error=>document.getElementById('admin-status').textContent=error.message);
  document.getElementById('refresh').onclick=async event=>{const button=event.currentTarget;button.disabled=true;document.getElementById('admin-status').textContent='新しいファイルを取り込み中…';try{const response=await fetch('/__admin/refresh',{method:'POST',headers:{'X-Admin-Request':'refresh'}});if(!response.ok)throw new Error('ローカルAdminサーバー（8766）で開いてください。');await loadAdmin();}catch(error){document.getElementById('admin-status').textContent=error.message;}finally{button.disabled=false;}};
});
