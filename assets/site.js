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

function highlightTimelineCode(code) {
  const strings = [];
  let source = escapeHtml(code).replace(/(&quot;.*?&quot;|'[^']*')/g, value => {
    const token = `@@STRING_${String.fromCharCode(65 + strings.length)}@@`;
    strings.push(value);
    return token;
  });
  source = source
    .replace(/\b(PROGRAM|PRINT|END|IDENTIFICATION|DIVISION|PROGRAM-ID|PROCEDURE|DISPLAY|STOP|RUN|class|public|static|void|int|return|const|let|when|for|seconds|SELECT|AS|package|import|func|fn|MOV|ADD|GOTO)\b/gi, '<span class="syntax-keyword">$1</span>')
    .replace(/\b(print|printf|println|log|show|say|main|format|Println)\b/gi, '<span class="syntax-function">$1</span>')
    .replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="syntax-number">$1</span>');
  strings.forEach((value, index) => {
    source = source.replace(`@@STRING_${String.fromCharCode(65 + index)}@@`, `<span class="syntax-string">${value}</span>`);
  });
  return source;
}

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
  const buttons = tabs.map(([, label], index) => `<button type="button" class="ui-tab" role="tab" id="${id}-tab-${index}" aria-controls="${id}-panel-${index}" aria-selected="${index === 0}" tabindex="${index === 0 ? '0' : '-1'}" data-tutorial-tab="${index}">${escapeHtml(label)}</button>`).join('');
  const panels = tabs.map(([, label, body], index) => {
    const nestedBody = markdownHtml(body.trim()).replace(/<(\/?)h([34])>/g, (_, closing, level) => `<${closing}h${Number(level) + 1}>`);
    return `<section role="tabpanel" id="${id}-panel-${index}" aria-labelledby="${id}-tab-${index}" data-tutorial-panel="${index}"${index === 0 ? '' : ' hidden'}><h3>${escapeHtml(label)}</h3>${nestedBody}</section>`;
  }).join('');
  return `<div class="tutorial-tabs" data-tutorial-tabs><div class="tutorial-tab-list ui-tabs" role="tablist" aria-label="Operating system">${buttons}</div>${panels}</div>`;
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
      return `<a class="${levelClass}" href="${escapeHtml(href)}"${panelData}>${escapeHtml(section.label)}</a>`;
    }).join('');
    const firstSection = outline[0];
    const titleHref = current ? `#${firstSection?.id || 'tutorial-section-1'}` : tutorialLink(item, returnUrl);
    const titlePanel = current && firstSection && firstSection.panelIndex !== '' ? ` data-toc-panel="${escapeHtml(firstSection.panelIndex)}"` : '';
    const sectionId = `tutorial-toc-sections-${index + 1}`;
    return `<div class="tutorial-toc-step${current ? ' is-current is-open' : ''}"><div class="tutorial-toc-row"><span class="tutorial-toc-number">${String(index + 1).padStart(2, '0')}</span><a class="tutorial-toc-step-link" href="${escapeHtml(titleHref)}"${titlePanel}><span class="lang-en">${escapeHtml(item.en)}</span><span class="lang-ja jp" lang="ja">${escapeHtml(item.ja)}</span></a><button type="button" class="tutorial-toc-expand" data-toc-expand aria-controls="${sectionId}" aria-expanded="${current}" aria-label="${escapeHtml(item.ja)}の項目を開閉">⌄</button></div><nav id="${sectionId}" aria-label="${escapeHtml(item.en)} sections"${current ? '' : ' hidden'}>${sectionLinks}</nav></div>`;
  }).join('');
  toc.innerHTML = `<header><a class="tutorial-toc-title" href="#tutorial-section-1"><span class="lang-en">TUTORIAL INDEX</span><span class="lang-ja jp" lang="ja">チュートリアル 目次</span></a><span>01—07</span></header><div class="tutorial-toc-steps">${steps}</div>`;
  toc.querySelectorAll('[data-toc-expand]').forEach(button => button.addEventListener('click', () => {
    const sections = toc.querySelector(`#${button.getAttribute('aria-controls')}`);
    const expanded = button.getAttribute('aria-expanded') === 'true';
    button.setAttribute('aria-expanded', String(!expanded));
    button.closest('.tutorial-toc-step').classList.toggle('is-open', !expanded);
    if (sections) sections.hidden = expanded;
  }));
  toc.querySelector('.tutorial-toc-title')?.addEventListener('click', event => {
    const firstHeading = article.querySelector('#tutorial-section-1');
    if (!firstHeading) return;
    event.preventDefault();
    history.replaceState({}, '', '#tutorial-section-1');
    firstHeading.scrollIntoView({ behavior:'smooth', block:'start' });
  });
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

async function setupCourseGuide() {
  const root = document.querySelector('[data-course-guide]');
  if (!root) return;
  try {
    const response = await fetch('content/course-guide.md', { cache:'no-cache' });
    if (!response.ok) throw new Error('Could not load course guide');
    const guide = parseFrontMatter(await response.text());
    const sections = guide.sections.map(item => {
      const [ja, en = ja] = item.title.split(' / ');
      const id = `guide-${en.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}`;
      return { ...item, ja, en, id };
    });
    const label = item => `<span class="lang-ja jp" lang="ja">${escapeHtml(item.ja)}</span><span class="lang-en">${escapeHtml(item.en)}</span>`;
    const weights = [guide.grade_weekly, guide.grade_project, guide.grade_final].map(value => Number(value));
    const validWeights = weights.every(value => Number.isFinite(value) && value >= 0) && weights.reduce((sum, value) => sum + value, 0) === 100;
    const gradeChart = validWeights ? `<div class="guide-grade-chart" role="img" aria-label="Weekly assignments ${weights[0]} percent; final project ${weights[1]} percent; final in-class challenge ${weights[2]} percent"><div class="guide-grade-bar"><span class="guide-grade-weekly" style="width:${weights[0]}%">${weights[0]}%</span><span class="guide-grade-project" style="width:${weights[1]}%">${weights[1]}%</span><span class="guide-grade-final" style="width:${weights[2]}%">${weights[2]}%</span></div><div class="guide-grade-key"><div><span class="guide-grade-swatch guide-grade-weekly"></span><span class="lang-ja jp" lang="ja">毎週の課題</span><span class="lang-en">Weekly assignments</span><strong>${weights[0]}%</strong></div><div><span class="guide-grade-swatch guide-grade-project"></span><span class="lang-ja jp" lang="ja">最終プロジェクト</span><span class="lang-en">Final project</span><strong>${weights[1]}%</strong></div><div><span class="guide-grade-swatch guide-grade-final"></span><span class="lang-ja jp" lang="ja">授業内チャレンジ</span><span class="lang-en">Final in-class challenge</span><strong>${weights[2]}%</strong></div></div></div>` : '';
    root.innerHTML = `<header class="guide-opening"><p class="eyebrow">2026–2 PROGRAMMING / COURSE GUIDE</p><h1><span class="lang-ja jp" lang="ja">${escapeHtml(guide.title_ja)}</span><span class="lang-en">${escapeHtml(guide.title)}</span></h1><p class="guide-lead lang-ja jp" lang="ja">${escapeHtml(guide.dek_ja)}</p><p class="guide-lead lang-en">${escapeHtml(guide.dek)}</p></header><div class="guide-sections">${sections.map(item => `<section class="guide-section${item.en === 'Grading' ? ' guide-section--grading' : ''}" id="${item.id}"><header><h2>${label(item)}</h2></header><div class="guide-section-body">${item.en === 'Grading' ? gradeChart : ''}${bilingualHtml(item.body)}</div></section>`).join('')}</div>`;
  } catch (error) {
    console.error(error);
    root.innerHTML = '<p class="agenda-locked">The course guide could not load. Please refresh the page.</p>';
  }
}

