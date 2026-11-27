"""Offline distribution contract tests. These do not execute Claude or Copilot models."""
from io import BytesIO
from pathlib import Path
import importlib.util
import json
import re
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("luminous_builder", ROOT/"scripts/build.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class DistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifacts = builder.outputs()
        cls.version = json.loads((ROOT/"release.json").read_text(encoding="utf-8"))["version"]
        cls.references = {
            "references/book-source-ledger.md": ROOT/"sources/book-source-ledger.md",
            "references/reflex-references.md": ROOT/"sources/reflex-references.md",
        }
        cls.references.update({
            "references/studies/"+p.name: p
            for p in sorted((ROOT/"sources/studies").glob("*.md"))
        })

    def test_both_downloadable_skill_zips_have_all_local_evidence(self):
        for platform in ("claude", "copilot"):
            with self.subTest(platform=platform):
                name=f"downloads/advice-from-luminouspeace-{platform}-v{self.version}.zip"
                with zipfile.ZipFile(BytesIO(self.artifacts[name])) as archive:
                    self.assertEqual(archive.testzip(),None)
                    contents=set(archive.namelist())
                    expected={
                        "advice-from-luminouspeace/SKILL.md",
                        *("advice-from-luminouspeace/"+name for name in self.references),
                    }
                    self.assertEqual(contents,expected)
                    self.assertTrue(all(i.compress_type==zipfile.ZIP_STORED for i in archive.infolist()))
                    for rel,src in self.references.items():
                        self.assertEqual(
                            archive.read("advice-from-luminouspeace/"+rel),
                            src.read_bytes(),
                            rel
                        )
                    skill=archive.read("advice-from-luminouspeace/SKILL.md").decode("utf-8")
                    for rel in re.findall(r"\]\((references/[^)]+\.md)\)",skill):
                        self.assertIn("advice-from-luminouspeace/"+rel,contents)
                        self.assertNotIn("..",rel.split("/"))

    def test_copilot_skill_is_portable_outside_source_repo(self):
        root=".github/skills/advice-from-luminouspeace/"
        path=ROOT/root/"SKILL.md"
        text=path.read_text(encoding="utf-8")
        self.assertNotIn("../../../sources/",text)
        self.assertIn("references/book-source-ledger.md",text)
        for rel,src in self.references.items():
            self.assertEqual(self.artifacts[root+rel],src.read_bytes())
            self.assertEqual((ROOT/root/rel).read_bytes(),src.read_bytes())

    def test_retired_material_absent(self):
        self.assertFalse(any('ask-him' in path for path in self.artifacts))
        self.assertNotIn('references/studies/S14-unresolved-title-2026-11-24.md',self.references)
        self.assertFalse(any('/S16-' in name for name in self.references))

    def test_live_acceptance_is_not_misrepresented_as_ci(self):
        runbook=(ROOT/"docs/INSTALLATION-AND-BEHAVIOR.md").read_text(encoding="utf-8")
        self.assertIn("native Copilot acceptance and v0.8 native reruns are pending",runbook)
        self.assertIn("The full protocol and v0.8 native reruns remain pending",runbook)


if __name__ == "__main__":
    unittest.main()
