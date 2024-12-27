from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina(development_mode=True)

# Window Customization
window.title = 'My Minecraft Clone'
window.borderless = False
window.size = (800, 600)
window.exit_button.visible = False
window.fps_counter.enabled = False
window.exit_button.disable()  # Disable the default exit button

# Textures
grass_texture = load_texture('grass_block.png')
stone_texture = load_texture('stone_block.png')
brick_texture = load_texture('brick_block.png')
dirt_texture = load_texture('dirt_block.png')
sky_texture = load_texture('skybox.png')
arm_texture = load_texture('arm_texture.png')
punch_sound = Audio('punch_sound', loop=False, autoplay=False)
block_pick = 1

# Sky
Sky(texture=sky_texture)

# Hand (First-person view)
hand = Entity(
    parent=camera.ui,
    model='arm',
    texture=arm_texture,
    scale=0.2,
    rotation=Vec3(150, -10, 0),
    position=Vec2(0.4, -0.6)
)

# Block Class
class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture=grass_texture):
        super().__init__(
            parent=scene,
            position=position,
            model='block',
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
                    voxel = Voxel(position=self.position + mouse.normal, texture=grass_texture)
                elif block_pick == 2:
                    voxel = Voxel(position=self.position + mouse.normal, texture=stone_texture)
                elif block_pick == 3:
                    voxel = Voxel(position=self.position + mouse.normal, texture=brick_texture)
                elif block_pick == 4:
                    voxel = Voxel(position=self.position + mouse.normal, texture=dirt_texture)
            elif key == 'right mouse down':
                punch_sound.play()
                destroy(self)

# World Generation (Basic)
for z in range(20):
    for x in range(20):
        voxel = Voxel(position=(x, 0, z))

# Player
player = FirstPersonController()

# Update function for hand animation
def update():
    global block_pick

    if held_keys['left mouse'] or held_keys['right mouse']:
        hand.active()
    else:
        hand.passive()

    if held_keys['1']: block_pick = 1
    if held_keys['2']: block_pick = 2
    if held_keys['3']: block_pick = 3
    if held_keys['4']: block_pick = 4

# Hand Animations
def hand_active():
    hand.position = Vec2(0.3, -0.5)

def hand_passive():
    hand.position = Vec2(0.4, -0.6)

hand.active = hand_active
hand.passive = hand_passive

app.run()
