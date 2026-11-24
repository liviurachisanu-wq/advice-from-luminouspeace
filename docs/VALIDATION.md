# Validation — offline v0.7.5 candidate

**Status:** under human review. No assertion of native Claude or GitHub Copilot activation or approval of a new release.

The retirement cleanup removes legacy online service code and old package dependencies, plus the unverified source entry. The 18 surviving source IDs are stable, with a deliberate gap. The single behavioral core retains R1–R7 and preserves source limitations.

## Required evidence
1. Regenerate deterministic assets: `python scripts/build.py` and `python scripts/build.py --check`.
2. Run all surviving Python tests: `python -m unittest discover -s tests -v`.
3. Validate privacy, source ID integrity, links, ZIP contents and SHA256 sums.
4. Confirm no obsolete hosted-service implementation, encrypted preference file, or retired edition archive is generated.
5. Check public HTTP delivery from an unauthenticated runner, separately from individual provider sandbox policies.
6. Test skill discovery and responses in native Claude and GitHub Copilot following [the acceptance protocol](INSTALLATION-AND-BEHAVIOR.md); CI is not a substitute.
7. Verify removal of targeted published GitHub Releases and tags via GitHub API after deletion. Historical Git objects, caches and independently deployed services are a separate concern.

## Verified cleanup — 25 November 2026

- Clean source was merged through [PR #8](https://github.com/liviurachisanu-wq/advice-from-luminouspeace/pull/8), main commit `151c4d128b2f8b25ee0777222f5d7f4d2a79228a`.
- [Deterministic rebuild](https://github.com/liviurachisanu-wq/advice-from-luminouspeace/actions/runs/45513862520) succeeded: **34 Python tests passed**, **14 reproducible generated files** built and checked.
- [Deletion and post-merge preflight](https://github.com/liviurachisanu-wq/advice-from-luminouspeace/actions/runs/45514068356) succeeded: same **34 Python tests**, **14 checked files**, 18 surviving source entries and absence of hosted edition source. All three explicitly requested legacy GitHub Releases and Git tags were verified absent individually.
- The daily book-study automation was updated to omit the retired entry while preserving all future historical date-to-source IDs.
- Older published versions `v0.7` and `v0.7.1` were **not** deleted because they were not requested. Current v0.7.5 is a **candidate on main**, not a new published GitHub Release.
- This does not rewrite GitHub commit history, recall previously downloaded copies, or shut down a separately deployed app.

**Native behavioral acceptance: Not verified.** The offline core and references passed static tests only. Hosted external-service shutdown requires separate credentials/actions outside GitHub.

