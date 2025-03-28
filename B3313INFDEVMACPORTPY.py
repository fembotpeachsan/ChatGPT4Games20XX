from ursina import *
from ursina.shaders import basic_lighting_shader
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Settings
window.title = "Peach's Castle Grounds"
window.borderless = False
window.exit_button.visible = False
mouse.locked = True

# Environment Setup
scene.fog_color = color.rgb(135, 206, 235)
scene.fog_density = 0.01
scene.ambient_color = color.light_gray

def create_peachs_castle():
    # Main Castle Structure
    castle = Entity(
        model='cube', 
        scale=(15, 20, 15),
        texture='brick',
        color=color.rgb(255, 200, 200),
        position=(0, 10, 0),
        collider='box',
        shader=basic_lighting_shader
    )
    
    # Central Tower
    tower = Entity(
        model='cylinder', 
        scale=(5, 30, 5),
        texture='brick',
        color=color.rgb(255, 220, 220),
        position=(0, 15, 0),
        collider='mesh'
    )
    
    # Courtyard
    courtyard = Entity(
        model='plane',
        scale=(50, 1, 50),
        texture='grass',
        position=(0, 0, 0),
        collider='box'
    )
    
    # Main Door
    door = Entity(
        model='cube',
        scale=(3, 5, 0.5),
        texture='wood',
        color=color.brown,
        position=(0, 2.5, 7.5),
        collider='box'
    )
    
    # Castle Windows
    for y in [5, 10, 15]:
        for x in [-4, 4]:
            window = Entity(
                model='quad',
                scale=(2, 3),
                texture='window',
                position=(x, y, 7.4),
                rotation=(0, 180, 0)
            )
    
    # Castle Roof
    roof = Entity(
        model='cone',
        scale=(16, 8, 16),
        color=color.red,
        position=(0, 20, 0),
        rotation=(0, 0, 0)
    )

# Basic Trees
def create_trees():
    for x in [-20, 20]:
        for z in [-20, 20]:
            trunk = Entity(
                model='cylinder',
                scale=(1, 5, 1),
                color=color.brown,
                position=(x, 2.5, z)
            )
            leaves = Entity(
                model='sphere',
                scale=(3, 4, 3),
                color=color.green,
                position=(x, 5, z)
            )

# Player Controller
class CastleVisitor(FirstPersonController):
    def __init__(self):
        super().__init__(
            position=(0, 2, -20),
            speed=8,
            jump_height=2,
            gravity=1
        )
        self.mouse_sensitivity = Vec2(100, 100)

# Game Setup
create_peachs_castle()
create_trees()
player = CastleVisitor()

# Lighting
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, 1))

# Start Game
app.run()
