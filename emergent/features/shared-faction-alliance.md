# Shared-Faction Alliance

Status: Complete

Date: 2026/10/05

## Approved behavior

- Element Number: 16
- Behavior: Two characters sharing at least one faction are allies.
- Arrange: Create Hero, Companion, and a named Knights faction, then join both characters to the same Knights identity.
- Act: Ask Hero whether Companion is an ally.
- Assert: Hero and Companion are allies.

## Responsibility design

- Receiver job: `PlayerCharacter` compares its memberships with another character and answers the alliance query.
- Information owner: Each `PlayerCharacter` owns its own encapsulated faction memberships; `Faction` owns the shared identity.
- Decision owner: The receiver's `isAlliedWith(PlayerCharacter)` behavior owns the membership-intersection decision.
- State owner: No state changes; each character retains ownership of its membership set.
- Dependency abstraction: None required by this slice.
- Concrete implementation: Return true when any faction identity in the receiver's set is present in the other character's set.
- Injection point: None required by this slice.
- Composition root: None required by this slice.

## Red evidence

- Outside red: `SharedFactionAlliance_bdd` failed test compilation because `PlayerCharacter.isAlliedWith(PlayerCharacter)` did not exist.
- Focused red: `PlayerCharacterAllianceTest` failed test compilation for the same missing query; no production change preceded the run.

## Implementation

- Smallest behavior change: Add `PlayerCharacter.isAlliedWith(PlayerCharacter)` and test membership intersection using exact `Faction` identity.
- Refactoring while green: None; comparing the two membership sets is cohesive with the receiver's membership behavior.

## Verification

- Targeted tests: `PlayerCharacterAllianceTest` and `SharedFactionAlliance_bdd` pass, 2 tests with 0 failures.
- Complete suite: Thirty-four active Java tests pass, one explicitly deferred legacy seed is skipped, and 55 Starter tests pass.
- Quality checks: Membership collections remain encapsulated; no self-alliance, same-name equality, explicit non-alliance, combat, healing, progression, or magical-object behavior was introduced.
- Completion lane and receipt: Final behavior lane passed with candidate digest `sha256:254f62c9acda9af055d701b69dc136ac2b8d4ba66f4046275c7563150bf2515d` after the plan and responsibility-map update.

## Decisions and challenges

- Human decisions: Approved the shared-Knights scenario, exact output, and missing-query outside red using alias `a`; then confirmed that red and authorized the focused test plus minimal intersection implementation using alias `a`.
- Contextual coaching dispositions: Self-alliance, same-name faction equality, explicit no-shared-faction characterization, ally damage/healing, non-ally healing, lifetime faction history/progression, and magical objects remain deferred to separately approved slices.
- Challenges: Java permits one `PlayerCharacter` instance to inspect another instance's private membership set, preserving collection encapsulation while avoiding a broader exposure protocol.
