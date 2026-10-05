# Leave One Faction

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 15
- Behavior: A character can leave one faction without affecting another membership.
- Arrange: Create Hero plus named Knights and Mages factions, then join Hero to both.
- Act: Hero leaves Knights.
- Assert: Hero no longer belongs to Knights and still belongs to Mages.

## Responsibility design

- Receiver job: `PlayerCharacter` accepts a faction to leave and changes its own memberships.
- Information owner: `Faction` owns its name and identity; `PlayerCharacter` owns its faction memberships.
- Decision owner: `PlayerCharacter.leave(Faction)` decides how the supplied identity is removed without disturbing other memberships.
- State owner: `PlayerCharacter` owns and mutates the membership set.
- Dependency abstraction: None required by this slice.
- Concrete implementation: Remove the supplied `Faction` from the existing identity-based set.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `CharacterLeavesFaction_bdd` failed test compilation because `PlayerCharacter.leave(Faction)` did not exist.
- Focused red: `PlayerCharacterFactionLeavingTest` failed test compilation for the same missing command; no production change preceded the run.

## Implementation

- Smallest behavior change: Add `PlayerCharacter.leave(Faction)` and remove the supplied faction from the character's existing membership set.
- Refactoring while green: None; the command belongs with the membership state already owned by `PlayerCharacter`.

## Verification

- Targeted tests: `PlayerCharacterFactionLeavingTest` and `CharacterLeavesFaction_bdd` pass, 2 tests with 0 failures.
- Complete suite: Thirty-two active Java tests pass, one explicitly deferred legacy seed is skipped, and 55 Starter tests pass.
- Quality checks: Other membership identities remain intact; no behavior for leaving an unjoined faction, same-name equality, allies, healing, progression, or magical objects was introduced.
- Completion lane and receipt: Final behavior lane passed with candidate digest `sha256:e52d5d9cfde75f48a9b2af3fd56267098d7203b978c757688b5abad581ab193b` after the plan and responsibility-map update.

## Decisions and challenges

- Human decisions: Approved the leave-one-preserve-one scenario, exact output, and missing-leave outside red using alias `a`; then confirmed that red and authorized the focused test plus minimal implementation using alias `a`.
- Contextual coaching dispositions: Leaving an unjoined faction, same-name faction equality, allies, ally damage/healing, non-ally healing, lifetime faction history/progression, and magical objects remain deferred to separately approved slices.
- Challenges: Maven compiles all test sources before applying its test-name filter, so the focused-red run reported the missing method in both public and focused tests; both independently exercised the intended command once implemented.
