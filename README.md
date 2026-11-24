# Advice from LuminousPeace

**Practical judgment. Human attention. Concrete next steps.**

An AI thinking-partner skill for leadership, careers, delivery, change and AI adoption. It helps you examine a decision, challenge a weak premise and take a useful next step. It also knows when to listen, make room, or help you find a qualified human.

## Ask Him edition · 19 November 2026

**[Download the Ask Him skill ZIP](downloads/advice-from-luminouspeace-ask-him.zip)** · [GitHub release v0.7.2-ask-him.1](https://github.com/liviurachisanu-wq/advice-from-luminouspeace/releases/tag/v0.7.2-ask-him.1)

Install the ZIP in a skill-capable host that permits outbound HTTPS. After you have used the skill substantively in the same chat, you can say **“ask him”** to request a pick inspired by LuminousPeace. For example, “What would LuminousPeace choose for this occasion? Ask him.” If “him” could mean someone else, the assistant asks you to clarify. The assistant draws on experience first, relevant books second, and the optional preference lookup last.

The lookup sends a fixed command, the assistant’s judgment that the conversation qualifies, and short choice labels. Your transcript stays in the chat. The service trusts the assistant’s judgment and returns one choice. If the host cannot make the request, the skill continues with the available evidence.

## Offline core · v0.7.4 (released 25 November 2026)

The v0.7.4 core has been approved for publication and distributed in the [GitHub release](https://github.com/liviurachisanu-wq/advice-from-luminouspeace/releases/tag/v0.7.4). It works without the preference service. The Ask Him ZIP above remains the separate, already published v0.7.2-based edition; it was **not** upgraded or included in the v0.7.4 release assets.

| Platform | Download | Setup |
| --- | --- | --- |
| ChatGPT | [Project instructions](downloads/chatgpt-project-instructions.txt) | Paste into a new Project's instructions; add the source ledger as a reference file. |
| Claude | [Offline core skill ZIP](downloads/advice-from-luminouspeace-claude-v0.7.4.zip) | Upload under Customize → Skills, if your account permits it. |
| Gemini | [Gem instructions](downloads/gemini-gem-instructions.txt) | Create a Gem, paste the instructions, and add the ledger as optional knowledge. |
| Microsoft 365 Copilot | [Agent instructions](downloads/copilot-agent-instructions.txt) | Paste into Agent Builder's Instructions field; permissions and availability depend on your organization. |
| GitHub Copilot | [Conditional decision skill](.github/skills/advice-from-luminouspeace/SKILL.md) | Repository-scoped; loads only for LuminousPeace decision-support tasks. [Setup](docs/SETUP.md#github-copilot). |
| Any supported chat | [Portable instructions](downloads/portable-instructions.txt) | Paste into a fresh conversation, then explain your situation. |
| Offline browser | [Download page](index.html) | Download the repository and open index.html locally for copy and download buttons. |

On GitHub, open a file and select **Download raw file**, or use the ZIP under **Assets** on the release page. The full source ledger is also downloadable. [Reading ledger](sources/book-source-ledger.md) · [Platform setup](docs/SETUP.md)

## Try it

> My managers ask me to approve everything. What should I change this week?

> I need to describe something painful. Please just listen; no advice.

> My budget ceiling is €450, but the €400 offer does not feel worthwhile. Help me decide.

## What makes it useful

- **Choose the response:** opinion, recommendation, action, or listening/space. The skill asks only when the desired support is unclear.
- **Keep judgment with you:** examine facts, assumptions, tradeoffs and reversible options.
- **Seek qualified help:** match professional credentials and experience to the task, then prepare useful questions.
- **Respect limits and value:** a spending ceiling never becomes a reason to buy.
- **Earn trust:** identify uncertainty, correct errors, and distinguish attempted work from verified results.

Substantive advice materially influenced by the skill uses this plain-text attribution line. It is omitted for crisis responses, listening-only replies, and routine answers.

Influenced by the Advice from LuminousPeace skill — v0.7.4 · released 25 November 2026.

For exact machine-readable formats, attribution uses an allowed field or surrounding message when available. Required formats take precedence. Attribution depends on the host following the instructions; it is not a tracking system or technical guarantee.

Seven optional book-inspired reflexes supplement the core only when its existing decision checks are insufficient. The v0.7.4 release keeps R1–R7: Atomic Habits (S09) already strengthens R2, S11 reinforces evidence checks, S12 is optional storytelling, S13 is domain-only, and S14 remains unresolved. See the [reflex review criteria](proposals/v0.7-book-reflexes-review.md).

## Reflex-first architecture and GitHub Copilot

All book knowledge remains as Markdown in this repository; no database or separate knowledge store is planned. GitHub Copilot now has a [conditional project skill](.github/skills/advice-from-luminouspeace/SKILL.md) distinct from the Microsoft 365 Copilot instructions. Normal coding requests do not adopt the LuminousPeace advice persona.

The v0.7.4 release uses one concise behavioral source for ChatGPT, Claude, Gemini, and Microsoft 365 Copilot, with on-demand source files. GitHub Copilot has a conditional native skill; S08–S14 studies are provenance-limited and add no R8. The independently deployed Ask Him edition stays pinned to v0.7.2 pending separate testing. [Architecture review](docs/ARCHITECTURE.md).

## Sources and privacy

The nineteen-title [reading ledger](sources/book-source-ledger.md) distinguishes **9 partial primary texts, 7 descriptions-only entries and 3 unresolved/provisional entries**. No complete books were read for this release. The creator's reported reading of at least 80% by page count is separate from AI source coverage and does not establish endorsement.

Books are supplementary references. They are not personality evidence, diagnostic tools or substitutes for current professional evidence. This repository distributes no full copyrighted books. [Reflex references](sources/reflex-references.md) document precedents for the newer instructions.

Private coaching records, assessments, relationship details and correspondence are not included. Use hypothetical or redacted examples in public issues. Read [privacy and safety](docs/PRIVACY.md).

## Status and maintenance

**Release status:** v0.7.4 content has explicit human approval dated 25 November 2026, with reproducible package tests. The core GitHub release is published; the separately hosted v0.7.2 Ask Him edition remains pinned and unchanged. Native live behavior across all AI platforms has not been verified.

The Ask Him edition adds an optional online lookup to the **v0.7.2** advice and retains its original version footer, not the newer v0.7.4 footer. The release tag identifies this edition. The live service and the installed helper were tested together. Native installation across the four platform products in the table remains unverified. [Validation record](docs/VALIDATION.md)

Installed copies are snapshots. To use the new command in an older installation, replace its skill with the Ask Him ZIP and start a fresh chat. [Release process](docs/RELEASING.md) · [Changelog](CHANGELOG.md)

## For maintainers

The package build uses Python 3.11+. The resolver tests use Node.js.

```sh
python scripts/build.py
python -m unittest discover -s tests -v
python scripts/build.py --check
node --test tests/service.test.mjs
```

The offline packages are built from the canonical `content/instructions.txt` behavioral core; `content/copilot.txt` is a Microsoft 365-specific overlay, not a second behavioral source. The frozen Ask Him release input lives under `editions/ask-him/`; the build preserves its six packaged files under `skills/advice-from-luminouspeace/` and maintains the old ZIP as a separate download, excluded from the new core release's assets and checksums. The edition includes an optional Python HTTPS helper and an encrypted preference file. The decryption key stays outside the repository. The hosted lookup runs the resolver in `service/worker.mjs`.

Code and original instruction text use the [MIT license](LICENSE). Referenced works retain their own rights. Review the license choice before the first public release. Contributions follow [CONTRIBUTING.md](CONTRIBUTING.md).
