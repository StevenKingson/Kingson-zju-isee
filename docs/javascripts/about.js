(() => {
  "use strict";
  if (window.teaAbout) return;
  window.teaAbout = true;
  let events;
  function initialize() {
    events?.abort();
    events = new AbortController();
    const { signal } = events;
    const hero = document.querySelector(".about-hero");
    if (!hero) return;
    const fit = () => hero.style.setProperty("--about-top", `${hero.getBoundingClientRect().top + window.scrollY}px`);
    fit();
    const observer = new ResizeObserver(fit);
    document.querySelectorAll(".md-header, .md-tabs").forEach((element) => observer.observe(element));
    window.addEventListener("resize", fit, { signal });
    const dialog = document.getElementById("wechat-contact");
    const button = hero.querySelector(".about-wechat-button");
    button.addEventListener("click", () => dialog.showModal(), { signal });
    dialog.querySelector(".about-dialog-close").addEventListener("click", () => dialog.close(), { signal });
    dialog.addEventListener("click", (event) => {
      if (event.target !== dialog) return;
      const box = dialog.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
    }, { signal });
    signal.addEventListener("abort", () => { observer.disconnect(); if (dialog.open) dialog.close(); }, { once: true });
  }
  if (typeof document$ !== "undefined") document$.subscribe(initialize);
  else initialize();
})();
