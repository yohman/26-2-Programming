const slides = [...document.querySelectorAll('[data-slide]')];
const slideCount = document.getElementById('slide-count');
let slideIndex = 0;
let activeView = 'slides';
let activeTopic = 0;
let lastExplanation = null;

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
    inputs:[{ key:'place', ja:'場所', en:'Place', value:'Tokyo' },{ key:'mag', ja:'マグニチュード', en:'Magnitude', value:'4.2', type:'number' }],
    run:({ place, mag }) => result(`quake = {"place": ${string(place)}, "mag": ${number(mag)}}\nprint(quake["place"])\nprint(quake["mag"])`,`${place}\n${number(mag)}`,'辞書は名前つきの項目をまとめるPythonのオブジェクトです。','A dictionary is a Python object that groups named fields.')
  }
];

function language() { return document.documentElement.dataset.language || 'ja'; }
function setLanguage(value) {
  document.documentElement.dataset.language=value;
  document.documentElement.lang=value;
  localStorage.setItem('programming-language',value);
  const toggle=document.getElementById('language-toggle');
  toggle.textContent=value==='ja'?'EN':'日本語';
  toggle.setAttribute('aria-label',value==='ja'?'Switch to English':'日本語に切り替える');
  if (lastExplanation) document.getElementById('playground-explanation').textContent=lastExplanation[value];
}

function showSlide(index) {
  slideIndex=Math.max(0,Math.min(index,slides.length-1));
  slides.forEach((slide,i)=>{ slide.hidden=i!==slideIndex; slide.classList.toggle('is-active',i===slideIndex); });
  slideCount.textContent=`${String(slideIndex+1).padStart(2,'0')} / ${String(slides.length).padStart(2,'0')}`;
  document.getElementById('previous-slide').disabled=slideIndex===0;
  document.getElementById('next-slide').disabled=slideIndex===slides.length-1;
}

function showView(view) {
  activeView=view;
  document.getElementById('slides-view').hidden=view!=='slides';
  document.getElementById('playground-view').hidden=view!=='playground';
  document.querySelectorAll('[data-view]').forEach(button=>{
    const selected=button.dataset.view===view;
    button.classList.toggle('is-selected',selected);
    button.setAttribute('aria-selected',String(selected));
  });
  history.replaceState({},'',view==='playground'?'#playground':location.pathname+location.search);
}

function renderTopic(index) {
  activeTopic=index;
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
document.getElementById('previous-slide').addEventListener('click',()=>showSlide(slideIndex-1));
document.getElementById('next-slide').addEventListener('click',()=>showSlide(slideIndex+1));
document.addEventListener('keydown',event=>{
  if (activeView!=='slides' || /^(INPUT|TEXTAREA|SELECT)$/.test(event.target.tagName)) return;
  if (event.key==='ArrowRight') showSlide(slideIndex+1);
  if (event.key==='ArrowLeft') showSlide(slideIndex-1);
});
document.getElementById('playground-run').addEventListener('click',runTopic);
document.getElementById('playground-controls').addEventListener('keydown',event=>{ if (event.key==='Enter') runTopic(); });
const topicNav=document.getElementById('playground-topics');
topics.forEach((topic,index)=>{
  const button=document.createElement('button');
  button.type='button';
  button.dataset.topic=String(index);
  button.innerHTML=`<span class="ja">${topic.ja}</span><span class="en">${topic.en}</span>`;
  button.addEventListener('click',()=>renderTopic(index));
  topicNav.append(button);
});
showSlide(0);
renderTopic(0);
if (location.hash==='#playground') showView('playground');
