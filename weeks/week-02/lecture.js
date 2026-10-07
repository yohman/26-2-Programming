const slides = [...document.querySelectorAll('[data-slide]')];
const slideCount = document.getElementById('slide-count');
const slidesView = document.getElementById('slides-view');
const fullscreenButton = document.getElementById('slide-fullscreen');
let slideIndex = 0;
let activeView = 'slides';
let activePlayground = 'markdown';
let activeTopic = 0;
let lastExplanation = null;
let selectedMarkdownExample = 'intro';

const markdownExamples = {
  intro: {
    titleJa:'見出し・文章・リスト', titleEn:'Heading, sentence + list',
    ja: '# はじめてのNotebook\n今日やること：\n- Cellをつくる\n- 結果を見る',
    en: '# My first notebook\nToday I will:\n- Add a cell\n- Check the result'
  },
  emphasis: {
    titleJa:'強調とコード', titleEn:'Emphasis + inline code',
    ja: 'これは **大事な結果** です。\nこの行は *少し強調* します。\n`print()` はコードの名前です。',
    en: 'This is an **important result**.\nThis is *slightly emphasized*.\n`print()` is the name of a function.'
  },
  list: {
    titleJa:'箇条書き', titleEn:'Bullet list',
    ja: '## 実行する前に\n- 結果を予想する\n- Code Cellを実行する\n- 出力を確かめる',
    en: '## Before running\n- Predict the result\n- Run the Code cell\n- Check the output'
  },
  steps: {
    titleJa:'番号付き手順', titleEn:'Numbered steps',
    ja: '## Notebookを動かす\n1. Kernelを選ぶ\n2. Code Cellを実行する\n3. 出力を確認する',
    en: '## Run the notebook\n1. Select a kernel\n2. Run the Code cell\n3. Check the output'
  },
  link: {
    titleJa:'リンク', titleEn:'Link',
    ja: '資料：[Jupyterの公式サイト](https://jupyter.org/)\nあとで読み返せるように残す。',
    en: 'Resource: [Jupyter’s website](https://jupyter.org/)\nKeep the source for later.'
  },
  quote: {
    titleJa:'引用・メモ', titleEn:'Quote or note',
    ja: '> Aha! `"5"` は文字、`5` は数字。',
    en: '> Aha! `"5"` is text; `5` is a number.'
  },
  reflection: {
    titleJa:'観察メモ', titleEn:'Observation note',
    ja: '## 気づいたこと\n**予想：** 5 + 2 は 7。\n\n**結果：** 7 が表示された。\n\n**次に試す：** 数を変えてみる。',
    en: '## What I noticed\n**Prediction:** 5 + 2 will be 7.\n\n**Result:** The output was 7.\n\n**Next:** Change one number.'
  }
};

