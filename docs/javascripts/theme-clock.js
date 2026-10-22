// Runs in the document head so the local-time theme is applied before painting.
(() => {
  "use strict";
  if (window.teaThemeClock) {
    window.teaThemeClock.sync();
    return;
  }
  const storageKey = "tea-theme-time-override";
  let override = readOverride();
  let timer;
  let theme;

  function readOverride() {
    try { return JSON.parse(localStorage.getItem(storageKey)); } catch { return null; }
  }

  function currentPeriod(now) {
    const hour = now.getHours();
    const day = hour >= 6 && hour < 18;
    const start = new Date(now);
    if (hour < 6) start.setDate(start.getDate() - 1);
    start.setHours(day ? 6 : 18, 0, 0, 0);
    const next = new Date(now);
    if (hour >= 18) next.setDate(next.getDate() + 1);
    next.setHours(day ? 18 : 6, 0, 0, 0);
    return { key: String(start.getTime()), theme: day ? "day" : "night", next };
  }

  function sync() {
    const now = new Date();
    const period = currentPeriod(now);
    const value = override?.period === period.key && ["day", "night"].includes(override.theme)
      ? override.theme : period.theme;
    const changed = value !== theme;
    theme = value;
    document.documentElement.dataset.teaTheme = theme;
    if (document.body) document.body.dataset.mdColorScheme = theme === "night" ? "slate" : "default";
    if (changed) window.dispatchEvent(new CustomEvent("tea-theme-change", { detail: theme }));
    clearTimeout(timer);
    // Check clock/time-zone changes each minute and also at the next boundary.
    timer = setTimeout(sync, Math.min(60000, Math.max(100, period.next.getTime() - now.getTime() + 20)));
  }

  function setManualTheme(value) {
    if (!["day", "night"].includes(value)) return;
    override = { theme: value, period: currentPeriod(new Date()).key };
    try { localStorage.setItem(storageKey, JSON.stringify(override)); } catch { /* Works in memory, too. */ }
    sync();
  }

  window.teaThemeClock = { get theme() { return theme; }, setManualTheme, sync };
  window.addEventListener("focus", sync);
  window.addEventListener("pageshow", sync);
  window.addEventListener("storage", (event) => {
    if (event.key === storageKey || event.key === null) {
      override = readOverride();
      sync();
    }
  });
  document.addEventListener("visibilitychange", () => { if (!document.hidden) sync(); });
  sync();
})();
