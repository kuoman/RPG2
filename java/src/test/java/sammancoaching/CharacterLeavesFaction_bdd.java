package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class CharacterLeavesFaction_bdd {
    @Test
    void leavingOneFactionPreservesOtherMemberships() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var knights = new Faction("Knights");
        var mages = new Faction("Mages");
        hero.join(knights);
        hero.join(mages);

        // Act
        hero.leave(knights);

        // Assert
        Approvals.verify("""
                Hero leaves Knights.
                Hero belongs to Knights: %s.
                Hero belongs to Mages: %s.
                """.formatted(
                        hero.belongsTo(knights),
                        hero.belongsTo(mages)));
    }
}
