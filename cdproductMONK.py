from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.health_bar import HealthBar
import random

app = Ursina()

def safe_entity(*args, **kwargs):
    """Create an entity with fallback in case of missing models/textures."""
    default_kwargs = {
        'model': 'cube',
        'color': color.white,
        'texture': None,
        'collider': None
    }
    merged_kwargs = {**default_kwargs, **kwargs}
    try:
        e = Entity(*args, **merged_kwargs)
        return e
    except Exception as ex:
        print(f"Entity creation failed with error: {ex}. Falling back to default entity.")
        return Entity(model='cube', color=color.white)

# Enhanced ground
ground = safe_entity(
    model='plane',
    scale=(100,1,100),
    color=color.olive,
    texture='brick',
    texture_scale=(100,100)
)
ground.collider = 'mesh'

# More detailed ancient structures
pyramid = safe_entity(
    model='pyramid',
    scale=5,
    position=(0,2.5,20),
    color=color.gray,
    texture='brick'
)
temple = safe_entity(
    model='cube',
    scale=(10,5,10),
    position=(-20,2.5,0),
    color=color.light_gray,
    texture='brick'
)
obelisk = safe_entity(
    model='cube',
    scale=(1,8,1),
    position=(20,4,0),
    color=color.dark_gray,
    texture='granite'
)

# Improved cybermonk character
cybermonk = FirstPersonController(
    position=(0,2,0),
    model='cube',
    color=color.cyan,
    scale=(1,1.8,1)
)
cybermonk.cursor = safe_entity(
    model='sphere',
    color=color.red,
    scale=0.02,
    parent=camera
)

# Cyber elements with enhanced visuals
cyber_elements = []
for i in range(10):
    pos = Vec3(random.uniform(-50,50), 0.5, random.uniform(-50,50))
    ce = safe_entity(
        model='sphere',
        color=color.cyan,
        scale=0.5,
        position=pos
    )
    try:
        ce.shader = lit_with_shadows_shader
    except Exception as ex:
        print(f"Failed to apply shader to cyber element: {ex}")
    cyber_elements.append(ce)

# Simple particle effect using Entity system
def create_particle(position):
    particle = Entity(
        model='sphere',
        color=color.cyan,
        scale=0.1,
        position=position,
        texture='circle'
    )
    particle.animate_scale(0, duration=1, curve=curve.linear)
    particle.animate_color(color.clear, duration=1)
    destroy(particle, delay=1)

# Fixed distance calculation
def calculate_distance(pos1, pos2):
    """Calculate distance between two Vec3 positions"""
    return (pos1 - pos2).length()

# Improved interaction system
def update():
    for entity in cyber_elements + [pyramid, temple, obelisk]:
        # Use the new distance calculation function
        distance = calculate_distance(cybermonk.position, entity.position)
        if distance < 3:
            if not hasattr(entity, 'original_color'):
                entity.original_color = entity.color
            entity.color = color.red
            # Create particles near player with controlled spawn rate
            if random.random() < 0.1:
                create_particle(cybermonk.position + Vec3(
                    random.uniform(-0.5, 0.5),
                    random.uniform(0, 1),
                    random.uniform(-0.5, 0.5)
                ))
        else:
            if hasattr(entity, 'original_color'):
                entity.color = entity.original_color

# Dynamic lighting
sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))

# Cybernature
for _ in range(20):
    x, z = random.uniform(-50, 50), random.uniform(-50, 50)
    cyber_tree = safe_entity(
        model='cube',
        color=color.lime,
        position=(x, 1, z),
        scale=(0.5, 3, 0.5)
    )
    cyber_leaves = safe_entity(
        model='sphere',
        color=color.green,
        position=(x, 3, z),
        scale=2
    )
    try:
        cyber_leaves.shader = lit_with_shadows_shader
    except Exception as ex:
        print(f"Failed to apply shader to cyber leaves: {ex}")

# Enhanced sky
try:
    sky = Sky(texture='sky_sunset')
except Exception as ex:
    print(f"Failed to load sky texture: {ex}, using default sky.")
    sky = Sky()

# HUD for player status
energy_bar = HealthBar(
    bar_color=color.cyan,
    roundness=0.5,
    value=100,
    position=(0.1,-0.4)
)
Text("Cyber Energy", scale=1, position=(-0.1,-0.4))

# Run the game
app.run()