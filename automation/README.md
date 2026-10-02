# Automation Records

This repository-root directory owns collaboration workflows, programming-process improvements, quality-automation records, and skill-evolution artifacts.

Executable machinery remains at the conventional path used by its runtime, including `.codecraft`, `.github/workflows`, `.habit-hooks`, and `pmd`. Skills and agent configuration already contained in `.agents`, `.codex`, or `.claude` remain there. This directory holds the agreements, evidence, and decisions that explain and evolve that machinery.

Feature evidence, architecture records, and session handoffs belong under the categories documented in `emergent/README.md`.

`review-decisions.json` is the tracked ledger for contextual quality coaching. Executable commands under `.codecraft/bin/` propose and resolve entries only through explicit workflow steps.

`.codecraft/bin/codecraft_run.py` manages the ignored active-run record used as compact, resumable workflow context. It routes AI and deterministic tools without replacing human approval, Git, signed receipts, or committed evidence.

`codecraft-starter/` is the versioned, self-contained Java/Maven distribution of the reusable workflow. Its installer separates distribution-managed machinery from project-owned agreements and evidence, provides conflict-safe upgrades, and includes clean-room acceptance tests.
