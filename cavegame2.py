from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from PIL import Image
from random import randint, uniform
from noise import pnoise2
import os

# Texture Generation
def create_texture(name, color):
    if not os.path.exists('assets'):
        os.makedirs('assets')
    img = Image.new('RGB', (16, 16), color)
    img.save(f'assets/{name}.png')

def setup_textures():
    if not os.path.exists('assets/grass.png'):  # Load textures only once
        textures = {
            'grass': (34, 139, 34),
            'dirt': (101, 67, 33),
            'stone': (128, 128, 128),
            'bedrock': (20, 20, 20),
            'wood': (157, 128, 79),
            'leaves': (20, 128, 20),
            'water': (30, 144, 255),
            'sand': (194, 178, 128)
        }
        for tex_name, tex_color in textures.items():
            create_texture(tex_name, tex_color)

# Voxel Class
class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture='grass'):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=f'assets/{texture}.png',
            color=color.color(0, 0, uniform(0.9, 1.0)),
            scale=1.0
        )
    
    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                Voxel(position=self.position + mouse.normal, texture=self.texture)
            elif key == 'right mouse down':
                destroy(self)

# World Generation
def generate_world(world_size=32, seed=0):
    bedrock_height = -4
    water_level = 1
    for z in range(-world_size // 2, world_size // 2):
        for x in range(-world_size // 2, world_size // 2):
            y = int(pnoise2(x / 20, z / 20, octaves=3, persistence=0.5, lacunarity=2.0, base=seed) * 8)
            Voxel(position=(x, y, z), texture='grass')
            for _ in range(y - 1, bedrock_height, -1):
                texture = 'dirt' if _ > water_level else 'sand' if _ == water_level else 'stone'
                Voxel(position=(x, _, z), texture=texture)
            if y <= water_level:
                Voxel(position=(x, water_level, z), texture='water')

# Main Menu
def show_main_menu():
    window.color = color.rgb(0, 128, 255)  # Set background to Minecraft sky blue
    title = Text('ChatGPT Minecraft', scale=3, origin=(0, 0), y=0.4, background=True, color=color.white)
    play_button = Button(text='Play', scale=(0.3, 0.1), position=(0, 0.1), color=color.azure)
    quit_button = Button(text='Quit', scale=(0.3, 0.1), position=(0, -0.1), color=color.red)

    def start_game():
        title.disable()
        play_button.disable()
        quit_button.disable()
        start_gameplay()

    def quit_game():
        application.quit()

    play_button.on_click = start_game
    quit_button.on_click = quit_game

# Main Game
def start_gameplay():
    setup_textures()

    player = FirstPersonController()
    player.cursor.visible = False
    player.gravity = 0.5
    player.x = player.z = 5
    player.jump_height = 1.2
    player.jump_duration = 0.5
    player.speed = 4

    sky = Entity(parent=scene, model='sphere', scale=500, double_sided=True, texture='sky_default', color=color.rgb(128, 200, 255))

    seed = randint(0, 1000)
    generate_world(world_size=16, seed=seed)

    light = DirectionalLight(parent=scene, y=100, z=-100, rotation=(45, -45, 0))
    light.color = color.rgb(255, 255, 255)

# Main Function
if __name__ == '__main__':
    app = Ursina()
    show_main_menu()
    app.run()
