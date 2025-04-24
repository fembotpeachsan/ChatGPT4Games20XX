# test.py
from ursina import *
import random

app = Ursina()

# --- Player Setup ---
# Using FirstPersonController as a base for 3D movement,
# but we'll adjust the camera later for a third-person feel.
player = FirstPersonController(
    collider='box',
    jump_height=2,
    speed=5,
    origin_y=-0.5,
    color=color.blue, # Start color
)
player.collider.scale_y = 2 # Make collider taller
player.health = 3 # Simple health system
player.max_health = 3
player.coins = 0
player.can_double_jump = False
player.invulnerable_timer = 0 # Timer for invulnerability after taking damage

# --- Camera Setup ---
camera.pivot = player # Follow the player
camera.position = (0, 5, -15) # Initial offset
camera.rotation_x = 20 # Look down slightly

# --- Sky ---
sky = Sky(color=color.cyan) # SM64-ish blue sky

# --- Ground and Platforms ---
ground = Entity(model='plane', scale=100, color=color.lime, collider='box')
# Simple platforms
platform1 = Entity(model='cube', color=color.gray, position=(0, 2, 10), scale=(5, 1, 5), collider='box')
platform2 = Entity(model='cube', color=color.gray, position=(-8, 4, 15), scale=(3, 1, 3), collider='box')
platform3 = Entity(model='cube', color=color.gray, position=(8, 6, 20), scale=(4, 1, 4), collider='box')

# --- UI ---
coin_text = Text(text=f'Coins: {player.coins}', position=(-0.85, 0.45), scale=1.5, origin=(-0.5, 0))
health_text = Text(text=f'Health: {player.health}', position=(-0.85, 0.40), scale=1.5, origin=(-0.5, 0))
debug_text = Text(text='', position=(0.5, 0.45), scale=1.2, origin=(0.5, 0)) # For position/debug

# --- Enemies ---
enemies = []
class Enemy(Entity):
    def __init__(self, position=(0, 1, 0)):
        super().__init__(
            model='sphere',
            color=color.red,
            position=position,
            collider='sphere'
        )
        self.speed = 1
        self.health = 1
        enemies.append(self)

    def update(self):
        if not self.enabled:
            return

        # Basic AI: Move towards player on the XZ plane
        direction = player.position - self.position
        direction.y = 0 # Ignore vertical difference
        if direction.length() > 0.5 and direction.length() < 20: # Only move if player is within range
            self.position += direction.normalized() * self.speed * time.dt

        # Check for player collision
        if self.intersects(player).hit:
            if player.y > self.y + 0.5: # Player is above (stomp)
                self.disable()
                Audio('tone', pitch=1.5, loop=False, autoplay=True)
                player.jump() # Small bounce after stomp
                invoke(self.enable, delay=5) # Respawn after 5 seconds
            elif player.invulnerable_timer <= 0: # Player takes damage
                take_damage(1)
                Audio('tone', pitch=0.5, loop=False, autoplay=True)

# --- Coins ---
coins = []
def spawn_coin(position):
    coin = Entity(
        model='sphere',
        color=color.yellow,
        position=position,
        scale=0.5,
        collider='sphere',
        shader='lit_with_shadows_shader' # Make it look a bit nicer
    )
    coins.append(coin)
    return coin

# Spawn some initial coins
for i in range(5):
    spawn_coin(position=(random.uniform(-10, 10), 1, random.uniform(5, 20)))
spawn_coin(platform1.position + (0, 1, 0))
spawn_coin(platform2.position + (0, 1, 0))
spawn_coin(platform3.position + (0, 1, 0))


# --- Player Functions ---
def take_damage(amount):
    if player.invulnerable_timer > 0:
        return
    player.health -= amount
    player.invulnerable_timer = 1.5 # 1.5 seconds of invulnerability
    health_text.text = f'Health: {player.health}'
    if player.health <= 0:
        print_on_screen("Game Over!", position=(0,0), scale=3, duration=3)
        player.position = (0, 5, 0) # Respawn
        player.health = player.max_health
        health_text.text = f'Health: {player.health}'
    # Visual feedback for damage
    player.animate_color(color.red, duration=0.1)
    invoke(lambda: player.animate_color(color.blue, duration=0.5), delay=0.1)


# --- Feature Actions ---
def change_skybox_color():
    """Change the skybox to a random color."""
    sky.color = color.random_color()
    Audio('tone', pitch=random.uniform(0.8, 1.2), loop=False, autoplay=True)

def spawn_new_enemy():
    """Spawn a simple enemy near the player."""
    spawn_pos = player.position + (random.uniform(-10, 10), 2, random.uniform(5, 10))
    Enemy(position=spawn_pos)
    Audio('tone', pitch=0.7, loop=False, autoplay=True)

