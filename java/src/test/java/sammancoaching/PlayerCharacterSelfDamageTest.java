package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class PlayerCharacterSelfDamageTest {
    @Test
    void ignoresDamageWhenTheAttackerIsTheTarget() {
        // Arrange
        var hero = new PlayerCharacter("Hero");

        // Act
        hero.receiveDamage(hero, 100);

        // Assert
        var status = hero.status();
        assertEquals(1000, status.health());
        assertTrue(status.alive());
    }
}
