# Responsibility Map

Record responsibilities learned from implemented behavior. Do not speculate beyond observed design pressure.

| Object or protocol | Job | Owns | Collaborates with | Open questions |
| --- | --- | --- | --- | --- |
| `PlayerCharacter` | Maintain one character's domain state and apply received damage | Name, health, life state, and the lethal-health boundary | Receives an attacker and damage amount; exposes an immutable `Status` snapshot to the printer | Self-damage, already-dead targets, and invalid amounts remain deferred |
| `PlayerCharacter.Status` | Carry an immutable observation of character state | Snapshot values only | Created by `PlayerCharacter`; consumed by `PlayerCharacterPrinter` | None for the approved creation behavior |
| `PlayerCharacterPrinter` | Render character state in domain language | Presentation format | Reads a `PlayerCharacter.Status` snapshot | Future presentation needs remain deferred |
