# Java Coverage Coaching

Date: 2026/10/01

Automation: coverage coaching 0.1.0; CodeCraft 0.10.0

## Intent

Turn JaCoCo's missed lines, branches, methods, and complexity into actionable design and testing feedback without introducing a coverage gate or encouraging tests written only to increase a percentage.

## Observed Pattern

- One missed branch in `MagicalObjectDurability.isDestroyed()` looks like a focused behavior-test opportunity.
- Seven wholly unexecuted methods may instead indicate missing behavior, unnecessary queries, or protocols broader than their clients need.
- Aggregate percentages make those distinct situations look alike and do not explain the appropriate response.

## Tests and Red Evidence

- The first focused run failed because `coach_java_coverage` did not exist.
- The Maven integration test then failed because no `coach-java-coverage` execution existed.
- A focused example distinguishes a changed-code decision gap, a wholly unexecuted baseline method, and partially uncovered lines.
- Independent review reproduced two deletion-only Git diff defects: an empty new-side range was ignored, and a fully deleted file could inherit the previous file's path. Exact focused regressions failed before each parser correction.
- Independent review also identified stale derived reports and ambiguous identifiers for same-line overloads; focused regressions failed before those corrections.
- Focused tests cover Git changed-line collection and parsing, deletion-only changes, deleted files, untracked files, changed-first prioritization, overload identity, signal classification, advisory grid and JSON output, stale-report cleanup, and Maven ordering before Habit Hooks.

## Implementation

- `.codecraft/bin/coach_java_coverage.py` reads method-level JaCoCo counters after report generation.
- Entirely unexecuted methods prompt a behavior-versus-API decision.
- Partially covered decisions prompt consideration of a focused behavioral test.
- Partially covered straight-line methods prompt consideration of a meaningful missing scenario.
- Git diff and untracked-file evidence classify findings as changed code or existing baseline; changed-code findings sort first.
- Deletion-only hunks mark their surviving-file anchor as changed, while completely deleted files cannot leak their hunks into another file.
- JVM method descriptors disambiguate overloaded methods in machine identifiers and the review grid.
- `java/pom.xml` runs the coach immediately before Habit Hooks during `verify`.
- Human-readable output is written to `java/target/site/codecraft-coverage-coaching/review-grid.md`; stable machine-readable findings are written to `findings.json`.
- The coach does not mutate the tracked review ledger. Codex records contextual findings only through the existing human review-decision workflow.

## Decisions

- Coverage findings never fail the build merely because code is uncovered.
- Tooling failures such as a missing or malformed JaCoCo report still fail closed.
- The coach identifies structural evidence but does not decide whether a test or design change is correct.
- Existing BDD protection and approval checkpoints remain unchanged.

## Verification

- Focused coverage-coaching tests: 8 passed.
- Focused metrics tests: 6 passed.
- Independent review: all deletion parsing, stale-output, and overload findings resolved; no release-blocking findings remain.
- Complete current-worktree verification: 95 Java tests and 103 workflow automation tests passed.
- Canonical command: `./mvnw verify`
- Final isolated completion evidence is held in the signed automation-lane receipt rather than copied into this artifact.

## Challenges

- A build must not mutate a tracked coaching ledger, so the coach creates derived review artifacts under `target/` and leaves durable dispositions to the explicit review workflow.
- Changed-method ranges are inferred from JaCoCo method start lines and the next method start; this is deterministic and intentionally conservative rather than a full Java parser. Same-line overloads share the changed classification but retain distinct descriptors.
