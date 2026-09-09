const weekFiles = [
  '01-first-instruction.md','02-variables.md','03-collections.md','04-conditionals.md',
  '05-for-loops.md','06-while-loops.md','07-logic-loops.md','08-bicycle-theft.md',
  '09-functions.md','10-systems.md','11-objects-modules.md','12-review.md',
  '13-tkinter.md','14-final-report.md'
];

const phaseStarts = {
  '01':['WRITE · write exact instructions','書く · 正確な命令を書く'],
  '05':['REPEAT · make a process travel','繰り返す · 手順を何度でも使う'],
  '09':['COMPOSE · build reusable tools','組み立てる · 再利用できる道具を作る'],
  '12':['MAKE · shape a result of your own','つくる · 自分の結果を形にする']
};

const escapeHtml = value => String(value || '').replace(/[&<>\"]/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' })[char]);

function parseFrontMatter(source) {
  const match = source.match(/^---\s*\n([\s\S]*?)\n---\s*\n?([\s\S]*)$/);
  if (!match) throw new Error('Missing front matter');
  const meta = Object.fromEntries(match[1].split('\n').map(line => {
    const index = line.indexOf(':');
    return index < 0 ? [] : [line.slice(0, index).trim(), line.slice(index + 1).trim().replace(/^['"]|['"]$/g, '')];
  }).filter(entry => entry.length));
  const sections = [...match[2].matchAll(/^##\s+(.+)\n([\s\S]*?)(?=^##\s+|$(?![\s\S]))/gm)].map(([, title, body]) => ({ title:title.trim(), body:body.trim() }));
  return { ...meta, week:Number(meta.week), sections };
}

function parseBilingual(body) {
  const en = body.match(/(?:^|\n)EN:\s*([\s\S]*?)(?=\nJP:|$)/)?.[1]?.trim() || '';
  const ja = body.match(/(?:^|\n)JP:\s*([\s\S]*?)$/)?.[1]?.trim() || '';
  return { en, ja };
}

function highlightEscapedCode(code) {
  return code
    .replace(/(&quot;[^&]*?&quot;|'[^']*?')/g, '<span class="syntax-string">$1</span>')
    .replace(/\b(print|input|type|int|float|str|bool|len|range)\b/g, '<span class="syntax-function">$1</span>')
    .replace(/\b(True|False|None)\b/g, '<span class="syntax-constant">$1</span>')
    .replace(/\b(def|return|if|elif|else|for|while|in|import|from)\b/g, '<span class="syntax-keyword">$1</span>')
    .replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="syntax-number">$1</span>');
}

function highlightCode(code) { return highlightEscapedCode(escapeHtml(code)); }

function numberedCodeHtml(source) {
  return source.split('\n').map((line, index) => `<span class="code-row"><i>${index + 1}</i><span>${highlightCode(line) || ' '}</span></span>`).join('');
}

function inline(text) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, (_, code) => `<code>${highlightEscapedCode(code)}</code>`)
    .replace(/\[([^\]]+)\]\(([^\s)]+)\)/g, '<a href="$2">$1</a>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
}

function tableHtml(lines) {
  const rows = lines.map(line => line.trim().replace(/^\||\|$/g, '').split('|').map(cell => cell.trim()));
  const [head, , ...body] = rows;
  return `<div class="content-table-wrap"><table class="content-table"><thead><tr>${head.map(cell => `<th>${inline(cell)}</th>`).join('')}</tr></thead><tbody>${body.map(row => `<tr>${row.map(cell => `<td>${inline(cell)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}

function markdownHtml(markdown) {
  return markdown.split(/\n{2,}/).filter(Boolean).map(block => {
    const lines = block.split('\n');
    const fence = block.match(/^```(?:python)?\n([\s\S]*?)\n```$/);
    const heading = lines[0].match(/^(#{1,3})\s+(.+)$/);
    if (fence) return `<pre class="code-block" aria-label="Python code"><code>${highlightCode(fence[1])}</code></pre>`;
    if (heading) return `<h${heading[1].length + 1}>${inline(heading[2])}</h${heading[1].length + 1}>${lines.length > 1 ? markdownHtml(lines.slice(1).join('\n').trim()) : ''}`;
    if (lines.every(line => /^>\s+/.test(line))) return `<blockquote>${lines.map(line => inline(line.replace(/^>\s+/, ''))).join('<br>')}</blockquote>`;
    if (lines.length >= 2 && /^\s*\|?\s*:?-{3,}/.test(lines[1])) return tableHtml(lines);
    if (lines.every(line => /^\s*-\s+/.test(line))) return `<ul>${lines.map(line => `<li>${inline(line.replace(/^\s*-\s+/, ''))}</li>`).join('')}</ul>`;
    if (lines.every(line => /^\s*\d+\.\s+/.test(line))) return `<ol>${lines.map(line => `<li>${inline(line.replace(/^\s*\d+\.\s+/, ''))}</li>`).join('')}</ol>`;
    return `<p>${lines.map(inline).join('<br>')}</p>`;
  }).join('');
}

function bilingualHtml(body) {
  const copy = parseBilingual(body);
  return `${copy.en ? `<div class="lang-en copy-block">${markdownHtml(copy.en)}</div>` : ''}${copy.ja ? `<div class="lang-ja jp copy-block" lang="ja">${markdownHtml(copy.ja)}</div>` : ''}`;
}

function fileType(href, external) {
  if (external) return 'LINK';
  const extension = href.split('?')[0].split('.').pop().toLowerCase();
  return ({ pdf:'PDF', ipynb:'IPYNB', csv:'CSV', md:'MD', py:'PY', png:'PNG', jpg:'JPG', jpeg:'JPG', gif:'GIF', zip:'ZIP' })[extension] || 'FILE';
}

function resourcesHtml(body, onlyKinds = []) {
  return body.split('\n').map(raw => raw.trim()).filter(line => line.startsWith('- ')).map(line => {
    const match = line.match(/^-\s*\[([^\]]+)\]\(([^\s)]+)\)(?:\s*\{([^}]+)\})?$/);
    if (!match) return '';
    const [, label, href, kind = 'support'] = match;
    if (onlyKinds.length && !onlyKinds.includes(kind.toLowerCase())) return '';
    const external = /^https?:/.test(href);
    const type = fileType(href, external);
    const viewer = `viewer.html?file=${encodeURIComponent(href)}&title=${encodeURIComponent(label)}`;
    return `<div class="file-action" data-kind="${escapeHtml(kind.toLowerCase())}"><span class="file-name">${escapeHtml(label)}</span><span class="file-type">${type}</span><a class="file-preview" href="${external ? escapeHtml(href) : viewer}"${external ? ' target="_blank" rel="noopener"' : ''}><span class="lang-ja jp" lang="ja">プレビュー</span><span class="lang-en">PREVIEW</span></a>${external ? '' : `<a class="file-download" href="${escapeHtml(href)}" download><span class="lang-ja jp" lang="ja">ダウンロード</span><span class="lang-en">DOWNLOAD</span></a>`}</div>`;
  }).join('');
}

function section(week, key) { return week.sections.find(item => item.title.toLowerCase().startsWith(key.toLowerCase())); }
function isOpen(week) { return new URLSearchParams(location.search).has('planning') || week.preview === 'true' || new Date() >= new Date(week.publish_at); }
function dateLabel(value) { return new Intl.DateTimeFormat('ja-JP', { dateStyle:'long', timeZone:'Asia/Tokyo' }).format(new Date(value)); }

function practiceMixHtml(w) {
  if (!w.practice_mix) return '';
  const values = [...w.practice_mix.matchAll(/(Human|AI|Agent)\s+(\d+)%/g)].map(([, label, value]) => ({ label, value:Number(value) }));
  const colors = { Human:'human', AI:'ai', Agent:'agent' };
  const japaneseLabels = { Human:'人', AI:'AI', Agent:'エージェント' };
  const segments = values.map(item => `<span class="mix-segment ${colors[item.label]}" style="width:${item.value}%" title="${item.label} ${item.value}%"><i>${item.value >= 15 ? item.value + '%' : ''}</i></span>`).join('');
  const key = values.map(item => `<span><i class="mix-dot ${colors[item.label]}"></i>${item.label} ${item.value}%</span>`).join('');
  const keyJapanese = values.map(item => `<span><i class="mix-dot ${colors[item.label]}"></i>${japaneseLabels[item.label]} ${item.value}%</span>`).join('');
  return `<div class="practice-mix" role="img" aria-label="Practice mix: ${escapeHtml(w.practice_mix)}"><div class="mix-label"><span class="lang-en">Practice mix</span><span class="lang-ja jp" lang="ja">実践の割合</span></div><div class="mix-bar">${segments}</div><div class="mix-key"><span class="lang-en">${key}</span><span class="lang-ja jp mix-ja" lang="ja">${keyJapanese}</span></div></div>`;
}

function courseDateLabels(value) {
  if (!value) return { en:'Date to be confirmed', ja:'日程は後日案内' };
  const date = new Date(`${value}T12:00:00+09:00`);
  return {
    en: new Intl.DateTimeFormat('en-US', { weekday:'short', month:'short', day:'numeric', year:'numeric', timeZone:'Asia/Tokyo' }).format(date),
    ja: new Intl.DateTimeFormat('ja-JP', { weekday:'short', year:'numeric', month:'long', day:'numeric', timeZone:'Asia/Tokyo' }).format(date)
  };
}

function courseScheduleHtml(w) {
  const date = courseDateLabels(w.course_date);
  const time = escapeHtml(w.course_time || '13:10–14:50');
  return `<div class="week-schedule"><span class="lang-en">${escapeHtml(date.en)}</span><span class="lang-ja jp" lang="ja">${escapeHtml(date.ja)}</span><small><span class="lang-en">PERIOD 3 · ${time} · 100 MIN</span><span class="lang-ja jp" lang="ja">3限 · ${time} · 100分</span></small></div>`;
}

function agendaWeek(w) {
  const open = isOpen(w);
  const paths = [
    ['Lecture Flow','講義の流れ',['lecture']],
    ['In-Class Notebook','授業内ノートブック',['notebook','fundamentals','support']],
    ['In-Class Challenge','授業内チャレンジ',['challenge']],
    ['Take-Home Assignment','持ち帰り課題',['homework']]
  ];
  const insights = [['Aha!','Aha!'],['Takeaway','今週の要点']];
  const resources = section(w, 'Resources');
  const details = open ? `<div class="week-grid"><div class="week-path">${paths.map(([key, ja, resourceKinds]) => {
    const item = section(w,key); const links = resources ? resourcesHtml(resources.body, resourceKinds) : '';
    return item ? `<section class="practice-${key.toLowerCase().replace(/[^a-z]+/g,'-')}"><b><span class="lang-en">${key.toUpperCase()}</span><small class="lang-ja jp" lang="ja">${ja}</small></b>${bilingualHtml(item.body)}${links ? `<div class="section-resources">${links}</div>` : ''}</section>` : '';
  }).join('')}</div><aside class="week-insights">${insights.map(([key, ja]) => {
    const item = section(w,key); return item ? `<div class="insight"><b><span class="lang-en">${key.toUpperCase()}</span><small class="lang-ja jp" lang="ja">${ja}</small></b>${bilingualHtml(item.body)}</div>` : '';
  }).join('')}</aside></div>` : `<p class="agenda-locked"><strong>COMING SOON / 準備中</strong> · Details publish ${dateLabel(w.publish_at)}.</p>`;
  const mix = practiceMixHtml(w);
  const id = `week-${String(w.week).padStart(2,'0')}`;
  const detailId = `${id}-details`;
  const overview = `<p class="week-overview lang-en">${escapeHtml(w.overview || '')}</p><p class="week-overview lang-ja jp" lang="ja">${escapeHtml(w.overview_ja || '')}</p>`;
  return `<article class="week${open ? '' : ' is-locked'}" id="${id}"><div class="week-number">${String(w.week).padStart(2,'0')}<small>${escapeHtml(w.phase)}</small></div><div class="week-content"><div class="week-summary">${courseScheduleHtml(w)}<div class="week-summary-copy"><h2 class="lang-en">${escapeHtml(w.title)}</h2><h2 class="lang-ja jp week-title-ja" lang="ja">${escapeHtml(w.title_ja || '')}</h2>${overview}</div><button class="week-toggle" type="button" data-week-toggle aria-expanded="false" aria-controls="${detailId}"><span class="lang-en">VIEW DETAILS</span><span class="lang-ja jp" lang="ja">詳細を見る</span><i aria-hidden="true">↓</i></button></div><div class="week-details" id="${detailId}" hidden>${mix}${details}</div></div></article>`;
}

function renderAgenda(weeks) {
  const root = document.querySelector('[data-agenda]'); if (!root) return;
  const controls = `<div class="syllabus-controls"><div><p class="eyebrow">SYLLABUS VIEW / シラバス</p><p class="lang-en">Fourteen meetings, one clear route. Open a week when you are ready for its materials.</p><p class="lang-ja jp" lang="ja">14回の授業を、ひと目で確認。必要な週だけ詳細を開こう。</p></div><button class="syllabus-toggle" type="button" data-agenda-expand aria-expanded="false"><span class="lang-en">EXPAND ALL</span><span class="lang-ja jp" lang="ja">すべて開く</span><i aria-hidden="true">↓</i></button></div>`;
  root.innerHTML = controls + weeks.map(w => `${phaseStarts[String(w.week).padStart(2,'0')] ? `<div class="phase-band"><b><span class="lang-en">${phaseStarts[String(w.week).padStart(2,'0')][0]}</span><small class="lang-ja jp" lang="ja">${phaseStarts[String(w.week).padStart(2,'0')][1]}</small></b><span>${w.week === 1 ? '01–04' : w.week === 5 ? '05–08' : w.week === 9 ? '09–11' : '12–14'}</span></div>` : ''}${agendaWeek(w)}`).join('');
}

function setupAgendaToggles() {
  const root = document.querySelector('[data-agenda]');
  if (!root) return;
  const allButton = root.querySelector('[data-agenda-expand]');
  const updateAllButton = () => {
    const weeks = [...root.querySelectorAll('.week')];
    const expanded = weeks.length > 0 && weeks.every(week => week.classList.contains('is-expanded'));
    if (!allButton) return;
    allButton.setAttribute('aria-expanded', String(expanded));
    allButton.innerHTML = expanded
      ? '<span class="lang-en">COLLAPSE ALL</span><span class="lang-ja jp" lang="ja">すべて閉じる</span><i aria-hidden="true">↑</i>'
      : '<span class="lang-en">EXPAND ALL</span><span class="lang-ja jp" lang="ja">すべて開く</span><i aria-hidden="true">↓</i>';
  };
  const setExpanded = (week, expanded) => {
    const details = week.querySelector('.week-details');
    const button = week.querySelector('[data-week-toggle]');
    week.classList.toggle('is-expanded', expanded);
    details.hidden = !expanded;
    button.setAttribute('aria-expanded', String(expanded));
    button.innerHTML = expanded
      ? '<span class="lang-en">HIDE DETAILS</span><span class="lang-ja jp" lang="ja">詳細を閉じる</span><i aria-hidden="true">↑</i>'
      : '<span class="lang-en">VIEW DETAILS</span><span class="lang-ja jp" lang="ja">詳細を見る</span><i aria-hidden="true">↓</i>';
  };
  root.querySelectorAll('[data-week-toggle]').forEach(button => button.addEventListener('click', () => {
    const week = button.closest('.week');
    setExpanded(week, !week.classList.contains('is-expanded'));
    updateAllButton();
  }));
  if (allButton) allButton.addEventListener('click', () => {
    const expand = allButton.getAttribute('aria-expanded') !== 'true';
    root.querySelectorAll('.week').forEach(week => setExpanded(week, expand));
    updateAllButton();
  });
}

function setupMenu() {
  const button = document.querySelector('.menu-toggle'), nav = document.querySelector('.site-nav');
  if (!button || !nav) return;
  button.addEventListener('click', () => { const open = nav.classList.toggle('open'); button.setAttribute('aria-expanded', String(open)); });
}

function setupLanguage() {
  const root = document.documentElement;
  document.querySelectorAll('.jp').forEach(element => element.classList.add('lang-ja'));
  document.querySelectorAll('.translation.jp').forEach(japanese => {
    const parent = japanese.parentElement;
    const englishNodes = [...parent.childNodes].filter(node => node !== japanese && node.nodeType === Node.TEXT_NODE && node.textContent.trim());
    if (!englishNodes.length) return;
    const english = document.createElement('span');
    english.className = 'lang-en';
    parent.insertBefore(english, englishNodes[0]);
    englishNodes.forEach(node => english.appendChild(node));
  });
  const saved = localStorage.getItem('programming-language');
  const setLanguage = language => {
    root.dataset.language = language;
    document.querySelectorAll('[data-language-toggle]').forEach(button => {
      const isJapanese = language === 'ja';
      button.textContent = isJapanese ? 'EN' : '日本語';
      button.setAttribute('aria-label', isJapanese ? 'Switch to English' : '日本語に切り替える');
      button.setAttribute('title', isJapanese ? 'English' : '日本語');
    });
  };
  setLanguage(saved === 'en' ? 'en' : 'ja');
  document.querySelectorAll('[data-language-toggle]').forEach(button => button.addEventListener('click', () => {
    const next = root.dataset.language === 'ja' ? 'en' : 'ja';
    localStorage.setItem('programming-language', next);
    setLanguage(next);
  }));
}

function setupFirstPython() {
  const input = document.querySelector('[data-python-input]');
  const name = document.querySelector('[data-python-name]');
  const output = document.querySelector('[data-python-output]');
  const button = document.querySelector('[data-run-python]');
  if (!input || !name || !output || !button) return;
  const message = () => `Hello, ${(input.value || 'world').trim() || 'world'}!`;
  const sync = () => { name.textContent = (input.value || 'world').trim() || 'world'; };
  input.addEventListener('input', sync);
  input.addEventListener('keydown', event => { if (event.key === 'Enter') { event.preventDefault(); button.click(); } });
  button.addEventListener('click', () => {
    sync();
    output.textContent = message();
    output.parentElement.classList.add('has-output');
  });
}

async function setupFileViewer() {
  const root = document.querySelector('[data-file-viewer]');
  if (!root) return;
  const params = new URLSearchParams(location.search);
  const file = params.get('file') || '';
  const title = params.get('title') || file.split('/').pop() || 'File preview';
  if (!/^(weeks|content)\//.test(file)) { root.innerHTML = '<p>File preview is unavailable.</p>'; return; }
  const extension = file.split('.').pop().toLowerCase();
  const download = `<a class="file-download viewer-download" href="${escapeHtml(file)}" download>↓ <span>DOWNLOAD</span></a>`;
  try {
    if (extension === 'pdf') {
      root.innerHTML = `<div class="viewer-title"><p class="eyebrow">PDF PREVIEW</p><h1>${escapeHtml(title)}</h1>${download}</div><iframe class="pdf-viewer" title="${escapeHtml(title)}" src="${escapeHtml(file)}"></iframe>`;
      return;
    }
    const response = await fetch(file, { cache:'no-cache' });
    if (!response.ok) throw new Error('File not found');
    const source = await response.text();
    if (extension === 'ipynb') {
      const notebook = JSON.parse(source);
      const cells = notebook.cells || [];
      const preview = cells.slice(0, 12).map(cell => cell.cell_type === 'code'
        ? `<section class="notebook-cell code-cell"><div class="cell-label"><span>▶</span> Code</div><pre class="code-block"><code>${numberedCodeHtml((cell.source || []).join(''))}</code></pre></section>`
        : `<section class="notebook-cell markdown-cell"><div class="cell-label">Markdown</div><div class="notebook-markdown">${markdownHtml((cell.source || []).join(''))}</div></section>`).join('');
      root.innerHTML = `<div class="viewer-title"><p class="eyebrow">JUPYTER NOTEBOOK · ${cells.length} CELLS</p><h1>${escapeHtml(title)}</h1>${download}</div><section class="notebook-shell"><header class="notebook-toolbar"><span class="notebook-tab">${escapeHtml(title)} · Preview</span><span class="notebook-run">▶ Run All</span><span class="notebook-kernel">Python 3.12</span></header><article class="notebook-preview">${preview}</article></section>`;
      return;
    }
    root.innerHTML = `<div class="viewer-title"><p class="eyebrow">MARKDOWN PREVIEW</p><h1>${escapeHtml(title)}</h1>${download}</div><article class="markdown-preview">${markdownHtml(source.replace(/^#\s+(.+)$/m, '**$1**'))}</article>`;
  } catch (error) { root.innerHTML = `<p class="agenda-locked">Could not preview ${escapeHtml(title)}. ${download}</p>`; }
}

async function loadWeeks() {
  const responses = await Promise.all(weekFiles.map(file => fetch(`content/weeks/${file}`, { cache:'no-cache' }).then(response => {
    if (!response.ok) throw new Error(`Could not load ${file}`); return response.text();
  })));
  return responses.map(parseFrontMatter).sort((a,b) => a.week - b.week);
}

document.addEventListener('DOMContentLoaded', async () => {
  setupMenu();
  setupLanguage();
  setupFirstPython();
  setupFileViewer();
  try { const weeks = await loadWeeks(); renderAgenda(weeks); setupAgendaToggles(); }
  catch (error) { console.error(error); document.querySelectorAll('[data-agenda]').forEach(node => { node.innerHTML = '<p class="agenda-locked">Course content could not load. Please refresh the page.</p>'; }); }
});