async function setupFinalProjectPage() {
  const root = document.querySelector('[data-final-project]');
  if (!root) return;
  let returnUrl = 'guide.html';
  const requestedReturn = new URLSearchParams(location.search).get('return');
  if (requestedReturn) {
    try {
      const candidate = new URL(requestedReturn, location.href);
      if (candidate.protocol === location.protocol && candidate.host === location.host && /\/(?:index|agenda|guide)\.html$/.test(candidate.pathname)) returnUrl = candidate.href;
    } catch (_) { /* Keep the course guide as the safe default. */ }
  }
  const backToGuide = /\/guide\.html$/.test(new URL(returnUrl, location.href).pathname);
  try {
    const response = await fetch('content/final-project.md', { cache:'no-cache' });
    if (!response.ok) throw new Error('Could not load final project requirements');
    const project = parseFrontMatter(await response.text());
    const sections = project.sections.map(item => {
      const [ja, en = ja] = item.title.split(' / ');
      const id = `project-${en.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}`;
      return `<section class="project-section" id="${id}"><header><h2><span class="lang-ja jp" lang="ja">${escapeHtml(ja)}</span><span class="lang-en">${escapeHtml(en)}</span></h2></header><div class="project-section-body">${bilingualHtml(item.body)}</div></section>`;
    }).join('');
    root.innerHTML = `<header class="project-opening"><a class="project-back" href="${escapeHtml(returnUrl)}"><span class="lang-ja jp" lang="ja">← ${backToGuide ? 'この授業について' : '授業予定'}に戻る</span><span class="lang-en">← Back to ${backToGuide ? 'course guide' : 'agenda'}</span></a><p class="eyebrow">2026–2 PROGRAMMING / FINAL PROJECT</p><h1><span class="lang-ja jp" lang="ja">${escapeHtml(project.title_ja)}</span><span class="lang-en">${escapeHtml(project.title)}</span></h1>${homeworkDeadlineHtml({ homework_due:project.due_at })}<p class="project-meta"><span class="lang-ja jp" lang="ja">成績の20% · UNIPA</span><span class="lang-en">20% of course grade · UNIPA</span></p></header><div class="project-sections">${sections}</div>`;
  } catch (error) {
    console.error(error);
    root.innerHTML = '<p class="agenda-locked">The final project requirements could not load. Please refresh the page.</p>';
  }
}

function fileType(href, external) {
  if (external) return 'LINK';
  const extension = href.split('?')[0].split('.').pop().toLowerCase();
  return ({ pdf:'PDF', ipynb:'IPYNB', csv:'CSV', md:'MD', py:'PY', html:'HTML', png:'PNG', jpg:'JPG', jpeg:'JPG', gif:'GIF', zip:'ZIP' })[extension] || 'FILE';
}

function resourcesHtml(body, onlyKinds = []) {
  return body.split('\n').map(raw => raw.trim()).filter(line => line.startsWith('- ')).map(line => {
    const match = line.match(/^-\s*\[([^\]]+)\]\(([^\s)]+)\)(?:\s*\{([^}]+)\})?$/);
    if (!match) return '';
    const [, label, href, kind = 'support'] = match;
    if (onlyKinds.length && !onlyKinds.includes(kind.toLowerCase())) return '';
    if (href === 'content/final-project.md') return `<a class="project-resource-link" data-project-link href="final-project.html"><span><span class="lang-ja jp" lang="ja">最終プロジェクト要項</span><span class="lang-en">Final Project Requirements</span></span><b aria-hidden="true">→</b></a>`;
    const external = /^https?:/.test(href);
    const type = fileType(href, external);
    const displayLabel = label.replace(/^Week\s+\d{2}\s+(?:In-Class|Challenge|Take-Home|Homework|Lecture|Setup)\s+—\s+/i, '').replace(/\s+Template$/i, '');
    const viewer = `viewer.html?file=${encodeURIComponent(href)}&title=${encodeURIComponent(label)}`;
    const direct = external || type === 'HTML';
    return `<div class="file-action" data-kind="${escapeHtml(kind.toLowerCase())}" title="${escapeHtml(label)}"><span class="file-name">${escapeHtml(displayLabel)}</span><span class="file-type">${type}</span><span class="file-links"><a class="file-preview"${external ? '' : type === 'HTML' ? ' data-lecture-page' : ' data-file-preview'} href="${direct ? escapeHtml(href) : viewer}" aria-label="${escapeHtml(label)} — ${direct ? '開く / Open' : 'プレビュー / Preview'}"${external ? ' target="_blank" rel="noopener"' : ''}><span class="lang-ja jp" lang="ja">${direct ? '開く' : 'プレビュー'}</span><span class="lang-en">${direct ? 'Open' : 'Preview'}</span></a>${external ? '' : `<a class="file-download" href="${escapeHtml(href)}" download aria-label="${escapeHtml(label)} — ダウンロード / Download"><span class="lang-ja jp" lang="ja">ダウンロード</span><span class="lang-en">Download</span></a>`}</span></div>`;
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
    return `<a class="tutorial-link" data-file-preview href="${viewer}" aria-label="${escapeHtml(label)}"><span class="tutorial-number">${String(index + 1).padStart(2, '0')}</span><span class="tutorial-link-title"><strong class="lang-en">${escapeHtml(englishLabel)}</strong><strong class="lang-ja jp" lang="ja">${escapeHtml(japaneseLabel)}</strong></span><b aria-hidden="true">↗</b></a>`;
  }).filter(Boolean);
  if (!links.length) return '';
  return `<section class="week-tutorials"><div class="tutorials-intro"><p>TUTORIALS / チュートリアル</p><h4 class="lang-en">From setup to your first code</h4><h4 class="lang-ja jp" lang="ja">準備から、最初のコードまで</h4></div><nav class="tutorial-links" aria-label="Week 01 tutorials"><p class="tutorial-group-label"><span class="lang-en">SET UP · 01–04</span><span class="lang-ja jp" lang="ja">準備 · 01–04</span></p>${links.slice(0, 4).join('')}<p class="tutorial-group-label"><span class="lang-en">TRY PYTHON · 05–07</span><span class="lang-ja jp" lang="ja">動かす · 05–07</span></p>${links.slice(4).join('')}</nav></section>`;
}

