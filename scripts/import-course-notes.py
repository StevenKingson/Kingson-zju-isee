"""One-time import of the author's course essays and laboratory report collection.

Run with the project virtual environment. Inputs are read only. Website edits after
import should be made in docs/course; rerunning intentionally replaces generated pages.
"""
from __future__ import annotations

import argparse
from collections import OrderedDict
from hashlib import sha256
from html import escape
from pathlib import Path
import json
import re
import shutil
from urllib.parse import quote, unquote, urlsplit
import zipfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
COURSE = DOCS / "course"
AUDIT = {"courses": [], "reports": [], "copied": [], "format_changes": []}

YEAR_CATEGORIES = {
    "year1": [("专业基础课程", "hard"), ("专业必修课程", "major"), ("思政军体类课程", "politics"),
              ("通识选修课程", "general-electives"), ("体育类课程", "sports"), ("外语类课程", "languages")],
    "year2": [("通识必修课程", "general-required"), ("通识选修课程", "general-electives"),
              ("专业基础课程", "foundation"), ("专业必修课程", "major-required"), ("实验课合集", "labs"),
              ("个性修读课程", "personal"), ("体育类课程", "sports")],
}
SLUGS = {
    "year1": ["calculus", "linear-algebra", "c-programming", "engineering-drawing", "physics-1", "ode",
              "electronics-training", "ic-introduction", "military-training", "new-china-history", "ethics-law",
              "situation-policy", "modern-china-history", "biomedical-engineering", "peer-counseling",
              "pre-qin-thought", "sight-singing", "career-planning", "table-tennis", "swimming",
              "english-4", "english-test"],
    "year2": ["military-theory", "marxism", "english-3", "physics-2", "economic-law", "choral-art",
              "complex-analysis", "electronic-circuits", "probability-statistics", "digital-systems", "signals-systems",
              "isee-introduction", "semiconductor-physics", "artificial-intelligence", "cognitive-practice",
              "physics-lab", "circuit-design-1", "circuit-design-2", "digital-systems-lab",
              "numerical-analysis", "microeconomics", "medical-instruments", "swimming"],
}


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def relative_link(path: Path, source: Path):
    import os
    return quote(Path(os.path.relpath(path, source.parent)).as_posix(), safe="/.-_")


def copy_file(source: Path, target: Path):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    AUDIT["copied"].append({"source": str(source), "destination": str(target.relative_to(ROOT)),
                            "sha256": sha256(source.read_bytes()).hexdigest()})


def sections(text: str):
    chunks = []
    for line in text.splitlines():
        if line.startswith("# "):
            chunks.append({"title": line[2:].strip(), "lines": []})
        elif chunks:
            chunks[-1]["lines"].append(line)
    return chunks


def image_sources(text):
    paths = [m.group(1).strip().strip("<>") for m in re.finditer(r"!\[[^\]]*\]\(([^\n]+?)\)", text)]
    paths += re.findall(r'<img\b[^>]*\bsrc=["\x27]([^"\x27]+)', text)
    return paths


def copy_essay_images(text: str, source: Path, target: Path):
    for rel in image_sources(text):
        if urlsplit(rel).scheme:
            continue
        original = source.parent / unquote(rel)
        if not original.is_file():
            raise FileNotFoundError(original)
        copy_file(original, target.parent / unquote(rel))


def format_math(text: str, label: str):
    # Typora accepts $$...$$ inside prose; Arithmatex expects $...$ there.
    output = []
    changed = 0
    in_block = False
    in_code = False
    for line in text.splitlines():
        clean = line.replace("\u200b", "")
        if clean.lstrip().startswith("```"):
            in_code = not in_code
        if in_code:
            output.append(clean)
            continue
        if clean.strip() == "$$":
            if not in_block and output and output[-1].strip():
                output.append("")
            output.append(clean)
            in_block = not in_block
            if not in_block:
                output.append("")
            continue
        one_line = re.fullmatch(r"(\s*)\$\$(.+)\$\$\s*", clean)
        if one_line and not in_block:
            indent, expression = one_line.groups()
            output.extend(["", indent + "$$", indent + expression.strip(), indent + "$$", ""])
            continue
        if "$$" in clean and not in_block:
            clean, count = re.subn(r"\$\$([^$\n]+)\$\$", r"$\1$", clean)
            changed += count
        output.append(clean)
    if changed:
        AUDIT["format_changes"].append({"page": label, "inline_math_delimiters": changed})
    return "\n".join(output)


