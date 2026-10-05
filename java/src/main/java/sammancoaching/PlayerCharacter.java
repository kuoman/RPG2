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
        health -= damagePoints;
    }

    Status status() {
        return new Status(name, health, alive);
    }

    record Status(String name, int health, boolean alive) {
    }
}
