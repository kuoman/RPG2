package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;

class CharacterJoinsFactions_bdd {
    @Test
    void characterCanJoinMoreThanOneFaction() {
        // Arrange
        var hero = new PlayerCharacter("Hero");
        var knights = new Faction("Knights");
        var mages = new Faction("Mages");
        hero.join(knights);

        // Act
        hero.join(mages);

        // Assert
        Approvals.verify("""
                Hero joins Knights, then Mages.
                Hero belongs to Knights: %s.
                Hero belongs to Mages: %s.
                """.formatted(
                        hero.belongsTo(knights),
                        hero.belongsTo(mages)));
    }
}
