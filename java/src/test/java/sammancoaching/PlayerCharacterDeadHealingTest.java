package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

class PlayerCharacterDeadHealingTest {
    @Test
    void doesNotHealADeadCharacter() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var orc = new PlayerCharacter("Orc");
        hero.receiveDamage(orc, 1000);

        // Act
        hero.heal(100);

        // Assert
        var status = hero.status();
        assertEquals(0, status.health());
        assertFalse(status.alive());
    }
}
