/* Every exported submission is visible; hearted projects are featured first. */
let galleryVersion='',galleryRecords=[],galleryTag='';
let galleryWeeks=[];
let galleryRender=0;
const notebookLoads=new Map();
let featuredIDs=null,featuredVersion='';
function applyFeatured(){if(featuredIDs!==null)galleryRecords.forEach(record=>{record.featured=(record.submission_ids||[record.id]).some(id=>featuredIDs.has(id));});}
async function updateFeatured(){
  try{
    const response=await fetch('submissions/featured.json?t='+Date.now(),{cache:'no-store'});
    if(!response.ok)return;
    const data=await response.json();
    if(!Array.isArray(data.ids)||data.ids.some(id=>typeof id!=='string'||! /^[a-f0-9]{20}$/.test(id)))return;
    const version=JSON.stringify([...data.ids].sort());
    if(featuredVersion!==version){featuredVersion=version;featuredIDs=new Set(data.ids);applyFeatured();if(galleryVersion)renderGallery();}
  }catch{}
}
const galleryHost=document.getElementById('gallery-content');
const weekPicker=document.getElementById('gallery-week-select');
function assignmentTitle(week,language) {
  const meta=galleryWeeks.find(w=>w.week===Number(week));
  return (language==='ja'?meta?.gallery_title_ja||meta?.title_ja:meta?.gallery_title||meta?.title)||'Week '+String(week).padStart(2,'0');
}
function weekEntries(week) {
  return galleryRecords.filter(record=>record.week===week).sort((a,b)=>Number(!!b.featured)-Number(!!a.featured));
}
function submitterLabel(record) {
  const people=record.members||record.submitters||[{name:record.student_name,reading:record.student_reading}];
  return people.map(person=>person.name+(people.length===1&&person.reading?' · '+person.reading:'')).join(' / ');
}
function credits(record) {
  const count=(record.members||record.submitters||[]).length;
  return '<span class="lang-ja">'+(count>1?'メンバー：':'作成者：')+'</span><span class="lang-en">'+(count>1?'Members: ':'Author: ')+'</span>'+esc(submitterLabel(record));
}
function groupLabel(record) {
  return record.submission_count>1?'<p class="gallery-group-note"><span class="lang-ja">提出 '+record.submission_count+'件をグループで表示</span><span class="lang-en">'+record.submission_count+' submissions, one group</span></p>':'';
}
function versionLinks(record,chosen) {
  if((record.variants||[]).length<2)return null;
  const nav=document.createElement('nav');nav.className='gallery-versions';nav.setAttribute('aria-label','Submitted notebook versions');
  const label=document.createElement('span');label.innerHTML='<span class="lang-ja">提出Notebook：</span><span class="lang-en">Submitted notebooks: </span>';nav.append(label);
  record.variants.forEach(version=>{
    const link=document.createElement('a');link.href='gallery.html?week='+record.week+'&id='+record.id+'&variant='+version.id;
    link.textContent=version.submitters.map(person=>person.name).join(' / ');
    if(version.notebook_path===chosen.notebook_path)link.setAttribute('aria-current','page');
    nav.append(link);
  });
  return nav;
}
function colabURL(record) {
  return /^submissions\/notebooks\/[a-f0-9]{20}\.ipynb$/.test(record.notebook_path||'')
    ? 'https://colab.research.google.com/github/yohman/26-2-Programming/blob/main/'+record.notebook_path : null;
}
const featuredBadge='<span class="gallery-featured-label"><span aria-hidden="true">♥</span> <span class="lang-ja">注目の作品</span><span class="lang-en">Featured</span></span>';
async function loadNotebook(record) {
  if(record.notebook?.cells || record.has_notebook===false)return;
  const cacheKey=record.notebook_path||record.id;
  if(!notebookLoads.has(cacheKey))notebookLoads.set(cacheKey,(async()=>{
    const requests=[fetch(record.notebook_path,{cache:'no-store'})];
    if(record.replay_path)requests.push(fetch(record.replay_path,{cache:'no-store'}));
    const responses=await Promise.all(requests);
    if(responses.some(response=>!response.ok))throw new Error('Notebook unavailable');
    const data=await Promise.all(responses.map(response=>response.json()));
    return {notebook:data[0],replay:data[1]||{cells:[]}};
  })().catch(error=>{notebookLoads.delete(cacheKey);throw error;}));
  Object.assign(record,await notebookLoads.get(cacheKey));
}
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
  button.onclick=async()=>{
    await loadNotebook(record);
    // Download only the already-public, sanitized code and saved outputs.
    const blob=new Blob([JSON.stringify(downloadableNotebook(record),null,2)],{type:'application/x-ipynb+json'});
    const url=URL.createObjectURL(blob),link=document.createElement('a');
    link.href=url;link.download='week-'+String(record.week).padStart(2,'0')+'-'+record.id+'.ipynb';
    document.body.append(link);link.click();link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  };
  actions.append(button);
  const colab=colabURL(record);
  if(colab){
    const link=document.createElement('a');link.className='gallery-colab';link.href=colab;link.target='_blank';link.rel='noopener noreferrer';
    link.innerHTML='<span class="lang-ja">Colabで開く ↗</span><span class="lang-en">Open in Colab ↗</span>';
    actions.append(link);
  }
  return actions;
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
  const source=record.thumbnail_code||joined(record.notebook?.cells.find(cell=>cell.cell_type==='code')?.source);
  return '<h2>'+esc(record.title)+'</h2><pre style="white-space:pre-wrap">'+esc(source.split('\n').slice(0,10).join('\n'))+'</pre>';
}
async function renderGallery() {
  const render=++galleryRender;
  const query=new URLSearchParams(location.search),id=query.get('id');
  const record=galleryRecords.find(s=>s.id===id||s.submission_ids?.includes(id));
  const requested=Number(query.get('week'));
  const week=record?.week||(requested>=1&&requested<=14?requested:Math.max(1,...galleryRecords.map(s=>s.week)));
  fillWeekPicker(week);
  galleryHost.replaceChildren();
  document.getElementById('gallery-heading').hidden=!!record;
  document.getElementById('gallery-back').hidden=!record;
  document.getElementById('gallery-back').href='gallery.html?week='+week;
  if(record){
    const variantID=query.get('variant')||(id!==record.id?id:null);
    const variant=record.variants?.find(version=>version.id===variantID);
    const view=variant?{...record,...variant,notebook:undefined,replay:undefined}:record;
    const heading=document.createElement('header');heading.className='gallery-notebook-title';
    heading.innerHTML='<p class="eyebrow">WEEK '+String(record.week).padStart(2,'0')+'</p><p><span class="lang-ja">'+esc(assignmentTitle(week,'ja'))+'</span><span class="lang-en">'+esc(assignmentTitle(week,'en'))+'</span></p><h1>'+esc(record.title)+'</h1><p>'+credits(record)+'</p>';
    heading.insertAdjacentHTML('beforeend',groupLabel(record));
    const versions=versionLinks(record,view);if(versions)heading.append(versions);
    if(record.featured)heading.insertAdjacentHTML('afterbegin',featuredBadge);
    const navigation=()=>notebookNavigation(weekEntries(week),record.id,item=>'gallery.html?week='+week+'&id='+item.id);
    const loading=document.createElement('p');loading.setAttribute('role','status');
    loading.innerHTML='<span class="lang-ja">Notebookを読み込み中…</span><span class="lang-en">Loading notebook…</span>';
    galleryHost.append(navigation(),heading,notebookDownload(view),loading);document.title=record.title+' · Student work';
    try{
      await loadNotebook(view);
      if(render!==galleryRender)return;
      view.replay ||= {cells:[]};view.attachments ||= [];
      if(!view.notebook)view.notebook={cells:[{cell_type:'markdown',source:'Notebookのプレビューはありません。 / No notebook preview available.'}]};
      loading.replaceWith(renderNotebook(view));galleryHost.append(notebookDownload(view),navigation());
    }catch{
      if(render!==galleryRender)return;
      loading.innerHTML='<span class="lang-ja">Notebookを読み込めませんでした。ページを再読み込みしてください。</span><span class="lang-en">Unable to load the notebook. Please reload this page.</span>';
    }
    return;
  }
  if(id){history.replaceState(null,'','gallery.html?week='+week);document.getElementById('gallery-status').textContent='この作品は現在公開されていません。';}
  const entries=weekEntries(week);
  const submitted=entries.reduce((count,entry)=>count+(entry.submission_count||1),0);
  {
    const title=document.createElement('header');title.className='gallery-assignment';title.innerHTML='<p class="eyebrow">WEEK '+String(week).padStart(2,'0')+'</p><h2><span class="lang-ja">'+esc(assignmentTitle(week,'ja'))+'</span><span class="lang-en">'+esc(assignmentTitle(week,'en'))+'</span></h2><p><span class="lang-ja">公開作品 '+entries.length+'件'+(submitted>entries.length?'（提出 '+submitted+'件）':'')+'</span><span class="lang-en">'+entries.length+' published projects'+(submitted>entries.length?' from '+submitted+' submissions':'')+'</span></p>';
    const grid=document.createElement('div');grid.className='gallery-grid';
    entries.forEach(record=>{
      const card=document.createElement('a');card.className='gallery-card'+(record.featured?' gallery-card--featured':'');card.href='gallery.html?week='+week+'&id='+record.id;
      card.innerHTML='<div class="gallery-thumb" aria-hidden="true"></div><h2>'+esc(record.title)+'</h2><p>'+credits(record)+'</p>';
      card.insertAdjacentHTML('beforeend',groupLabel(record));
      if(record.featured)card.insertAdjacentHTML('afterbegin',featuredBadge);
      const thumb=card.querySelector('.gallery-thumb');
      if(/^submissions\/thumbnails\/[a-f0-9]{20}\.(png|jpg)$/.test(record.thumbnail_path||'')){
        const image=document.createElement('img');image.src=record.thumbnail_path;image.loading='lazy';image.alt='';thumb.append(image);
      }else{
        // Both title and code are escaped; no student HTML executes here.
        thumb.innerHTML=thumbnail(record);
      }
      grid.append(card);
    });galleryHost.append(title,grid);
    if(!entries.length){const empty=document.createElement('p');empty.innerHTML='<span class="lang-ja">この週の公開作品はまだありません。</span><span class="lang-en">No projects have been published for this week yet.</span>';galleryHost.append(empty);}
  }
}
async function updateGallery() {
  updateFeatured();
  try {
    const url='submissions/gallery.json?t='+Date.now();
    // Recheck small headers, not multi-megabyte notebook images, every ten seconds.
    if(galleryTag){const probe=await fetch(url,{method:'HEAD',cache:'no-store'});if(probe.ok&&(probe.headers.get('etag')||probe.headers.get('last-modified'))===galleryTag)return;}
    const response=await fetch(url,{cache:'no-store'});
    if(!response.ok)throw new Error('Gallery unavailable');
    const data=await response.json();
    galleryTag=response.headers.get('etag')||response.headers.get('last-modified')||'';
    if(data.updated!==galleryVersion){galleryVersion=data.updated;notebookLoads.clear();galleryRecords=data.submissions;applyFeatured();renderGallery();}
  } catch(error){if(!galleryVersion)document.getElementById('gallery-status').textContent='作品を読み込めませんでした。しばらくしてから再度お試しください。';}
}
updateGallery();
loadWeeks().then(weeks=>{galleryWeeks=weeks;if(galleryVersion)renderGallery();}).catch(()=>{});
weekPicker.onchange=()=>{history.pushState(null,'','gallery.html?week='+weekPicker.value);document.getElementById('gallery-status').textContent='';renderGallery();};
window.addEventListener('popstate',renderGallery);
new MutationObserver(()=>fillWeekPicker(Number(weekPicker.value)||1)).observe(document.documentElement,{attributes:true,attributeFilter:['data-language']});
setInterval(()=>{if(!document.hidden)updateGallery();},10000);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)updateGallery();});
