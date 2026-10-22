# KING桑の放课后茶会

这是一个使用 MkDocs 和 Material 主题搭建的个人网站。

## 下次怎样打开网站

1. 用文件资源管理器打开这个文件夹。
2. 双击 `start-preview.bat`，保留打开的命令窗口。
3. 在浏览器地址栏输入 `http://127.0.0.1:8000/`，按回车。
4. 停止预览时，点击命令窗口，按 `Ctrl+C`；如果提示是否终止，输入 `Y` 并按回车。

这是本机预览地址。公开网站地址为 <https://stevenkingson.github.io/Kingson-isee.github.io/>，通过 GitHub Pages 自动部署。

## 怎样修改内容

1. 右键点击要修改的 `.md` 文件，选择“打开方式”→“记事本”（也可使用你喜欢的文本编辑器）。
2. 修改文字，按 `Ctrl+S` 保存。
3. 保持预览运行，浏览器通常会自动刷新。

| 文件 | 用途 |
| --- | --- |
| `mkdocs.yml` | 网站名称、主题和顶部导航 |
| `docs/index.md` | 主页 |
| `docs/course/index.md` | 课程列表 |
| `docs/friends/index.md` | 友链 |
| `docs/about/index.md` | 自我介绍 |
| `docs/stylesheets/extra.css` | 纯白主页的外观样式 |

## 怎样新增课程文章

课程区现已按你的两篇原文整理为 `docs/course/year1/`（大一）和 `docs/course/year2/`（大二），每个学年下再按原来的课程分类建文件夹。共 47 门课程，分成 45 篇课程心得；原文合写的微积分Ⅰ／Ⅱ、大二游泳中级／初级保留合写。

- 每门课的正文是对应文件夹内的 `index.md`，可直接用记事本修改。
- 两篇完整总结分别在各学年的 `overview.md`，同时保留原始 Markdown 及配图的 ZIP 下载。
- 转专业经验单独放在 `docs/course/year1/transfer.md`。
- 报告放在对应课程的 `reports/` 内，共 26 份。12 份 Markdown 报告支持在线阅读，全部 PDF 和已有的 10 份 Word 原稿都可打开或下载；数据处理脚本、图表、原始图片和数电 Lab 19 的 LaTeX 项目也保留了下载入口。
- 大物报告大压缩包与解压后的 129 个文件逐一核对一致，因此没有在网站里重复放大包；数电 LaTeX 的临时编译文件也不放入网站，已有的完整 PDF 与源项目已分别归档。
- 大二的“经济法理论与实务”和“合唱艺术”按原文目录归入“通识选修课程”；“认知实践”仍沿用正文的位置，放在“专业必修课程”；“个性修读课程”保留“本专业进阶模块／跨专业课程”层级。
- 保留原文的个人评价、成绩和经历，仅整理标题、目录、附件链接，以及网页需要的公式格式。原始资料均保留在原位置。

现有课程推荐直接修改对应文件夹的 `index.md`。导航中各分类直接列出课程；大一的“硬课”已改为“专业基础课程”，“专业课程”已改为“专业必修课程”。分类目录页与写作示例已移除。

26 份实验报告页面都提供“展开 PDF 预览”，点击后可在页面中翻页、输入页码和缩放；点击“在线打开 PDF”仍可打开原文件。预览组件放在网站本地，PDF 只在展开时加载。

部分 Word 原稿的封面仍含姓名、学号等原始信息。后续公开部署前，可先检查这些附件，按你的需要脱敏。

下面是新增一般文章的基础示例：

1. 打开 `docs/course` 文件夹。
2. 在对应学年和分类的文件夹内，新建一个课程文件夹，再新建 `index.md`；可参考已有课程的格式填写标题和正文。
3. 用记事本打开新文件，按示例修改标题和正文，然后保存。
4. 在对应学年的 `index.md` 中加上新课程链接，再在 `mkdocs.yml` 的 `nav` 对应分类中添加导航，例如：

   ```markdown
   - [我的第一篇笔记](hard/my-first-note/index.md) — 一句话介绍。
   ```

