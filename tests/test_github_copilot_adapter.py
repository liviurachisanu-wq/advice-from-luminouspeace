"""Static checks for additive GitHub Copilot integration, not live validation."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GitHubCopilotAdapterTests(unittest.TestCase):
    def test_conditional_skill_and_limit(self):
        text = (ROOT / ".github/skills/advice-from-luminouspeace/SKILL.md").read_text("utf-8")
        self.assertTrue(text.startswith("---\nname: advice-from-luminouspeace\n"))
        self.assertIn("Do not activate for unrelated coding", text)
        self.assertIn("R1 accountable power", text)
        self.assertIn("R7 trust", text)
        self.assertNotRegex(text, r"(?m)^R8\b")
        self.assertLess(len(text), 6000)

    def test_portable_reference_links_and_bundled_copies(self):
        path = ROOT / ".github/skills/advice-from-luminouspeace/SKILL.md"
        text=path.read_text(encoding="utf-8")
        links=re.findall(r"\\]\\((references/[^)]+\\.md)\\)", text)
        self.assertGreaterEqual(len(links),3)
        self.assertNotIn("../../../sources/",text)
        for rel in links:
            self.assertNotIn("..",rel.split("/"))
            self.assertTrue((path.parent/rel).is_file(),rel)
        self.assertEqual(
            (path.parent/"references/book-source-ledger.md").read_bytes(),
            (ROOT/"sources/book-source-ledger.md").read_bytes())

    def test_study_does_not_claim_new_book_coverage(self):
        text = (ROOT / "sources/studies/S11-three-body-problem-2026-11-21.md").read_text("utf-8")
        self.assertIn("Coverage change:** none", text)
        self.assertIn("No R8", text)
        self.assertIn("not** a new full-text reading", text)
        instructions = (ROOT / ".github/copilot-instructions.md").read_text("utf-8")
        self.assertIn("do **not** automatically adopt", instructions)
        self.assertIn("No database", instructions)


if __name__ == "__main__":
    unittest.main()
