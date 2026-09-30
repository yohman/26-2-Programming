const weekFiles = [
  '01-first-instruction.md','02-variables.md','03-collections.md','04-conditionals.md',
  '05-for-loops.md','06-while-loops.md','07-logic-loops.md','08-bicycle-theft.md',
  '09-functions.md','10-systems.md','11-objects-modules.md','12-review.md',
  '13-tkinter.md','14-final-report.md'
];

const tutorialSequence = [
  { file:'weeks/week-01/tutorials/01-install-python.md', ja:'Pythonをインストールする', en:'Install Python' },
  { file:'weeks/week-01/tutorials/02-install-vscode.md', ja:'VS Codeを準備する', en:'Set up VS Code' },
  { file:'weeks/week-01/tutorials/03-course-workspace.md', ja:'授業フォルダをつくる', en:'Create the course workspace' },
  { file:'weeks/week-01/tutorials/04-environment-and-kernel.md', ja:'.venvとKernelをつなぐ', en:'Environment and kernel' },
  { file:'weeks/week-01/tutorials/05-jupyter-notebook.md', ja:'Jupyter Notebookの使い方', en:'Use a notebook' },
  { file:'weeks/week-01/tutorials/06-markdown-basics.md', ja:'Markdownで説明を書く', en:'Markdown basics' },
  { file:'weeks/week-01/tutorials/07-python-basics-and-challenges.md', ja:'Python BasicsとローカルChallenge', en:'Python basics and challenges' }
];

const phaseStarts = {
  '01':['WRITE · write exact instructions','書く · 正確な命令を書く'],
  '05':['REPEAT · make a process travel','繰り返す · 手順を何度でも使う'],
  '09':['COMPOSE · build reusable tools','組み立てる · 再利用できる道具を作る'],
  '12':['MAKE · shape a result of your own','つくる · 自分の結果を形にする']
};

const pdfPageCounts = {
  'weeks/week-01/week-01-lecture-first-python.pdf': 47,
  'weeks/week-02/lecture.pdf': 12,
  'weeks/week-03/lecture.pdf': 6,
  'weeks/week-04/lecture.pdf': 15,
  'weeks/week-05/lecture.pdf': 15,
  'weeks/week-06/lecture.pdf': 4,
  'weeks/week-07/lecture.pdf': 4,
  'weeks/week-08/lecture.pdf': 19,
  'weeks/week-09/lecture.pdf': 13,
  'weeks/week-10/lecture.pdf': 25,
  'weeks/week-11/lecture.pdf': 23,
  'weeks/week-12/lecture.pdf': 19
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
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>');
}

function tableHtml(lines) {
  const rows = lines.map(line => line.trim().replace(/^\||\|$/g, '').split('|').map(cell => cell.trim()));
  const [head, , ...body] = rows;
  return `<div class="content-table-wrap"><table class="content-table"><thead><tr>${head.map(cell => `<th>${inline(cell)}</th>`).join('')}</tr></thead><tbody>${body.map(row => `<tr>${row.map(cell => `<td>${inline(cell)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}

function markdownHtml(markdown) {
  return markdown.split(/\n{2,}/).filter(block => block.trim()).map(rawBlock => {
    const block = rawBlock.trim();
    const lines = block.split('\n');
    const fence = block.match(/^```([a-z0-9_-]*)\n([\s\S]*?)\n```$/i);
    const heading = lines[0].match(/^(#{1,3})\s+(.+)$/);
    if (fence) {
      const language = fence[1].toLowerCase();
      const code = language === 'python' || language === 'py' ? highlightCode(fence[2]) : escapeHtml(fence[2].replace(/\\`/g, '`'));
      return `<pre class="code-block" aria-label="${escapeHtml(language || 'Code')} code"><code>${code}</code></pre>`;
    }
    if (heading) return `<h${heading[1].length + 1}>${inline(heading[2])}</h${heading[1].length + 1}>${lines.length > 1 ? markdownHtml(lines.slice(1).join('\n').trim()) : ''}`;
    if (lines.every(line => /^>\s+/.test(line))) {
      const quote = lines.map(line => line.replace(/^>\s+/, '')).join('\n');
      const label = quote.match(/^\*\*([^*]+)\*\*/)?.[1]?.toLowerCase() || '';
      const kind = /aha/.test(label) ? 'aha' : /tip|ヒント/.test(label) ? 'tip' : /check|確認/.test(label) ? 'check' : /goal|ゴール/.test(label) ? 'goal' : 'note';
      return `<aside class="content-callout content-callout--${kind}">${lines.map(line => `<p>${inline(line.replace(/^>\s+/, ''))}</p>`).join('')}</aside>`;
    }
    if (lines.length >= 2 && /^\s*\|?\s*:?-{3,}/.test(lines[1])) return tableHtml(lines);
    if (lines.every(line => /^\s*-\s+/.test(line))) return `<ul>${lines.map(line => `<li>${inline(line.replace(/^\s*-\s+/, ''))}</li>`).join('')}</ul>`;
    if (lines.every(line => /^\s*\d+\.\s+/.test(line))) return `<ol>${lines.map(line => `<li>${inline(line.replace(/^\s*\d+\.\s+/, ''))}</li>`).join('')}</ol>`;
    return `<p>${lines.map(inline).join('<br>')}</p>`;
  }).join('');
}