function appendMarkdownInline(parent, source) {
  const parts = source.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\(https?:\/\/[^\s)]+\))/g);
  parts.forEach(part => {
    let element;
    if (/^\*\*[^*]+\*\*$/.test(part)) {
      element = document.createElement('strong'); element.textContent = part.slice(2, -2);
    } else if (/^\*[^*]+\*$/.test(part)) {
      element = document.createElement('em'); element.textContent = part.slice(1, -1);
    } else if (/^`[^`]+`$/.test(part)) {
      element = document.createElement('code'); element.textContent = part.slice(1, -1);
    } else {
      const link = part.match(/^\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)$/);
      if (link) {
        element = document.createElement('a'); element.href = link[2]; element.textContent = link[1];
        element.target = '_blank'; element.rel = 'noopener noreferrer';
      }
    }
    parent.append(element || document.createTextNode(part));
  });
}

function renderMarkdownInto(preview, source) {
  preview.replaceChildren();
  let list = null;
  let paragraph = null;
  source.split(/\r?\n/).forEach(line => {
    if (!line.trim()) { list = null; paragraph = null; return; }
    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    const bullet = line.match(/^\s*[-*]\s+(.+)$/);
    const numbered = line.match(/^\s*\d+\.\s+(.+)$/);
    if (heading) {
      list = null;
      paragraph = null;
      const element = document.createElement(`h${heading[1].length}`);
      appendMarkdownInline(element, heading[2]); preview.append(element);
    } else if (bullet || numbered) {
      paragraph = null;
      const type = bullet ? 'ul' : 'ol';
      if (!list || list.tagName.toLowerCase() !== type) {
        list = document.createElement(type); preview.append(list);
      }
      const item = document.createElement('li');
      appendMarkdownInline(item, (bullet || numbered)[1]); list.append(item);
    } else if (line.startsWith('> ')) {
      list = null;
      paragraph = null;
      const element = document.createElement('blockquote');
      appendMarkdownInline(element, line.slice(2)); preview.append(element);
    } else {
      list = null;
      if (!paragraph) {
        paragraph = document.createElement('p'); preview.append(paragraph);
      } else {
        paragraph.append(document.createTextNode(' '));
      }
      appendMarkdownInline(paragraph, line);
    }
  });
}

function renderMarkdown() {
  renderMarkdownInto(document.getElementById('markdown-preview'), document.getElementById('markdown-input').value);
}

function renderMarkdownExamples() {
  const root = document.getElementById('markdown-examples');
  const locale = language();
  root.replaceChildren();
  Object.entries(markdownExamples).forEach(([key, example], index) => {
    const card = document.createElement('article'); card.className = 'markdown-example'; card.dataset.example = key;
    const header = document.createElement('header');
    const title = document.createElement('h3'); title.textContent = `${String(index + 1).padStart(2, '0')}  ${locale === 'ja' ? example.titleJa : example.titleEn}`;
    const button = document.createElement('button'); button.type = 'button'; button.dataset.markdownExample = key;
    button.textContent = locale === 'ja' ? '編集して試す →' : 'Try in editor →';
    button.setAttribute('aria-expanded', 'false');
    header.append(title, button);
    const pair = document.createElement('div'); pair.className = 'markdown-example-pair';
    const sourceBox = document.createElement('div'); sourceBox.className = 'markdown-example-source';
    const sourceLabel = document.createElement('small'); sourceLabel.textContent = 'MARKDOWN';
    const sourcePre = document.createElement('pre'); sourcePre.textContent = example[locale];
    sourceBox.append(sourceLabel, sourcePre);
    const resultBox = document.createElement('div'); resultBox.className = 'markdown-example-result';
    const resultLabel = document.createElement('small'); resultLabel.textContent = locale === 'ja' ? '表示結果' : 'RENDERED';
    const resultContent = document.createElement('div'); resultContent.className = 'markdown-preview-content';
    renderMarkdownInto(resultContent, example[locale]);
    resultBox.append(resultLabel, resultContent);
    pair.append(sourceBox, resultBox); card.append(header, pair); root.append(card);
  });
}

function showMarkdownExample(key) {
  const card = document.querySelector(`[data-example="${key}"]`);
  const button = card.querySelector('[data-markdown-example]');
  let editor = card.querySelector('textarea');
  if (!editor) {
    const source = card.querySelector('.markdown-example-source pre');
    editor = document.createElement('textarea');
    editor.value = source.textContent;
    editor.rows = Math.max(5, editor.value.split('\n').length + 1);
    editor.setAttribute('aria-label', `${language() === 'ja' ? 'Markdownを編集：' : 'Edit Markdown: '}${card.querySelector('h3').textContent}`);
    editor.spellcheck = false;
    editor.addEventListener('input', () => renderMarkdownInto(card.querySelector('.markdown-preview-content'), editor.value));
    source.replaceWith(editor);
    button.classList.add('is-selected');
    button.setAttribute('aria-expanded', 'true');
  }
  editor.focus({preventScroll: true});
}

const string = value => JSON.stringify(String(value));
const number = value => Number(value);
const cleanNumbers = value => String(value).split(',').map(part => Number(part.trim()));
const result = (code, output, ja, en) => ({ code, output, ja, en });

const topics = [
  {
    ja:'print と文字', en:'print and text',
    inputs:[{ key:'message', ja:'表示する言葉', en:'Text to print', value:'Hello, Week 02!' }],
    run:({ message }) => result(`print(${string(message)})`, message, '引用符の中は文字列。print()がその中身を表示します。', 'Quotation marks make a string. print() displays its contents.')
  },
  {
    ja:'計算', en:'Arithmetic',
    inputs:[{ key:'a', ja:'数A', en:'Number A', value:'12', type:'number' },{ key:'operator', ja:'演算', en:'Operation', value:'+', options:['+','-','*','/'] },{ key:'b', ja:'数B', en:'Number B', value:'5', type:'number' }],
    run:({ a, operator, b }) => {
      const left=number(a), right=number(b);
      const code=`print(${left} ${operator} ${right})`;
      if (operator==='/' && right===0) return result(code,'ZeroDivisionError: division by zero','0では割れません。エラーも大切な結果です。','Division by zero raises an error. Errors are results worth reading.');
      const value={'+':left+right,'-':left-right,'*':left*right,'/':left/right}[operator];
      return result(code,String(value),'数値なら、Pythonは式を計算します。','With numbers, Python evaluates the expression.');
    }
  },
  {
    ja:'変数', en:'Variables',
    inputs:[{ key:'score', ja:'最初の点数', en:'Starting score', value:'70', type:'number' },{ key:'bonus', ja:'追加点', en:'Bonus', value:'5', type:'number' }],
    run:({ score, bonus }) => result(`score = ${number(score)}\nscore = score + ${number(bonus)}\nprint(score)`,String(number(score)+number(bonus)),'同じ変数名に、新しく計算した値を保存します。','The variable name now holds the newly calculated value.')
  },
  {
    ja:'int と float', en:'int and float',
    inputs:[{ key:'kind', ja:'数の書き方', en:'Write the number as', value:'int', options:[['int','3 · int'],['float','3.0 · float']] }],
    run:({ kind }) => {
      const decimal=kind==='float';
      return result(`value = ${decimal?'3.0':'3'}\nprint(type(value))\nprint(value + 1)`,decimal?"<class 'float'>\n4.0":"<class 'int'>\n4",'小数点があるとfloat。計算後もfloatとして表示されます。','A decimal point makes a float. The result stays a float.');
    }
  },
  {
    ja:'input と型変換', en:'Input and conversion',
    inputs:[{ key:'years', ja:'何年後？', en:'How many years?', value:'5' }],
    run:({ years }) => {
      const code=`years = input("何年後？ ")\nprint(type(years))\nprint(2026 + int(years))`;
      if (!/^[+-]?\d+$/.test(years.trim())) return result(code,`<class 'str'>\nValueError: invalid literal for int()`, 'input()は文字を返します。整数に変換できない文字はValueErrorです。', 'input() returns text. Text that cannot become an integer raises ValueError.');
      return result(code,`<class 'str'>\n${2026+Number(years)}`, 'input()の結果は文字。int()で整数に変えてから足します。', 'input() returns text. int() converts it before adding.');
    }
  },
  {
    ja:'f文字列', en:'f-strings',
    inputs:[{ key:'name', ja:'名前', en:'Name', value:'Aoi' },{ key:'years', ja:'何年後？', en:'Years ahead', value:'5', type:'number' }],
    run:({ name, years }) => result(`name = ${string(name)}\nyears = ${number(years)}\nprint(f"{name}へ。{2026 + years}年の私より。")`,`${name}へ。${2026+number(years)}年の私より。`,'f文字列の{ }には変数や計算した結果を入れられます。','The { } in an f-string can contain a variable or expression.')
  },
  {
    ja:'データ型', en:'Data types',
    inputs:[{ key:'kind', ja:'値の種類', en:'Choose a value', value:'text', options:[['text','"5" · str'],['int','5 · int'],['float','5.0 · float'],['list','[2, 4, 6] · list'],['dict','{"mag": 4.2} · dict']] }],
    run:({ kind }) => {
      const examples={text:['"5"','str'],int:['5','int'],float:['5.0','float'],list:['[2, 4, 6]','list'],dict:['{"mag": 4.2}','dict']};
      const [value,type]=examples[kind];
      return result(`value = ${value}\nprint(type(value))`,`<class '${type}'>`,'見た目だけでは型は決まりません。引用符と記号を見てください。','Appearance alone does not determine type. Look at quotes and brackets.');
    }
  },
  {
    ja:'リストと配列', en:'Lists and arrays',
    inputs:[{ key:'values', ja:'数値（カンマ区切り）', en:'Numbers, comma-separated', value:'1, 2, 3' }],
    run:({ values }) => {
      const items=cleanNumbers(values);
      if (!items.length || items.some(item=>!Number.isFinite(item))) return result('# 1, 2, 3 のように入力してください','ValueError','数をカンマで区切って入力してください。','Enter numbers separated by commas.');
      const list=JSON.stringify(items);
      const array=`[${items.map(item=>item*2).join(' ')}]`;
      return result(`scores = ${list}\nprint(scores + scores)\n\nimport numpy as np\narray = np.array(scores)\nprint(array + array)`,`${JSON.stringify([...items,...items])}\n${array}`,'リストの+は連結。NumPy配列の+は各要素の計算です。配列の実行にはNumPyが必要です。','List + concatenates. NumPy array + adds each element. NumPy must be installed to run this in a notebook.');
    }
  },
  {
    ja:'辞書とオブジェクト', en:'Dictionaries and objects',
    inputs:[{ key:'place', ja:'場所', en:'Place', value:'Tokyo' },{ key:'mag', ja:'マグニチュード', en:'Magnitude', value:'4.2', type:'number' },{ key:'lat', ja:'緯度', en:'Latitude', value:'35.68', type:'number' },{ key:'lon', ja:'経度', en:'Longitude', value:'139.69', type:'number' }],
    run:({ place, mag, lat, lon }) => result(`quake = {\n    "place": ${string(place)},\n    "mag": ${number(mag)},\n    "latitude": ${number(lat)},\n    "longitude": ${number(lon)}\n}\nprint(quake["place"])\nprint(quake["mag"])\nprint(quake["latitude"], quake["longitude"])`,`${place}\n${number(mag)}\n${number(lat)} ${number(lon)}`,'辞書は場所・大きさ・緯度・経度を名前で取り出せます。','A dictionary lets us retrieve place, magnitude, latitude, and longitude by name.')
  }
];

function language() { return document.documentElement.dataset.language || 'ja'; }
function setLanguage(value) {
  const previous = language();
  const markdownInput = document.getElementById('markdown-input');
  const swapExample = !markdownInput.value || markdownInput.value === markdownExamples[selectedMarkdownExample][previous];
  document.documentElement.dataset.language=value;
  document.documentElement.lang=value;
  localStorage.setItem('programming-language',value);
  const toggle=document.getElementById('language-toggle');
  toggle.textContent=value==='ja'?'EN':'日本語';
  toggle.setAttribute('aria-label',value==='ja'?'Switch to English':'日本語に切り替える');
  if (lastExplanation) document.getElementById('playground-explanation').textContent=lastExplanation[value];
  if (swapExample) {
    markdownInput.value = markdownExamples[selectedMarkdownExample][value];
    renderMarkdown();
  }
  renderMarkdownExamples();
  document.querySelectorAll('#python-topic-select option').forEach(option => {
    option.textContent = topics[Number(option.value)][value];
  });
}

function showSlide(index) {
  slideIndex=Math.max(0,Math.min(index,slides.length-1));
  slides.forEach((slide,i)=>{ slide.hidden=i!==slideIndex; slide.classList.toggle('is-active',i===slideIndex); });
  slideCount.textContent=`${String(slideIndex+1).padStart(2,'0')} / ${String(slides.length).padStart(2,'0')}`;
  document.getElementById('previous-slide').disabled=slideIndex===0;
  document.getElementById('next-slide').disabled=slideIndex===slides.length-1;
}

function updateFullscreenControl() {
  const active=document.fullscreenElement===slidesView || slidesView.classList.contains('is-fullscreen-fallback');
  fullscreenButton.setAttribute('aria-pressed',String(active));
  fullscreenButton.querySelector('[data-fullscreen-enter]').hidden=active;
  fullscreenButton.querySelector('[data-fullscreen-exit]').hidden=!active;
}

async function toggleSlidesFullscreen() {
  if (document.fullscreenElement===slidesView) {
    await document.exitFullscreen();
  } else if (slidesView.classList.contains('is-fullscreen-fallback')) {
    slidesView.classList.remove('is-fullscreen-fallback');
    updateFullscreenControl();
  } else {
    try {
      if (!slidesView.requestFullscreen) throw new Error('Fullscreen API unavailable');
      await slidesView.requestFullscreen();
    } catch (_) {
      slidesView.classList.add('is-fullscreen-fallback');
      updateFullscreenControl();
    }
  }
}

function showView(view) {
  activeView=view;
  document.getElementById('slides-view').hidden=view!=='slides';
  document.getElementById('playground-view').hidden=view!=='playground';
  document.querySelectorAll('[data-lecture-destination]').forEach(link => {
    if (link.dataset.lectureDestination === view) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });
  document.querySelectorAll('[data-view]').forEach(button=>{
    const selected=button.dataset.view===view;
    button.classList.toggle('is-selected',selected);
    button.setAttribute('aria-selected',String(selected));
  });
  history.replaceState({},'',view==='playground'?`#playground-${activePlayground}`:location.pathname+location.search);
}

function showPlayground(kind) {
  activePlayground=kind;
  document.getElementById('markdown-playground').hidden=kind!=='markdown';
  document.getElementById('python-playground').hidden=kind!=='python';
  document.querySelectorAll('[data-playground]').forEach(button=>{
    const selected=button.dataset.playground===kind;
    button.classList.toggle('is-selected',selected);
    button.setAttribute('aria-selected',String(selected));
    button.tabIndex=selected?0:-1;
  });
  if (activeView==='playground') history.replaceState({},'',`#playground-${kind}`);
}

function renderTopic(index) {
  activeTopic=index;
  document.getElementById('python-topic-select').value=String(index);
  document.querySelectorAll('[data-topic]').forEach((button,i)=>{
    button.classList.toggle('is-selected',i===index);
    button.setAttribute('aria-current',i===index?'true':'false');
  });
  const controls=document.getElementById('playground-controls');
  controls.replaceChildren();
  topics[index].inputs.forEach(input=>{
    const label=document.createElement('label');
    const ja=document.createElement('span'); ja.className='ja'; ja.textContent=input.ja;
    const en=document.createElement('span'); en.className='en'; en.textContent=input.en;
    label.append(ja,en);
    let field;
    if (input.options) {
      field=document.createElement('select');
      input.options.forEach(option=>{
        const item=document.createElement('option');
        item.value=Array.isArray(option)?option[0]:option;
        item.textContent=Array.isArray(option)?option[1]:option;
        field.append(item);
      });
    } else {
      field=document.createElement('input');
      field.type=input.type||'text';
      if (field.type==='number') field.step='any';
      field.value=input.value;
    }
    field.dataset.key=input.key;
    label.append(field);
    controls.append(label);
  });
  runTopic();
}

function runTopic() {
  const values=Object.fromEntries([...document.querySelectorAll('#playground-controls [data-key]')].map(field=>[field.dataset.key,field.value]));
  const answer=topics[activeTopic].run(values);
  document.getElementById('playground-code').textContent=answer.code;
  document.getElementById('playground-output').textContent=answer.output;
  lastExplanation=answer;
  document.getElementById('playground-explanation').textContent=answer[language()];
}

const returnParam=new URLSearchParams(location.search).get('return');
if (returnParam) {
  try {
    const candidate=new URL(returnParam,location.href);
    if (candidate.origin===location.origin && /\/(?:index|agenda)\.html$/.test(candidate.pathname)) document.getElementById('lecture-return').href=candidate.href;
  } catch (_) { /* Keep the Week 02 fallback. */ }
}

document.getElementById('language-toggle').addEventListener('click',()=>setLanguage(language()==='ja'?'en':'ja'));
setLanguage(localStorage.getItem('programming-language')==='en'?'en':'ja');
document.querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',()=>showView(button.dataset.view)));
document.querySelectorAll('[data-lecture-destination]').forEach(link => link.addEventListener('click', event => {
  event.preventDefault();
  showView(link.dataset.lectureDestination);
}));
document.querySelectorAll('[data-playground]').forEach(button=>{
  button.addEventListener('click',()=>showPlayground(button.dataset.playground));
  button.addEventListener('keydown',event=>{
    if (!['ArrowLeft','ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    const next=button.dataset.playground==='markdown'?'python':'markdown';
    showPlayground(next);
    document.querySelector(`[data-playground="${next}"]`).focus();
  });
});
document.getElementById('markdown-examples').addEventListener('click',event=>{
  const button=event.target.closest('[data-markdown-example]');
  if (button) showMarkdownExample(button.dataset.markdownExample);
});
document.getElementById('markdown-input').addEventListener('input',()=>{
  document.querySelectorAll('[data-markdown-example]').forEach(button=>{
    button.classList.remove('is-selected');
    button.setAttribute('aria-pressed','false');
  });
  renderMarkdown();
});
document.getElementById('previous-slide').addEventListener('click',()=>showSlide(slideIndex-1));
document.getElementById('next-slide').addEventListener('click',()=>showSlide(slideIndex+1));
const slideStage=document.querySelector('.slide-stage');
let swipeStart=null;
slideStage.addEventListener('touchstart',event=>{
  if (event.touches.length!==1 || event.target.closest('pre, a, button, input, textarea')) return;
  const touch=event.touches[0];
  const bounds=slideStage.getBoundingClientRect();
  if (touch.clientX-bounds.left<24 || bounds.right-touch.clientX<24) return;
  swipeStart={ x:touch.clientX, y:touch.clientY };
},{passive:true});
slideStage.addEventListener('touchend',event=>{
  if (!swipeStart || event.changedTouches.length!==1) return;
  const dx=event.changedTouches[0].clientX-swipeStart.x;
  const dy=event.changedTouches[0].clientY-swipeStart.y;
  swipeStart=null;
  if (Math.abs(dx)<55 || Math.abs(dx)<Math.abs(dy)*1.25) return;
  showSlide(slideIndex+(dx<0?1:-1));
},{passive:true});
slideStage.addEventListener('touchcancel',()=>{ swipeStart=null; },{passive:true});
fullscreenButton.addEventListener('click',toggleSlidesFullscreen);
document.addEventListener('fullscreenchange',updateFullscreenControl);
document.addEventListener('keydown',event=>{
  if (event.key==='Escape' && slidesView.classList.contains('is-fullscreen-fallback')) {
    slidesView.classList.remove('is-fullscreen-fallback');
    updateFullscreenControl();
    return;
  }
  if (activeView!=='slides' || /^(INPUT|TEXTAREA|SELECT)$/.test(event.target.tagName)) return;
  if (event.key==='ArrowRight') showSlide(slideIndex+1);
  if (event.key==='ArrowLeft') showSlide(slideIndex-1);
});
document.getElementById('playground-run').addEventListener('click',runTopic);
document.getElementById('playground-controls').addEventListener('keydown',event=>{ if (event.key==='Enter') runTopic(); });
const topicNav=document.getElementById('playground-topics');
const topicSelect=document.getElementById('python-topic-select');
topicSelect.addEventListener('change',()=>renderTopic(Number(topicSelect.value)));
topics.forEach((topic,index)=>{
  const option=document.createElement('option');
  option.value=String(index);
  option.textContent=topic[language()];
  topicSelect.append(option);
  const button=document.createElement('button');
  button.type='button';
  button.dataset.topic=String(index);
  button.innerHTML=`<span class="ja">${topic.ja}</span><span class="en">${topic.en}</span>`;
  button.addEventListener('click',()=>renderTopic(index));
  topicNav.append(button);
});
showSlide(0);
renderTopic(0);
if (location.hash==='#playground' || location.hash==='#playground-python') showPlayground('python');
if (location.hash.startsWith('#playground')) showView('playground');
else showView('slides');