function lectureTimelinesHtml(body) {
  const groups = body.split(/^###\s+/m).slice(1).map(group => {
    const [key, ...lines] = group.split('\n');
    const rows = lines.filter(line => /^-\s+/.test(line)).map(line => line.replace(/^-\s+/, '').split('|').map(value => value.trim()));
    const entries = rows.map(parts => {
      const [year, title, ja, en, visual, url, credit = '', sampleRaw = '', famousJa = '', famousEn = '', usersJa = '', usersEn = '', popularityRaw = '', gamesRaw = ''] = parts;
      const popularity = Number.parseFloat(popularityRaw);
      const games = gamesRaw.split(';').map(game => {
        const [gameTitle, image, link] = game.split('~').map(value => value.trim());
        return gameTitle && image && link ? { title:gameTitle, image, link } : null;
      }).filter(Boolean);
      return { year, title, ja, en, visual, url, credit, games, sample:sampleRaw.replaceAll('⏎', '\n'), famousJa, famousEn, usersJa, usersEn, popularity:Number.isFinite(popularity) ? popularity : 0 };
    });
    return { key:key.trim().toLowerCase(), entries, rows };
  });
  const journey = groups.find(group => group.key === 'journey')?.entries || [];
  const languages = groups.find(group => group.key === 'languages')?.entries || [];
  const pythonRows = groups.find(group => group.key === 'python')?.rows || [];
  if (!journey.length && !languages.length) return '';
  const yearValue = value => {
    const year = Number.parseInt(value, 10);
    return /s$/i.test(value) ? year + 5 : year;
  };
  const visual = (item, kind, className) => /\.(?:svg|png|jpe?g|webp)$/i.test(item.visual)
    ? `<span class="${className} ${kind === 'languages' ? 'is-logo' : ''}"><img src="${escapeHtml(item.visual)}" alt="${escapeHtml(item.title)}" loading="lazy"></span>`
    : `<span class="${className} is-type" aria-hidden="true"><strong>${escapeHtml(item.visual)}</strong></span>`;
  const pythonPanel = rows => {
    const items = rows.map(([kind, key, titleEn, titleJa, textEn, textJa, detail = '', secondary = '', url = '']) => ({
      kind, key, titleEn, titleJa, textEn, textJa, url,
      visual: kind === 'milestone' ? detail : '',
      credit: kind === 'milestone' ? secondary : '',
      sample: kind === 'domain' ? detail.replaceAll('⏎', '\n') : '',
      output: kind === 'domain' ? secondary : ''
    }));
    const milestones = items.filter(item => item.kind === 'milestone');
    const metrics = items.filter(item => item.kind === 'metric');
    const domains = items.filter(item => item.kind === 'domain');
    if (!items.length) return '';
    const years = milestones.map(item => Number(item.key));
    const minimum = Math.min(...years);
    const maximum = Math.max(...years);
    const historyPoints = milestones.map((item, index) => {
      const x = 5 + ((Number(item.key) - minimum) / Math.max(1, maximum - minimum)) * 90;
      return `<button type="button" class="python-history-point${index % 2 ? ' is-lower' : ''}${index === 0 ? ' is-active' : ''}" style="--python-year-x:${x}%" data-python-history-jump="${index}"${index === 0 ? ' aria-current="true"' : ''}><i aria-hidden="true"></i><b>${escapeHtml(item.key)}</b><span class="lang-en">${escapeHtml(item.titleEn)}</span><span class="lang-ja jp" lang="ja">${escapeHtml(item.titleJa)}</span></button>`;
    }).join('');
    const historyDetails = milestones.map((item, index) => `<article class="python-history-detail${index === 0 ? ' is-active' : ''}${item.visual ? ' has-visual' : ''}" data-python-history-detail="${index}"${index === 0 ? '' : ' hidden'}><span>${escapeHtml(item.key)}</span>${item.visual ? `<figure class="python-history-visual"><img src="${escapeHtml(item.visual)}" alt="${item.key === '1989' || item.key === '1991' ? 'Guido van Rossum, creator of Python' : escapeHtml(item.titleEn)}" loading="lazy"><figcaption><a href="${escapeHtml(item.credit || item.url)}" target="_blank" rel="noopener">${item.key === '1989' || item.key === '1991' ? 'Photo source · Daniel Stroud' : 'Image source'}</a>${item.key === '1989' || item.key === '1991' ? ' · <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener">CC BY-SA 4.0</a>' : ''}</figcaption></figure>` : ''}<div><h5 class="lang-en">${escapeHtml(item.titleEn)}</h5><h5 class="lang-ja jp" lang="ja">${escapeHtml(item.titleJa)}</h5><p class="lang-en">${escapeHtml(item.textEn)}</p><p class="lang-ja jp" lang="ja">${escapeHtml(item.textJa)}</p></div><a href="${escapeHtml(item.url)}" target="_blank" rel="noopener">SOURCE ↗</a></article>`).join('');
    const metricCards = metrics.map(item => `<a class="python-metric" href="${escapeHtml(item.url)}" target="_blank" rel="noopener"><strong>${escapeHtml(item.key)}</strong><span class="lang-en">${escapeHtml(item.titleEn)}</span><span class="lang-ja jp" lang="ja">${escapeHtml(item.titleJa)}</span></a>`).join('');
    const domainButtons = domains.map((item, index) => `<button type="button" data-python-domain-jump="${index}" class="${index === 0 ? 'is-active' : ''}"${index === 0 ? ' aria-current="true"' : ''}><strong class="lang-en">${escapeHtml(item.titleEn)}</strong><strong class="lang-ja jp" lang="ja">${escapeHtml(item.titleJa)}</strong></button>`).join('');
    const domainScenes = domains.map((item, index) => `<article class="python-code-scene${index === 0 ? ' is-active' : ''}" data-python-domain-scene="${index}"${index === 0 ? '' : ' hidden'}><div class="python-code-intent"><span>HUMAN INTENT</span><p class="lang-en">${escapeHtml(item.textEn)}</p><p class="lang-ja jp" lang="ja">${escapeHtml(item.textJa)}</p></div><div class="python-flow-arrow" aria-hidden="true">→</div><div class="python-code-window"><header><i></i><i></i><i></i><span>${escapeHtml(item.key)}.py</span></header><pre><code>${numberedCodeHtml(item.sample)}</code></pre></div><div class="python-flow-arrow" aria-hidden="true">→</div><div class="python-code-result"><span>OUTPUT</span><strong>${escapeHtml(item.output)}</strong></div><button type="button" class="python-trace-button" data-python-trace><span class="lang-en">TRACE THE CODE ▶</span><span class="lang-ja jp" lang="ja">コードを追う ▶</span></button></article>`).join('');
    return `<div id="timeline-python" role="tabpanel" aria-labelledby="timeline-tab-python" data-lecture-timeline-panel="python" hidden><section class="python-lecture" data-python-lecture><header class="python-lecture-opening"><img src="assets/timeline/python-logo.svg" alt="Python"><div><h4 class="lang-en">Readable code. Many possibilities.</h4><h4 class="lang-ja jp" lang="ja">読みやすいコードから、広がる可能性。</h4><small class="lang-en">A language that can take you from a first lesson to data, research, and AI.</small><small class="lang-ja jp" lang="ja">最初の一歩から、データ・研究・AIまでつながる言語。</small></div></header><div class="python-metrics">${metricCards}</div><section class="python-history"><div class="python-section-heading"><span>HISTORY</span><h5 class="lang-en">From a holiday project to a language used around the world.</h5><h5 class="lang-ja jp" lang="ja">休暇中の個人プロジェクトから、世界で使われる言語へ。</h5></div><div class="python-history-scroll"><div class="python-history-map"><span class="python-history-axis" aria-hidden="true"></span>${historyPoints}</div></div><span class="python-history-cue lang-en">SCROLL TO EXPLORE →</span><span class="python-history-cue lang-ja jp" lang="ja">横にスクロールしてたどる →</span><div class="python-history-details">${historyDetails}</div></section><section class="python-domains"><div class="python-section-heading"><span>TRY IT</span><h5 class="lang-en">Pick a use. Follow the code to its result.</h5><h5 class="lang-ja jp" lang="ja">用途を選び、コードから出力まで追ってみよう。</h5></div><nav class="python-domain-tabs" aria-label="Python application areas">${domainButtons}</nav><div class="python-domain-scenes">${domainScenes}</div></section><footer class="python-honesty"><b class="lang-en">Popular does not mean perfect for everything.</b><b class="lang-ja jp" lang="ja">人気があることは、何にでも最適という意味ではない。</b><span class="lang-en">Python is powerful because it is readable, adaptable, and used across many fields.</span><span class="lang-ja jp" lang="ja">読みやすく、応用の幅が広く、多くの分野で使われている。それがPythonの強み。</span></footer></section></div>`;
  };
  const panel = (items, kind, label, tabId) => {
    const values = items.map(item => yearValue(item.year));
    const minimum = Math.min(...values);
    const maximum = Math.max(...values);
    const span = Math.max(1, maximum - minimum);
    const position = value => 7 + ((value - minimum) / span) * 86;
    const interval = span <= 42 ? 5 : 10;
    const ticks = [];
    for (let year = Math.ceil(minimum / interval) * interval; year <= maximum; year += interval) {
      ticks.push(`<span class="history-tick" style="--history-x:${position(year)}%"><b>${year}</b></span>`);
    }
    const maxPopularity = Math.max(1, ...items.map(item => item.popularity));
    const laneLastYear = [-Infinity, -Infinity, -Infinity];
    const events = items.map((item, index) => {
      if (kind !== 'languages') return `<button type="button" class="history-event journey-lane-${index % 3}${index === 0 ? ' is-active' : ''}" style="--history-x:${position(values[index])}%" data-history-jump="${index}"${index === 0 ? ' aria-current="true"' : ''}>${visual(item, kind, 'history-event-visual')}<span class="history-event-copy"><b>${escapeHtml(item.year)}</b><strong>${escapeHtml(item.title)}</strong></span></button>`;
      const currentYear = values[index];
      let lane = laneLastYear.findIndex(lastYear => currentYear - lastYear >= 7);
      if (lane < 0) lane = laneLastYear.indexOf(Math.min(...laneLastYear));
      laneLastYear[lane] = currentYear;
      const size = Math.max(38, Math.sqrt(item.popularity / maxPopularity) * 112);
      const popularity = item.popularity ? `${item.popularity.toFixed(1)}%` : 'HIST.';
      return `<button type="button" class="history-bubble lane-${lane}${index === 0 ? ' is-active' : ''}" style="--history-x:${position(currentYear)}%;--bubble-size:${size.toFixed(1)}px" data-history-jump="${index}" aria-label="${escapeHtml(`${item.title}, ${item.year}, ${popularity}`)}"${index === 0 ? ' aria-current="true"' : ''}><span class="history-bubble-orb">${visual(item, kind, 'history-bubble-mark')}</span><span class="history-bubble-copy"><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.year)} · ${escapeHtml(popularity)}</small></span></button>`;
    }).join('');
    const facts = item => item.famousJa || item.usersJa ? `<div class="history-facts"><div><span>FAMOUS USE · 代表的な用途</span><p class="lang-en">${escapeHtml(item.famousEn)}</p><p class="lang-ja jp" lang="ja">${escapeHtml(item.famousJa)}</p></div><div><span>PRIMARY USERS · 主な利用者</span><p class="lang-en">${escapeHtml(item.usersEn)}</p><p class="lang-ja jp" lang="ja">${escapeHtml(item.usersJa)}</p></div></div>` : '';
    const details = items.map((item, index) => {
      const games = item.games?.length ? `<section class="history-game-shelf" aria-label="この機種のゲーム"><span class="lang-en">GAMES FOR THIS COMPUTER</span><span class="lang-ja jp" lang="ja">この機種のゲーム</span><div>${item.games.map(game => `<a href="${escapeHtml(game.link)}" target="_blank" rel="noopener" aria-label="${escapeHtml(`${game.title} · 詳細情報`)}"><img src="${escapeHtml(game.image)}" alt="${escapeHtml(`${game.title}の画像`)}" loading="lazy" referrerpolicy="no-referrer"><strong>${escapeHtml(game.title)}</strong></a>`).join('')}</div></section>` : '';
      return `<article class="history-annotation${item.sample ? ' has-code' : ''}${item.famousJa ? ' has-facts' : ''}${item.games?.length ? ' has-games' : ''}${index === 0 ? ' is-active' : ''}" data-history-detail="${index}"${index === 0 ? '' : ' hidden'}>${visual(item, kind, 'history-annotation-visual')}<div class="history-annotation-copy"><span>${escapeHtml(item.year)}${item.popularity ? ` · ${item.popularity.toFixed(1)}% USED IN 2025` : ''}</span><h5>${escapeHtml(item.title)}</h5><p class="lang-en">${escapeHtml(item.en)}</p><p class="lang-ja jp" lang="ja">${escapeHtml(item.ja)}</p>${games}${facts(item)}</div>${item.sample ? `<div class="history-code-sample"><span>HELLO, WORLD · ${escapeHtml(item.title)}</span><pre><code>${highlightTimelineCode(item.sample)}</code></pre></div>` : ''}<div class="history-annotation-links"><a class="history-source" href="${escapeHtml(item.url)}" target="_blank" rel="noopener"><span class="lang-en">EXPLORE ↗</span><span class="lang-ja jp" lang="ja">詳しく見る ↗</span></a>${item.credit ? `<a class="history-credit" href="${escapeHtml(item.credit)}" target="_blank" rel="noopener">IMAGE SOURCE ↗</a>` : ''}</div></article>`;
    }).join('');
    const scaleNote = kind === 'languages' ? `<div class="history-scale-note"><span class="lang-en">Horizontal position = release year · bubble area = 2025 use</span><span class="lang-ja jp" lang="ja">横位置＝発表年 · 円の面積＝2025年の使用率</span><small class="lang-en">Stack Overflow “Have used” share (31,771 responses). Historic languages absent from the survey use the minimum marker.</small><small class="lang-ja jp" lang="ja">Stack Overflow「過去1年に使用」の割合（31,771回答）。調査にない歴史的言語は最小サイズ。</small><a href="https://survey.stackoverflow.co/2025/technology#1-programming-scripting-and-markup-languages" target="_blank" rel="noopener">SOURCE ↗</a></div>` : '';
    return `<div id="timeline-${kind}" role="tabpanel" aria-labelledby="${tabId}" data-lecture-timeline-panel="${kind}" hidden><div class="history-explorer${kind === 'languages' ? ' is-languages' : ''}" data-history-explorer tabindex="0" aria-label="${escapeHtml(label)}">${scaleNote}<p class="timeline-scroll-cue"><span class="lang-en">SCROLL THE TIMELINE →</span><span class="lang-ja jp" lang="ja">年表を横にスクロール →</span></p><div class="history-map-scroll"><div class="history-map ${kind === 'languages' ? 'is-bubble-map' : 'is-journey-map'}"><span class="history-axis" aria-hidden="true"></span>${ticks.join('')}<nav aria-label="${escapeHtml(label)} chronology">${events}</nav></div></div><div class="history-annotations">${details}</div></div></div>`;
  };
  return `<section class="lecture-timelines" data-lecture-timelines><div class="lecture-timeline-tabs ui-tabs" role="tablist" aria-label="Lecture topics"><button type="button" class="ui-tab" role="tab" aria-selected="false" aria-expanded="false" aria-controls="timeline-journey" id="timeline-tab-journey" data-lecture-timeline-tab="journey"><span class="lang-en">My PC Journey</span><span class="lang-ja jp" lang="ja">私のPC史</span></button><button type="button" class="ui-tab" role="tab" aria-selected="false" aria-expanded="false" aria-controls="timeline-languages" id="timeline-tab-languages" data-lecture-timeline-tab="languages" tabindex="-1"><span class="lang-en">Programming Languages</span><span class="lang-ja jp" lang="ja">言語の歩み</span></button><button type="button" class="ui-tab" role="tab" aria-selected="false" aria-expanded="false" aria-controls="timeline-python" id="timeline-tab-python" data-lecture-timeline-tab="python" tabindex="-1"><span class="lang-en">Why Python?</span><span class="lang-ja jp" lang="ja">なぜPython？</span></button></div>${panel(journey, 'journey', 'My PC Journey', 'timeline-tab-journey')}${panel(languages, 'languages', 'Languages that changed the world', 'timeline-tab-languages')}${pythonPanel(pythonRows)}</section>`;
}

