# Self Healing

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 6
- Behavior: A living damaged character can heal itself by an approved amount.
- Arrange: Orc damages a newly created Hero from 1000 health to 900 health.
- Act: Hero heals itself for 50 health.
- Assert: Hero has 950 health and remains alive.

## Responsibility design

- Receiver job: `PlayerCharacter` maintains its own health and restores it when asked to heal itself.
- Information owner: The receiving `PlayerCharacter` owns its health and life state.
- Decision owner: No additional policy decision is required in this slice; the character applies the approved healing amount.
- State owner: The receiving `PlayerCharacter`.
- Dependency abstraction: None required by this slice.
- Concrete implementation: `PlayerCharacter.heal` adds the supplied health points to current health.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `CharacterHealing_bdd` failed at test compilation because `PlayerCharacter.heal(int)` did not exist.
- Focused red: Not separately captured; the public outside red had already isolated the same missing protocol, and the focused test was added with the minimal implementation before focused green.

## Implementation

- Smallest behavior change: Add `heal(int healthPoints)` to increase the character's health by the approved amount.
- Refactoring while green: None; health mutation remains cohesive with the existing state owner.

## Verification

- Targeted tests: `PlayerCharacterHealingTest` and `CharacterHealing_bdd` pass, 2 tests with 0 failures.
- Complete suite: Twelve active Java tests pass, one explicitly deferred legacy seed is skipped, and 55 Starter tests pass.
- Quality checks: No new abstraction, collaborator, injection point, or dependency was introduced.
- Completion lane and receipt: Final behavior lane passed with candidate digest `sha256:bfc57486ba72de43b5ab3bdc128050d9cb088c33fef0967b2a535991e3f29b50` after the plan and responsibility-map update.

## Decisions and challenges

- Human decisions: Approved Element 6 and confirmed the exact missing `heal(int)` outside red using alias `a`.
- Contextual coaching dispositions: Maximum-health capping, dead-character healing, healing other characters, magical objects, and zero or negative amounts remain deferred to separately approved slices.
- Challenges: A run-state-only compound command naming the newly protected BDD path was falsely blocked and was safely split into two unprotected routing updates. The focused red was not captured separately and is recorded as missing evidence rather than inferred.
