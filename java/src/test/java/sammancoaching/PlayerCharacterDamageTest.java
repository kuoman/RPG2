package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class PlayerCharacterDamageTest {
    @Test
    void subtractsDamageFromHealthWithoutKillingTheTarget() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var orc = new PlayerCharacter("Orc");

        // Act
        hero.receiveDamage(orc, 100);

        // Assert
        var status = hero.status();
        assertEquals(900, status.health());
        assertTrue(status.alive());
    }
}
