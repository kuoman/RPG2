package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class SharedFactionAlliance_bdd {
    @Test
    void charactersSharingAFactionAreAllies() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var companion = new PlayerCharacter("Companion");
        var knights = new Faction("Knights");
        hero.join(knights);
        companion.join(knights);

        // Act
        var allies = hero.isAlliedWith(companion);

        // Assert
        Approvals.verify("""
                Hero and Companion share Knights.
                Hero and Companion are allies: %s.
                """.formatted(allies));
    }
}