function setupLectureTimelineTabs(root = document) {
  root.querySelectorAll('[data-lecture-timelines]').forEach(group => {
    const buttons = [...group.querySelectorAll('[data-lecture-timeline-tab]')];
    const panels = [...group.querySelectorAll('[data-lecture-timeline-panel]')];
    let activeIndex = -1;
    const select = (index, toggle = false) => {
      activeIndex = toggle && activeIndex === index ? -1 : index;
      buttons.forEach((button, buttonIndex) => {
        const active = buttonIndex === activeIndex;
        button.setAttribute('aria-selected', String(active));
        button.setAttribute('aria-expanded', String(active));
        button.tabIndex = active || (activeIndex === -1 && buttonIndex === 0) ? 0 : -1;
      });
      panels.forEach((panel, panelIndex) => { panel.hidden = panelIndex !== activeIndex; });
    };
    buttons.forEach((button, index) => {
      button.addEventListener('click', () => select(index, true));
      button.addEventListener('keydown', event => {
        if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
        event.preventDefault();
        const next = (index + (event.key === 'ArrowRight' ? 1 : -1) + buttons.length) % buttons.length;
        select(next);
        buttons[next].focus();
      });
    });
    group.querySelectorAll('[data-history-explorer]').forEach(explorer => {
      const details = [...explorer.querySelectorAll('[data-history-detail]')];
      const jumps = [...explorer.querySelectorAll('[data-history-jump]')];
      let current = 0;
      const show = (requested, scrollTimeline = false) => {
        current = Math.max(0, Math.min(details.length - 1, requested));
        details.forEach((detail, index) => {
          detail.hidden = index !== current;
          detail.classList.toggle('is-active', index === current);
        });
        jumps.forEach((jump, index) => {
          jump.classList.toggle('is-active', index === current);
          if (index === current) jump.setAttribute('aria-current', 'true');
          else jump.removeAttribute('aria-current');
        });
        if (scrollTimeline) jumps[current]?.scrollIntoView({ behavior:'smooth', block:'nearest', inline:'center' });
      };
      jumps.forEach((jump, index) => jump.addEventListener('click', () => show(index, true)));
      explorer.addEventListener('keydown', event => {
        if (!['ArrowLeft', 'ArrowRight'].includes(event.key) || event.target.closest('[role="tab"]')) return;
        event.preventDefault();
        show(current + (event.key === 'ArrowRight' ? 1 : -1), true);
      });
      show(0);
    });
    group.querySelectorAll('[data-python-lecture]').forEach(lecture => {
      const historyJumps = [...lecture.querySelectorAll('[data-python-history-jump]')];
      const historyDetails = [...lecture.querySelectorAll('[data-python-history-detail]')];
      const historyScroll = lecture.querySelector('.python-history-scroll');
      const historyControls = document.createElement('nav');
      historyControls.className = 'python-history-controls';
      historyControls.setAttribute('aria-label', 'Python history navigation');
      historyControls.innerHTML = '<button type="button" data-python-history-previous aria-label="前の出来事 / Previous event">←</button><span data-python-history-count aria-live="polite"></span><button type="button" data-python-history-next aria-label="次の出来事 / Next event">→</button>';
      lecture.querySelector('.python-history-details')?.after(historyControls);
      const previousHistory = historyControls.querySelector('[data-python-history-previous]');
      const nextHistory = historyControls.querySelector('[data-python-history-next]');
      const historyCount = historyControls.querySelector('[data-python-history-count]');
      const domainJumps = [...lecture.querySelectorAll('[data-python-domain-jump]')];
      const domainScenes = [...lecture.querySelectorAll('[data-python-domain-scene]')];
      const choose = (jumps, scenes, requested) => {
        const current = Math.max(0, Math.min(scenes.length - 1, requested));
        jumps.forEach((jump, index) => {
          jump.classList.toggle('is-active', index === current);
          if (index === current) jump.setAttribute('aria-current', 'true');
          else jump.removeAttribute('aria-current');
        });
        scenes.forEach((scene, index) => {
          scene.hidden = index !== current;
          scene.classList.toggle('is-active', index === current);
          scene.classList.remove('is-tracing');
        });
      };
      let historyIndex = 0;
      const timelinePosition = index => {
        const points = historyJumps.map(jump => jump.offsetLeft + jump.offsetWidth / 2);
        const span = points[points.length - 1] - points[0];
        return span > 0 ? (points[index] - points[0]) / span : 0;
      };
      const showHistory = (requested, scrollTimeline = false) => {
        historyIndex = Math.max(0, Math.min(historyDetails.length - 1, requested));
        choose(historyJumps, historyDetails, historyIndex);
        historyCount.textContent = `${String(historyIndex + 1).padStart(2, '0')} / ${String(historyDetails.length).padStart(2, '0')}`;
        previousHistory.disabled = historyIndex === 0;
        nextHistory.disabled = historyIndex === historyDetails.length - 1;
        if (scrollTimeline && historyScroll) {
          const travel = historyScroll.scrollWidth - historyScroll.clientWidth;
          historyScroll.scrollTo({ left: timelinePosition(historyIndex) * travel, behavior:'auto' });
        }
      };
      historyJumps.forEach((jump, index) => jump.addEventListener('click', () => showHistory(index, true)));
      previousHistory.addEventListener('click', () => showHistory(historyIndex - 1, true));
      nextHistory.addEventListener('click', () => showHistory(historyIndex + 1, true));
      let scrollFrame = 0;
      historyScroll?.addEventListener('scroll', () => {
        cancelAnimationFrame(scrollFrame);
        scrollFrame = requestAnimationFrame(() => {
          const travel = historyScroll.scrollWidth - historyScroll.clientWidth;
          if (travel <= 0 || historyJumps.length < 2) return;
          const position = historyScroll.scrollLeft / travel;
          const nearest = historyJumps.reduce((best, _jump, index) =>
            Math.abs(timelinePosition(index) - position) < Math.abs(timelinePosition(best) - position) ? index : best, 0);
          if (nearest !== historyIndex) showHistory(nearest);
        });
      }, { passive:true });
      domainJumps.forEach((jump, index) => jump.addEventListener('click', () => choose(domainJumps, domainScenes, index)));
      lecture.querySelectorAll('[data-python-trace]').forEach(button => button.addEventListener('click', () => {
        const scene = button.closest('[data-python-domain-scene]');
        scene.classList.remove('is-tracing');
        void scene.offsetWidth;
        scene.classList.add('is-tracing');
      }));
      showHistory(0);
      choose(domainJumps, domainScenes, 0);
    });
  });
}

