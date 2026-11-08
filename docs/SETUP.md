# Platform setup

Documentation checked 8 November 2026. Product menus, limits and account permissions can change. These are documented setup routes, not claims that the package was installed or tested in your account.

## ChatGPT

1. Download `downloads/chatgpt-project-instructions.txt` and `sources/book-source-ledger.md`.
2. Create a new Project called Advice from LuminousPeace.
3. Paste the instruction text into the Project instructions. Add the ledger as a reference file; uploading a file alone is not the same as setting instructions.
4. Start a fresh chat inside the Project and try a scenario from `docs/VALIDATION.md`.

If the interface rejects the full text, use the portable text in a fresh conversation rather than silently truncating the instructions. This repository does not install a native ChatGPT personal skill.

Official reference: [Projects in ChatGPT](https://help.openai.com/en/articles/10169521-projects-in-chatgpt).

## Claude

1. Download `downloads/advice-from-luminouspeace-claude-v0.5.zip` as a file; do not upload the full repository ZIP as a skill.
2. In Customize → Skills, choose the create/upload option and upload the skill ZIP.
3. Enable it and explicitly ask to use Advice from LuminousPeace in a fresh chat.
4. Confirm the response matches the requested mode and carries the correct version footnote.

The ZIP has one root folder, `advice-from-luminouspeace/`, containing `SKILL.md` and `references/`. Skill availability can depend on account and organization settings. If unavailable, paste the portable instructions into a fresh chat instead.

Official references: [Use skills](https://support.claude.com/en/articles/12512180-use-skills-in-claude), [Create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).

## Gemini

1. Open Gemini on the web, select Gems, then New Gem.
2. Name it Advice from LuminousPeace and paste `downloads/gemini-gem-instructions.txt` into Instructions.
3. Optionally attach `sources/book-source-ledger.md` in Knowledge.
4. Preview and save. Check behavior and attribution in a fresh conversation.

This is a Gem configuration, not a native skill ZIP import. Avoid automatic rewriting of the instructions unless you compare and approve the resulting changes.

Official reference: [Use Gems](https://support.google.com/gemini/answer/15146780?hl=en).

## Microsoft 365 Copilot

1. Use Microsoft 365 Copilot → New agent → Configure, where available.
2. Set the agent name to **LuminousPeace Advice** (under the documented 30-character limit).
3. Paste `downloads/copilot-agent-instructions.txt` into Instructions. The build checks its UTF-16 length against 8,000 characters.
4. Test in the preview. Add the reading ledger as knowledge only if the tenant and file support permit it; do not move behavior instructions into knowledge to evade the limit.
5. Save according to your organization's policies. No Microsoft 365 connector or access to work data is required by this package.

The compact export is an intentional adaptation. Compare it against the portable variant when changing behavior. Consumer Copilot and Microsoft 365 Agent Builder have different features; the portable paste-in-chat route may be used where supported, but no consumer custom-agent import is claimed.

Official reference: [Agent Builder configuration](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-build-agents).

## Updates

Replace the installed skill or pasted instructions with a new release; downloads are snapshots. Start a fresh conversation when testing an update to reduce influence from earlier instructions. Do not claim the creator approved a release unless its release record explicitly says so.
