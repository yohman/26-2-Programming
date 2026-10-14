const slides = [...document.querySelectorAll('[data-slide]')];
const stage = document.querySelector('.slide-stage');
const view = document.getElementById('slides-view');
const previous = document.getElementById('previous-slide');
const next = document.getElementById('next-slide');
const fullscreen = document.getElementById('slide-fullscreen');
const query = new URLSearchParams(location.search);
const embedded = query.get('embed') === '1';
if (embedded) {
  document.body.classList.add('lecture-embedded');
  previous.textContent = '‹';
  next.textContent = '›';
  previous.setAttribute('aria-label', '前のスライド / Previous slide');
  next.setAttribute('aria-label', '次のスライド / Next slide');
  document.querySelectorAll('[data-explore-link]').forEach(link => { link.target = '_top'; });
}
let slideIndex = 0;
document.querySelectorAll('[data-explore-link]').forEach(link => link.addEventListener('click', () => {
  const url = new URL(link.href);
  if (query.has('p')) url.searchParams.set('p', '');
  url.searchParams.set('return', embedded ? '../../agenda.html?open=03#week-03' : location.pathname + location.search);
  link.href = url.href;
}));
document.querySelectorAll('.lecture-notebook-cell pre code, .bus-code code').forEach(code => {
  const source = code.textContent;
  const pattern = /("[^"\n]*"|'[^'\n]*')|\b(for|in|del)\b|\b(print|sum|len|type|int|float)\b|\b(\d+(?:\.\d+)?)\b/g;
  let position = 0;
  code.replaceChildren();
  for (const match of source.matchAll(pattern)) {
    code.append(document.createTextNode(source.slice(position, match.index)));
    const token = document.createElement('span');
    token.className = match[1] ? 'syntax-string' : match[2] ? 'syntax-keyword' : match[3] ? 'syntax-function' : 'syntax-number';
    token.textContent = match[0];
    code.append(token);
    position = match.index + match[0].length;
  }
  code.append(document.createTextNode(source.slice(position)));
});

function language(value) {
  document.documentElement.dataset.language = value;
  document.documentElement.lang = value;
  const toggle = document.getElementById('language-toggle');
  toggle.textContent = value === 'ja' ? 'EN' : '日本語';
  toggle.setAttribute('aria-label', value === 'ja' ? 'Switch to English' : '日本語に切り替える');
  try { localStorage.setItem('programming-language', value); } catch (_) {}
}
let savedLanguage = 'ja';
try { savedLanguage = localStorage.getItem('programming-language') === 'en' ? 'en' : 'ja'; } catch (_) {}
language(savedLanguage);
document.getElementById('language-toggle').addEventListener('click', () => language(document.documentElement.lang === 'ja' ? 'en' : 'ja'));
window.addEventListener('storage', event => { if (event.key === 'programming-language') language(event.newValue === 'en' ? 'en' : 'ja'); });

try {
  const destination = new URL(query.get('return') || '../../agenda.html?open=03#week-03', location.href);
  if (destination.origin === location.origin && /\/(?:index|agenda)\.html$/.test(destination.pathname)) document.getElementById('lecture-return').href = destination.href;
} catch (_) {}

function showSlide(index) {
  slideIndex = Math.max(0, Math.min(slides.length - 1, index));
  slides.forEach((slide, i) => { slide.hidden = i !== slideIndex; });
  document.getElementById('slide-count').textContent = String(slideIndex + 1).padStart(2, '0') + ' / ' + slides.length;
  previous.disabled = slideIndex === 0;
  next.disabled = slideIndex === slides.length - 1;
  stage.scrollTop = 0;
  const url = new URL(location.href);
  url.searchParams.set('slide', slideIndex + 1);
  history.replaceState(null, '', url);
}
previous.addEventListener('click', () => showSlide(slideIndex - 1));
next.addEventListener('click', () => showSlide(slideIndex + 1));
document.addEventListener('keydown', event => {
  if (event.target.closest('input, textarea, select')) return;
  if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
    event.preventDefault();
    showSlide(slideIndex + (event.key === 'ArrowRight' ? 1 : -1));
  }
  if (event.key === 'Escape') { view.classList.remove('is-fullscreen-fallback'); updateFullscreen(); }
});
let touch = null;
stage.addEventListener('touchstart', event => {
  if (event.touches.length !== 1 || event.target.closest('button, a')) return;
  touch = { x:event.touches[0].clientX, y:event.touches[0].clientY };
}, {passive:true});
stage.addEventListener('touchend', event => {
  if (!touch || !event.changedTouches.length) return;
  const dx = event.changedTouches[0].clientX - touch.x;
  const dy = event.changedTouches[0].clientY - touch.y;
  touch = null;
  if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) showSlide(slideIndex + (dx < 0 ? 1 : -1));
}, {passive:true});
stage.addEventListener('touchcancel', () => { touch = null; }, {passive:true});

function updateFullscreen() {
  fullscreen.setAttribute('aria-pressed', String(document.fullscreenElement === view || view.classList.contains('is-fullscreen-fallback')));
}
fullscreen.addEventListener('click', async () => {
  if (document.fullscreenElement === view) await document.exitFullscreen();
  else if (view.classList.contains('is-fullscreen-fallback')) view.classList.remove('is-fullscreen-fallback');
  else {
    try { await view.requestFullscreen(); }
    catch (_) { view.classList.add('is-fullscreen-fallback'); }
  }
  updateFullscreen();
});
document.addEventListener('fullscreenchange', updateFullscreen);

document.querySelectorAll('[data-reveal]').forEach((button, index) => {
  const cell = button.closest('.lecture-notebook-cell');
  const output = cell.nextElementSibling;
  output.id = 'example-output-' + index;
  button.setAttribute('aria-controls', output.id);
  button.addEventListener('click', () => {
    output.hidden = !output.hidden;
    cell.classList.toggle('is-executed', !output.hidden);
    button.setAttribute('aria-expanded', String(!output.hidden));
  });
});
showSlide(Math.max(0, (Number(query.get('slide')) || 1) - 1));
