from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import random, sin, cos

app = Ursina()

# Window optimization for M1 Mac
window.vsync = True
window.size = (800, 600)
window.borderless = False
window.fullscreen = False
window.exit_button.visible = True
window.fps_counter.enabled = True

# Generate grass texture
grass_texture = load_texture('grass_block.png') # Replace with actual image path if available

class Voxel(Button):
    def __init__(self, position=(0,0,0)):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=grass_texture, # Use grass texture
            color=color.white, # Set color to white to avoid tinting the texture
            highlight_color=color.lime,
            scale=0.5  # Reduced scale for better performance
        )

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                voxel = Voxel(position=self.position + mouse.normal)
            if key == 'right mouse down':
                destroy(self)

class AI(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model='cube',
            color=color.red,
            scale=0.5
        )
        self.speed = 2  # Controlled AI speed

    def update(self):
        # Optimized AI movement
        if distance(self.position, player.position) < 20:  # Only update when close
            self.look_at(player)
            self.position += self.forward * time.dt * self.speed

class Player(FirstPersonController):
    def __init__(self):
        super().__init__()
        self.speed = 8  # Adjusted player speed
        self.version_text = Text(
            text='Version: 1.0.0',
            position=(-0.5,-0.4),
            scale=2,
            background=True
        )

    def update(self):
        super().update()
        if self.position.y < -20:
            self.position = (10, 10, 10)

# Optimized terrain generation
TERRAIN_SIZE = 16  # Reduced terrain size

# River implementation
river_width = 4
river_length = TERRAIN_SIZE

for z in range(TERRAIN_SIZE):
    for x in range(TERRAIN_SIZE):
        y = round(sin(x*0.3)*cos(z*0.3)*3)  # Simplified terrain formula

        # Check if within river boundaries
        if abs(x - TERRAIN_SIZE // 2) < river_width // 2 and z < river_length:
            # Create water block
            Entity(
                parent=scene,
                position=(x, -0.5, z), # Place water slightly below ground level
                model='cube',
                texture='white_cube', # Replace with water texture if available
                color=color.blue,
                scale=0.5
            )
        else:
            # Only create visible blocks
            voxel = Voxel(position=(x,y,z))
            if y > 0:
                voxel = Voxel(position=(x,y-1,z))  # One layer below surface


# Scene optimization
scene.fog_density = 0.1
scene.fog_color = color.light_gray

player = Player()
player.position = (8, 5, 8)  # Adjusted spawn position

ai = AI()
ai.position = (5, 5, 5)

def update():
    # Performance monitoring
    if held_keys['tab']:
        print(f'FPS: {1/time.dt:.0f}')

app.run()
