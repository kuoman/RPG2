package sammancoaching;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class PlayerCharacterLowerLevelDamageIncreaseTest {
    @Test
    void oneLevelDisadvantageIncreasesDamageTenPercentAndRoundsDown() {
        // Arrange
        var attacker = new PlayerCharacter("Attacker");
        var target = new PlayerCharacter("Target");
        attacker.gainLevel();

        // Act
        target.receiveDamage(attacker, 95);

        // Assert
        assertEquals(896, target.status().health());
    }

    @Test
    void sixLevelDisadvantageCapsIncreaseAtFiftyPercent() {
        // Arrange
        var attacker = new PlayerCharacter("Attacker");
        var target = new PlayerCharacter("Target");
        for (int additionalLevel = 0; additionalLevel < 6; additionalLevel++) {
            attacker.gainLevel();
        }

        // Act
        target.receiveDamage(attacker, 100);

        // Assert
        assertEquals(850, target.status().health());
    }
}
