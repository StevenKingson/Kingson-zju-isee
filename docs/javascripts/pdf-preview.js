(() => {
  "use strict";
  const root = new URL("../", document.currentScript.src);
  const vendor = new URL("javascripts/vendor/pdfjs/", root);
  let library;
  let cleanups = [];
  function pdfLibrary() {
    if (!library) library = import(new URL("pdf.min.mjs", vendor).href).then((pdfjs) => {
      pdfjs.GlobalWorkerOptions.workerSrc = new URL("pdf.worker.min.mjs", vendor).href;
      return pdfjs;
    }).catch((error) => { library = undefined; throw error; });
    return library;
  }
  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function initialize(details) {
    const source = new URL(details.dataset.pdf, location.href).href;
    const toolbar = element("div", "pdf-toolbar");
    const previous = element("button", "", "← 上一页");
    const next = element("button", "", "下一页 →");
    previous.type = next.type = "button";
    const form = element("form", "pdf-page-form");
    const label = element("label", "", "页码 ");
    const input = element("input");
    input.type = "number";
    input.min = input.step = input.value = "1";
    input.required = true;
    input.setAttribute("aria-label", "PDF 页码");
    const total = element("span", "pdf-total", "/ —");
    const jump = element("button", "", "跳转");
    jump.type = "submit";
    label.append(input);
    form.append(label, total, jump);
    const zoom = element("select");
    zoom.setAttribute("aria-label", "PDF 缩放");
    for (const [value, text] of [["1", "适应宽度"], ["1.25", "放大至 125%"], ["1.5", "放大至 150%"], ["2", "放大至 200%"]]) {
      const option = element("option", "", text);
      option.value = value;
      zoom.append(option);
    }
    toolbar.append(previous, form, next, zoom);
    const viewport = element("div", "pdf-viewport");
    viewport.tabIndex = 0;
    viewport.setAttribute("aria-label", "PDF 页面预览，可滚动查看");
    const canvas = element("canvas");
    canvas.hidden = true;
    canvas.setAttribute("role", "img");
    viewport.append(canvas);
    const status = element("p", "pdf-status", "展开后加载 PDF。");
    status.setAttribute("role", "status");
    const retry = element("button", "pdf-retry", "重新加载 PDF");
    retry.type = "button";
    retry.hidden = true;
    details.append(toolbar, viewport, status, retry);
    let documentPdf;
    let loading;
    let starting = false;
    let renderTask;
    let pageNumber = 1;
    let disposed = false;
    let sequence = 0;
    let queue = Promise.resolve();
    let lastWidth = 0;
    const controls = [previous, next, input, jump, zoom];
    function syncControls() {
      const ready = !!documentPdf;
      controls.forEach((control) => { control.disabled = !ready; });
      previous.disabled = !ready || pageNumber === 1;
      next.disabled = !ready || pageNumber === documentPdf.numPages;
      input.value = String(pageNumber);
    }
    syncControls();
    function render() {
      const token = ++sequence;
      renderTask?.cancel();
      queue = queue.catch(() => {}).then(async () => {
        if (disposed || token !== sequence || !documentPdf || !details.open) return;
        const page = await documentPdf.getPage(pageNumber);
        if (disposed || token !== sequence) return;
        const width = Math.max(160, viewport.clientWidth - 24);
        const scale = width / page.getViewport({scale: 1}).width * Number(zoom.value);
        const pageView = page.getViewport({scale});
        const pixels = Math.min(devicePixelRatio || 1, 2);
        canvas.width = Math.floor(pageView.width * pixels);
        canvas.height = Math.floor(pageView.height * pixels);
        canvas.style.width = `${Math.floor(pageView.width)}px`;
        canvas.style.height = `${Math.floor(pageView.height)}px`;
        canvas.setAttribute("aria-label", `PDF 第 ${pageNumber} 页，共 ${documentPdf.numPages} 页`);
        canvas.hidden = false;
        viewport.setAttribute("aria-busy", "true");
        status.textContent = `正在显示第 ${pageNumber} 页…`;
        renderTask = page.render({canvasContext: canvas.getContext("2d"), viewport: pageView,
          transform: pixels === 1 ? null : [pixels, 0, 0, pixels, 0, 0]});
        await renderTask.promise;
        if (disposed || token !== sequence) return;
        status.textContent = `第 ${pageNumber} / ${documentPdf.numPages} 页 · 放大后可在视窗中滚动查看`;
        viewport.setAttribute("aria-busy", "false");
      }).catch((error) => {
        if (disposed || token !== sequence || error.name === "RenderingCancelledException") return;
        viewport.setAttribute("aria-busy", "false");
        status.textContent = "这页暂时无法预览，可以重新加载，或点击上方链接打开 PDF 原文件。";
        retry.hidden = false;
      });
    }
    async function load() {
      if (disposed || starting || loading || documentPdf) return;
      starting = true;
      status.textContent = "正在加载 PDF…";
      retry.hidden = true;
      let task;
      try {
        const pdfjs = await pdfLibrary();
        if (disposed) return;
        task = pdfjs.getDocument({url: source, cMapUrl: new URL("cmaps/", vendor).href,
          cMapPacked: true, standardFontDataUrl: new URL("standard_fonts/", vendor).href,
          wasmUrl: new URL("wasm/", vendor).href, isEvalSupported: false});
        loading = task;
        task.onProgress = ({loaded, total: bytes}) => {
          if (!disposed && bytes) status.textContent = `正在加载 PDF… ${Math.min(100, Math.round(loaded / bytes * 100))}%`;
        };
        const result = await task.promise;
        if (disposed) { await result.destroy(); return; }
        documentPdf = result;
        input.max = String(documentPdf.numPages);
        total.textContent = `/ ${documentPdf.numPages}`;
        syncControls();
        render();
      } catch {
        if (disposed) return;
        status.textContent = "PDF 预览未能加载，请重试，或点击上方链接打开原文件。";
        retry.hidden = false;
        await task?.destroy();
      } finally { loading = undefined; starting = false; }
    }
    details.addEventListener("toggle", () => {
      details.querySelector("summary").textContent = details.open ? "收起 PDF 预览" : "展开 PDF 预览";
      if (details.open) {
        if (documentPdf) render(); else void load();
      } else { ++sequence; renderTask?.cancel(); }
    });
    previous.addEventListener("click", () => { pageNumber = Math.max(1, pageNumber - 1); syncControls(); render(); });
    next.addEventListener("click", () => { pageNumber = Math.min(documentPdf.numPages, pageNumber + 1); syncControls(); render(); });
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!form.reportValidity() || !documentPdf) return;
      pageNumber = Number(input.value);
      syncControls();
      render();
    });
    zoom.addEventListener("change", render);
    retry.addEventListener("click", () => {
      if (documentPdf) render(); else void load();
    });
    const observer = new ResizeObserver(() => {
      const width = viewport.clientWidth;
      if (width !== lastWidth && width > 0) { lastWidth = width; if (documentPdf && details.open) render(); }
    });
    observer.observe(viewport);
    cleanups.push(() => {
      disposed = true;
      ++sequence;
      renderTask?.cancel();
      observer.disconnect();
      const currentTask = queue;
      void currentTask.finally(() => (documentPdf || loading)?.destroy()).catch(() => {});
    });
  }
  function pageReady() {
    cleanups.forEach((cleanup) => cleanup());
    cleanups = [];
    document.querySelectorAll("details.report-pdf[data-pdf]").forEach(initialize);
  }
  if (typeof document$ !== "undefined") document$.subscribe(pageReady);
  else pageReady();
})();