5. 保存后，到浏览器中的“课程”页面点击新文章。

## 重新安装环境（仅在环境丢失时需要）

在此文件夹的地址栏输入 `powershell` 并按回车，然后逐行输入：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m mkdocs serve
```

不需要手动激活虚拟环境。

## ACG宝库和随机背景

- 每次打开或刷新主页，都会从画集中随机挑选一张背景；点击“换一张背景”可以继续换图。
- 主页底部的图片编号可以直接打开画集中的同一张图片。
- “ACG宝库 → KING桑の追番日记”存放推荐笔记。复制 `docs/acg/diary/k-on.md` 写新文章，再在同文件夹 `index.md` 中添加链接即可。
- “ACG宝库 → 快来看轻音少女美图”可以选择画集、前后翻页、输入文件编号跳转、全屏查看或打开原图。
- 画集地址会保留当前编号，可以复制到收藏夹，下次直接打开这一张。

原来的 423 张图片已移动到 `docs/assets/artbooks/k-on-2009-2012/`，保留了 `001.jpg` 等原文件名。第 233 张的茶杯已重绘为透明底矢量图标：`docs/assets/icons/tea-cup.svg`。所有页面的大标题都会自动显示这个图案。

### 以后添加另一套画集

1. 打开 `docs/assets/artbooks`，新建一个文件夹，例如 `k-on-another-book`。
2. 将新画集图片放进去，建议命名为 `001.jpg`、`002.jpg` 等，编号不要重复。
3. 如果想自定义画集名称，复制现有画集的 `album.json` 到新文件夹，用记事本修改 `title` 和 `description` 后面的文字；保留英文双引号和逗号。
4. 停止原有预览，重新双击 `start-preview.bat`。它会自动更新图片列表。新画集会出现在画集下拉框里，也会参与主页背景随机展示。

预览运行时如果只想刷新画集目录，在项目文件夹打开 PowerShell，运行：

```powershell
.\.venv\Scripts\python.exe scripts\update-gallery.py
```

浏览器每次只加载当前图片和相邻图片，不会一次下载整套画集。

## 昼夜主题、背景音乐与陪读角色

右上角三个按钮从左到右分别是：昼夜主题、播放/暂停、歌曲目录。

- 点击主题按钮，切换白天和夜晚。首次访问跟随系统主题，之后记住你的选择。
- 白天图标取自 210 号底部第二位的唯，夜晚图标参照 182 号左侧的唯重画成 Q 版，换上 242 号左侧的奶油黄条纹睡衣、配套长裤，并在角色左眼眼角加上哈欠泪珠。
- 音乐按钮每次完整打开网站会从 119、120 号的五个耳机人物中随机选择头像。
- 初次打开默认随机选歌并尝试播放。如果浏览器阻止自动播放，点一下右上角的 ▶ 即可。主动暂停后，站内切页不会重新播放。
- 点击右上角的 ☷ 打开歌曲目录，点击歌名播放；也可以随机下一首或调整音量。
- 站内导航采用局部加载，音乐在切页时继续播放；完整刷新后会尽量恢复进度，是否自动恢复声音由浏览器决定。
- 在课程页面的大标题下，可以选择 150–158 号的九个陪读角色。默认位于右下角，按住角色拖动即可移动，也可聚焦后按方向键移动。暂时没有对话或其他互动。

### 添加歌曲

1. 将音乐文件复制到 `docs/assets/music/`。已放入的占位歌曲为 `FantasticYouth - 小喋日和.mp3`，原位置的文件保留。
2. 关闭原有预览，再双击 `start-preview.bat`。程序会自动更新曲库。
3. 打开右上角的歌曲目录，新歌会按文件名显示。

支持 MP3、OGG、WAV、M4A、AAC、FLAC；实际可播放的格式取决于浏览器，优先使用 MP3。当前只有一首歌时，“随机下一首”会重新播放这首歌。

预览运行时也可以手动刷新曲库：

```powershell
.\.venv\Scripts\python.exe scripts\update-music.py
```

然后完整刷新浏览器页面。曲库内不会自动包含电脑其他位置的文件。

## 留言板：本机预览与共享留言

网站仓库已创建为 `StevenKingson/Kingson-isee.github.io`。共享留言还需要接通 Giscus；本机预览时，留言只保存在当前浏览器，最多保留最近 100 条。清除浏览器数据可能使它们丢失，可以点击“导出备份”下载 JSON 文件。本机留言不会自动发布或同步到 GitHub。

上线后的共享留言使用 [Giscus](https://giscus.app/zh-CN)，保存到 GitHub Discussions。未完成配置时，公开网站只显示“正在准备中”，不会把本机预览当成共享留言。

按以下步骤接通：

1. 打开准备存放留言的 **公开 GitHub 仓库**，点击顶部 **Settings**。
2. 在 **General → Features** 中，勾选 **Discussions**。
3. 打开 [Giscus 配置页](https://giscus.app/zh-CN)，按网页提示安装 Giscus 应用，并只选择需要使用的仓库。
4. 在 Giscus 网页的“仓库”栏输入 `StevenKingson/Kingson-isee.github.io`，选择一个 Discussion 分类，例如 Announcements。
5. 向下找到自动生成的 `<script>` 配置，里面会出现 `data-repo`、`data-repo-id`、`data-category`、`data-category-id`。
6. 用记事本打开 `docs/assets/giscus.json`，把这四个值分别填入 `repo`、`repoId`、`category`、`categoryId` 的英文双引号中。不要删除逗号和双引号，也不需要粘贴整段脚本。
7. 保存并刷新。留言页会自动切换成共享留言，访客登录 GitHub 后即可留言。留言可在仓库的 Discussions 中管理，昼夜主题也会同步到评论框。

这里填写的仓库和分类 ID 是公开配置，不需要填写 GitHub 密码或访问令牌。

## GitHub Pages 自动部署

源代码仓库：<https://github.com/StevenKingson/Kingson-isee.github.io>。

网站网址：<https://stevenkingson.github.io/Kingson-isee.github.io/>。

`.github/workflows/ci.yml` 会在每次推送到 `main` 后安装 `requirements.txt` 中的 MkDocs 和 Material，更新画集和曲库列表，严格检查并构建网站，然后使用 GitHub 官方 Pages Actions 发布。

首次设置：打开仓库 **Settings → Pages → Build and deployment → Source**，选择 **GitHub Actions**。此工作流直接发布构建产物，无需 `gh-pages` 分支，也无需另外添加访问令牌。若首次构建时尚未设置 Pages，在设置后到 **Actions → Build and deploy website → Run workflow → Run workflow** 手动再运行一次。

`mkdocs.yml` 的 `site_url` 从 `SITE_URL` 环境变量读取，本机未设置时使用预览地址；自动部署时由 Pages 提供真实网站网址，支持仓库名称带来的子目录。

### 以后怎样更新网站

1. 修改 `docs/` 中的文章或素材，保存并用本机预览检查。
2. 在项目文件夹的地址栏输入 `powershell`，按回车，依次运行：

```powershell
git add .
git commit -m "更新网站内容"
git push
```

3. 打开仓库的 **Actions**，等待最新一条工作流出现绿色对勾；通常几分钟后网站即可更新，首次上传素材较多时可能更久。

`site/`、`.venv/`、`__pycache__/`、`output/` 和日志均已排除，自动生成文件与本机备份不会提交。

角色素材与生成提示记录见 [素材说明](scripts/ASSET-NOTES.md)。
