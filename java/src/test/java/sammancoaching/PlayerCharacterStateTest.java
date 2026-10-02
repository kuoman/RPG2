package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class PlayerCharacterStateTest {
    @Test
    void newCharacterStartsWithFullHealthAndAlive() {
        // Arrange
        var hero = new PlayerCharacter("Hero");

        // Act
        var status = hero.status();

        // Assert
        assertEquals(new PlayerCharacter.Status("Hero", 1000, true), status);
    }
}