def toggle_double_jump():
    """Toggle double jump capability."""
    player.can_double_jump = not player.can_double_jump
    status = "Enabled" if player.can_double_jump else "Disabled"
    print_on_screen(f"Double Jump {status}", position=(0,0), duration=2)
    Audio('tone', pitch=1 if player.can_double_jump else 0.8, loop=False, autoplay=True)
    # Reset jump height if it was modified by the old function
    player.jump_height = 2

def create_platform():
    """Place a temporary platform in front of the player."""
    pos = player.position + player.forward * 3
    pos.y = round(pos.y) + 1 # Place slightly above player feet level
    platform = Entity(
        model='cube',
        color=color.brown,
        position=pos,
        scale=(2, 0.5, 2),
        collider='box'
    )
    Audio('tone', pitch=1.1, loop=False, autoplay=True)
    destroy(platform, delay=10) # Platform disappears after 10 seconds

def toggle_player_speed():
    """Toggle between normal and boosted speed."""
    if player.speed == 5:
        player.speed = 10
    else:
        player.speed = 5
    status = "Boosted" if player.speed == 10 else "Normal"
    print_on_screen(f"Speed {status}", position=(0,0), duration=2)
    Audio('tone', pitch=1.2 if player.speed == 10 else 0.9, loop=False, autoplay=True)

# --- Interactive Buttons (using simple Entities) ---
class FeatureButton(Entity):
    def __init__(self, position, feature_name, action):
        super().__init__(
            model='cube',
            color=color.dark_gray,
            position=position,
            scale=1,
            collider='box',
            highlight_color=color.light_gray,
            shader='lit_with_shadows_shader'
        )
        self.feature_name = feature_name
        self.action = action
        self.tooltip = Text(text=feature_name, position=self.position + (0, 1.2, 0), scale=2, origin=(0,0), enabled=False, background=True)

    def on_mouse_enter(self):
        self.tooltip.enable()

    def on_mouse_exit(self):
        self.tooltip.disable()

    def input(self, key):
        if self.hovered and key == 'left mouse down':
            self.action()
            # Play sound handled within the action itself now

# Create buttons
button_y = 0.5 # Place buttons on the ground level
skybox_button = FeatureButton(position=(0, button_y, 5), feature_name='Change Sky', action=change_skybox_color)
enemy_button = FeatureButton(position=(2.5, button_y, 5), feature_name='Spawn Enemy', action=spawn_new_enemy)
jump_button = FeatureButton(position=(-2.5, button_y, 5), feature_name='Toggle Dbl Jump', action=toggle_double_jump)
platform_button = FeatureButton(position=(5, button_y, 5), feature_name='Create Platform', action=create_platform)
speed_button = FeatureButton(position=(-5, button_y, 5), feature_name='Toggle Speed', action=toggle_player_speed)

# --- Update Function ---
def update():
    # Update UI
    debug_text.text = f'Pos: {player.position.round(2)}'
    health_text.text = f'Health: {player.health}'
    coin_text.text = f'Coins: {player.coins}'

    # Simple camera follow - adjust position based on player forward
    camera.position = player.up * 5 + player.back * 15
    camera.look_at(player)

    # Player invulnerability timer
    if player.invulnerable_timer > 0:
        player.invulnerable_timer -= time.dt
        # Flicker effect
        player.visible = int(player.invulnerable_timer * 10) % 2 == 0
    else:
        player.visible = True # Ensure player is visible when not invulnerable

    # Coin collection
    global coins
    for coin in coins:
        if coin.enabled and distance(player, coin) < 1.5:
            coin.disable()
            player.coins += 1
            Audio('tone', pitch=2, loop=False, autoplay=True, volume=0.5)
            # Optional: Respawn coin after a delay
            # invoke(coin.enable, delay=10)

    # Fall death/respawn
    if player.y < -10:
        take_damage(1) # Lose health on fall
        player.position = (0, 5, 0) # Respawn point

# --- Input Handling ---
# Basic double jump logic
jump_count = 0
def input(key):
    global jump_count
    if key == 'space' and player.can_double_jump:
        if player.grounded:
            jump_count = 1
        elif jump_count == 1:
            player.jump()
            jump_count = 2 # Prevent further jumps until grounded
    elif key == 'space' and not player.can_double_jump:
        jump_count = 0 # Reset if double jump is off

    # Reset jump count when grounded
    if player.grounded:
        jump_count = 0

# --- Settings ---
window.fps_counter.enabled = True
window.exit_button.visible = False
window.title = 'Ursina SM64-like Test'

# --- Run ---
app.run()
