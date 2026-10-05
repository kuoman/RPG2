package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class HigherLevelDamageReduction_bdd {
    @Test
    void higherLevelTargetTakesCappedReducedDamage() {
        // Arrange
        var attacker = new PlayerCharacter("Attacker");
        var target = new PlayerCharacter("Target");
        var printer = new PlayerCharacterPrinter();
        for (int additionalLevel = 0; additionalLevel < 6; additionalLevel++) {
            target.gainLevel();
        }
        var attackerProgression = printer.printProgression(attacker);
        var targetProgression = printer.printProgression(target);
        var beforeDamage = printer.print(target);

        // Act
        target.receiveDamage(attacker, 95);

        // Assert
        var afterDamage = printer.print(target);
        Approvals.verify("""
                Attacker: %s
                Target: %s
                Requested damage: 95.
                The six-level reduction is capped at 50%%.
                Fractional damage rounds down.
                Before: %s
                After: %s
                """.formatted(
                attackerProgression,
                targetProgression,
                beforeDamage,
                afterDamage));
    }
}
