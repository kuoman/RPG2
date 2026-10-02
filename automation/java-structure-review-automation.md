# Java Structure Review Automation

Date: 2026/10/01

Automation: CodeCraft 0.5.0; structure review 0.1.0

## Intent

Detect recurring Java organization pressure early and require a collaborative architecture review without automatically moving files.

## Observed Pattern

- Forty-five completed roadmap behaviors produced 26 production types and 44 test types in one declared package.
- Stable responsibility clusters are visible for character interactions, character life, and magical objects.
- Package moves affect dependency direction and protected BDD assets, so unattended organization would be unsafe.

## Tests and Red Evidence

- The focused workflow suite initially failed because `review_java_structure` did not exist.
- The Maven-integration test then failed because no `review-java-structure` verify execution existed.
- Tests cover package inventory, behavior-count cadence, size thresholds, production dependency cycles, report rendering, and Maven integration.

## Implementation

- `.codecraft/bin/review_java_structure.py` reads declared packages, imports, roadmap completion, and the project-local policy.
- Check mode fails when review is due; `--report` always prints evidence without blocking.
- `java/pom.xml` runs check mode during every canonical verification.
- `.codecraft/structure-review.json` records the reviewed behavior count, cadence, and current file limits.
- CodeCraft 0.5.0 routes due findings through a collaborative green-refactor workflow.

## Decisions

- Review is due every three completed roadmap behaviors, on package-size overflow, or on a production package cycle.
- Automation reports structural facts but never moves files or selects boundaries.
- The initial limits of 30 production and 50 test files allowed the automation commit to remain green while the separately approved first package migration was prepared.
- The accepted package migration is complete, and the limits are now 12 production and 20 test files per package.
- Advancing the review baseline requires human agreement.

## Verification

- Focused structural-review tests: 6 passed.
- Complete workflow suite: 27 passed.
- Complete Java suite: 80 passed.
- Maven lifecycle: the structural inventory ran during `verify` and reported the baseline current.
- Quality checks: all enforced Habit Hooks checks passed.
- Canonical command: `./mvnw verify`

## First Review Outcome

- Production packages contain 8 character types, 10 character-life types, and 8 magic types.
- Test packages contain 16 character behaviors, 14 life behaviors, 6 magic behaviors, and 2–3 focused tests per production package.
- The production dependency graph is acyclic: `magic -> character -> character.life`.
- Seventy Java type bodies remained unchanged; only paths, package declarations, and required imports changed.

## Challenges

- The gate had to detect current pressure without making its own installation uncommittable. The automation increment therefore used explicit temporary limits, which this separate organization increment tightened after the package review.
