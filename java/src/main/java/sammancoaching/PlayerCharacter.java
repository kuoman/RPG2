package sammancoaching;

public class PlayerCharacter {
    private final String name;
    private int health;
    private int maximumHealth;
    private boolean alive;

    public PlayerCharacter(String name) {
        this.name = name;
        maximumHealth = 1000;
        health = maximumHealth;
        alive = true;
    }

    public void receiveDamage(PlayerCharacter enemy, int damagePoints) {
        if (enemy == this) {
            return;
        }
        if (damagePoints >= health) {
            health = 0;
            alive = false;
        } else {
            health -= damagePoints;
        }
    }

    public void heal(int healthPoints) {
        if (!alive) {
            return;
        }
        health = Math.min(maximumHealth, health + healthPoints);
    }

    Status status() {
        return new Status(name, health, alive);
    }

    record Status(String name, int health, boolean alive) {
    }
}