function section(week, key) { return week.sections.find(item => item.title.toLowerCase().startsWith(key.toLowerCase())); }
function previewAll() { return new URLSearchParams(location.search).get('preview') === 'all'; }
function isLocalPreview() { return ['localhost', '127.0.0.1', '[::1]'].includes(location.hostname); }
function isAvailable(week) { return isLocalPreview() || previewAll() || week.week === 1 || new Date() >= new Date(week.publish_at); }

function releaseDateLabels(value) {
  const date = new Date(value);
  return {
    en: new Intl.DateTimeFormat('en-US', { month:'short', day:'numeric', timeZone:'Asia/Tokyo' }).format(date),
    ja: new Intl.DateTimeFormat('ja-JP', { month:'long', day:'numeric', timeZone:'Asia/Tokyo' }).format(date)
  };
}

function practiceMixHtml(w) {
  if (!w.practice_mix) return '';
  const values = [...w.practice_mix.matchAll(/(Human|AI)\s+(\d+)%/g)].map(([, label, value]) => ({ label, value:Number(value) }));
  const colors = { Human:'human', AI:'ai' };
  const japaneseLabels = { Human:'人', AI:'AI' };
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

function homeworkDeadlineHtml(w) {
  if (!w.homework_due) return '';
  const deadline = new Date(w.homework_due);
  if (Number.isNaN(deadline.getTime())) return '';
  const japaneseDate = new Intl.DateTimeFormat('ja-JP', { year:'numeric', month:'long', day:'numeric', weekday:'short', timeZone:'Asia/Tokyo' }).format(deadline);
  const englishDate = new Intl.DateTimeFormat('en-US', { weekday:'short', month:'short', day:'numeric', year:'numeric', timeZone:'Asia/Tokyo' }).format(deadline);
  return `<p class="homework-deadline"><span class="lang-ja jp" lang="ja">締切：${escapeHtml(japaneseDate)} 23:59 JST</span><span class="lang-en">Due ${escapeHtml(englishDate)} · 11:59 PM JST</span></p>`;
}

function weekTwoAgendaHtml(body) {
  const copy = parseBilingual(body);
  const rows = language => [...(copy[language] || '').matchAll(/^\|\s*(\d\d:\d\d[–-]\d\d:\d\d)\s*\|\s*\*\*(.+?)\*\*\s*(.*?)\s*\|$/gm)]
    .map(([, time, title, note]) => ({ time, title:title.replace(/\s*·\s*\d+\s*(?:min|分)$/i, ''), note }));
  const en = rows('en');
  const ja = rows('ja');
  if (en.length !== 4 || ja.length !== 4) return bilingualHtml(body);
  return `<ol class="week-lecture-agenda" aria-label="Class agenda / 今日の流れ">${en.map((item, index) => `<li><time>${escapeHtml(item.time)}</time><strong class="lang-ja jp" lang="ja">${escapeHtml(ja[index].title)}</strong><strong class="lang-en">${escapeHtml(item.title)}</strong><span class="lang-ja jp" lang="ja">${escapeHtml(ja[index].note)}</span><span class="lang-en">${escapeHtml(item.note)}</span></li>`).join('')}</ol>`;
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
  const setupCheck = section(w, 'Setup Check');
  const lectureFiles = resources ? resourcesHtml(resources.body, ['lecture']) : '';
  const notebookFiles = resources ? resourcesHtml(resources.body, ['notebook','fundamentals','experiment']) : '';
  const challengeFiles = resources ? resourcesHtml(resources.body, ['challenge']) : '';
  const sharedFiles = resources ? resourcesHtml(resources.body, ['support','data']) : '';
  const homeworkFiles = resources ? resourcesHtml(resources.body, ['homework']) : '';
  const resourceBlock = (files, showLabel = true) => files ? `<div class="section-resources">${showLabel ? '<p class="resources-label"><span class="lang-en">FILES</span><span class="lang-ja jp" lang="ja">使用するファイル</span></p>' : ''}${files}</div>` : '';
  const classTabs = [];
  if (setupCheck) classTabs.push({ key:'setup', en:'Setup check', ja:'環境チェック', content:`<div class="class-task">${bilingualHtml(setupCheck.body)}</div>` });
  if (tutorials) classTabs.push({ key:'tutorials', en:'Tutorials', ja:'チュートリアル', content:tutorialsHtml(tutorials.body) });
  if (notebook) classTabs.push({ key:'notebook', en:'In-class activity', ja:'授業内アクティビティ', content:`<div class="class-task">${bilingualHtml(notebook.body)}${resourceBlock(notebookFiles, false)}</div>` });
  if (challenge) classTabs.push({ key:'challenge', en:'30-min challenge', ja:'30分チャレンジ', content:`<div class="class-task">${bilingualHtml(challenge.body)}${resourceBlock(challengeFiles + (w.week === 2 ? sharedFiles : ''), false)}</div>` });
  const tabId = `class-${String(w.week).padStart(2,'0')}`;
  const inClassCopy = classTabs.length ? `<div class="class-tabs"><div class="class-tab-list ui-tabs" role="tablist" aria-label="In-class activities" style="--class-tab-count:${classTabs.length}">${classTabs.map((tab, index) => `<button type="button" class="class-tab ui-tab" role="tab" id="${tabId}-${tab.key}-tab" aria-controls="${tabId}-${tab.key}-panel" aria-selected="${index === 0}" tabindex="${index === 0 ? '0' : '-1'}"><span class="lang-en">${tab.en}</span><span class="lang-ja jp" lang="ja">${tab.ja}</span></button>`).join('')}</div>${classTabs.map((tab, index) => `<div class="class-tab-panel" role="tabpanel" id="${tabId}-${tab.key}-panel" aria-labelledby="${tabId}-${tab.key}-tab"${index === 0 ? '' : ' hidden'}>${tab.content}</div>`).join('')}</div>${w.week === 1 || w.week === 2 ? '' : resourceBlock(sharedFiles)}` : '';
  const lectureResource = resources?.body.split('\n').map(line => line.trim()).find(line => /\{lecture\}$/.test(line));
  const lectureMatch = lectureResource?.match(/^[-]\s*\[([^\]]+)\]\(([^\s)]+)\)/);
  const lecturePath = lectureMatch?.[2] || '';
  const lectureViewer = lecturePath ? `viewer.html?file=${encodeURIComponent(lecturePath)}&title=${encodeURIComponent(lectureMatch[1])}` : '';
  const lectureThumb = lecturePath && fileType(lecturePath, false) === 'PDF' ? pdfPageImage(lecturePath, w.week === 1 ? 5 : 1) : '';
  const lectureDeck = lectureFiles ? `<aside class="lecture-deck-panel"><p class="lecture-deck-label"><span class="lang-en">LECTURE SLIDES</span><span class="lang-ja jp" lang="ja">講義スライド</span></p>${lectureThumb ? `<a class="lecture-deck-thumbnail" data-file-preview href="${lectureViewer}" aria-label="${escapeHtml(lectureMatch[1])}"><img src="${escapeHtml(lectureThumb)}" alt="${escapeHtml(lectureMatch[1])} slide preview" loading="lazy"></a>` : ''}<p class="lecture-deck-title">${escapeHtml(lectureMatch?.[1] || '')}</p></aside>` : '';
  const weekTwoLectureTabs = `<iframe class="agenda-slide-frame" src="weeks/week-02/lecture.html?embedded=1" title="Week 02 lecture slides — Basics and Earthquake Map" loading="lazy" allow="fullscreen" allowfullscreen></iframe>`;
  const lectureActions = w.week === 2 ? `<nav class="lecture-header-actions" aria-label="Lecture tools"><a class="file-preview" data-lecture-page href="weeks/week-02/lecture.html#playground">Playground ↗</a><a class="file-preview" data-lecture-page href="weeks/week-02/lecture.html#slides"><span class="lang-ja jp" lang="ja">プレビュー</span><span class="lang-en">Preview</span> ↗</a></nav>` : '';
  const lectureVisual = lectureTimelines ? lectureTimelinesHtml(lectureTimelines.body) : lectureDeck;
  return `<details class="week${w.week === 1 ? ' week--first' : w.week === 2 ? ' week--second' : ''}" id="${id}"${defaultOpen ? ' open' : ''}><summary class="week-summary">${summary}<span class="week-toggle"><span class="week-toggle-closed"><span class="lang-en">OPEN WEEK</span><span class="lang-ja jp" lang="ja">週を開く</span></span><span class="week-toggle-open"><span class="lang-en">CLOSE WEEK</span><span class="lang-ja jp" lang="ja">週を閉じる</span></span><b aria-hidden="true">↓</b></span></summary><div class="week-body">${w.week === 2 && lecture ? weekTwoAgendaHtml(lecture.body) : ''}<section class="course-section course-section--lecture${lectureTimelines ? ' has-timelines' : ''}"><header><div><p>LECTURE / 講義</p><h3 class="lang-en">${w.week === 1 ? 'From computers to Python' : w.week === 2 ? 'Python basics + earthquake map' : 'This week’s lecture'}</h3><h3 class="lang-ja jp" lang="ja">${w.week === 1 ? 'コンピュータからPythonへ' : w.week === 2 ? 'Pythonの基本と地震地図' : '今週の講義'}</h3></div>${lectureActions}</header><div class="course-section-content">${w.week === 2 ? weekTwoLectureTabs : `${lecture ? bilingualHtml(lecture.body) : ''}${lectureVisual}`}</div></section><section class="course-section course-section--in-class"><header><div><p>IN CLASS / 授業内</p><h3 class="lang-en">Practice in class</h3><h3 class="lang-ja jp" lang="ja">授業内課題</h3></div></header><div class="course-section-content">${inClassCopy}</div></section><section class="course-section course-section--homework"><header><div><p>HOMEWORK / 宿題</p><h3 class="lang-en">${w.week === 2 ? 'Your earthquake map' : 'Make something of your own'}</h3><h3 class="lang-ja jp" lang="ja">${w.week === 2 ? '自分の地震地図' : '宿題'}</h3></div></header><div class="course-section-content">${homeworkDeadlineHtml(w)}${homework ? bilingualHtml(homework.body) : ''}${resourceBlock(homeworkFiles, w.week !== 1)}</div></section></div></details>`;
}

