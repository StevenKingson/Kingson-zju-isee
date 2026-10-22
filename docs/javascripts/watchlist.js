(() => {
  "use strict";
  if (window.teaWatchlist) return;
  window.teaWatchlist = true;
  const root = new URL("../", document.currentScript.src);
  const recommendationUrl = "https://github.com/StevenKingson/Kingson-zju-isee/issues/new?template=anime-recommendation.yml";
  let events;
  const make = (tag, className, text) => {
    const element = document.createElement(tag);
    element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  };
  function makeCard(anime, key, signal) {
    const card = make("article", "anime-card");
    const button = make("button", "anime-cover");
    button.type = "button";
    button.setAttribute("aria-label", `查看《${anime.title}》的评价`);
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", `anime-review-${key}`);
    const image = make("img", "anime-image");
    image.src = new URL(anime.cover, root).href;
    image.alt = `${anime.title} 官方视觉图`;
    image.width = 600;
    image.height = 850;
    image.decoding = "async";
    if (anime.coverFit === "cover") image.classList.add("anime-image-fill");
    button.append(image);
    button.append(make("span", `anime-status${anime.completed ? " is-complete" : ""}`, anime.completed ? "已看完" : anime.status),
      make("span", "anime-cover-hint", "点击看评价 ↗"));
    const overlay = make("span", "anime-review");
    overlay.id = `anime-review-${key}`;
    overlay.hidden = true;
    const score = typeof anime.score === "number" ? `${anime.score} / 10` : "暂未评分";
    overlay.append(make("span", "anime-review-label", "KING桑的观后感"), make("strong", "anime-score", score),
      make("span", "anime-review-text", anime.review || "还没有写下评价，等看完再来聊聊。"),
      make("span", "anime-review-close", "再点一次收起 · Esc 关闭"));
    button.append(overlay);
    function setOpen(open) {
      overlay.hidden = !open;
      button.setAttribute("aria-expanded", String(open));
      button.setAttribute("aria-label", `${open ? "收起" : "查看"}《${anime.title}》的评价`);
    }
    button.addEventListener("click", () => setOpen(overlay.hidden), { signal });
    button.addEventListener("keydown", (event) => {
      if (event.key === "Escape") { setOpen(false); event.preventDefault(); }
    }, { signal });
    card.append(button, make("h4", "anime-title", anime.title));
    const meta = make("div", "anime-card-meta");
    meta.append(make("span", "anime-card-score", typeof anime.score === "number" ? `★ ${anime.score} / 10` : "评分待更新"));
    const source = make("a", "anime-source", "官方视觉图 ↗");
    source.href = anime.source;
    source.target = "_blank";
    source.rel = "noopener noreferrer";
    source.title = anime.sourceName;
    meta.append(source);
    card.append(meta);
    return card;
  }
  async function initialize() {
    events?.abort();
    events = new AbortController();
    const { signal } = events;
    const target = document.getElementById("anime-watchlist");
    if (!target) return;
    try {
      const response = await fetch(new URL("assets/anime/watchlist.json", root), { signal });
      if (!response.ok) throw new Error("watchlist unavailable");
      const data = await response.json();
      const shelves = make("div", "anime-shelves");
      const sections = [
        { key: "watching", title: "正在追", intro: "按季度收藏，每周的期待。", groups: data.watching },
        { key: "planned", title: "打算补", intro: "好故事从不怕晚一点相遇。", groups: [{ season: "待补清单", anime: data.planned }] },
        { key: "recommended", title: "疯狂推", intro: "看过之后，仍然念念不忘。", groups: [{ season: "我的心头好", anime: data.recommended }] }
      ];
      sections.forEach((section, index) => {
        const shelf = make("section", `anime-shelf anime-${section.key}`);
        const heading = make("h2", "anime-shelf-title");
        heading.id = `anime-${section.key}`;
        shelf.setAttribute("aria-labelledby", heading.id);
        heading.append(make("span", "anime-shelf-number", `0${index + 1}`), document.createTextNode(section.title),
          make("span", "anime-count", String(section.groups.reduce((sum, group) => sum + group.anime.length, 0))));
        shelf.append(heading, make("p", "anime-shelf-intro", section.intro));
        section.groups.forEach((group, groupIndex) => {
          const groupBox = make("div", "anime-season");
          groupBox.append(make("h3", "anime-season-title", group.season));
          group.anime.forEach((anime, animeIndex) => groupBox.append(makeCard(anime, `${section.key}-${groupIndex}-${animeIndex}`, signal)));
          shelf.append(groupBox);
        });
        if (!section.groups.some((group) => group.anime.length)) shelf.append(make("p", "anime-empty", "这一页，留给下一个好故事。"));
        if (section.key === "planned") {
          const link = make("a", "anime-recommend-link", "推荐一部番 ↗");
          link.href = recommendationUrl;
          link.target = "_blank";
          link.rel = "noopener noreferrer";
          shelf.append(link, make("p", "anime-recommend-note", "通过 GitHub 留下你的推荐理由。"));
        }
        shelves.append(shelf);
      });
      if (!signal.aborted) target.replaceChildren(shelves);
    } catch (error) {
      if (error.name !== "AbortError") {
        target.replaceChildren(make("p", "anime-empty", "日记暂时未能打开，请刷新页面再试一次。"));
      }
    } finally {
      target.setAttribute("aria-busy", "false");
    }
  }
  if (typeof document$ !== "undefined") document$.subscribe(initialize);
  else initialize();
})();
