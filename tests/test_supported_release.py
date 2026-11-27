"""Single-version offline distribution contract (static; not native model runtime)."""
from pathlib import Path
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]

class SupportedReleaseTests(unittest.TestCase):
    def test_single_release_metadata(self):
        data=json.loads((ROOT/'release.json').read_text(encoding='utf-8'))
        self.assertEqual(data['version'],'0.8.1')
        self.assertEqual(data['status'],'release-candidate')
        self.assertEqual(data['content_review']['status'],'pending')
        self.assertIsNone(data['content_review']['date'])
        self.assertEqual(data['content_review']['version'],'0.8.1')
        self.assertNotIn('edition',data)

    def test_no_obsolete_release_links_or_old_host_dependencies(self):
        files=['README.md','CHANGELOG.md','docs/SETUP.md','docs/VALIDATION.md',
               'docs/INSTALLATION-AND-BEHAVIOR.md','docs/ARCHITECTURE.md',
               'docs/RELEASING.md','docs/PRIVACY.md','docs/PRIVACY-REVIEW.md',
               'content/instructions.txt',
               '.github/skills/advice-from-luminouspeace/SKILL.md']
        for name in files:
            s=(ROOT/name).read_text(encoding='utf-8')
            with self.subTest(file=name):
                self.assertNotRegex(s,r'v0[.]7[.](?:1|2|3|4)(?![0-9])')
                self.assertNotRegex(s,r'v0[.]7(?![.0-9])')
                self.assertNotIn('ask-liviu.',s.lower())
                self.assertNotIn('ask-him.zip',s.lower())
        self.assertNotIn('nineteen', (ROOT/'.github/skills/advice-from-luminouspeace/SKILL.md').read_text(encoding='utf-8').lower())

    def test_supported_attribution(self):
        expected='Influenced by the Advice from LuminousPeace skill — v0.8.1 · prepared 27 November 2026.'
        for name in ['content/instructions.txt','.github/skills/advice-from-luminouspeace/SKILL.md']:
            self.assertIn(expected,(ROOT/name).read_text(encoding='utf-8'))

    def test_only_surviving_source_ids(self):
        s=(ROOT/'sources/book-source-ledger.md').read_text(encoding='utf-8')
        ids=re.findall(r'(?m)^## (S[0-9][0-9]) — ',s)
        self.assertEqual(ids,[f'S{i:02d}' for i in range(1,20) if i not in (14,16)])
        self.assertNotIn('S14',(ROOT/'sources/studies/README.md').read_text(encoding='utf-8'))

if __name__ == '__main__':
    unittest.main()
