const slides = [...document.querySelectorAll('[data-slide]')];
const slidesView = document.getElementById('slides-view');
const labView = document.getElementById('loop-lab-view');
const stage = document.querySelector('.slide-stage');
const previous = document.getElementById('previous-slide');
const next = document.getElementById('next-slide');
const fullscreen = document.getElementById('slide-fullscreen');
const query = new URLSearchParams(location.search);
const embedded = query.get('embed') === '1';
let slideIndex = 0;
let activeView = 'slides';
let activeTopic = 0;
let savedExplanation = null;

function language() {
  return document.documentElement.dataset.language || 'ja';
}

function setLanguage(value) {
  document.documentElement.dataset.language = value;
  document.documentElement.lang = value;
  const toggle = document.getElementById('language-toggle');
  toggle.textContent = value === 'ja' ? 'EN' : '日本語';
  toggle.setAttribute('aria-label', value === 'ja' ? 'Switch to English' : '日本語に切り替える');
  try { localStorage.setItem('programming-language', value); } catch (_) {}
  if (savedExplanation) document.getElementById('loop-explanation').textContent = savedExplanation[value];
  document.querySelectorAll('#loop-topic-select option').forEach(option => {
    option.textContent = topics[Number(option.value)][value];
  });
}

function showSlide(value) {
  slideIndex = Math.max(0, Math.min(slides.length - 1, value));
  slides.forEach((slide, index) => { slide.hidden = index !== slideIndex; });
  document.getElementById('slide-count').textContent = `${String(slideIndex + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
  previous.disabled = slideIndex === 0;
  next.disabled = slideIndex === slides.length - 1;
  stage.scrollTop = 0;
  const url = new URL(location.href);
  url.searchParams.set('slide', slideIndex + 1);
  history.replaceState(null, '', url);
}

function updateFullscreen() {
  fullscreen.setAttribute('aria-pressed', String(document.fullscreenElement === slidesView || slidesView.classList.contains('is-fullscreen-fallback')));
}

function showView(view) {
  activeView = view;
  slidesView.hidden = view !== 'slides';
  labView.hidden = view !== 'lab';
  document.querySelectorAll('[data-lecture-destination]').forEach(link => {
    if (link.dataset.lectureDestination === view) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });
  history.replaceState(null, '', view === 'lab' ? '#loop-lab' : `${location.pathname}${location.search}`);
}

function addSyntaxHighlighting() {
  document.querySelectorAll('pre code').forEach(code => {
    if (code.closest('#loop-code, #loop-output, .lecture-cell-output')) return;
    const source = code.textContent;
    const pattern = /(#[^\n]*)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|\b(for|in|if|else|elif|and|or|not|True|False)\b|\b(print|range|append|len|sum)\b|\b(\d+(?:_\d+)*(?:\.\d+)?)\b/g;
    let position = 0;
    code.replaceChildren();
    for (const match of source.matchAll(pattern)) {
      code.append(document.createTextNode(source.slice(position, match.index)));
      const token = document.createElement('span');
      token.className = match[1] ? 'syntax-comment' : match[2] ? 'syntax-string' : match[3] ? 'syntax-keyword' : match[4] ? 'syntax-function' : 'syntax-number';
      token.textContent = match[0];
      code.append(token);
      position = match.index + match[0].length;
    }
    code.append(document.createTextNode(source.slice(position)));
  });
}

function quoted(value) {
  return JSON.stringify(String(value));
}

function numbers(value) {
  return String(value).split(',').map(item => Number(item.trim())).filter(item => Number.isFinite(item));
}

function names(value) {
  return String(value).split(',').map(item => item.trim()).filter(Boolean).slice(0, 8);
}

function result(code, output, ja, en, cards = []) {
  return { code, output, ja, en, cards };
}

const topics = [
  {
    ja: '名前にあいさつ', en: 'Greeting names',
    inputs: [{ key: 'names', ja: '名前（カンマ区切り）', en: 'Names, comma-separated', value: 'Aoi, Kai, Mina' }],
    run: ({ names: rawNames }) => {
      const items = names(rawNames);
      if (!items.length) return result('# 名前を1つ以上入力してください', 'ValueError', '名前をカンマで区切って入力してください。', 'Enter at least one name, separated by commas.');
      const list = `[${items.map(quoted).join(', ')}]`;
      const output = items.map(name => `Welcome, ${name}!`).join('\n');
      return result(`names = ${list}\n\nfor name in names:\n    print(f"Welcome, {name}!")`, output, 'リストの一人ずつが name に入り、同じ print() が繰り返されます。', 'Each person from the list goes into name, and the same print() repeats.');
    }
  },
  {
    ja: 'rangeで数える', en: 'Counting with range',
    inputs: [{ key: 'start', ja: '開始', en: 'Start', value: '1', type: 'number' }, { key: 'end', ja: '終了の手前', en: 'Stop before', value: '5', type: 'number' }],
    run: ({ start, end }) => {
      const first = Number(start);
      const last = Number(end);
      if (!Number.isInteger(first) || !Number.isInteger(last)) return result('# 整数を入力してください', 'ValueError', '開始と終了の手前には整数を入れてください。', 'Use whole numbers for start and end.');
      const items = [];
      for (let number = first; number < last; number += 1) items.push(number);
      const output = items.length ? items.map(number => `Round ${number}`).join('\n') : '(no output)';
      return result(`for number in range(${first}, ${last}):\n    print(f"Round {number}")`, output, 'range の2つ目の数は含まれません。値がない範囲では、ループは一度も動きません。', 'The second number in range is excluded. With no values in the range, the loop does not run.');
    }
  },
  {
    ja: '合計を育てる', en: 'Growing a total',
    inputs: [{ key: 'scores', ja: '数値（カンマ区切り）', en: 'Numbers, comma-separated', value: '3, 8, 2, 9' }],
    run: ({ scores: rawScores }) => {
      const items = numbers(rawScores);
      if (!items.length) return result('# 例: 3, 8, 2, 9', 'ValueError', '数値をカンマで区切って入力してください。', 'Enter numbers separated by commas.');
      let total = 0;
      const output = [];
      items.forEach(score => { total += score; output.push(`after ${score}: ${total}`); });
      output.push(`Final total: ${total}`);
      return result(`scores = [${items.join(', ')}]\ntotal = 0\n\nfor score in scores:\n    total += score\n    print(f"after {score}: {total}")\n\nprint(f"Final total: {total}")`, output.join('\n'), 'total はループの前で0から始め、各周回で前の合計に次の値を足します。', 'total starts at zero before the loop, then adds the next value to the previous total on every turn.');
    }
  },
  {
    ja: '合格だけ選ぶ', en: 'Filtering pass scores',
    inputs: [{ key: 'scores', ja: '数値（カンマ区切り）', en: 'Numbers, comma-separated', value: '43, 61, 78, 55, 92' }, { key: 'minimum', ja: '合格ライン', en: 'Pass mark', value: '60', type: 'number' }],
    run: ({ scores: rawScores, minimum }) => {
      const items = numbers(rawScores);
      const mark = Number(minimum);
      if (!items.length || !Number.isFinite(mark)) return result('# 数値を入力してください', 'ValueError', '数値と合格ラインを確認してください。', 'Check the numbers and the pass mark.');
      const passing = items.filter(score => score >= mark);
      const output = `passing = ${JSON.stringify(passing)}`;
      return result(`scores = [${items.join(', ')}]\npassing = []\n\nfor score in scores:\n    if score >= ${mark}:\n        passing.append(score)\n\nprint(passing)`, output, 'if を通った値だけが passing に append されます。append は if の中に置きます。', 'Only values that pass the if test are appended to passing. Keep append inside the if block.');
    }
  },
  {
    ja: 'データからカードをつくる', en: 'Making cards from data',
    inputs: [{ key: 'rows', ja: '都道府県:人口（カンマ区切り）', en: 'Prefecture:population, comma-separated', value: '北海道:5140000, 東京都:14038000, 大阪府:8782000' }],
    run: ({ rows: rawRows }) => {
      const records = String(rawRows).split(',').map(item => {
        const [name, population] = item.split(':').map(part => part.trim());
        return { name, population: Number(population) };
      }).filter(row => row.name && Number.isFinite(row.population)).slice(0, 6);
      if (!records.length) return result('# 例: 北海道:5140000, 東京都:14038000', 'ValueError', '「名前:数値」をカンマで区切って入力してください。', 'Use “name:number” entries separated by commas.');
      const rows = records.map(row => `    {"name": ${quoted(row.name)}, "population": ${row.population}},`).join('\n');
      const output = records.map(row => `${row.name}: ${row.population.toLocaleString('en-US')}`).join('\n');
      return result(`prefectures = [\n${rows}\n]\n\ncards = []\nfor prefecture in prefectures:\n    label = f"{prefecture['name']}: {prefecture['population']:,}"\n    cards.append(label)\n\nprint(*cards, sep="\\n")`, output, '一件のデータから一つの文字列を作り、cards に追加します。データが増えると、カードも同じ数だけ増えます。', 'Make one string from each record, then append it to cards. Add more data and the same number of cards appears.', records);
    }
  }
];

function renderTopic(index) {
  activeTopic = index;
  document.getElementById('loop-topic-select').value = String(index);
  document.querySelectorAll('[data-topic]').forEach((button, buttonIndex) => {
    button.classList.toggle('is-selected', buttonIndex === index);
    button.setAttribute('aria-current', buttonIndex === index ? 'true' : 'false');
  });
  const controls = document.getElementById('loop-controls');
  controls.replaceChildren();
  topics[index].inputs.forEach(input => {
    const label = document.createElement('label');
    const ja = document.createElement('span');
    const en = document.createElement('span');
    ja.className = 'ja';
    en.className = 'en';
    ja.textContent = input.ja;
    en.textContent = input.en;
    const field = document.createElement('input');
    field.type = input.type || 'text';
    field.value = input.value;
    field.dataset.key = input.key;
    if (field.type === 'number') field.step = '1';
    label.append(ja, en, field);
    controls.append(label);
  });
  runTopic();
}

function renderCards(cards) {
  const root = document.getElementById('loop-visual');
  root.replaceChildren();
  cards.forEach(card => {
    const item = document.createElement('div');
    item.className = 'data-card';
    const title = document.createElement('strong');
    const detail = document.createElement('small');
    title.textContent = card.name;
    detail.textContent = `${card.population.toLocaleString('en-US')} people`;
    item.append(title, detail);
    root.append(item);
  });
}

function runTopic() {
  const values = Object.fromEntries([...document.querySelectorAll('#loop-controls [data-key]')].map(field => [field.dataset.key, field.value]));
  const answer = topics[activeTopic].run(values);
  document.getElementById('loop-code').textContent = answer.code;
  document.getElementById('loop-output').textContent = answer.output;
  savedExplanation = answer;
  document.getElementById('loop-explanation').textContent = answer[language()];
  renderCards(answer.cards);
}

if (embedded) {
  document.body.classList.add('lecture-embedded');
  document.querySelector('.lecture-header').hidden = true;
}

try {
  const destination = new URL(query.get('return') || '../../agenda.html?open=05#week-05', location.href);
  if (destination.origin === location.origin && /\/(?:index|agenda)\.html$/.test(destination.pathname)) document.getElementById('lecture-return').href = destination.href;
} catch (_) {}

addSyntaxHighlighting();
setLanguage((() => { try { return localStorage.getItem('programming-language') === 'en' ? 'en' : 'ja'; } catch (_) { return 'ja'; } })());
document.getElementById('language-toggle').addEventListener('click', () => setLanguage(language() === 'ja' ? 'en' : 'ja'));
window.addEventListener('storage', event => { if (event.key === 'programming-language') setLanguage(event.newValue === 'en' ? 'en' : 'ja'); });

previous.addEventListener('click', () => showSlide(slideIndex - 1));
next.addEventListener('click', () => showSlide(slideIndex + 1));
document.addEventListener('keydown', event => {
  if (event.target.closest('input, textarea, select')) return;
  if (activeView === 'slides' && ['ArrowLeft', 'ArrowRight'].includes(event.key)) {
    event.preventDefault();
    showSlide(slideIndex + (event.key === 'ArrowRight' ? 1 : -1));
  }
  if (event.key === 'Escape' && slidesView.classList.contains('is-fullscreen-fallback')) {
    slidesView.classList.remove('is-fullscreen-fallback');
    updateFullscreen();
  }
});

let touch = null;
stage.addEventListener('touchstart', event => {
  if (event.touches.length !== 1 || event.target.closest('button, a, input')) return;
  touch = { x: event.touches[0].clientX, y: event.touches[0].clientY };
}, { passive: true });
stage.addEventListener('touchend', event => {
  if (!touch || !event.changedTouches.length) return;
  const dx = event.changedTouches[0].clientX - touch.x;
  const dy = event.changedTouches[0].clientY - touch.y;
  touch = null;
  if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) showSlide(slideIndex + (dx < 0 ? 1 : -1));
}, { passive: true });
stage.addEventListener('touchcancel', () => { touch = null; }, { passive: true });

fullscreen.addEventListener('click', async () => {
  if (document.fullscreenElement === slidesView) await document.exitFullscreen();
  else if (slidesView.classList.contains('is-fullscreen-fallback')) slidesView.classList.remove('is-fullscreen-fallback');
  else {
    try { await slidesView.requestFullscreen(); }
    catch (_) { slidesView.classList.add('is-fullscreen-fallback'); }
  }
  updateFullscreen();
});
document.addEventListener('fullscreenchange', updateFullscreen);

document.querySelectorAll('[data-reveal]').forEach((button, index) => {
  const cell = button.closest('.lecture-notebook-cell');
  const output = cell.nextElementSibling;
  output.id = `example-output-${index}`;
  button.setAttribute('aria-controls', output.id);
  button.addEventListener('click', () => {
    output.hidden = !output.hidden;
    button.setAttribute('aria-expanded', String(!output.hidden));
  });
});

document.querySelectorAll('[data-quiz-choice]').forEach(button => button.addEventListener('click', () => {
  const correct = button.dataset.quizChoice === 'two';
  const feedback = document.getElementById('quiz-feedback');
  feedback.textContent = language() === 'ja'
    ? (correct ? '正解。600万人以上なのは東京都と大阪府。北海道は514万人です。' : 'もう一度データを確認しよう。600万人以上かを一件ずつ調べます。')
    : (correct ? 'Correct. Tokyo and Osaka are at least 6 million. Hokkaido has 5.14 million.' : 'Check the data again. Test one record at a time against 6 million.');
}));

document.querySelectorAll('[data-lecture-destination]').forEach(link => link.addEventListener('click', event => {
  event.preventDefault();
  showView(link.dataset.lectureDestination);
}));
document.getElementById('loop-run').addEventListener('click', runTopic);
document.getElementById('loop-controls').addEventListener('keydown', event => { if (event.key === 'Enter') runTopic(); });
const topicNav = document.getElementById('loop-topics');
const topicSelect = document.getElementById('loop-topic-select');
topicSelect.addEventListener('change', () => renderTopic(Number(topicSelect.value)));
topics.forEach((topic, index) => {
  const option = document.createElement('option');
  option.value = String(index);
  option.textContent = topic[language()];
  topicSelect.append(option);
  const button = document.createElement('button');
  button.type = 'button';
  button.dataset.topic = String(index);
  button.innerHTML = `<span class="ja">${topic.ja}</span><span class="en">${topic.en}</span>`;
  button.addEventListener('click', () => renderTopic(index));
  topicNav.append(button);
});

showSlide(Math.max(0, (Number(query.get('slide')) || 1) - 1));
renderTopic(0);
if (location.hash === '#loop-lab') showView('lab');
else showView('slides');
