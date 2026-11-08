from pathlib import Path
from io import BytesIO
from html.parser import HTMLParser
import hashlib,importlib.util,json,re,unittest,zipfile,sys,tempfile
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
    def setUpClass(cls):cls.out=builder.outputs();cls.meta=json.loads((ROOT/'release.json').read_text())
    def test_generated_files_are_current(self):
        for name,payload in self.out.items():self.assertEqual((ROOT/name).read_bytes(),payload,name)
    def test_platform_parity_and_limit(self):
        self.assertEqual(self.out['downloads/portable-instructions.txt'],self.out['downloads/chatgpt-project-instructions.txt'])
        self.assertEqual(self.out['downloads/portable-instructions.txt'],self.out['downloads/gemini-gem-instructions.txt'])
        self.assertLessEqual(len(self.out['downloads/copilot-agent-instructions.txt'].decode().encode('utf-16-le'))//2,8000)
    def test_native_zip_layout_and_references(self):
        name=f"downloads/advice-from-luminouspeace-claude-v{self.meta['version']}.zip"
        with zipfile.ZipFile(BytesIO(self.out[name])) as z:
            self.assertEqual(len(z.namelist()),3)
            self.assertTrue(all(info.create_system == 3 for info in z.infolist()))
            for n in z.namelist():self.assertTrue(n.startswith('advice-from-luminouspeace/'));self.assertNotIn('..',n)
            skill=z.read('advice-from-luminouspeace/SKILL.md').decode()
            self.assertTrue(skill.startswith('---\nname: advice-from-luminouspeace\n'))
            self.assertIn(self.out['downloads/portable-instructions.txt'].decode().strip(),skill)
            for ref in re.findall(r'references/[a-z-]+\.md',skill):self.assertIn('advice-from-luminouspeace/'+ref,z.namelist())
    def test_release_metadata_and_attribution(self):
        for key in ['downloads/portable-instructions.txt','downloads/copilot-agent-instructions.txt']:
            text=self.out[key].decode();self.assertIn(self.meta['footnote'],text);self.assertIn('listening or space',text)
            for n in range(1,20):self.assertRegex(text,rf'\bS{n:02d}\b')
        self.assertEqual(self.meta['content_review']['status'],'approved')
        self.assertEqual(self.meta['status'],'privacy-hardened-preview')
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
    def test_release_rejects_unexpected_downloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'downloads').mkdir()
            (root/'downloads'/'unexpected.txt').write_text('synthetic')
            with mock.patch.object(releaser,'outputs',return_value={'downloads/expected.txt':b'synthetic'}):
                with self.assertRaisesRegex(ValueError,'only the generated'):releaser.release_assets(root)
    def test_source_coverage(self):
        ledger=(ROOT/'sources/book-source-ledger.md').read_text(encoding='utf-8')
        self.assertEqual(len(re.findall(r'^## S\d\d ',ledger,re.M)),19)
        self.assertIn('0 complete books',ledger)
    def test_landing_links(self):
        page=self.out['index.html'].decode();parser=Links();parser.feed(page)
        for link in parser.links:
            if not link.startswith(('https:','#')):self.assertTrue((ROOT/link).exists(),link)
        self.assertNotRegex(page,r'<script[^>]+src=|fetch\(|XMLHttpRequest')
    def test_checksums_and_reproducibility(self):
        for line in self.out['downloads/SHA256SUMS.txt'].decode().splitlines():
            digest,name=line.split('  ',1);self.assertEqual(digest,hashlib.sha256(self.out['downloads/'+name]).hexdigest())
        self.assertEqual(self.out,builder.outputs())

if __name__=='__main__':unittest.main()
