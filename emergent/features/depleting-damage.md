# Depleting Damage

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 4
- Behavior: Damage equal to current health kills the target.
- Arrange: A newly created Hero at 1000 health and alive, with an Orc attacker.
- Act: Hero receives exactly 1000 damage from Orc.
- Assert: Hero has 0 health and is dead.

## Responsibility design

- Receiver job: `PlayerCharacter` maintains its own state and enforces the lethal-health boundary.
- Information owner: The receiving `PlayerCharacter` owns its health and life state.
- Decision owner: The receiving `PlayerCharacter` decides whether damage equals or exceeds its current health.
- State owner: The receiving `PlayerCharacter`.
- Dependency abstraction: None required by this slice.
- Concrete implementation: `PlayerCharacter.receiveDamage` uses an inclusive lethal comparison.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `DepletingDamage_bdd` expected 0 health/dead but observed 0 health/alive.
- Focused red: `PlayerCharacterDepletingDamageTest` expected dead but observed alive.

## Implementation

- Smallest behavior change: Change the lethal comparison from `>` to `>=`.
- Refactoring while green: None; the existing state owner already has the correct responsibility.

## Verification

- Targeted tests: `PlayerCharacterDepletingDamageTest` and `DepletingDamage_bdd` pass, 2 tests with 0 failures.
- Complete suite: Eight active Java tests pass, one explicitly deferred legacy seed is skipped, and 53 Starter tests pass.
- Quality checks: No new abstraction or dependency was introduced.
- Completion lane and receipt: Behavior lane passed with receipt `sha256:bad988e1104b831cc42ad871ceb2d62500290adb2cd2470341546690159a3a03`.

## Decisions and challenges

- Human decisions: Approved Element 4 and confirmed the exact expected outside red using alias `a`.
- Contextual coaching dispositions: Self-damage, already-dead targets, invalid damage amounts, healing, and levels remain deferred to separately approved slices.
- Challenges: None beyond the expected boundary-value red/green cycle.
