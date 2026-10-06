package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class NonAllyHealing_bdd {
    @Test
    void nonAllyHealingIsIgnored() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var stranger = new PlayerCharacter("Stranger");
        var orc = new PlayerCharacter("Orc");
        var printer = new PlayerCharacterPrinter();
        hero.receiveDamage(orc, 100);
        var beforeHealing = printer.print(hero);

        // Act
        stranger.heal(hero, 50);

        // Assert
        var afterHealing = printer.print(hero);
        Approvals.verify("""
                Hero and Stranger share no faction.
                Stranger attempts to heal Hero by 50.
                Before: %s
                After: %s
                """.formatted(beforeHealing, afterHealing));
    }
}
