"""Add a basic release note for owner edits; preserve hand-written release notes."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def changed_paths(root):
    paths = set()
    for arguments in [('diff', '--name-only', '-z', 'HEAD'), ('ls-files', '--others', '--exclude-standard', '-z')]:
        result = subprocess.run(['git', *arguments], cwd=root, capture_output=True, check=True)
        paths.update(p for p in result.stdout.decode('utf-8').split('\0') if p)
    return paths


def titles_for(root, paths):
    titles = []
    for source in sorted(paths):
        file = root / source
        if not file.is_file():
            continue
        candidate = file if file.suffix == '.md' else file.parent / 'index.md'
        if not candidate.is_file():
            candidate = file.parent.parent / 'index.md'
        if not candidate.is_file():
            continue
        match = re.search(r'^#\s+(.+)$', candidate.read_text(encoding='utf-8'), re.MULTILINE)
        if match:
            title = re.sub(r'[<>\[\]`*_]', '', match.group(1)).strip()
            if title and title not in titles:
                titles.append(title)
    return titles


def summaries(root, paths):
    notes = []
    courses = {p for p in paths if p.startswith('docs/course/')}
    if courses:
        titles = titles_for(root, courses)
        detail = '、'.join('《' + t + '》' for t in titles[:4])
        if len(titles) > 4:
            detail += f'等 {len(titles)} 篇内容'
        notes.append('**课程内容**：更新' + (detail or '课程心得与配套资料') + '。')
    if any(p.startswith('docs/assets/anime/') or p.startswith('docs/acg/diary/') for p in paths):
        notes.append('**追番日记**：更新作品清单、评分评价或封面素材。')
    if any(p.startswith('docs/assets/music/') for p in paths):
        notes.append('**BGM**：更新歌单与曲库内容。')
    if any(p.startswith('docs/assets/artbooks/') or p == 'docs/assets/gallery.json' for p in paths):
        notes.append('**画集**：补充或调整画集素材。')
    if any(p.startswith(('docs/javascripts/', 'docs/stylesheets/', 'overrides/')) or p == 'mkdocs.yml' for p in paths):
        notes.append('**网站体验**：调整页面样式、导航或交互功能。')
    other = {p for p in paths if p.startswith('docs/') and p.endswith('.md')
             and not p.startswith(('docs/course/', 'docs/acg/diary/', 'docs/changelog/'))}
    if other:
        titles = titles_for(root, other)
        if titles:
            notes.append('**页面内容**：更新' + '、'.join('《' + t + '》' for t in titles[:4]) + '。')
    return notes


def update(root=ROOT):
    paths = changed_paths(root)
    log = root / 'docs/changelog/index.md'
    if not log.is_file() or 'docs/changelog/index.md' in paths:
        return False  # The owner/agent already supplied a more specific log.
    notes = summaries(root, paths)
    if not notes:
        return False
    source = log.read_text(encoding='utf-8')
    day = datetime.now(timezone(timedelta(hours=8))).date().isoformat()
    heading = f'## {day}\n'
    entry = '\n'.join('- ' + note for note in notes) + '\n\n'
    if heading in source:
        position = source.index(heading) + len(heading)
        source = source[:position] + '\n' + entry + source[position:].lstrip('\n')
    else:
        first_date = re.search(r'^## \d{4}-\d{2}-\d{2}\s*$', source, re.MULTILINE)
        if not first_date:
            raise ValueError('更新日志缺少日期标题，请先保留一个“## 年-月-日”记录。')
        source = source[:first_date.start()] + heading + '\n' + entry + source[first_date.start():]
    log.write_text(source, encoding='utf-8')
    return True


if __name__ == '__main__':
    print('已补充本次内容修改的基本更新日志。' if update() else '更新日志已由人工维护，或没有需要补记的内容。')
