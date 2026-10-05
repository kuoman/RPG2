package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class PlayerCharacterAllyHealingTest {
    @Test
    void allyCanHealADamagedCharacter() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var companion = new PlayerCharacter("Companion");
        var orc = new PlayerCharacter("Orc");
        var knights = new Faction("Knights");
        hero.receiveDamage(orc, 100);
        hero.join(knights);
        companion.join(knights);

        // Act
        companion.heal(hero, 50);

        // Assert
        assertEquals(950, hero.status().health());
    }
}
