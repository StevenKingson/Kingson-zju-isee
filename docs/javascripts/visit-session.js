/* Share one visit between tabs. This stores session state, never a local total. */
((global) => {
  "use strict";
  const KEY = "tea-visit-session-v1", TOKEN = KEY + "-token", FALLBACK = KEY + "-fallback";
  const TIMEOUT = 30 * 60 * 1000;
  function createVisitSession(env) {
    const now = () => env.Date.now();
    const uid = () => env.crypto?.randomUUID?.() || `${now()}-${Math.random().toString(36).slice(2)}`;
    const tab = uid();
    let memory = null, joined = false, allowHandoff = true;
    function get(store, key) { try { return env[store].getItem(key); } catch { return null; } }
    function read() {
      try { return JSON.parse(get("localStorage", KEY) || get("sessionStorage", FALLBACK)) || memory; }
      catch { return memory; }
    }
    function write(record) {
      memory = record;
      const raw = JSON.stringify(record);
      try { env.localStorage.setItem(KEY, raw); }
      catch { try { env.sessionStorage.setItem(FALLBACK, raw); } catch { /* In-memory fallback. */ } }
    }
    function lock(action) {
      return env.navigator?.locks?.request ? env.navigator.locks.request(KEY, action) : Promise.resolve(action());
    }
    function continuation() {
      const type = env.performance?.getEntriesByType?.("navigation")?.[0]?.type;
      if (type === "reload") return true;
      try { return env.isInternal(env.document.referrer); } catch { return false; }
    }
    function claim() {
      const time = now();
      let record = read();
      if (!record || typeof record.id !== "string" || !Number.isFinite(record.lastSeen)
        || time - record.lastSeen >= TIMEOUT || !record.tabs || typeof record.tabs !== "object") record = null;
      if (record) {
        record.tabs = Object.fromEntries(Object.entries(record.tabs)
          .filter(([, seen]) => Number.isFinite(seen) && time - seen < TIMEOUT));
        const handoff = allowHandoff && get("sessionStorage", TOKEN) === record.id && continuation();
        if (!Object.keys(record.tabs).length && !joined && !handoff) record = null;
      }
      if (!record) record = {id: uid(), tabs: {}, lastSeen: time, attempted: false};
      record.tabs[tab] = time; record.lastSeen = time;
      const count = !record.attempted;
      // Reserve before requesting: an ambiguous network failure must not cause
      // another tab or reload to submit the same visit a second time.
      record.attempted = true;
      write(record); joined = true; allowHandoff = true;
      try { env.sessionStorage.setItem(TOKEN, record.id); } catch { /* Optional. */ }
      return {count, id: record.id};
    }
    function leave() {
      const record = read();
      if (record?.tabs?.[tab] !== undefined) {
        delete record.tabs[tab]; record.lastSeen = now(); write(record);
      }
      joined = false;
    }
    function heartbeat() {
      return lock(() => {
        const record = read();
        if (!joined || !record?.tabs || record.tabs[tab] === undefined) return;
        record.tabs[tab] = now(); record.lastSeen = now(); write(record);
      });
    }
    return {claim: () => lock(claim), heartbeat, leave,
      reenter() { joined = false; allowHandoff = false; }};
  }
  if (typeof module !== "undefined" && module.exports) module.exports = {createVisitSession, TIMEOUT};
  else global.teaVisitSession = {createVisitSession};
})(globalThis);
