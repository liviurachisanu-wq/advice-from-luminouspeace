"""Check that a release draft uses the exact bytes from its verified tag."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import draft_release


class ReleaseCheckoutTests(unittest.TestCase):
    def setUp(self):
        project = tempfile.TemporaryDirectory()
        self.addCleanup(project.cleanup)
        self.root = Path(project.name)
        self.asset = self.root / 'downloads' / 'instructions.txt'
        self.asset.parent.mkdir()
        self.original = b'Instructions from the tagged release.\n'
        self.asset.write_bytes(self.original)
        metadata = {'version': '1.0', 'name': 'Example'}
        (self.root / 'release.json').write_text(json.dumps(metadata), encoding='utf-8')
        (self.root / 'CHANGELOG.md').write_text('## v1.0\nDocumented changes.\n', encoding='utf-8')
        (self.root / '.gitignore').write_text('__pycache__/\n', encoding='utf-8')
        self.git('init', '-q')
        self.git('add', '.')
        self.git('commit', '-qm', 'Release fixture')
        self.git('tag', 'v1.0')

    def git(self, *args):
        subprocess.run(
            ['git', '-c', 'core.autocrlf=false', '-c', 'user.name=Fixture',
             '-c', 'user.email=fixture' + chr(64) + 'example.invalid', *args],
            cwd=self.root, check=True, capture_output=True,
        )

    def test_rejects_worktree_and_index_changes(self):
        self.asset.write_bytes(b'Revised instructions.\n')
        with self.assertRaisesRegex(ValueError, 'clean'):
            draft_release.require_tag_checkout(self.root, 'v1.0')
        self.git('add', '--', 'downloads/instructions.txt')
        self.asset.write_bytes(self.original)
        with self.assertRaisesRegex(ValueError, 'clean'):
            draft_release.require_tag_checkout(self.root, 'v1.0')

    def test_ignored_cache_does_not_block_release(self):
        cache = self.root / '__pycache__'
        cache.mkdir()
        (cache / 'fixture.pyc').write_bytes(b'cache')
        self.assertTrue(draft_release.require_tag_checkout(self.root, 'v1.0'))

    def test_draft_uses_tagged_snapshot_and_notes(self):
        git_run = subprocess.run
        submitted = []

        def record_draft(args, **kwargs):
            if args[0] != 'gh':
                return git_run(args, **kwargs)
            self.assertEqual(args[:6], ['gh', 'release', 'create', 'v1.0', '--verify-tag', '--draft'])
            self.assertEqual(kwargs['input'], b'Documented changes.\n')
            snapshot = Path(args[-1])
            self.assertNotEqual(snapshot, self.asset)
            self.assertEqual(snapshot.name, self.asset.name)
            self.asset.write_bytes(b'Local edit during upload.\n')
            submitted.append(snapshot.read_bytes())
            return subprocess.CompletedProcess(args, 0)

        with patch.object(draft_release, 'release_assets', return_value=[self.asset]):
            with patch.object(subprocess, 'run', side_effect=record_draft):
                draft_release.main(self.root)
        self.assertEqual(submitted, [self.original])

    def test_named_edition_uses_edition_tag_title_and_notes(self):
        metadata = {"name": "Example", "version": "1.0", "edition": {"tag": "v1.0-special.1", "name": "Special"}}
        (self.root / "release.json").write_text(json.dumps(metadata), encoding="utf-8")
        (self.root / "CHANGELOG.md").write_text("## v1.0-special.1\nEdition notes.\n\n## v1.0\nCore notes.\n", encoding="utf-8")
        self.git("add", "release.json", "CHANGELOG.md")
        self.git("commit", "-qm", "Edition fixture")
        self.git("tag", "v1.0-special.1")
        git_run = subprocess.run
        submitted = []

        def capture(args, **kwargs):
            if args[0] != "gh":
                return git_run(args, **kwargs)
            submitted.append((args[3], args[args.index("--title") + 1], kwargs["input"]))
            return subprocess.CompletedProcess(args, 0)

        with patch.object(draft_release, "release_assets", return_value=[self.asset]):
            with patch.object(subprocess, "run", side_effect=capture):
                draft_release.main(self.root)
        self.assertEqual(submitted, [("v1.0-special.1", "Example · Special edition", b"Edition notes.\n")])

    def test_changed_asset_after_preflight_is_rejected(self):
        def select_asset(root):
            self.asset.write_bytes(b'Local edit after preflight.\n')
            return [self.asset]

        with patch.object(draft_release, 'release_assets', side_effect=select_asset):
            with self.assertRaisesRegex(ValueError, 'differs from the tagged file'):
                draft_release.main(self.root)


if __name__ == '__main__':
    unittest.main()