function tutorialTabsHtml(source) {
  const tabs = [...source.matchAll(/^###\s+(Windows|macOS)\s*\n([\s\S]*?)(?=^###\s+(?:Windows|macOS)\s*$|$(?![\s\S]))/gmi)];
  if (!tabs.length) return markdownHtml(source);
  const id = `tutorial-tabs-${Math.random().toString(36).slice(2, 9)}`;
  const buttons = tabs.map(([, label], index) => `<button type="button" role="tab" id="${id}-tab-${index}" aria-controls="${id}-panel-${index}" aria-selected="${index === 0}" tabindex="${index === 0 ? '0' : '-1'}" data-tutorial-tab="${index}">${escapeHtml(label)}</button>`).join('');
  const panels = tabs.map(([, label, body], index) => {
    const nestedBody = markdownHtml(body.trim()).replace(/<(\/?)h([34])>/g, (_, closing, level) => `<${closing}h${Number(level) + 1}>`);
    return `<section role="tabpanel" id="${id}-panel-${index}" aria-labelledby="${id}-tab-${index}" data-tutorial-panel="${index}"${index === 0 ? '' : ' hidden'}><h3>${escapeHtml(label)}</h3>${nestedBody}</section>`;
  }).join('');
  return `<div class="tutorial-tabs" data-tutorial-tabs><div class="tutorial-tab-list" role="tablist" aria-label="Operating system">${buttons}</div>${panels}</div>`;
}

function tutorialMarkdownHtml(source) {
  const groups = [];
  const prepared = source.replace(/<!--\s*tabs:start\s*-->([\s\S]*?)<!--\s*tabs:end\s*-->/gi, (_, body) => {
    const token = `TUTORIALTABSGROUP${groups.length}`;
    groups.push(tutorialTabsHtml(body.trim()));
    return `\n\n${token}\n\n`;
  });
  let html = markdownHtml(prepared);
  groups.forEach((group, index) => { html = html.replace(`<p>TUTORIALTABSGROUP${index}</p>`, group); });
  return html.replace(/<a href="(https?:\/\/[^\"]+)">/g, '<a href="$1" target="_blank" rel="noopener">');
}

function setupTutorialTabs(root = document) {
  root.querySelectorAll('[data-tutorial-tabs]').forEach(group => {
    const buttons = [...group.querySelectorAll('[data-tutorial-tab]')];
    const panels = [...group.querySelectorAll('[data-tutorial-panel]')];
    const select = index => {
      buttons.forEach((button, buttonIndex) => {
        const selected = buttonIndex === index;
        button.setAttribute('aria-selected', String(selected));
        button.tabIndex = selected ? 0 : -1;
      });
      panels.forEach((panel, panelIndex) => { panel.hidden = panelIndex !== index; });
    };
    buttons.forEach((button, index) => {
      button.addEventListener('click', () => select(index));
      button.addEventListener('keydown', event => {
        if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
        event.preventDefault();
        const next = (index + (event.key === 'ArrowRight' ? 1 : -1) + buttons.length) % buttons.length;
        select(next);
        buttons[next].focus();
      });
    });
  });
}

function tutorialLink(item, returnUrl) {
  const query = new URLSearchParams({
    file:item.file,
    title:`${item.ja} / ${item.en}`,
    return:returnUrl
  });
  return `viewer.html?${query.toString()}`;
}

function tutorialNavigationHtml(file, returnUrl) {
  const index = tutorialSequence.findIndex(item => item.file === file);
  if (index < 0) return '';
  const control = (item, direction) => {
    const previous = direction === 'previous';
    const directionLabel = previous
      ? '<span class="lang-en">← PREVIOUS</span><span class="lang-ja jp" lang="ja">← 前へ</span>'
      : '<span class="lang-en">NEXT →</span><span class="lang-ja jp" lang="ja">次へ →</span>';
    if (!item) {
      const endLabel = previous
        ? '<span class="lang-en">First tutorial</span><span class="lang-ja jp" lang="ja">最初のTutorial</span>'
        : '<span class="lang-en">Last tutorial</span><span class="lang-ja jp" lang="ja">最後のTutorial</span>';
      return `<span class="tutorial-step tutorial-step--${direction} is-disabled" aria-disabled="true"><small>${directionLabel}</small><strong>${endLabel}</strong></span>`;
    }
    return `<a class="tutorial-step tutorial-step--${direction}" href="${escapeHtml(tutorialLink(item, returnUrl))}"><small>${directionLabel}</small><strong><span class="lang-en">${escapeHtml(item.en)}</span><span class="lang-ja jp" lang="ja">${escapeHtml(item.ja)}</span></strong></a>`;
  };
  return `<nav class="tutorial-pager" aria-label="Tutorial navigation">${control(tutorialSequence[index - 1], 'previous')}${control(tutorialSequence[index + 1], 'next')}</nav>`;
}

function tutorialOutline(source) {
  const container = document.createElement('div');
  container.innerHTML = tutorialMarkdownHtml(source.replace(/^#\s+.+\n?/, ''));
  return [...container.querySelectorAll('h3, h4, h5')].map((heading, index) => ({
    id:`tutorial-section-${index + 1}`,
    label:heading.textContent.trim(),
    level:Number(heading.tagName.slice(1)),
    panelIndex:heading.closest('[data-tutorial-panel]')?.dataset.tutorialPanel ?? ''
  }));
}

async function setupTutorialToc(root, file, returnUrl, currentSource) {
  const article = root.querySelector('.tutorial-preview');
  const toc = root.querySelector('[data-tutorial-toc]');
  if (!article || !toc) return;
  const currentHeadings = [...article.querySelectorAll('h3, h4, h5')];
  currentHeadings.forEach((heading, index) => {
    const id = `tutorial-section-${index + 1}`;
    heading.id = id;
  });
  const sources = await Promise.all(tutorialSequence.map(item => item.file === file
    ? Promise.resolve(currentSource)
    : fetch(item.file, { cache:'no-cache' }).then(response => response.ok ? response.text() : '').catch(() => '')));
  const currentIndex = tutorialSequence.findIndex(item => item.file === file);
  const steps = tutorialSequence.map((item, index) => {
    const current = index === currentIndex;
    const outline = tutorialOutline(sources[index] || '');
    const sectionLinks = outline.map(section => {
      const levelClass = section.level === 5 ? 'is-subsection is-subsection--deep' : section.level === 4 ? 'is-subsection' : '';
      const href = current ? `#${section.id}` : `${tutorialLink(item, returnUrl)}#${section.id}`;
      const panelData = current && section.panelIndex !== '' ? ` data-toc-panel="${escapeHtml(section.panelIndex)}"` : '';
      const newTab = current ? '' : ' target="_blank" rel="noopener"';
      return `<a class="${levelClass}" href="${escapeHtml(href)}"${panelData}${newTab}>${escapeHtml(section.label)}</a>`;
    }).join('');
    const openLink = current
      ? '<a class="tutorial-toc-open" href="#"><span class="lang-en">TOP OF THIS STEP ↑</span><span class="lang-ja jp" lang="ja">このステップの先頭へ ↑</span></a>'
      : `<a class="tutorial-toc-open" href="${escapeHtml(tutorialLink(item, returnUrl))}" target="_blank" rel="noopener"><span class="lang-en">OPEN TUTORIAL ↗</span><span class="lang-ja jp" lang="ja">Tutorialを開く ↗</span></a>`;
    return `<details class="tutorial-toc-step${current ? ' is-current' : ''}"${current ? ' open' : ''}><summary><span>${String(index + 1).padStart(2, '0')}</span><strong><span class="lang-en">${escapeHtml(item.en)}</span><span class="lang-ja jp" lang="ja">${escapeHtml(item.ja)}</span></strong><b aria-hidden="true">⌄</b></summary><nav aria-label="${escapeHtml(item.en)} sections">${openLink}${sectionLinks}</nav></details>`;
  }).join('');
  toc.innerHTML = `<header><p>TUTORIALS</p><span><span class="lang-en">7 STEPS</span><span class="lang-ja jp" lang="ja">全7ステップ</span></span></header><div class="tutorial-toc-steps">${steps}</div>`;
  toc.querySelectorAll('[data-toc-panel]').forEach(link => link.addEventListener('click', event => {
    event.preventDefault();
    const panelIndex = link.dataset.tocPanel;
    const button = article.querySelector(`[data-tutorial-tab="${panelIndex}"]`);
    const target = article.querySelector(link.getAttribute('href'));
    button?.click();
    if (!target) return;
    history.replaceState({}, '', link.getAttribute('href'));
    requestAnimationFrame(() => target.scrollIntoView({ behavior:'smooth', block:'start' }));
  }));
  const initialTarget = location.hash ? article.querySelector(location.hash) : null;
  if (initialTarget) {
    const panel = initialTarget.closest('[data-tutorial-panel]');
    if (panel) article.querySelector(`[data-tutorial-tab="${panel.dataset.tutorialPanel}"]`)?.click();
    requestAnimationFrame(() => initialTarget.scrollIntoView({ block:'start' }));
  }
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
    const displayLabel = label.replace(/^Week\s+\d{2}\s+(?:In-Class|Challenge|Take-Home|Lecture|Setup)\s+—\s+/i, '');
    const viewer = `viewer.html?file=${encodeURIComponent(href)}&title=${encodeURIComponent(label)}`;
    return `<div class="file-action" data-kind="${escapeHtml(kind.toLowerCase())}" title="${escapeHtml(label)}"><span class="file-name">${escapeHtml(displayLabel)}</span><span class="file-type">${type}</span><span class="file-links"><a class="file-preview"${external ? '' : ' data-file-preview'} href="${external ? escapeHtml(href) : viewer}"${external ? ' target="_blank" rel="noopener"' : ''}><span class="lang-ja jp" lang="ja">${external ? '開く' : 'プレビュー'}</span><span class="lang-en">${external ? 'OPEN' : 'PREVIEW'}</span></a>${external ? '' : `<a class="file-download" href="${escapeHtml(href)}" download><span class="lang-ja jp" lang="ja">ダウンロード</span><span class="lang-en">DOWNLOAD</span></a>`}</span></div>`;
  }).join('');
}

function tutorialsHtml(body) {
  const links = body.split('\n').map(line => line.trim()).filter(line => line.startsWith('- ')).map((line, index) => {
    const match = line.match(/^-\s*\[([^\]]+)\]\(([^\s)]+)\)/);
    if (!match) return '';
    const [, label, href] = match;
    const [rawJapaneseLabel, rawEnglishLabel = rawJapaneseLabel] = label.split(/\s+\/\s+/, 2);
    const japaneseLabel = rawJapaneseLabel.replace(/`/g, '');
    const englishLabel = rawEnglishLabel.replace(/`/g, '');
    const viewer = `viewer.html?file=${encodeURIComponent(href)}&title=${encodeURIComponent(label)}`;
    return `<a class="tutorial-link" data-file-preview href="${viewer}" aria-label="${escapeHtml(label)}"><span class="tutorial-number">${String(index + 1).padStart(2, '0')}</span><span class="tutorial-link-title"><strong class="lang-en">${escapeHtml(englishLabel)}</strong><strong class="lang-ja jp" lang="ja">${escapeHtml(japaneseLabel)}</strong></span><b aria-hidden="true">→</b></a>`;
  }).join('');
  if (!links) return '';
  return `<section class="week-tutorials"><div class="tutorials-intro"><p>WEEK 01 · TUTORIALS</p><h4 class="lang-en">Set up Python, one step at a time</h4><h4 class="lang-ja jp" lang="ja">Pythonを動かすまでの7ステップ</h4><small class="lang-en">Start at 01 and continue downward. Reopen any step when you need help.</small><small class="lang-ja jp" lang="ja">01から順番に進みます。困ったときは、必要なステップをもう一度開いてください。</small></div><nav class="tutorial-links" aria-label="Week 01 tutorials">${links}</nav></section>`;
}

