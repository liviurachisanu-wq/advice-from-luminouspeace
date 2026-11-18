"""Check the landing page's content policy against the bytes a browser parses."""

import base64
import hashlib
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build import outputs


class PageSource(HTMLParser):
    def __init__(self):
        super().__init__()
        self.policy = {}
        self.blocks = {}
        self.block = None
        self.executable_attributes = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.executable_attributes.extend(key for key in attrs if key.startswith('on'))
        if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'content-security-policy':
            for directive in attrs['content'].split(';'):
                name, *sources = directive.split()
                self.policy[name] = sources
        elif tag in ('script', 'style', 'pre'):
            self.block = attrs.get('id', tag)
            self.blocks.setdefault(self.block, []).append('')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'pre'):
            self.block = None

    def handle_data(self, data):
        if self.block:
            self.blocks[self.block][-1] += data


class LandingPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = outputs()
        cls.page = PageSource()
        cls.page.feed(cls.files['index.html'].decode('utf-8'))
        cls.page.close()

    def test_policy_allows_only_the_shipped_script_and_stylesheet(self):
        for tag in ('script', 'style'):
            with self.subTest(tag=tag):
                [source] = self.page.blocks[tag]
                digest = hashlib.sha256(source.encode('utf-8')).digest()
                expected = "'sha256-" + base64.b64encode(digest).decode('ascii') + "'"
                self.assertEqual(self.page.policy[tag + '-src'], [expected])
        for directive in ('default-src', 'base-uri', 'form-action'):
            self.assertEqual(self.page.policy[directive], ["'none'"])
        self.assertEqual(self.page.executable_attributes, [])

    def test_clipboard_sources_match_downloads_including_final_newline(self):
        for kind, filename in [('portable', 'portable-instructions.txt'), ('copilot', 'copilot-agent-instructions.txt')]:
            with self.subTest(kind=kind):
                [source] = self.page.blocks['text-' + kind]
                self.assertEqual(source.encode('utf-8'), self.files['downloads/' + filename])


if __name__ == '__main__':
    unittest.main()
