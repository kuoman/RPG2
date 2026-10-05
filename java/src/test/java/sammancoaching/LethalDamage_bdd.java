package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class LethalDamage_bdd {
    @Test
    void overkillDamageClampsHealthAndKillsTheTarget() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var orc = new PlayerCharacter("Orc");
        var printer = new PlayerCharacterPrinter();
        var beforeDamage = printer.print(hero);

        // Act
        hero.receiveDamage(orc, 1500);

        // Assert
        var afterDamage = printer.print(hero);
        Approvals.verify("""
                Orc deals 1500 damage to Hero.
                Before: %s
                After: %s
                """.formatted(beforeDamage, afterDamage));
    }
}
