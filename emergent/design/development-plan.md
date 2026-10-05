# Development Plan

Record the agreed behavior sequence here. Completed items are evidence-backed. Unchecked items are provisional and require their own human BDD design checkpoint before implementation.

## Specification policy

- The later `RPG Combat` block in `README.md` supersedes the original rules where it changes Levels and Changing level.
- Damage and Health, Factions, and Magical objects retain their original rules because the later block says they have no changes.
- The approved project decision that damage equal to current health is lethal remains authoritative.
- Exact examples, rounding, and ambiguous transfer semantics are decided collaboratively at the relevant behavior checkpoint rather than invented in advance.

## 1. Core damage and health

- [x] A newly created character starts with 1000 health and is alive.
- [x] Receiving 100 damage reduces a living target from 1000 health to 900.
- [x] Damage greater than current health clamps the target to 0 health and kills it.
- [x] Damage equal to current health leaves the target at 0 health and dead.
- [x] A character cannot damage itself.

## 2. Healing

- [ ] A living damaged character can heal itself by an approved amount.
- [ ] Healing cannot raise a character above its current maximum health.
- [ ] A dead character cannot heal itself.

## 3. Levels, maximum health, and damage scaling

- [ ] A new character starts at level 1 with maximum health 1000.
- [ ] Each additional level increases maximum health by 100.
- [ ] Damage is reduced by 10% for each level the target is above the attacker, capped at a 50% reduction.
- [ ] Damage is increased by 10% for each level the target is below the attacker, capped at a 50% increase.
- [ ] Define integer damage rounding collaboratively before the first percentage modifier is implemented.

## 4. Factions and allies

- [ ] A new character belongs to no faction.
- [ ] A character can join one or more factions.
- [ ] A character can leave a faction without affecting membership in other factions.
- [ ] Two characters sharing at least one faction are allies.
- [ ] Allies cannot damage one another.
- [ ] Allies can heal one another.
- [ ] A character cannot heal a non-ally.

## 5. Magical objects

- [ ] A magical object is created with fixed maximum health and matching current health.
- [ ] Damage reduces a magical object's health; zero health destroys it without going below zero.
- [ ] Characters cannot heal magical objects.
- [ ] Magical objects are neutral and cannot belong to factions.
- [ ] A healing magical object can give a character a requested amount of health within both maximum-health limits.
- [ ] Define collaboratively whether transferred healing consumes the healing object's current health.
- [ ] A healing magical object cannot deal damage.
- [ ] A magical weapon deals its fixed damage when used by a character.
- [ ] Each weapon use reduces the weapon's health by 1; reaching zero destroys it.
- [ ] A magical weapon cannot give health to a character.

## 6. Level gain from surviving damage

- [ ] A level 1 character gains a level after cumulatively surviving 1000 damage points.
- [ ] A character at each subsequent level must survive an additional threshold equal to its current level times 1000 damage points before gaining the next level.
- [ ] Damage-based level gain occurs directly after an attack and only when the character survives it.
- [ ] Define collaboratively whether one attack can cross and award multiple damage-survival thresholds.

## 7. Level gain from faction history

- [ ] A character's lifetime count of distinct joined factions is retained after leaving them.
- [ ] A level 1 character gains a level after belonging to three distinct factions.
- [ ] Each subsequent faction-based level requires three additional distinct lifetime memberships.

## 8. Temporary level loss and recovery

- [ ] Characters have no maximum level and never fall below level 1.
- [ ] A surviving character loses one level when one attack exceeds 50% of its maximum health.
- [ ] Damage equal to exactly 50% of maximum health does not cause level loss.
- [ ] Separate qualifying attacks can remove additional levels down to level 1.
- [ ] Healing back to maximum health restores all levels lost to major blows.
- [ ] Define collaboratively which maximum-health value governs recovery while levels are temporarily missing.
- [ ] Damage- and faction-based level gains are suspended while major-blow levels are missing.
- [ ] On full recovery, restored levels are applied before any additional levels already earned through damage or faction history.

## Deferred unspecified behavior

- Receiving damage after death and zero or negative damage amounts are not specified by the source requirements. They remain outside the roadmap until the human adds explicit rules.
