# Prevent Ally Damage

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 17
- Behavior: Allies cannot damage one another.
- Arrange: Create Hero and Companion, join both to the same named Knights faction identity, and capture Hero's initial printed state.
- Act: Companion attempts to deal 100 damage to Hero.
- Assert: Hero remains alive at 1000 health.

## Responsibility design

- Receiver job: `PlayerCharacter` decides whether to admit incoming character damage before scaling or mutating health.
- Information owner: Each `PlayerCharacter` owns its faction memberships, health, and life state; `Faction` supplies shared identity.
- Decision owner: The receiving character rejects damage when its established alliance query recognizes the attacker as an ally.
- State owner: The receiving character retains ownership of health and life state, which remain unchanged for allied damage.
- Dependency abstraction: None required by this slice.
- Concrete implementation: Extend the existing early-return guard in `receiveDamage` with `isAlliedWith(enemy)`.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `AllyDamage_bdd` produced the approved mismatch: expected Hero at 1000 health, but unchanged production reported 900 health.
- Focused red: `PlayerCharacterAllyDamageTest` failed with expected health 1000 and actual health 900; no production change preceded the run.

## Implementation

- Smallest behavior change: Return from `receiveDamage` when the attacker shares any faction identity with the receiver.
- Refactoring while green: None; the established alliance query already owns the membership-intersection decision.

## Verification

- Targeted tests: `PlayerCharacterAllyDamageTest` and `AllyDamage_bdd` pass, 2 tests with 0 failures.
- Complete suite: Thirty-six active Java tests pass, one explicitly deferred legacy seed is skipped, and 55 Starter tests pass.
- Quality checks: Damage admission precedes level scaling and health mutation; self-damage and non-allied damage behavior remain intact, with no healing, equality, progression, or magical-object behavior introduced.
- Completion lane and receipt: Final isolated behavior lane passed with candidate digest `sha256:b73eef2eaa8fe139d733ced234400a9a08f7d52fb704483c053b25dad0278c5e` after the plan and responsibility-map update.

## Decisions and challenges

- Human decisions: Approved the shared-Knights damage scenario, exact unchanged-health output, and predicted 900-health outside red using alias `a`; then confirmed the observed mismatch and authorized generated-output cleanup, one focused test, and the minimal damage guard using alias `a`.
- Contextual coaching dispositions: Self-alliance, same-name faction equality, explicit non-alliance, ally healing, non-ally healing, faction history/progression, and magical objects remain deferred to separately approved slices.
- Challenges: Reusing `isAlliedWith` keeps faction membership encapsulated and makes damage admission explicit without adding a collaborator or exposing the membership collection.
