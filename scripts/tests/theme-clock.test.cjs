const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.resolve(__dirname, '../../docs/javascripts/theme-clock.js'), 'utf8');
function createTheme(dark, options = {}) {
  const listeners = {}, mediaListeners = [];
  const saved = options.saved || new Map([
    ['tea-theme', 'night'], ['tea-theme-time-override', JSON.stringify({theme:'night',period:'legacy'})]
  ]);
  if (options.preference) saved.set('tea-theme-preference', options.preference);
  const media = {matches:dark, addEventListener(type, fn) { mediaListeners.push(fn); }};
  const document = {documentElement:{dataset:{}}, body:options.noBody ? null : {dataset:{}},
    addEventListener(type, fn) { listeners[type]=fn; }};
  const window = {addEventListener(type, fn) {listeners[type]=fn;},
    dispatchEvent(event) { listeners[event.type]?.(event); },
    matchMedia:options.noMedia ? undefined : () => media};
  const context = {window,document,
    localStorage:{getItem(key) {if(options.blockStorage)throw Error();return saved.get(key)??null;},
      setItem(key,value) {if(options.blockStorage)throw Error();saved.set(key,value);}},
    CustomEvent:class{constructor(type,init){this.type=type;this.detail=init.detail;}},
    setTimeout(){throw Error('System theme must not schedule clock timers');}};
  vm.runInNewContext(source,context);
  const controller=window.teaThemeClock;
  vm.runInNewContext(source,context);
  assert.equal(window.teaThemeClock,controller);
  assert.equal(mediaListeners.length,options.noMedia ? 0 : 1,'No duplicate listeners after navigation');
  return {controller,document,saved,listeners,
    system(value){media.matches=value;for(const fn of mediaListeners)fn({matches:value});}};
}
for (const dark of [false,true]) {
  const t=createTheme(dark);
  assert.equal(t.controller.mode,'system','Ignore legacy time-based choices');
  assert.equal(t.controller.theme,dark?'night':'day');
  assert.equal(t.document.body.dataset.mdColorScheme,dark?'slate':'default');
  t.system(!dark);
  assert.equal(t.controller.theme,dark?'day':'night','System changes apply immediately');
}
const manual=createTheme(false);
manual.controller.setManualTheme('night');
manual.system(false);
assert.equal(manual.controller.theme,'night','Keep an explicit manual choice');
assert.equal(createTheme(false,{saved:manual.saved}).controller.theme,'night','Keep choice after reload');
manual.controller.useSystemTheme();
assert.equal(manual.controller.theme,'day');
manual.system(true);
assert.equal(manual.controller.theme,'night');
manual.controller.setManualTheme('invalid');
assert.equal(manual.controller.mode,'system');
const blocked=createTheme(true,{blockStorage:true});
blocked.controller.setManualTheme('day');
assert.equal(blocked.controller.theme,'day');
blocked.controller.useSystemTheme();
assert.equal(blocked.controller.theme,'night');
const shared=createTheme(false);
shared.saved.set('tea-theme-preference','night');
shared.listeners.storage({key:'tea-theme-preference'});
assert.equal(shared.controller.theme,'night');
shared.saved.delete('tea-theme-preference');
shared.listeners.storage({key:null});
assert.equal(shared.controller.mode,'system');
assert.equal(shared.controller.theme,'day');
assert.equal(createTheme(false,{preference:'invalid'}).controller.mode,'system');
assert.equal(createTheme(false,{noMedia:true}).controller.theme,'day');
assert.equal(createTheme(true,{noBody:true}).document.documentElement.dataset.teaTheme,'night','Avoid first-paint flash');
console.log('Passed: system light/dark, live changes, manual choice, restore system, reload, storage sync, legacy migration and first paint.');
