package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class AllyDamage_bdd {
    @Test
    void allyDamageIsIgnored() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var companion = new PlayerCharacter("Companion");
        var knights = new Faction("Knights");
        var printer = new PlayerCharacterPrinter();
        hero.join(knights);
        companion.join(knights);
        var beforeDamage = printer.print(hero);

        // Act
        hero.receiveDamage(companion, 100);

        // Assert
        var afterDamage = printer.print(hero);
        Approvals.verify("""
                Hero and Companion share Knights.
                Companion attempts to deal 100 damage to Hero.
                Before: %s
                After: %s
                """.formatted(beforeDamage, afterDamage));
    }
}
