# Catalog scan review (2026-10-17)

Source revision: `7c41a3e9addbd4cc20f0f6477b3facaf3c982862`. With plugin-scanner 3.0.123, the original local score was 43; after these changes it is 86. These are local preflight results. Listing still requires the catalog's own completed centralized score of at least 80.

## Changes and review

Actions are pinned to immutable SHAs (the Rust action uses upstream master history with an explicit stable toolchain input where applicable), a vulnerability reporting policy and Dependabot are added, and a read-only, offline source scan runs on pushes and pull requests using the catalog's exact action SHA and score threshold. No scanner suppressions or baseline are configured.

All remaining HARDCODED_SECRET findings are non-credentials: image-use:2694 builds a per-send guard identifier from uuid.uuid4(), test_image_use.py:160 passes a placeholder token inside a mocked environment, and docs/superpowers/plans/2026-07-03-drawstyle-platform.md:59 contains a test-only session-secret example. Locations refer to the original revision. These remain visible rather than being suppressed.

Release hardening separates main-push eligibility from privileged work, always checks out trusted main without persisting credentials, and verifies that the successful workflow_run originated in this repository and matches that checkout. Stale events, forks, failed/PR runs, other branches and non-main manual dispatches cannot release. The existing page-JavaScript regression harness now executes in an explicit VM context with a timeout rather than lexical eval; the same native-send guard scenarios still pass.

## Reproduction

```sh
# In an isolated Python environment:
python -m pip install plugin-scanner==3.0.123
plugin-scanner scan . --format json --output /tmp/image-use-scan.json --min-score 80 --fail-on-severity none
```

## Remaining rule locations

| Rule | Severity | Location |
| --- | --- | --- |
| `HARDCODED_SECRET` | high | `image-use:2694` |
| `HARDCODED_SECRET` | high | `test_image_use.py:160` |
| `HARDCODED_SECRET` | high | `docs/superpowers/plans/2026-07-03-drawstyle-platform.md:59` |
