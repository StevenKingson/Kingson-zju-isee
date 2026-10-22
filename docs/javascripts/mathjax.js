(() => {
  "use strict";
  window.MathJax = {
    tex: {
      inlineMath: [["\\(", "\\)"]],
      displayMath: [["\\[", "\\]"]],
      processEscapes: true,
      processEnvironments: true,
    },
    options: {ignoreHtmlClass: ".*|", processHtmlClass: "arithmatex"},
    startup: {typeset: false},
  };
  let queue = Promise.resolve();
  const processed = new WeakSet();
  function renderMath() {
    queue = queue.then(async () => {
      if (!window.MathJax?.startup?.promise) return;
      await MathJax.startup.promise;
      const article = document.querySelector(".md-content__inner");
      if (!article || processed.has(article)) return;
      // Instant navigation replaces <head>; rebuild MathJax's dynamic styles.
      MathJax.startup.output.clearCache();
      MathJax.typesetClear();
      MathJax.texReset();
      await MathJax.typesetPromise([article]);
      processed.add(article);
    }).catch((error) => console.warn("公式暂时无法排版", error));
  }
  if (typeof document$ !== "undefined") document$.subscribe(renderMath);
  window.addEventListener("load", renderMath, {once: true});
})();
