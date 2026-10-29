/* Every exported submission is visible; hearted projects are featured first. */
let galleryVersion='',galleryRecords=[],galleryTag='';
let galleryWeeks=[];
const galleryHost=document.getElementById('gallery-content');
const weekPicker=document.getElementById('gallery-week-select');
function assignmentTitle(week,language) {
  const meta=galleryWeeks.find(w=>w.week===Number(week));
  return (language==='ja'?meta?.gallery_title_ja||meta?.title_ja:meta?.gallery_title||meta?.title)||'Week '+String(week).padStart(2,'0');
}
function weekEntries(week) {
  return galleryRecords.filter(record=>record.week===week).sort((a,b)=>Number(!!b.featured)-Number(!!a.featured));
}
const featuredBadge='<span class="gallery-featured-label"><span aria-hidden="true">♥</span> <span class="lang-ja">注目の作品</span><span class="lang-en">Featured</span></span>';
function downloadableNotebook(record) {
  return {
    nbformat:4,nbformat_minor:4,
    metadata:{kernelspec:{display_name:'Python 3',language:'python',name:'python3'},language_info:{name:'python'}},
    cells:record.notebook.cells.map(cell=>{
      const copy={...cell,metadata:{},source:cell.source||''};
      if(cell.cell_type==='code'){
        copy.execution_count=cell.execution_count??null;
        copy.outputs=cell.outputs||[];
      }
      return copy;
    })
  };
}
function notebookDownload(record) {
  const actions=document.createElement('div');actions.className='gallery-download-actions';
  if(record.has_notebook===false){
    actions.innerHTML='<p><span class="lang-ja">Notebookファイルは提出されていません。ダウンロードはありません。</span><span class="lang-en">No notebook file was submitted; no download is available.</span></p>';
    return actions;
  }
  const button=document.createElement('button');button.type='button';button.className='gallery-download';
  button.innerHTML='<span class="lang-ja">↓ Notebookをダウンロード (.ipynb)</span><span class="lang-en">↓ Download notebook (.ipynb)</span>';
  button.onclick=()=>{
    // Download only the already-public, sanitized code and saved outputs.
    const blob=new Blob([JSON.stringify(downloadableNotebook(record),null,2)],{type:'application/x-ipynb+json'});
    const url=URL.createObjectURL(blob),link=document.createElement('a');
    link.href=url;link.download='week-'+String(record.week).padStart(2,'0')+'-'+record.id+'.ipynb';
    document.body.append(link);link.click();link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  };
  actions.append(button);return actions;
}
function fillWeekPicker(selected) {
  const weeks=[...new Set([...galleryWeeks.map(w=>w.week),...galleryRecords.map(s=>s.week)])].sort((a,b)=>a-b);
  const language=document.documentElement.dataset.language||'ja';
  weekPicker.replaceChildren(...weeks.map(week=>{
    const option=document.createElement('option');option.value=week;
    const count=galleryRecords.filter(s=>s.week===week).length;
    option.textContent='Week '+String(week).padStart(2,'0')+' · '+assignmentTitle(week,language)+' ('+count+')';
    option.selected=week===selected;return option;
  }));
}
function thumbnail(record) {
  const widget=record.replay.cells.flatMap(c=>c.outputs).find(o=>o.data?.['text/html']);
  const outputs=record.notebook.cells.flatMap(c=>c.outputs||[]);
  const visual=widget||outputs.find(o=>o.data?.['image/png']||o.data?.['text/html']);
  if(visual?.data?.['text/html'])return joined(visual.data['text/html']);
  if(visual?.data?.['image/png'])return '<img style="max-width:100%" src="data:image/png;base64,'+joined(visual.data['image/png'])+'">';
  const first=record.notebook.cells.find(c=>c.cell_type==='code');
  return '<h2>'+esc(record.title)+'</h2><pre style="white-space:pre-wrap">'+esc(joined(first?.source).split('\n').slice(0,10).join('\n'))+'</pre>';
}
function renderGallery() {
  const query=new URLSearchParams(location.search),id=query.get('id');
  const record=galleryRecords.find(s=>s.id===id);
  const requested=Number(query.get('week'));
  const week=record?.week||(requested>=1&&requested<=14?requested:Math.max(1,...galleryRecords.map(s=>s.week)));
  fillWeekPicker(week);
  galleryHost.replaceChildren();
  document.getElementById('gallery-heading').hidden=!!record;
  document.getElementById('gallery-back').hidden=!record;
  document.getElementById('gallery-back').href='gallery.html?week='+week;
  if(record){
    const heading=document.createElement('header');heading.className='gallery-notebook-title';
    heading.innerHTML='<p class="eyebrow">WEEK '+String(record.week).padStart(2,'0')+'</p><p><span class="lang-ja">'+esc(assignmentTitle(week,'ja'))+'</span><span class="lang-en">'+esc(assignmentTitle(week,'en'))+'</span></p><h1>'+esc(record.title)+'</h1><p>'+esc(record.student_name)+' · '+esc(record.student_reading)+'</p>';
    if(record.featured)heading.insertAdjacentHTML('afterbegin',featuredBadge);
    const navigation=()=>notebookNavigation(weekEntries(week),record.id,item=>'gallery.html?week='+week+'&id='+item.id);
    galleryHost.append(navigation(),heading,notebookDownload(record),renderNotebook(record),notebookDownload(record),navigation());document.title=record.title+' · Student work';return;
  }
  if(id){history.replaceState(null,'','gallery.html?week='+week);document.getElementById('gallery-status').textContent='この作品は現在公開されていません。';}
  const entries=weekEntries(week);
  {
    const title=document.createElement('header');title.className='gallery-assignment';title.innerHTML='<p class="eyebrow">WEEK '+String(week).padStart(2,'0')+'</p><h2><span class="lang-ja">'+esc(assignmentTitle(week,'ja'))+'</span><span class="lang-en">'+esc(assignmentTitle(week,'en'))+'</span></h2><p><span class="lang-ja">公開作品 '+entries.length+'件</span><span class="lang-en">'+entries.length+' published projects</span></p>';
    const grid=document.createElement('div');grid.className='gallery-grid';
    entries.forEach(record=>{
      const card=document.createElement('a');card.className='gallery-card'+(record.featured?' gallery-card--featured':'');card.href='gallery.html?week='+week+'&id='+record.id;
      card.innerHTML='<div class="gallery-thumb" aria-hidden="true"></div><h2>'+esc(record.title)+'</h2><p>'+esc(record.student_name)+' · '+esc(record.student_reading)+'</p>';
      if(record.featured)card.insertAdjacentHTML('afterbegin',featuredBadge);
      const frame=document.createElement('iframe');frame.sandbox='';frame.loading='lazy';frame.tabIndex=-1;frame.title=record.title;
      frame.srcdoc='<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src data: https:; base-uri \'none\'; form-action \'none\'"><style>body{font-family:sans-serif;padding:16px;color:#24323e}pre{font-size:15px}</style>'+thumbnail(record);
      card.querySelector('.gallery-thumb').append(frame);grid.append(card);
    });galleryHost.append(title,grid);
    if(!entries.length){const empty=document.createElement('p');empty.innerHTML='<span class="lang-ja">この週の公開作品はまだありません。</span><span class="lang-en">No projects have been published for this week yet.</span>';galleryHost.append(empty);}
  }
}
async function updateGallery() {
  try {
    const url='submissions/gallery.json?t='+Date.now();
    // Recheck small headers, not multi-megabyte notebook images, every ten seconds.
    if(galleryTag){const probe=await fetch(url,{method:'HEAD',cache:'no-store'});if(probe.ok&&(probe.headers.get('etag')||probe.headers.get('last-modified'))===galleryTag)return;}
    const response=await fetch(url,{cache:'no-store'});
    if(!response.ok)throw new Error('Gallery unavailable');
    const data=await response.json();
    galleryTag=response.headers.get('etag')||response.headers.get('last-modified')||'';
    if(data.updated!==galleryVersion){galleryVersion=data.updated;galleryRecords=data.submissions;renderGallery();}
  } catch(error){if(!galleryVersion)document.getElementById('gallery-status').textContent='作品を読み込めませんでした。しばらくしてから再度お試しください。';}
}
updateGallery();
loadWeeks().then(weeks=>{galleryWeeks=weeks;if(galleryVersion)renderGallery();}).catch(()=>{});
weekPicker.onchange=()=>{history.pushState(null,'','gallery.html?week='+weekPicker.value);document.getElementById('gallery-status').textContent='';renderGallery();};
window.addEventListener('popstate',renderGallery);
new MutationObserver(()=>fillWeekPicker(Number(weekPicker.value)||1)).observe(document.documentElement,{attributes:true,attributeFilter:['data-language']});
setInterval(()=>{if(!document.hidden)updateGallery();},10000);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)updateGallery();});
