package sammancoaching;

import org.approvaltests.Approvals;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

class PlayerCharacterTest {
    @Disabled("Pending approved damage behavior")
    @Test
    void dealDamage() {
        // arrange
        var hero = new PlayerCharacter("Hero");
        var orc = new PlayerCharacter("Orc");
        var story = new StringBuilder();
        story.append(hero.toString() + "\n");

        // act
        story.append("Orc deals 100 damage to Hero\n");
        hero.receiveDamage(orc, 100);

        // assert
        story.append(hero.toString() + "\n");
        Approvals.verify(story.toString());
    }

}