def import_essay(source: Path, year: str):
    text = source.read_text(encoding="utf-8-sig")
    chunks = sections(text)
    course_chunks = [part for part in chunks if any(line.startswith("## ") for line in part["lines"])]
    categories = OrderedDict()
    entries = []
    for part, (category, category_slug) in zip(course_chunks, YEAR_CATEGORIES[year], strict=True):
        courses = []
        for line in part["lines"]:
            if line.startswith("## "):
                header = line[3:].strip()
                match = re.match(r"(.+?)\s+([\d.]+学分.*)$", header)
                if not match:
                    raise ValueError(f"Unrecognized course header: {header}")
                courses.append({"names": [match[1]], "info": [match[2]], "body": []})
            elif courses:
                courses[-1]["body"].append(line)
        merged = []
        for entry in courses:
            if merged and not "\n".join(merged[-1]["body"]).strip():
                previous = merged[-1]
                previous["names"].extend(entry["names"])
                previous["info"].extend(entry["info"])
                previous["body"] = entry["body"]
            else:
                merged.append(entry)
        categories[category] = {"slug": category_slug, "entries": merged}
        for entry in merged:
            entry.update(category=category, category_slug=category_slug, year=year)
            entries.append(entry)
    for entry, slug in zip(entries, SLUGS[year], strict=True):
        entry["slug"] = slug
        entry["title"] = "、".join(entry["names"]).replace("信息与电子工程/导论", "信息与电子工程导论")
        entry["path"] = COURSE / year / entry["category_slug"] / slug / "index.md"
        entry["reports"] = []
        copy_essay_images("\n".join(entry["body"]), source, entry["path"])
        AUDIT["courses"].append({"year": year, "category": entry["category"], "names": entry["names"],
                                  "page": str(entry["path"].relative_to(DOCS))})

    year_label = "大一" if year == "year1" else "大二"
    full = [f"# {year_label}课程总结 · 合订本", "", f"[按课程浏览](index.md) · [下载原始 Markdown 及配图](original-source.zip)", ""]
    category_index = 0
    for part in chunks[1:]:
        if part["title"] == "目录":
            continue
        title = part["title"]
        if any(line.startswith("## ") for line in part["lines"]):
            title = YEAR_CATEGORIES[year][category_index][0]
            category_index += 1
        full.extend(["## " + title, ""])
        full.extend("#" + line if line.startswith("## ") else line for line in part["lines"])
    overview = COURSE / year / "overview.md"
    write(overview, "\n".join(full))
    copy_essay_images(text, source, overview)
    archive = COURSE / year / "original-source.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(source, source.name)
        for rel in image_sources(text):
            if not urlsplit(rel).scheme:
                z.write(source.parent / rel, rel)

    if year == "year1":
        transfer = next(part for part in chunks if part["title"] == "转专业经验")
        write(COURSE / year / "transfer.md", "# 生医工转微电子 · 转专业经验\n\n" + "\n".join(transfer["lines"]) + "\n\n---\n\n[返回大一课程目录](index.md)")
    return categories, entries


def size_text(size):
    return f"{size / 1024 / 1024:.1f} MB" if size >= 1024 * 1024 else f"{size / 1024:.0f} KB"


