import sys
from ursina import *

# Constants
LEVEL_COUNT = 32
GRAVITY = 0.8
JUMP_POWER = -16
PLAYER_SPEED = 5
ENEMY_SPEED = 2
LEVEL_LENGTH = 200  # Length in Z direction for 3D

# Colors
SKY_COLOR = color.rgb(107, 140, 255)
GROUND_COLOR = color.rgb(96, 56, 19)
COIN_COLOR = color.rgb(255, 223, 0)
PLAYER_COLOR = color.red
ENEMY_COLOR = color.orange

app = Ursina()
window.title = 'Super Mario 3D Land - Python Edition'
window.fullscreen = True  # For 4K/fullscreen; adjust if needed
# window.size = (3840, 2160)  # Uncomment for windowed 4K mode

class Player(Entity):
    def __init__(self):
        super().__init__(model='cube', scale=(1, 2, 1), color=PLAYER_COLOR, collider='box')
        self.velocity_y = 0
        self.on_ground = False
        self.score = 0

    def update(self):
        # Movement
        direction = Vec3(held_keys['d'] - held_keys['a'], 0, held_keys['w'] - held_keys['s']).normalized() * PLAYER_SPEED * time.dt
        self.position += direction

        # Gravity and jump
        ray = raycast(self.world_position, direction=Vec3(0, -1, 0), distance=2.1, ignore=[self])
        if ray.hit:
            self.on_ground = True
            self.velocity_y = 0
        else:
            self.on_ground = False

        if held_keys['space'] and self.on_ground:
            self.velocity_y = JUMP_POWER

        self.velocity_y += GRAVITY
        self.y += self.velocity_y * time.dt

        # Fall death
        if self.y < -10:
            print('Game Over! Fell off the level.')
            app.close()

        # Collect coins
        for coin in level_coins[:]:
            if distance(self, coin) < 2:
                destroy(coin)
                level_coins.remove(coin)
                self.score += 1

        # Enemy collision
        for enemy in level_enemies:
            if distance(self, enemy) < 2:
                print('Game Over! Hit an enemy.')
                app.close()

class Enemy(Entity):
    def __init__(self, position):
        super().__init__(model='cube', scale=(1, 2, 1), color=ENEMY_COLOR, collider='box', position=position)
        self.direction = 1

    def update(self):
        self.z += ENEMY_SPEED * time.dt * self.direction
        # Simple turnaround (expand with raycasts for walls)
        if self.z > 50 or self.z < 0:
            self.direction *= -1

# Level data
level_data = []
for i in range(LEVEL_COUNT):
    world_number = (i // 4) + 1
    level_number = (i % 4) + 1
    level_data.append({'world': f'{world_number}-{level_number}', 'type': 'ground' if world_number % 2 == 1 else 'underground'})

# Global lists
level_platforms = []
level_coins = []
level_enemies = []

player = Player()
camera.add_script(SmoothFollow(target=player, offset=(0, 5, -20), speed=4))

sky = Sky()

# UI
level_text = Text(text='', origin=(-0.5, 0.5), scale=2)
score_text = Text(text='', origin=(-0.5, 0.45), scale=2)

def create_level(level_index):
    global level_platforms, level_coins, level_enemies
    # Clear previous
    for p in level_platforms:
        destroy(p)
    for c in level_coins:
        destroy(c)
    for e in level_enemies:
        destroy(e)
    level_platforms = []
    level_coins = []
    level_enemies = []

    # Ground
    ground = Entity(model='plane', scale=(50, 1, LEVEL_LENGTH), position=(0, 0, LEVEL_LENGTH/2), color=GROUND_COLOR, texture='grass', collider='mesh')
    level_platforms.append(ground)

    # Example platforms for World 1-1
    if level_data[level_index]['world'] == '1-1':
        platform1 = Entity(model='cube', scale=(10, 1, 5), position=(0, 2, 20), color=GROUND_COLOR, collider='box')
        level_platforms.append(platform1)
        coin = Entity(model='sphere', scale=1, position=(0, 3, 20), color=COIN_COLOR, collider='sphere')
        level_coins.append(coin)
        enemy = Enemy(position=(0, 2, 30))
        level_enemies.append(enemy)

    # Add more for other levels...

current_level = 0
create_level(current_level)

def update():
    player.update()
    for e in level_enemies:
        e.update()

    # Level progression
    if player.z > LEVEL_LENGTH:
        global current_level
        current_level += 1
        if current_level >= LEVEL_COUNT:
            print('Congratulations! Completed all levels!')
            app.close()
        else:
            player.position = Vec3(0, 1, 0)
            create_level(current_level)

    # Update UI
    level_text.text = f'World {level_data[current_level]["world"]}'
    score_text.text = f'Score: {player.score}'

    # Quit
    if held_keys['escape']:
        app.close()

app.run()
