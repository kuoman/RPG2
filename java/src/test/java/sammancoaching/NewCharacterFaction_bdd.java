package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class NewCharacterFaction_bdd {
    @Test
    void newCharacterBelongsToNoFaction() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var knights = new Faction("Knights");

        // Act
        var belongsToKnights = hero.belongsTo(knights);

        // Assert
        Approvals.verify("""
                Hero is newly created.
                Hero belongs to Knights: %s.
                """.formatted(belongsToKnights));
    }
}
