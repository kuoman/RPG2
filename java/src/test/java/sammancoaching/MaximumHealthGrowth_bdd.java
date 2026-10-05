package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class MaximumHealthGrowth_bdd {
    @Test
    void gainingALevelIncreasesMaximumHealth() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var printer = new PlayerCharacterPrinter();
        var beforeLevelGain = printer.printProgression(hero);

        // Act
        hero.gainLevel();

        // Assert
        var afterLevelGain = printer.printProgression(hero);
        Approvals.verify("""
                Hero gains one level.
                Before: %s
                After: %s
                """.formatted(beforeLevelGain, afterLevelGain));
    }
}
