/* Step through outputs evaluated by Python when the deck was built. */
(() => {
  const trace = document.querySelector('[data-name-trace]');
  if (!trace) return; // The release gate removes the deck before class.
  const {nameTrace} = JSON.parse(document.getElementById('lesson-data').textContent);
  const next = trace.querySelector('[data-fn-next]');
  const current = trace.querySelector('[data-current]');
  const printed = trace.querySelector('.fn-printed');
  let step = 0;
  next.addEventListener('click', () => {
    const [name, result] = nameTrace[step++];
    current.textContent = 'name_tag(' + JSON.stringify(name) + ')';
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
