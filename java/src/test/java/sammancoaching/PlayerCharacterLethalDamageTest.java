package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

class PlayerCharacterLethalDamageTest {
    @Test
    void overkillDamageClampsHealthAndKillsTheTarget() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var orc = new PlayerCharacter("Orc");

        // Act
        hero.receiveDamage(orc, 1500);

        // Assert
        var status = hero.status();
        assertEquals(0, status.health());
        assertFalse(status.alive());
    }
}
