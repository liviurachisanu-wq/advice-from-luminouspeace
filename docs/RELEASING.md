# Release process

Review the project at least monthly. A review may conclude that no substantive change is justified; do not fabricate updates. Provider changes or material errors can justify earlier releases.

1. Review explicit user feedback and source accuracy; exclude private coaching and identifying details.
2. Edit both instruction variants. Update version, release date, status, next review and exact footnote in `release.json` and the instructions. Keep human approval separate from draft release dates.
3. Update README, setup downloads and CHANGELOG when version names change. Do not claim older behavior tests cover the new version.
4. Run `python scripts/build.py`, `python -m unittest discover -s tests -v` and `python scripts/build.py --check`. Include tests and archives in privacy review; keep protected-identity fixtures outside the repository. Review author and committer metadata separately and use a no-reply identity. Do not assume a connector hides the account email.
5. Human reviewer checks behavior, privacy, source limits, license and platform setup; record their explicit decision. Never infer approval from silence or passing tests.
6. Create a GitHub repository under the chosen publishing account and push only this project. No private review-pack HTML, account links or original workspace history belongs in it.
7. Create a reviewed version tag such as `v0.6`. The optional **Draft release** workflow requires an existing matching tag and creates a draft with downloadable assets; review it before publishing.
8. Publish the release when authorized. Users must replace their installed copies; this repository does not silently update them.

The repository is prepared for GitHub but no repository account, remote URL, tag or public deployment is created by the preparation process. The original instruction text and build scripts are prepared with MIT licensing for human review; third-party works keep their rights.

The landing page works offline. GitHub renders `index.html` as source by default; a live website requires a separate GitHub Pages configuration. No hosted-site availability is claimed.
