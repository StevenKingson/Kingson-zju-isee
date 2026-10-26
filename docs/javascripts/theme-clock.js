// Apply the system preference in the document head, before the first paint.
(() => {
  "use strict";
  if (window.teaThemeClock) { window.teaThemeClock.sync(); return; }
  const storageKey = "tea-theme-preference";
  const system = window.matchMedia?.("(prefers-color-scheme: dark)");
  // Ignore the old time-based override, so existing visitors start in system mode.
  const read = () => {
    try {
      const value = localStorage.getItem(storageKey);
      return ["day", "night"].includes(value) ? value : "system";
    } catch { return "system"; }
  };
  let mode = read(), theme, notifiedMode;
  function sync() {
    const next = mode === "system" ? (system?.matches ? "night" : "day") : mode;
    const changed = next !== theme || mode !== notifiedMode;
    theme = next;
    notifiedMode = mode;
    document.documentElement.dataset.teaTheme = theme;
    if (document.body) document.body.dataset.mdColorScheme = theme === "night" ? "slate" : "default";
    if (changed) window.dispatchEvent(new CustomEvent("tea-theme-change", { detail: theme }));
  }
  function setMode(value) {
    if (!["system", "day", "night"].includes(value)) return;
    mode = value;
    try { localStorage.setItem(storageKey, mode); } catch { /* Keep this tab's choice. */ }
    sync();
  }
  window.teaThemeClock = {
    get theme() { return theme; }, get mode() { return mode; },
    setManualTheme: (value) => { if (["day", "night"].includes(value)) setMode(value); },
    useSystemTheme: () => setMode("system"), sync,
  };
  if (system?.addEventListener) system.addEventListener("change", sync);
  else system?.addListener?.(sync);
  window.addEventListener("focus", sync);
  window.addEventListener("pageshow", sync);
  window.addEventListener("storage", (event) => {
    if (event.key === storageKey || event.key === null) { mode = read(); sync(); }
  });
  document.addEventListener("visibilitychange", () => { if (!document.hidden) sync(); });
  sync();
})();
