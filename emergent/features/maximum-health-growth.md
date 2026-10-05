# Maximum Health Growth

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 10
- Behavior: Each additional level increases maximum health by 100.
- Arrange: Create Hero at level 1 with maximum health 1000 and capture that progression state.
- Act: Hero gains one already-authorized level.
- Assert: Hero is level 2 with maximum health 1100.

## Responsibility design

- Receiver job: `PlayerCharacter` advances its level and maximum health together after a level gain has already been authorized.
- Information owner: `PlayerCharacter` owns level and maximum health; its immutable `Status` snapshot carries their observed values.
- Decision owner: `PlayerCharacter` decides the synchronized state transition, while eligibility for gaining a level remains outside this slice.
- State owner: `PlayerCharacter`.
- Dependency abstraction: None required by this slice.
- Concrete implementation: Package-private `gainLevel()` increments level once and maximum health by 100 without changing current health.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `MaximumHealthGrowth_bdd` failed at test compilation because `PlayerCharacter.gainLevel()` did not exist.
- Focused red: `PlayerCharacterMaximumHealthGrowthTest` and the approved BDD both failed at test compilation because `gainLevel()` did not exist.

## Implementation

- Smallest behavior change: Add one package-private transition that increments level and maximum health together.
- Refactoring while green: None; the existing state owner and immutable observation boundary remain cohesive.

## Verification

- Targeted tests: Starting progression and maximum-health growth focused/public tests pass, 4 tests with 0 failures.
- Complete suite: Twenty active Java tests pass, one explicitly deferred legacy seed is skipped, and 55 Starter tests pass.
- Quality checks: No eligibility policy, collaborator, public leveling command, interface, injection point, health refill, or unrelated progression rule was introduced.
- Completion lane and receipt: Final behavior lane passed with candidate digest `sha256:081f07821b4e77204524da63eb3f712273b36d3e08e5263126f793d4d85a2452` after the plan and responsibility-map update.

## Decisions and challenges

- Human decisions: Approved Element 10 and confirmed the exact missing-`gainLevel()` outside red using alias `a`.
- Contextual coaching dispositions: Level eligibility, damage/faction progression, current-health refill on level gain, damage scaling, and temporary level loss remain deferred to separately approved slices.
- Challenges: A package-private transition models an already-decided level gain without exposing arbitrary public leveling or prematurely choosing an eligibility mechanism.
