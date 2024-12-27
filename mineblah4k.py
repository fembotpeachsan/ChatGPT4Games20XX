from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# Initialize App
app = Ursina(development_mode=False)

# Window Customization
window.title = 'Cave Game'
window.borderless = False
window.size = (800, 600)
window.exit_button.visible = False
window.fps_counter.enabled = False

# Textures and Sound
stone_texture = load_texture('stone_block.png')
dirt_texture = load_texture('dirt_block.png')
sky_texture = load_texture('skybox.png')
punch_sound = Audio('punch_sound', loop=False, autoplay=False)

block_pick = 1

# Sky
Sky(texture=sky_texture)

# Block Class
class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture=stone_texture):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=texture,
            color=color.color(0, 0, random.uniform(0.9, 1)),
            scale=0.5
        )

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                punch_sound.play()
                if block_pick == 1:
                    Voxel(position=self.position + mouse.normal, texture=stone_texture)
                elif block_pick == 2:
                    Voxel(position=self.position + mouse.normal, texture=dirt_texture)
            elif key == 'right mouse down':
                punch_sound.play()
                destroy(self)

# Generate Terrain
for z in range(20):
    for x in range(20):
        voxel = Voxel(position=(x, 0, z), texture=stone_texture)
        if random.random() > 0.8:  # Randomly add dirt blocks on top of stone
            Voxel(position=(x, 1, z), texture=dirt_texture)

# Player Controller
player = FirstPersonController()

# Update Function for Block Selection
def update():
    global block_pick

    if held_keys['1']:
        block_pick = 1
    if held_keys['2']:
        block_pick = 2

# Run the Game
app.run()
