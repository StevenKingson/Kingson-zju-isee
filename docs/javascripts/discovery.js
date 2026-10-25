((global) => {
  "use strict";
  function safePath(value, root) {
    if (typeof value !== "string" || value.length > 600) return null;
    try {
      const target = new URL(value, root);
      if (target.origin !== root.origin || !target.pathname.startsWith(root.pathname)
        || target.username || target.password || !target.pathname.endsWith("/")) return null;
      return target.pathname.slice(root.pathname.length);
    } catch { return null; }
  }
  function cleanEntries(value, root, limit = 200) {
    if (!Array.isArray(value)) return [];
    const seen = new Set();
    return value.filter((item) => item && typeof item.title === "string")
      .map((item) => ({ url: safePath(item.url, root), title: item.title.trim().slice(0, 160),
        time: Number.isFinite(item.time) ? item.time : 0 }))
      .filter((item) => item.url !== null && item.title && !seen.has(item.url) && seen.add(item.url))
      .slice(0, limit);
  }
  function filterCourses(courses, filters, saved = new Set()) {
    const terms = filters.q.normalize("NFKC").toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    return courses.filter((course) => {
      const text = [course.title, course.aliases, course.category].join(" ").normalize("NFKC").toLocaleLowerCase();
      return (!filters.year || course.year === filters.year)
        && (!filters.category || course.category === filters.category)
        && (filters.type !== "reports" || course.reports)
        && (filters.type !== "downloads" || course.downloads > 0)
        && (filters.type !== "saved" || saved.has(course.url))
        && terms.every((term) => text.includes(term));
    });
  }
  if (typeof module !== "undefined" && module.exports) module.exports = { safePath, cleanEntries, filterCourses };
  if (typeof document === "undefined") return;

  const root = new URL("../", document.currentScript.src);
  const BOOKMARKS = "tea-reading-bookmarks-v1", HISTORY = "tea-reading-history-v1";
  const memory = new Map();
  const temporaryKeys = new Set();
  let pageEvents, catalogue;
  const make = (tag, cls, text) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  };
  const link = (title, path, cls = "") => {
    const anchor = make("a", cls, title);
    anchor.href = new URL(path, root).href;
    return anchor;
  };
  function read(key, limit) {
    try {
      if (!temporaryKeys.has(key)) memory.set(key, JSON.parse(localStorage.getItem(key)) || []);
    } catch { /* Keep the in-page fallback. */ }
    return cleanEntries(memory.get(key), root, limit);
  }
  function save(key, entries) {
    memory.set(key, entries);
    try {
      localStorage.setItem(key, JSON.stringify(entries)); temporaryKeys.delete(key); return true;
    } catch { temporaryKeys.add(key); return false; }
  }
  function loadCatalogue() {
    if (!catalogue) catalogue = fetch(new URL("assets/discovery.json", root)).then((response) => {
      if (!response.ok) throw Error("无法读取目录");
      return response.json();
    }).catch((error) => { catalogue = null; throw error; });
    return catalogue;
  }
  const savedPaths = () => new Set(read(BOOKMARKS).map((item) => item.url));
  function changeBookmark(title, url) {
    const entries = read(BOOKMARKS);
    const exists = entries.some((item) => item.url === url);
    const next = exists ? entries.filter((item) => item.url !== url)
      : [{title, url, time: Date.now()}, ...entries].slice(0, 200);
    const persisted = save(BOOKMARKS, next);
    refreshBookmarks();
    const status = document.querySelector(".reading-feedback");
    if (status) status.textContent = persisted ? (exists ? "已移除书签" : "已收藏，可在「书签与更新」找回")
      : "浏览器未允许保存，书签暂存到本次页面关闭前。";
  }
  function bookmarkButton(title, url, compact = false) {
    const button = make("button", `reading-bookmark${compact ? " is-compact" : ""}`);
    button.type = "button";
    button.dataset.bookmarkUrl = url;
    button.dataset.bookmarkTitle = title;
    button.dataset.compact = String(compact);
    button.addEventListener("click", () => changeBookmark(title, url), {signal: pageEvents.signal});
    return button;
  }
  function refreshBookmarks() {
    const saved = savedPaths();
    for (const button of document.querySelectorAll("[data-bookmark-url]")) {
      const selected = saved.has(button.dataset.bookmarkUrl);
      button.textContent = button.dataset.compact === "true" ? (selected ? "★" : "☆")
        : (selected ? "★ 已收藏" : "☆ 收藏本页");
      button.setAttribute("aria-pressed", String(selected));
      button.setAttribute("aria-label", `${selected ? "取消收藏" : "收藏"}：${button.dataset.bookmarkTitle}`);
      button.title = selected ? "点击取消收藏" : "保存在当前浏览器";
    }
    document.querySelector("[data-course-explorer]")?.dispatchEvent(new Event("bookmarkschange"));
  }

  function setupPageActions() {
    const heading = document.querySelector(".md-content__inner h1");
    const path = safePath(location.href, root);
    if (!heading || !path || path === "desk/" || document.querySelector(".reading-page-actions")) return;
    const history = read(HISTORY, 8).filter((item) => item.url !== path);
    save(HISTORY, [{title: heading.textContent.trim(), url: path, time: Date.now()}, ...history].slice(0, 8));
    // The overview already has a bookmark control on every course card.
    if (path === "course/") return;
    const bar = make("div", "reading-page-actions");
    const status = make("span", "reading-feedback");
    status.setAttribute("role", "status");
    bar.append(bookmarkButton(heading.textContent.trim(), path), link("我的书签 ↗", "desk/"), status);
    heading.after(bar);
    refreshBookmarks();
  }

  function setupExplorer(host, data) {
    host.replaceChildren();
    const heading = make("div", "discovery-heading");
    const title = make("h2", "", "课程速查");
    heading.append(title, make("span", "discovery-count", `${data.courses.length} 个课程入口`));
    const searchLabel = make("label", "discovery-search", "搜索课程");
    const input = make("input");
    input.type = "search";
    input.placeholder = "课程名或简称，例如：电工训、数值分析";
    input.autocomplete = "off";
    searchLabel.append(input);
    const controls = make("div", "discovery-controls");
    const yearGroup = make("div", "discovery-years");
    yearGroup.setAttribute("role", "group");
    yearGroup.setAttribute("aria-label", "筛选学年");
    const filters = {q: "", year: "", category: "", type: ""};
    let visible = 12;
    const categoryLabel = make("label", "discovery-select", "课程类别");
    const category = make("select");
    category.setAttribute("aria-label", "课程类别");
    categoryLabel.append(category);
    const typeLabel = make("label", "discovery-select", "内容类型");
    const type = make("select");
    type.setAttribute("aria-label", "内容类型");
    for (const [value, text] of [["", "全部内容"], ["reports", "有实验 / 总结报告"], ["downloads", "有下载资料"], ["saved", "已收藏的课程"]]) {
      const option = make("option", "", text); option.value = value; type.append(option);
    }
    typeLabel.append(type);
    const status = make("p", "discovery-status");
    status.setAttribute("role", "status");
    const grid = make("div", "discovery-grid");
    const more = make("button", "discovery-more", "再看 12 个课程入口 ↓");
    more.type = "button";
    const feedback = make("p", "reading-feedback");
    feedback.setAttribute("role", "status");

    function render() {
      const matches = filterCourses(data.courses, filters, savedPaths());
      grid.replaceChildren();
      status.textContent = `找到 ${matches.length} 个课程入口${matches.length > visible ? ` · 先展示 ${visible} 个` : ""}`;
      for (const course of matches.slice(0, visible)) {
        const card = make("article", "discovery-card");
        const top = make("div", "discovery-card-top");
        top.append(make("span", "discovery-meta", `${course.year} · ${course.category}`), bookmarkButton(course.title, course.url, true));
        const name = make("h3"); name.append(link(course.title, course.url));
        const facts = make("p", "discovery-card-facts", course.summary || "课程心得与学习记录");
        const links = make("div", "discovery-card-links");
        links.append(link("课程心得 →", course.url));
        if (course.reports) links.append(link("报告预览", course.reports));
        if (course.resources) links.append(link("配套资料", course.resources));
        if (course.downloads) facts.append(make("span", "discovery-downloads", `${course.downloads} 份可下载文件`));
        card.append(top, name, facts, links); grid.append(card);
      }
      if (!matches.length) {
        const empty = make("div", "discovery-empty");
        empty.append(make("strong", "", "还没找到这门课"), make("p", "", "试试更短的关键词，或放宽学年、类别和内容筛选。"));
        const reset = make("button", "discovery-more", "清除筛选"); reset.type = "button";
        reset.addEventListener("click", () => {
          Object.assign(filters, {q: "", year: "", category: "", type: ""});
          input.value = type.value = ""; updateCategories(); updateYears(); render(); input.focus();
        }, {signal: pageEvents.signal});
        empty.append(reset); grid.append(empty);
      }
      more.hidden = matches.length <= visible;
      // Update the new star buttons without recursively rerendering the finder.
      const saved = savedPaths();
      for (const button of grid.querySelectorAll("[data-bookmark-url]")) {
        const selected = saved.has(button.dataset.bookmarkUrl);
        button.textContent = selected ? "★" : "☆";
        button.setAttribute("aria-pressed", String(selected));
        button.setAttribute("aria-label", `${selected ? "取消收藏" : "收藏"}：${button.dataset.bookmarkTitle}`);
        button.title = selected ? "点击取消收藏" : "保存在当前浏览器";
      }
    }
    function updateCategories() {
      category.replaceChildren();
      const categories = [...new Set(data.courses.filter((c) => !filters.year || c.year === filters.year).map((c) => c.category))];
      if (!categories.includes(filters.category)) filters.category = "";
      for (const text of ["全部类别", ...categories]) {
        const option = make("option", "", text); option.value = text === "全部类别" ? "" : text; category.append(option);
      }
      category.value = filters.category;
    }
    function updateYears() {
      for (const button of yearGroup.children) button.setAttribute("aria-pressed", String(button.dataset.year === filters.year));
    }
    for (const [value, text] of [["", "全部学年"], ["大一", "大一"], ["大二", "大二"]]) {
      const button = make("button", "", text); button.type = "button"; button.dataset.year = value;
      button.addEventListener("click", () => { filters.year = value; visible = 12; updateCategories(); updateYears(); render(); }, {signal: pageEvents.signal});
      yearGroup.append(button);
    }
    input.addEventListener("input", () => { filters.q = input.value; visible = 12; render(); }, {signal: pageEvents.signal});
    category.addEventListener("change", () => { filters.category = category.value; visible = 12; render(); }, {signal: pageEvents.signal});
    type.addEventListener("change", () => { filters.type = type.value; visible = 12; render(); }, {signal: pageEvents.signal});
    more.addEventListener("click", () => { visible += 12; render(); }, {signal: pageEvents.signal});
    host.addEventListener("bookmarkschange", () => {
      // Keep focus on the star the reader just clicked unless filtering removes it.
      if (filters.type === "saved") render();
    }, {signal: pageEvents.signal});
    controls.append(yearGroup, categoryLabel, typeLabel);
    host.append(heading, searchLabel, controls, status, grid, more, feedback);
    updateCategories(); updateYears(); render();
  }

  function renderDesk(host, data) {
    host.replaceChildren();
    const privacy = make("p", "desk-privacy", "书签和最近浏览只保存在当前浏览器；无需登录，清除浏览器数据后会丢失。" );
    host.append(privacy);
    function section(title, note, entries, kind) {
      const area = make("section", "desk-section");
      const header = make("div", "discovery-heading");
      header.append(make("h2", "", title), make("span", "discovery-count", `${entries.length}${kind === "updates" ? " 条" : " 篇"}`));
      area.append(header, make("p", "desk-note", note));
      if (!entries.length) {
        const empty = make("div", "discovery-empty");
        const message = kind === "saved" ? "还没有书签。在文章标题下点击「☆ 收藏本页」，就能把它留在这里。"
          : kind === "updates" ? "暂时没有更新记录，课程仍可从导航正常阅读。" : "读过的课程笔记和文章会出现在这里。";
        empty.append(make("p", "", message), link("去课程页逛逛 →", "course/"));
        area.append(empty);
      } else {
        const list = make("ul", "desk-list");
        for (const entry of entries) {
          const item = make("li");
          const copy = make("div"); copy.append(link(entry.title, entry.url));
          if (kind === "updates") copy.append(make("p", "desk-row-meta", `${entry.date}${entry.section ? " · " + entry.section : ""}`));
          else copy.append(make("p", "desk-row-meta", `${kind === "saved" ? "收藏于" : "阅读于"} ${new Date(entry.time).toLocaleDateString("zh-CN")}`));
          item.append(copy);
          if (kind === "saved") {
            const remove = make("button", "desk-remove", "移除"); remove.type = "button";
            remove.setAttribute("aria-label", `移除书签：${entry.title}`);
            remove.addEventListener("click", () => {
              save(BOOKMARKS, read(BOOKMARKS).filter((p) => p.url !== entry.url));
              renderDesk(host, data);
              host.querySelector(".desk-section h2")?.focus();
            }, {signal: pageEvents.signal});
            item.append(remove);
          }
          list.append(item);
        }
        area.append(list);
      }
      area.querySelector("h2").tabIndex = -1;
      host.append(area);
    }
    section("我的收藏", "把常用课程和想回看的内容放在一起。", read(BOOKMARKS), "saved");
    section("最近浏览", "保留最近打开的 8 个页面，方便继续阅读。", read(HISTORY, 8), "history");
    section("最近更新", "近期补充或修改的内容，从这里看看有什么新东西。", data.updates, "updates");
  }

  async function initialize() {
    pageEvents?.abort();
    pageEvents = new AbortController();
    const signal = pageEvents.signal;
    setupPageActions();
    const explorer = document.querySelector("[data-course-explorer]");
    const desk = document.querySelector("[data-reading-desk]");
    global.addEventListener("storage", (event) => {
      if ([BOOKMARKS, HISTORY].includes(event.key)) refreshBookmarks();
    }, {signal});
    if (!explorer && !desk) return;
    try {
      const data = await loadCatalogue();
      if (signal.aborted) return;
      if (explorer) setupExplorer(explorer, data);
      if (desk) renderDesk(desk, data);
      global.addEventListener("storage", (event) => {
        if (![BOOKMARKS, HISTORY].includes(event.key)) return;
        if (desk) renderDesk(desk, data);
      }, {signal});
    } catch {
      if (signal.aborted) return;
      const host = explorer || desk;
      host.replaceChildren(make("p", "", "目录暂时没能打开，请刷新重试。课程仍可从学年入口和侧边导航阅读。"), link("浏览大一课程", "course/year1/"), make("span", "", " · "), link("浏览大二课程", "course/year2/"));
    }
  }
  if (global.document$?.subscribe) global.document$.subscribe(initialize);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize);
  else initialize();
})(globalThis);
