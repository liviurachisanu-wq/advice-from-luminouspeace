# Release process

Review the project at least monthly. A review may conclude that no substantive change is justified; do not fabricate updates. Provider changes or material errors can justify earlier releases.

1. Review explicit user feedback and source accuracy; exclude private coaching and identifying details.
2. Edit the single behavior source `content/instructions.txt`; edit `content/copilot.txt` only for host-specific Microsoft 365 constraints. Do not duplicate behavioral rules in the overlay. Update version, date, status, next review, and exact footnote in `release.json` and the core; derive Microsoft output in the builder. Keep human approval separate from draft release dates.
3. Update README, setup downloads and CHANGELOG when version names change. Do not claim older behavior tests cover the new version.
4. Run `python scripts/build.py`, `python -m unittest discover -s tests -v` and `python scripts/build.py --check`. Include tests and archives in privacy review; keep protected-identity fixtures outside the repository. Review author and committer metadata separately and use a no-reply identity. Do not assume a connector hides the account email.
5. Human reviewer checks behavior, privacy, source limits, license and platform setup; record their explicit decision. Never infer approval from silence or passing tests.
6. Create a GitHub repository under the chosen publishing account and push only this project. No private review-pack HTML, account links or original workspace history belongs in it.
7. Create a reviewed version tag such as `v0.6`. The optional **Draft release** workflow requires an existing matching tag and creates a draft with downloadable assets; review it before publishing.
8. Publish the release when authorized. Users must replace their installed copies; this repository does not silently update them.

The named Ask Him edition of the v0.7.2 core uses the release tag `v0.7.2-ask-him.1`. The `edition` entry in `release.json` records the edition name, tag and release date. The core version, approval scope and attribution retain their original meaning.

For this edition, run `node --test tests/service.test.mjs` and build the Worker with `python scripts/build_service.py OUTPUT.mjs`. Packaging and validation need no secret. Check that the GitHub ZIP matches the separately deployed download, the repository’s native skill files match the ZIP members, and the hosted lookup accepts the current command after both activation conditions are met. Keep the key and the owner’s private maintenance files outside GitHub.

The repository landing page works offline. The optional preference lookup runs on the separately hosted Ask Him site. A GitHub push and a service deployment update different destinations. Verify both when changing the public edition. [Hosted Ask Him site](https://ask-liviu.liviurachisanu800587.chatgpt.site)
