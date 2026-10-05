# Empty Initial Faction Membership

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 13
- Behavior: A newly created character belongs to no faction.
- Arrange: Create Hero and a named Knights faction.
- Act: Ask whether Hero belongs to Knights.
- Assert: Hero does not belong to Knights.

## Responsibility design

- Receiver job: `PlayerCharacter` owns its memberships and answers whether it belongs to a supplied faction.
- Information owner: `Faction` owns its name and identity; `PlayerCharacter` owns its faction memberships.
- Decision owner: `PlayerCharacter.belongsTo(Faction)` decides membership from the character's encapsulated collection.
- State owner: `PlayerCharacter` owns the initially empty membership set.
- Dependency abstraction: None required by this slice.
- Concrete implementation: A named `Faction` domain object and an identity-based membership set owned by `PlayerCharacter`.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `NewCharacterFaction_bdd` failed test compilation because `Faction` did not exist.
- Focused red: `PlayerCharacterFactionMembershipTest` failed test compilation because `Faction` did not exist; no production change preceded the run.

## Implementation

- Smallest behavior change: Add the named `Faction` type, initialize each character with an empty faction set, and expose the read-only `belongsTo(Faction)` query.
- Refactoring while green: None; the minimal responsibilities were already cohesive.

## Verification

- Targeted tests: `PlayerCharacterFactionMembershipTest` and `NewCharacterFaction_bdd` pass, 2 tests with 0 failures.
- Complete suite: Twenty-eight active Java tests pass, one explicitly deferred legacy seed is skipped, and 55 Starter tests pass.
- Quality checks: Faction membership remains encapsulated; no join, leave, ally, faction-equality, progression, or magical-object behavior was introduced.
- Completion lane and receipt: Final behavior lane passed with candidate digest `sha256:5d75a246a5b572f19f401d4b7e116d9274a17aa8a9d4431049a8f84e2c757b18` after the plan and responsibility-map update.

## Decisions and challenges

- Human decisions: Approved the named `Faction` object, `belongsTo` query, exact public scenario, and expected missing-protocol outside red using alias `a`; then confirmed that red and authorized the focused test plus minimal implementation using alias `a`.
- Contextual coaching dispositions: Joining, leaving, same-name equality, allies, ally damage/healing, faction-based progression, and magical objects remain deferred to separately approved slices.
- Challenges: Maven compiles all test sources before applying its test-name filter, so the focused-red run reported the same missing `Faction` type in both the public and focused tests; the focused test still independently exercised the intended protocol once it existed.
