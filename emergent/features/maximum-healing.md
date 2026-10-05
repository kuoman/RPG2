# Maximum Healing

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 7
- Behavior: Healing cannot raise a character above its current maximum health.
- Arrange: Orc damages a newly created Hero from 1000 health to 900 health.
- Act: Hero attempts to heal itself for 200 health.
- Assert: Hero stops at 1000 health and remains alive.

## Responsibility design

- Receiver job: `PlayerCharacter` maintains its own health and prevents healing above its current maximum.
- Information owner: The receiving `PlayerCharacter` owns current health, current maximum health, and life state.
- Decision owner: The receiving `PlayerCharacter` decides the allowed post-healing health from its maximum boundary.
- State owner: The receiving `PlayerCharacter`.
- Dependency abstraction: None required by this slice.
- Concrete implementation: `PlayerCharacter.heal` assigns the lower of current maximum health or current health plus the supplied amount.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `MaximumHealing_bdd` expected 1000 health/alive but observed 1100 health/alive.
- Focused red: `PlayerCharacterMaximumHealingTest` expected health 1000 but observed 1100.

## Implementation

- Smallest behavior change: Store current maximum health at 1000, initialize health from it, and clamp healing with that owned boundary.
- Refactoring while green: None; the boundary belongs with the health state it protects.

## Verification

- Targeted tests: The focused and public maximum-healing tests plus both prior healing tests pass, 4 tests with 0 failures.
- Complete suite: Fourteen active Java tests pass, one explicitly deferred legacy seed is skipped, and 55 Starter tests pass.
- Quality checks: No public level protocol, policy abstraction, collaborator, injection point, or dependency was introduced.
- Completion lane and receipt: Final behavior lane passed with candidate digest `sha256:1bf937c3e85d3a6a79754c8e9ce8610a69489607eb5da7a5fb4bd94a26b2963d` after the plan and responsibility-map update.

## Decisions and challenges

- Human decisions: Approved Element 7 with alias `a` after one malformed `1a` response was rejected, then confirmed the exact 1100-health outside red with alias `a`.
- Contextual coaching dispositions: Dead-character healing, levels and level-based maximum growth, healing other characters, magical objects, and zero or negative amounts remain deferred to separately approved slices.
- Challenges: The malformed response was correctly treated as non-authorization. The focused red was captured separately before production implementation.
