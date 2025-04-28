from ursina import *
from panda3d.core import ClockObject

app = Ursina()
window.size = (600, 400)
# Cap the frame rate at 60 FPS for consistency with Paper Mario
app.clock.setMode(ClockObject.MLimited)
app.clock.setFrameRate(60)
camera.orthographic = True
camera.position = (0, 0, -10)
camera.look_at((0, 0, 0))

# Player setup
player = Entity(model='cube', color=color.red, scale=(0.5, 1, 0.01), position=(0, 5, 0))
player.velocity_y = 0
player.on_ground = False
gravity = 20
jump_strength = 10
speed = 5

# Platforms
ground = Entity(model='cube', color=color.green, scale=(20, 1, 0.01), position=(0, -2, 0))
platform1 = Entity(model='cube', color=color.green, scale=(2, 0.2, 0.01), position=(-5, 0, 0))
platform2 = Entity(model='cube', color=color.green, scale=(2, 0.2, 0.01), position=(0, 2, 0))
platform3 = Entity(model='cube', color=color.green, scale=(2, 0.2, 0.01), position=(5, 4, 0))
platforms = [ground, platform1, platform2, platform3]

# Enemies
enemy1 = Entity(model='cube', color=color.brown, scale=(0.5, 0.5, 0.01), position=(-3, -1.5, 0))
enemy1.direction = 1
enemy1.speed = 2
enemy1.min_x = -4
enemy1.max_x = -2

enemy2 = Entity(model='cube', color=color.brown, scale=(0.5, 0.5, 0.01), position=(0, 2.1, 0))
enemy2.direction = 1
enemy2.speed = 2
enemy2.min_x = -1
enemy2.max_x = 1

enemies = [enemy1, enemy2]

# Collectibles
coin1 = Entity(model='cube', color=color.yellow, scale=(0.2, 0.2, 0.01), position=(-5, 1, 0))
coin2 = Entity(model='cube', color=color.yellow, scale=(0.2, 0.2, 0.01), position=(0, 3, 0))
coin3 = Entity(model='cube', color=color.yellow, scale=(0.2, 0.2, 0.01), position=(5, 5, 0))
collectibles = [coin1, coin2, coin3]

# Flag (goal)
flag = Entity(model='cube', color=color.blue, scale=(0.2, 2, 0.01), position=(10, 0, 0))

# Score display
score = 0
score_text = Text(text=f"Score: {score}", position=(-0.9, 0.9), scale=2)

# Level complete message
level_complete_text = Text(text="Level Complete!", position=(0, 0), scale=3, enabled=False)

# Collision detection function
def collision_check(a, b):
    return abs(a.x - b.x) < (a.scale_x + b.scale_x) / 2 and abs(a.y - b.y) < (a.scale_y + b.scale_y) / 2

# Game update loop
def update():
    global score

    # Reset player's ground state
    player.on_ground = False

    # Horizontal movement
    player.x += (held_keys['right arrow'] - held_keys['left arrow']) * speed * time.dt

    # Apply gravity
    player.velocity_y -= gravity * time.dt
    player.y += player.velocity_y * time.dt

    # Platform collisions
    for platform in platforms:
        if collision_check(player, platform):
            if player.velocity_y < 0:  # Player is falling
                player.y = platform.y + platform.scale_y / 2 + player.scale_y / 2
                player.velocity_y = 0
                player.on_ground = True

    # Enemy collisions
    for enemy in enemies[:]:
        if collision_check(player, enemy):
            if player.velocity_y < 0 and player.y > enemy.y:  # Player lands on enemy
                destroy(enemy)
                enemies.remove(enemy)
                player.velocity_y = 5  # Bounce effect
            else:
                print("Player hit by enemy")  # Simple damage feedback

    # Collectible collisions
    for coin in collectibles[:]:
        if collision_check(player, coin):
            destroy(coin)
            collectibles.remove(coin)
            score += 1
            score_text.text = f"Score: {score}"

    # Flag collision (level end)
    if collision_check(player, flag):
        level_complete_text.enabled = True

    # Enemy movement
    for enemy in enemies:
        enemy.x += enemy.direction * enemy.speed * time.dt
        if enemy.x > enemy.max_x or enemy.x < enemy.min_x:
            enemy.direction *= -1

    # Coin rotation for visual flair
    for coin in collectibles:
        coin.rotation_z += 100 * time.dt

    # Camera follows player horizontally like in Paper Mario
    camera.x = player.x

# Input handling for jumping
def input(key):
    if key == 'space' and player.on_ground:
        player.velocity_y = jump_strength
        player.on_ground = False

# Start the game
app.run() 
