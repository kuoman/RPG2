# Responsibility Map

Record responsibilities learned from implemented behavior. Do not speculate beyond observed design pressure.

| Object or protocol | Job | Owns | Collaborates with | Open questions |
| --- | --- | --- | --- | --- |
| `PlayerCharacter` | Maintain one character's domain state, join and leave factions, answer faction-membership and shared-faction alliance queries, advance an already-authorized level gain, reject self-inflicted damage, scale damage from relative levels, apply received damage, restore living health, and enforce health boundaries | Name, object identity, faction memberships, health, current maximum health, level, life state, and damage boundaries | Receives a `Faction` to join, leave, or query; compares memberships with another `PlayerCharacter`; receives an attacker and requested damage amount; compares the attacker's level with its own; accepts a self-healing amount; and exposes an immutable `Status` snapshot to the printer | Self-alliance, explicit no-shared-faction behavior, faction equality, ally combat/healing rules, level-gain eligibility, current-health effects during progression, already-dead damage, and invalid amounts remain deferred |
| `Faction` | Represent one named faction identity | Name and object identity | Joined, left, queried, and compared as shared identity by `PlayerCharacter` membership behavior | Equality between separately constructed same-name factions remains deferred |
| `PlayerCharacter.Status` | Carry an immutable observation of character state | Name, health, life state, level, and maximum-health snapshot values | Created by `PlayerCharacter`; consumed by `PlayerCharacterPrinter` | Future progression counters remain deferred |
| `PlayerCharacterPrinter` | Render health/life and progression state in domain language without changing the character | Presentation formats | Reads a `PlayerCharacter.Status` snapshot | Future presentation needs remain deferred |
