package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class PlayerCharacterLevelTest {
    @Test
    void startsAtLevelOneWithMaximumHealth() {
        // Arrange
        var hero = new PlayerCharacter("Hero");

        // Act
        var status = hero.status();

        // Assert
        assertEquals(1, status.level());
        assertEquals(1000, status.maximumHealth());
    }
}
