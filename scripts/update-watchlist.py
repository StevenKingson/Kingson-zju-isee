"""Validate the owner's watchlist and refresh its searchable no-JavaScript text."""
from html import escape
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def update():
    data = json.loads((DOCS / "assets/anime/watchlist.json").read_text(encoding="utf-8"))
    groups = [("正在追 · " + group["season"], group["anime"]) for group in data["watching"]]
    groups += [("打算补", data["planned"]), ("疯狂推", data["recommended"])]
    paragraphs = []
    ids = set()
    for group, entries in groups:
        for anime in entries:
            title = anime["title"]
            if not title or anime["id"] in ids:
                raise ValueError(f"番剧名称为空或 id 重复：{title}")
            ids.add(anime["id"])
            score = anime["score"]
            if score is not None and (type(score) not in (int, float) or not 0 <= score <= 10):
                raise ValueError(f"《{title}》的评分须为 0～10 或 null")
            if not isinstance(anime["completed"], bool):
                raise ValueError(f"《{title}》的 completed 须为 true 或 false")
            if anime["status"] == "已弃坑" and anime["completed"]:
                raise ValueError(f"《{title}》不能同时标记已弃坑和已看完")
            for key in ("cover", "coverOverlay"):
                if key not in anime:
                    continue
                path = (DOCS / anime[key]).resolve()
                if not path.is_relative_to(DOCS.resolve()) or not path.is_file():
                    raise ValueError(f"《{title}》的图片不存在：{anime[key]}")
            status = "已看完" if anime["completed"] else anime["status"]
            text = f"{group}：{title} · {status}"
            if score is not None:
                text += f" · {score}/10"
            if anime["review"]:
                text += "。" + anime["review"]
            paragraphs.append("  <p>" + escape(text) + "</p>")
    paragraphs.append("  <p>请启用浏览器 JavaScript，以查看封面和展开评价。</p>")
    index = DOCS / "acg/diary/index.md"
    source = index.read_text(encoding="utf-8")
    start = source.index("<noscript>") + len("<noscript>")
    end = source.index("</noscript>", start)
    refreshed = source[:start] + "\n" + "\n".join(paragraphs) + "\n" + source[end:]
    if refreshed != source:
        index.write_text(refreshed, encoding="utf-8")
    print(f"追番目录已更新：{len(ids)} 部作品。")


if __name__ == "__main__":
    try:
        update()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f"追番清单检查失败：{error}", file=sys.stderr)
        raise SystemExit(1)
