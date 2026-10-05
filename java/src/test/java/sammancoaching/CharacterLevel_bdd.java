package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class CharacterLevel_bdd {
    @Test
    void newCharacterStartsAtLevelOneWithMaximumHealth() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var printer = new PlayerCharacterPrinter();

        // Act
        var progression = printer.printProgression(hero);

        // Assert
        Approvals.verify(progression);
    }
}
