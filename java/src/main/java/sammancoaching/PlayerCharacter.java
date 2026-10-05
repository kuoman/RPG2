package sammancoaching;

public class PlayerCharacter {
    private final String name;
    private int health;
    private int level;
    private int maximumHealth;
    private boolean alive;

    public PlayerCharacter(String name) {
        this.name = name;
        level = 1;
        maximumHealth = 1000;
        health = maximumHealth;
        alive = true;
    }

    public void receiveDamage(PlayerCharacter enemy, int damagePoints) {
        if (enemy == this) {
            return;
        }
        var appliedDamage = damagePoints;
        if (level > enemy.level) {
            var levelAdvantage = level - enemy.level;
            var reductionPercentage = Math.min(levelAdvantage * 10, 50);
            appliedDamage = damagePoints * (100 - reductionPercentage) / 100;
        }
        if (appliedDamage >= health) {
            health = 0;
            alive = false;
        } else {
            health -= appliedDamage;
        }
    }

    public void heal(int healthPoints) {
        if (!alive) {
            return;
        }
        health = Math.min(maximumHealth, health + healthPoints);
    }

    void gainLevel() {
        level += 1;
        maximumHealth += 100;
    }

    Status status() {
        return new Status(name, health, alive, level, maximumHealth);
    }

    record Status(String name, int health, boolean alive, int level, int maximumHealth) {
    }
}
