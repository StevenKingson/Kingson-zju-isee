/* Dynamic cards and instant navigation share the same external-link policy. */
((global) => {
  "use strict";
  function isExternal(value, base) {
    try {
      const target = new URL(value, base);
      return /^(https?:)$/.test(target.protocol) && target.origin !== new URL(base).origin;
    } catch { return false; }
  }
  if (typeof module !== "undefined" && module.exports) module.exports = { isExternal };
  if (typeof document === "undefined") return;
  function update(anchor) {
    if (!isExternal(anchor.getAttribute("href"), location.href)) return;
    anchor.target = "_blank";
    const rel = new Set(anchor.rel.split(/\s+/).filter(Boolean));
    rel.add("noopener"); rel.add("noreferrer");
    anchor.rel = [...rel].join(" ");
  }
  function scan(node) {
    if (node.nodeType !== 1) return;
    if (node.matches("a[href]")) update(node);
    node.querySelectorAll("a[href]").forEach(update);
  }
  const observer = new MutationObserver((changes) => {
    for (const change of changes) {
      if (change.type === "attributes") update(change.target);
      else change.addedNodes.forEach(scan);
    }
  });
  function initialize() {
    scan(document.documentElement);
    observer.disconnect();
    observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ["href"] });
  }
  // Apply synchronously even to a link clicked immediately after insertion.
  document.addEventListener("click", (event) => {
    const anchor = event.target.closest?.("a[href]");
    if (anchor) update(anchor);
  }, true);
  if (global.document$?.subscribe) global.document$.subscribe(initialize);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize, {once: true});
  else initialize();
})(globalThis);
