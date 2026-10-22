"""Render the owner's Markdown guide as a standalone, offline HTML document."""
from pathlib import Path
import markdown
from markdown.extensions.toc import slugify_unicode

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "网站操作指南.md"
renderer = markdown.Markdown(extensions=["extra", "toc", "sane_lists"],
    extension_configs={"toc": {"slugify": slugify_unicode, "toc_depth": "2-2"}})
content = renderer.convert(source.read_text(encoding="utf-8"))
template = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>KING桑的网站操作指南</title>
<style>
:root{color-scheme:light;--accent:#a65387;--ink:#302a34;--muted:#726976;--line:#e9dfe7}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#faf8fb;color:var(--ink);font:16px/1.85 "Microsoft YaHei",system-ui,sans-serif}
header{padding:34px max(24px,calc((100% - 1200px)/2));border-bottom:1px solid var(--line);background:white}
header strong{font-size:23px}header p{margin:6px 0 0;color:var(--muted)}
.layout{max-width:1250px;margin:auto;display:grid;grid-template-columns:245px minmax(0,1fr);gap:30px;padding:30px 24px 70px}
nav{position:sticky;top:20px;align-self:start;max-height:calc(100vh - 40px);overflow:auto;font-size:14px;padding:12px;background:white;border:1px solid var(--line);border-radius:14px}
nav ul{padding-left:22px}nav a{text-decoration:none}main{min-width:0;background:white;border:1px solid var(--line);border-radius:18px;padding:26px 38px}
h1{font-size:30px;margin-top:0}h2{font-size:24px;margin-top:2.2em;padding-bottom:8px;border-bottom:1px solid var(--line);scroll-margin-top:25px}h3{font-size:19px;margin-top:1.8em}
a{color:var(--accent);overflow-wrap:anywhere}code{font-family:Consolas,"Microsoft YaHei",monospace;background:#f5eff5;border-radius:4px;padding:2px 5px;font-size:.9em;overflow-wrap:anywhere}
pre{overflow:auto;padding:18px;background:#f7f4f8;border:1px solid var(--line);border-radius:10px;line-height:1.6}pre code{background:none;padding:0;overflow-wrap:normal}
table{border-collapse:collapse;width:100%;font-size:14px;display:block;overflow:auto}th,td{border:1px solid var(--line);text-align:left;vertical-align:top;padding:10px 12px}th{background:#f7f1f6}
blockquote{margin:20px 0;padding:12px 18px;border-left:4px solid #c68ab1;background:#fbf5fa}blockquote p{margin:0}li{margin:6px 0}hr{border:0;border-top:1px solid var(--line);margin:35px 0}
@media(max-width:850px){.layout{display:block;padding:20px 14px}nav{position:static;max-height:none;margin-bottom:20px}main{padding:24px 20px}h1{font-size:26px}}
@media print{body{background:white}header,nav{display:none}.layout{display:block;padding:0}main{border:0;padding:0}pre{white-space:pre-wrap}h2,h3{break-after:avoid}a{color:inherit}}
</style></head><body>
<header><strong>☕ KING桑の放课后茶会 · 站长手册</strong><p>修改内容 → 本机预览 → 双击上传 → 等待网站更新</p></header>
<div class="layout"><nav aria-label="操作指南目录">__TOC__</nav><main>__CONTENT__</main></div>
</body></html>
"""
html = template.replace("__TOC__", renderer.toc).replace("__CONTENT__", content)
(ROOT / "网站操作指南.html").write_text(html, encoding="utf-8")
print("操作指南已更新：网站操作指南.html")
