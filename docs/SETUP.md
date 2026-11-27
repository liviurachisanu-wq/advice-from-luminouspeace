# Platform setup — offline v0.8.1 candidate

The package is a Markdown instruction skill, not a runnable server. Native installation should use the platform's own skill or agent configuration interface. See the [validation record](VALIDATION.md) for native smoke-test coverage and pending checks.

## Claude
1. Download `downloads/advice-from-luminouspeace-claude-v0.8.1.zip` to your computer from this candidate checkout; for the published release use its exact tag and assets.
2. In Claude, open Customize → Skills and upload/create a skill where your account permits it.
3. Enable the skill and begin a fresh conversation. The ZIP contains one `advice-from-luminouspeace/` folder with `SKILL.md` and local `references/`.
4. Run the [native acceptance scenarios](INSTALLATION-AND-BEHAVIOR.md).

[Claude skills reference](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).

## GitHub Copilot
1. Download `downloads/advice-from-luminouspeace-copilot-v0.8.1.zip` to your computer.
2. Extract its single `advice-from-luminouspeace/` folder under `.github/skills/` in the target repository, or a supported personal skill location.
3. In a supported Copilot CLI, use `/skills reload`, `/skills list` and `/skills info advice-from-luminouspeace` to verify discovery.
4. Request the skill explicitly for a decision; ordinary coding should not adopt its advice persona.

[GitHub Copilot agent skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills).

## ChatGPT
Paste `downloads/chatgpt-project-instructions.txt` into a new Project's Instructions; attach `sources/book-source-ledger.md` if relevant. Uploading a file alone does not activate instructions.

[ChatGPT Projects](https://help.openai.com/en/articles/10169521-projects-in-chatgpt).

## Gemini
Create a Gem, paste `downloads/gemini-gem-instructions.txt` and optionally attach the ledger.

[Gemini Gems](https://support.google.com/gemini/answer/15146780?hl=en).

## Microsoft 365 Copilot
Paste `downloads/copilot-agent-instructions.txt` into Agent Builder. The builder enforces an 8,000 UTF-16-character bound; tenant access policies still apply.

[Microsoft Agent Builder](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-build-agents).

## If the AI sandbox gets HTTP 403
Download the artifact in your own browser, then import it through the supported native host UI. A GitHub `/blob/` page is an HTML viewer, not a skills installer. As a fallback, paste `downloads/portable-instructions.txt` into a fresh conversation and label it a *manual instruction test*, not verified native installation.

No service endpoint, secret, database or dependency installation is required.
