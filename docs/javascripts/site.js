(() => {
  "use strict";
  // Resolve from this script, so links also work when published in a subdirectory.
  const siteRoot = new URL("../", document.currentScript.src);
  const assetUrl = (path) => new URL(path, siteRoot).href;
  let pageEvents;
  function initializePage() {
  pageEvents?.abort();
  pageEvents = new AbortController();
  const hero = document.querySelector(".home-hero");
  const gallery = document.querySelector(".artbook");
  document.body.classList.toggle("tea-home", Boolean(hero));
  if (hero) {
    // Measure the real navigation/footer height, including changes caused by zoom.
    const chrome = [...document.querySelectorAll(".md-header, .md-tabs, .md-footer")];
    const fitHome = () => {
      const height = chrome.reduce((sum, element) => sum + element.getBoundingClientRect().height, 0);
      hero.style.setProperty("--tea-chrome-height", `${height}px`);
    };
    const observer = new ResizeObserver(fitHome);
    chrome.forEach((element) => observer.observe(element));
    pageEvents.signal.addEventListener("abort", () => observer.disconnect(), { once: true });
    fitHome();
  }
  if (!hero && !gallery) return;

  async function loadAlbums() {
    const response = await fetch(assetUrl("assets/gallery.json"));
    if (!response.ok) throw new Error("无法读取画集列表");
    const data = await response.json();
    const albums = data.albums.filter((album) => album.images.length);
    if (!albums.length) throw new Error("还没有可展示的图片");
    return albums;
  }

  function setupHome(albums) {
    const choices = albums.flatMap((album) => album.images.map((picture) => ({ album, picture })));
    const image = hero.querySelector(".home-background");
    const button = document.getElementById("change-background");
    const source = document.getElementById("background-source");
    const status = document.getElementById("background-status");
    let previous = -1;
    let request = 0;
    function changeBackground() {
      let index = Math.floor(Math.random() * choices.length);
      if (choices.length > 1 && index === previous) index = (index + 1) % choices.length;
      previous = index;
      const { album, picture } = choices[index];
      const token = ++request;
      button.disabled = true;
      status.textContent = "正在准备背景…";
      const next = new Image();
      next.onload = () => {
        if (request !== token) return;
        image.src = next.src;
        hero.classList.add("has-background");
        const url = new URL("acg/gallery/", siteRoot);
        url.searchParams.set("album", album.id);
        url.searchParams.set("image", picture.number);
        source.href = url.href;
        source.textContent = `画集 · ${String(picture.number).padStart(3, "0")} 号 ↗`;
        status.textContent = "";
        button.disabled = false;
      };
      next.onerror = () => {
        if (request !== token) return;
        status.textContent = "这张图片未能打开，请点击换一张。";
        button.disabled = false;
      };
      next.src = assetUrl(picture.src);
    }
    button.addEventListener("click", changeBackground);
    changeBackground();
  }

  function setupGallery(albums) {
    const select = document.getElementById("album-select");
    const image = document.getElementById("artbook-image");
    const placeholder = document.getElementById("artbook-placeholder");
    const previous = document.getElementById("artbook-prev");
    const next = document.getElementById("artbook-next");
    const counter = document.getElementById("artbook-counter");
    const input = document.getElementById("artbook-number");
    const form = document.getElementById("artbook-jump");
    const status = document.getElementById("artbook-status");
    const original = document.getElementById("artbook-original");
    const viewport = gallery.querySelector(".artbook-viewport");
    const fullscreen = document.getElementById("artbook-fullscreen");
    const params = new URLSearchParams(location.search);
    let album = albums.find((item) => item.id === params.get("album")) || albums[0];
    let index = 0;
    let request = 0;

    select.replaceChildren(...albums.map((item) => {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = `${item.title}（${item.images.length} 张）`;
      return option;
    }));
    select.disabled = false;
    input.disabled = false;
    form.querySelector("button").disabled = false;
    fullscreen.disabled = false;

    function showImage(target) {
      index = Math.max(0, Math.min(target, album.images.length - 1));
      const picture = album.images[index];
      const token = ++request;
      gallery.setAttribute("aria-busy", "true");
      image.classList.add("is-loading");
      placeholder.hidden = false;
      placeholder.textContent = "正在打开图片…";
      select.value = album.id;
      document.getElementById("album-description").textContent = album.description;
      previous.disabled = index === 0;
      next.disabled = index === album.images.length - 1;
      counter.textContent = `${index + 1} / ${album.images.length}`;
      input.min = Math.min(...album.images.map((item) => item.number));
      input.max = Math.max(...album.images.map((item) => item.number));
      input.value = picture.number;
      input.setCustomValidity("");
      original.hidden = true;
      status.textContent = `正在读取 ${picture.name}…`;
      const url = new URL(location.href);
      url.searchParams.set("album", album.id);
      url.searchParams.set("image", picture.number);
      history.replaceState(null, "", url);
      const pending = new Image();
      pending.onload = () => {
        if (request !== token) return;
        image.src = pending.src;
        image.alt = `${album.title} · 第 ${picture.number} 号图片`;
        image.classList.remove("is-loading");
        placeholder.hidden = true;
        gallery.setAttribute("aria-busy", "false");
        original.href = pending.src;
        original.hidden = false;
        status.textContent = `${picture.name} · ${pending.naturalWidth} × ${pending.naturalHeight} · 共 ${album.images.length} 张`;
        // Fetch only neighboring images, never the entire book at once.
        for (const neighbor of [album.images[index - 1], album.images[index + 1]]) {
          if (neighbor) new Image().src = assetUrl(neighbor.src);
        }
      };
      pending.onerror = () => {
        if (request !== token) return;
        gallery.setAttribute("aria-busy", "false");
        placeholder.textContent = "这张图片暂时无法打开。可尝试其他编号。";
        status.textContent = `读取 ${picture.name} 失败。点击“跳转”可重试。`;
      };
      pending.src = assetUrl(picture.src);
    }

    previous.addEventListener("click", () => showImage(index - 1));
    next.addEventListener("click", () => showImage(index + 1));
    select.addEventListener("change", () => {
      album = albums.find((item) => item.id === select.value);
      showImage(0);
    });
    input.addEventListener("input", () => input.setCustomValidity(""));
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const target = album.images.findIndex((picture) => picture.number === Number(input.value));
      if (target === -1) {
        input.setCustomValidity("画集中没有这个编号，请输入现有图片的编号。");
        input.reportValidity();
        return;
      }
      showImage(target);
    });
    gallery.addEventListener("keydown", (event) => {
      if (event.target.closest("input, select, button, a") || event.altKey || event.ctrlKey || event.metaKey) return;
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        showImage(index + (event.key === "ArrowLeft" ? -1 : 1));
      }
    });
    fullscreen.addEventListener("click", async () => {
      try {
        if (document.fullscreenElement) await document.exitFullscreen();
        else if (viewport.requestFullscreen) await viewport.requestFullscreen();
        else window.open(assetUrl(album.images[index].src), "_blank", "noopener");
      } catch {
        status.textContent = "浏览器暂不允许全屏，可点击“打开原图”查看。";
      }
    });
    document.addEventListener("fullscreenchange", () => {
      fullscreen.textContent = document.fullscreenElement ? "退出全屏" : "全屏查看";
    }, {signal: pageEvents.signal});
    const requested = params.get("image");
    const initial = requested === null ? 0 : album.images.findIndex((picture) => picture.number === Number(requested));
    showImage(initial < 0 ? 0 : initial);
    if (initial < 0) status.textContent = "未找到链接中的编号，已打开第一张。";
  }

  loadAlbums().then((albums) => {
    if (!(hero?.isConnected || gallery?.isConnected)) return;
    if (hero) setupHome(albums);
    if (gallery) setupGallery(albums);
  }).catch((error) => {
    if (!(hero?.isConnected || gallery?.isConnected)) return;
    if (hero) {
      document.getElementById("background-status").textContent = `${error.message}，请刷新重试。`;
      document.getElementById("change-background").disabled = true;
    }
    if (gallery) {
      gallery.setAttribute("aria-busy", "false");
      document.getElementById("artbook-placeholder").textContent = "画集暂时无法打开";
      document.getElementById("artbook-status").textContent = `${error.message}，请刷新重试。`;
    }
  });
  }
  if (typeof document$ !== "undefined") document$.subscribe(initializePage);
  else initializePage();
})();
