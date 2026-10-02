# Restore Progression Red

Date: 2026/09/30

Automation: CodeCraft feature cycle 0.4.1

## Intent

Remove an unapproved higher-level damage threshold rule so the next progression behavior can enter the outside-in cycle with an honest failing BDD.

## Authorized Scope

- Preserve every behavior already approved in `progression-basics-1`.
- Keep the approved fixed threshold of 1000 survived damage for gaining a level.
- Do not define how much survived damage a character at level 2 or above requires.
- Do not create, modify, or delete a protected BDD asset.
- Do not change the provisional plan.

## Responsibility Design

- Receiver job: `CharacterProgression` owns progression state and decides when accumulated survived damage earns a level.
- Information owner: `DamageOutcome` reports the damage and whether the character survived it.
- Decision owner: `CharacterProgression` applies only the currently approved fixed threshold.
- State-change owner: `CharacterProgression` changes its accumulated damage and level; `HealthCapacity` changes maximum health when told.
- Dependency abstraction: `HealthCapacity`
- Concrete implementation: `CharacterHealth`
- Injection point: the `CharacterProgression` constructor
- Composition root: `PlayerCharacterFactory`
- SOLID review: the edit adds no responsibility or dependency, keeps progression policy behind its cohesive protocol, and leaves concrete assembly outside the policy object.

## Smallest Correction

`CharacterProgression` no longer multiplies the damage threshold by the current level. The constant name now describes the single approved rule rather than implying an unapproved per-level policy.

## Verification

- Focused progression suite: 6 tests passed.
- Canonical repository verification: `./mvnw verify` passed.
- No protected BDD asset or batch manifest changed.

## Decisions

- This is a scope correction from green: approved behavior remains green while behavior that had no approved BDD is removed.
- The next higher-level threshold must be proposed in the approval grid and observed red before production code defines it.
- `PlayerCharacter` remains outside this increment; its unrelated formatting change is preserved untouched.

## Challenges

- The previous formula anticipated the next kata requirement and made its natural BDD unexpectedly green. Returning to the last approved behavior restores meaningful outside-in feedback.
