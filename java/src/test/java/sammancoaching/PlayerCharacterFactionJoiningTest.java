package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertTrue;

class PlayerCharacterFactionJoiningTest {
    @Test
    void joinsAnAdditionalFactionWithoutLosingExistingMembership() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var knights = new Faction("Knights");
        var mages = new Faction("Mages");
        hero.join(knights);

        // Act
        hero.join(mages);

        // Assert
        assertTrue(hero.belongsTo(knights));
        assertTrue(hero.belongsTo(mages));
    }
}
