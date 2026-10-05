# Lethal Damage

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 3
- Behavior: Overkill damage clamps health and kills the target.
- Arrange: A newly created Hero at 1000 health and alive, with an Orc attacker.
- Act: Hero receives 1500 damage from Orc.
- Assert: Hero has 0 health and is dead.

## Responsibility design

- Receiver job: `PlayerCharacter` maintains its own state and enforces the overkill boundary.
- Information owner: The receiving `PlayerCharacter` owns its health and life state.
- Decision owner: The receiving `PlayerCharacter` decides whether damage exceeds its current health.
- State owner: The receiving `PlayerCharacter`.
- Dependency abstraction: None required by this slice.
- Concrete implementation: `PlayerCharacter.receiveDamage` clamps health to 0 and marks the receiver dead when damage exceeds current health.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `LethalDamage_bdd` expected 0 health/dead but observed -500 health/alive.
- Focused red: `PlayerCharacterLethalDamageTest` expected 0 health but observed -500.

## Implementation

- Smallest behavior change: Branch only when damage exceeds current health; clamp health to 0 and set alive to false, otherwise retain ordinary subtraction.
- Refactoring while green: None; the existing state owner already has the correct responsibility.

## Verification

- Targeted tests: `PlayerCharacterLethalDamageTest` and `LethalDamage_bdd` pass, 2 tests with 0 failures.
- Complete suite: Six active Java tests pass, one explicitly deferred legacy seed is skipped, and 53 Starter tests pass.
- Quality checks: No new abstraction or dependency was introduced.
- Completion lane and receipt: Behavior lane passed with receipt `sha256:747c918c194687b7fc448fb2fef8e2b29057212363bc2f4bd148a684199f2302`.

## Decisions and challenges

- Human decisions: Approved Element 3 and confirmed the exact expected outside red using alias `a`.
- Contextual coaching dispositions: Exact-health depletion, self-damage, already-dead targets, invalid damage amounts, healing, and levels remain deferred to separately approved slices.
- Challenges: None beyond the expected outside-red and focused-red cycles; non-protected run context avoided the redundant metadata approval seen previously.
