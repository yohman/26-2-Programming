/* Text art: spinning bicycle spokes and the weather-app review sky. */
(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const scenes = [...document.querySelectorAll('[data-ascii-scene]')].map(root => ({
    root, button: root.querySelector('[data-ascii-toggle]'),
    sprites: [...root.querySelectorAll('[data-ascii-bike], [data-ascii-weather-art]')].map(art => ({
      art, frames: JSON.parse(art.dataset.asciiFrames || root.dataset.frames), frame: 0
    })),
    label: root.dataset.animationLabel || 'bicycle animation', period: Number(root.dataset.frameMs) || 160,
    updated: 0, wanted: !reduced.matches, visible: false
  }));
  let timer = null, active = [];
  const sync = () => {
    active = scenes.filter(scene => scene.wanted && scene.visible && !document.hidden && !scene.root.closest('[hidden]'));
    scenes.forEach(scene => {
      const running = active.includes(scene);
      scene.root.classList.toggle('ascii-running', running);
      scene.button.textContent = scene.wanted ? 'Ⅱ' : '▶';
      scene.button.setAttribute('aria-pressed', String(scene.wanted));
      scene.button.setAttribute('aria-label', (scene.wanted ? 'Pause ' : 'Play ') + scene.label);
    });
    if (active.length && timer === null) timer = setInterval(() => {
      const now = performance.now();
      active.forEach(scene => {
        if (now - scene.updated < scene.period) return;
        scene.updated = now;
        scene.sprites.forEach(sprite => {
          sprite.frame = (sprite.frame + 1) % sprite.frames.length;
          sprite.art.textContent = sprite.frames[sprite.frame];
        });
      });
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
