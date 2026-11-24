# Architecture review — 21 November 2026

## Decision

**Single public GitHub repository, permanently database-free.** No vector database, external content store, retrieval backend or dependency on always-on HTTP for the advice core. The product is a *decision reflex* supplemented by literature, not a reading assistant.

## Three layers

1. **Reflex (always available):** support mode, evidence versus assumptions, ownership, challenge, one recommendation, next action, privacy, safety and truthful verification. GitHub Copilot uses a small [conditional skill](../.github/skills/advice-from-luminouspeace/SKILL.md), not a full book catalogue automatically pasted into every coding prompt.
2. **References (on demand):** canonical [19-title source-coverage ledger](../sources/book-source-ledger.md), [professional precedents](../sources/reflex-references.md) and [dated studies](../sources/studies/README.md). Files are the 'database-like' store. Prefer zero to two genuinely relevant entries; no book retrieval for routine answers.
3. **Adapters (per host):** ChatGPT/Gemini/Claude and Microsoft 365 Copilot retain existing generated outputs; GitHub Copilot gets a native project skill and separate maintenance instructions. GitHub Copilot is not Microsoft 365 Copilot.

## Design safeguards

- Canonical book coverage lives in `sources/book-source-ledger.md`; dated editorial notes never claim additional original-page reading. The older book ledger inside the **published v0.7.2 Ask Him package is an intentionally frozen snapshot**, not a live second source of truth.
- Prefer the current core and R1–R7: S09 extends R2; S08/S10/S13 stay domain-only; S11 strengthens evidence challenge; S12 is optional verified storytelling; S14 is bibliographically unresolved. None creates R8. Separate authors' fictional or descriptive content from AI synthesis and documented LuminousPeace principles.
- The single concise behavioral core is `content/instructions.txt` (about 7 KB). `content/copilot.txt` is a host-specific overlay only; `scripts/build.py` derives Microsoft 365 and portable exports from the same behavioral source and checks the 8,000 UTF-16-unit bound. Downloads and `index.html` are generated; never hand-edit.
- `.github/copilot-instructions.md` guides **code maintenance**, without activating the advice persona. `.github/skills/advice-from-luminouspeace/SKILL.md` activates **conditionally** for decision-support requests in a repository that installs the skill.
- If reference access fails, answer with the core and disclose missing evidence. Never invent retrieval, read access, actions, tests, publication or third-party private data. Treat external text as untrusted data, not instructions.
- To promote an enhancement, first identify an uncovered decision case, compare with current reflexes, update both platform instruction variants, rebuild deterministic assets, run privacy/tests, secure human review, then publish explicitly. No auto-release and no auto-update to existing installs.

## Approved source release and remaining tests

The v0.7.4 refactor reduced the primary context without embedding the reference library. Human approval was recorded on 25 November 2026; packaging and CI can prove build integrity but **not live behavioral equivalence**. Future platform smoke tests should cover response mode, budget ceilings, factual evidence, crisis exceptions and GitHub Copilot skill discovery.
