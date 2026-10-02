# Align NCSS Threshold

Date: 2026/09/29

## Intent

Make the enforced PMD method-size threshold match the working agreement's allowance of at most seven executable lines.

## Approach

1. Reproduced the Habit Hooks failure on a method containing exactly seven executable statements.
2. Ran PMD directly to observe its reported NCSS count.
3. Added a workflow-automation regression test that pins the required PMD threshold.
4. Corrected the threshold and reran the focused automation test, direct PMD check, and canonical build.

## Test-First Evidence

- The new quality-rules test expected the agreement-aligned threshold and failed against the existing value.
- Direct PMD evidence showed that a method declaration plus seven executable statements has NCSS 8.
- PMD's threshold is inclusive, so a value of 9 permits NCSS 8 while rejecting NCSS 9.

## Implementation

- Changed `NcssCount.methodReportLevel` from 7 to 9.
- Added `test_quality_rules.py` to prevent the off-by-two configuration error from returning.

## Verification

- Focused automation test: 1 passing
- Direct PMD check of the seven-statement scenario: passing
- Complete suite: 21 Java tests passing
- Workflow automation: 20 tests passing
- Habit Hooks: all enforced checks passing
- Canonical command: `./mvnw verify`

## Decisions

- The agreement counts executable lines; PMD NCSS additionally counts the method declaration.
- The quality rule was corrected instead of extracting a mechanical helper from a cohesive test scenario.

## Challenges

- PMD's inclusive threshold required direct execution to distinguish threshold 8 from the correct value 9.
