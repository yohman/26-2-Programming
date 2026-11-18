/* Local review UI. Student HTML is confined to opaque-origin sandboxed frames. */
const localAdmin = ['127.0.0.1','localhost','[::1]'].includes(location.hostname);
const adminRoot = document.getElementById('admin-content');
let manifest, reviewGroups, currentSubmission, currentReviewGroup, selectedMode='saved', selectedTab='notebook';
const params=new URLSearchParams(location.search);
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const joined=value=>Array.isArray(value)?value.join(''):value||'';
const fileURL=path=>'./'+path.split('/').map(encodeURIComponent).join('/');
const heartsStorageKey='programming-admin-hearts-v1';
let hearts=new Set();
try { hearts=new Set(JSON.parse(localStorage.getItem(heartsStorageKey)||'[]')); } catch {}
const heartPendingKey='programming-admin-hearts-pending-v1';
let heartSync=null,onHeartChange=()=>{},heartPublication={state:'idle'};
function heartStatus({saving=false,error=null,sync=heartPublication}={}){
  updateHeartButtons();
  heartPublication=sync||heartPublication;
  const status=document.getElementById('admin-status');if(!status)return;
  status.textContent=error?'選択を保存できませんでした。自動で再試行します。':saving?'選択を保存中…':heartPublication.state==='error'?'選択は保存済みです。公開更新を再試行しています。':['pending','publishing'].includes(heartPublication.state)?'選択は保存済みです。公開ギャラリーへ送信中…':'選択は保存済みです。公開サイトへの反映には少し時間がかかります。';
}
function updateHeartButtons(){
  document.querySelectorAll('.submission-heart').forEach(button=>{
    const selected=JSON.parse(button.dataset.heartKeys||'[]').some(key=>hearts.has(key));
    button.setAttribute('aria-pressed',String(selected));
    button.setAttribute('aria-label',selected?'注目の作品から外す':'注目の作品に追加');
    button.setAttribute('aria-busy',String(!!heartSync?.busy));
    button.innerHTML='<span aria-hidden="true">'+(selected?'♥':'♡')+'</span> '+(selected?'注目の作品':'注目にする');
  });
}
// Generated preview IDs change after a re-import; original submission identities do not.
const heartKey=(record,week=record.week)=>JSON.stringify([Number(week),record.student,record.file||'']);
function heartButton(record,week=record.week){
  const button=document.createElement('button');button.className='submission-heart';button.type='button';
  const keys=AdminGroups.heartKeys(record,week);button.dataset.heartKeys=JSON.stringify(keys);
  const selected=AdminGroups.isSelected(record,hearts,week);
  button.setAttribute('aria-pressed',String(selected));
  button.setAttribute('aria-label',selected?'注目の作品から外す':'注目の作品に追加');
  button.innerHTML='<span aria-hidden="true">'+(selected?'♥':'♡')+'</span> '+(selected?'注目の作品':'注目にする');
  button.onclick=()=>heartSync.setMany(AdminGroups.changesFor(record,hearts,week));
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
    if(cell.cell_type==='markdown') {const section=document.createElement('section');section.className='review-markdown';section.innerHTML=notebookMarkdownHtml(joined(cell.source));section.querySelectorAll('img[src^="attachment:"]').forEach(image=>{const name=decodeURIComponent(image.getAttribute('src').slice('attachment:'.length));const attachment=cell.attachments?.[name]||{};const entry=Object.entries(attachment).find(([type,value])=>type.startsWith('image/')&&joined(value));if(entry){const [type,value]=entry;image.src='data:'+type+';base64,'+joined(value);}});section.querySelectorAll('a').forEach(a=>{if(!['http:','https:'].includes(new URL(a.href,location.href).protocol)){a.removeAttribute('href');}a.target='_blank';a.rel='noopener noreferrer';});host.append(section);return;}
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
function notebookMarkdownHtml(source) {
  // Keep blank lines inside fenced examples instead of treating them as paragraphs.
  return source.split(/(^```[^\n]*\n[\s\S]*?^```\s*$)/gm).map(part=>{
    const fence=part.match(/^```([^\n]*)\n([\s\S]*?)\n```\s*$/);
    return fence?'<pre class="review-code"><code>'+(/^(python|py)?\s*$/.test(fence[1])?notebookCodeHtml(fence[2]):esc(fence[2]))+'</code></pre>':markdownHtml(part.replace(/^(\s*)\* /gm,'$1- '));
  }).join('');
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
function groupsForWeek(week){return reviewGroups.weeks.find(item=>item.week===week)?.groups||[];}
function memberNames(group){return group.members.map(person=>person.name).join(' / ');}
function renderSubmission(record,group){
  currentSubmission=record;currentReviewGroup=group;onHeartChange=()=>{};
  const groupID=group?.id||record.id,selection=group||record;
  adminRoot.innerHTML='<a href="?week='+record.week+'#submission-'+esc(groupID)+'">← Week '+String(record.week).padStart(2,'0')+' の一覧</a><header class="submission-heading"><p class="review-legend">WEEK '+String(record.week).padStart(2,'0')+'</p><h2>'+esc(group?.title||record.title)+'</h2><p class="group-members">'+(group?.members.length>1?'メンバー：':'作成者：')+esc(group?memberNames(group):record.student_name)+'</p>'+(group?'<p>'+group.submission_count+'件の提出</p>':'')+'</header><div class="submission-actions"></div><div class="review-mode-controls"><button data-mode="saved" aria-pressed="'+(selectedMode==='saved')+'">提出時の出力</button><button data-mode="replay" aria-pressed="'+(selectedMode==='replay')+'">ローカル再実行</button></div><nav class="review-tabs"><button data-tab="notebook" aria-pressed="'+(selectedTab==='notebook')+'">Notebook</button><button data-tab="results" aria-pressed="'+(selectedTab==='results')+'">結果</button><button data-tab="files" aria-pressed="'+(selectedTab==='files')+'">添付ファイル</button></nav><div id="submission-body"></div>';
  if(group?.variants.length>1){
    const versions=document.createElement('nav');versions.className='admin-versions';versions.setAttribute('aria-label','Submitted notebook versions');
    versions.innerHTML='<span>提出Notebook：</span>';
    group.variants.forEach(version=>{
      const link=document.createElement('a');link.href='?week='+record.week+'&id='+group.id+'&variant='+version.id;
      link.textContent=version.submitters.map(person=>person.name).join(' / ');
      if(version.id===record.id||version.source_ids.includes(record.id))link.setAttribute('aria-current','page');
      versions.append(link);
    });
    adminRoot.querySelector('.submission-heading').append(versions);
  }
  const actions=adminRoot.querySelector('.submission-actions');actions.append(heartButton(selection));
  if(group&&!group.unpublished&&record.notebook){
    const source=group.sources.find(item=>item.id===record.id);
    const link=document.createElement('a');link.className='admin-button';link.href='https://colab.research.google.com/github/yohman/26-2-Programming/blob/main/submissions/notebooks/'+source.public_id+'.ipynb';link.target='_blank';link.rel='noopener noreferrer';link.textContent='Colabで開く ↗';actions.append(link);
  }
  const body=document.getElementById('submission-body');
  if(!record.notebook){const note=document.createElement('p');note.className='review-warning';note.textContent='この提出ファイルは空か読み取れません。ほかの提出版は上から選べます。';body.append(note);}
  body.append(selectedTab==='files'?renderAttachments(record):selectedTab==='notebook'?renderNotebook(record):renderResults(record));
  const entries=groupsForWeek(record.week),navigation=()=>notebookNavigation(entries,groupID,item=>'?week='+record.week+'&id='+item.id);
  adminRoot.querySelector('.submission-heading').before(navigation());
  const footer=document.createElement('div');footer.className='submission-footer-actions';footer.append(heartButton(selection));adminRoot.append(footer,navigation());
  adminRoot.querySelectorAll('[data-mode]').forEach(button=>button.onclick=()=>{selectedMode=button.dataset.mode;renderSubmission(record,group);});
  adminRoot.querySelectorAll('[data-tab]').forEach(button=>button.onclick=()=>{selectedTab=button.dataset.tab;renderSubmission(record,group);});
}
function renderWeek(week){
  const data=reviewGroups.weeks.find(item=>item.week===week),groups=data?.groups||[];
  adminRoot.innerHTML='<div class="admin-toolbar"><h2>Week '+String(week).padStart(2,'0')+' · '+groups.length+'作品'+(data?' / '+data.submissions+'件の提出':'')+'</h2><div class="admin-filters"><input id="student-search" placeholder="メンバー・作品名で検索" aria-label="Search submissions"><button class="heart-filter" aria-pressed="false"></button></div></div><div class="submission-grid gallery-grid"></div>';
  const search=adminRoot.querySelector('input'),filter=adminRoot.querySelector('.heart-filter');let heartedOnly=false;
  const updateCount=()=>{filter.textContent='♥ のみ ('+groups.filter(group=>AdminGroups.isSelected(group,hearts)).length+')';filter.setAttribute('aria-pressed',String(heartedOnly));};
  const redraw=()=>{
    const host=adminRoot.querySelector('.submission-grid');host.replaceChildren();const query=search.value.toLowerCase();
    groups.filter(group=>(group.title+' '+group.members.map(person=>person.name+' '+person.reading).join(' ')+' '+group.sources.map(source=>source.student+' '+source.file).join(' ')).toLowerCase().includes(query)&&(!heartedOnly||AdminGroups.isSelected(group,hearts))).forEach(group=>{
      const card=document.createElement('article');card.className='submission-card group-card gallery-card';card.id='submission-'+group.id;card.append(heartButton(group));
      const link=document.createElement('a');link.className='group-preview';link.href='?week='+week+'&id='+group.id;
      const thumb=document.createElement('div');thumb.className='gallery-thumb';
      if(/^submissions\/thumbnails\/[a-f0-9]{20}\.(png|jpg)$/.test(group.thumbnail_path||'')){
        const image=document.createElement('img');image.src='../'+group.thumbnail_path;image.loading='lazy';image.alt='';thumb.append(image);
      }else thumb.innerHTML='<h3>'+esc(group.title)+'</h3><pre>'+esc(group.thumbnail_code||'')+'</pre>';
      link.append(thumb);
      const title=document.createElement('h3');title.textContent=group.title;link.append(title);
      const names=document.createElement('p');names.className='group-members';names.textContent=(group.members.length>1?'メンバー：':'作成者：')+memberNames(group);link.append(names);
      const count=document.createElement('p');count.className='gallery-group-note';count.textContent=group.submission_count+'件の提出'+(group.variants.length>1?' · Notebook '+group.variants.length+'版':'');link.append(count);
      card.append(link);host.append(card);
    });
    if(!host.children.length){const empty=document.createElement('p');empty.className='review-legend';empty.textContent=heartedOnly?'紹介候補がありません。各グループの♡で追加できます。':'一致する作品がありません。';host.append(empty);}
    updateCount();
  };
  onHeartChange=()=>{if(heartedOnly)redraw();else updateCount();};filter.onclick=()=>{heartedOnly=!heartedOnly;redraw();};search.oninput=redraw;redraw();
}
async function loadAdmin(){
  if(!localAdmin){document.querySelector('main').textContent='Local access only.';return;}
  const responses=await Promise.all([fetch('_review/index.json',{cache:'no-store'}),fetch('../submissions/gallery.json',{cache:'no-store'})]);
  if(responses.some(response=>!response.ok))throw new Error('作品グループを読み込めませんでした。再読み込みしてください。');
  const [index,gallery]=await Promise.all(responses.map(response=>response.json()));manifest=index;reviewGroups=await AdminGroups.build(manifest,gallery);
  const week=Number(params.get('week'))||manifest.weeks.at(-1)?.week||1;
  document.getElementById('admin-weeks').innerHTML='<label for="admin-week-select">課題の週</label><select id="admin-week-select">'+Array.from({length:14},(_,i)=>{const number=i+1,data=reviewGroups.weeks.find(item=>item.week===number);return '<option value="'+number+'"'+(number===week?' selected':'')+'>Week '+String(number).padStart(2,'0')+' · '+(data?data.groups.length+'作品':'未取り込み')+'</option>';}).join('')+'</select>';
  document.getElementById('admin-week-select').onchange=event=>location.href='?week='+event.target.value;
  document.getElementById('admin-status').textContent='更新：'+new Date(manifest.generated).toLocaleString('ja-JP');
  if(!params.get('id')){renderWeek(week);return;}
  const id=params.get('id');if(!/^[a-f0-9]{20}$/.test(id))throw new Error('Invalid submission ID');
  let group=groupsForWeek(week).find(item=>item.id===id||item.source_ids.includes(id));
  if(!group&&currentSubmission){group=groupsForWeek(week).find(item=>item.sources.some(source=>source.student===currentSubmission.student&&source.file===currentSubmission.file));}
  if(!group){params.delete('id');params.delete('variant');history.replaceState(null,'','?'+params);renderWeek(week);return;}
  const requested=params.get('variant')||(group.source_ids.includes(id)?id:group.primary_id);
  const chosen=group.sources.find(source=>source.id===requested)||group.sources.find(source=>source.id===group.primary_id);
  const response=await fetch('_review/'+chosen.id+'/submission.json',{cache:'no-store'});if(!response.ok)throw new Error('Submission not found');
  renderSubmission(await response.json(),group);
}
document.addEventListener('DOMContentLoaded',()=>{
  if(!adminRoot)return;
  (async()=>{
    const response=await fetch('/__admin/hearts',{cache:'no-store'});
    if(!response.ok)throw new Error('Adminサーバーを更新してください。');
    const state=await response.json();
    let pending={};try{pending=JSON.parse(localStorage.getItem(heartPendingKey)||'{}');}catch{}
    heartSync=HeartSync.create({initial:state.hearts??[...hearts],pending,
      send:async changes=>{
        const response=await fetch('/__admin/hearts',{method:'POST',keepalive:true,headers:{'Content-Type':'application/json','X-Admin-Request':'hearts'},body:JSON.stringify({changes})});
        if(!response.ok)throw new Error('Heart save failed');
        return response.json();
      },
      persist:(values,changes)=>{try{localStorage.setItem(heartsStorageKey,JSON.stringify(values));localStorage.setItem(heartPendingKey,JSON.stringify(changes));}catch{}},
      onChange:values=>{hearts=values;updateHeartButtons();onHeartChange();},onStatus:heartStatus
    });
    heartPublication=state.sync||{state:'idle'};
    await loadAdmin();
    async function pollHearts(){
      try{
        const response=await fetch('/__admin/hearts',{cache:'no-store'});
        if(response.ok){const state=await response.json();heartSync.accept(state.hearts||[]);heartPublication=state.sync;if(!heartSync.busy)heartStatus({sync:state.sync});}
      }catch{}finally{setTimeout(pollHearts,heartPublication?.state==='idle'?5000:1000);}
    }
    if(heartPublication.state!=='idle')heartStatus({sync:heartPublication});
    setTimeout(pollHearts,1000);
    window.addEventListener('pagehide',()=>heartSync.flush());
  })().catch(error=>document.getElementById('admin-status').textContent=error.message);
  document.getElementById('refresh').onclick=async event=>{const button=event.currentTarget;button.disabled=true;document.getElementById('admin-status').textContent='新しいファイルを取り込み中…';try{const response=await fetch('/__admin/refresh',{method:'POST',headers:{'X-Admin-Request':'refresh'}});if(!response.ok)throw new Error('ローカルAdminサーバー（8766）で開いてください。');await loadAdmin();}catch(error){document.getElementById('admin-status').textContent=error.message;}finally{button.disabled=false;}};
});
