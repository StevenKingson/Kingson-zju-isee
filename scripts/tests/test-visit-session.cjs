const assert = require('node:assert/strict');
const {createVisitSession, TIMEOUT} = require('../../docs/javascripts/visit-session.js');
function storage() {
  const values = new Map();
  return {getItem:key=>values.get(key) || null, setItem:(key,value)=>values.set(key,value)};
}
let time = 100000, serial = 0, queue = Promise.resolve();
const locks = {request(key, action) {
  const task = queue.then(action); queue = task.catch(()=>{}); return task;
}};
function browser(shared, tabStorage = storage(), type = 'navigate', referrer = '') {
  return {env: {localStorage:shared, sessionStorage:tabStorage,
    Date:{now:()=>time}, crypto:{randomUUID:()=>String(++serial)}, navigator:{locks},
    performance:{getEntriesByType:()=>[{type}]}, document:{referrer},
    isInternal:value=>value.startsWith('https://site.example/')}, tabStorage};
}
function tab(shared, saved, type, referrer) {
  const {env,tabStorage}=browser(shared,saved,type,referrer);
  return {visit:createVisitSession(env),saved:tabStorage};
}
(async()=>{
  const shared=storage(), a=tab(shared), b=tab(shared);
  const first=await Promise.all([a.visit.claim(),b.visit.claim()]);
  assert.equal(first.filter(x=>x.count).length,1,'simultaneous tabs count once');
  assert.equal(first[0].id,first[1].id);
  assert.equal((await a.visit.claim()).count,false,'instant navigation only reads');
  a.visit.leave();
  const back=tab(shared,a.saved,'navigate','https://outside.example/');
  assert.equal((await back.visit.claim()).count,false,'another site tab keeps the visit alive');
  b.visit.leave(); back.visit.leave();
  const refresh=tab(shared,back.saved,'reload');
  assert.equal((await refresh.visit.claim()).count,false,'full reload with no other tabs continues');
  refresh.visit.leave();
  const internal=tab(shared,refresh.saved,'navigate','https://site.example/course/');
  assert.equal((await internal.visit.claim()).count,false,'normal internal document navigation continues');
  internal.visit.leave();
  const next=tab(shared);
  assert.equal((await next.visit.claim()).count,true,'new tab after the last close is a new visit');
  next.visit.leave();
  const externalReturn=tab(shared,next.saved,'navigate','https://outside.example/');
  assert.equal((await externalReturn.visit.claim()).count,true,'leaving and returning in same tab starts a visit');
  externalReturn.visit.leave(); externalReturn.visit.reenter();
  assert.equal((await externalReturn.visit.claim()).count,true,'bfcache return after last exit starts a visit');
  time+=TIMEOUT+1; // A forced shutdown never delivered pagehide.
  assert.equal((await tab(shared).visit.claim()).count,true,'stale crash leases expire');
  const alive=tab(shared); await alive.visit.claim();
  time+=TIMEOUT-10; await alive.visit.heartbeat(); time+=20;
  assert.equal((await tab(shared).visit.claim()).count,false,'heartbeat keeps open tabs alive');
  const reserved=tab(storage()); await reserved.visit.claim();
  assert.equal((await reserved.visit.claim()).count,false,'network uncertainty never resubmits a visit');
  const denied={getItem(){throw Error('blocked');},setItem(){throw Error('blocked');}};
  const privateTab=tab(denied); assert.equal((await privateTab.visit.claim()).count,true);
  privateTab.visit.leave();
  const privateReload=tab(denied,privateTab.saved,'reload');
  assert.equal((await privateReload.visit.claim()).count,false,'sessionStorage fallback survives a reload');
  console.log('Passed: multi-tab races, refresh, internal navigation, last close, external return, bfcache, crash timeout and storage fallback.');
})().catch(error=>{console.error(error);process.exitCode=1;});
