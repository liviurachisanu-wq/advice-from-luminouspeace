# Validation — v0.8.1 release candidate

**Candidate scope:** Single-source offline LuminousPeace decision skill. Seven optional reflexes, 17 surviving source entries with stable source IDs, ChatGPT/Gemini/Microsoft 365 text packages and self-contained Claude/GitHub Copilot ZIPs.

**Validation gates**
1. Python unit/integration tests and privacy rules must pass on the exact release commit.
2. The generated package tree must pass reproducibility checks without stale files.
3. SHA256SUMS and release assets must match tagged source bytes.
4. Published assets must match their exact tag. The v0.8.1 candidate is not yet published. Historical releases may remain available.
5. Anonymous raw/ZIP download checks must be distinguished from actual installed-host skill behavior.
6. The independently hosted former website requires a separate administrative shutdown and endpoint verification; removing GitHub code does not deactivate it.

**Native evidence (26 November 2026):** Claude Sonnet 5.5 loaded the installed v0.7.5 skill, proposed reversible delegation with explicit limits, and did not claim a personal preference or visibly perform a hosted lookup. Copilot runtime acceptance, active ChatGPT Project Instructions, and native v0.8 reruns remain pending.

**Hosting evidence (26 November 2026):** Sites access is owner-only. Anonymous GET requests to the landing page and both legacy ZIP routes returned HTTP 401.

All historical source IDs remain stable even when a catalogue entry was retired. Existing caches, forks, installed copies and old Git objects cannot be recalled through release deletion alone.

The final release CI run and GitHub API audit must provide publication evidence; native v0.8.1 tests remain pending.
