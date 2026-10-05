# Self Damage Prevention

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 5
- Behavior: A character cannot damage itself.
- Arrange: A newly created Hero at 1000 health and alive.
- Act: Hero attempts to deal itself 100 damage.
- Assert: Hero remains at 1000 health and alive.

## Responsibility design

- Receiver job: `PlayerCharacter` maintains its own state and rejects self-inflicted damage.
- Information owner: The receiving `PlayerCharacter` owns its health, life state, and object identity.
- Decision owner: The receiving `PlayerCharacter` decides whether the attacker is itself before applying damage.
- State owner: The receiving `PlayerCharacter`.
- Dependency abstraction: None required by this slice.
- Concrete implementation: `PlayerCharacter.receiveDamage` returns without mutation when the attacker is the receiver.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `SelfDamage_bdd` expected 1000 health/alive but observed 900 health/alive.
- Focused red: `PlayerCharacterSelfDamageTest` expected 1000 health but observed 900.

## Implementation

- Smallest behavior change: Return from `receiveDamage` when the attacker reference is identical to the receiver.
- Refactoring while green: None; the invariant belongs with the existing state owner.

## Verification

- Targeted tests: `PlayerCharacterSelfDamageTest` and `SelfDamage_bdd` pass, 2 tests with 0 failures.
- Complete suite: Ten active Java tests pass, one explicitly deferred legacy seed is skipped, and 55 Starter tests pass.
- Quality checks: No new abstraction, collaborator, injection point, or dependency was introduced.
- Completion lane and receipt: Behavior lane passed with final receipt `sha256:880b13cc62f84293f1ae11f8f41ce0962668b26c980a420182cc5197c830b282` after the plan and responsibility-map update.

## Decisions and challenges

- Human decisions: Approved Element 5 and confirmed the exact expected outside red using alias `a`.
- Contextual coaching dispositions: Same-named distinct characters, already-dead targets, invalid damage amounts, healing, and levels remain deferred to separately approved slices.
- Challenges: Read-only regex alternation and protected run-context paths caused guard false positives; both were rerouted without adding human checkpoints or changing behavior scope.
