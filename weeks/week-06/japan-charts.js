(() => {
  const query = new URLSearchParams(location.search);
  const page = document.getElementById('chart-page');
  if (!query.has('p') && Date.now() < Date.parse('2026-11-05T12:00:00+09:00')) {
    const notice = document.createElement('p');
    notice.textContent = 'Week 06 · 11月5日 12:00 JST 公開 / Available November 5 at noon JST.';
    document.body.append(notice);
    return;
  }
  page.hidden = false;
  if (query.has('p')) document.querySelectorAll('a[href]').forEach(link => {
    const url = new URL(link.href, location.href);
    if (url.origin === location.origin && url.pathname.endsWith('.html')) {
      url.searchParams.set('p', ''); link.href = url.href;
    }
  });
  const sections = [...document.querySelectorAll('section[id]')];
  const links = [...document.querySelectorAll('nav a[href]')];
  const update = () => {
    let active = sections[0];
    for (const section of sections) if (section.getBoundingClientRect().top <= 160) active = section;
    links.forEach(link => {
      if (new URL(link.href).hash === '#' + active.id) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  };
  let pending = false;
  window.addEventListener('scroll', () => {
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => { update(); pending = false; });
  }, { passive: true });
  update();
  if (location.hash) document.getElementById(location.hash.slice(1))?.scrollIntoView();
})();
