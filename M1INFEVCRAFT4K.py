from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Configure window
window.size = (600, 400)
window.title = 'Minecraft Infdev Clone'
window.borderless = False
window.fullscreen = False

# Load textures
grass_texture = load_texture('grass_block.png')
stone_texture = load_texture('stone_block.png')
dirt_texture = load_texture('dirt_block.png')
brick_texture = load_texture('brick_block.png')
sky_texture = load_texture('skybox.png')
arm_texture = load_texture('arm_texture.png')

block_pick = 1

# Define the voxel/block class
class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture=grass_texture):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=texture,
            color=color.color(0, 0, random.uniform(0.9, 1)),
            highlight_color=color.lime,
        )

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                if block_pick == 1:
                    voxel = Voxel(position=self.position + mouse.normal, texture=grass_texture)
                if block_pick == 2:
                    voxel = Voxel(position=self.position + mouse.normal, texture=stone_texture)
                if block_pick == 3:
                    voxel = Voxel(position=self.position + mouse.normal, texture=dirt_texture)
                if block_pick == 4:
                    voxel = Voxel(position=self.position + mouse.normal, texture=brick_texture)
            if key == 'right mouse down':
                destroy(self)

# Define the sky
class Sky(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            texture=sky_texture,
            scale=150,
            double_sided=True
        )

# Define the player's hand
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='cube',
            texture=arm_texture,
            scale=0.2,
            rotation=Vec3(150, -10, 0),
            position=Vec2(0.5, -0.6)
        )

    def active(self):
        self.position = Vec2(0.4, -0.5)

    def passive(self):
        self.position = Vec2(0.5, -0.6)

# Generate terrain
for x in range(-20, 21):
    for z in range(-20, 21):
        voxel = Voxel(position=(x, 0, z))

player = FirstPersonController()
sky = Sky()
hand = Hand()

def update():
    global block_pick
    if held_keys['1']: block_pick = 1
    if held_keys['2']: block_pick = 2
    if held_keys['3']: block_pick = 3
    if held_keys['4']: block_pick = 4

    if held_keys['left mouse'] or held_keys['right mouse']:
        hand.active()
    else:
        hand.passive()

app.run()
