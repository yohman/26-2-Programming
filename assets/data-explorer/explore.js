/* Read-only API explorer. No keys, proxies, or background polling. */
const byId = id => document.getElementById(id);
const locale = () => document.documentElement.dataset.language === 'en' ? 'en' : 'ja';
const textFor = value => typeof value === 'string' ? value : value?.[locale()] || '';
const state = { config:null, week:null, id:null, dataset:null, raw:'', data:null, url:'', mode:'pretty', source:null, token:0, blob:null, geoBlob:null, map:null, geojson:null };
const cache = new Map();
let controller;
let mapLibrary;
let gtfsType;
const defaults = {
  toeiBus:{},
  toei:{line:'Oedo'},
  weather:{latitude:'35.68',longitude:'139.69',forecast_days:'1'},
  earthquakes:{magnitude:'2.5',period:'day'},
  pokemon:{name:'pikachu'},
  transit:{route:'1',limit:'20'},
  tokyo:{},
  lapd:{area:'all',limit:'50'},
  holidays:{year:'2026'}
};
const fields = {
  toeiBus:[],
  toei:[{key:'line',label:{ja:'路線 · odpt:railway',en:'Line · odpt:railway'},options:[['Oedo','大江戸線 · Oedo'],['Asakusa','浅草線 · Asakusa'],['Mita','三田線 · Mita'],['Shinjuku','新宿線 · Shinjuku'],['Arakawa','東京さくらトラム · Arakawa'],['all','全路線 · All lines']]}],
  tokyo:[],
  lapd:[
    {key:'area',label:{ja:'地区 · $where',en:'Area · $where'},options:[['all','All areas'],['Central','Central'],['Hollywood','Hollywood'],['Pacific','Pacific'],['Harbor','Harbor']]},
    {key:'limit',label:{ja:'$limit · 最大件数',en:'$limit · Maximum rows'},options:[['25','25'],['50','50'],['100','100']]}
  ],
  weather:[
    {key:'latitude',label:{ja:'latitude · 緯度',en:'latitude'},type:'number',min:-90,max:90,step:'any'},
    {key:'longitude',label:{ja:'longitude · 経度',en:'longitude'},type:'number',min:-180,max:180,step:'any'},
    {key:'forecast_days',label:{ja:'forecast_days · 日数',en:'forecast_days'},options:[['1','1'],['2','2'],['3','3']]}
  ],
  earthquakes:[
    {key:'magnitude',label:{ja:'最小マグニチュード',en:'Minimum magnitude'},options:[['2.5','M2.5+'],['4.5','M4.5+']]},
    {key:'period',label:{ja:'期間',en:'Window'},options:[['hour','1 hour'],['day','24 hours'],['week','7 days']]}
  ],
  pokemon:[{key:'name',label:{ja:'フォーム名',en:'Form name'},options:[['pikachu','pikachu'],['bulbasaur','bulbasaur'],['charmander','charmander']]}],
  transit:[
    {key:'route',label:{ja:'filter[route] · 路線',en:'filter[route]'},options:[['1','1 · Bus'],['Red','Red · Subway'],['Orange','Orange · Subway']]},
    {key:'limit',label:{ja:'page[limit] · 最大件数',en:'page[limit]'},options:[['5','5'],['10','10'],['20','20']]}
  ],
  holidays:[{key:'year',label:{ja:'表示年 · ブラウザー内の絞り込み',en:'Display year · browser filter'},type:'number',min:1955,max:2027,step:'1'}]
};

