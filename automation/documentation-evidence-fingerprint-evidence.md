# Documentation evidence fingerprint repair

## Failure

The receipt-bound roadmap commit `3e5619b` contained exactly its approved candidate and evidence paths. Its staged receipt check passed, but its post-commit check failed with `material verification inputs changed` because the documentation lane treats Markdown as a material input.

## Cause

Staged fingerprinting checked out the receipt base and overlaid only candidate content. Committed fingerprinting instead checked out the entire commit, so Markdown evidence affected the fingerprint only after commit. Exact commit-path validation already verifies candidate plus evidence separately.

## Repair

CodeCraft Starter 0.5.2 makes both modes check out the receipt base and overlay only candidate content from the requested source. Evidence remains constrained by its allowlist and the exact committed-path check.

The clean-room transaction test now includes allowed Markdown evidence. It passed staged verification before the repair and failed only at post-commit verification; after the repair, both checks pass.

## Scope

No RPG behavior, roadmap content, or commit history is changed. Commit `3e5619b` will be rechecked in place after the project-local installation is upgraded through the distribution.
