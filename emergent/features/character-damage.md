# Character Damage

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 2
- Behavior: Damage reduces the target's health.
- Arrange: A newly created Hero and Orc, with Hero at 1000 health and alive.
- Act: Hero receives 100 damage from Orc.
- Assert: Hero has 900 health and remains alive.

## Responsibility design

- Receiver job: `PlayerCharacter` maintains and changes its own state.
- Information owner: The receiving `PlayerCharacter` owns its health and life state.
- Decision owner: The receiving `PlayerCharacter` applies the approved damage amount.
- State owner: The receiving `PlayerCharacter`.
- Dependency abstraction: None required by this slice.
- Concrete implementation: `PlayerCharacter.receiveDamage` subtracts the damage amount from health.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `CharacterDamage_bdd` expected 900 health but observed 1000 because `receiveDamage` was a no-op.
- Focused red: `PlayerCharacterDamageTest` expected 900 health but observed 1000.

## Implementation

- Smallest behavior change: Subtract `damagePoints` from the receiver's health.
- Refactoring while green: None; the existing state owner already has the correct responsibility.

## Verification

- Targeted tests: `PlayerCharacterDamageTest` and `CharacterDamage_bdd` pass, 2 tests with 0 failures.
- Complete suite: Four active Java tests pass, one explicitly deferred legacy seed is skipped, and 53 Starter tests pass.
- Quality checks: `git diff --check` passes; no new abstraction or dependency was introduced.
- Completion lane and receipt: Behavior lane passed with receipt `sha256:da7a712ed851eb2ebbdd884267d9f0e7ee48cacbf723327ba4d3a2801a128c03`.

## Decisions and challenges

- Human decisions: Approved Element 2 and confirmed the exact expected outside red using alias `a`.
- Contextual coaching dispositions: Lethal damage, health clamping, self-damage, invalid damage amounts, healing, and levels remain deferred to separately approved slices.
- Challenges: Protected-path references in run metadata caused one redundant guard checkpoint; the first automated permission review for isolated verification timed out before the unchanged retry succeeded.
