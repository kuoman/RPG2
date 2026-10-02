# Responsibility Map

Record responsibilities learned from implemented behavior. Do not speculate beyond observed design pressure.

| Object or protocol | Job | Owns | Collaborates with | Open questions |
| --- | --- | --- | --- | --- |
| `PlayerCharacter` | Maintain one character's domain state | Name, health, and life state | Exposes an immutable `Status` snapshot to the printer | Damage behavior remains deferred |
| `PlayerCharacter.Status` | Carry an immutable observation of character state | Snapshot values only | Created by `PlayerCharacter`; consumed by `PlayerCharacterPrinter` | None for the approved creation behavior |
| `PlayerCharacterPrinter` | Render character state in domain language | Presentation format | Reads a `PlayerCharacter.Status` snapshot | Future presentation needs remain deferred |
