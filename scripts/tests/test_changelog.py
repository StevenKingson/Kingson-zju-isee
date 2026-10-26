import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('changelog', ROOT / 'scripts/update-changelog.py')
log = importlib.util.module_from_spec(spec)
spec.loader.exec_module(log)


class ChangelogIntegrationTests(unittest.TestCase):
    def setUp(self):
        parent = (ROOT / 'output').resolve()
        self.temp = tempfile.TemporaryDirectory(prefix='changelog-test-', dir=parent)
        self.root = Path(self.temp.name).resolve()
        assert self.root.is_relative_to(parent)
        self.addCleanup(self.temp.cleanup)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        self.file = self.root / 'docs/course/year1/test/index.md'
        self.file.parent.mkdir(parents=True)
        self.file.write_text('# 测试课程\n\n原文\n', encoding='utf-8')
        self.changelog = self.root / 'docs/changelog/index.md'
        self.changelog.parent.mkdir()
        self.changelog.write_text('# 更新日志\n\n<div markdown="1">\n\n## 2026-10-22\n\n- 原记录。\n\n</div>\n', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '-qm', 'Initial fixture')

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True)

    def test_content_change_is_logged_once_and_preserves_history(self):
        self.file.write_text('# 测试课程\n\n新内容\n', encoding='utf-8')
        self.assertTrue(log.update(self.root))
        text = self.changelog.read_text(encoding='utf-8')
        self.assertIn('《测试课程》', text)
        self.assertIn('- 原记录。', text)
        self.assertFalse(log.update(self.root))
        self.assertEqual(text, self.changelog.read_text(encoding='utf-8'))

    def test_manual_note_is_not_overwritten(self):
        self.file.write_text('# 测试课程\n\n新内容\n', encoding='utf-8')
        text = self.changelog.read_text(encoding='utf-8') + '\n人工写的详细说明。\n'
        self.changelog.write_text(text, encoding='utf-8')
        self.assertFalse(log.update(self.root))
        self.assertEqual(text, self.changelog.read_text(encoding='utf-8'))

    def test_staged_and_new_pages_are_included(self):
        self.file.write_text('# 测试课程\n\n改动\n', encoding='utf-8')
        self.git('add', '.')
        other = self.root / 'docs/about/index.md'
        other.parent.mkdir(); other.write_text('# 关于\n', encoding='utf-8')
        self.assertTrue(log.update(self.root))
        text = self.changelog.read_text(encoding='utf-8')
        self.assertIn('《测试课程》', text)
        self.assertIn('《关于》', text)

    def test_unrelated_scripts_do_not_create_release_notes(self):
        (self.root / 'helper.py').write_text('pass\n')
        self.assertFalse(log.update(self.root))


if __name__ == '__main__':
    unittest.main()
