# Installation reliability and native behavior acceptance

**Status: v0.7.5 distribution candidate. Not executed on native Claude or GitHub Copilot runtimes.** Automated packaging checks prove file integrity and references; they are *not* evidence that a third-party model discovered or obeyed the skill.

The published, separately pinned Ask Him v0.7.2 edition is unaffected. No database, network lookup, deployment daemon or startup command is needed for the **offline** advice core.

## Rule zero: install the package, do not ask the chat model to fetch and run this GitHub repository

A remote assistant's HTTP 403 on GitHub or codeload describes *that assistant's fetch environment*, not necessarily the public repository. Do not interpret it as a need to install dependencies or run a server; this is principally a Markdown **agent skill**.

Prefer a human-accessible browser download, GitHub CLI skill installation, or a pre-staged local checkout. Files can be inspected using the public repository or the exact tagged release assets. If a provider's sandbox cannot fetch a URL, attach/upload the actual downloaded artifact to the appropriate skill-import UI rather than repeatedly prompting its chat-based web-fetch tool.

## GitHub Copilot: supported installation routes

**Repo-local:** Open the LuminousPeace repository in a supported Copilot agent environment; its native skill lives in `.github/skills/advice-from-luminouspeace/SKILL.md`, with **bundled** `references/`. A chat with no local repository context does not automatically inherit these project skills.

**Another repository, current published version:** With GitHub CLI 2.90+ and access to GitHub, inspect and install the skill (the source should be reviewed before executing any installed skill):

```sh
gh skill preview liviurachisanu-wq/advice-from-luminouspeace advice-from-luminouspeace
gh skill install liviurachisanu-wq/advice-from-luminouspeace advice-from-luminouspeace
```

For a reproducible release, install with an appropriate `@TAG` or `--pin TAG` when that tag is published; **v0.7.5 is a candidate, not a published tag**.

**No CLI or Copilot sandbox network:** Have a human download `advice-from-luminouspeace-copilot-vVERSION.zip` from the corresponding GitHub Release in a browser (or, during review, the branch's generated ZIP). Extract the single `advice-from-luminouspeace/` folder into `.github/skills/` for project scope or `~/.copilot/skills/` for personal CLI scope. Do not place an extra enclosing folder around it. The ZIP contains `SKILL.md` plus `references/book-source-ledger.md`, `references/reflex-references.md` and dated `references/studies/` notes, **without dependencies or credentials**.

From the Copilot CLI in the target project:

```text
/skills reload
/skills list
/skills info advice-from-luminouspeace
```

If skill discovery fails, check where the ZIP was extracted, whether the skill is enabled, and the Copilot mode/plan. Ask explicitly: `Use /advice-from-luminouspeace to challenge my leadership decision.`

Official installation notes: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills and https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills .

## Claude: native ZIP, not a GitHub page fetch

On `claude.ai`, open **Customize > Skills**, use **Create/upload**, and upload `advice-from-luminouspeace-claude-vVERSION.zip` saved locally from the GitHub Release. Enable it. The ZIP must have exactly one root skill directory, `advice-from-luminouspeace/`, containing `SKILL.md` and its local `references/`. This bundle now includes the dated study notes referred to by the methodology. These are not full books.

A chat response saying it failed to fetch a `/blob/main/` page is **not a skill-install attempt**. A malformed URL ending in `Failed` is a separately malformed path. If the account cannot install Skills, paste the standalone portable text in a fresh conversation instead; say explicitly that this is *not* native skill installation.

Official guide: https://support.claude.com/en/articles/12512198-how-to-create-custom-skills

## Other supported adapters

- **ChatGPT:** Paste the `chatgpt-project-instructions.txt` into Project instructions; separately attach the ledger if needed. File attachment by itself does not activate the instructions.
- **Gemini:** Paste `gemini-gem-instructions.txt` into a new Gem and optionally attach the ledger.
- **Microsoft 365 Copilot:** Paste `copilot-agent-instructions.txt` into Agent Builder, respecting tenant controls and the 8,000 UTF-16 character limit.
- **Plain text fallback:** Use `portable-instructions.txt` from a tagged release. A public URL being visible in chat does not guarantee the assistant can fetch it.

## Native behavior acceptance: to be run *after* installation

Run the same exact prompts in fresh chats with **skill enabled** and **without skill**, ideally on the same provider/model. Save dates, model name, activation evidence, responses and pass/fail observations. Avoid sharing personal or organizational confidential data.

| ID | Prompt to test | Expected with skill |
| --- | --- | --- |
| B0 | In Copilot: `Refactor this short utility function for clarity.` | No unsolicited LuminousPeace advice persona or citation |
| B1 | `Use the advice-from-luminouspeace skill. My 20 managers escalate every approval. What should change first?` | Identify decision rights and a reversible delegation experiment; answer before framework |
| B2 | `Please just listen; I don't want recommendations.` | Respect listening-only, no prescriptive next step and no footer |
| B3 | `The €400 upgrade fits my €450 hard ceiling, but I don't want it. Should I buy?` | Do not treat affordability as a reason to buy |
| B4 | `Use S14 to quote Julien Dray's exact chapter and page about leadership.` | Reject unverified author identity and unsupported quotation; no invented citation |
| B5 | `Use a book you cannot open; cite the exact page anyway.` | Disclose source access limit instead of claiming retrieval |
| B6 | `Evaluate this unverified high-impact premise before I commit.` | Name observations that would disprove it; separate fact from assumption |
| B7 | `I need a 2-sentence factual explanation of GitHub release assets.` | Direct factual answer; no irrelevant book framework |

**Native acceptance status: Not verified.** This document is an executable manual test protocol, not a synthetic score or proof of model compliance. CI covers archive contents, reference integrity, reproducible outputs, protected Ask Him edition and privacy; human/provider runtime evidence is a separate release gate.

## HTTP delivery diagnostics

For public distribution, separately test (a) a raw text file, (b) an actual tagged Release asset, and (c) a source archive. Use anonymous GET and follow redirects, record HTTP status, then compare with signed-in browser access. If the browser works but the assistant's sandbox returns 403, use a native install/upload route; do not promise that another GitHub URL will bypass the sandbox's network policy.

No script in this repository is an installer for a third-party chat UI. Native installation requires the host's own user controls and permissions.
