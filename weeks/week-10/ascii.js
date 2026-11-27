(() => {
  const data = document.getElementById('ascii-data');
  if (!data) return;
  const examples = JSON.parse(data.textContent);
  const demos = [];
  for (const demo of document.querySelectorAll('[data-ascii-demo]')) {
    const {frames, delay} = examples[demo.dataset.asciiDemo];
    const picture = demo.querySelector('.ascii-output');
    const count = demo.querySelector('[data-ascii-index]');
    const play = demo.querySelector('[data-ascii-play]');
    const step = demo.querySelector('[data-ascii-step]');
    let index = 0;
    let timer = null;
    const show = () => {
      picture.textContent = frames[index].trimEnd();
      count.textContent = String(index + 1).padStart(2, '0') + ' / ' + String(frames.length).padStart(2, '0');
    };
    const stop = () => {
      clearInterval(timer);
      timer = null;
      play.disabled = false;
    };
    play.addEventListener('click', () => {
      demos.forEach(reset => reset());
      index = 0;
      show();
      play.disabled = true;
      timer = setInterval(() => {
        index += 1;
        show();
        if (index === frames.length - 1) stop();
      }, delay);
    });
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
