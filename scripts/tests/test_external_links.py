"""Verify all built links without altering code, entities, or internal navigation."""
import importlib.util
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('external_links', ROOT / 'hooks/external_links.py')
links = importlib.util.module_from_spec(spec)
spec.loader.exec_module(links)


class Anchors(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.anchors = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.anchors.append(dict(attrs))


class ExternalLinkTests(unittest.TestCase):
    def test_external_and_internal_links(self):
        text = '''<!doctype html><!-- keep -->
<a href="https://www.cc98.org/topic/1?a=1&amp;b=2" target="_self" rel="nofollow">资源 &amp; 分享</a>
<a href="//example.org/">外站</a><a href="../course/">课程</a>
<a href="#top">顶部</a><a href="mailto:a@example.org">邮件</a>
<a href="https://site.example/about/">关于</a>
<script>if (x < 2 && y > 1) console.log("&amp;");</script>'''
        output = links.on_post_page(text, None, {'site_url': 'https://site.example/'})
        anchors = Anchors(output).anchors
        for anchor in anchors[:2]:
            self.assertEqual(anchor['target'], '_blank')
            self.assertTrue({'noopener', 'noreferrer'} <= set(anchor['rel'].split()))
        self.assertIn('nofollow', anchors[0]['rel'])
        self.assertEqual(anchors[0]['href'], 'https://www.cc98.org/topic/1?a=1&b=2')
        for anchor in anchors[2:]:
            self.assertNotIn('target', anchor)
        self.assertIn('<script>if (x < 2 && y > 1) console.log("&amp;");</script>', output)
        self.assertIn('<!-- keep -->', output)

    def test_idempotent(self):
        text = '<a href="https://outside.example/" rel="noopener">资源</a>'
        config = {'site_url': 'https://site.example/'}
        once = links.on_post_page(text, None, config)
        self.assertEqual(links.on_post_page(once, None, config), once)


if __name__ == '__main__':
    unittest.main()
