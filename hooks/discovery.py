"""Build the course finder from the existing navigation, without a second catalogue."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ALIASES = {
    "electronics-training": "电工训 工训", "isee-introduction": "信电导",
    "circuit-design-1": "电设1 电设一 电设Ⅰ", "circuit-design-2": "电设2 电设二 电设Ⅱ",
    "physics-lab": "大物实验", "numerical-analysis": "数分 数值分析",
    "microeconomics": "微经 味精", "digital-systems-lab": "数电实验",
    "electronic-circuits": "电基", "probability-statistics": "概统 概率论",
    "complex-analysis": "复变", "c-programming": "C程 C语言",
}


def nav_pages(items, crumbs=()):
    for item in items:
        if not isinstance(item, dict):
            continue
        for label, target in item.items():
            trail = (*crumbs, label)
            if isinstance(target, list):
                yield from nav_pages(target, trail)
            elif isinstance(target, str) and target.endswith('.md'):
                yield target, trail


def page_url(source):
    return source[:-8] if source.endswith('index.md') else source[:-3] + '/'


def build_catalogue(config):
    docs = Path(config['docs_dir'])
    navigation = list(nav_pages(config['nav']))
    courses = []
    for source, crumbs in navigation:
        file = docs / source
        if not file.is_file():
            continue
        raw = file.read_text(encoding='utf-8')
        match = re.search(r'^#\s+(.+)$', raw, re.MULTILINE)
        title = match.group(1).strip() if match else crumbs[-1]
        parts = Path(source).parts
        if len(parts) == 5 and parts[0] == 'course' and parts[1] in ('year1', 'year2') and parts[-1] == 'index.md':
            folder = file.parent
            downloads = sum(1 for p in folder.rglob('*') if p.suffix.lower() in {'.pdf', '.docx', '.zip', '.pptx', '.xlsx', '.m', '.py'})
            summary = re.search(r'^>\s*\*\*.+?\*\*\s*·\s*(.+)$', raw, re.MULTILINE)
            courses.append({
                'title': title, 'url': page_url(source), 'year': crumbs[1], 'category': crumbs[2],
                'aliases': ALIASES.get(parts[-2], ''),
                'summary': summary.group(1).split('（')[0].strip() if summary else '',
                'reports': page_url(str((folder / 'reports/index.md').relative_to(docs)).replace('\\', '/')) if (folder / 'reports/index.md').is_file() else None,
                'resources': page_url(str((folder / 'resources/index.md').relative_to(docs)).replace('\\', '/')) if (folder / 'resources/index.md').is_file() else None,
                'downloads': downloads,
            })
    return {'courses': courses}


def on_post_build(config, **kwargs):
    target = Path(config['site_dir']) / 'assets/discovery.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_catalogue(config), ensure_ascii=False), encoding='utf-8')
