package sammancoaching;

public class PlayerCharacter {
    private final String name;
    private int health;
    private boolean alive;

    public PlayerCharacter(String name) {
        this.name = name;
        health = 1000;
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
        health += healthPoints;
    }

    Status status() {
        return new Status(name, health, alive);
    }

    record Status(String name, int health, boolean alive) {
    }
}
