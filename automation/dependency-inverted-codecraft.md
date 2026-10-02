# Dependency-Inverted CodeCraft

Date: 2026/09/30

Version: 0.4.1

## Intent

Correct the responsibility-driven workflow so it inspects construction ownership and dependency direction, not only behavior and state ownership.

## Observed Gap

The first proposed `Health` extraction delegated health behavior but instantiated the collaborator inside `PlayerCharacter`. The workflow did not explicitly ask who constructed separately responsible collaborators or where concrete implementation selection belonged.

## Changes

- Added a mandatory five-principle SOLID review.
- Added dependency protocol, injection point, concrete implementation, and composition-root questions.
- Added a pure-refactoring checkpoint beginning and ending green.
- Distinguished separately responsible collaborators from legitimate internally owned values and collections.
- Expanded the feature artifact template to record dependency direction explicitly.
- Updated the responsibility map with the approved dependency-inverted health direction.

## Decisions

- Policy objects receive collaborators instead of constructing implementations with separate domain jobs.
- Concrete implementations and configuration values are selected at an external factory or composition root.
- Interfaces must express cohesive client-used protocols rather than exist only to satisfy a mechanical rule.

## Verification

- Canonical command: `./mvnw verify`
- Result: 33 Java tests and 21 workflow tests passed; Habit Hooks passed

## Challenges

- The constructor migration affects protected BDD tests and therefore remains subject to exact, single-use review and approval after the workflow correction is committed.
