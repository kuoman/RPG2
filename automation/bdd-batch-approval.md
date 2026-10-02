# Finite BDD Batch Approval

Date: 2026/09/29
Automation: CodeCraft feature cycle 0.3.0

## Intent

Reduce repetitive approval interruptions without weakening the human checkpoint around high-level behavior tests.

## Approved Design

- A batch is finite, ordered, exact-source, and single-use.
- Its protected manifest records each scenario's public API, behavioral Act, assertions, complete test source, and expected red evidence.
- The hook denies unapproved, altered, replayed, and out-of-order BDD creation.
- The expected-red verifier runs only the approved BDD class and accepts only its declared failure.
- An accepted expected red permits continuation without another human pause.
- Each feature is completed, fully verified, and committed green before the next batch entry begins.
- Any unexpected green, different red, source difference, API change, assertion change, or order change pauses the workflow for collaboration.

## First Batch

`healing-basics-1` contains three already approved behaviors:

1. A living character heals itself.
2. Healing stops at maximum health.
3. A dead character cannot heal.

## Implementation

- Expanded `.codecraft/hooks/protect_bdd.py` to recognize and consume exact next batch entries.
- Added `.codecraft/bin/run_bdd_red.py` for deterministic expected-red verification.
- Added the protected `.codecraft/bdd-batches/healing-basics-1.json` manifest.
- Expanded the CodeCraft skill and feature cycle to version 0.3.0.
- Made batch manifests read-only in the normal CodeCraft sandbox.

## Test-First Evidence

The first automation run failed because batch authorization, consumption, manifest protection, and the expected-red runner did not exist. The smallest implementation then made all 19 automation tests pass.

## Challenges and Decisions

- Blanket approval would permit behavior beyond what the human reviewed, so it remains prohibited.
- A path-only allowlist would permit silent assertion changes, so approval includes exact source.
- Absolute patch paths are normalized to their project-relative manifest paths and covered by a regression test.
- A failing command alone cannot distinguish intended red from unrelated breakage, so the verifier checks declared output fragments.
- Project hook changes require a fresh trusted Codex session before they can be relied upon as an active security boundary.