def import_report(folder: Path, entry: dict, slug: str, title: str, pdf_name: str | None = None,
                  word_name: str | None = None, project_folder: Path | None = None):
    destination = entry["path"].parent / "reports" / slug
    destination.mkdir(parents=True, exist_ok=True)
    if pdf_name:
        files = [folder / pdf_name]
        if word_name:
            files.append(folder / word_name)
    else:
        files = [p for p in folder.rglob("*") if p.is_file()]
    markdown_files = [p for p in files if p.suffix.lower() == ".md"]
    if len(markdown_files) > 1:
        raise ValueError(f"Too many report texts in {folder}")
    md = markdown_files[0] if markdown_files else None
    for path in files:
        if path != md:
            copy_file(path, destination / path.relative_to(folder))
    downloadable = [p for p in files if p.suffix.lower() in {".pdf", ".docx"}]
    controls = [f"# {title}", "", f"[← {entry['title']} · 课程心得](../../index.md) · [全部实验报告](../index.md)", ""]
    controls += [f"- [{'在线打开 PDF' if p.suffix.lower() == '.pdf' else '下载 Word 原稿'}（{size_text(p.stat().st_size)}）]({quote(p.relative_to(folder).as_posix())})" for p in downloadable]
    for pdf in (p for p in downloadable if p.suffix.lower() == '.pdf'):
        pdf_url = escape(quote(pdf.relative_to(folder).as_posix()), quote=True)
        controls.extend(["", f'<details class="report-pdf" data-pdf="{pdf_url}">',
                         '<summary>展开 PDF 预览</summary>', '</details>', ""])
    source_files = [p for p in files if p.suffix.lower() not in {".pdf", ".docx"}]
    if project_folder:
        source_files += [p for p in project_folder.rglob("*") if p.is_file() and "out" not in p.relative_to(project_folder).parts]
    if source_files:
        with zipfile.ZipFile(destination / "source.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for p in source_files:
                relative = p.relative_to(project_folder) if project_folder and p.is_relative_to(project_folder) else p.relative_to(folder)
                z.write(p, relative)
        controls.append("- [下载可编辑源文件与配套图片、脚本](source.zip)")
    py_files = [p for p in files if p.suffix.lower() == ".py"]
    if py_files:
        controls.extend(["", "<details markdown=\"1\"><summary>数据处理脚本</summary>", ""])
        controls += [f"- [{p.name}]({quote(p.relative_to(folder).as_posix())})" for p in py_files]
        controls.extend(["", "</details>"])
    controls.extend(["", "---", ""])
    if md:
        body = md.read_text(encoding="utf-8-sig")
        controls.append(format_math(body, str((destination / 'index.md').relative_to(DOCS))))
    else:
        controls.append("这份报告保留原有文档版式，可点击上方链接在浏览器中打开 PDF，或下载已有的可编辑原稿。")
    write(destination / "index.md", "\n".join(controls))
    report = {"title": title, "path": destination / "index.md", "online": bool(md),
              "pdf": len([p for p in downloadable if p.suffix.lower() == '.pdf']),
              "word": len([p for p in downloadable if p.suffix.lower() == '.docx'])}
    entry["reports"].append(report)
    AUDIT["reports"].append({**{k: v for k, v in report.items() if k != "path"},
                              "course": entry["title"], "page": str(report["path"].relative_to(DOCS))})


def report_links(entry, source):
    return "\n".join(f"- [{report['title']}]({relative_link(report['path'], source)}) · {'在线正文 / PDF' if report['online'] else 'PDF'}" for report in entry["reports"])


def render_course(entry):
    path = entry["path"]
    year = "大一" if entry["year"] == "year1" else "大二"
    lines = [f"# {entry['title']}", "", f"[{year}课程](../../index.md) / {entry['category']}", ""]
    for name, info in zip(entry["names"], entry["info"]):
        lines.extend([f"> **{name}** · {info}", ""])
    if len(entry["names"]) > 1:
        lines.extend(["原文将以上两门课程放在一起讲解，以下保留合并心得。", ""])
    if entry["reports"]:
        lines.extend(["## 实验报告", "", report_links(entry, path), "", "## 课程心得", ""])
    if entry["category_slug"] == "personal":
        group = "本专业进阶模块" if entry["slug"] == "numerical-analysis" else "跨专业课程"
        lines.extend([f"**修读分类：{group}**", ""])
    lines.append("\n".join(entry["body"]).strip())
    if entry["reports"]:
        report_index = path.parent / "reports" / "index.md"
        write(report_index, f"# {entry['title']} · 实验报告\n\n[← 返回课程心得](../index.md)\n\n" + report_links(entry, report_index))
    write(path, "\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freshman", type=Path, required=True)
    parser.add_argument("--sophomore", type=Path, required=True)
    parser.add_argument("--reports-root", type=Path, required=True)
    args = parser.parse_args()
    year_data = {}
    all_entries = []
    for year, source in [("year1", args.freshman), ("year2", args.sophomore)]:
        categories, entries = import_essay(source, year)
        year_data[year] = categories
        all_entries += entries
    lookup = {entry["slug"]: entry for entry in all_entries if entry["year"] == "year2"}
    root = args.reports_root
    physics = [
        ("动态法测量材料杨氏模量", "dynamic-young", "动态法测量材料杨氏模量"),
        ("金属材料杨氏模量测量", "metal-young", "金属材料杨氏模量测量"),
        ("示波器实验报告", "oscilloscope", "示波器的使用"),
        ("分光计实验报告", "spectrometer", "分光计的调整和使用"),
        ("交流电路功率因数实验、组装整流器", "power-factor-rectifier", "交流电路功率因数实验、组装整流器"),
        ("铁磁材料的磁滞回线和基本磁化曲线", "hysteresis", "铁磁材料的磁滞回线和基本磁化曲线"),
        ("双棱镜干涉", "biprism", "双棱镜干涉"), ("光的偏振应用研究", "polarization", "光的偏振应用研究"),
        ("等厚干涉", "equal-thickness", "等厚干涉"),
        ("光电效应测量普朗克常量", "photoelectric", "光电效应测量普朗克常量"),
        ("用双臂电桥测低电阻", "kelvin-bridge", "用双臂电桥测低电阻"),
        ("万用表的设计", "multimeter", "万用表的设计"),
        ("惠斯登电桥", "wheatstone", "惠斯登电桥"), ("非平衡电桥", "unbalanced-bridge", "非平衡电桥"),
    ]
    for folder, slug, title in physics:
        import_report(root / "大物实验报告分享" / folder, lookup["physics-lab"], slug, title)
    for i, title in enumerate(["基于 MATLAB 的信号频谱分析", "基于 Simulink 的信号调制仿真", "基于 Multisim 的三极管放大电路仿真"], 1):
        import_report(root / "信电导实验报告分享", lookup["isee-introduction"], f"experiment-{i}", f"实验 {i} · {title}", f"实验{i}.pdf")
    circuits = [("1", "电路定律验证实验"), ("2", "一阶 RC 电路的瞬态响应过程实验研究"),
                ("3", "OrCAD 软件练习"), ("4、5", "晶体管共射放大电路设计、仿真与测试"),
                ("6", "集成运算放大器应用电路研究（Ⅰ）"), ("7", "集成运算放大器应用电路研究（Ⅱ）")]
    for number, title in circuits:
        word = f"实验{'5' if number == '4、5' else number}.docx"
        import_report(root / "电设1实验报告分享", lookup["circuit-design-1"], "experiment-" + number.replace("、", "-"),
                      f"实验 {number} · {title}", f"实验{number}.pdf", word)
    import_report(root / "电设2实验报告分享", lookup["circuit-design-2"], "current-voltage", "电流–电压转换电路实验研究",
                  "电流-电压转换电路实验报告.pdf", "电流-电压转换电路实验报告.docx")
    import_report(root / "数电实验报告分享", lookup["digital-systems-lab"], "lab-5", "Lab 5 · 常用组合电路模块的设计和应用",
                  "Lab5实验报告.pdf", "Lab5实验报告.docx")
    import_report(root / "数电实验报告分享", lookup["digital-systems-lab"], "lab-19", "Lab 19 · 音乐播放实验",
                  "Lab19实验报告.pdf", project_folder=root / "数电实验报告分享" / "报告")
    for entry in all_entries:
        render_course(entry)

    nav = [{"课程总览": "course/index.md"}]
    year_counts = {}
    for year, categories in year_data.items():
        year_label = "大一" if year == "year1" else "大二"
        count = sum(len(entry["names"]) for cat in categories.values() for entry in cat["entries"])
        year_counts[year] = count
        year_index = COURSE / year / "index.md"
        year_lines = [f"# {year_label}课程", "", f"{count} 门课程，沿用原总结中的分类与顺序。", "",
                      "[阅读课程总结合订本](overview.md) · [下载原始 Markdown 及配图](original-source.zip)", ""]
        year_nav = [{"学年总览": str(year_index.relative_to(DOCS)).replace('\\', '/')},
                    {"课程总结合订本": f"course/{year}/overview.md"}]
        for category, data in categories.items():
            category_index = COURSE / year / data["slug"] / "index.md"
            category_lines = [f"# {category}", "", f"[{year_label}课程](../index.md)", ""]
            category_nav = []
            year_lines.extend(["## " + category, ""])
            last_group = None
            for entry in data["entries"]:
                if data["slug"] == "personal":
                    group = "本专业进阶模块" if entry["slug"] == "numerical-analysis" else "跨专业课程"
                    if last_group != group:
                        year_lines.extend(["### " + group, ""])
                        category_lines.extend(["## " + group, ""])
                        category_nav.append({group: []})
                        last_group = group
                badge = f" · {len(entry['reports'])} 份实验报告" if entry["reports"] else ""
                year_lines.append(f"- [{entry['title']}]({relative_link(entry['path'], year_index)}){badge}")
                category_lines.extend([f"- [{entry['title']}]({relative_link(entry['path'], category_index)}){badge}",
                                       f"  - {'；'.join(entry['info'])}"])
                path = entry["path"].relative_to(DOCS).as_posix()
                if entry["reports"]:
                    child = [{"课程心得": path}, {"报告目录": entry['path'].parent.relative_to(DOCS).as_posix() + "/reports/index.md"}]
                    child += [{r["title"]: r["path"].relative_to(DOCS).as_posix()} for r in entry["reports"]]
                    node = {entry["title"]: child}
                else:
                    node = {entry["title"]: path}
                if data["slug"] == "personal":
                    category_nav[-1][group].append(node)
                else:
                    category_nav.append(node)
            year_lines.append("")
            year_nav.append({category: category_nav})
        if year == "year1":
            year_lines.extend(["## 转专业经验", "", "[生医工转微电子 · 转专业经验](transfer.md)"])
            year_nav.append({"转专业经验": "course/year1/transfer.md"})
        write(year_index, "\n".join(year_lines))
        nav.append({year_label: year_nav})
    yml_path = ROOT / "mkdocs.yml"
    yml = yml_path.read_text(encoding="utf-8")
    # Keep !ENV and existing theme settings intact; change only the navigation block.
    full_nav = [{"主页": "index.md"}, {"课程": nav}, {"ACG宝库": [
        {"宝库首页": "acg/index.md"}, {"KING桑の追番日记": "acg/diary/index.md"}, {"快来看轻音少女美图": "acg/gallery/index.md"}]},
        {"友链": "friends/index.md"}, {"关于": "about/index.md"}, {"留言板": "guestbook/index.md"}]
    navigation = yaml.safe_dump({"nav": full_nav}, allow_unicode=True, sort_keys=False, width=120)
    yml = re.sub(r"(?ms)^nav:\n.*?(?=^extra_css:)", navigation + "\n", yml)
    write(yml_path, yml)
    report_count = len(AUDIT["reports"])
    write(COURSE / "index.md", f'''---
hide:
  - toc
---

# 课程

从大一到大二，记录上课的体验、选课时的犹豫，以及期末之后的复盘。

共整理 **{sum(year_counts.values())} 门课程心得**、**{report_count} 份实验报告**。课程分类沿用原文，图片、公式和配套资料随课程一起归档。

<div class="acg-cards">
  <a class="acg-card" href="year1/">
    <span class="acg-card-label">FRESHMAN YEAR · 01</span>
    <strong>大一课程与转专业经验</strong>
    <span>{year_counts['year1']} 门课程 · 专业基础、专业必修、思政军体、通识选修、体育、外语。</span>
    <span class="acg-card-arrow">从这里开始 →</span>
  </a>
  <a class="acg-card" href="year2/">
    <span class="acg-card-label">SOPHOMORE YEAR · 02</span>
    <strong>大二课程与实验报告</strong>
    <span>{year_counts['year2']} 门课程 · 通识、专业基础、专业必修、实验课、个性修读与体育。</span>
    <span class="acg-card-arrow">翻开这一年 →</span>
  </a>
</div>

## 实验报告快捷入口

| 所属课程 | 报告数量 | 入口 |
| --- | --- | --- |
| 信息与电子工程导论 | 3 | [信电导实验报告](year2/major-required/isee-introduction/reports/index.md) |
| 大学物理实验 | 14 | [大物实验报告](year2/labs/physics-lab/reports/index.md) |
| 电子电路设计实验Ⅰ | 6（含实验 4、5 合并报告） | [电设Ⅰ实验报告](year2/labs/circuit-design-1/reports/index.md) |
| 电子电路设计实验Ⅱ | 1 | [电设Ⅱ实验报告](year2/labs/circuit-design-2/reports/index.md) |
| 数字系统设计实验 | 2 | [数电实验报告](year2/labs/digital-systems-lab/reports/index.md) |

''')
    AUDIT["summary"] = {"course_count": sum(year_counts.values()), "course_pages": len(all_entries), "report_count": report_count,
                          "online_reports": sum(r["online"] for r in AUDIT["reports"]),
                          "pdf_count": sum(r["pdf"] for r in AUDIT["reports"]), "word_count": sum(r["word"] for r in AUDIT["reports"])}
    audit_path = ROOT / "output" / "course-import-audit.json"
    write(audit_path, json.dumps(AUDIT, ensure_ascii=False, indent=2))
    print(json.dumps(AUDIT["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
