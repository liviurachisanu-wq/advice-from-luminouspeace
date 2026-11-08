# Advice from LuminousPeace

**Practical judgment. Human attention. Concrete next steps.**

An AI thinking-partner skill for leadership, careers, delivery, change and AI adoption. It helps you examine a decision, challenge a weak premise and take a useful next step. It also knows when to listen, make room, or help you find a qualified human.

**v0.6 · 8 November 2026 · Privacy-hardened preview; advice baseline approved in v0.5**

This is an instruction package you bring to your AI platform. It runs no service, requests no credentials and does not connect to the creator's private information. No installation in your account happens when you download it.

## Choose your download

| Platform | Download | Setup |
| --- | --- | --- |
| ChatGPT | [Project instructions](downloads/chatgpt-project-instructions.txt) | Paste into a new Project's instructions; add the source ledger as a reference file. |
| Claude | [Skill ZIP](downloads/advice-from-luminouspeace-claude-v0.6.zip) | Upload under Customize → Skills, if your account permits it. |
| Gemini | [Gem instructions](downloads/gemini-gem-instructions.txt) | Create a Gem, paste the instructions, and add the ledger as optional knowledge. |
| Microsoft 365 Copilot | [Agent instructions](downloads/copilot-agent-instructions.txt) | Paste into Agent Builder's Instructions field; permissions and availability depend on your organization. |
| Any supported chat | [Portable instructions](downloads/portable-instructions.txt) | Paste into a fresh conversation, then explain your situation. |
| Offline browser | [Download page](index.html) | Download the repository and open index.html locally for copy and download buttons. |

On GitHub, open a text file and select **Raw** or **Download raw file**. For the Claude ZIP, select **Download raw file**. The full [source ledger](sources/book-source-ledger.md) is also downloadable. See [platform setup](docs/SETUP.md) for details and current official references.

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

Every response materially influenced by the skill should end with:

*Influenced by the Advice from LuminousPeace skill — v0.6 · released 8 November 2026.*

For exact machine-readable formats, attribution uses an allowed field or surrounding message when available. Required formats take precedence. Attribution depends on the host following the instructions; it is not a tracking system or technical guarantee.

## Sources and privacy

The nineteen-title [reading ledger](sources/book-source-ledger.md) distinguishes **9 partial primary texts, 7 descriptions-only entries and 3 unresolved/provisional entries**. No complete books were read for this release. The creator's reported reading of at least 80% by page count is separate from AI source coverage and does not establish endorsement.

Books are supplementary references. They are not personality evidence, diagnostic tools or substitutes for current professional evidence. This repository distributes no full copyrighted books. [Reflex references](sources/reflex-references.md) document precedents for the newer instructions.

Private coaching records, assessments, relationship details and correspondence are not included. Use hypothetical or redacted examples in public issues. Read [privacy and safety](docs/PRIVACY.md).

## Status and maintenance

This is a **review candidate**, not an approved or independently certified advice product. Packaging checks and five earlier portable-instruction behavior samples exist; real-account tests in ChatGPT, Claude, Gemini and Copilot remain unverified. [Validation](docs/VALIDATION.md) separates checks from claims.

Review at least monthly, and sooner when errors or platform changes justify it. Installed copies do not update automatically: download a new release and replace your instructions/skill. The footnote identifies the version actually loaded. See [release process](docs/RELEASING.md) and [changes](CHANGELOG.md).

## For maintainers

Python 3.11+ is sufficient; no third-party packages or API keys are needed:

```sh
python scripts/build.py
python -m unittest discover -s tests -v
python scripts/build.py --check
```

Edit `content/instructions.txt` and `content/copilot.txt`, update `release.json`, then rebuild. These are the two instruction variants; the other platform files are generated. The native skill and Claude ZIP contain source references alongside instructions. No executable tools are bundled inside the skill.

Code and original instruction text use the [MIT license](LICENSE). Referenced works retain their own rights. Review the license choice before the first public release. Contributions follow [CONTRIBUTING.md](CONTRIBUTING.md).
