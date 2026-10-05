# Dead Character Healing

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 8
- Behavior: A dead character cannot heal itself.
- Arrange: Orc deals 1000 damage to Hero, leaving Hero at 0 health and dead.
- Act: Hero attempts to heal itself for 100 health.
- Assert: Hero remains at 0 health and dead.

## Responsibility design

- Receiver job: `PlayerCharacter` maintains its health and refuses healing while dead.
- Information owner: The receiving `PlayerCharacter` owns health, current maximum health, and life state.
- Decision owner: The receiving `PlayerCharacter` decides whether its life state permits healing.
- State owner: The receiving `PlayerCharacter`.
- Dependency abstraction: None required by this slice.
- Concrete implementation: `PlayerCharacter.heal` returns without mutation when the character is not alive.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `DeadCharacterHealing_bdd` expected 0 health/dead but observed 100 health/dead.
- Focused red: `PlayerCharacterDeadHealingTest` expected health 0 but observed 100.

## Implementation

- Smallest behavior change: Return from `heal(int)` before changing health when `alive` is false.
- Refactoring while green: None; health and life state already belong to the same cohesive state owner.

## Verification

- Targeted tests: The focused and public dead-healing tests plus four prior healing tests pass, 6 tests with 0 failures.
- Complete suite: Sixteen active Java tests pass, one explicitly deferred legacy seed is skipped, and 55 Starter tests pass.
- Quality checks: No resurrection behavior, collaborator, policy abstraction, injection point, or dependency was introduced.
- Completion lane and receipt: Final behavior lane passed with candidate digest `sha256:1eafd15afed1cab2eb52832ee6d2509df6d8ca2e65260fdf02cc2a1322cc7037` after the plan and responsibility-map update.

## Decisions and challenges

- Human decisions: Approved Element 8 and confirmed the exact 100-health-while-dead outside red using alias `a`.
- Contextual coaching dispositions: Resurrection, healing other characters, damage after death, levels, magical objects, and zero or negative amounts remain deferred to separately approved slices.
- Challenges: The focused red was captured separately before production implementation; no workflow exception was needed.
