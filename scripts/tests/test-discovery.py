"""Check discovery against the real website and its navigation."""
import importlib.util
from pathlib import Path
import unittest
from mkdocs.config import load_config

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('discovery', ROOT / 'hooks/discovery.py')
discovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discovery)


class DiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config(str(ROOT / 'mkdocs.yml'))
        cls.data = discovery.build_catalogue(cls.config)

    def test_every_course_is_present_once(self):
        courses = self.data['courses']
        # Calculus I/II and the two swimming levels share one page each.
        self.assertEqual(len(courses), 45)
        self.assertEqual(len({c['url'] for c in courses}), 45)
        self.assertEqual(sum(c['year'] == '大一' for c in courses), 22)
        self.assertEqual(sum(c['year'] == '大二' for c in courses), 23)

    def test_all_course_and_resource_links_exist(self):
        for course in self.data['courses']:
            for key in ['url', 'reports', 'resources']:
                if course[key]:
                    self.assertTrue((ROOT / 'docs' / course[key] / 'index.md').is_file(), course[key])

    def test_new_materials_and_aliases_are_available(self):
        course = next(c for c in self.data['courses'] if 'electronics-training/' in c['url'])
        self.assertIn('电工训', course['aliases'])
        self.assertEqual(course['downloads'], 8)
        self.assertTrue(course['reports'])
        numerical = next(c for c in self.data['courses'] if 'numerical-analysis/' in c['url'])
        self.assertTrue(numerical['resources'])

    def test_catalogue_only_contains_courses(self):
        # Public updates have one home: the manually maintained changelog.
        self.assertEqual(set(self.data), {'courses'})


if __name__ == '__main__':
    unittest.main()
