# Offline release process

1. Review the owner's feedback, provenance, privacy and the source ledger. Do not infer consent or author endorsement.
2. Edit `content/instructions.txt` for behavior and `content/copilot.txt` only for Microsoft host constraints.
3. Prepare `release.json` with candidate version, approval status and a truthful attribution footer; approval is separate from the candidate date.
4. Run `python scripts/build.py`, `python -m unittest discover -s tests -v`, and `python scripts/build.py --check`.
5. Review generated ZIPs, SHA256 checksums, platform links, source IDs, copyright and privacy guard.
6. Collect native Claude and GitHub Copilot activation plus scenario results independently from CI. Static checks are not proof of model behavior.
7. After explicit human approval, merge reviewed code, tag the exact tested commit, create a draft GitHub Release, inspect it and publish only approved assets.
8. Verify public release bytes and tag/commit identity. Installed copies do not auto-update.

The core has no external database, hosted preference lookup, encryption key or private service dependency. Deleting GitHub releases and tags does not rewrite old commits or shut down independent third-party services.
