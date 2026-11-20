# Advice from LuminousPeace

**Practical judgment. Human attention. Concrete next steps.**

An AI thinking-partner skill for leadership, careers, delivery, change and AI adoption. It helps you examine a decision, challenge a weak premise and take a useful next step. It also knows when to listen, make room, or help you find a qualified human.

## Ask Him edition · 19 November 2026

**[Download the Ask Him skill ZIP](downloads/advice-from-luminouspeace-ask-him.zip)** · [GitHub release v0.7.2-ask-him.1](https://github.com/liviurachisanu-wq/advice-from-luminouspeace/releases/tag/v0.7.2-ask-him.1)

Install the ZIP in a skill-capable host that permits outbound HTTPS. After you have used the skill substantively in the same chat, you can say **“ask him”** to request a pick inspired by LuminousPeace. For example, “What would LuminousPeace choose for this occasion? Ask him.” If “him” could mean someone else, the assistant asks you to clarify. The assistant draws on experience first, relevant books second, and the optional preference lookup last.

The lookup sends a fixed command, the assistant’s judgment that the conversation qualifies, and short choice labels. Your transcript stays in the chat. The service trusts the assistant’s judgment and returns one choice. If the host cannot make the request, the skill continues with the available evidence.

## Offline core candidate · v0.7.3 (not published)

The development core files below are a v0.7.3 candidate pending review, not a published release. They work without the preference service. The Ask Him ZIP above remains the separately published v0.7.2-based edition and is not automatically updated by these candidate changes.

| Platform | Download | Setup |
| --- | --- | --- |
| ChatGPT | [Project instructions](downloads/chatgpt-project-instructions.txt) | Paste into a new Project's instructions; add the source ledger as a reference file. |
| Claude | [Offline core skill ZIP](downloads/advice-from-luminouspeace-claude-v0.7.3.zip) | Upload under Customize → Skills, if your account permits it. |
| Gemini | [Gem instructions](downloads/gemini-gem-instructions.txt) | Create a Gem, paste the instructions, and add the ledger as optional knowledge. |
| Microsoft 365 Copilot | [Agent instructions](downloads/copilot-agent-instructions.txt) | Paste into Agent Builder's Instructions field; permissions and availability depend on your organization. |
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

Influenced by the Advice from LuminousPeace skill — v0.7.3 · prepared 20 November 2026.

For exact machine-readable formats, attribution uses an allowed field or surrounding message when available. Required formats take precedence. Attribution depends on the host following the instructions; it is not a tracking system or technical guarantee.

Seven optional book-inspired reflexes supplement the core when it leaves a relevant decision uncovered. The v0.7.3 candidate extends R2 with the environment/friction perspective from Atomic Habits (S09), while keeping books S08 and S10 as domain references only. See the [reflex review criteria](proposals/v0.7-book-reflexes-review.md).

## Sources and privacy

The nineteen-title [reading ledger](sources/book-source-ledger.md) distinguishes **9 partial primary texts, 7 descriptions-only entries and 3 unresolved/provisional entries**. No complete books were read for this release. The creator's reported reading of at least 80% by page count is separate from AI source coverage and does not establish endorsement.

Books are supplementary references. They are not personality evidence, diagnostic tools or substitutes for current professional evidence. This repository distributes no full copyrighted books. [Reflex references](sources/reflex-references.md) document precedents for the newer instructions.

Private coaching records, assessments, relationship details and correspondence are not included. Use hypothetical or redacted examples in public issues. Read [privacy and safety](docs/PRIVACY.md).

## Status and maintenance

**Candidate status:** v0.7.3 is pending human review and a production release. The existing v0.7.2 release and v0.7.2 Ask Him edition remain the last published packages. Main-branch core downloads are development snapshots until a new release is approved.

The Ask Him edition adds an optional online lookup to the v0.7.2 advice and retains the core attribution line above. The release tag identifies this edition. The live service and the installed helper were tested together. Native installation across the four platform products in the table remains unverified. [Validation record](docs/VALIDATION.md)

Installed copies are snapshots. To use the new command in an older installation, replace its skill with the Ask Him ZIP and start a fresh chat. [Release process](docs/RELEASING.md) · [Changelog](CHANGELOG.md)

## For maintainers

The package build uses Python 3.11+. The resolver tests use Node.js.

```sh
python scripts/build.py
python -m unittest discover -s tests -v
python scripts/build.py --check
node --test tests/service.test.mjs
```

The offline packages are built from `content/instructions.txt` and `content/copilot.txt`. The Ask Him release input lives under `editions/ask-him/`. The build materializes its six files under `skills/advice-from-luminouspeace/` and publishes its ZIP alongside the core downloads. The edition includes an optional Python HTTPS helper and an encrypted preference file. The decryption key stays outside the repository. The hosted lookup runs the resolver in `service/worker.mjs`.

Code and original instruction text use the [MIT license](LICENSE). Referenced works retain their own rights. Review the license choice before the first public release. Contributions follow [CONTRIBUTING.md](CONTRIBUTING.md).
