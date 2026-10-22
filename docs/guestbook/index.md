---
hide:
  - toc
---

# 留言板

来过茶会，就留下几句话吧。聊聊喜欢的番剧、最近在听的歌，或者简单打个招呼。

<section id="guestbook" aria-label="茶会留言板">
  <div id="guestbook-notice" class="guestbook-notice" role="status">正在准备留言板…</div>
  <div class="giscus" id="giscus-comments"></div>
  <div id="guestbook-local" hidden>
    <form id="guestbook-form" class="guestbook-form">
      <label for="guestbook-name">怎么称呼你</label>
      <input id="guestbook-name" name="name" maxlength="30" placeholder="茶会的朋友" autocomplete="nickname" required>
      <label for="guestbook-message">想说的话</label>
      <textarea id="guestbook-message" name="message" rows="4" maxlength="1000" placeholder="今天也来喝杯茶吧…" required></textarea>
      <div class="guestbook-submit-row">
        <span>最多 1000 字 · 纯文字留言</span>
        <button type="submit">保存本机留言</button>
      </div>
    </form>
    <div class="guestbook-list-heading"><h2>本机留言</h2><button id="guestbook-export" type="button">导出备份 ↓</button></div>
    <div id="guestbook-messages" aria-live="polite"></div>
    <p id="guestbook-status" role="status"></p>
  </div>
</section>

<noscript>请启用 JavaScript 来查看和填写留言。</noscript>
