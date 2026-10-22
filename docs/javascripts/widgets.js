(() => {
  "use strict";
  if (window.teaWidgets) return;
  window.teaWidgets = true;
  const root = new URL("../", document.currentScript.src);
  const url = (path) => new URL(path, root).href;
  const read = (key, fallback, storage = localStorage) => {
    try { return JSON.parse(storage.getItem(key)) ?? fallback; } catch { return fallback; }
  };
  const save = (key, value, storage = localStorage) => {
    try { storage.setItem(key, JSON.stringify(value)); return true; } catch { return false; }
  };
  const make = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };
  const imagePath = "assets/characters/";
  let theme = document.documentElement.dataset.teaTheme || "day";
  const tools = make("div", "tea-tools");
  tools.setAttribute("aria-label", "主题与背景音乐");
  const themeButton = make("button", "tea-icon-button tea-theme-button");
  themeButton.type = "button";
  const themeImage = new Image();
  themeImage.alt = "";
  const themeBadge = make("span", "tea-icon-badge");
  themeButton.append(themeImage, themeBadge);
  const playButton = make("button", "tea-icon-button tea-music-button");
  playButton.type = "button";
  const avatar = make("span", "music-avatar");
  avatar.setAttribute("aria-hidden", "true");
  avatar.dataset.character = String(Math.floor(Math.random() * 5));
  const playBadge = make("span", "tea-icon-badge", "▶");
  playButton.append(avatar, playBadge);
  const listButton = make("button", "tea-list-button", "☷");
  listButton.type = "button";
  listButton.setAttribute("aria-label", "打开歌曲目录");
  listButton.setAttribute("aria-expanded", "false");
  listButton.setAttribute("aria-controls", "tea-music-panel");
  tools.append(themeButton, playButton, listButton);

  const panel = make("section", "tea-music-panel");
  panel.id = "tea-music-panel";
  panel.hidden = true;
  panel.setAttribute("aria-label", "歌曲目录");
  const heading = make("div", "music-panel-heading");
  const close = make("button", "tea-text-button", "关闭 ×");
  close.type = "button";
  close.setAttribute("aria-label", "关闭歌曲目录");
  heading.append(make("strong", "", "放课后点歌台"), close);
  const nowPlaying = make("p", "music-now-playing", "正在读取曲库…");
  const musicStatus = make("p", "music-status");
  musicStatus.setAttribute("role", "status");
  const trackList = make("div", "music-track-list");
  const playerControls = make("div", "music-player-controls");
  const randomButton = make("button", "tea-text-button", "随机下一首 ↻");
  randomButton.type = "button";
  const volumeLabel = make("label", "", "音量");
  const volume = make("input");
  volume.type = "range";
  volume.min = "0";
  volume.max = "1";
  volume.step = "0.05";
  volume.value = String(read("tea-volume", 0.4));
  volume.setAttribute("aria-label", "背景音乐音量");
  volumeLabel.append(volume);
  playerControls.append(randomButton, volumeLabel);
  panel.append(heading, nowPlaying, musicStatus, trackList, playerControls,
    make("p", "music-footnote", "随机播放 · 首次有声播放可能需要点击 ▶"));
  const audio = new Audio();
  audio.id = "tea-bgm";
  audio.preload = "metadata";
  audio.volume = Math.max(0, Math.min(1, Number(volume.value) || 0));
  document.body.append(panel, audio);

  function applyTheme(value) {
    theme = value;
    document.documentElement.dataset.teaTheme = theme;
    document.body.dataset.mdColorScheme = theme === "night" ? "slate" : "default";
    themeImage.src = url(`${imagePath}theme-${theme}.png${theme === "night" ? "?v=pajamas-242" : ""}`);
    themeBadge.textContent = theme === "day" ? "☀" : "☾";
    themeButton.setAttribute("aria-label", theme === "day" ? "切换到夜晚主题" : "切换到白天主题");
    themeButton.title = theme === "day" ? "白天 · 点击切换夜晚" : "夜晚 · 点击切换白天";
    const frame = document.querySelector("iframe.giscus-frame");
    frame?.contentWindow?.postMessage({ giscus: { setConfig: { theme: theme === "night" ? "dark" : "light" } } }, "https://giscus.app");
  }
  themeButton.addEventListener("click", () => {
    applyTheme(theme === "day" ? "night" : "day");
    try { localStorage.setItem("tea-theme", theme); } catch { /* Still works for this visit. */ }
  });
  applyTheme(theme);

  function openPanel(open) {
    panel.hidden = !open;
    listButton.setAttribute("aria-expanded", String(open));
    if (open) close.focus();
  }
  listButton.addEventListener("click", () => openPanel(panel.hidden));
  close.addEventListener("click", () => { openPanel(false); listButton.focus(); });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !panel.hidden) { openPanel(false); listButton.focus(); }
  });
  document.addEventListener("click", (event) => {
    if (!panel.hidden && !panel.contains(event.target) && !tools.contains(event.target)) openPanel(false);
  });

  let tracks = [];
  let current = -1;
  let attempted = new Set();
  const resume = read("tea-bgm-session", null, sessionStorage);
  function rememberMusic() {
    if (current < 0) return;
    save("tea-bgm-session", {id: tracks[current].id, time: audio.currentTime,
      playing: !audio.paused, volume: audio.volume}, sessionStorage);
  }
  function syncPlayer() {
    playBadge.textContent = audio.paused ? "▶" : "Ⅱ";
    playButton.setAttribute("aria-label", audio.paused ? "播放背景音乐" : "暂停背景音乐");
    playButton.setAttribute("aria-pressed", String(!audio.paused));
    playButton.title = `${audio.paused ? "播放" : "暂停"}：${tracks[current]?.title || "背景音乐"}`;
    tools.classList.toggle("is-playing", !audio.paused);
    for (const [index, button] of [...trackList.children].entries()) {
      button.classList.toggle("is-current", index === current);
      button.setAttribute("aria-pressed", String(index === current));
    }
    if (current >= 0) nowPlaying.textContent = `${audio.paused ? "已选" : "正在播放"} · ${tracks[current].title}`;
  }
  async function play() {
    try {
      await audio.play();
      musicStatus.textContent = "";
      attempted.clear();
    } catch (error) {
      if (error.name === "AbortError") return;
      musicStatus.textContent = error.name === "NotAllowedError"
        ? "歌曲已随机选好，点击右上角 ▶ 开始播放。"
        : "这首歌暂时无法播放，请重新点击播放或选择其他歌曲。";
    }
    syncPlayer();
  }
  function selectTrack(index, autoplay = true, seek = 0) {
    if (!tracks.length) return;
    current = index;
    audio.src = url(tracks[current].src);
    if (seek > 0) audio.addEventListener("loadedmetadata", () => {
      if (Number.isFinite(audio.duration)) audio.currentTime = Math.min(seek, Math.max(0, audio.duration - 0.1));
    }, {once: true});
    audio.load();
    syncPlayer();
    if (autoplay) void play();
  }
  function randomTrack() {
    if (!tracks.length) return;
    let next = Math.floor(Math.random() * tracks.length);
    if (tracks.length > 1 && next === current) next = (next + 1) % tracks.length;
    selectTrack(next);
  }
  playButton.disabled = true;
  randomButton.disabled = true;
  syncPlayer();
  playButton.addEventListener("click", () => {
    if (audio.paused) void play(); else audio.pause();
  });
  randomButton.addEventListener("click", randomTrack);
  volume.addEventListener("input", () => {
    audio.volume = Number(volume.value);
    save("tea-volume", audio.volume);
  });
  audio.addEventListener("play", () => { syncPlayer(); rememberMusic(); });
  audio.addEventListener("pause", () => { syncPlayer(); rememberMusic(); });
  audio.addEventListener("ended", randomTrack);
  audio.addEventListener("error", () => {
    attempted.add(current);
    if (attempted.size < tracks.length) {
      const next = tracks.findIndex((_, index) => !attempted.has(index));
      selectTrack(next);
    } else {
      musicStatus.textContent = "曲库中的歌曲暂时无法播放，请检查音乐文件或更换浏览器。";
      openPanel(true);
    }
  });
  window.addEventListener("pagehide", rememberMusic);
  let lastSaved = 0;
  audio.addEventListener("timeupdate", () => {
    if (Date.now() - lastSaved > 3000) { rememberMusic(); lastSaved = Date.now(); }
  });
  fetch(url("assets/music/playlist.json")).then((response) => {
    if (!response.ok) throw new Error();
    return response.json();
  }).then((data) => {
    tracks = data.tracks;
    if (!tracks.length) {
      nowPlaying.textContent = "曲库还没有歌曲";
      musicStatus.textContent = "将歌曲放入 docs/assets/music 后重新启动预览。";
      return;
    }
    tracks.forEach((track, index) => {
      const button = make("button", "music-track", `${String(index + 1).padStart(2, "0")}  ${track.title}`);
      button.type = "button";
      button.addEventListener("click", () => { attempted.clear(); selectTrack(index); });
      trackList.append(button);
    });
    playButton.disabled = false;
    randomButton.disabled = false;
    const resumedIndex = resume ? tracks.findIndex((track) => track.id === resume.id) : -1;
    if (resumedIndex >= 0) selectTrack(resumedIndex, resume.playing, resume.time);
    else randomTrack();
  }).catch(() => {
    nowPlaying.textContent = "暂时无法读取歌曲目录";
    musicStatus.textContent = "请刷新重试，或重新启动预览更新曲库。";
  });

  // A single companion is visible at a time; all nine source figures are selectable.
  const petNames = ["平泽唯", "山中佐和子", "琴吹紬", "平泽忧", "铃木纯", "田井中律", "秋山澪", "真锅和", "中野梓"];
  const pet = make("div", "course-pet");
  pet.id = "course-pet";
  pet.hidden = true;
  const petImage = new Image();
  petImage.draggable = false;
  petImage.alt = "";
  pet.tabIndex = 0;
  pet.setAttribute("role", "group");
  pet.setAttribute("aria-label", "课程页桌宠，可拖动；聚焦后用方向键移动");
  pet.append(petImage);
  document.body.append(pet);
  let petIndex = Math.max(0, Math.min(8, Number(read("tea-pet-character", 0)) || 0));
  let drag = null;
  function updatePet() {
    petImage.src = url(`${imagePath}pet-${150 + petIndex}.png`);
    pet.title = `${petNames[petIndex]} · 按住拖动`;
  }
  updatePet();
  function positionPet(x, y) {
    const top = (document.querySelector(".md-header")?.getBoundingClientRect().bottom || 48) + 8;
    x = Math.max(4, Math.min(x, innerWidth - pet.offsetWidth - 4));
    y = Math.max(top, Math.min(y, innerHeight - pet.offsetHeight - 4));
    pet.style.left = `${x}px`;
    pet.style.top = `${y}px`;
    pet.style.right = "auto";
    pet.style.bottom = "auto";
  }
  pet.addEventListener("pointerdown", (event) => {
    if (event.button !== 0) return;
    const rect = pet.getBoundingClientRect();
    drag = {id: event.pointerId, dx: event.clientX - rect.left, dy: event.clientY - rect.top};
    pet.setPointerCapture(event.pointerId);
    pet.classList.add("is-dragging");
  });
  pet.addEventListener("pointermove", (event) => {
    if (drag?.id === event.pointerId) positionPet(event.clientX - drag.dx, event.clientY - drag.dy);
  });
  const finishDrag = () => { drag = null; pet.classList.remove("is-dragging"); };
  pet.addEventListener("pointerup", finishDrag);
  pet.addEventListener("pointercancel", finishDrag);
  pet.addEventListener("lostpointercapture", finishDrag);
  pet.addEventListener("keydown", (event) => {
    const movement = {ArrowLeft: [-12, 0], ArrowRight: [12, 0], ArrowUp: [0, -12], ArrowDown: [0, 12]}[event.key];
    if (movement) {
      event.preventDefault();
      const rect = pet.getBoundingClientRect();
      positionPet(rect.left + movement[0], rect.top + movement[1]);
    }
  });
  window.addEventListener("resize", () => {
    if (!pet.hidden && pet.style.left) {
      const rect = pet.getBoundingClientRect();
      positionPet(rect.left, rect.top);
    }
  });

  function setupCourse() {
    const coursePath = new URL("course/", root).pathname;
    pet.hidden = !(location.pathname === coursePath.slice(0, -1) || location.pathname.startsWith(coursePath));
    if (pet.hidden) return;
    const controls = make("div", "course-pet-settings");
    const label = make("label", "", "陪读角色 ");
    const select = make("select");
    select.setAttribute("aria-label", "选择陪读角色");
    petNames.forEach((name, index) => {
      const option = make("option", "", `${name} · ${150 + index} 号`);
      option.value = String(index);
      select.append(option);
    });
    select.value = String(petIndex);
    select.addEventListener("change", () => {
      petIndex = Number(select.value);
      save("tea-pet-character", petIndex);
      updatePet();
    });
    const toggle = make("button", "tea-text-button", "收起桌宠");
    toggle.type = "button";
    toggle.addEventListener("click", () => {
      pet.hidden = !pet.hidden;
      toggle.textContent = pet.hidden ? "显示桌宠" : "收起桌宠";
    });
    label.append(select);
    controls.append(label, toggle, make("span", "", "按住右下角的角色即可拖动"));
    document.querySelector(".md-content__inner h1")?.after(controls);
  }

  function setupLocalGuestbook(container) {
    const list = container.querySelector("#guestbook-messages");
    const status = container.querySelector("#guestbook-status");
    const form = container.querySelector("#guestbook-form");
    const key = "tea-guestbook-local-v1";
    const stored = read(key, []);
    let messages = Array.isArray(stored) ? stored.filter((item) => typeof item?.name === "string" && typeof item?.message === "string") : [];
    container.querySelector("#guestbook-local").hidden = false;
    function render() {
      list.replaceChildren();
      if (!messages.length) list.append(make("p", "guestbook-empty", "还没有本机留言，来留第一句话吧。"));
      for (const item of messages) {
        const article = make("article", "guestbook-message");
        const date = new Date(item.date);
        article.append(make("strong", "", item.name), make("time", "", Number.isNaN(date.getTime()) ? "" : date.toLocaleString("zh-CN")), make("p", "", item.message));
        list.append(article);
      }
    }
    render();
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const name = form.elements.name.value.trim();
      const message = form.elements.message.value.trim();
      if (!name || !message) { status.textContent = "昵称和留言都要填写文字哦。"; return; }
      const updated = [{name: name.slice(0, 30), message: message.slice(0, 1000), date: new Date().toISOString()}, ...messages].slice(0, 100);
      if (!save(key, updated)) { status.textContent = "浏览器无法保存留言，请先复制文字备份。"; return; }
      messages = updated;
      form.elements.message.value = "";
      render();
      status.textContent = "已保存在当前浏览器，其他访客不可见。";
    });
    container.querySelector("#guestbook-export").addEventListener("click", () => {
      const blob = new Blob([JSON.stringify(messages, null, 2)], {type: "application/json"});
      const href = URL.createObjectURL(blob);
      const anchor = make("a");
      anchor.href = href;
      anchor.download = "茶会本机留言备份.json";
      anchor.click();
      setTimeout(() => URL.revokeObjectURL(href), 1000);
    });
  }

  async function setupGuestbook() {
    const container = document.getElementById("guestbook");
    if (!container) return;
    const notice = container.querySelector("#guestbook-notice");
    try {
      const response = await fetch(url("assets/giscus.json"));
      if (!response.ok) throw new Error();
      const config = await response.json();
      if (!container.isConnected) return;
      const configured = config.repo && config.repoId && config.category && config.categoryId;
      if (!configured) {
        if (["localhost", "127.0.0.1", "[::1]"].includes(location.hostname)) {
          notice.textContent = "本机预览模式 · 留言仅保存在当前浏览器，不会公开或自动同步。最多保留最近 100 条，请按需导出备份。GitHub 仓库创建后，可接通 Giscus 共享留言。";
          setupLocalGuestbook(container);
        } else {
          notice.textContent = "茶会留言板正在准备中，站长接通 GitHub 留言服务后即可使用。";
        }
        return;
      }
      notice.textContent = "共享留言由 GitHub Discussions 保存，登录 GitHub 后即可留言。";
      const script = document.createElement("script");
      script.src = "https://giscus.app/client.js";
      script.async = true;
      script.crossOrigin = "anonymous";
      const attributes = {repo: config.repo, "repo-id": config.repoId, category: config.category,
        "category-id": config.categoryId, mapping: "specific", term: "KING桑の放课后茶会 · 留言板",
        strict: "1", "reactions-enabled": "1", "emit-metadata": "0", "input-position": "top",
        theme: theme === "night" ? "dark" : "light", lang: "zh-CN", loading: "lazy"};
      for (const [key, value] of Object.entries(attributes)) script.setAttribute(`data-${key}`, value);
      script.addEventListener("error", () => { notice.textContent = "暂时无法连接 GitHub 留言服务，请稍后刷新重试。"; });
      container.querySelector(".giscus").append(script);
    } catch {
      if (container.isConnected) notice.textContent = "留言配置读取失败，请刷新重试。";
    }
  }

  function pageReady() {
    // The player and audio element persist while Material swaps the page content.
    document.querySelector(".md-header__inner")?.append(tools);
    document.body.dataset.mdColorScheme = theme === "night" ? "slate" : "default";
    openPanel(false);
    setupCourse();
    void setupGuestbook();
  }
  if (typeof document$ !== "undefined") document$.subscribe(pageReady);
  else pageReady();
})();
