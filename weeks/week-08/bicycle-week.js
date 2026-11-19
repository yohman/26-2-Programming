/* Independent quiz and hackathon timers, measured against the wall clock. */
(() => {
  const view = document.getElementById('slides-view');
  if (view) {
    let fadeTimer;
    const reveal = () => {
      if (!document.body.classList.contains('camera-active')) return;
      document.body.classList.add('camera-controls-visible');
      clearTimeout(fadeTimer);
      fadeTimer = setTimeout(() => document.body.classList.remove('camera-controls-visible'), 1500);
    };
    const sync = () => {
      const active = view.querySelector('[data-slide]:not([hidden])');
      document.body.classList.toggle('camera-active', !!active?.classList.contains('layout-camera'));
      document.body.classList.remove('camera-controls-visible');
      clearTimeout(fadeTimer);
    };
    view.addEventListener('lecture:slidechange', sync);
    view.addEventListener('pointermove', reveal);
    view.addEventListener('pointerdown', reveal);
    document.addEventListener('keydown', event => { if (event.key === 'Tab') reveal(); });
    document.querySelector('.lecture-header')?.addEventListener('pointermove', reveal);
    sync();
  }
  document.querySelectorAll('[data-quiz-clock], [data-bike-clock]').forEach(root => {
    const display = root.querySelector('[data-clock]');
    const toggle = root.querySelector('[data-clock-toggle]');
    const status = root.querySelector('[data-clock-status]');
    const phaseSeconds = Number(root.dataset.seconds) || 6 * 60;
    let remaining = phaseSeconds, deadline = 0, running = false;
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
      toggle.setAttribute('aria-pressed', String(running));
    }
    function reset() { running = false; remaining = phaseSeconds; message('開始待ち', 'Ready'); render(); }
    toggle.addEventListener('click', () => {
      if (running) { render(); running = false; message('一時停止', 'Paused'); }
      else {
        if (!remaining) remaining = phaseSeconds;
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
  });
})();
