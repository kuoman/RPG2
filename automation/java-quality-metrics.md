# Java Quality Metrics

Date: 2026/10/01

Automation: coverage visibility 0.1.0

## Intent

Make Java coverage, complexity, size, and test-suite composition visible on every canonical verification without introducing a quality gate.

## Metrics

| Metric | Definition |
| --- | --- |
| Line coverage | JaCoCo covered and coverable executable source lines |
| Branch coverage | JaCoCo covered and total `if` and `switch` branches |
| Cyclomatic complexity | JaCoCo total, covered, and missed McCabe complexity |
| Physical production lines | All text lines, including blank lines, in production `.java` files |
| Unit tests | Surefire test cases from current test source classes not ending in `_bdd` |
| BDD tests | Surefire test cases from current test source classes ending in `_bdd` |

## Tests and Red Evidence

- The first focused run failed because the metrics reporter did not exist.
- The Maven integration test then failed because no JaCoCo report execution existed.
- The first complete build exposed a misplaced metrics execution under the dependency plugin; the integration test was tightened to verify plugin ownership before the POM was corrected.
- A stale Surefire report reproduced test-count inflation, and focused regressions now ensure generated inputs and owned derived reports are cleared before a run while removed test classes are ignored.
- An independent review found that stale reports for still-present classes could still inflate counts, that the initial physical-line baseline included an unrelated working-tree edit, and that report ordering depended on POM order. All three findings were resolved before completion.
- The focused suite covers counter parsing, source and test classification, deterministic JSON and Markdown output, missing-report failure, stale-input cleanup, stale-report handling, Maven lifecycle ordering, and absence of the JaCoCo `check` goal.

## Implementation

- JaCoCo 0.8.15 instruments the Java tests and writes HTML, XML, and CSV reports during `verify`.
- `.codecraft/bin/report_java_metrics.py` combines JaCoCo XML, current Surefire XML, and current Java source files.
- A `validate`-phase preparation removes only the prior JaCoCo execution data, Surefire `TEST-*.xml` inputs, and owned JaCoCo, metrics, and coverage-coaching report directories before the current tests execute.
- JaCoCo writes its report during `prepare-package`; summary generation remains in `verify`, so lifecycle phase ordering does not depend on plugin declaration order.
- The summary is printed during Maven verification and written to `java/target/site/codecraft-metrics/README.md` and `metrics.json`.
- The detailed browsable report is written to `java/target/site/jacoco/index.html`.
- No coverage threshold or JaCoCo `check` execution is configured.

## Baseline

| Metric | Result |
| --- | ---: |
| Line coverage | 95.24% (180/189) |
| Branch coverage | 97.83% (45/46) |
| Cyclomatic complexity | 110 total; 102 covered; 8 missed |
| Production source | 656 physical lines in 27 files |
| Unit tests | 49 |
| BDD tests | 46 |
| Total tests | 95 |

## Verification

- Focused metrics automation tests: 6 passed.
- Complete Java suite: 95 passed.
- Complete workflow automation suite: 95 passed.
- Independent review: three findings resolved before the final gate.
- The automation completion lane ran `./mvnw verify` successfully against isolated `HEAD` plus only this increment.
- Habit Hooks: all enforced checks passed.

## Decisions

- Coverage remains informational; a declining percentage does not fail verification.
- Both physical and coverable line counts are shown because they answer different questions.
- Test counts describe executed test cases, not test source files.
- Baseline values come from isolated verification of `HEAD` plus only this automation increment.
- Reports are derived artifacts under `target/` and are not committed.

## Challenges

- Canonical verification does not run Maven's `clean` phase, so old coverage, Surefire inputs, and derived reports can survive. Preparation narrowly removes those owned generated paths, and the reporter additionally filters results against current test source class names.
