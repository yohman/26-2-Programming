/* Read-only API explorer. No stored credentials, proxies, or background polling. */
const byId = id => document.getElementById(id);
const locale = () => document.documentElement.dataset.language === 'en' ? 'en' : 'ja';
const textFor = value => typeof value === 'string' ? value : value?.[locale()] || '';
const state = { config:null, week:null, id:null, dataset:null, raw:'', data:null, url:'', mode:'pretty', source:null, token:0, blob:null, geoBlob:null, map:null, geojson:null };
const cache = new Map();
let controller;
let mapLibrary;
let mapPopup=null, popupTimer=null, hoveredRecord=null;
function closeMapPopup() {
  clearTimeout(popupTimer);
  mapPopup?.remove();mapPopup=null;hoveredRecord=null;
}
function schedulePopupClose() {
  clearTimeout(popupTimer);
  popupTimer=setTimeout(closeMapPopup,180);
}
let gtfsType;
let lapdLocations=[];
let lapdLocationError=false;
let highlightedDescent=null;
let satelliteMap=false;
const descentAliases={'B':'Black/African American','Black':'Black/African American','W':'White/Caucasian','White':'White/Caucasian','A - Asian':'Asian','F - Filipino':'Filipino','H - Hispanic':'Hispanic','K - Korean':'Korean','O - Other':'Other','U - Hawaiian':'Hawaiian','X - Unknown':'Unknown'};
const descentNames=['Hispanic','Black/African American','White/Caucasian','Other Asian','Other','Unknown','Not reported','Asian','American Indian','Asian Indian','Cambodian','Chinese','Filipino','Guamanian','Hawaiian','Japanese','Korean','Laotian','Middle Eastern/Arab','Pacific Islander','Samoan','Vietnamese'];
// Stable categorical colors, not a severity scale. Unknown values stay neutral.
const descentColors=['#e76f00','#6d3fc0','#0072ce','#008b80','#d33178','#697580','#a1a8ae','#008b80','#a64b00','#b35399','#216c9c','#8752b0','#bc5b00','#427d45','#008a9b','#b63d64','#6269bf','#bd7c00','#00766c','#a64835','#7e4d93','#4f7f26'];
const descentLabel=value=>descentAliases[value]||value||'Not reported';
const descentColor=value=>descentColors[descentNames.indexOf(value)]||'#777777';
async function victimLocations(victims,saved,signal) {
  if(saved) {const res=await fetch('weeks/week-03/explore-data/lapd-victim-locations.json',{signal});if(!res.ok)throw new Error('Location backup unavailable');return res.json();}
  const ids=[...new Set(victims.map(v=>v.caseno).filter(id=>/^[A-Za-z0-9_-]+$/.test(id||'')))];const rows=[];
  for(let i=0;i<ids.length;i+=100) {
    const url=new URL('https://data.lacity.org/resource/k7nn-b2ep.json');
    url.searchParams.set('$select','caseno,hndrdth_lat,hndrdth_lon');url.searchParams.set('$group','caseno,hndrdth_lat,hndrdth_lon');
    url.searchParams.set('$where',"caseno in ("+ids.slice(i,i+100).map(id=>"'"+id+"'").join(',')+") AND hndrdth_lat > 0 AND hndrdth_lon < 0");url.searchParams.set('$limit','5000');
    const res=await fetch(url,{signal,credentials:'omit'});if(!res.ok)throw new Error('Location lookup failed');const batch=await res.json();if(batch.length>=5000)throw new Error('Location lookup truncated');rows.push(...batch);
  }
  return rows;
}
const weatherPlaces={tokyo:{lat:35.68,lon:139.69,ja:'東京',en:'Tokyo'},kashiwa:{lat:35.86,lon:139.97,ja:'柏',en:'Kashiwa'},osaka:{lat:34.69,lon:135.5,ja:'大阪',en:'Osaka'},sapporo:{lat:43.06,lon:141.35,ja:'札幌',en:'Sapporo'},naha:{lat:26.21,lon:127.68,ja:'那覇',en:'Naha'}};
const defaults = {
  books:{q:'intitle:鬼滅の刃',langRestrict:'ja',maxResults:'6',apiKey:''},
  players:{query:'Shohei Ohtani'},
  sports:{league:'epl',date:''},
  toeiBus:{},
  toei:{line:'Oedo'},
  weather:{location:'tokyo',latitude:'35.68',longitude:'139.69',forecast_days:'1'},
  earthquakes:{magnitude:'2.5',period:'day'},
  pokemon:{name:'pikachu'},
  music:{term:'Eminem Lose Yourself',limit:'5'},
  transit:{route:'1',limit:'20'},
  tokyo:{},
  lapd:{area:'all',limit:'50'},
  holidays:{year:'2026'}
};
const fields = {
  books:[
    {key:'q',label:{ja:'q · 本・著者を検索',en:'q · Book or author'},type:'text'},
    {key:'langRestrict',label:{ja:'言語',en:'Language'},options:[['ja','日本語'],['en','English'],['','All']]},
    {key:'maxResults',label:{ja:'maxResults · 最大件数',en:'maxResults · Maximum results'},options:[['6','6'],['12','12'],['20','20']]},
    {key:'apiKey',label:{ja:'APIキー（任意・保存しません）',en:'API key (optional, never stored)'},type:'password',optional:true}
  ],
  players:[{key:'query',label:{ja:'選手名（英字）',en:'Player name'},type:'text'}],
  sports:[
    {key:'league',label:{ja:'競技・リーグ',en:'Sport / league'},options:[['epl','EPL · Premier League'],['laliga','La Liga'],['mlb','MLB'],['mlbPlayoffs','MLB · Playoffs'],['nba','NBA'],['nfl','NFL'],['nhl','NHL']]},
    {key:'date',label:{ja:'日付（空欄＝ESPNの最新表示）',en:'Date (blank = ESPN default)'},type:'date',optional:true}
  ],
  music:[
    {key:'term',label:{ja:'term · 曲名・アーティスト',en:'term · Song or artist'},type:'text'},
    {key:'limit',label:{ja:'limit · 最大件数',en:'limit · Maximum results'},options:[['5','5'],['10','10'],['20','20']]}
  ],
  toeiBus:[],
  toei:[{key:'line',label:{ja:'路線 · odpt:railway',en:'Line · odpt:railway'},options:[['Oedo','大江戸線 · Oedo'],['Asakusa','浅草線 · Asakusa'],['Mita','三田線 · Mita'],['Shinjuku','新宿線 · Shinjuku'],['Arakawa','東京さくらトラム · Arakawa'],['all','全路線 · All lines']]}],
  tokyo:[],
  lapd:[
    {key:'area',label:{ja:'地区 · $where',en:'Area · $where'},options:[['all','All areas'],['Central','Central'],['Hollywood','Hollywood'],['Pacific','Pacific'],['Harbor','Harbor']]},
    {key:'limit',label:{ja:'$limit · 最大件数',en:'$limit · Maximum rows'},options:[['25','25'],['50','50'],['100','100'],['1000','1,000']]}
  ],
  weather:[
    {key:'location',label:{ja:'場所',en:'Location'},options:[['tokyo','東京 · Tokyo'],['kashiwa','柏 · Kashiwa'],['osaka','大阪 · Osaka'],['sapporo','札幌 · Sapporo'],['naha','那覇 · Naha'],['custom','座標で指定 · Coordinates']]},
    {key:'latitude',label:{ja:'latitude · 緯度',en:'latitude'},type:'number',min:-90,max:90,step:'any'},
    {key:'longitude',label:{ja:'longitude · 経度',en:'longitude'},type:'number',min:-180,max:180,step:'any'},
    {key:'forecast_days',label:{ja:'forecast_days · 日数',en:'forecast_days'},options:[['1','1'],['2','2'],['3','3']]}
  ],
  earthquakes:[
    {key:'magnitude',label:{ja:'最小マグニチュード',en:'Minimum magnitude'},options:[['2.5','M2.5+'],['4.5','M4.5+']]},
    {key:'period',label:{ja:'期間',en:'Window'},options:[['hour','1 hour'],['day','24 hours'],['week','7 days'],['month','30 days']]}
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
  if(id==='books') {
    const url=new URL('https://www.googleapis.com/books/v1/volumes');
    url.searchParams.set('q',v.q);url.searchParams.set('maxResults',v.maxResults);
    if(v.langRestrict)url.searchParams.set('langRestrict',v.langRestrict);
    return url.href;
  }
  if(id==='players') {
    const url=new URL('https://site.api.espn.com/apis/common/v3/search');
    url.searchParams.set('query',v.query);url.searchParams.set('limit','10');url.searchParams.set('type','player');return url.href;
  }
  if(id==='sports') {
    const paths={epl:'soccer/eng.1',laliga:'soccer/esp.1',mlb:'baseball/mlb',mlbPlayoffs:'baseball/mlb',nba:'basketball/nba',nfl:'football/nfl',nhl:'hockey/nhl'};
    const url=new URL('https://site.api.espn.com/apis/site/v2/sports/'+(paths[v.league]||paths.epl)+'/scoreboard');
    if(/^\d{4}-\d{2}-\d{2}$/.test(v.date||''))url.searchParams.set('dates',v.date.replaceAll('-',''));
    return url.href;
  }
  if(id==='music') {
    const url=new URL('https://itunes.apple.com/search');
    Object.entries({term:v.term,entity:'song',country:'US',limit:v.limit}).forEach(([key,value])=>url.searchParams.set(key,value));
    return url.href;
  }
  if(id==='toeiBus') return 'https://api-public.odpt.org/api/v4/gtfs/realtime/ToeiBus';
  if(id==='toei') {
    const url=new URL('https://api-public.odpt.org/api/v4/odpt:Train');
    url.searchParams.set('odpt:operator','odpt.Operator:Toei');
    if(v.line!=='all')url.searchParams.set('odpt:railway','odpt.Railway:Toei.'+v.line);
    return url.href;
  }
  if(id==='tokyo') return 'https://api.odpt.org/api/v4/odpt:Train?odpt:operator=odpt.Operator:TokyoMetro&odpt:railway=odpt.Railway:TokyoMetro.Yurakucho&acl:consumerKey=YOUR_API_KEY';
  if(id==='lapd') {
    const url=new URL('https://data.lacity.org/resource/gqf2-vm2j.json');
    url.searchParams.set('$select','caseno,uniquevictimno,date_occ,area_name,victimofslist,vict_age,vict_sex,vict_descent,victim_type,victim_shot');
    if(v.area!=='all')url.searchParams.set('$where',"trim(area_name) = '"+v.area+"'");
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
    else { input.type=field.type; if(field.min!==undefined)input.min=field.min; if(field.max!==undefined)input.max=field.max; if(field.step!==undefined)input.step=field.step; input.required=!field.optional; }
    input.value = v[field.key];
    input.addEventListener('input',()=>{
      if(state.id==='weather') {
        if(field.key==='location' && weatherPlaces[input.value]) {
          const place=weatherPlaces[input.value];byId('parameter-fields').querySelector('[name="latitude"]').value=place.lat;byId('parameter-fields').querySelector('[name="longitude"]').value=place.lon;
        } else if(['latitude','longitude'].includes(field.key)) byId('parameter-fields').querySelector('[name="location"]').value='custom';
      }
      updateRequest();
    });
    if(field.type==='password')input.autocomplete='off';
    label.append(input); byId('parameter-fields').append(label);
  });
  if(state.id==='books') {
    const examples=document.createElement('div');examples.className='book-search-examples';
    ['鬼滅の刃','君の名は。','君たちはどう生きるか'].forEach(title=>{
      const button=document.createElement('button');button.type='button';button.textContent=title;
      button.addEventListener('click',()=>{byId('parameter-fields').querySelector('[name="q"]').value='intitle:'+title;updateRequest();fetchData(!values().apiKey.trim(),true);});
      examples.append(button);
    });
    byId('parameter-fields').append(examples);
  }
  updateRequest();
}
function status(message,kind='live') { byId('data-status').textContent = textFor(message); byId('data-status').dataset.kind=kind; }
function renderStatus() {
  if (!state.source) return;
  const time=state.source.at;
  if (state.source.saved) {
    if(state.dataset.classroom_example) {
      status({ja:'授業用サンプル · Google Booksの書誌ページから作成 · APIの実応答ではありません。',en:'Classroom sample · compiled from Google Books bibliographic pages · not a captured API response.'},'snapshot');
      return;
    }
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
  if(state.id==='earthquakes') result=(state.data.features||[]).filter(f=>f.geometry?.type==='Point' && valid(...f.geometry.coordinates)).map(f=>{
    const feature=point(...f.geometry.coordinates.slice(0,2),f.properties?.place,'M '+f.properties?.mag+' · '+new Date(f.properties?.time).toISOString());
    const magnitude=Number(f.properties?.mag);
    feature.properties.radius=Number.isFinite(magnitude)?Math.max(2,Math.min(64,3*Math.pow(2,magnitude-2.5))):3;
    return feature;
  });
  if(state.id==='weather' && valid(state.data.longitude,state.data.latitude)) result=[point(state.data.longitude,state.data.latitude,'Forecast location',state.data.current?.time+' · '+state.data.current?.temperature_2m+' °C')];
  if(state.id==='transit') result=(state.data.data||[]).filter(v=>valid(v.attributes?.longitude,v.attributes?.latitude)).map(v=>point(v.attributes.longitude,v.attributes.latitude,'Vehicle '+(v.attributes.label||v.id),'Route '+(v.relationships?.route?.data?.id||'')+' · '+v.attributes.updated_at));
  if(state.id==='toeiBus') result=(state.data.entity||[]).filter(e=>valid(e.vehicle?.position?.longitude,e.vehicle?.position?.latitude)).map(e=>{
    const v=e.vehicle,p=v.position;
    const stamp=v.timestamp||state.data.header?.timestamp;
    return point(p.longitude,p.latitude,'Bus '+(v.vehicle?.label||v.vehicle?.id||e.id),'Route '+(v.trip?.route_id||'—')+' · '+p.latitude.toFixed(5)+', '+p.longitude.toFixed(5)+' · '+(stamp?new Date(stamp*1000).toLocaleString('ja-JP',{timeZone:'Asia/Tokyo'})+' JST':'Time not supplied'));
  });
  if(state.id==='lapd') {
    const locations=new Map();lapdLocations.forEach(row=>{const list=locations.get(row.caseno)||new Map();list.set(row.hndrdth_lon+','+row.hndrdth_lat,row);locations.set(row.caseno,list);});
    result=state.data.flatMap(v=>{const matches=locations.get(v.caseno);if(matches?.size!==1)return [];const row=[...matches.values()][0],lon=Number(row.hndrdth_lon),lat=Number(row.hndrdth_lat);if(!valid(lon,lat)||!lon||!lat)return [];
      const race=descentLabel(v.vict_descent);const f=point(lon,lat,v.victimofslist,'Approximate hundred-block location');
      Object.assign(f.properties,{radius:7,color:descentColor(race),race,descent:v.vict_descent||'',age:v.vict_age||'',sex:v.vict_sex||'',victimType:v.victim_type||'',shot:v.victim_shot||'',date:v.date_occ||'',area:v.area_name||'',caseNo:v.caseno||'',victimId:v.uniquevictimno||''});return [f];});
  }
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
function applyMapHighlight() {
  const map=state.map;if(!map?.getLayer('records'))return;
  const focused=state.id==='lapd' && highlightedDescent;
  const selected=['==',['get','race'],highlightedDescent||''];
  map.setPaintProperty('records','circle-opacity',focused?['case',selected,1,.12]:(state.id==='earthquakes' ? .45 : state.id==='lapd' ? 1 : .9));
  map.setPaintProperty('records','circle-stroke-opacity',focused?['case',selected,1,.12]:(state.id==='earthquakes' ? .65 : 1));
  map.setLayoutProperty('records','circle-sort-key',focused?['case',selected,1,0]:0);
  byId('map-legend')?.querySelectorAll('button').forEach(button=>{
    const active=(button.dataset.category||null)===highlightedDescent;
    button.setAttribute('aria-pressed',String(active));
    button.classList.toggle('is-dimmed',Boolean(highlightedDescent && !active));
  });
}
function mapControls() {
  let controls=byId('map-basemap');
  if(!controls){controls=document.createElement('div');controls.id='map-basemap';controls.setAttribute('role','group');byId('map-canvas').before(controls);}
  controls.setAttribute('aria-label',textFor({ja:'背景地図',en:'Basemap'}));controls.replaceChildren();
  [[false,{ja:'地図',en:'Street'}],[true,{ja:'衛星写真',en:'Satellite'}]].forEach(([satellite,label])=>{
    const button=document.createElement('button');button.type='button';button.textContent=textFor(label);button.setAttribute('aria-pressed',String(satelliteMap===satellite));
    button.addEventListener('click',()=>{
      satelliteMap=satellite;
      if(state.map?.getLayer('satellite-imagery'))state.map.setLayoutProperty('satellite-imagery','visibility',satellite?'visible':'none');
      mapControls();
    });controls.append(button);
  });
}
async function mapView() {
  const token=state.token; state.geojson=features();
  mapControls();
  let legend=byId('map-legend');if(!legend){legend=document.createElement('div');legend.id='map-legend';byId('map-status').after(legend);}legend.replaceChildren();legend.hidden=state.id!=='lapd';
  if(state.id==='lapd') {
    const counts=new Map();state.geojson.features.forEach(f=>counts.set(f.properties.race,(counts.get(f.properties.race)||0)+1));
    if(!counts.has(highlightedDescent))highlightedDescent=null;
    const all=document.createElement('button');all.type='button';all.textContent=textFor({ja:'すべて',en:'All'});all.setAttribute('aria-pressed',String(!highlightedDescent));
    all.addEventListener('click',()=>{highlightedDescent=null;closeMapPopup();applyMapHighlight();});legend.append(all);
    [...counts].sort((a,b)=>b[1]-a[1]).forEach(([race,count])=>{
      const item=document.createElement('button'),swatch=document.createElement('i');item.type='button';item.dataset.category=race;item.setAttribute('aria-pressed',String(highlightedDescent===race));
      swatch.style.background=descentColor(race);swatch.setAttribute('aria-hidden','true');item.append(swatch,document.createTextNode(race+' ('+count+')'));
      item.addEventListener('click',()=>{highlightedDescent=highlightedDescent===race?null:race;closeMapPopup();applyMapHighlight();});legend.append(item);
    });
  }
  if(state.geoBlob)URL.revokeObjectURL(state.geoBlob);
  state.geoBlob=URL.createObjectURL(new Blob([JSON.stringify(state.geojson,null,2)],{type:'application/geo+json'}));
  byId('download-geojson').href=state.geoBlob;
  byId('download-geojson').download=state.id+(state.source?.saved?'-saved-example':'')+'.geojson';
  byId('download-geojson').hidden=!state.geojson.features.length;
  if(!state.geojson.features.length) { byId('map-status').textContent=state.id==='lapd'?textFor({ja:lapdLocationError?'位置の照合を取得できませんでした。Raw / Prettyは利用できます。':'取得した被害者記録に、一意に照合できる位置がありません。',en:lapdLocationError?'Location lookup failed. Raw / Pretty remain available.':'No victim records have an unambiguous matched location.'}):textFor({ja:'この応答に表示できる座標はありません。運行時間外や空の配信もあります。',en:'This response has no mappable coordinates. The feed may be empty or the route out of service.'}); if(state.map?.getSource('records'))state.map.getSource('records').setData(state.geojson); return; }
  byId('map-status').textContent=textFor({ja:'地図を読み込み中…',en:'Loading map…'});
  try {
    const lib=await loadMapLibrary(); if(token!==state.token || state.mode!=='map') return;
    if(!state.map) {
      state.map=new lib.Map({container:'map-canvas',style:'https://tiles.openfreemap.org/styles/liberty',center:[0,20],zoom:1});
      state.map.addControl(new lib.NavigationControl(),'top-right');
      state.map.on('error',()=>{byId('map-status').textContent=textFor({ja:'背景地図を取得できない場合があります。Raw / Prettyはそのまま使えます。',en:'Some map resources could not load. Raw and Pretty remain available.'});});
      await new Promise(resolve=>state.map.once('load',resolve));
      state.map.addSource('records',{type:'geojson',data:state.geojson});
      state.map.addLayer({id:'records',type:'circle',source:'records',paint:{'circle-radius':['get','radius'],'circle-color':['coalesce',['get','color'],'#315876'],'circle-stroke-color':'#fff','circle-stroke-width':1.5}});
      state.map.addSource('satellite-imagery',{type:'raster',tiles:['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],tileSize:256,maxzoom:19,attribution:'Imagery © Esri, Vantor, Earthstar Geographics, and the GIS User Community'});
      state.map.addLayer({id:'satellite-imagery',type:'raster',source:'satellite-imagery',layout:{visibility:satelliteMap?'visible':'none'}},'records');
      const showPopup=event=>{
        const f=state.id==='lapd' && highlightedDescent?event.features?.find(feature=>feature.properties.race===highlightedDescent):event.features?.[0];if(!f){schedulePopupClose();return;}
        clearTimeout(popupTimer);
        const key=JSON.stringify([f.geometry.coordinates,f.properties]);
        if(key===hoveredRecord && mapPopup?.isOpen())return;
        closeMapPopup();hoveredRecord=key;
        const content=document.createElement('div');
        const title=document.createElement('strong'); title.textContent=f.properties.title;
        const detail=document.createElement('p'); detail.textContent=f.properties.detail;
        if(state.id==='lapd') {
          const selected=state.geojson.features.find(item=>item.properties.victimId===f.properties.victimId);
          const coordinates=selected?.geometry.coordinates||f.geometry.coordinates;
          const records=state.geojson.features.filter(item=>(!highlightedDescent || item.properties.race===highlightedDescent) && item.geometry.coordinates.every((v,i)=>Math.abs(v-coordinates[i])<.00000001));
          if(!records.length)return;
          const body=document.createElement('div');
          const show=index=>{body.replaceChildren();const p=records[index].properties;const heading=document.createElement('strong');heading.textContent=p.title;body.append(heading);const dl=document.createElement('dl');
            [[{ja:'被害者記録ID',en:'Victim record'},p.victimId],[{ja:'人種・出自（記録値）',en:'Recorded descent'},p.descent],[{ja:'年齢',en:'Age'},p.age],[{ja:'性別（記録値）',en:'Recorded sex'},p.sex],[{ja:'被害者種別',en:'Victim type'},p.victimType],[{ja:'銃撃（記録値）',en:'Victim shot'},p.shot],[{ja:'発生日',en:'Occurrence date'},p.date],[{ja:'地区',en:'Area'},p.area],[{ja:'事件番号',en:'Case number'},p.caseNo]].forEach(([label,value])=>{const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=textFor(label);dd.textContent=value||textFor({ja:'記載なし',en:'Not reported'});dl.append(dt,dd);});body.append(dl);};
          if(records.length>1){const select=document.createElement('select');select.setAttribute('aria-label',textFor({ja:'同じ概略位置の被害者記録',en:'Victim records at this approximate location'}));records.forEach((r,i)=>{const o=document.createElement('option');o.value=i;o.textContent=(i+1)+' / '+records.length+' · '+r.properties.victimId;select.append(o);});select.addEventListener('change',()=>show(Number(select.value)));content.append(select);}
          show(0);content.append(body);const caveat=document.createElement('p');caveat.textContent=textFor({ja:'事件番号でOffensesと照合した概略位置。正確な住所ではありません。',en:'Approximate location joined to Offenses by case number, not an exact address.'});content.append(caveat);
        } else content.append(title,detail);
        const coordinates=[...f.geometry.coordinates];
        while(Math.abs(event.lngLat.lng-coordinates[0])>180)coordinates[0]+=event.lngLat.lng>coordinates[0]?360:-360;
        mapPopup=new lib.Popup({maxWidth:'360px'}).setLngLat(coordinates).setDOMContent(content).addTo(state.map);
        const element=mapPopup.getElement();
        element.addEventListener('mouseenter',()=>clearTimeout(popupTimer));
        element.addEventListener('mouseleave',schedulePopupClose);
      };
      state.map.on('mousemove','records',event=>{
        state.map.getCanvas().style.cursor='pointer';showPopup(event);
      });
      state.map.on('mouseleave','records',()=>{
        state.map.getCanvas().style.cursor='';schedulePopupClose();
      });
      // Touch devices retain tap-to-open; mouse users only need to hover.
      state.map.on('click','records',event=>{
        if(window.matchMedia('(hover: none)').matches || event.originalEvent?.sourceCapabilities?.firesTouchEvents)showPopup(event);
      });
      state.map.on('movestart',closeMapPopup);
    }
    if(token!==state.token || state.mode!=='map') return;
    state.map.resize(); state.map.getSource('records').setData(state.geojson);
    applyMapHighlight();
    state.map.setPaintProperty('records','circle-stroke-width',state.id==='earthquakes'?1:1.5);
    const points=state.geojson.features.map(f=>f.geometry.coordinates);
    const bounds=new lib.LngLatBounds(points[0],points[0]); points.slice(1).forEach(p=>bounds.extend(p));
    if(points.length===1)state.map.jumpTo({center:points[0],zoom:10});
    else state.map.fitBounds(bounds,{padding:45,maxZoom:13,duration:0});
    byId('map-status').textContent=state.id==='lapd'?textFor({ja:'取得 '+state.data.length+'件 / 地図 '+points.length+'件。Offensesの座標をcasenoで照合。未照合・複数位置の記録は地図から除外。同じ場所の点は重なります。',en:state.data.length+' fetched / '+points.length+' mapped. Coordinates joined from Offenses by caseno. Unmatched/ambiguous locations omitted; co-located points overlap.'}):textFor({ja:points.length+'地点 · 同じ応答の座標をGeoJSONにして表示。',en:points.length+' points · coordinates from the same response, rendered as GeoJSON.'});
  } catch(error) { byId('map-status').textContent=textFor({ja:'地図を表示できません（WebGLまたは地図ライブラリ）。Raw / Prettyを使ってください。',en:'Map unavailable (WebGL or map-library issue). Use Raw or Pretty instead.'}); }
}
function renderViews() {
  if(state.mode!=='map')closeMapPopup();
  const hasData=state.data!==null;
  const pokemon=state.id==='pokemon';
  const usage=pokemon || ['music','sports','players','books'].includes(state.id);
  const visualButton=document.querySelector('[data-view="map"], [data-view="usage"]');
  visualButton.dataset.view=usage?'usage':'map';
  visualButton.textContent=state.id==='books'?textFor({ja:'本棚',en:'Bookshelf'}):state.id==='players'?textFor({ja:'選手プロフィール',en:'Player bio'}):state.id==='sports'?textFor({ja:'スコア',en:'Scores'}):state.id==='music'?textFor({ja:'曲を聴く',en:'Listen'}):pokemon?'Usage':'Map';
  byId('raw-output').hidden=state.mode!=='raw';
  byId('pretty-output').hidden=state.mode!=='pretty' || state.id==='holidays';
  byId('csv-output').hidden=state.mode!=='pretty' || state.id!=='holidays';
  byId('map-output').hidden=state.mode!=='map';
  byId('usage-output').hidden=state.mode!=='usage';
  byId('weather-output').hidden=state.mode!=='weather';
  const weatherButton=document.querySelector('[data-view="weather"]');weatherButton.hidden=state.id!=='weather';weatherButton.disabled=!hasData;
  if(state.mode==='weather')renderWeather();
  if(state.mode==='usage') { if(state.id==='books')renderBooksUsage(); else if(state.id==='players')renderPlayerSearch(); else if(state.id==='sports')renderSportsUsage(); else if(state.id==='music')renderMusicUsage(); else renderPokemonUsage(); }
  byId('color-control').hidden=state.mode!=='pretty' || state.id==='holidays';
  document.querySelectorAll('[data-view]').forEach(button=>{button.setAttribute('aria-pressed',String(button.dataset.view===state.mode)); if(['map','usage'].includes(button.dataset.view))button.disabled=!hasData || (!usage && !state.dataset.map);});
  byId('raw-output').querySelector('code').textContent=state.raw;
  byId('coordinate-note').textContent=textFor(state.dataset.map_note);
  if(state.id==='lapd') {const link=document.createElement('a');link.href='https://data.lacity.org/Public-Safety/LAPD-NIBRS-Offenses-Dataset/k7nn-b2ep';link.target='_blank';link.rel='noopener';link.textContent=textFor({ja:' 座標の照合元：Offenses ↗',en:' Coordinate source: Offenses ↗'});byId('coordinate-note').append(link);}
  if(!hasData) {byId('pretty-output').querySelector('code').textContent=''; byId('csv-output').replaceChildren(); return;}
  if(state.id==='holidays')csvTable(); else jsonColors(JSON.stringify(state.data,null,2));
  if(state.mode==='map')mapView();
}
function renderWeather() {
  const host=byId('weather-output');host.replaceChildren();if(!state.data)return;
  const data=state.data,url=new URL(state.url),lat=Number(url.searchParams.get('latitude')),lon=Number(url.searchParams.get('longitude'));
  const place=Object.values(weatherPlaces).find(p=>Math.abs(p.lat-lat)<.00001 && Math.abs(p.lon-lon)<.00001);
  const heading=document.createElement('div');heading.className='weather-summary';
  const location=document.createElement('div'),title=document.createElement('h3'),coords=document.createElement('p');
  title.textContent=place?place[locale()]:textFor({ja:'指定した地点',en:'Custom location'});
  coords.className='subtle';coords.textContent=lat.toFixed(2)+', '+lon.toFixed(2)+' · '+(data.timezone||'');location.append(title,coords);
  const current=document.createElement('div'),temp=document.createElement('strong'),at=document.createElement('p');
  temp.textContent=Number.isFinite(data.current?.temperature_2m)?data.current.temperature_2m+' '+(data.current_units?.temperature_2m||'°C'):'—';
  at.textContent=textFor({ja:'現在のモデル値 · ',en:'Current model value · '})+(data.current?.time||'—').replace('T',' ');current.append(temp,at);heading.append(location,current);
  const titleChart=document.createElement('h4');titleChart.textContent=textFor({ja:'時間ごとの気温予報',en:'Hourly temperature forecast'});
  const times=data.hourly?.time||[],temps=data.hourly?.temperature_2m||[];
  const points=times.map((time,i)=>({time,temp:temps[i],i})).filter(p=>typeof p.temp==='number' && Number.isFinite(p.temp));
  host.append(heading,titleChart);
  if(!points.length){const empty=document.createElement('p');empty.textContent=textFor({ja:'表示できる時間別気温がありません。',en:'No hourly temperatures available.'});host.append(empty);return;}
  const width=760,height=290,left=48,right=22,top=18,bottom=48;
  const min=Math.floor(Math.min(...points.map(p=>p.temp))-1),max=Math.ceil(Math.max(...points.map(p=>p.temp))+1);
  const x=i=>left+i/Math.max(1,times.length-1)*(width-left-right),y=t=>height-bottom-(t-min)/(max-min)*(height-top-bottom);
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 '+width+' '+height);svg.setAttribute('role','img');svg.setAttribute('aria-label',textFor({ja:'時間と気温の折れ線グラフ。下のスライダーで値を確認できます。',en:'Temperature versus time. Use the slider below to read values.'}));
  const el=(tag,attrs,text)=>{const n=document.createElementNS(svg.namespaceURI,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));if(text!==undefined)n.textContent=text;svg.append(n);return n;};
  for(let i=0;i<=4;i++){const value=min+(max-min)*i/4;el('line',{x1:left,x2:width-right,y1:y(value),y2:y(value),class:'weather-grid'});el('text',{x:left-10,y:y(value)+4,'text-anchor':'end'},Math.round(value)+'°');}
  const tickCount=Math.min(5,times.length);
  for(let i=0;i<tickCount;i++){const index=Math.round(i/Math.max(1,tickCount-1)*(times.length-1));el('text',{x:x(index),y:height-22,'text-anchor':i===0?'start':i===tickCount-1?'end':'middle'},times[index].slice(5).replace('T',' '));}
  let segment=[];const flush=()=>{if(segment.length)el('polyline',{points:segment.join(' '),class:'weather-line'});segment=[];};
  times.forEach((_,i)=>{if(typeof temps[i]==='number' && Number.isFinite(temps[i]))segment.push(x(i)+','+y(temps[i]));else flush();});flush();
  const cursor=el('line',{x1:x(0),x2:x(0),y1:top,y2:height-bottom,class:'weather-cursor'}),dot=el('circle',{cx:0,cy:0,r:5,class:'weather-dot'});
  const label=document.createElement('label');label.className='weather-hour';const readout=document.createElement('output'),slider=document.createElement('input');slider.type='range';slider.min=0;slider.max=times.length-1;slider.step=1;slider.setAttribute('aria-label',textFor({ja:'予報の時間を選ぶ',en:'Select forecast hour'}));
  const select=index=>{slider.value=index;const t=temps[index];readout.textContent=times[index].replace('T',' ')+' · '+(typeof t==='number' && Number.isFinite(t)?t+' '+(data.hourly_units?.temperature_2m||'°C'):textFor({ja:'欠損',en:'Missing'}));slider.setAttribute('aria-valuetext',readout.textContent);cursor.setAttribute('x1',x(index));cursor.setAttribute('x2',x(index));dot.setAttribute('cx',x(index));dot.setAttribute('cy',Number.isFinite(t)?y(t):0);dot.setAttribute('visibility',typeof t==='number' && Number.isFinite(t)?'visible':'hidden');};
  slider.addEventListener('input',()=>select(Number(slider.value)));
  svg.addEventListener('pointermove',event=>{const rect=svg.getBoundingClientRect();select(Math.max(0,Math.min(times.length-1,Math.round(((event.clientX-rect.left)/rect.width*width-left)/(width-left-right)*(times.length-1)))));});
  const nowIndex=times.findIndex(time=>time>=data.current?.time);select(nowIndex>=0?nowIndex:0);label.append(readout,slider);host.append(svg,label);
  const note=document.createElement('p');note.className='subtle';note.textContent=textFor({ja:'時刻は地点の現地時間。予報・現在値は気象モデルの値で、観測値とは限りません。地名は選択した座標のラベルです。',en:'Times use the location’s timezone. Forecast/current values are model data, not necessarily observations. The location name labels the selected coordinates.'});host.append(note);
}
function renderPokemonUsage() {
  byId('usage-output').setAttribute('aria-label','Pokémon usage example');
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
function renderMusicUsage() {
  const host=byId('usage-output');
  host.replaceChildren();
  host.setAttribute('aria-label',textFor({ja:'音楽データの使用例',en:'Music data usage example'}));
  if(!state.data)return;
  const songs=(state.data?.results||[]).filter(song=>song.kind==='song');
  if(!songs.length) {
    const note=document.createElement('p');
    note.textContent=textFor({ja:'曲が見つかりません。別の曲名で検索してみよう。',en:'No songs found. Try another song title.'});
    host.append(note);return;
  }
  const grid=document.createElement('div');grid.className='music-results';
  songs.forEach(song=>{
    const card=document.createElement('article');card.className='music-result';
    const image=document.createElement('img');
    try {
      const artwork=new URL(song.artworkUrl100);
      if(artwork.protocol==='https:' && artwork.hostname.endsWith('.mzstatic.com')) {
        image.src=artwork.href;image.alt='';image.loading='lazy';image.width=100;image.height=100;card.append(image);
      }
    } catch (_) {}
    const details=document.createElement('div');
    const title=document.createElement('h3');title.textContent=song.trackName;
    const artist=document.createElement('p');artist.textContent=song.artistName;
    const album=document.createElement('p');album.className='subtle';album.textContent=song.collectionName;
    details.append(title,artist,album);
    try {
      const url=new URL(song.trackViewUrl);
      if(url.protocol==='https:' && ['music.apple.com','itunes.apple.com'].includes(url.hostname)) {
        const link=document.createElement('a');link.href=url.href;link.target='_blank';link.rel='noopener';
        link.textContent=textFor({ja:'Apple Musicで試聴 ↗',en:'Listen on Apple Music ↗'});
        details.append(link);
      }
    } catch (_) {}
    card.append(details);grid.append(card);
  });
  host.append(grid);
  const note=document.createElement('p');note.className='subtle';
  note.textContent=textFor({ja:'resultsはリスト、一曲は辞書。trackNameが曲名、artistNameが歌手、trackViewUrlが試聴ページへのリンク。試聴の提供状況は地域や曲によって異なります。',en:'results is a list; each song is a dictionary. trackName gives the title, artistName the artist, and trackViewUrl the listening page. Preview availability varies by region and song.'});
  host.append(note);
}
function renderSportsUsage() {
  const host=byId('usage-output');host.replaceChildren();
  host.setAttribute('aria-label',textFor({ja:'ESPNスコアボード',en:'ESPN scoreboard'}));
  if(!state.data)return;
  const data=state.data;
  const playoffs=!state.source?.saved && values().league==='mlbPlayoffs';
  const events=(data.events||[]).filter(event=>!playoffs || Number(event.season?.type||data.season?.type)===3);
  const heading=document.createElement('h3');heading.textContent=(data.leagues?.[0]?.name||'ESPN')+(playoffs?' · Playoffs':'');
  const date=document.createElement('p');date.className='subtle';
  date.textContent=textFor({ja:'配信対象日：',en:'Feed date: '})+(data.day?.date||textFor({ja:'各試合の日時を参照',en:'See each game'}));
  host.append(heading,date);
  if(!events.length) {
    const empty=document.createElement('p');empty.textContent=textFor({ja:playoffs?'この応答にプレーオフの試合はありません。別の日付を選んでください。':'この応答に試合はありません。別の日付を選んでください。',en:'No games in this response. Try another date.'});host.append(empty);return;
  }
  const grid=document.createElement('div');grid.className='sports-results';
  events.forEach(event=>{
    const competition=event.competitions?.[0];if(!competition)return;
    const card=document.createElement('article');card.className='sports-game';
    const status=competition.status||event.status||{};
    const line=document.createElement('p');line.className='sports-status';line.dataset.state=status.type?.state||'pre';
    const label=status.type?.state==='in'?textFor({ja:'試合中',en:'LIVE'}):status.type?.completed?textFor({ja:'終了',en:'FINAL'}):status.type?.description||textFor({ja:'予定',en:'Scheduled'});
    const detail=status.type?.shortDetail||status.type?.detail||'';
    line.textContent=label+(detail && detail!==label?' · '+detail:'');card.append(line);
    [...(competition.competitors||[])].sort((a,b)=>a.homeAway==='away'?-1:b.homeAway==='away'?1:0).forEach(team=>{
      const row=document.createElement('div');row.className='sports-team';if(team.winner)row.classList.add('is-winner');
      const name=document.createElement('span');name.textContent=team.team?.displayName||team.team?.name||'Team';
      const score=document.createElement('strong');score.textContent=status.type?.state==='pre'?'—':String(team.score??'—');
      row.append(name,score);card.append(row);
    });
    const at=new Date(event.date);const time=document.createElement('p');time.className='subtle';
    time.textContent=Number.isNaN(at.getTime())?'':at.toLocaleString(locale()==='ja'?'ja-JP':'en-US',{timeZone:'Asia/Tokyo',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})+' JST';card.append(time);
    const note=competition.series?.summary||competition.notes?.[0]?.headline;
    if(note){const p=document.createElement('p');p.className='subtle';p.textContent=note;card.append(p);}
    const href=event.links?.find(link=>link.rel?.includes('summary'))?.href||event.links?.[0]?.href;
    try{const url=new URL(href);if(url.protocol==='https:'&&(url.hostname==='espn.com'||url.hostname.endsWith('.espn.com'))){const a=document.createElement('a');a.href=url.href;a.target='_blank';a.rel='noopener';a.textContent=textFor({ja:'ESPNで試合を見る ↗',en:'Game details on ESPN ↗'});card.append(a);}}catch(_){}
    grid.append(card);
  });
  host.append(grid);
}
const playerProfiles=new Map();
let playerSelection=0;
function renderPlayerSearch() {
  const host=byId('usage-output');host.replaceChildren();
  host.setAttribute('aria-label',textFor({ja:'選手検索とプロフィール',en:'Player search and bio'}));
  if(!state.data)return;
  const players=(state.data.items||[]).filter(player=>player.type==='player');
  if(!players.length){const p=document.createElement('p');p.textContent=textFor({ja:'選手が見つかりません。英字の名前で検索してみよう。',en:'No players found. Try the name in English.'});host.append(p);return;}
  const label=document.createElement('label');label.className='player-picker';
  const caption=document.createElement('span');caption.textContent=textFor({ja:'検索結果から選ぶ',en:'Choose a player'});
  const select=document.createElement('select');
  players.forEach((player,index)=>{const option=document.createElement('option');option.value=index;option.textContent=player.displayName+' · '+(player.label||player.league||'');select.append(option);});
  label.append(caption,select);
  const bio=document.createElement('section');bio.className='player-bio';bio.setAttribute('aria-live','polite');
  host.append(label,bio);
  select.addEventListener('change',()=>loadPlayerBio(players[Number(select.value)],bio));
  loadPlayerBio(players[0],bio);
}
async function loadPlayerBio(player,host) {
  const selection=++playerSelection,token=state.token,saved=state.source?.saved;
  host.textContent=textFor({ja:'プロフィールを取得中…',en:'Loading player bio…'});
  if(!/^[a-z0-9.-]+$/i.test(player.sport||'') || !/^[a-z0-9.-]+$/i.test(player.league||'') || !/^\d+$/.test(player.id||''))return;
  const url='https://site.api.espn.com/apis/common/v3/sports/'+player.sport+'/'+player.league+'/athletes/'+player.id;
  let data=null,error=false;
  try{
    const key=saved?'saved-'+player.id:url;
    if(playerProfiles.has(key))data=playerProfiles.get(key);
    else {
      const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),12000);
      try {
        const response=await fetch(saved && player.id==='39832'?'weeks/week-03/explore-data/player-bio.json':url,{signal:controller.signal,credentials:'omit'});
        if(!response.ok)throw new Error('Profile unavailable');
        data=await response.json();playerProfiles.set(key,data);
      } finally {clearTimeout(timer);}
    }
  }catch(_){error=true;}
  if(selection!==playerSelection || token!==state.token || !host.isConnected)return;
  host.replaceChildren();
  const athlete=data?.athlete||player,team=athlete.team?.displayName||player.teamRelationships?.[0]?.displayName;
  const header=document.createElement('div');header.className='player-bio-header';
  try {const url=new URL(athlete.headshot?.href||player.headshot?.href);if(url.protocol==='https:'&&url.hostname==='a.espncdn.com'){const image=document.createElement('img');image.src=url.href;image.alt=athlete.displayName;header.append(image);}}catch(_){}
  const intro=document.createElement('div'),title=document.createElement('h3');title.textContent=athlete.displayName;
  const summary=document.createElement('p');summary.textContent=[team,athlete.position?.displayName||athlete.position?.name,athlete.jersey?'#'+athlete.jersey:null].filter(Boolean).join(' · ');
  intro.append(title,summary);header.append(intro);host.append(header);
  const facts=document.createElement('dl');facts.className='player-bio-facts';
  const birth=athlete.birthPlace;
  const birthplace=typeof birth==='string'?birth:[birth?.city,birth?.state,birth?.country].filter(Boolean).join(', ');
  const rows=[
    [{ja:'年齢',en:'Age'},athlete.age],
    [{ja:'生年月日',en:'Born'},athlete.dateOfBirth?.split('T')[0]],
    [{ja:'出身地',en:'Birthplace'},birthplace],
    [{ja:'身長',en:'Height'},athlete.displayHeight],
    [{ja:'体重',en:'Weight'},athlete.displayWeight],
    [{ja:'デビュー年',en:'Debut year'},athlete.debutYear],
    [{ja:'リーグ',en:'League'},player.league?.toUpperCase()]
  ];
  rows.forEach(([label,value])=>{if(value===undefined||value===null||value==='')return;const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=textFor(label);dd.textContent=String(value);facts.append(dt,dd);});host.append(facts);
  const note=document.createElement('p');note.className='subtle';note.textContent=textFor(error?{ja:'詳細を取得できないため、検索結果にある情報のみ表示しています。',en:'Profile request failed; showing available search fields only.'}:saved?{ja:'保存プロフィール · 2026-10-15取得。現在の所属や年齢とは異なる場合があります。',en:'Saved profile retrieved 2026-10-15; team or age may have changed.'}:{ja:'ESPNの応答にある項目のみ表示。未提供の情報は省略しています。',en:'Only fields supplied by ESPN are shown; unavailable details are omitted.'});host.append(note);
  const profileLink=(athlete.links||player.links||[]).find(link=>link.rel?.includes('bio')&&link.href?.startsWith('https://www.espn.com/'))||(player.links||[]).find(link=>link.href?.startsWith('https://www.espn.com/'));
  if(profileLink){const a=document.createElement('a');a.href=profileLink.href;a.target='_blank';a.rel='noopener';a.textContent=textFor({ja:'ESPNの選手ページ ↗',en:'Player on ESPN ↗'});host.append(a);}
  const source=document.createElement('details'),heading=document.createElement('summary');heading.textContent=textFor({ja:'プロフィールのAPI・JSON',en:'Profile API & JSON'});source.append(heading);
  const api=document.createElement('a');api.href=url;api.target='_blank';api.rel='noopener';api.textContent=url;source.append(api);
  if(data){const pre=document.createElement('pre'),code=document.createElement('code');code.textContent=JSON.stringify(data.athlete||data,null,2);pre.append(code);source.append(pre);}
  host.append(source);
}
function renderBooksUsage() {
  const host=byId('usage-output');host.replaceChildren();
  host.setAttribute('aria-label',textFor({ja:'本の検索結果',en:'Book results'}));
  if(!state.data)return;
  const books=state.data.items||[];
  if(!books.length) {
    const note=document.createElement('p');note.textContent=textFor({ja:'本が見つかりません。検索語を変えてみよう。',en:'No books found. Try another search.'});host.append(note);return;
  }
  const grid=document.createElement('div');grid.className='book-results';
  books.forEach(book=>{
    const info=book.volumeInfo||{};
    const card=document.createElement('article');card.className='book-result';
    const cover=document.createElement('div');cover.className='book-cover';
    const missing=()=>{cover.replaceChildren();const label=document.createElement('span');label.textContent=textFor({ja:'表紙なし',en:'No cover'});cover.append(label);};
    missing();
    try {
      const imageURL=new URL(info.imageLinks?.thumbnail||info.imageLinks?.smallThumbnail);
      if(['http:','https:'].includes(imageURL.protocol) && /^(books\.google\.(com|co\.jp)|books\.googleusercontent\.com)$/.test(imageURL.hostname)) {
        imageURL.protocol='https:';
        const image=document.createElement('img');image.src=imageURL.href;image.alt=info.title||'';image.loading='lazy';image.addEventListener('error',missing,{once:true});cover.replaceChildren(image);
      }
    }catch(_){}
    const details=document.createElement('div');
    const title=document.createElement('h3');title.textContent=info.title||textFor({ja:'タイトル不明',en:'Untitled'});
    const author=document.createElement('p');author.className='book-author';author.textContent=(info.authors||[]).join(' / ')||textFor({ja:'著者情報なし',en:'Author unavailable'});
    details.append(title,author);
    const facts=document.createElement('p');facts.className='subtle';
    facts.textContent=[info.publisher,info.publishedDate,info.pageCount?info.pageCount+textFor({ja:'ページ',en:' pages'}):null,info.language].filter(Boolean).join(' · ');details.append(facts);
    const isbn=(info.industryIdentifiers||[]).find(id=>id.type==='ISBN_13');
    if(isbn){const p=document.createElement('p');p.className='subtle';p.textContent='ISBN '+isbn.identifier;details.append(p);}
    if(info.description){const p=document.createElement('p');p.className='book-description';p.textContent=(new DOMParser().parseFromString(info.description,'text/html').body.textContent||'').slice(0,240);details.append(p);}
    try {
      const url=new URL(info.infoLink||'https://books.google.com/books?id='+encodeURIComponent(book.id));
      if(['http:','https:'].includes(url.protocol) && /^(books\.google\.(com|co\.jp)|play\.google\.com)$/.test(url.hostname)) {
        url.protocol='https:';const link=document.createElement('a');link.href=url.href;link.target='_blank';link.rel='noopener';link.textContent=textFor({ja:'Google Booksで見る ↗',en:'View on Google Books ↗'});details.append(link);
      }
    }catch(_){}
    card.append(cover,details);grid.append(card);
  });
  host.append(grid);
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
async function fetchData(saved=false,keepFields=false) {
  closeMapPopup();
  controller?.abort(); controller=new AbortController(); const token=++state.token; const dataset=state.dataset;
  const requestController=controller;
  if(saved && !keepFields)renderFields(state.id==='holidays'?values():defaults[state.id]);
  const url=requestURL(state.id,values());
  if(!saved && cache.has(url)) { const record=cache.get(url);lapdLocations=record.locations||[];lapdLocationError=record.locationError||false; response(record.raw,url,false,record.decoded,record.bytes); state.source=record.source; renderStatus(); return; }
  state.raw=''; state.data=null; state.source=null;
  byId('download-data').hidden=true;
  if(state.map?.getSource('records')) state.map.getSource('records').setData({type:'FeatureCollection',features:[]});
  renderViews();
  byId('fetch-data').disabled=true;
  status({ja:saved?'保存例を読み込み中…':'APIに問い合わせ中…',en:saved?'Loading saved example…':'Requesting data…'});
  const timer=setTimeout(()=>requestController.abort(),state.id==='lapd'?45000:15000);
  try {
    let fetchURL=saved?dataset.snapshot:url;
    if(!saved && state.id==='books' && values().apiKey) {
      const authenticated=new URL(url);authenticated.searchParams.set('key',values().apiKey.trim());fetchURL=authenticated.href;
    }
    const res=await fetch(fetchURL,{signal:requestController.signal,credentials:'omit'});
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
    if(saved && state.id==='books' && keepFields) {
      const sample=JSON.parse(raw),query=values().q.replace(/^intitle:/,'');
      sample.items=sample.items.filter(book=>book.volumeInfo.title.includes(query));
      raw=JSON.stringify(sample,null,2);
    }
    if(token!==state.token)return;
    let locations=[],locationError=false;
    if(state.id==='lapd') {try{locations=await victimLocations(JSON.parse(raw),saved,requestController.signal);}catch(error){if(requestController.signal.aborted)throw error;locationError=true;}}
    if(token!==state.token)return;
    lapdLocations=locations;lapdLocationError=locationError;
    response(raw,url,saved,decoded,bytes);
    if(!saved)cache.set(url,{raw,decoded,bytes,locations,locationError,source:state.source});
  } catch(error) {
    if(token!==state.token)return;
    status(state.id==='books'?{ja:'Google Booksを取得できませんでした。APIキー・利用上限を確認するか、「授業用サンプル」を開いてください。',en:'Google Books request failed. Check your API key or quota, or open the classroom sample.'}:{ja:'取得できませんでした（通信・CORS・配信制限）。「保存例を使う」で実データの保存版を開けます。',en:'Request failed (network, CORS, or provider limits). Use saved example to open a real cached response.'},'error');
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
  byId('load-snapshot').querySelector('.lang-ja').textContent=d.classroom_example?'授業用サンプル':'保存例を使う';
  byId('load-snapshot').querySelector('.lang-en').textContent=d.classroom_example?'Classroom sample':'Use saved example';
  byId('raw-link').querySelector('.lang-ja').textContent=d.documentation_example?'仕様書のRaw例':'提供元のRawデータ';
  byId('raw-link').querySelector('.lang-en').textContent=d.documentation_example?'Raw documentation example':'Provider’s raw data';
}
function chooseDataset(id,load=true) {
  closeMapPopup();
  if(id!==state.id)highlightedDescent=null;
  controller?.abort(); ++state.token;
  state.id=id; state.dataset=state.config.datasets[id]; state.raw=''; state.data=null; state.source=null;
  if(!state.dataset.map && state.mode==='map')state.mode='pretty';
  if(state.mode==='usage' && !['pokemon','music','sports','players','books'].includes(id))state.mode='pretty';
  if(state.mode==='weather' && id!=='weather')state.mode='pretty';
  if(id==='weather')state.mode='weather';
  if(id==='pokemon')state.mode='usage';
  if(id==='music')state.mode='usage';
  if(id==='sports')state.mode='usage';
  if(id==='players')state.mode='usage';
  if(id==='books')state.mode='usage';
  if(id==='toeiBus')state.mode='map';
  byId('download-data').hidden=true; byId('fetch-data').disabled=false;
  document.querySelectorAll('[data-dataset]').forEach(button=>{
    const active=button.dataset.dataset===id;
    button.setAttribute('aria-selected',String(active)); button.tabIndex=active?0:-1;
    if(active)byId('dataset-panel').setAttribute('aria-labelledby',button.id);
  });
  metadata(); renderFields(); renderViews();
  const url=new URL(location.href); url.searchParams.set('week',String(state.week.week).padStart(2,'0')); url.searchParams.set('example',id); history.replaceState(null,'',url);
  if(load)fetchData(state.dataset.browser_fetch===false || state.dataset.classroom_example===true);
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
