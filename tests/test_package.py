from pathlib import Path
from io import BytesIO
from html.parser import HTMLParser
import hashlib,importlib.util,json,re,subprocess,unittest,zipfile,sys,tempfile
from urllib.parse import unquote, urlsplit
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import privacy_guard as guard
import draft_release as releaser
spec=importlib.util.spec_from_file_location('builder',ROOT/'scripts/build.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.links.extend(v for k,v in attrs if k=='href')

class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.out=builder.outputs();cls.meta=json.loads((ROOT/'release.json').read_text(encoding='utf-8'))
    def test_generated_files_are_current(self):
        builder.check_generated(ROOT, self.out)
    def test_platform_parity_and_limit(self):
        self.assertEqual(self.out['downloads/portable-instructions.txt'],self.out['downloads/chatgpt-project-instructions.txt'])
        self.assertEqual(self.out['downloads/portable-instructions.txt'],self.out['downloads/gemini-gem-instructions.txt'])
        self.assertLessEqual(len(self.out['downloads/copilot-agent-instructions.txt'].decode().encode('utf-16-le'))//2,8000)
    def test_offline_native_zip_layout_and_references(self):
        name=f"downloads/advice-from-luminouspeace-claude-v{self.meta['version']}.zip"
        with zipfile.ZipFile(BytesIO(self.out[name])) as z:
            study_count = len(list((ROOT/'sources/studies').glob('*.md')))
            self.assertEqual(len(z.namelist()),3 + study_count)
            self.assertTrue(all(info.create_system == 3 for info in z.infolist()))
            self.assertTrue(all(info.compress_type == zipfile.ZIP_STORED for info in z.infolist()))
            for n in z.namelist():self.assertTrue(n.startswith('advice-from-luminouspeace/'));self.assertNotIn('..',n)
            skill=z.read('advice-from-luminouspeace/SKILL.md').decode()
            self.assertTrue(skill.startswith('---\nname: advice-from-luminouspeace\n'))
            self.assertIn(self.out['downloads/portable-instructions.txt'].decode().strip(),skill)
            for ref in re.findall(r'references/[a-z-]+\.md',skill):self.assertIn('advice-from-luminouspeace/'+ref,z.namelist())
            for original in sorted((ROOT/'sources/studies').glob('*.md')):
                self.assertEqual(z.read('advice-from-luminouspeace/references/studies/'+original.name),
                                 original.read_bytes())
    def test_release_metadata_and_attribution(self):
        for key in ['downloads/portable-instructions.txt','downloads/copilot-agent-instructions.txt']:
            text=self.out[key].decode();self.assertIn(self.meta['footnote'],text.splitlines());self.assertIn('listening or space',text)
            for n in range(1,8):self.assertRegex(text,rf'\bS{n:02d}\b')
            for n in range(8,14):self.assertIn(f'S{n:02d}',text)
            self.assertNotIn('S14',text)
        review = self.meta['content_review']
        self.assertEqual(review['version'], self.meta['version'])
        if self.meta['status'] == 'release-candidate':
            self.assertEqual(review['status'], 'pending')
            self.assertIsNone(review['date'])
        else:
            self.assertEqual(review['status'], 'approved')
            self.assertTrue(review['date'])
    def test_single_behavioral_source_and_compact_adapter(self):
        core=(ROOT/'content/instructions.txt').read_text(encoding='utf-8').rstrip()+'\n'
        portable=self.out['downloads/portable-instructions.txt'].decode()
        ms=self.out['downloads/copilot-agent-instructions.txt'].decode()
        self.assertEqual(portable,core)
        self.assertEqual(ms.split('\n',1)[1].split('\n\nMICROSOFT 365 COPILOT ADAPTER',1)[0].strip(),
                         core.split('\n',1)[1].strip())
        self.assertLessEqual(len(ms.encode('utf-16-le'))//2,7600)

    def test_both_instruction_variants_include_all_reflexes(self):
        for name in ('portable-instructions.txt', 'copilot-agent-instructions.txt'):
            text = self.out[f'downloads/{name}'].decode()
            self.assertRegex(text, r'(?m)^OPTIONAL BOOK-INSPIRED REFLEXES$')
            self.assertEqual(re.findall(r'(?m)^R([1-7])\s', text), list('1234567'))
    def test_recent_books_do_not_create_extra_reflexes(self):
        full = self.out['downloads/portable-instructions.txt'].decode()
        compact = self.out['downloads/copilot-agent-instructions.txt'].decode()
        ledger = (ROOT / 'sources/book-source-ledger.md').read_text(encoding='utf-8')
        for source in (full, compact):
            for needle in ('S08', 'S09', 'S10', 'friction'):
                self.assertIn(needle, source)
            self.assertNotRegex(source, r'(?m)^R(?:8|9|10)(?:\\s|\\b)')
        for source_id in ('S08', 'S09', 'S10'):
            self.assertIn('Conversation-study addendum', ledger.split('## ' + source_id, 1)[1].split('\\n## ', 1)[0])

    def test_obsolete_service_and_source_removed(self):
        core=self.out['downloads/portable-instructions.txt'].decode()
        self.assertNotIn('S14',core)
        self.assertFalse(any('ask-him' in name for name in self.out))
        self.assertNotIn('edition', self.meta)

    def test_release_assets_match_generated_downloads(self):
        assets = releaser.release_assets(ROOT)
        self.assertEqual({path.name for path in assets}, {
            Path(name).name for name in self.out if name.startswith('downloads/')
        })
    def test_public_identity_and_no_private_artifacts(self):
        guard.scan_repository(ROOT)
    def test_privacy_guard_rejects_contacts_in_nested_archives(self):
        contact=('sample' + '@' + 'example.invalid').encode()
        inner=BytesIO()
        with zipfile.ZipFile(inner,'w') as z:z.writestr('notes.txt',contact)
        outer=BytesIO()
        with zipfile.ZipFile(outer,'w') as z:z.writestr('inner.zip',inner.getvalue())
        with self.assertRaisesRegex(ValueError,'email address'):guard.scan_payload('outer.zip',outer.getvalue())
    def test_privacy_guard_rejects_unsafe_or_unreviewed_exports(self):
        samples=[('../notes.txt',b'synthetic'),('report.pdf',b'synthetic'),('notes.txt',('libfile_'+'a'*32).encode()),('notes.txt',('ghp_'+'x'*32).encode())]
        for name,payload in samples:
            with self.subTest(name=name):
                with self.assertRaises(ValueError):guard.scan_payload(name,payload)
    def test_stale_zip_is_rejected_by_release_and_build_check(self):
        name = 'downloads/old.zip'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'downloads').mkdir()
            (root / name).write_bytes(b'stale')
            expected = {}
            with self.assertRaisesRegex(ValueError, r'Unexpected generated files: downloads/old[.]zip'):
                builder.check_generated(root, expected)
            with mock.patch.object(releaser, 'outputs', return_value=expected):
                with self.assertRaisesRegex(ValueError, r'Unexpected generated files: downloads/old[.]zip'):
                    releaser.release_assets(root)

    def test_unexpected_native_skill_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'skills/advice-from-luminouspeace/references').mkdir(parents=True)
            (root / 'skills/advice-from-luminouspeace/references/stale.md').touch()
            with self.assertRaisesRegex(ValueError, 'Unexpected generated files'):
                builder.check_generated(root, {})

    def test_release_requires_checkout_of_tagged_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def git(*args):
                subprocess.run(
                    ['git', '-c', 'user.name=Release Test',
                     '-c', 'user.email=release-test' + chr(64) + 'example.invalid', *args],
                    cwd=root, capture_output=True, check=True,
                )

            git('init', '-q')
            git('commit', '-q', '--allow-empty', '-m', 'tagged')
            git('tag', '-a', 'v1.0', '-m', 'release')
            releaser.require_tag_checkout(root, 'v1.0')
            with self.assertRaisesRegex(ValueError, 'Cannot resolve release commit'):
                releaser.require_tag_checkout(root, 'v1.1')
            git('commit', '-q', '--allow-empty', '-m', 'different checkout')
            with self.assertRaisesRegex(ValueError, 'HEAD must match'):
                releaser.require_tag_checkout(root, 'v1.0')

    def test_release_notes_include_only_matching_version(self):
        changelog = '# Changelog\n\n## v1.00 — Later\n\nLater.\n\n## v1.0 — Patch\n\nPatch.\n\n## v0.7 — Earlier\n\nEarlier.\n'
        self.assertEqual(releaser.release_notes(changelog, 'v1.0'), 'Patch.\n')
        with self.assertRaisesRegex(ValueError, 'Expected one changelog section'):
            releaser.release_notes(changelog, 'v1.1')

    def test_both_variants_include_safety_and_attribution_exceptions(self):
        safety_rules = []
        for name in ('portable-instructions.txt', 'copilot-agent-instructions.txt'):
            text = self.out[f'downloads/{name}'].decode()
            rule = re.search(r'(?m)^IMMEDIATE SAFETY\n(.+)$', text)[1]
            safety_rules.append(rule)
            self.assertIn('credible immediate danger', rule)
            self.assertIn('Give a specific emergency number only for an established location.', rule)
            self.assertIn('Language alone is insufficient.', rule)
            self.assertIn("Use the user's language, including any introductory disclosure.", text)
            self.assertIn('Keep the version footer verbatim.', text)
            self.assertIn('Skip the support menu, persona, book reflexes, and attribution', rule)
            self.assertIn('Omit it for crisis responses, listening-only replies, and routine answers.', text)
            self.assertIn('Keep it outside drafts, code, and other requested artifacts.', text)
        self.assertEqual(*safety_rules)

    def test_readme_and_setup_local_links(self):
        for name in ('README.md', 'docs/SETUP.md'):
            path = ROOT / name
            text = path.read_text(encoding='utf-8')
            for target in re.findall(r'\]\(([^()\s]+)\)', text):
                link = urlsplit(target)
                if not link.scheme and not link.netloc and link.path:
                    self.assertTrue((path.parent / unquote(link.path)).exists(), (name, target))
        setup = (ROOT / 'docs/SETUP.md').read_text(encoding='utf-8')
        self.assertIn(f'advice-from-luminouspeace-claude-v{self.meta["version"]}.zip', setup)
    def test_source_coverage(self):
        ledger=(ROOT/'sources/book-source-ledger.md').read_text(encoding='utf-8')
        self.assertEqual(len(re.findall(r'^## S\d\d ',ledger,re.M)),18)
        self.assertNotRegex(ledger,r'(?m)^## S14\b')
        self.assertIn('0 complete books',ledger)
    def test_landing_links(self):
        page=self.out['index.html'].decode();parser=Links();parser.feed(page)
        self.assertEqual(parser.links[0], 'downloads/chatgpt-project-instructions.txt')
        for link in parser.links:
            if not link.startswith(('https:','#')):self.assertTrue((ROOT/link).exists(),link)
        self.assertNotRegex(page,r'<script[^>]+src=|fetch\(|XMLHttpRequest')
    def test_checksums_and_reproducibility(self):
        checksum_names = {row.split('  ', 1)[1] for row in self.out['downloads/SHA256SUMS.txt'].decode().splitlines()}
        self.assertEqual(checksum_names, {Path(name).name for name in self.out if name.startswith('downloads/') and not name.endswith(('SHA256SUMS.txt',))})
        for line in self.out['downloads/SHA256SUMS.txt'].decode().splitlines():
            digest,name=line.split('  ',1);self.assertEqual(digest,hashlib.sha256(self.out['downloads/'+name]).hexdigest())
        self.assertEqual(self.out,builder.outputs())

if __name__=='__main__':unittest.main()
