/* Site age is local; shared visit counts come from the public Busuanzi service. */
((global) => {
  "use strict";
  const OPENED_AT = "2026-10-22T17:08:29+08:00";
  const PUBLIC_ROOT = "https://stevenkingson.github.io/Kingson-zju-isee/";
  const COUNTER_ENDPOINT = "https://busuanzi.ibruce.info/busuanzi";
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
  let timer, sequence = 0, visits = null, state = "loading";
  function render() {
    const clock = document.querySelector("[data-site-uptime]");
    if (clock) clock.textContent = uptime(Date.now());
    const counter = document.querySelector("[data-site-visits]");
    const detail = document.querySelector("[data-site-visits-status]");
    if (!counter) return;
    counter.textContent = state === "local" ? "上线后开始统计"
      : visits !== null ? `${visits.toLocaleString("zh-CN")} 次`
        : state === "error" ? "暂不可用" : "正在读取…";
    detail.textContent = state === "local" ? "本地预览不计入访问人次"
      : state === "error" ? "统计服务暂不可用，下次打开页面时重试"
        : "全站页面访问次数，重复访问也会计入";
  }
  function countVisit() {
    if (!isPublicPage(location.href)) { state = "local"; render(); return; }
    const request = ++sequence;
    const callback = `teaVisit_${Date.now()}_${request}`;
    const script = document.createElement("script");
    let settled = false, timeout;
    const cleanup = () => { clearTimeout(timeout); script.remove(); delete global[callback]; };
    const fail = () => {
      if (settled) return;
      settled = true;
      if (request === sequence) { state = "error"; render(); }
      cleanup();
    };
    global[callback] = (data) => {
      if (settled) return;
      const value = visitValue(data?.site_pv);
      if (value === null) { fail(); return; }
      settled = true;
      // A slow response from the previous page must not replace the newest count.
      if (request === sequence) { visits = value; state = "ready"; render(); }
      cleanup();
    };
    script.async = true;
    script.src = `${COUNTER_ENDPOINT}?jsonpCallback=${callback}`;
    script.referrerPolicy = "strict-origin-when-cross-origin";
    script.onerror = fail;
    script.onload = () => { if (!settled) fail(); };
    timeout = setTimeout(fail, 10000);
    document.head.append(script);
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
