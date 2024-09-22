from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import time

app = Ursina()

# Cave size parameters
cave_width = 20
cave_length = 20

# Player attributes
player_health = 100
ammo = 50

# List to hold walls and enemies
walls = []
enemies = []

# Create a simple "cave" environment by placing floor and random walls
for z in range(cave_length):
    for x in range(cave_width):
        # Creating the floor with a collider so the player doesn't fall through
        Entity(model='cube', color=color.gray, scale=(1, 0.1, 1), position=(x, 0, z), collider='box')

        # Randomly place some walls to simulate cave-like structure
        if random.random() < 0.2:  # 20% chance to place a wall
            wall = Entity(model='cube', color=color.dark_gray, scale=(1, 2, 1), position=(x, 1, z), collider='box')
            walls.append(wall)

# Create the player (camera + movement)
player = FirstPersonController()
player.y = 1  # Lift the player slightly above the ground

# HUD for displaying health and ammo
health_text = Text(text=f'Health: {player_health}', position=(-0.85, 0.45), scale=2, origin=(0, 0), background=True)
ammo_text = Text(text=f'Ammo: {ammo}', position=(-0.85, 0.4), scale=2, origin=(0, 0), background=True)

# Function to update HUD
def update_hud():
    health_text.text = f'Health: {player_health}'
    ammo_text.text = f'Ammo: {ammo}'

# Function to check if a position is free (no wall or enemy)
def is_position_free(x, z):
    for wall in walls:
        if int(wall.position.x) == x and int(wall.position.z) == z:
            return False
    for enemy in enemies:
        if int(enemy.position.x) == x and int(enemy.position.z) == z:
            return False
    return True

# Enemy class to create AI movement
class Enemy(Entity):
    def __init__(self, position=(0, 1, 0), **kwargs):
        super().__init__(
            model='cube',
            color=color.red,
            scale=(1, 2, 1),
            position=position,
            collider='box',
            **kwargs
        )
        self.health = 50
        self.speed = 0.02  # Reduced speed to make enemies slower like Doom
        self.target = player
        self.update_time = 0  # Tracks time for AI decision-making
        self.attack_delay = 1  # Slower attack frequency (1 second delay)

    def update(self):
        self.update_time += time.dt  # Accumulate time

        # Only update movement and attack every 0.5 seconds to simulate slower AI
        if self.update_time > 0.5:
            self.update_time = 0  # Reset the timer

            # Move towards the player
            if distance(self.position, player.position) > 2:
                direction = (player.position - self.position).normalized()
                self.position += direction * self.speed

            # If enemy is close to player, deal damage after a delay
            if distance(self.position, player.position) < 2:
                if self.attack_delay <= 0:  # Attack cooldown
                    deal_damage(10)
                    self.attack_delay = 1  # Reset the attack cooldown
                else:
                    self.attack_delay -= time.dt  # Reduce cooldown timer

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            enemies.remove(self)
            destroy(self)

# Shooting mechanics (raycasting)
def shoot():
    global ammo
    if ammo > 0:
        ammo -= 1
        update_hud()
        hit_info = raycast(player.position, player.forward, distance=10, ignore=[player,])
        if hit_info.hit:
            if isinstance(hit_info.entity, Enemy):
                hit_info.entity.take_damage(25)

# Enemy spawning function
def spawn_enemy():
    while True:
        x = random.randint(0, cave_width - 1)
        z = random.randint(0, cave_length - 1)
        if is_position_free(x, z):
            enemy = Enemy(position=(x, 1, z))
            enemies.append(enemy)
            break

# Deal damage to the player
def deal_damage(damage):
    global player_health
    player_health -= damage
    update_hud()
    if player_health <= 0:
        print("Game Over!")
        application.quit()

# Periodically spawn enemies
def update():
    if random.random() < 0.01:  # Adjust the probability to control the spawn rate
        spawn_enemy()

    # Shooting mechanic (Z key press to shoot)
    if held_keys['z']:  # Listen for Z key press to shoot
        shoot()

app.run()
