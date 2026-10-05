package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class AllyHealing_bdd {
    @Test
    void allyCanHealADamagedCharacter() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var companion = new PlayerCharacter("Companion");
        var orc = new PlayerCharacter("Orc");
        var knights = new Faction("Knights");
        var printer = new PlayerCharacterPrinter();
        hero.receiveDamage(orc, 100);
        hero.join(knights);
        companion.join(knights);
        var beforeHealing = printer.print(hero);

        // Act
        companion.heal(hero, 50);

        // Assert
        var afterHealing = printer.print(hero);
        Approvals.verify("""
                Hero and Companion share Knights.
                Companion attempts to heal Hero by 50.
                Before: %s
                After: %s
                """.formatted(beforeHealing, afterHealing));
    }
}