function lectureTimelinesHtml(body) {
  const groups = body.split(/^###\s+/m).slice(1).map(group => {
    const [key, ...lines] = group.split('\n');
    const entries = lines.filter(line => /^-\s+/.test(line)).map(line => {
      const [year, title, ja, en, visual, url, credit = ''] = line.replace(/^-\s+/, '').split('|').map(value => value.trim());
      return { year, title, ja, en, visual, url, credit };
    });
    return { key:key.trim().toLowerCase(), entries };
  });
  const journey = groups.find(group => group.key === 'journey')?.entries || [];
  const languages = groups.find(group => group.key === 'languages')?.entries || [];
  if (!journey.length && !languages.length) return '';
  const visual = (item, kind) => /\.(?:svg|png|jpe?g|webp)$/i.test(item.visual)
    ? `<div class="history-object ${kind === 'languages' ? 'is-logo' : ''}"><span class="history-backdrop-year" aria-hidden="true">${escapeHtml(item.year)}</span><img src="${escapeHtml(item.visual)}" alt="${escapeHtml(item.title)}" loading="lazy"></div>`
    : `<div class="history-object is-type"><span class="history-backdrop-year" aria-hidden="true">${escapeHtml(item.year)}</span><strong aria-hidden="true">${escapeHtml(item.visual)}</strong></div>`;
  const panel = (items, kind, label, tabId) => {
    const slides = items.map((item, index) => `<article class="history-slide${index === 0 ? ' is-active' : ''}" data-history-slide="${index}"${index === 0 ? '' : ' hidden'}>${visual(item, kind)}<div class="history-story"><div class="history-meta"><span>${escapeHtml(item.year)}</span><span data-history-count>${String(index + 1).padStart(2, '0')} / ${String(items.length).padStart(2, '0')}</span></div><h5>${escapeHtml(item.title)}</h5><p class="lang-en">${escapeHtml(item.en)}</p><p class="lang-ja jp" lang="ja">${escapeHtml(item.ja)}</p><a class="history-source" href="${escapeHtml(item.url)}" target="_blank" rel="noopener"><span class="lang-en">EXPLORE ↗</span><span class="lang-ja jp" lang="ja">詳しく見る ↗</span></a>${item.credit ? `<a class="history-credit" href="${escapeHtml(item.credit)}" target="_blank" rel="noopener">IMAGE SOURCE ↗</a>` : ''}</div></article>`).join('');
    const rail = items.map((item, index) => `<button type="button" data-history-jump="${index}"${index === 0 ? ' class="is-active" aria-current="true"' : ''}><span>${escapeHtml(item.year)}</span><strong>${escapeHtml(item.title)}</strong></button>`).join('');
    return `<div id="timeline-${kind}" role="tabpanel" aria-labelledby="${tabId}" data-lecture-timeline-panel="${kind}"${kind === 'journey' ? '' : ' hidden'}><div class="history-explorer" data-history-explorer tabindex="0" aria-label="${escapeHtml(label)}" style="--history-items:${items.length}"><div class="history-stage">${slides}<div class="history-controls"><button type="button" data-history-prev aria-label="Previous item">←</button><span data-history-status>01 / ${String(items.length).padStart(2, '0')}</span><button type="button" data-history-next aria-label="Next item">→</button></div></div><nav class="history-rail" aria-label="${escapeHtml(label)} chronology">${rail}</nav></div></div>`;
  };
  return `<section class="lecture-timelines" data-lecture-timelines><div class="lecture-timeline-intro"><p>TRACE 01 · MACHINES ↔ LANGUAGES</p><h4 class="lang-en">Move through the machines and languages that changed what code could do.</h4><h4 class="lang-ja jp" lang="ja">一台ずつ触れて、コードでできることの変化をたどる。</h4></div><div class="lecture-timeline-tabs" role="tablist" aria-label="Lecture history"><button type="button" role="tab" aria-selected="true" aria-controls="timeline-journey" id="timeline-tab-journey" data-lecture-timeline-tab="journey"><span>MY PC JOURNEY</span><small class="lang-en">The machines that made me want to create</small><small class="lang-ja jp" lang="ja">「つくりたい」を育てたコンピュータ</small></button><button type="button" role="tab" aria-selected="false" aria-controls="timeline-languages" id="timeline-tab-languages" data-lecture-timeline-tab="languages" tabindex="-1"><span class="lang-en">LANGUAGES THAT CHANGED THE WORLD</span><span class="lang-ja jp" lang="ja">世界を変えたプログラミング言語</span><small class="lang-en">New ways to tell machines what we mean</small><small class="lang-ja jp" lang="ja">機械に意図を伝える、新しい方法</small></button></div>${panel(journey, 'journey', 'My PC Journey', 'timeline-tab-journey')}${panel(languages, 'languages', 'Languages that changed the world', 'timeline-tab-languages')}</section>`;
}

