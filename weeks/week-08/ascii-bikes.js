/* The art is text. Swap four spoke characters; CSS moves the rider. */
(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const scenes = [...document.querySelectorAll('[data-ascii-scene]')].map(root => ({
    root, bike: root.querySelector('[data-ascii-bike]'), button: root.querySelector('[data-ascii-toggle]'),
    frames: JSON.parse(root.dataset.frames), wanted: !reduced.matches, visible: false, frame: 0
  }));
  let timer = null, active = [];
  const sync = () => {
    active = scenes.filter(scene => scene.wanted && scene.visible && !document.hidden && !scene.root.closest('[hidden]'));
    scenes.forEach(scene => {
      const running = active.includes(scene);
      scene.root.classList.toggle('ascii-running', running);
      scene.button.textContent = scene.wanted ? 'Ⅱ' : '▶';
      scene.button.setAttribute('aria-pressed', String(scene.wanted));
      scene.button.setAttribute('aria-label', scene.wanted ? 'Pause bicycle animation' : 'Play bicycle animation');
    });
    if (active.length && timer === null) timer = setInterval(() => {
      active.forEach(scene => { scene.frame = (scene.frame + 1) % scene.frames.length; scene.bike.textContent = scene.frames[scene.frame]; });
    }, 160);
    if (!active.length && timer !== null) { clearInterval(timer); timer = null; }
  };
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => { scenes.find(scene => scene.root === entry.target).visible = entry.isIntersecting; });
    sync();
  });
  scenes.forEach(scene => {
    observer.observe(scene.root);
    scene.button.addEventListener('click', () => { scene.wanted = !scene.wanted; sync(); });
  });
  reduced.addEventListener('change', () => { scenes.forEach(scene => { scene.wanted = !reduced.matches; }); sync(); });
  document.addEventListener('visibilitychange', sync);
  document.getElementById('slides-view')?.addEventListener('lecture:slidechange', sync);
  sync();
  // The challenge is revealed by its release gate before jumping to a section.
  if (document.getElementById('course-page') && location.hash) {
    requestAnimationFrame(() => {
      const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      target?.scrollIntoView();
    });
  }
})();
