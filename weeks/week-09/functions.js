/* Step through outputs evaluated by Python when the deck was built. */
(() => {
  const flowFrames = [
    {row: 0, phase: 'start', ms: 650},
    {row: 1, phase: 'define', ms: 1100},
    {row: 5, phase: 'skip', ms: 840},
    ...[6, 7, 8].flatMap(caller => [
      {row: caller, caller, phase: 'call', ms: 660},
      ...[2, 3, 4].map(row => ({row, caller, phase: 'inside', ms: 470})),
      {row: caller, caller, phase: 'return', ms: 730},
    ]),
    {row: 9, phase: 'continue', ms: 720},
    {row: null, phase: 'done'},
  ].map((frame, tick) => ({...frame, linear: tick < 10 ? tick : null}));
  if (typeof module !== 'undefined' && module.exports) module.exports = {flowFrames};
  if (typeof document === 'undefined') return;

  const trace = document.querySelector('[data-name-trace]');
  if (!trace) return; // The release gate removes the deck before class.
  const flow = document.querySelector('[data-fn-execution]');
  if (flow) {
    const linear = [...flow.querySelectorAll('[data-flow-side="linear"] li')];
    const right = flow.querySelector('[data-flow-side="calls"]');
    const rows = [...right.querySelectorAll('li')];
    const play = flow.querySelector('[data-flow-play]');
    const step = flow.querySelector('[data-flow-step]');
    const caption = flow.querySelector('[data-flow-caption]');
    const last = flowFrames.length - 1;
    let tick = -1, playing = false, timer;

    function render() {
      const frame = flowFrames[tick];
      const history = flowFrames.slice(0, Math.max(0,tick));
      const passed = new Set(history.filter(item => item.phase !== 'inside').map(item => item.row));
      linear.forEach((line, i) => {
        line.classList.toggle('is-current', frame?.linear === i);
        line.classList.toggle('is-past', i < tick);
      });
      const inBody = frame?.phase === 'inside';
      rows.forEach((line, i) => {
        line.classList.toggle('is-current', frame?.row === i);
        line.classList.toggle('is-past', passed.has(i) || (inBody && i >= 2 && i < frame.row));
        line.classList.toggle('is-caller', inBody && frame.caller === i);
      });
      right.toggleAttribute('data-hop', inBody);
      if (inBody) right.style.setProperty('--flow-caller', frame.caller);
      const n = frame?.caller - 5;
      const labels = {
        ready: ['右の字下げされた3行に注目。','Watch the three indented lines on the right.'],
        start: ['どちらも一番上から実行。','Both start at the top.'],
        define: ['右は関数を定義。中の3行はまだ実行しない。','Define the function. Its body waits.'],
        skip: ['右は関数の下へ進む。','Continue below the definition.'],
        call: [n+'回目の呼び出し。関数の中へ。','Call '+n+': jump to the function.'],
        inside: [n+'回目。関数の中を上から実行。','Call '+n+': run the indented lines.'],
        return: [n+'回目。呼び出した行へ戻る。','Call '+n+': return to the caller.'],
        continue: ['最後の呼び出しの次の行へ。','Continue after the last call.'],
        done: ['定義は1回。関数の中は3回実行した。','One definition. The function body ran three times.'],
      };
      const [ja, en] = labels[frame?.phase ?? 'ready'];
      flow.dataset.flowPhase = frame?.phase ?? 'ready';
      flow.querySelector('[data-flow-ja]').textContent = ja;
      flow.querySelector('[data-flow-en]').textContent = en;
      play.querySelector('[data-flow-glyph]').textContent = playing ? 'Ⅱ' : tick === last ? '↻' : '▶';
      play.querySelector('[data-flow-play-ja]').textContent = playing ? '一時停止' : tick === last ? 'もう一度' : '再生';
      play.querySelector('[data-flow-play-en]').textContent = playing ? 'Pause' : tick === last ? 'Replay' : 'Play';
      step.disabled = tick === last;
    }
    function pause() {
      clearTimeout(timer);
      playing = false;
      caption.setAttribute('aria-live', 'polite');
      render();
    }
    function advance() {
      tick++;
      if (tick === last) { pause(); return; }
      render();
      timer = setTimeout(advance, flowFrames[tick].ms);
    }
    play.addEventListener('click', () => {
      if (playing) { pause(); return; }
      if (tick === last) tick = -1;
      playing = true;
      caption.setAttribute('aria-live', 'off');
      advance();
    });
    step.addEventListener('click', () => {
      clearTimeout(timer);
      playing = false;
      caption.setAttribute('aria-live', 'polite');
      if (tick < last) tick++;
      render();
    });
    document.getElementById('slides-view').addEventListener('lecture:slidechange', () => {
      if (playing && flow.closest('[data-slide]').hidden) pause();
    });
    document.addEventListener('visibilitychange', () => { if (document.hidden && playing) pause(); });
    render();
  }
  const {nameTrace} = JSON.parse(document.getElementById('lesson-data').textContent);
  document.querySelectorAll('[data-fn-choices]').forEach(demo => {
    const choices = [...demo.querySelectorAll('button[data-fn-choice]')];
    const results = [...demo.querySelectorAll('[data-fn-choice-result]')];
    choices.forEach(button => button.addEventListener('click', () => {
      choices.forEach(choice => choice.setAttribute('aria-pressed', String(choice === button)));
      results.forEach(result => { result.hidden = result.dataset.fnChoiceResult !== button.dataset.fnChoice; });
    }));
  });
  const next = trace.querySelector('[data-fn-next]');
  const current = trace.querySelector('[data-current]');
  const printed = trace.querySelector('.fn-printed');
  let step = 0;
  next.addEventListener('click', () => {
    const [call, result] = nameTrace[step++];
    current.textContent = call;
    const tag = document.createElement('li');
    tag.textContent = result;
    printed.append(tag);
    next.disabled = step === nameTrace.length;
  });
  trace.querySelector('[data-fn-reset]').addEventListener('click', () => {
    step = 0;
    next.disabled = false;
    current.textContent = '—';
    printed.replaceChildren();
  });

  document.querySelectorAll('[data-fn-reveal]').forEach(button => {
    button.setAttribute('aria-expanded', 'false');
    button.addEventListener('click', () => {
      const result = button.nextElementSibling;
      result.hidden = !result.hidden;
      button.setAttribute('aria-expanded', String(!result.hidden));
    });
  });

  const panel = document.querySelector('.fn-panel');
  const choices = [...panel.querySelectorAll('input')];
  const grid = panel.querySelector('[data-fn-grid]');
  const template = panel.querySelector('template').content.firstElementChild;
  const nextCity = panel.querySelector('[data-fn-city]');
  const outline = panel.querySelector('[data-fn-cities]');
  let shown = 0;
  const selected = () => choices.filter(input => input.checked);
  function render() {
    const enabled = selected();
    const visible = enabled.slice(0, shown);
    const result = template.cloneNode(false);
    for (const choice of visible) result.append(template.children[choices.indexOf(choice)].cloneNode(true));
    grid.replaceChildren(result);
    outline.textContent = 'cities = ' + JSON.stringify(enabled.map(input => input.value))
      + '  ·  len(badges) = ' + visible.length;
    nextCity.disabled = shown >= enabled.length;
  }
  choices.forEach(input => input.addEventListener('change', () => { shown = 0; render(); }));
  nextCity.addEventListener('click', () => { shown++; render(); });
  panel.querySelector('[data-fn-build]').addEventListener('click', () => { shown = selected().length; render(); });
  render();
})();