function setupLectureTimelineTabs(root = document) {
  root.querySelectorAll('[data-lecture-timelines]').forEach(group => {
    const buttons = [...group.querySelectorAll('[data-lecture-timeline-tab]')];
    const panels = [...group.querySelectorAll('[data-lecture-timeline-panel]')];
    const select = index => {
      buttons.forEach((button, buttonIndex) => {
        const active = buttonIndex === index;
        button.setAttribute('aria-selected', String(active));
        button.tabIndex = active ? 0 : -1;
      });
      panels.forEach((panel, panelIndex) => { panel.hidden = panelIndex !== index; });
    };
    buttons.forEach((button, index) => {
      button.addEventListener('click', () => select(index));
      button.addEventListener('keydown', event => {
        if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
        event.preventDefault();
        const next = (index + (event.key === 'ArrowRight' ? 1 : -1) + buttons.length) % buttons.length;
        select(next);
        buttons[next].focus();
      });
    });
    group.querySelectorAll('[data-history-explorer]').forEach(explorer => {
      const slides = [...explorer.querySelectorAll('[data-history-slide]')];
      const jumps = [...explorer.querySelectorAll('[data-history-jump]')];
      const previous = explorer.querySelector('[data-history-prev]');
      const next = explorer.querySelector('[data-history-next]');
      const status = explorer.querySelector('[data-history-status]');
      let current = 0;
      let pointerStart = null;
      const show = (requested, scrollRail = false) => {
        current = Math.max(0, Math.min(slides.length - 1, requested));
        slides.forEach((slide, index) => {
          slide.hidden = index !== current;
          slide.classList.toggle('is-active', index === current);
        });
        jumps.forEach((jump, index) => {
          jump.classList.toggle('is-active', index === current);
          if (index === current) jump.setAttribute('aria-current', 'true');
          else jump.removeAttribute('aria-current');
        });
        if (status) status.textContent = `${String(current + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
        if (previous) previous.disabled = current === 0;
        if (next) next.disabled = current === slides.length - 1;
        explorer.style.setProperty('--history-progress', `${((current + 1) / slides.length) * 100}%`);
        if (scrollRail) jumps[current]?.scrollIntoView({ behavior:'smooth', block:'nearest', inline:'center' });
      };
      jumps.forEach((jump, index) => jump.addEventListener('click', () => show(index, true)));
      previous?.addEventListener('click', () => show(current - 1, true));
      next?.addEventListener('click', () => show(current + 1, true));
      explorer.addEventListener('keydown', event => {
        if (!['ArrowLeft', 'ArrowRight'].includes(event.key) || event.target.closest('[role="tab"]')) return;
        event.preventDefault();
        show(current + (event.key === 'ArrowRight' ? 1 : -1), true);
      });
      const stage = explorer.querySelector('.history-stage');
      stage?.addEventListener('pointerdown', event => {
        if (event.target.closest('a, button')) return;
        pointerStart = event.clientX;
      });
      stage?.addEventListener('pointerup', event => {
        if (pointerStart === null) return;
        const distance = event.clientX - pointerStart;
        pointerStart = null;
        if (Math.abs(distance) > 45) show(current + (distance < 0 ? 1 : -1), true);
      });
      stage?.addEventListener('pointercancel', () => { pointerStart = null; });
      show(0);
    });
  });
}

function section(week, key) { return week.sections.find(item => item.title.toLowerCase().startsWith(key.toLowerCase())); }
function previewAll() { return new URLSearchParams(location.search).get('preview') === 'all'; }
function isAvailable(week) { return previewAll() || week.week === 1 || new Date() >= new Date(week.publish_at); }

function releaseDateLabels(value) {
  const date = new Date(value);
  return {
    en: new Intl.DateTimeFormat('en-US', { month:'short', day:'numeric', timeZone:'Asia/Tokyo' }).format(date),
    ja: new Intl.DateTimeFormat('ja-JP', { month:'long', day:'numeric', timeZone:'Asia/Tokyo' }).format(date)
  };
}

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

function agendaWeek(w, defaultOpen = false) {
  const available = isAvailable(w);
  const id = `week-${String(w.week).padStart(2,'0')}`;
  const overview = `<p class="week-overview lang-en">${escapeHtml(w.overview || '')}</p><p class="week-overview lang-ja jp" lang="ja">${escapeHtml(w.overview_ja || '')}</p>`;
  const summary = `<div class="week-index"><span class="week-number">${String(w.week).padStart(2,'0')}</span>${courseScheduleHtml(w)}</div><div class="week-summary-copy"><span class="week-phase">${escapeHtml(w.phase)}</span><span class="week-title lang-en">${escapeHtml(w.title)}</span><span class="week-title lang-ja jp" lang="ja">${escapeHtml(w.title_ja || '')}</span>${overview}</div>`;

  if (!available) {
    const release = releaseDateLabels(w.publish_at);
    return `<article class="week week--locked" id="${id}"><div class="week-summary">${summary}<span class="week-release"><span class="lang-en">Available ${escapeHtml(release.en)}</span><span class="lang-ja jp" lang="ja">${escapeHtml(release.ja)} 公開</span></span></div></article>`;
  }

  const resources = section(w, 'Resources');
  const lecture = section(w, 'Lecture Flow');
  const lectureTimelines = section(w, 'Lecture Timelines');
  const notebook = section(w, 'In-Class Notebook');
  const challenge = section(w, 'In-Class Challenge');
  const homework = section(w, 'Take-Home Assignment');
  const tutorials = section(w, 'Tutorials');
  const lectureFiles = resources ? resourcesHtml(resources.body, ['lecture']) : '';
  const classFiles = resources ? resourcesHtml(resources.body, ['notebook','fundamentals','support','experiment','challenge','data']) : '';
  const homeworkFiles = resources ? resourcesHtml(resources.body, ['homework']) : '';
  const inClassCopy = `${tutorials ? tutorialsHtml(tutorials.body) : ''}${notebook ? `<div class="class-task"><h4><span class="lang-en">GUIDED NOTEBOOK</span><span class="lang-ja jp" lang="ja">授業内ノートブック</span></h4>${bilingualHtml(notebook.body)}</div>` : ''}${challenge ? `<div class="class-task class-task--challenge"><h4><span class="lang-en">FINAL 30-MINUTE CHALLENGE</span><span class="lang-ja jp" lang="ja">最後の30分チャレンジ</span></h4>${bilingualHtml(challenge.body)}</div>` : ''}`;
  const resourceBlock = files => files ? `<div class="section-resources"><p class="resources-label"><span class="lang-en">FILES</span><span class="lang-ja jp" lang="ja">使用するファイル</span></p>${files}</div>` : '';
  const lectureResource = resources?.body.split('\n').map(line => line.trim()).find(line => /\{lecture\}$/.test(line));
  const lectureMatch = lectureResource?.match(/^[-]\s*\[([^\]]+)\]\(([^\s)]+)\)/);
  const lecturePath = lectureMatch?.[2] || '';
  const lectureViewer = lecturePath ? `viewer.html?file=${encodeURIComponent(lecturePath)}&title=${encodeURIComponent(lectureMatch[1])}` : '';
  const lectureThumb = lecturePath && fileType(lecturePath, false) === 'PDF' ? pdfPageImage(lecturePath, w.week === 1 ? 5 : 1) : '';
  const lectureDeck = lectureFiles ? `<aside class="lecture-deck-panel"><p class="lecture-deck-label"><span class="lang-en">LECTURE SLIDES</span><span class="lang-ja jp" lang="ja">講義スライド</span></p>${lectureThumb ? `<a class="lecture-deck-thumbnail" data-file-preview href="${lectureViewer}" aria-label="${escapeHtml(lectureMatch[1])}"><img src="${escapeHtml(lectureThumb)}" alt="${escapeHtml(lectureMatch[1])} slide preview" loading="lazy"></a>` : ''}<p class="lecture-deck-title">${escapeHtml(lectureMatch?.[1] || '')}</p></aside>` : '';
  const lectureVisual = lectureTimelines ? lectureTimelinesHtml(lectureTimelines.body) : lectureDeck;
  return `<details class="week" id="${id}"${defaultOpen ? ' open' : ''}><summary class="week-summary">${summary}<span class="week-toggle"><span class="week-toggle-closed"><span class="lang-en">OPEN WEEK</span><span class="lang-ja jp" lang="ja">週を開く</span></span><span class="week-toggle-open"><span class="lang-en">CLOSE WEEK</span><span class="lang-ja jp" lang="ja">週を閉じる</span></span><b aria-hidden="true">↓</b></span></summary><div class="week-body"><section class="course-section course-section--lecture${lectureTimelines ? ' has-timelines' : ''}"><header><span>01</span><div><p>LECTURE</p><h3 class="lang-en">This week’s lecture</h3><h3 class="lang-ja jp" lang="ja">今週の講義</h3></div></header><div class="course-section-content">${lecture ? bilingualHtml(lecture.body) : ''}${lectureVisual}</div></section><section class="course-section course-section--in-class"><header><span>02</span><div><p>IN CLASS</p><h3 class="lang-en">Practice in class</h3><h3 class="lang-ja jp" lang="ja">授業内課題</h3></div></header><div class="course-section-content">${inClassCopy}${resourceBlock(classFiles)}</div></section><section class="course-section course-section--homework"><header><span>03</span><div><p>HOMEWORK</p><h3 class="lang-en">Make something of your own</h3><h3 class="lang-ja jp" lang="ja">宿題</h3></div></header><div class="course-section-content">${homework ? bilingualHtml(homework.body) : ''}${resourceBlock(homeworkFiles)}</div></section></div></details>`;
}

function renderAgenda(weeks) {
  const root = document.querySelector('[data-agenda]');
  if (!root) return;
  const preview = previewAll();
  const today = new Intl.DateTimeFormat('en-CA', { timeZone:'Asia/Tokyo', year:'numeric', month:'2-digit', day:'2-digit' }).format(new Date());
  const current = weeks.find(w => isAvailable(w) && w.course_date >= today) || [...weeks].reverse().find(isAvailable) || weeks[0];
  const heading = `<section class="agenda-heading wrap"><div><p class="eyebrow">2026–2 PROGRAMMING / プログラミング</p><h1><span class="lang-en">Course agenda</span><span class="lang-ja jp" lang="ja">授業予定</span></h1></div><p><span class="lang-en">Thursday · Period 3 · 13:10–14:50</span><span class="lang-ja jp" lang="ja">木曜日 · 3限 · 13:10–14:50</span></p>${preview ? '<span class="preview-notice">PREVIEW · ALL WEEKS</span>' : ''}</section>`;
  root.innerHTML = `${heading}<section class="week-list wrap">${weeks.map(w => agendaWeek(w, preview || w.week === current.week)).join('')}</section>`;
}

function setupAgendaToggles() {
  const root = document.querySelector('[data-agenda]');
  if (!root) return;
  const state = new URLSearchParams(location.search);
  const requestedOpen = new Set((state.get('open') || '').split(',').filter(Boolean));
  if (requestedOpen.size) root.querySelectorAll('details.week').forEach(week => { week.open = requestedOpen.has(week.id.replace('week-', '')); });
  root.querySelectorAll('details.week').forEach(week => week.addEventListener('toggle', () => {
    const url = new URL(location.href);
    const openWeeks = [...root.querySelectorAll('details.week[open]')].map(item => item.id.replace('week-', ''));
    if (openWeeks.length) url.searchParams.set('open', openWeeks.join(','));
    else url.searchParams.delete('open');
    url.searchParams.delete('scroll');
    history.replaceState({}, '', `${url.pathname}${url.search}${url.hash}`);
  }));
  const returnScroll = Number(state.get('scroll'));
  if (Number.isFinite(returnScroll) && returnScroll > 0) requestAnimationFrame(() => window.scrollTo(0, returnScroll));
}

function agendaReturnUrl() {
  const url = new URL(location.href);
  const root = document.querySelector('[data-agenda]');
  if (root) {
    const openWeeks = [...root.querySelectorAll('details.week[open]')].map(week => week.id.replace('week-', ''));
    if (openWeeks.length) url.searchParams.set('open', openWeeks.join(','));
    else url.searchParams.delete('open');
  }
  url.searchParams.set('scroll', String(Math.round(window.scrollY)));
  return `${url.pathname}${url.search}${url.hash}`;
}

function setupPreviewLinks() {
  const saveReturnDestination = event => {
    if (!(event.target instanceof Element)) return;
    const link = event.target.closest('a[data-file-preview]');
    if (!link) return;
    const viewer = new URL(link.href, location.href);
    viewer.searchParams.set('return', agendaReturnUrl());
    link.href = viewer.href;
  };
  document.addEventListener('pointerdown', saveReturnDestination);
  document.addEventListener('click', saveReturnDestination);
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

function pdfPageImage(file, page) {
  const slug = file.replace(/\//g, '--').replace(/\.pdf$/i, '');
  return `assets/pdf-previews/${slug}/page-${String(page).padStart(2, '0')}.jpg`;
}

function setupPdfPaging(file, title, pageCount, initialPage) {
  const documentViewer = document.querySelector('[data-pdf-document]');
  if (!documentViewer) return;
  const image = documentViewer.querySelector('[data-pdf-page-image]');
  const input = documentViewer.querySelector('[data-pdf-page-input]');
  const currentLabels = documentViewer.querySelectorAll('[data-pdf-current]');
  const previousButtons = documentViewer.querySelectorAll('[data-pdf-previous]');
  const nextButtons = documentViewer.querySelectorAll('[data-pdf-next]');
  let currentPage = Math.min(pageCount, Math.max(1, initialPage));
  const update = requestedPage => {
    currentPage = Math.min(pageCount, Math.max(1, Number(requestedPage) || 1));
    image.src = pdfPageImage(file, currentPage);
    image.alt = `${title} — page ${currentPage} of ${pageCount}`;
    input.value = String(currentPage);
    currentLabels.forEach(label => { label.textContent = String(currentPage); });
    previousButtons.forEach(button => { button.disabled = currentPage === 1; });
    nextButtons.forEach(button => { button.disabled = currentPage === pageCount; });
    const url = new URL(location.href);
    if (currentPage === 1) url.searchParams.delete('page');
    else url.searchParams.set('page', String(currentPage));
    history.replaceState({}, '', `${url.pathname}${url.search}${url.hash}`);
    if (currentPage < pageCount) {
      const nextImage = new Image();
      nextImage.src = pdfPageImage(file, currentPage + 1);
    }
  };
  previousButtons.forEach(button => button.addEventListener('click', () => update(currentPage - 1)));
  nextButtons.forEach(button => button.addEventListener('click', () => update(currentPage + 1)));
  input.addEventListener('change', () => update(input.value));
  input.addEventListener('keydown', event => {
    if (event.key === 'Enter') { event.preventDefault(); update(input.value); input.select(); }
  });
  document.addEventListener('keydown', event => {
    if (event.target instanceof HTMLInputElement) return;
    if (event.key === 'ArrowLeft') update(currentPage - 1);
    if (event.key === 'ArrowRight') update(currentPage + 1);
  });
  update(currentPage);
}

async function setupFileViewer() {
  const root = document.querySelector('[data-file-viewer]');
  if (!root) return;
  const params = new URLSearchParams(location.search);
  const file = params.get('file') || '';
  const title = params.get('title') || file.split('/').pop() || 'File preview';
  const fallback = new URL('index.html', location.href);
  const requestedReturn = params.get('return');
  let returnUrl = fallback.href;
  if (requestedReturn) {
    try {
      const candidate = new URL(requestedReturn, location.href);
      if (candidate.protocol === location.protocol && candidate.host === location.host && (candidate.pathname === '/' || /\/(?:index|agenda)\.html$/.test(candidate.pathname))) returnUrl = candidate.href;
    } catch (_) { /* Use the agenda as a safe fallback. */ }
  }
  const back = `<a class="viewer-back" href="${escapeHtml(returnUrl)}"><span class="lang-en">← BACK TO AGENDA</span><span class="lang-ja jp" lang="ja">← 授業予定に戻る</span></a>`;
  const actions = download => `<div class="viewer-actions">${back}${download}</div>`;
  if (!/^(weeks|content)\//.test(file)) { root.innerHTML = `<div class="viewer-title"><p class="eyebrow">FILE PREVIEW</p><h1>${escapeHtml(title)}</h1>${actions('')}</div><p class="agenda-locked">File preview is unavailable.</p>`; return; }
  const extension = file.split('.').pop().toLowerCase();
  const isTutorial = /^weeks\/week-01\/tutorials\//.test(file);
  const download = isTutorial ? '' : `<a class="file-download viewer-download" href="${escapeHtml(file)}" download>↓ <span>DOWNLOAD</span></a>`;
  try {
    if (extension === 'pdf') {
      const pageCount = pdfPageCounts[file] || 1;
      const initialPage = Number(params.get('page')) || 1;
      const pager = `<nav class="pdf-pager" aria-label="PDF pages"><button type="button" data-pdf-previous><span aria-hidden="true">←</span> <span class="lang-en">PREVIOUS</span><span class="lang-ja jp" lang="ja">前へ</span></button><label><span class="lang-en">PAGE</span><span class="lang-ja jp" lang="ja">ページ</span> <input data-pdf-page-input type="number" min="1" max="${pageCount}" value="${Math.min(pageCount, Math.max(1, initialPage))}" aria-label="Page number"> <span>/ ${pageCount}</span></label><button type="button" data-pdf-next><span class="lang-en">NEXT</span><span class="lang-ja jp" lang="ja">次へ</span> <span aria-hidden="true">→</span></button></nav>`;
      root.innerHTML = `<div class="viewer-title"><p class="eyebrow">PDF PREVIEW · ${pageCount} PAGES</p><h1>${escapeHtml(title)}</h1>${actions(download)}</div><section class="pdf-document" data-pdf-document>${pager}<figure class="pdf-preview"><img data-pdf-page-image src="${escapeHtml(pdfPageImage(file, initialPage))}" alt="${escapeHtml(title)} — page ${initialPage} of ${pageCount}"></figure><div class="pdf-page-status" aria-live="polite"><span class="lang-en">PAGE <b data-pdf-current>${initialPage}</b> OF ${pageCount}</span><span class="lang-ja jp" lang="ja"><b data-pdf-current>${initialPage}</b> / ${pageCount} ページ</span></div></section>`;
      setupPdfPaging(file, title, pageCount, initialPage);
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
      root.innerHTML = `<div class="viewer-title"><p class="eyebrow">JUPYTER NOTEBOOK · ${cells.length} CELLS</p><h1>${escapeHtml(title)}</h1>${actions(download)}</div><section class="notebook-shell"><header class="notebook-toolbar"><span class="notebook-tab">${escapeHtml(title)} · Preview</span><span class="notebook-run">▶ Run All</span><span class="notebook-kernel">Python 3.12</span></header><article class="notebook-preview">${preview}</article></section>`;
      return;
    }
    if (isTutorial) {
      root.innerHTML = `<div class="viewer-title tutorial-viewer-title"><p class="eyebrow">WEEK 01 · TUTORIAL</p><h1>${escapeHtml(title)}</h1>${actions('')}</div><div class="tutorial-layout"><aside class="tutorial-toc" data-tutorial-toc></aside><article class="markdown-preview tutorial-preview">${tutorialMarkdownHtml(source.replace(/^#\s+.+\n?/, ''))}</article></div>${tutorialNavigationHtml(file, returnUrl)}`;
      setupTutorialTabs(root);
      await setupTutorialToc(root, file, returnUrl, source);
      return;
    }
    root.innerHTML = `<div class="viewer-title"><p class="eyebrow">MARKDOWN PREVIEW</p><h1>${escapeHtml(title)}</h1>${actions(download)}</div><article class="markdown-preview">${markdownHtml(source.replace(/^#\s+(.+)$/m, '**$1**'))}</article>`;
  } catch (error) { root.innerHTML = `<div class="viewer-title"><p class="eyebrow">FILE PREVIEW</p><h1>${escapeHtml(title)}</h1>${actions(download)}</div><p class="agenda-locked">Could not preview ${escapeHtml(title)}.</p>`; }
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
  setupPreviewLinks();
  setupFileViewer();
  try { const weeks = await loadWeeks(); renderAgenda(weeks); setupAgendaToggles(); setupLectureTimelineTabs(); }
  catch (error) { console.error(error); document.querySelectorAll('[data-agenda]').forEach(node => { node.innerHTML = '<p class="agenda-locked">Course content could not load. Please refresh the page.</p>'; }); }
});