function values() { return Object.fromEntries([...byId('parameter-fields').querySelectorAll('[name]')].map(field => [field.name,field.value])); }
function requestURL(id, v) {
  if(id==='toeiBus') return 'https://api-public.odpt.org/api/v4/gtfs/realtime/ToeiBus';
  if(id==='toei') {
    const url=new URL('https://api-public.odpt.org/api/v4/odpt:Train');
    url.searchParams.set('odpt:operator','odpt.Operator:Toei');
    if(v.line!=='all')url.searchParams.set('odpt:railway','odpt.Railway:Toei.'+v.line);
    return url.href;
  }
  if(id==='tokyo') return 'https://api.odpt.org/api/v4/odpt:Train?odpt:operator=odpt.Operator:TokyoMetro&odpt:railway=odpt.Railway:TokyoMetro.Yurakucho&acl:consumerKey=YOUR_API_KEY';
  if(id==='lapd') {
    const url=new URL('https://data.lacity.org/resource/k7nn-b2ep.json');
    url.searchParams.set('$select','date_occ,area_name,nibr_description,hndrdth_lat,hndrdth_lon');
    url.searchParams.set('$where','hndrdth_lat > 0 AND hndrdth_lon < 0'+(v.area==='all'?'':" AND trim(area_name) = '"+v.area+"'"));
    url.searchParams.set('$order','date_occ DESC'); url.searchParams.set('$limit',v.limit); return url.href;
  }
  if (id === 'weather') {
    const url = new URL('https://api.open-meteo.com/v1/forecast');
    Object.entries({latitude:v.latitude,longitude:v.longitude,current:'temperature_2m',hourly:'temperature_2m',forecast_days:v.forecast_days,timezone:'Asia/Tokyo'}).forEach(([k,value]) => url.searchParams.set(k,value));
    return url.href;
  }
  if (id === 'earthquakes') return 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/' + v.magnitude + '_' + v.period + '.geojson';
  if (id === 'pokemon') return 'https://pokeapi.co/api/v2/pokemon-form/' + v.name;
  if (id === 'transit') {
    const url = new URL('https://api-v3.mbta.com/vehicles');
    url.searchParams.set('filter[route]',v.route); url.searchParams.set('page[limit]',v.limit);
    return url.href;
  }
  return 'https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv';
}
function updateRequest() {
  const url = requestURL(state.id,values());
  byId('request-url').textContent = url;
  byId('raw-link').href = state.dataset.documentation_example ? state.dataset.snapshot : url;
  if (state.id === 'holidays' && state.data) renderViews();
  if (state.data && state.url !== url) status({ja:'新しい条件は未取得です。「取得する」を押してください。下は前の応答です。',en:'New parameters have not been fetched. Press Fetch data. The view below is the previous response.'},'pending');
}
function renderFields(v = defaults[state.id]) {
  byId('parameter-fields').replaceChildren();
  fields[state.id].forEach(field => {
    const label = document.createElement('label');
    const caption = document.createElement('span'); caption.textContent = textFor(field.label); label.append(caption);
    const input = document.createElement(field.options ? 'select' : 'input');
    input.name = field.key;
    if (field.options) field.options.forEach(([value,title]) => { const option=document.createElement('option'); option.value=value; option.textContent=title; input.append(option); });
    else { input.type=field.type; input.min=field.min; input.max=field.max; input.step=field.step; input.required=true; }
    input.value = v[field.key];
    input.addEventListener('input',updateRequest);
    label.append(input); byId('parameter-fields').append(label);
  });
  updateRequest();
}
function status(message,kind='live') { byId('data-status').textContent = textFor(message); byId('data-status').dataset.kind=kind; }
function renderStatus() {
  if (!state.source) return;
  const time=state.source.at;
  if (state.source.saved) {
    if(state.dataset.documentation_example) {
      status({ja:'公式仕様書の応答例 · '+state.dataset.snapshot_at+' · ライブデータではありません。',en:'Official documentation response example · dated 2017-11-28 · not live.'},'snapshot');
      return;
    }
    status({ja:'保存例 · '+state.dataset.snapshot_at+'取得 · 自動更新ではありません。初期条件のデータを表示中。',en:'Saved example · retrieved '+state.dataset.snapshot_at+' · not live. Showing the default request.'},'snapshot');
    if (state.dataset.snapshot_source) {
      const source=document.createElement('a'); source.href=state.dataset.snapshot_source; source.target='_blank'; source.rel='noopener'; source.textContent=textFor({ja:' 配信元リポジトリの保存データ ↗',en:' Provider repository snapshot ↗'}); byId('data-status').append(source);
    }
  }
  else status({ja:'API応答取得：'+time+' · '+state.dataset.format+' · '+state.source.bytes.toLocaleString()+' bytes · 自動更新なし',en:'Response fetched: '+time+' · '+state.dataset.format+' · '+state.source.bytes.toLocaleString()+' bytes · no automatic refresh'});
  if(state.id==='toeiBus' && state.data.header?.timestamp) {
    const at=new Date(state.data.header.timestamp*1000).toLocaleString('ja-JP',{timeZone:'Asia/Tokyo'})+' JST';
    byId('data-status').append(document.createTextNode(textFor({ja:' · フィード時刻：'+at,en:' · Feed timestamp: '+at})));
  }
}
function parseCSV(source) {
  const rows=[]; let row=[],field='',quoted=false;
  for (let i=0;i<source.length;i++) {
    const char=source[i];
    if (char === '"') {
      if (quoted && source[i+1] === '"') { field+='"'; i++; } else quoted=!quoted;
    } else if (char === ',' && !quoted) { row.push(field); field=''; }
    else if ((char === '\n' || char === '\r') && !quoted) {
      if (char === '\r' && source[i+1] === '\n') i++;
      row.push(field); if(row.some(value=>value.length)) rows.push(row); row=[]; field='';
    } else field+=char;
  }
  if(field.length || row.length) { row.push(field); rows.push(row); }
  return rows;
}
function jsonColors(value) {
  const code=byId('pretty-output').querySelector('code'); code.replaceChildren();
  if (!byId('syntax-color').checked) { code.textContent=value; return; }
  const pattern=/("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false|null)\b|-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b/g;
  let position=0;
  for(const match of value.matchAll(pattern)) {
    code.append(document.createTextNode(value.slice(position,match.index)));
    const token=document.createElement('span');
    token.className=match[2]?'json-key':match[1]?'json-string':match[3]?'json-literal':'json-number';
    token.textContent=match[0]; code.append(token); position=match.index+match[0].length;
  }
  code.append(document.createTextNode(value.slice(position)));
}
function csvTable() {
  const [headers,...rows]=state.data; const table=document.createElement('table');
  const thead=document.createElement('thead'); const head=document.createElement('tr');
  (headers||[]).forEach(value=>{const th=document.createElement('th'); th.scope='col'; th.textContent=value; head.append(th);});
  thead.append(head); table.append(thead);
  const body=document.createElement('tbody'); const year=values().year;
  rows.filter(row=>!year || row[0].split('/')[0]===year).forEach(row=>{
    const tr=document.createElement('tr');
    row.forEach(value=>{const td=document.createElement('td'); td.textContent=value; tr.append(td);}); body.append(tr);
  });
  table.append(body); byId('csv-output').replaceChildren(table);
}
function features() {
  const valid=(lon,lat)=> typeof lon==='number' && typeof lat==='number' && Number.isFinite(lon) && Number.isFinite(lat) && Math.abs(lon)<=180 && Math.abs(lat)<=90;
  const point=(lon,lat,title,detail,mag=0)=>({type:'Feature',geometry:{type:'Point',coordinates:[lon,lat]},properties:{title:String(title||''),detail:String(detail||''),radius:Math.max(5,Math.min(14,Number(mag)||5))}});
  let result=[];
  if(state.id==='earthquakes') result=(state.data.features||[]).filter(f=>f.geometry?.type==='Point' && valid(...f.geometry.coordinates)).map(f=>point(...f.geometry.coordinates.slice(0,2),f.properties?.place,'M '+f.properties?.mag+' · '+new Date(f.properties?.time).toISOString(),f.properties?.mag));
  if(state.id==='weather' && valid(state.data.longitude,state.data.latitude)) result=[point(state.data.longitude,state.data.latitude,'Forecast location',state.data.current?.time+' · '+state.data.current?.temperature_2m+' °C')];
  if(state.id==='transit') result=(state.data.data||[]).filter(v=>valid(v.attributes?.longitude,v.attributes?.latitude)).map(v=>point(v.attributes.longitude,v.attributes.latitude,'Vehicle '+(v.attributes.label||v.id),'Route '+(v.relationships?.route?.data?.id||'')+' · '+v.attributes.updated_at));
  if(state.id==='toeiBus') result=(state.data.entity||[]).filter(e=>valid(e.vehicle?.position?.longitude,e.vehicle?.position?.latitude)).map(e=>{
    const v=e.vehicle,p=v.position;
    const stamp=v.timestamp||state.data.header?.timestamp;
    return point(p.longitude,p.latitude,'Bus '+(v.vehicle?.label||v.vehicle?.id||e.id),'Route '+(v.trip?.route_id||'—')+' · '+p.latitude.toFixed(5)+', '+p.longitude.toFixed(5)+' · '+(stamp?new Date(stamp*1000).toLocaleString('ja-JP',{timeZone:'Asia/Tokyo'})+' JST':'Time not supplied'));
  });
  if(state.id==='lapd') result=state.data.filter(v=>v.hndrdth_lon && v.hndrdth_lat && valid(Number(v.hndrdth_lon),Number(v.hndrdth_lat)) && Number(v.hndrdth_lat)!==0 && Number(v.hndrdth_lon)!==0).map(v=>point(Number(v.hndrdth_lon),Number(v.hndrdth_lat),v.nibr_description,(v.area_name||'').trim()+' · '+v.date_occ+' · Approximate hundred-block location'));
  return {type:'FeatureCollection',features:result};
}
function loadMapLibrary() {
  if(window.maplibregl) return Promise.resolve(window.maplibregl);
  if(mapLibrary) return mapLibrary;
  mapLibrary=new Promise((resolve,reject)=>{
    const css=document.createElement('link'); css.rel='stylesheet'; css.href='https://unpkg.com/maplibre-gl@5.6.2/dist/maplibre-gl.css'; document.head.append(css);
    const script=document.createElement('script'); script.src='https://unpkg.com/maplibre-gl@5.6.2/dist/maplibre-gl.js';
    const timer=setTimeout(()=>reject(new Error('MapLibre download timed out')),15000);
    script.onload=()=>{clearTimeout(timer);resolve(window.maplibregl);}; script.onerror=()=>{clearTimeout(timer);reject(new Error('MapLibre unavailable'));}; document.head.append(script);
  });
  return mapLibrary;
}
async function mapView() {
  const token=state.token; state.geojson=features();
  if(state.geoBlob)URL.revokeObjectURL(state.geoBlob);
  state.geoBlob=URL.createObjectURL(new Blob([JSON.stringify(state.geojson,null,2)],{type:'application/geo+json'}));
  byId('download-geojson').href=state.geoBlob;
  byId('download-geojson').download=state.id+(state.source?.saved?'-saved-example':'')+'.geojson';
  byId('download-geojson').hidden=!state.geojson.features.length;
  if(!state.geojson.features.length) { byId('map-status').textContent=textFor({ja:'この応答に表示できる座標はありません。運行時間外や空の配信もあります。',en:'This response has no mappable coordinates. The feed may be empty or the route out of service.'}); if(state.map?.getSource('records'))state.map.getSource('records').setData(state.geojson); return; }
  byId('map-status').textContent=textFor({ja:'地図を読み込み中…',en:'Loading map…'});
  try {
    const lib=await loadMapLibrary(); if(token!==state.token || state.mode!=='map') return;
    if(!state.map) {
      state.map=new lib.Map({container:'map-canvas',style:'https://tiles.openfreemap.org/styles/liberty',center:[0,20],zoom:1});
      state.map.addControl(new lib.NavigationControl(),'top-right');
      state.map.on('error',()=>{byId('map-status').textContent=textFor({ja:'背景地図を取得できない場合があります。Raw / Prettyはそのまま使えます。',en:'Some map resources could not load. Raw and Pretty remain available.'});});
      await new Promise(resolve=>state.map.once('load',resolve));
      state.map.addSource('records',{type:'geojson',data:state.geojson});
      state.map.addLayer({id:'records',type:'circle',source:'records',paint:{'circle-radius':['get','radius'],'circle-color':'#315876','circle-stroke-color':'#fff','circle-stroke-width':1.5}});
      state.map.on('click','records',event=>{
        const f=event.features[0]; const content=document.createElement('div');
        const title=document.createElement('strong'); title.textContent=f.properties.title;
        const detail=document.createElement('p'); detail.textContent=f.properties.detail;
        content.append(title,detail); new lib.Popup().setLngLat(f.geometry.coordinates).setDOMContent(content).addTo(state.map);
      });
    }
    if(token!==state.token || state.mode!=='map') return;
    state.map.resize(); state.map.getSource('records').setData(state.geojson);
    const points=state.geojson.features.map(f=>f.geometry.coordinates);
    const bounds=new lib.LngLatBounds(points[0],points[0]); points.slice(1).forEach(p=>bounds.extend(p));
    if(points.length===1)state.map.jumpTo({center:points[0],zoom:10});
    else state.map.fitBounds(bounds,{padding:45,maxZoom:13,duration:0});
    byId('map-status').textContent=textFor({ja:points.length+'地点 · 同じ応答の座標をGeoJSONにして表示。',en:points.length+' points · coordinates from the same response, rendered as GeoJSON.'});
  } catch(error) { byId('map-status').textContent=textFor({ja:'地図を表示できません（WebGLまたは地図ライブラリ）。Raw / Prettyを使ってください。',en:'Map unavailable (WebGL or map-library issue). Use Raw or Pretty instead.'}); }
}
function renderViews() {
  const hasData=state.data!==null;
  const pokemon=state.id==='pokemon';
  const visualButton=document.querySelector('[data-view="map"], [data-view="usage"]');
  visualButton.dataset.view=pokemon?'usage':'map';
  visualButton.textContent=pokemon?'Usage':'Map';
  byId('raw-output').hidden=state.mode!=='raw';
  byId('pretty-output').hidden=state.mode!=='pretty' || state.id==='holidays';
  byId('csv-output').hidden=state.mode!=='pretty' || state.id!=='holidays';
  byId('map-output').hidden=state.mode!=='map';
  byId('usage-output').hidden=state.mode!=='usage';
  if(state.mode==='usage')renderPokemonUsage();
  byId('color-control').hidden=state.mode!=='pretty' || state.id==='holidays';
  document.querySelectorAll('[data-view]').forEach(button=>{button.setAttribute('aria-pressed',String(button.dataset.view===state.mode)); if(['map','usage'].includes(button.dataset.view))button.disabled=!hasData || (!pokemon && !state.dataset.map);});
  byId('raw-output').querySelector('code').textContent=state.raw;
  byId('coordinate-note').textContent=textFor(state.dataset.map_note);
  if(!hasData) {byId('pretty-output').querySelector('code').textContent=''; byId('csv-output').replaceChildren(); return;}
  if(state.id==='holidays')csvTable(); else jsonColors(JSON.stringify(state.data,null,2));
  if(state.mode==='map')mapView();
}
function renderPokemonUsage() {
  const host=byId('usage-output'); host.replaceChildren();
  if(!state.data)return;
  const data=state.data;
  const title=document.createElement('h3');title.textContent=textFor({ja:'JSONから、ポケモン図鑑のカードへ',en:'From JSON to a Pokédex card'});
  const intro=document.createElement('p');intro.textContent=textFor({ja:'上でポケモンを選んで取得。画像の向きや色を変えてみよう。下のカードは、同じAPI応答からつくっています。',en:'Choose a Pokémon above and fetch. Try another sprite view or color. This card is built from the same API response.'});
  const card=document.createElement('div');card.className='pokemon-card';
  const image=document.createElement('img');image.width=192;image.height=192;image.alt=data.name||'Pokémon';
  const info=document.createElement('div');
  const name=document.createElement('h4');name.textContent=data.name||'—';
  const types=document.createElement('p');types.textContent=(data.types||[]).map(t=>t.type?.name).filter(Boolean).join(' / ');
  const controls=document.createElement('div');controls.className='pokemon-sprite-controls';
  const note=document.createElement('p');note.className='subtle';note.setAttribute('role','status');
  let selected='front_default';
  const variants=[['front_default',{ja:'正面',en:'Front'}],['back_default',{ja:'後ろ',en:'Back'}],['front_shiny',{ja:'色違い · 正面',en:'Shiny · front'}],['back_shiny',{ja:'色違い · 後ろ',en:'Shiny · back'}]];
  const update=()=>{
    const path=data.sprites?.[selected];let safe=false;
    try{const url=new URL(path);safe=url.protocol==='https:' && url.hostname==='raw.githubusercontent.com';if(safe)image.src=url.href;}catch(_){}
    image.hidden=!safe;
    note.textContent=safe?'sprites["'+selected+'"]':textFor({ja:'この画像は提供されていません。',en:'This sprite is not available.'});
    controls.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.sprite===selected)));
  };
  variants.forEach(([key,label])=>{const button=document.createElement('button');button.type='button';button.dataset.sprite=key;button.textContent=textFor(label);button.disabled=!data.sprites?.[key];button.addEventListener('click',()=>{selected=key;update();});controls.append(button);});
  image.addEventListener('error',()=>{image.hidden=true;note.textContent=textFor({ja:'画像を読み込めませんでした。名前とタイプは同じ応答から表示しています。',en:'The sprite could not load. Name and types still come from the same response.'});});
  info.append(name,types,controls,note);card.append(image,info);
  const keys=document.createElement('dl');keys.className='pokemon-field-guide';
  [['pokemon["name"]',{ja:'カードの名前',en:'Card name'}],['pokemon["types"][0]["type"]["name"]',{ja:'最初のタイプ',en:'First type'}],['pokemon["sprites"]["front_default"]',{ja:'画像のURL → 画像として表示',en:'Image URL → displayed sprite'}]].forEach(([key,label])=>{const term=document.createElement('dt'),code=document.createElement('code'),description=document.createElement('dd');code.textContent=key;term.append(code);description.textContent=textFor(label);keys.append(term,description);});
  host.append(title,intro,card,keys);update();
}
function response(raw,url,saved=false,decoded=null,bytes=null) {
  state.raw=raw; state.url=url;
  state.data=decoded || (state.id==='holidays'?parseCSV(raw):JSON.parse(raw));
  state.source={saved,bytes:bytes?.byteLength || new TextEncoder().encode(raw).length,at:new Date().toLocaleString('ja-JP',{timeZone:'Asia/Tokyo'})+' JST'};
  if(state.blob)URL.revokeObjectURL(state.blob);
  state.blob=URL.createObjectURL(new Blob([bytes||raw],{type:bytes?'application/octet-stream':state.id==='holidays'?'text/csv;charset=utf-8':'application/json;charset=utf-8'}));
  byId('download-data').href=state.blob; byId('download-data').download=state.id+(saved?'-saved-example':'')+(bytes?'.pb':state.id==='holidays'?'.csv':state.dataset.format==='GeoJSON'?'.geojson':'.json'); byId('download-data').hidden=false;
  renderStatus(); renderViews();
}
async function fetchData(saved=false) {
  controller?.abort(); controller=new AbortController(); const token=++state.token; const dataset=state.dataset;
  if(saved)renderFields(state.id==='holidays'?values():defaults[state.id]);
  const url=requestURL(state.id,values());
  if(!saved && cache.has(url)) { const record=cache.get(url); response(record.raw,url,false,record.decoded,record.bytes); state.source=record.source; renderStatus(); return; }
  state.raw=''; state.data=null; state.source=null;
  byId('download-data').hidden=true;
  if(state.map?.getSource('records')) state.map.getSource('records').setData({type:'FeatureCollection',features:[]});
  renderViews();
  byId('fetch-data').disabled=true;
  status({ja:saved?'保存例を読み込み中…':'APIに問い合わせ中…',en:saved?'Loading saved example…':'Requesting data…'});
  const timer=setTimeout(()=>controller.abort(),15000);
  try {
    const res=await fetch(saved?dataset.snapshot:url,{signal:controller.signal,credentials:'omit'});
    if(!res.ok)throw new Error('HTTP '+res.status);
    const buffer=await res.arrayBuffer(); if(buffer.byteLength>1500000)throw new Error('Response too large');
    let raw,decoded=null,bytes=null;
    if(dataset.binary) {
      if(!gtfsType)gtfsType=fetch('assets/data-explorer/vendor/gtfs-realtime.proto').then(r=>{if(!r.ok)throw new Error('Schema unavailable');return r.text();}).then(proto=>protobuf.parse(proto,{keepCase:true}).root.lookupType('transit_realtime.FeedMessage')).catch(error=>{gtfsType=null;throw error;});
      const type=await gtfsType;
      bytes=new Uint8Array(buffer);
      decoded=type.toObject(type.decode(bytes),{longs:Number,enums:String});
      raw=Array.from({length:Math.ceil(bytes.length/16)},(_,row)=>row*16).map(offset=>offset.toString(16).padStart(6,'0')+'  '+[...bytes.slice(offset,offset+16)].map(b=>b.toString(16).padStart(2,'0')).join(' ')).join('\n');
    } else raw=new TextDecoder(dataset.encoding).decode(buffer);
    if(token!==state.token)return;
    response(raw,url,saved,decoded,bytes);
    if(!saved)cache.set(url,{raw,decoded,bytes,source:state.source});
  } catch(error) {
    if(token!==state.token)return;
    status({ja:'取得できませんでした（通信・CORS・配信制限）。「保存例を使う」で実データの保存版を開けます。',en:'Request failed (network, CORS, or provider limits). Use saved example to open a real cached response.'},'error');
  } finally {clearTimeout(timer); if(token===state.token)byId('fetch-data').disabled=false;}
}
function metadata() {
  const d=state.dataset;
  byId('provider').textContent=d.provider+' · '+d.format;
  byId('data-title').textContent=textFor(d.title); byId('data-summary').textContent=textFor(d.summary);
  byId('docs-link').href=d.docs; byId('parameter-explanation').textContent=textFor(d.parameters);
  byId('data-aha').textContent=textFor(d.aha); byId('python-path').textContent=d.python;
  byId('fetch-data').querySelector('.lang-ja').textContent=d.browser_fetch===false?'保存例を読み直す':'取得する';
  byId('fetch-data').querySelector('.lang-en').textContent=d.browser_fetch===false?'Reload saved example':'Fetch data';
  if(d.documentation_example) {
    byId('fetch-data').querySelector('.lang-ja').textContent='仕様書の例を読む';
    byId('fetch-data').querySelector('.lang-en').textContent='Read documentation example';
  }
  byId('load-snapshot').hidden=d.browser_fetch===false;
  byId('raw-link').querySelector('.lang-ja').textContent=d.documentation_example?'仕様書のRaw例':'提供元のRawデータ';
  byId('raw-link').querySelector('.lang-en').textContent=d.documentation_example?'Raw documentation example':'Provider’s raw data';
}
function chooseDataset(id,load=true) {
  controller?.abort(); ++state.token;
  state.id=id; state.dataset=state.config.datasets[id]; state.raw=''; state.data=null; state.source=null;
  if(!state.dataset.map && state.mode==='map')state.mode='pretty';
  if(state.mode==='usage' && id!=='pokemon')state.mode='pretty';
  if(id==='pokemon')state.mode='usage';
  if(id==='toeiBus')state.mode='map';
  byId('download-data').hidden=true; byId('fetch-data').disabled=false;
  document.querySelectorAll('[data-dataset]').forEach(button=>{
    const active=button.dataset.dataset===id;
    button.setAttribute('aria-selected',String(active)); button.tabIndex=active?0:-1;
    if(active)byId('dataset-panel').setAttribute('aria-labelledby',button.id);
  });
  metadata(); renderFields(); renderViews();
  const url=new URL(location.href); url.searchParams.set('week',String(state.week.week).padStart(2,'0')); url.searchParams.set('example',id); history.replaceState(null,'',url);
  if(load)fetchData(state.dataset.browser_fetch===false);
}
function chooseWeek(week,example) {
  state.week=week; byId('dataset-tabs').replaceChildren();
  week.examples.forEach((id,index)=>{
    const button=document.createElement('button'); button.type='button'; button.className='ui-tab'; button.id='dataset-'+id; button.dataset.dataset=id; button.setAttribute('role','tab'); button.setAttribute('aria-controls','dataset-panel'); button.textContent=textFor(state.config.datasets[id].title);
    button.addEventListener('click',()=>chooseDataset(id));
    button.addEventListener('keydown',event=>{
      if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;
      event.preventDefault();
      const target=event.key==='Home'?0:event.key==='End'?week.examples.length-1:(index+(event.key==='ArrowRight'?1:-1)+week.examples.length)%week.examples.length;
      chooseDataset(week.examples[target]); byId('dataset-'+week.examples[target]).focus();
    });
    byId('dataset-tabs').append(button);
  });
  chooseDataset(week.examples.includes(example)?example:week.examples[0]);
}
document.addEventListener('DOMContentLoaded',async()=>{
  try {
    const query=new URLSearchParams(location.search);
    const configResponse=await fetch('content/explorations.json'); if(!configResponse.ok)throw new Error('Missing exploration content'); state.config=await configResponse.json();
    const allowed=[];
    for(const week of state.config.weeks) {
      const res=await fetch('content/weeks/'+week.content,{cache:'no-cache'}); if(!res.ok)continue;
      if(isAvailable(parseFrontMatter(await res.text())))allowed.push(week);
    }
    if(!allowed.length) {byId('explore-message').textContent=textFor({ja:'Explore教材は準備中です。公開までお待ちください。',en:'Explore materials are being prepared. Please check back after release.'}); byId('explore-week').disabled=true; return;}
    allowed.forEach(week=>{const option=document.createElement('option');option.value=week.week;option.textContent='Week '+String(week.week).padStart(2,'0')+' · '+textFor(week.title);byId('explore-week').append(option);});
    const week=allowed.find(w=>w.week===Number(query.get('week')))||allowed[0]; byId('explore-week').value=week.week;
    byId('explorer').hidden=false; byId('explore-message').textContent='';
    byId('explore-week').addEventListener('change',()=>chooseWeek(allowed.find(w=>w.week===Number(byId('explore-week').value))));
    byId('request-form').addEventListener('submit',event=>{event.preventDefault();cache.delete(requestURL(state.id,values()));fetchData(state.dataset.browser_fetch===false);});
    byId('load-snapshot').addEventListener('click',()=>fetchData(true));
    document.querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',()=>{state.mode=button.dataset.view;renderViews();}));
    byId('syntax-color').addEventListener('change',renderViews);
    new MutationObserver(()=>{
      const v=values();metadata();renderFields(v);renderStatus();renderViews();
      document.querySelectorAll('[data-dataset]').forEach(button=>button.textContent=textFor(state.config.datasets[button.dataset.dataset].title));
    }).observe(document.documentElement,{attributes:true,attributeFilter:['data-language']});
    try {const back=new URL(query.get('return')||'agenda.html?open='+String(week.week).padStart(2,'0')+'#week-'+String(week.week).padStart(2,'0'),location.href);if(back.origin===location.origin && /\/(?:agenda|index|weeks\/week-\d+\/lecture)\.html$/.test(back.pathname))byId('explore-return').href=back.href;}catch(_){}
    chooseWeek(week,query.get('example'));
  } catch(error) {byId('explore-message').textContent=textFor({ja:'Exploreを読み込めませんでした。ページを再読み込みしてください。',en:'Could not load Explore. Please reload the page.'});console.error(error);}
});
