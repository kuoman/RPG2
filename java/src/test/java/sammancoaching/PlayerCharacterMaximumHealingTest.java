package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class PlayerCharacterMaximumHealingTest {
    @Test
    void stopsHealingAtMaximumHealth() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var orc = new PlayerCharacter("Orc");
        hero.receiveDamage(orc, 100);

        // Act
        hero.heal(200);

        // Assert
        var status = hero.status();
        assertEquals(1000, status.health());
        assertTrue(status.alive());
    }
}
