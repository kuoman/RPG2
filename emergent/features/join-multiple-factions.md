# Join Multiple Factions

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 14
- Behavior: A character can join more than one faction without losing an existing membership.
- Arrange: Create Hero plus named Knights and Mages factions, then join Hero to Knights.
- Act: Hero joins Mages.
- Assert: Hero belongs to both Knights and Mages.

## Responsibility design

- Receiver job: `PlayerCharacter` accepts a faction to join and changes its own memberships.
- Information owner: `Faction` owns its name and identity; `PlayerCharacter` owns its faction memberships.
- Decision owner: `PlayerCharacter.join(Faction)` decides how the supplied identity is incorporated into existing membership.
- State owner: `PlayerCharacter` owns and mutates the membership set.
- Dependency abstraction: None required by this slice.
- Concrete implementation: Add the supplied `Faction` to the existing identity-based set.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `CharacterJoinsFactions_bdd` failed test compilation at both join calls because `PlayerCharacter.join(Faction)` did not exist.
- Focused red: `PlayerCharacterFactionJoiningTest` failed test compilation at both join calls for the same missing command; no production change preceded the run.

## Implementation

- Smallest behavior change: Add `PlayerCharacter.join(Faction)` and insert the supplied faction into the character's existing membership set.
- Refactoring while green: None; the command belongs with the membership state already owned by `PlayerCharacter`.

## Verification

- Targeted tests: `PlayerCharacterFactionJoiningTest` and `CharacterJoinsFactions_bdd` pass, 2 tests with 0 failures.
- Complete suite: Thirty active Java tests pass, one explicitly deferred legacy seed is skipped, and 55 Starter tests pass.
- Quality checks: Membership remains encapsulated; no leave, same-name equality, ally, healing, progression, or magical-object behavior was introduced.
- Completion lane and receipt: Final behavior lane passed with candidate digest `sha256:ff238c9f9cd90f2d0d86b5bfaeeabb4105adc5478dfd073e38afb78265f02c53` after the plan and responsibility-map update.

## Decisions and challenges

- Human decisions: Approved the two-faction scenario, exact output, and missing-join outside red using alias `a`; then confirmed that red and authorized the focused test plus minimal implementation using alias `a`.
- Contextual coaching dispositions: Leaving, same-name faction equality, allies, ally damage/healing, non-ally healing, faction-based progression, and magical objects remain deferred to separately approved slices.
- Challenges: Maven compiles all test sources before applying its test-name filter, so the focused-red run reported the missing method in both public and focused tests; both independently exercised the intended command once implemented.