function renderAgenda(weeks) {
  const root = document.querySelector('[data-agenda]');
  if (!root) return;
  const preview = previewAll();
  const today = new Intl.DateTimeFormat('en-CA', { timeZone:'Asia/Tokyo', year:'numeric', month:'2-digit', day:'2-digit' }).format(new Date());
  const current = weeks.find(w => isAvailable(w) && w.course_date >= today) || [...weeks].reverse().find(isAvailable) || weeks[0];
  const heading = `<section class="agenda-heading wrap"><div><p class="eyebrow">2026–2 PROGRAMMING / プログラミング</p><h1><span class="lang-en">Course agenda</span><span class="lang-ja jp" lang="ja">授業予定</span></h1></div><p><span class="lang-en">Thursday · Period 3 · 13:10–14:50</span><span class="lang-ja jp" lang="ja">木曜日 · 3限 · 13:10–14:50</span></p>${preview ? '<span class="preview-notice">PREVIEW · ALL WEEKS</span>' : ''}</section>`;
  const shortcuts = weeks.map(w => {
    const number = String(w.week).padStart(2, '0');
    const date = new Date(`${w.course_date}T12:00:00+09:00`);
    const ja = new Intl.DateTimeFormat('ja-JP', { month:'numeric', day:'numeric', weekday:'short', timeZone:'Asia/Tokyo' }).format(date);
    const en = new Intl.DateTimeFormat('en-US', { month:'short', day:'numeric', timeZone:'Asia/Tokyo' }).format(date);
    const classes = `week-shortcut${w.week === current.week ? ' is-current' : ''}${isAvailable(w) ? '' : ' is-locked'}`;
    return `<a class="${classes}" href="#week-${number}" aria-label="Week ${number}: ${escapeHtml(w.title)} — ${escapeHtml(en)}"${w.week === current.week ? ' aria-current="date"' : ''}><strong>${number}</strong><span class="lang-ja jp" lang="ja">${escapeHtml(ja)}</span><span class="lang-en">${escapeHtml(en)}</span></a>`;
  }).join('');
  root.innerHTML = `${heading}<nav class="week-shortcuts wrap" aria-label="Week shortcuts / 各週へ移動">${shortcuts}</nav><section class="week-list wrap">${weeks.map(w => agendaWeek(w, preview || w.week === current.week)).join('')}</section>`;
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
  root.querySelectorAll('.week-shortcut').forEach(shortcut => shortcut.addEventListener('click', () => {
    const week = root.querySelector(shortcut.getAttribute('href'));
    if (week?.tagName === 'DETAILS') week.open = true;
  }));
  const returnScroll = Number(state.get('scroll'));
  if (Number.isFinite(returnScroll) && returnScroll > 0) requestAnimationFrame(() => window.scrollTo(0, returnScroll));
}

