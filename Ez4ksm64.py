from ursina import *

app = Ursina()

# Player setup with first-person controls
player = FirstPersonController()

# Skybox setup with an initial color
sky = Sky(color=color.blue)

# Debug text to display player position
debug_text = Text(text='', position=(-0.5, 0.4))

# Define a class for interactive feature buttons
class FeatureButton(Entity):
    def __init__(self, position, feature_name, action):
        super().__init__(
            model='cube',
            color=color.gray,
            position=position,
            scale=1,
            collider='box'
        )
        self.feature_name = feature_name
        self.action = action
        # Display the feature name above the button
        self.text = Text(text=feature_name, position=self.position + (0, 1, 0), scale=2)

    def input(self, key):
        if self.hovered and key == 'left mouse down':
            self.action()
            # Play a procedural tone as feedback (no external audio files)
            Audio('tone', pitch=random.uniform(0.5, 1.5), loop=False, autoplay=True)

# Feature actions inspired by HackerSM64 capabilities
def change_skybox():
    """Change the skybox to a random color."""
    sky.color = color.random_color()

def spawn_enemy():
    """Spawn a simple enemy that moves back and forth."""
    enemy = Entity(
        model='sphere',
        color=color.red,
        position=player.position + (random.uniform(-5, 5), 0, random.uniform(-5, 5))
    )
    enemy.animate_x(enemy.x + random.uniform(-2, 2), duration=2, loop=True)

def toggle_jump_fix():
    """Toggle between normal and enhanced jump height to simulate a bugfix."""
    if player.jump_height == 2:
        player.jump_height = 4
    else:
        player.jump_height = 2

def place_block():
    """Place a block in front of the player for level design."""
    block = Entity(
        model='cube',
        color=color.brown,
        position=player.position + player.forward * 2
    )
    block.y = round(block.y)  # Snap to grid

def toggle_speed_boost():
    """Toggle between normal and boosted speed for gameplay enhancement."""
    if player.speed == 10:
        player.speed = 20
    else:
        player.speed = 10

# Create interactive buttons and position them in the scene
skybox_button = FeatureButton(position=(0, 0, 5), feature_name='Change Skybox', action=change_skybox)
enemy_button = FeatureButton(position=(2, 0, 5), feature_name='Spawn Enemy', action=spawn_enemy)
jump_fix_button = FeatureButton(position=(-2, 0, 5), feature_name='Toggle Jump Fix', action=toggle_jump_fix)
block_placer = FeatureButton(position=(4, 0, 5), feature_name='Place Block', action=place_block)
speed_boost = FeatureButton(position=(-4, 0, 5), feature_name='Toggle Speed Boost', action=toggle_speed_boost)

# Ground plane for the player to walk on
ground = Entity(model='plane', scale=100, color=color.green, collider='box')

def update():
    """Update the debug text with the player's position."""
    debug_text.text = f'Position: {player.position.round(2)}'

# Run the application
app.run()
