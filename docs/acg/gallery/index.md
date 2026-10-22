---
hide:
  - toc
---

# 快来看轻音少女美图

放课后的私人画集角落。图片会完整显示在视窗里，可以按顺序翻页，也可以输入原文件编号直接跳转。

<section class="artbook" aria-label="轻音少女画集浏览器" aria-busy="true">
  <div class="artbook-heading">
    <label for="album-select">选择画集</label>
    <select id="album-select" disabled><option>正在读取画集…</option></select>
    <span id="album-description"></span>
  </div>
  <div class="artbook-viewport" tabindex="0" aria-label="图片视窗，使用左右方向键翻页">
    <img id="artbook-image" alt="" decoding="async">
    <p id="artbook-placeholder">正在打开画集…</p>
    <button class="artbook-fullscreen" id="artbook-fullscreen" type="button" disabled>全屏查看</button>
  </div>
  <div class="artbook-controls">
    <button id="artbook-prev" type="button" disabled>← 上一张</button>
    <span id="artbook-counter">— / —</span>
    <button id="artbook-next" type="button" disabled>下一张 →</button>
    <form id="artbook-jump">
      <label for="artbook-number">图片编号</label>
      <input id="artbook-number" type="number" min="1" step="1" inputmode="numeric" required disabled>
      <button type="submit" disabled>跳转</button>
    </form>
    <a id="artbook-original" target="_blank" rel="noopener" hidden>打开原图 ↗</a>
  </div>
  <p id="artbook-status" role="status" aria-live="polite">正在读取图片列表…</p>
</section>

<noscript>请在浏览器中启用 JavaScript，以使用随机背景和画集翻页功能。</noscript>

小提示：点击图片视窗后，可用键盘的 **← / →** 翻页；全屏时按 **Esc** 退出。可以复制浏览器地址，保存当前图片的位置。
