package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class SelfDamage_bdd {
    @Test
    void selfDamageIsIgnored() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var printer = new PlayerCharacterPrinter();
        var beforeDamage = printer.print(hero);

        // Act
        hero.receiveDamage(hero, 100);

        // Assert
        var afterDamage = printer.print(hero);
        Approvals.verify("""
                Hero attempts to deal 100 damage to itself.
                Before: %s
                After: %s
                """.formatted(beforeDamage, afterDamage));
    }
}
