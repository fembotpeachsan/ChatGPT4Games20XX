from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import randint, choice
from math import floor, sin, cos

app = Ursina()
window.title = "Minecraft Beta 1.0"
window.borderless = False
window.size = (600, 400)

# Generate colors for blocks
block_colors = {
    'grass': color.rgb(50, 200, 50),
    'stone': color.rgb(100, 100, 100),
    'dirt': color.rgb(120, 72, 0),
    'sand': color.rgb(237, 201, 175),
}

# Define voxel class
class Voxel(Button):
    def __init__(self, position=(0,0,0), block_type='grass'):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture='white_cube',
            color=block_colors[block_type],
            highlight_color=color.lime
        )
        self.block_type = block_type

    def input(self, key):
        if self.hovered:
            if key == 'right mouse down':
                new_voxel = Voxel(position=self.position + mouse.normal, block_type=player.selected_block)
            if key == 'left mouse down':
                destroy(self)

# Simple terrain generator
def generate_terrain(size=20, height=5):
    for x in range(-size//2, size//2):
        for z in range(-size//2, size//2):
            y = floor(noise([x/10, z/10]) * height)
            block_type = choice(['grass', 'dirt', 'stone'])
            voxel = Voxel(position=(x, y, z), block_type=block_type)
            # Fill below terrain
            for dy in range(y):
                Voxel(position=(x, dy, z), block_type='dirt')

# Simple Perlin Noise function (simplified)
def noise(coords):
    x, z = coords
    return (sin(x * 0.8) * cos(z * 0.8) * 0.5) + 0.5

# Player setup
player = FirstPersonController()
player.selected_block = 'grass'

# Hotbar selection system
def update():
    if held_keys['1']: player.selected_block = 'grass'
    if held_keys['2']: player.selected_block = 'dirt'
    if held_keys['3']: player.selected_block = 'stone'
    if held_keys['4']: player.selected_block = 'sand'

# Generate the world
generate_terrain()

app.run()
   
