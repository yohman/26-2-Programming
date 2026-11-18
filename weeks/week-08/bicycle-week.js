/* Instructor's two 10-minute phases. Time is based on the clock, not interval ticks. */
(() => {
  const root = document.querySelector('[data-quiz-clock]');
  if (!root) return;
  const display = root.querySelector('[data-clock]');
  const toggle = root.querySelector('[data-clock-toggle]');
  const status = root.querySelector('[data-clock-status]');
  let remaining = 600, deadline = 0, running = false;
  function message(ja, en) {
    const jp = document.createElement('span'), eng = document.createElement('span');
    jp.className = 'ja'; jp.textContent = ja;
    eng.className = 'en'; eng.textContent = en;
    status.replaceChildren(jp, eng);
  }
  function render() {
    if (running) remaining = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
    if (running && remaining === 0) { running = false; message('時間です', 'Time is up'); }
    display.textContent = String(Math.floor(remaining / 60)).padStart(2, '0') + ':' + String(remaining % 60).padStart(2, '0');
    toggle.textContent = running ? 'Ⅱ' : '▶';
    toggle.setAttribute('aria-label', running ? 'Pause timer' : 'Start timer');
  }
  function reset() { running = false; remaining = 600; message('開始待ち', 'Ready'); render(); }
  toggle.addEventListener('click', () => {
    if (running) { render(); running = false; message('一時停止', 'Paused'); }
    else {
      if (!remaining) remaining = 600;
      deadline = Date.now() + remaining * 1000; running = true; message('計測中', 'Running');
    }
    render();
  });
  root.querySelector('[data-clock-reset]').addEventListener('click', reset);
  root.querySelectorAll('[data-phase]').forEach(button => button.addEventListener('click', () => {
    root.querySelectorAll('[data-phase]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    reset();
  }));
  setInterval(render, 250);
  render();
})();
