# Responsibility-Driven CodeCraft

Date: 2026/09/30

Version: 0.4.0

## Intent

Make responsibility ownership an explicit part of BDD design and green-code review instead of relying on structural quality checks to detect overloaded objects later.

## Changes

- Added responsibility questions before BDD approval and after every green feature.
- Added a provisional responsibility map for learned object jobs and open ownership questions.
- Standardized BDD proposals as numbered grids with `Behavior`, `Arrange`, `Act`, and `Assert` columns.
- Kept exact Java source and expected-red evidence keyed to each grid Element Number.
- Added optional Beyond Compare review for modifications to existing code or tests.
- Required batch execution to stop when responsibility learning invalidates a later approved entry.

## Decisions

- Semantic responsibility remains a collaborative design judgment rather than an enforced static rule.
- Public domain messages may remain on coordinating objects while their implementation delegates to the knowledge owner.
- Visual diff review never substitutes for protected-asset approval.

## Verification

- Canonical command: `./mvnw verify`
- Result: 33 Java tests and 21 workflow tests passed; Habit Hooks passed
- Beyond Compare availability: application found in the user's Applications directory without launching it

## Challenges

- The workflow must preserve exact-source protection while presenting proposals in a human-scannable grid, so source and red evidence remain keyed details beneath the grid.
