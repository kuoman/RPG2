package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class CharacterHealing_bdd {
    @Test
    void damagedLivingCharacterHealsItself() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var orc = new PlayerCharacter("Orc");
        var printer = new PlayerCharacterPrinter();
        hero.receiveDamage(orc, 100);
        var beforeHealing = printer.print(hero);

        // Act
        hero.heal(50);

        // Assert
        var afterHealing = printer.print(hero);
        Approvals.verify("""
                Orc deals 100 damage to Hero.
                Hero heals itself for 50 health.
                Before healing: %s
                After healing: %s
                """.formatted(beforeHealing, afterHealing));
    }
}
