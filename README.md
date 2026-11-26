# Advice from LuminousPeace

**Practical judgment. Human attention. Concrete next steps.**

An offline-first AI decision-support skill for leadership, career choices, IT delivery, change and responsible AI adoption. This repository contains instructions and Markdown references, not an application server or database.

## Current release — v0.8

**v0.8 is the current supported GitHub release.** Download the stable packages from [v0.8 release assets](https://github.com/liviurachisanu-wq/advice-from-luminouspeace/releases/tag/v0.8). The v0.7.5 Claude package passed a native smoke test; the v0.8 packages were validated offline. Native GitHub Copilot acceptance is pending.

| Platform | File | Installation |
| --- | --- | --- |
| ChatGPT | [Project instructions](downloads/chatgpt-project-instructions.txt) | Paste into a Project's instructions |
| Claude | [Native skill ZIP](downloads/advice-from-luminouspeace-claude-v0.8.zip) | Upload using Customize → Skills |
| GitHub Copilot | [Portable skill ZIP](downloads/advice-from-luminouspeace-copilot-v0.8.zip) | Extract the single skill directory into the host's skills folder |
| Gemini | [Gem instructions](downloads/gemini-gem-instructions.txt) | Paste into a new Gem |
| Microsoft 365 Copilot | [Agent instructions](downloads/copilot-agent-instructions.txt) | Paste into Agent Builder, subject to tenant policy |
| Other chats | [Portable text](downloads/portable-instructions.txt) | Paste instructions into a fresh conversation |

Both native ZIPs contain local source references. All canonical source material remains Markdown in this GitHub repository. See the [installation and behavior acceptance guide](docs/INSTALLATION-AND-BEHAVIOR.md) and [platform-specific setup](docs/SETUP.md).

## What the skill does

- Choose the right mode: opinion, recommendation, action, or listening/space.
- Separate facts from assumptions and challenge important premises.
- Respect user-defined thresholds; an affordable purchase may still be unwanted.
- Suggest a reversible next step, with ownership and observable results.
- Use zero to two optional book-derived reflexes (R1–R7) only when useful.
- Stay honest about source coverage, professional limits and what tools actually did.

The [source ledger](sources/book-source-ledger.md) contains **18 surviving entries**, preserving their existing source IDs (there is a deliberate gap). No complete copyrighted books are distributed.

## Example requests

> My managers escalate every minor approval. What should I change first?

> I want to talk about something difficult. Please listen; no advice.

> The upgrade fits my spending ceiling, but I don't want it. Should I buy it?

## Offline and privacy boundaries

The supported v0.8 package contains no hosted preference lookup, encryption key, external database or custom service. The former website is restricted to its owner. Signed-out checks returned HTTP 401 for its landing page and both legacy downloads on 26 November 2026. Previously downloaded packages and historical Git objects may persist. Users' AI providers control their own data settings.

For source limits, human approval and privacy practices, see [validation](docs/VALIDATION.md), [architecture](docs/ARCHITECTURE.md), [privacy](docs/PRIVACY.md) and [release process](docs/RELEASING.md).

## Build and validation

```sh
python scripts/build.py
python -m unittest discover -s tests -v
python scripts/build.py --check
```

Generated downloads, local skill references and the landing page should not be edited manually. The code and original skill text are MIT licensed; third-party works retain their own rights. Static tests cannot establish real model behavior.
