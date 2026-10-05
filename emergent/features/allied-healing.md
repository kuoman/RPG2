# Allied Healing

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 18
- Behavior: Allies can heal one another.
- Arrange: Damage Hero from 1000 to 900 health through Orc, then join Hero and Companion to the same named Knights faction identity.
- Act: Companion heals Hero by 50.
- Assert: Hero has 950 health and remains alive.

## Responsibility design

- Receiver job: The healing `PlayerCharacter` coordinates a request for another character to restore health.
- Information owner: The target `PlayerCharacter` owns health, life state, and maximum health; each character owns its faction memberships.
- Decision owner: The target retains the established living-state and maximum-health restoration decisions. Non-ally admission remains Element 19.
- State owner: The target alone changes its health through its existing `heal(int)` behavior.
- Dependency abstraction: None required by this slice.
- Concrete implementation: Overload `heal` with a target character and amount, then tell the target to apply its existing healing behavior.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `AllyHealing_bdd` failed test compilation because `PlayerCharacter.heal(PlayerCharacter, int)` did not exist.
- Focused red: `PlayerCharacterAllyHealingTest` failed test compilation for the same missing overload; no production change preceded the run.

## Implementation

- Smallest behavior change: Add `PlayerCharacter.heal(PlayerCharacter, int)` and delegate the amount to the target's existing `heal(int)` method.
- Refactoring while green: None; delegation preserves the target's cohesive ownership of health boundaries without duplicating restoration rules.

## Verification

- Targeted tests: `PlayerCharacterAllyHealingTest` and `AllyHealing_bdd` pass, 2 tests with 0 failures.
- Complete suite: Thirty-eight active Java tests pass, one explicitly deferred legacy seed is skipped, and 55 Starter tests pass.
- Quality checks: The target continues to enforce living-state and maximum-health constraints; no non-ally rejection, self-healing change, damage change, faction equality, progression, or magical-object behavior was introduced.
- Completion lane and receipt: Final isolated behavior lane passed with candidate digest `sha256:4d8645e6364e69341ab6cfa4b5b77eeb00c9d07c15806d97d66c0849ae0f7621` after the plan and responsibility-map update.

## Decisions and challenges

- Human decisions: Approved the allied-healing scenario, exact 900-to-950 output, and predicted missing-overload outside red using alias `a`; then confirmed the observed red and authorized one focused test plus only the delegation overload using alias `a`.
- Contextual coaching dispositions: Non-ally healing rejection, changes to self-healing, dead-target healing changes, faction equality, faction progression, damage behavior, and magical objects remain deferred to separately approved slices.
- Challenges: The positive behavior introduces the character-to-character protocol without preempting Element 19; the next behavior must add the alliance-admission rule before non-allied healing is considered complete.
