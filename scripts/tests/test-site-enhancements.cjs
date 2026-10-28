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

// Exercise the real page lifecycle with fake fetch responses, never real counts.
function environment(url, cached = null) {
  const nodes = Object.fromEntries(['uptime', 'visits', 'visits-status'].map(key => [`[data-site-${key}]`, {textContent: ''}]));
  let initialize;
  const requests = [], timers = new Map(), intervals = new Set(), events = {};
  let tick = 0;
  const document = {
    hidden: false, readyState: 'complete',
    querySelector: key => key === '[data-site-stats]' ? {} : nodes[key],
    addEventListener: (name, fn) => {events[name] = fn;}
  };
  const context = vm.createContext({URL, Date, AbortController, document, location: {href: url},
    localStorage: {getItem: () => cached, setItem(key, value) { cached = value; }},
    document$: {subscribe(fn) {initialize = fn; fn();}},
    fetch(url, options) {
      return new Promise((resolve, reject) => {
        requests.push({url, options, resolve, reject});
        options.signal.addEventListener('abort', () => reject(Error('aborted')));
      });
    },
    setTimeout(fn) {timers.set(++tick, fn); return tick;}, clearTimeout(id) {timers.delete(id);},
    setInterval(fn) {intervals.add(++tick); return tick;}, clearInterval(id) {intervals.delete(id);}
  });
  vm.runInContext(fs.readFileSync(require.resolve('../../docs/javascripts/site-stats.js'), 'utf8'), context);
  const flush = () => new Promise(resolve => setImmediate(resolve));
  async function respond(request, body, ok = true) {
    request.resolve({ok, json: async () => body}); await flush();
  }
  return {context, nodes, requests, timers, intervals, events, document, respond, flush,
    navigate: () => initialize(), cached: () => cached};
}
(async () => {
  const local = environment('http://127.0.0.1:8000/changelog/');
  assert.equal(local.requests.length, 0);
  assert.equal(local.nodes['[data-site-visits]'].textContent, '上线后开始统计');
  local.navigate(); assert.equal(local.intervals.size, 1);
  local.document.hidden = true; local.events.visibilitychange(); assert.equal(local.intervals.size, 0);
  local.document.hidden = false; local.events.visibilitychange(); assert.equal(local.intervals.size, 1);

  const live = environment(base + '?secret=private#heading');
  assert.equal(live.requests.length, 1);
  const body = JSON.parse(live.requests[0].options.body);
  assert.equal(body.url, base); assert.equal(body.isNewUv, false);
  assert.equal(live.requests[0].options.credentials, 'omit');
  assert.equal(live.requests[0].options.referrerPolicy, 'no-referrer');
  live.navigate(); assert.equal(live.requests.length, 2);
  await live.respond(live.requests[1], {status:'success', data:{site_pv:42}});
  await live.respond(live.requests[0], {status:'success', data:{site_pv:41}});
  assert.equal(live.nodes['[data-site-visits]'].textContent, '42 次');
  assert.equal(JSON.parse(live.cached()).value, 42);
  assert.equal(live.intervals.size, 1); assert.equal(live.timers.size, 0);

  for (const response of [{status:'success',data:{site_pv:'<img>'}}, {status:'error',data:{site_pv:0}}, {}]) {
    const invalid = environment(base); await invalid.respond(invalid.requests[0], response);
    assert.equal(invalid.nodes['[data-site-visits]'].textContent, '暂不可用');
  }
  const failed = environment(base); failed.requests[0].reject(Error('Network failed')); await failed.flush();
  assert.equal(failed.nodes['[data-site-visits]'].textContent, '暂不可用');
  assert.equal(failed.timers.size, 0);
  const timeout = environment(base); [...timeout.timers.values()][0](); await timeout.flush();
  assert.equal(timeout.nodes['[data-site-visits]'].textContent, '暂不可用');
  assert.equal(timeout.timers.size, 0);
  const restored = environment(base, JSON.stringify({value:42, time:start}));
  assert.equal(restored.nodes['[data-site-visits]'].textContent, '42 次（上次读数）');
  restored.requests[0].reject(Error('Network failed')); await restored.flush();
  assert.equal(restored.nodes['[data-site-visits]'].textContent, '42 次（上次读数）');
  assert.ok(restored.nodes['[data-site-visits-status]'].textContent.includes('上次读取：'));
  console.log('Passed: external URLs, uptime, local exclusion, JSON response, privacy, navigation races, marked cached values and failure cleanup.');
})().catch(error => { console.error(error); process.exitCode = 1; });
