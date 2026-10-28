const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {isExternal} = require('../../docs/javascripts/site-links.js');
const {uptime, isPublicPage, visitValue} = require('../../docs/javascripts/site-stats.js');
const {createVisitSession} = require('../../docs/javascripts/visit-session.js');
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
  const storage = new Map(cached ? [['tea-site-session-total-v1', cached]] : []);
  const sessionStorage = new Map();
  const document = {referrer: '',
    hidden: false, readyState: 'complete',
    querySelector: key => key === '[data-site-stats]' ? {} : nodes[key],
    addEventListener: (name, fn) => {events[name] = fn;}
  };
  const context = vm.createContext({URL, Date, AbortController, document, location: {href: url},
    teaVisitSession: {createVisitSession}, navigator: {},
    localStorage: {getItem: key => storage.get(key) || null, setItem(key,value) {storage.set(key,value);}},
    sessionStorage: {getItem: key => sessionStorage.get(key) || null, setItem(key,value) {sessionStorage.set(key,value);}},
    addEventListener: (name, fn) => {events[name] = fn;},
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
    navigate: () => initialize(), cached: () => storage.get('tea-site-session-total-v1')};
}
(async () => {
  const local = environment('http://127.0.0.1:8000/changelog/');
  assert.equal(local.requests.length, 0);
  assert.equal(local.nodes['[data-site-visits]'].textContent, '上线后开始统计');
  local.navigate(); assert.equal(local.intervals.size, 1);
  local.document.hidden = true; local.events.visibilitychange(); assert.equal(local.intervals.size, 0);
  local.document.hidden = false; local.events.visibilitychange(); assert.equal(local.intervals.size, 1);

  const live = environment(base + '?secret=private#heading'); await live.flush();
  assert.equal(live.requests.length, 1);
  const body = JSON.parse(live.requests[0].options.body);
  assert.equal(body.url, 'https://stevenkingson.github.io/Kingson-zju-isee/_stats/visits-v1/'); assert.equal(body.isNewUv, false);
  assert.equal(live.requests[0].options.credentials, 'omit');
  assert.equal(live.requests[0].options.referrerPolicy, 'no-referrer');
  live.navigate(); await live.flush(); assert.equal(live.requests.length, 2);
  assert.equal(live.requests[0].options.method, 'POST');
  assert.equal(live.requests[1].options.method, 'GET');
  assert.equal(live.requests[1].options.body, undefined);
  await live.respond(live.requests[1], {status:'success', data:{page_pv:42,site_pv:999}});
  await live.respond(live.requests[0], {status:'success', data:{page_pv:41,site_pv:998}});
  assert.equal(live.nodes['[data-site-visits]'].textContent, '42 次');
  assert.equal(JSON.parse(live.cached()).value, 42);
  assert.equal(live.intervals.size, 2); assert.equal(live.timers.size, 0);

  const entryRace = environment(base); await entryRace.flush();
  entryRace.navigate(); await entryRace.flush();
  await entryRace.respond(entryRace.requests[1], {status:'success',data:{page_pv:0}});
  await entryRace.respond(entryRace.requests[0], {status:'success',data:{page_pv:1}});
  assert.equal(entryRace.nodes['[data-site-visits]'].textContent, '1 次', 'entry POST finishing after a read must still update the total');

  for (const response of [{status:'success',data:{page_pv:'<img>'}}, {status:'error',data:{page_pv:0}}, {}]) {
    const invalid = environment(base); await invalid.flush(); await invalid.respond(invalid.requests[0], response);
    assert.equal(invalid.nodes['[data-site-visits]'].textContent, '暂不可用');
  }
  const failed = environment(base); await failed.flush(); failed.requests[0].reject(Error('Network failed')); await failed.flush();
  assert.equal(failed.nodes['[data-site-visits]'].textContent, '暂不可用');
  assert.equal(failed.timers.size, 0);
  const timeout = environment(base); await timeout.flush(); [...timeout.timers.values()][0](); await timeout.flush();
  assert.equal(timeout.nodes['[data-site-visits]'].textContent, '暂不可用');
  assert.equal(timeout.timers.size, 0);
  const restored = environment(base, JSON.stringify({value:42, time:start}));
  assert.equal(restored.nodes['[data-site-visits]'].textContent, '42 次（上次读数）');
  await restored.flush(); restored.requests[0].reject(Error('Network failed')); await restored.flush();
  assert.equal(restored.nodes['[data-site-visits]'].textContent, '42 次（上次读数）');
  assert.ok(restored.nodes['[data-site-visits-status]'].textContent.includes('上次读取：'));
  console.log('Passed: external URLs, uptime, local exclusion, JSON response, privacy, read-only navigation, response races, marked cached values and failure cleanup.');
})().catch(error => { console.error(error); process.exitCode = 1; });
