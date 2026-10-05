package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class PlayerCharacterHigherLevelDamageReductionTest {
    @Test
    void oneLevelAdvantageReducesDamageTenPercentAndRoundsDown() {
        // Arrange
        var attacker = new PlayerCharacter("Attacker");
        var target = new PlayerCharacter("Target");
        target.gainLevel();

        // Act
        target.receiveDamage(attacker, 95);

        // Assert
        assertEquals(915, target.status().health());
    }

    @Test
    void sixLevelAdvantageCapsReductionAtFiftyPercent() {
        // Arrange
        var attacker = new PlayerCharacter("Attacker");
        var target = new PlayerCharacter("Target");
        for (int additionalLevel = 0; additionalLevel < 6; additionalLevel++) {
            target.gainLevel();
        }

        // Act
        target.receiveDamage(attacker, 100);

        // Assert
        assertEquals(950, target.status().health());
    }
}
