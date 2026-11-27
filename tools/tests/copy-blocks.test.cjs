const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

test('code actions stay in the toolbar without adding copy buttons to output', async () => {
  class Element {
    constructor(tag) {
      this.tag = tag;
      this.children = [];
      this.dataset = {};
      this.attrs = new Map();
      this.events = {};
      const classes = new Set();
      this.classList = {
        add: key => classes.add(key),
        has: key => classes.has(key),
        toggle: key => classes.has(key) ? (classes.delete(key), false) : (classes.add(key), true),
      };
    }
    matches(selector) { return selector === this.tag || selector.split(', ').includes(this.kind); }
    closest(selector) { return this.inSlide && selector === '#slides-view' ? {} : null; }
    querySelector(selector) { return selector === 'code' ? this.code : null; }
    hasAttribute(key) { return this.attrs.has(key); }
    setAttribute(key, value) { this.attrs.set(key, value); }
    getAttribute(key) { return this.attrs.get(key); }
    addEventListener(name, fn) { this.events[name] = fn; }
    append(child) { child.isConnected = true; this.children.push(child); }
    prepend(child) { child.isConnected = true; this.children.unshift(child); }
  }
  const pre = new Element('pre');
  const bare = new Element('pre');
  const outputBoxes = ['pre.lesson-output', 'pre.ascii-output', 'pre.ascii-hello-output',
    'pre[data-demo-output]', 'pre[data-trace-output]'].map(kind => Object.assign(new Element('pre'), {kind}));
  const toolbar = new Element('.code-toolbar, .lecture-cell-toolbar');
  pre.previousElementSibling = toolbar;
  pre.inSlide = true;
  pre.scrollLeft = 20;
  const source = 'for letter in letters:\n    print(letter)\n';
  pre.code = {textContent: source};
  bare.code = {textContent: source};
  pre.children = [pre.code];
  bare.children = [bare.code];
  const installed = [];
  const copied = [];
  const context = {
    document: {
      readyState: 'complete',
      documentElement: {lang: 'en', dataset: {}},
      body: {},
      querySelectorAll: () => [pre, bare, ...outputBoxes],
      createElement: tag => new Element(tag),
    },
    navigator: {clipboard: {writeText: async text => copied.push(text)}},
    HTMLTextAreaElement: class {},
    MutationObserver: class { constructor(fn) {installed.push(fn);} observe(){} },
    requestAnimationFrame: fn => fn(),
    setTimeout: () => {},
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../../assets/copy-blocks.js'),'utf8'), context);
  const controls = toolbar.children[0];
  assert.equal(controls.className, 'block-controls');
  assert.equal(pre.children.length, 1);
  assert.equal(bare.children[0].className, 'block-controls block-controls--row');
  assert.ok(outputBoxes.every(box => !box.children.length && !box.classList.has('copyable-block')));
  const [wrap, copy] = controls.children;
  const event = {preventDefault(){},stopPropagation(){}};
  assert.equal(wrap.getAttribute('aria-pressed'), 'false');
  wrap.events.click(event);
  assert.equal(pre.scrollLeft, 0);
  assert.equal(wrap.getAttribute('aria-pressed'), 'true');
  assert.equal(pre.classList.has('is-code-wrapped'), true);
  await copy.events.click(event);
  assert.deepEqual(copied, [source]);
  installed[1]();
  assert.equal(toolbar.children.length, 1);
});
