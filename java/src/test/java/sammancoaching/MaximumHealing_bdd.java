package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class MaximumHealing_bdd {
    @Test
    void healingStopsAtMaximumHealth() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var orc = new PlayerCharacter("Orc");
        var printer = new PlayerCharacterPrinter();
        hero.receiveDamage(orc, 100);
        var beforeHealing = printer.print(hero);

        // Act
        hero.heal(200);

        // Assert
        var afterHealing = printer.print(hero);
        Approvals.verify("""
                Orc deals 100 damage to Hero.
                Hero attempts to heal itself for 200 health.
                Before healing: %s
                After healing: %s
                """.formatted(beforeHealing, afterHealing));
    }
}
