package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;

class PlayerCharacterFactionMembershipTest {
    @Test
    void newCharacterBelongsToNoFaction() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var knights = new Faction("Knights");

        // Act
        var belongsToKnights = hero.belongsTo(knights);

        // Assert
        assertFalse(belongsToKnights);
    }
}
