/* Site age is local; shared visit counts come from the public Vercount service. */
((global) => {
  "use strict";
  const OPENED_AT = "2026-10-22T17:08:29+08:00";
  const PUBLIC_ROOT = "https://stevenkingson.github.io/Kingson-zju-isee/";
  const COUNTER_ENDPOINT = "https://events.vercount.one/api/v2/log";
  function uptime(now, start = Date.parse(OPENED_AT)) {
    let seconds = Math.max(0, Math.floor((now - start) / 1000));
    const days = Math.floor(seconds / 86400); seconds %= 86400;
    const hours = Math.floor(seconds / 3600); seconds %= 3600;
    const minutes = Math.floor(seconds / 60); seconds %= 60;
    return `${days} 天 ${String(hours).padStart(2, "0")} 时 ${String(minutes).padStart(2, "0")} 分 ${String(seconds).padStart(2, "0")} 秒`;
  }
  function isPublicPage(value) {
    try {
      const url = new URL(value), root = new URL(PUBLIC_ROOT);
      return url.origin === root.origin && url.pathname.startsWith(root.pathname);
    } catch { return false; }
  }
  function visitValue(value) {
    return typeof value === "number" && Number.isSafeInteger(value) && value >= 0 ? value : null;
  }
  if (typeof module !== "undefined" && module.exports) module.exports = { uptime, isPublicPage, visitValue };
  if (typeof document === "undefined") return;
  const CACHE_KEY = "tea-site-visits-vercount-v1";
  let timer, sequence = 0, visits = null, readAt = 0, state = "loading";
  if (isPublicPage(location.href)) {
    try {
      const cached = JSON.parse(localStorage.getItem(CACHE_KEY));
      if (visitValue(cached?.value) !== null && Number.isFinite(cached?.time)) {
        visits = cached.value; readAt = cached.time; state = "cached";
      }
    } catch { /* Storage is optional and contains only the last public count. */ }
  }
  function render() {
    const clock = document.querySelector("[data-site-uptime]");
    if (clock) clock.textContent = uptime(Date.now());
    const counter = document.querySelector("[data-site-visits]");
    const detail = document.querySelector("[data-site-visits-status]");
    if (!counter) return;
    counter.textContent = state === "local" ? "上线后开始统计"
      : visits !== null ? `${visits.toLocaleString("zh-CN")} 次${state !== "ready" ? "（上次读数）" : ""}`
        : state === "error" ? "暂不可用" : "正在读取…";
    if (!detail) return;
    detail.textContent = state === "local" ? "本地预览不计入访问人次"
      : state !== "ready" && visits !== null ? `上次读取：${new Date(readAt).toLocaleString("zh-CN")}；${state === "error" ? "连接失败，下次打开页面时重试" : "正在更新"}`
        : state === "error" ? "统计服务连接失败，下次打开页面时重试"
          : "全站页面访问次数，重复访问也会计入";
  }
  async function countVisit() {
    if (!isPublicPage(location.href)) { state = "local"; render(); return; }
    const request = ++sequence;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    // Only send the public page path: query strings, hashes and referrers aren't needed.
    const page = new URL(location.href);
    page.search = ""; page.hash = "";
    state = visits === null ? "loading" : "cached"; render();
    try {
      const response = await fetch(COUNTER_ENDPOINT, {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({url: page.href, isNewUv: false}),
        signal: controller.signal, credentials: "omit", referrerPolicy: "no-referrer"
      });
      if (!response.ok) throw Error("Counter request failed");
      const data = await response.json();
      const value = data?.status === "success" ? visitValue(data.data?.site_pv) : null;
      if (value === null) throw Error("Invalid counter response");
      if (request !== sequence) return;
      visits = value; readAt = Date.now(); state = "ready";
      try { localStorage.setItem(CACHE_KEY, JSON.stringify({value, time: readAt})); } catch { /* Optional. */ }
    } catch {
      if (request === sequence) state = "error";
    } finally {
      clearTimeout(timeout);
      if (request === sequence) render();
    }
  }
  function initialize() {
    clearInterval(timer);
    render();
    // Count every real page load and MkDocs instant navigation across the site.
    countVisit();
    if (document.querySelector("[data-site-stats]") && !document.hidden) timer = setInterval(render, 1000);
  }
  document.addEventListener("visibilitychange", () => {
    clearInterval(timer);
    if (!document.hidden) {
      render();
      if (document.querySelector("[data-site-stats]")) timer = setInterval(render, 1000);
    }
  });
  if (global.document$?.subscribe) global.document$.subscribe(initialize);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize, {once: true});
  else initialize();
})(globalThis);
