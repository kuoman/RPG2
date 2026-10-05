# Lower-Level Damage Increase

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 12
- Behavior: Damage is increased by 10% for each level the target is below the attacker, capped at 50%, with fractional modified damage rounded down.
- Arrange: Create level 7 Attacker and level 1 Target with 1000 current health.
- Act: Target receives 95 requested damage from Attacker.
- Assert: The six-level increase is capped at 50%, 142.5 applied damage rounds down to 142, and Target remains alive with 858 health.

## Responsibility design

- Receiver job: `PlayerCharacter` compares its level with the attacker, determines the applied damage, and changes its own health and life state.
- Information owner: Each `PlayerCharacter` owns its level; the target owns its health and life state.
- Decision owner: The target's `receiveDamage` behavior owns the relative-level modifier, cap, and integer-rounding decisions.
- State owner: The target `PlayerCharacter`.
- Dependency abstraction: None required by this slice.
- Concrete implementation: A private signed level-difference calculation reduces or increases requested damage by 10% per level, caps the difference at five levels, and uses integer arithmetic to round final applied damage down.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `LowerLevelDamageIncrease_bdd` expected Target at 858 health but production reported 905 because it applied only the requested 95 damage.
- Focused red: The one-level case expected health 896 but received 905; the six-level cap case expected 850 but received 900.

## Implementation

- Smallest behavior change: Add the missing attacker-level-advantage branch, increasing requested damage by 10% per level up to 50% with integer round-down.
- Refactoring while green: Consolidated the mirrored increase and reduction branches into one private signed level-difference calculation without changing the public protocol.

## Verification

- Targeted tests: Both level modifiers plus existing normal, lethal, depleting, and self-damage regression tests pass, 14 tests with 0 failures.
- Complete suite: Twenty-six active Java tests pass, one explicitly deferred legacy seed is skipped, and 55 Starter tests pass.
- Quality checks: No public protocol, collaborator, interface, injection point, or unrelated progression rule was introduced; equal-level damage retains its direct path.
- Completion lane and receipt: Final behavior lane passed with candidate digest `sha256:3bf3f5b5ef2b085943e299b4c47667d0300c87a513beb127c4744f49314043fc` after the plan and responsibility-map update.

## Decisions and challenges

- Human decisions: Approved Element 12 and reuse of the established round-down policy using alias `a`; then confirmed the exact 905-health outside red and authorized private consolidation using alias `a`.
- Contextual coaching dispositions: Level eligibility, damage/faction progression, current-health refill, temporary level loss, and invalid damage amounts remain deferred to separately approved slices.
- Challenges: The signed calculation preserves equal-level damage exactly while expressing capped reduction and increase without duplicated branches.
