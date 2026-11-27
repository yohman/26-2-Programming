(() => {
  const data = document.getElementById('ascii-data');
  if (!data) return;
  const examples = JSON.parse(data.textContent);
  const demos = [];
  for (const demo of document.querySelectorAll('[data-ascii-demo]')) {
    let {frames, delay} = examples[demo.dataset.asciiDemo];
    const picture = demo.querySelector('.ascii-output');
    const count = demo.querySelector('[data-ascii-index]');
    const plays = demo.querySelectorAll('[data-ascii-play]');
    const step = demo.querySelector('[data-ascii-step]');
    const delayReadout = demo.querySelector('[data-ascii-delay]');
    let index = 0;
    let timer = null;
    const show = () => {
      picture.textContent = frames[index].trimEnd();
      count.textContent = String(index + 1).padStart(2, '0') + ' / ' + String(frames.length).padStart(2, '0');
    };
    const stop = () => {
      clearInterval(timer);
      timer = null;
      plays.forEach(play => { play.disabled = false; });
    };
    plays.forEach(play => play.addEventListener('click', () => {
      demos.forEach(reset => reset());
      ({frames, delay} = examples[play.dataset.asciiVariant || demo.dataset.asciiDemo]);
      plays.forEach(button => {
        if (button.dataset.asciiVariant) button.setAttribute('aria-pressed', String(button === play));
      });
      const pause = Number(play.dataset.asciiPlay) || delay;
      if (delayReadout) delayReadout.textContent = 'sleep(' + (pause / 1000) + ')';
      index = 0;
      show();
      if (frames.length < 2) return;
      play.disabled = true;
      timer = setInterval(() => {
        index += 1;
        show();
        if (index === frames.length - 1) stop();
      }, pause);
    }));
    step.addEventListener('click', () => {
      stop();
      index = (index + 1) % frames.length;
      show();
    });
    demos.push(stop);
  }
  document.getElementById('slides-view')?.addEventListener('lecture:slidechange', () => demos.forEach(stop => stop()));
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) demos.forEach(stop => stop());
  });
})();
