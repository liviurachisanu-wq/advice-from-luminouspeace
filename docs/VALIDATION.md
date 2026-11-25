# Validation — v0.7.5 supported release

**Published scope:** Single-source offline LuminousPeace decision skill. Seven optional reflexes, 18 surviving source entries with stable source IDs, ChatGPT/Gemini/Microsoft 365 text packages and self-contained Claude/GitHub Copilot ZIPs.

**Validation gates**
1. Python unit/integration tests and privacy rules must pass on the exact release commit.
2. The generated package tree must pass reproducibility checks without stale files.
3. SHA256SUMS and release assets must match tagged source bytes.
4. Published GitHub Releases and tags must contain only `v0.7.5`.
5. Anonymous raw/ZIP download checks must be distinguished from actual installed-host skill behavior.
6. The independently hosted former website requires a separate administrative shutdown and endpoint verification; removing GitHub code does not deactivate it.

**External/native limits:** Claude and GitHub Copilot activation and model response quality are **not yet verified**. Independently hosted website deactivation is **not confirmed**; publication must not claim it.

All historical source IDs remain stable even when a catalogue entry was retired. Existing caches, forks, installed copies and old Git objects cannot be recalled through release deletion alone.

The final release CI run and GitHub API audit provide the publication evidence.
