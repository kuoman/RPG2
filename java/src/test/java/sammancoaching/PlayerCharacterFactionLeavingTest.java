package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class PlayerCharacterFactionLeavingTest {
    @Test
    void leavesOneFactionWithoutLosingAnotherMembership() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var knights = new Faction("Knights");
        var mages = new Faction("Mages");
        hero.join(knights);
        hero.join(mages);

        // Act
        hero.leave(knights);

        // Assert
        assertFalse(hero.belongsTo(knights));
        assertTrue(hero.belongsTo(mages));
    }
}
