# 网站维护约定

- 本网站使用 MkDocs Material，工作目录是本仓库。保留用户自己尚未提交的改动。
- 每次完成网站功能、资料或番剧内容更新时，同步维护 `docs/changelog/index.md`。按 Asia/Shanghai 的实际日期倒序整理；同日记录合并在同一日期下。描述用户能看到的变化，不直接堆砌 Git 提交信息，不把未完成内容写成已上线。只有本地预览时明确标注。
- 追番清单的原稿是 `docs/assets/anime/watchlist.json`；修改后运行 `scripts/update-watchlist.py`，同步可搜索的无脚本文本。保留用户评价的原意，官方封面出处记入 `scripts/anime-artwork-sources.md`。
- 默认主题跟随设备的 `prefers-color-scheme`，不按时间切换。手动按钮再次点击可恢复跟随系统。
- 运行适合当前改动的检查及 `mkdocs build --strict`。是否上传依照当次用户指示，不把本地预览当作上传授权。
