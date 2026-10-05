package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class PlayerCharacterMaximumHealthGrowthTest {
    @Test
    void gainingALevelIncreasesMaximumHealthByOneHundred() {
        // Arrange
        var hero = new PlayerCharacter("Hero");

        // Act
        hero.gainLevel();

        // Assert
        var status = hero.status();
        assertEquals(2, status.level());
        assertEquals(1100, status.maximumHealth());
    }
}
