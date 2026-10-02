package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class CharacterCreation_bdd {
    @Test
    void newCharacterStartsWithFullHealthAndAlive() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var printer = new PlayerCharacterPrinter();

        // Act
        var characterStatus = printer.print(hero);

        // Assert
        Approvals.verify(characterStatus);
    }
}
