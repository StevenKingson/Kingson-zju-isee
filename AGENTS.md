# 网站维护约定

- 本网站使用 MkDocs Material，工作目录是本仓库。保留用户自己尚未提交的改动。
- 每次完成网站功能、资料或番剧内容更新时，同步维护 `docs/changelog/index.md`。按 Asia/Shanghai 的实际日期倒序整理；同日记录合并在同一日期下。描述用户能看到的变化，不直接堆砌 Git 提交信息，不把未完成内容写成已上线。只有本地预览时明确标注。
- 追番清单的原稿是 `docs/assets/anime/watchlist.json`；修改后运行 `scripts/update-watchlist.py`，同步可搜索的无脚本文本。保留用户评价的原意，官方封面出处记入 `scripts/anime-artwork-sources.md`。
- 默认主题跟随设备的 `prefers-color-scheme`，不按时间切换。手动按钮再次点击可恢复跟随系统。
- 运行适合当前改动的检查及 `mkdocs build --strict`。按用户的长期授权，网站修改完成并检查通过后，默认提交、推送至本站 GitHub 仓库并确认 Pages 发布成功，无需再次询问上传；若用户提前明确说明“先不上传”“只做本地预览”等，则仅完成本地修改。保留与本次任务无关的用户未提交改动。
