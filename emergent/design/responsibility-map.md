# Responsibility Map

Record responsibilities learned from implemented behavior. Do not speculate beyond observed design pressure.

| Object or protocol | Job | Owns | Collaborates with | Open questions |
| --- | --- | --- | --- | --- |
| `PlayerCharacter` | Maintain one character's domain state, initialize progression, reject self-inflicted damage, apply received damage, restore living health, and enforce healing boundaries | Name, object identity, health, current maximum health, level, life state, and damage boundaries | Receives an attacker and damage amount; accepts a self-healing amount; exposes an immutable `Status` snapshot to the printer | Level gain and level-driven maximum growth remain later slices; already-dead damage and invalid amounts remain deferred |
| `PlayerCharacter.Status` | Carry an immutable observation of character state | Name, health, life state, level, and maximum-health snapshot values | Created by `PlayerCharacter`; consumed by `PlayerCharacterPrinter` | Future progression counters remain deferred |
| `PlayerCharacterPrinter` | Render health/life and progression state in domain language without changing the character | Presentation formats | Reads a `PlayerCharacter.Status` snapshot | Future presentation needs remain deferred |
