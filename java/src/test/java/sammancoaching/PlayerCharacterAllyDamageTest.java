package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class PlayerCharacterAllyDamageTest {
    @Test
    void allyDamageIsIgnored() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var companion = new PlayerCharacter("Companion");
        var knights = new Faction("Knights");
        hero.join(knights);
        companion.join(knights);

        // Act
        hero.receiveDamage(companion, 100);

        // Assert
        assertEquals(1000, hero.status().health());
    }
}
