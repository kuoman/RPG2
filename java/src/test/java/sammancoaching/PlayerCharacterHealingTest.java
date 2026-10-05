package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class PlayerCharacterHealingTest {
    @Test
    void restoresHealthToALivingDamagedCharacter() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var orc = new PlayerCharacter("Orc");
        hero.receiveDamage(orc, 100);

        // Act
        hero.heal(50);

        // Assert
        var status = hero.status();
        assertEquals(950, status.health());
        assertTrue(status.alive());
    }
}
