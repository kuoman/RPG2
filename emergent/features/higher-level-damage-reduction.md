# Higher-Level Damage Reduction

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 11
- Behavior: Damage is reduced by 10% for each level the target is above the attacker, capped at 50%, with fractional modified damage rounded down.
- Arrange: Create level 1 Attacker and level 7 Target with 1000 current health.
- Act: Target receives 95 requested damage from Attacker.
- Assert: The six-level reduction is capped at 50%, 47.5 applied damage rounds down to 47, and Target remains alive with 953 health.

## Responsibility design

- Receiver job: `PlayerCharacter` compares its level with the attacker, determines the applied damage, and changes its own health and life state.
- Information owner: Each `PlayerCharacter` owns its level; the target owns its health and life state.
- Decision owner: The target's `receiveDamage` behavior owns the higher-level reduction, cap, and integer-rounding decisions.
- State owner: The target `PlayerCharacter`.
- Dependency abstraction: None required by this slice.
- Concrete implementation: Positive target level advantage reduces requested damage by 10% per level up to 50%; integer arithmetic rounds the final applied damage down.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `HigherLevelDamageReduction_bdd` expected Target at 953 health but unchanged production reported 905 because it applied all 95 requested damage.
- Focused red: The one-level case expected health 915 but received 905; the six-level cap case expected 950 but received 900.

## Implementation

- Smallest behavior change: Before applying damage, calculate a reduction only when the target is above the attacker, cap it at 50%, and use integer division for round-down behavior.
- Refactoring while green: None; the existing target-owned damage protocol remains cohesive and unchanged.

## Verification

- Targeted tests: The higher-level behavior plus existing normal, lethal, depleting, and self-damage regression set passes, 11 tests with 0 failures.
- Complete suite: Twenty-three active Java tests pass, one explicitly deferred legacy seed is skipped, and 55 Starter tests pass.
- Quality checks: No public protocol, collaborator, interface, injection point, lower-level damage increase, or unrelated progression rule was introduced.
- Completion lane and receipt: Final behavior lane passed with candidate digest `sha256:54f037c42562825aa6fdf3db2f183eee4aee561b34e4f42bd5b2605751d72c5c` after the plan and responsibility-map update.

## Decisions and challenges

- Human decisions: Approved Element 11, the 50% cap example, and round-down integer damage using alias `a`; then confirmed the exact 905-health outside red using alias `a`.
- Contextual coaching dispositions: Increased damage against lower-level targets and any shared modifier extraction remain deferred until the next separately approved slice creates real design pressure.
- Challenges: The calculation is guarded by positive target level advantage so equal- and lower-level targets retain the previously approved damage behavior.
