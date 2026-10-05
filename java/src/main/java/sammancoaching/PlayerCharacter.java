package sammancoaching;

import java.util.HashSet;
import java.util.Set;

public class PlayerCharacter {
    private final String name;
    private final Set<Faction> factions;
    private int health;
    private int level;
    private int maximumHealth;
    private boolean alive;

    public PlayerCharacter(String name) {
        this.name = name;
        factions = new HashSet<>();
        level = 1;
        maximumHealth = 1000;
        health = maximumHealth;
        alive = true;
    }

    public void receiveDamage(PlayerCharacter enemy, int damagePoints) {
        if (enemy == this || isAlliedWith(enemy)) {
            return;
        }
        var appliedDamage = damageAdjustedForLevelDifference(enemy, damagePoints);
        if (appliedDamage >= health) {
            health = 0;
            alive = false;
        } else {
            health -= appliedDamage;
        }
    }

    private int damageAdjustedForLevelDifference(PlayerCharacter enemy, int damagePoints) {
        var levelDifference = enemy.level - level;
        if (levelDifference == 0) {
            return damagePoints;
        }
        var cappedLevelDifference = Math.max(-5, Math.min(levelDifference, 5));
        return damagePoints * (100 + cappedLevelDifference * 10) / 100;
    }

    public void heal(int healthPoints) {
        if (!alive) {
            return;
        }
        health = Math.min(maximumHealth, health + healthPoints);
    }

    public void heal(PlayerCharacter character, int healthPoints) {
        character.heal(healthPoints);
    }

    void gainLevel() {
        level += 1;
        maximumHealth += 100;
    }

    public void join(Faction faction) {
        factions.add(faction);
    }

    public void leave(Faction faction) {
        factions.remove(faction);
    }

    public boolean belongsTo(Faction faction) {
        return factions.contains(faction);
    }

    public boolean isAlliedWith(PlayerCharacter character) {
        return factions.stream().anyMatch(character.factions::contains);
    }

    Status status() {
        return new Status(name, health, alive, level, maximumHealth);
    }

    record Status(String name, int health, boolean alive, int level, int maximumHealth) {
    }
}
