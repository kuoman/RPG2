# Starting Level

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 9
- Behavior: A new character starts at level 1 with maximum health 1000.
- Arrange: Create Hero and a character printer.
- Act: Render Hero's progression state.
- Assert: The result is `Hero is level 1 with maximum health 1000.`

## Responsibility design

- Receiver job: `PlayerCharacter` initializes and owns its level and current maximum health.
- Information owner: `PlayerCharacter` owns level and maximum health; its immutable `Status` snapshot carries their observed values.
- Decision owner: No progression decision occurs in this slice; construction establishes the required starting values.
- State owner: `PlayerCharacter`.
- Dependency abstraction: None required by this slice.
- Concrete implementation: Construction sets level to 1 and maximum health to 1000; `Status` exposes both, and `PlayerCharacterPrinter.printProgression` renders them.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `CharacterLevel_bdd` failed at test compilation because `PlayerCharacterPrinter.printProgression(PlayerCharacter)` did not exist.
- Focused red: `PlayerCharacterLevelTest` failed at test compilation because `Status.level()` and `Status.maximumHealth()` did not exist; the approved BDD still reported the missing printer method.

## Implementation

- Smallest behavior change: Initialize level at 1, append level and maximum health to the immutable status snapshot, and add separate progression rendering.
- Refactoring while green: Updated the existing state test for the expanded snapshot; existing health/life rendering and protected output stayed unchanged.

## Verification

- Targeted tests: The focused and public starting-level tests plus both prior creation tests pass, 4 tests with 0 failures.
- Complete suite: Eighteen active Java tests pass, one explicitly deferred legacy seed is skipped, and 55 Starter tests pass.
- Quality checks: No level-gain policy, collaborator, interface, injection point, or mutable state exposure was introduced.
- Completion lane and receipt: Final behavior lane passed with candidate digest `sha256:0021e80f385b0b145c720d15e34ad2d83fae55aa0c2a8de4fc396a6e7f49700a` after the plan and responsibility-map update.

## Decisions and challenges

- Human decisions: Approved Element 9 and confirmed the exact missing progression-rendering outside red using alias `a`.
- Contextual coaching dispositions: Level gain, maximum-health growth, damage scaling, progression counters, and temporary level loss remain deferred to separately approved slices.
- Challenges: The separate progression format preserved all existing protected approval strings while reusing the established immutable snapshot boundary.
