const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {isExternal} = require('../../docs/javascripts/site-links.js');
const {uptime, isPublicPage, visitValue} = require('../../docs/javascripts/site-stats.js');
const base = 'https://stevenkingson.github.io/Kingson-zju-isee/course/';
for (const value of ['https://www.cc98.org/topic/1', '//example.org/', 'https://space.bilibili.com/1']) {
  assert.equal(isExternal(value, base), true);
}
for (const value of ['../about/', '#heading', base, 'mailto:test@example.com', 'tel:123', 'javascript:void(0)']) {
  assert.equal(isExternal(value, base), false);
}
const start = Date.parse('2026-10-22T17:08:29+08:00');
assert.equal(uptime(start), '0 天 00 时 00 分 00 秒');
assert.equal(uptime(start + 90061000), '1 天 01 时 01 分 01 秒');
assert.equal(uptime(start - 1), '0 天 00 时 00 分 00 秒');
assert.equal(isPublicPage(base), true);
for (const value of ['http://localhost:8000/', 'http://127.0.0.1:8000/', 'https://preview.example/',
  'https://stevenkingson.github.io/Kingson-zju-isee-other/', 'https://stevenkingson.github.io/']) {
  assert.equal(isPublicPage(value), false);
}
for (const value of [null, '123', -1, Infinity, 1.5, Number.MAX_SAFE_INTEGER + 1, '<img>']) assert.equal(visitValue(value), null);
assert.equal(visitValue(0), 0);

// Exercise the real page lifecycle with fake network responses, never real counts.
function environment(url) {
  const nodes = Object.fromEntries(['uptime', 'visits', 'visits-status'].map(key => [`[data-site-${key}]`, {textContent: ''}]));
  let initialize;
  const requests = [], timers = new Map(), intervals = new Set(), events = {};
  let tick = 0;
  const document = {
    hidden: false, readyState: 'complete',
    querySelector: key => key === '[data-site-stats]' ? {} : nodes[key],
    addEventListener: (name, fn) => {events[name] = fn;},
    createElement: () => ({remove() {this.removed = true;}}),
    head: {append: script => requests.push(script)}
  };
  const context = vm.createContext({URL, Date, document, location: {href: url},
    document$: {subscribe(fn) {initialize = fn; fn();}},
    setTimeout(fn) {timers.set(++tick, fn); return tick;}, clearTimeout(id) {timers.delete(id);},
    setInterval(fn) {intervals.add(++tick); return tick;}, clearInterval(id) {intervals.delete(id);}
  });
  vm.runInContext(fs.readFileSync(require.resolve('../../docs/javascripts/site-stats.js'), 'utf8'), context);
  function respond(script, data) {
    const name = new URL(script.src).searchParams.get('jsonpCallback');
    context[name](data);
    assert.equal(context[name], undefined);
    assert.equal(script.removed, true);
  }
  return {context, nodes, requests, timers, intervals, events, document, respond, navigate: () => initialize()};
}
const local = environment('http://127.0.0.1:8000/changelog/');
assert.equal(local.requests.length, 0);
assert.equal(local.nodes['[data-site-visits]'].textContent, '上线后开始统计');
local.navigate(); assert.equal(local.intervals.size, 1);
local.document.hidden = true; local.events.visibilitychange(); assert.equal(local.intervals.size, 0);
local.document.hidden = false; local.events.visibilitychange(); assert.equal(local.intervals.size, 1);

const live = environment(base);
assert.equal(live.requests.length, 1);
live.navigate(); assert.equal(live.requests.length, 2);
live.respond(live.requests[1], {site_pv: 42});
live.respond(live.requests[0], {site_pv: 41}); // Slow previous page response.
assert.equal(live.nodes['[data-site-visits]'].textContent, '42 次');
assert.equal(live.intervals.size, 1);
const failed = environment(base); failed.requests[0].onerror();
assert.equal(failed.nodes['[data-site-visits]'].textContent, '暂不可用');
assert.equal(failed.timers.size, 0);
const invalid = environment(base); invalid.respond(invalid.requests[0], {site_pv: '<img>'});
assert.equal(invalid.nodes['[data-site-visits]'].textContent, '暂不可用');
const timeout = environment(base); [...timeout.timers.values()][0]();
assert.equal(timeout.nodes['[data-site-visits]'].textContent, '暂不可用');
console.log('Passed: external URLs, uptime, local exclusion, instant navigation counts, response races, failure and timer cleanup.');