function setupClassTabs(root = document) {
  root.querySelectorAll('.class-tabs').forEach(group => {
    const buttons = [...group.querySelectorAll('[role="tab"]')];
    const panels = [...group.querySelectorAll('[role="tabpanel"]')];
    if (!buttons.length) return;
    const storageKey = `programming-tab:${buttons[0].id}`;
    const select = (index, remember = true) => {
      buttons.forEach((button, i) => {
        button.setAttribute('aria-selected', String(i === index));
        button.tabIndex = i === index ? 0 : -1;
      });
      panels.forEach((panel, i) => { panel.hidden = i !== index; });
      if (remember) { try { sessionStorage.setItem(storageKey, String(index)); } catch (_) { /* Tabs still work without storage. */ } }
    };
    try {
      const saved = sessionStorage.getItem(storageKey);
      const index = Number(saved);
      if (saved !== null && Number.isInteger(index) && index >= 0 && index < buttons.length) select(index, false);
    } catch (_) { /* Use the default tab. */ }
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
    const lectureLink = event.target.closest('a[data-lecture-page]');
    if (lectureLink) {
      const lectureUrl = new URL(lectureLink.href, location.href);
      lectureUrl.searchParams.set('return', agendaReturnUrl());
      lectureLink.href = lectureUrl.href;
      return;
    }
    const projectLink = event.target.closest('a[data-project-link]');
    if (projectLink) {
      const projectUrl = new URL(projectLink.href, location.href);
      projectUrl.searchParams.set('return', agendaReturnUrl());
      projectLink.href = projectUrl.href;
      return;
    }
    const link = event.target.closest('a[data-file-preview], a[href^="viewer.html?file="]');
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

function parseCsv(source) {
  const rows = [];
  let row = [];
  let value = '';
  let quoted = false;
  const text = source.replace(/^\uFEFF/, '');
  for (let index = 0; index < text.length; index++) {
    const char = text[index];
    if (quoted) {
      if (char === '"' && text[index + 1] === '"') { value += '"'; index++; }
      else if (char === '"') quoted = false;
      else value += char;
    } else if (char === '"' && value === '') quoted = true;
    else if (char === ',') { row.push(value); value = ''; }
    else if (char === '\n' || char === '\r') {
      row.push(value);
      if (row.some(cell => cell !== '')) rows.push(row);
      row = [];
      value = '';
      if (char === '\r' && text[index + 1] === '\n') index++;
    } else value += char;
  }
  if (row.length || value !== '') { row.push(value); rows.push(row); }
  return rows;
}

function renderCsvPreview(root, source, title, actions, download) {
  const [columns = [], ...rows] = parseCsv(source);
  const pageSize = 50;
  const pageCount = Math.max(1, Math.ceil(rows.length / pageSize));
  const headings = columns.map(column => `<th scope="col">${escapeHtml(column)}</th>`).join('');
  root.innerHTML = `<div class="viewer-title"><p class="eyebrow">CSV PREVIEW</p><h1>${escapeHtml(title)}</h1>${actions(download)}</div><section class="csv-preview"><div class="csv-toolbar"><p><span class="lang-ja jp" lang="ja">${rows.length.toLocaleString('ja-JP')}行 · ${columns.length}列</span><span class="lang-en">${rows.length.toLocaleString('en-US')} rows · ${columns.length} columns</span></p><nav class="csv-pager" aria-label="CSV pages"><button type="button" data-csv-prev><span class="lang-ja jp" lang="ja">← 前へ</span><span class="lang-en">← Previous</span></button><span data-csv-page></span><button type="button" data-csv-next><span class="lang-ja jp" lang="ja">次へ →</span><span class="lang-en">Next →</span></button></nav></div><div class="csv-table-scroll"><table><caption class="sr-only">${escapeHtml(title)}</caption><thead><tr><th scope="col">#</th>${headings}</tr></thead><tbody data-csv-rows></tbody></table></div></section>`;
  const tbody = root.querySelector('[data-csv-rows]');
  const scroll = root.querySelector('.csv-table-scroll');
  const previous = root.querySelector('[data-csv-prev]');
  const next = root.querySelector('[data-csv-next]');
  const status = root.querySelector('[data-csv-page]');
  let page = 0;
  const showPage = () => {
    const start = page * pageSize;
    tbody.innerHTML = rows.slice(start, start + pageSize).map((row, offset) => `<tr><th scope="row">${start + offset + 1}</th>${columns.map((column, index) => `<td${column.toLowerCase() === 'place' ? ' class="csv-place"' : ''}>${escapeHtml(row[index] ?? '')}</td>`).join('')}</tr>`).join('');
    status.textContent = `${page + 1} / ${pageCount}`;
    previous.disabled = page === 0;
    next.disabled = page === pageCount - 1;
    scroll.scrollTo({ top:0, left:0 });
  };
  previous.addEventListener('click', () => { if (page > 0) { page--; showPage(); } });
  next.addEventListener('click', () => { if (page < pageCount - 1) { page++; showPage(); } });
  showPage();
}

async function setupFileViewer() {
  const root = document.querySelector('[data-file-viewer]');
  if (!root) return;
  const params = new URLSearchParams(location.search);
  const file = params.get('file') || '';
  if (file === 'content/final-project.md') {
    location.replace(new URL('final-project.html', location.href).href);
    return;
  }
  const title = params.get('title') || file.split('/').pop() || 'File preview';
  const fallback = new URL('index.html', location.href);
  const requestedReturn = params.get('return');
  let returnUrl = fallback.href;
  if (requestedReturn) {
    try {
      const candidate = new URL(requestedReturn, location.href);
      if (candidate.protocol === location.protocol && candidate.host === location.host && (candidate.pathname === '/' || /\/(?:index|agenda|guide)\.html$/.test(candidate.pathname))) returnUrl = candidate.href;
    } catch (_) { /* Use the agenda as a safe fallback. */ }
  }
  const backToGuide = /\/guide\.html$/.test(new URL(returnUrl).pathname);
  const back = `<a class="viewer-back" href="${escapeHtml(returnUrl)}"><span class="lang-en">← BACK TO ${backToGuide ? 'GUIDE' : 'AGENDA'}</span><span class="lang-ja jp" lang="ja">← ${backToGuide ? 'ガイド' : '授業予定'}に戻る</span></a>`;
  const actions = download => `<div class="viewer-actions">${back}${download}</div>`;
  if (!/^(weeks|content)\//.test(file)) { root.innerHTML = `<div class="viewer-title"><p class="eyebrow">FILE PREVIEW</p><h1>${escapeHtml(title)}</h1>${actions('')}</div><p class="agenda-locked">File preview is unavailable.</p>`; return; }
  const extension = file.split('.').pop().toLowerCase();
  const isTutorial = /^weeks\/week-01\/tutorials\//.test(file);
  const download = isTutorial ? '' : `<a class="file-download viewer-download" href="${escapeHtml(file)}" download><span class="lang-ja jp" lang="ja">ダウンロード</span><span class="lang-en">Download</span></a>`;
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
    if (extension === 'csv') {
      renderCsvPreview(root, source, title, actions, download);
      return;
    }
    if (extension === 'ipynb') {
      const notebook = JSON.parse(source);
      const cells = notebook.cells || [];
      const visibleCells = cells;
      const notebookText = value => Array.isArray(value) ? value.join('') : (value || '');
      const preview = visibleCells.map(cell => {
        if (cell.cell_type !== 'code') return `<section class="notebook-cell markdown-cell"><div class="cell-label">Markdown</div><div class="notebook-markdown">${markdownHtml(notebookText(cell.source))}</div></section>`;
        const output = (cell.outputs || []).map(item => notebookText(item.text || item.data?.['text/plain'])).filter(Boolean).join('\n');
        return `<section class="notebook-cell code-cell"><div class="cell-label"><span>▶</span> Code</div><div class="notebook-code-content"><pre class="code-block"><code>${numberedCodeHtml(notebookText(cell.source))}</code></pre>${output ? `<div class="notebook-output"><span>OUTPUT</span><pre>${escapeHtml(output)}</pre></div>` : ''}</div></section>`;
      }).join('');
      root.innerHTML = `<div class="viewer-title"><p class="eyebrow">JUPYTER NOTEBOOK · ${cells.length} CELLS</p><h1>${escapeHtml(title)}</h1>${actions(download)}</div><section class="notebook-shell"><header class="notebook-toolbar"><span class="notebook-tab">${escapeHtml(file.split('/').pop())}</span><span class="notebook-readonly"><span class="lang-ja jp" lang="ja">プレビュー · 読み取り専用</span><span class="lang-en">Preview · Read only</span></span></header><article class="notebook-preview">${preview}</article></section>`;
      return;
    }
    if (isTutorial) {
      root.innerHTML = `<div class="viewer-title tutorial-viewer-title"><p class="eyebrow">WEEK 01 · TUTORIAL</p><h1>${escapeHtml(title)}</h1>${actions('')}</div><div class="tutorial-layout"><aside class="tutorial-toc" data-tutorial-toc></aside><article class="markdown-preview tutorial-preview">${tutorialMarkdownHtml(source.replace(/^#\s+.+\n?/, ''))}</article></div>${tutorialNavigationHtml(file, returnUrl)}`;
      setupTutorialTabs(root);
      await setupTutorialToc(root, file, returnUrl, source);
      return;
    }
    if (extension === 'md' && /^---\s*\n[\s\S]*?\nbilingual:\s*true\s*\n[\s\S]*?\n---/.test(source)) {
      const document = parseFrontMatter(source);
      const heading = (ja, en) => `<span class="lang-ja jp" lang="ja">${escapeHtml(ja)}</span><span class="lang-en">${escapeHtml(en)}</span>`;
      const sections = document.sections.map(section => {
        const [ja, en = ja] = section.title.split(' / ');
        return `<section><h2>${heading(ja, en)}</h2>${bilingualHtml(section.body)}</section>`;
      }).join('');
      root.innerHTML = `<div class="viewer-title"><p class="eyebrow">MARKDOWN PREVIEW</p><h1>${heading(document.title_ja || document.title, document.title)}</h1>${actions(download)}</div><article class="markdown-preview">${sections}</article>`;
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
  setupCourseGuide();
  setupFinalProjectPage();
  if (document.querySelector('[data-agenda]')) {
    try { const weeks = await loadWeeks(); renderAgenda(weeks); setupAgendaToggles(); setupClassTabs(); setupLectureTimelineTabs(); }
    catch (error) { console.error(error); document.querySelectorAll('[data-agenda]').forEach(node => { node.innerHTML = '<p class="agenda-locked">Course content could not load. Please refresh the page.</p>'; }); }
  }
});
