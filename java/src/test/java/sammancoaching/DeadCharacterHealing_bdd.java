package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class DeadCharacterHealing_bdd {
    @Test
    void deadCharacterCannotHealItself() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var orc = new PlayerCharacter("Orc");
        var printer = new PlayerCharacterPrinter();
        hero.receiveDamage(orc, 1000);
        var beforeHealing = printer.print(hero);

        // Act
        hero.heal(100);

        // Assert
        var afterHealing = printer.print(hero);
        Approvals.verify("""
                Orc deals 1000 damage to Hero.
                Hero attempts to heal itself for 100 health.
                Before healing: %s
                After healing: %s
                """.formatted(beforeHealing, afterHealing));
    }
}
