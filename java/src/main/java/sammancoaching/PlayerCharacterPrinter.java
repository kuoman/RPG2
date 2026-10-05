package sammancoaching;

public class PlayerCharacterPrinter {
    public String print(PlayerCharacter character) {
        var status = character.status();
        var lifeState = status.alive() ? "alive" : "dead";
        return "%s has %d health and is %s."
                .formatted(status.name(), status.health(), lifeState);
    }

    public String printProgression(PlayerCharacter character) {
        var status = character.status();
        return "%s is level %d with maximum health %d."
                .formatted(status.name(), status.level(), status.maximumHealth());
    }
}
