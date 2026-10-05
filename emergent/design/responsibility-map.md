# Responsibility Map

Record responsibilities learned from implemented behavior. Do not speculate beyond observed design pressure.

| Object or protocol | Job | Owns | Collaborates with | Open questions |
| --- | --- | --- | --- | --- |
| `PlayerCharacter` | Maintain one character's domain state, reject self-inflicted damage, apply received damage, and restore its health | Name, object identity, health, life state, and damage boundaries | Receives an attacker and damage amount; accepts a self-healing amount; exposes an immutable `Status` snapshot to the printer | Maximum-health capping and dead-character healing remain later slices; already-dead damage and invalid amounts remain deferred |
| `PlayerCharacter.Status` | Carry an immutable observation of character state | Snapshot values only | Created by `PlayerCharacter`; consumed by `PlayerCharacterPrinter` | None for the approved creation behavior |
| `PlayerCharacterPrinter` | Render character state in domain language | Presentation format | Reads a `PlayerCharacter.Status` snapshot | Future presentation needs remain deferred |
