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

**Native behavioral acceptance: Not verified.** GitHub CI runs and outcomes should be recorded in the associated PR. Never describe source deletion as erasure of old copies or as the shutdown of an external host.
