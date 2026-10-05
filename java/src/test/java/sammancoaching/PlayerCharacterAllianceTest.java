package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertTrue;

class PlayerCharacterAllianceTest {
    @Test
    void sharedFactionMakesCharactersAllies() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var companion = new PlayerCharacter("Companion");
        var knights = new Faction("Knights");
        hero.join(knights);
        companion.join(knights);

        // Act
        var allies = hero.isAlliedWith(companion);

        // Assert
        assertTrue(allies);
    }
}
