/* The public feed contains only explicitly selected, exported notebook content. */
let galleryVersion='',galleryRecords=[];
const galleryHost=document.getElementById('gallery-content');
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
  const id=new URLSearchParams(location.search).get('id');
  const record=galleryRecords.find(s=>s.id===id);
  galleryHost.replaceChildren();
  document.getElementById('gallery-heading').hidden=!!record;
  document.getElementById('gallery-back').hidden=!record;
  if(record){
    const heading=document.createElement('header');heading.className='gallery-notebook-title';
    heading.innerHTML='<p class="eyebrow">WEEK '+String(record.week).padStart(2,'0')+'</p><h1>'+esc(record.title)+'</h1><p>'+esc(record.student_name)+' · '+esc(record.student_reading)+'</p>';
    galleryHost.append(heading,renderNotebook(record));document.title=record.title+' · Student work';return;
  }
  if(id){history.replaceState(null,'','gallery.html');document.getElementById('gallery-status').textContent='この作品は現在公開されていません。';}
  if(!galleryRecords.length){galleryHost.innerHTML='<p><span class="lang-ja">公開された作品はまだありません。</span><span class="lang-en">No projects published yet.</span></p>';return;}
  [...new Set(galleryRecords.map(s=>s.week))].sort((a,b)=>b-a).forEach(week=>{
    const title=document.createElement('h2');title.className='gallery-week';title.textContent='WEEK '+String(week).padStart(2,'0');
    const grid=document.createElement('div');grid.className='gallery-grid';
    galleryRecords.filter(s=>s.week===week).forEach(record=>{
      const card=document.createElement('a');card.className='gallery-card';card.href='gallery.html?id='+record.id;
      card.innerHTML='<div class="gallery-thumb" aria-hidden="true"></div><h2>'+esc(record.title)+'</h2><p>'+esc(record.student_name)+' · '+esc(record.student_reading)+'</p>';
      const frame=document.createElement('iframe');frame.sandbox='';frame.loading='lazy';frame.tabIndex=-1;frame.title=record.title;
      frame.srcdoc='<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src data: https:; base-uri \'none\'; form-action \'none\'"><style>body{font-family:sans-serif;padding:16px;color:#24323e}pre{font-size:15px}</style>'+thumbnail(record);
      card.querySelector('.gallery-thumb').append(frame);grid.append(card);
    });galleryHost.append(title,grid);
  });
}
async function updateGallery() {
  try {
    const response=await fetch('submissions/gallery.json?t='+Date.now(),{cache:'no-store'});
    if(!response.ok)throw new Error('Gallery unavailable');
    const data=await response.json();
    if(data.updated!==galleryVersion){galleryVersion=data.updated;galleryRecords=data.submissions;renderGallery();}
  } catch(error){if(!galleryVersion)document.getElementById('gallery-status').textContent='作品を読み込めませんでした。しばらくしてから再度お試しください。';}
}
updateGallery();
setInterval(()=>{if(!document.hidden)updateGallery();},10000);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)updateGallery();});
