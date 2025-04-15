from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from PIL import Image
from io import BytesIO  # Kept in case needed elsewhere, but unused now

app = Ursina()
window.size = (800, 600)
camera.fov = 90
tile_size = 1.0

def image_to_texture(img):
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    return Texture(img)  # Pass PIL image directly to Texture

def make_texture(color1, color2, pattern="checker"):
    img = Image.new('RGBA', (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            if pattern == "checker":
                px[x, y] = color1 if (x + y) % 2 == 0 else color2
            elif pattern == "stripes":
                px[x, y] = color1 if x % 2 == 0 else color2
            elif pattern == "dots":
                px[x, y] = color2 if (x * y) % 13 else color1
            else:
                px[x, y] = color1
    return image_to_texture(img)

textures = {
    "grass": make_texture((95, 187, 66, 255), (77, 158, 52, 255)),
    "dirt": make_texture((133, 94, 66, 255), (115, 75, 48, 255), "dots"),
    "stone": make_texture((120, 120, 120, 255), (90, 90, 90, 255), "stripes"),
    "sand": make_texture((235, 222, 160, 255), (215, 205, 140, 255)),
    "water": make_texture((64, 164, 223, 120), (40, 120, 180, 120), "stripes"),
    "leaves": make_texture((50, 205, 50, 255), (34, 139, 34, 255), "dots"),
    "log": make_texture((139, 69, 19, 255), (110, 50, 10, 255), "stripes")
}

def place_block(x, y, z, block_type):
    Entity(model='cube', texture=textures[block_type], position=(x, y, z), scale=tile_size, collider='box')

def generate_tree(x, y, z):
    for dy in range(2):
        place_block(x, y + dy, z, "log")
    for dx in [-1, 0, 1]:
        for dz in [-1, 0, 1]:
            for dy in [2, 3]:
                place_block(x + dx, y + dy, z + dz, "leaves")
    place_block(x, y + 4, z, "leaves")

from math import sin, cos
from random import randint, random

def generate_height(x, z):
    return int(sin(x * 0.2) * 2 + cos(z * 0.2) * 2 + 8 + randint(-1, 1))

world_width, world_depth, sea_level = 32, 32, 6

def generate_world():
    for x in range(world_width):
        for z in range(world_depth):
            h = generate_height(x, z)
            top = "grass" if h > sea_level else "sand"
            for y in range(h):
                block = top if y == h - 1 else "dirt" if y > h - 4 else "stone"
                place_block(x, y, z, block)
            for y in range(h, sea_level):
                place_block(x, y, z, "water")
            if top == "grass" and random() < 0.05:
                generate_tree(x, h - 1, z)  # Adjusted to start tree at ground level

player = FirstPersonController(gravity=0.3, jump_height=1.1, speed=4)
player.position = Vec3(world_width // 2, generate_height(world_width // 2, world_depth // 2) + 2, world_depth // 2)

def update():
    if held_keys['left mouse'] and mouse.hovered_entity:
        destroy(mouse.hovered_entity)
    if held_keys['right mouse'] and mouse.hovered_entity:
        pos = mouse.hovered_entity.position + mouse.normal
        place_block(round(pos.x), round(pos.y), round(pos.z), "grass")

generate_world()
app.run()
