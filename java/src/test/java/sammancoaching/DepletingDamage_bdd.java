package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class DepletingDamage_bdd {
    @Test
    void damageEqualToCurrentHealthKillsTheTarget() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var orc = new PlayerCharacter("Orc");
        var printer = new PlayerCharacterPrinter();
        var beforeDamage = printer.print(hero);

        // Act
        hero.receiveDamage(orc, 1000);

        // Assert
        var afterDamage = printer.print(hero);
        Approvals.verify("""
                Orc deals 1000 damage to Hero.
                Before: %s
                After: %s
                """.formatted(beforeDamage, afterDamage));
    }
}
