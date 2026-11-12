(() => {
  const query = new URLSearchParams(location.search);
  const page = document.getElementById('weather-guide');
  const toggle = document.getElementById('language-toggle');
  function language(value) {
    document.documentElement.lang = value;
    document.documentElement.dataset.language = value;
    toggle.textContent = value === 'ja' ? 'EN' : 'JP';
    toggle.setAttribute('aria-label', value === 'ja' ? 'Switch to English' : '日本語に切り替える');
    document.title = value === 'ja' ? '天気コード集 · Week 07 プログラミング' : 'Weather web tutorial · Week 07 Programming';
    document.querySelectorAll('[data-label-ja]').forEach(element => {
      element.setAttribute('aria-label', element.dataset[value === 'ja' ? 'labelJa' : 'labelEn']);
    });
    try { localStorage.setItem('programming-language', value); } catch {}
  }
  let initial = 'ja';
  try { initial = localStorage.getItem('programming-language') === 'en' ? 'en' : 'ja'; } catch {}
  language(initial);
  toggle.addEventListener('click', () => language(document.documentElement.lang === 'ja' ? 'en' : 'ja'));
  if (!query.has('p') && Date.now() < Date.parse(document.body.dataset.release)) {
    const notice = document.createElement('p');
    notice.textContent = initial === 'ja' ? '第7週 · 11月12日 12:00 JST 公開' : 'Week 07 · Available November 12 at noon JST.';
    document.body.append(notice); return;
  }
  page.hidden = false;
  if (query.has('p')) document.querySelectorAll('a[href]').forEach(link => {
    const url = new URL(link.href, location.href);
    if (url.origin === location.origin && url.pathname.endsWith('.html')) {
      url.searchParams.set('p', ''); link.href = url.href;
    }
  });
  const topics = [...document.querySelectorAll('[data-topic]')];
  const links = [...document.querySelectorAll('nav a')];
  function show(scroll) {
    const id = location.hash.slice(1);
    const selected = topics.find(topic => topic.id === id) || topics[0];
    topics.forEach(topic => topic.hidden = topic !== selected);
    links.forEach(link => {
      if (new URL(link.href).hash === '#' + selected.id) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    if (scroll) selected.scrollIntoView({block:'start'});
  }
  window.addEventListener('hashchange', () => show(true));
  show(Boolean(location.hash));
  document.querySelectorAll('pre[data-language="python"] code').forEach(code => {
    const source = code.textContent;
    const pattern = /(#[^\n]*)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|\b(for|while|if|else|in|is|None|or|from|import|with|as)\b|\b(\d+(?:\.\d+)?)\b/g;
    let pos = 0; code.replaceChildren();
    for (const match of source.matchAll(pattern)) {
      code.append(document.createTextNode(source.slice(pos, match.index)));
      const token = document.createElement('span');
      token.className = match[1] ? 'syntax-comment' : match[2] ? 'syntax-string' : match[3] ? 'syntax-keyword' : 'syntax-number';
      token.textContent = match[0]; code.append(token); pos = match.index + match[0].length;
    }
    code.append(document.createTextNode(source.slice(pos)));
  });
})();
