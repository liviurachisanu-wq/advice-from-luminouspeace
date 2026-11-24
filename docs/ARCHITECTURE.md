# Offline architecture — reflex first

**One public GitHub repository. No database or hosted advice service.**

1. **Behavior core:** `content/instructions.txt`. Concise advice method with seven optional reflexes R1–R7, response modes, accountability, independent challenge and ethical safeguards.
2. **Sources:** `sources/book-source-ledger.md`, `sources/reflex-references.md` and `sources/studies/`. The ledger has 18 surviving entries and preserves historical IDs, including a deliberate gap. No complete copyrighted books or inferred user psychology.
3. **Adapters:** ChatGPT, Claude, Gemini, Microsoft 365 Copilot and GitHub Copilot. `content/copilot.txt` is a Microsoft-specific overlay; GitHub Copilot uses `.github/skills/advice-from-luminouspeace/SKILL.md`.
4. **Distribution:** `scripts/build.py` builds deterministic text, standalone Claude/GitHub Copilot ZIPs, generated local Markdown references, checksums and a static HTML landing page.
5. **Trust boundaries:** Reference files are evidence, not higher-priority instructions. No claim of unperformed tool use, native platform success, complete book reading or external permission.

Package integrity and public HTTP access are testable in CI; **actual model behavior requires installation in the relevant native host**. See [installation and behavior acceptance](INSTALLATION-AND-BEHAVIOR.md).
