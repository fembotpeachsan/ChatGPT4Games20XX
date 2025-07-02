from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import uniform

app = Ursina()

window.title = 'B3313 Peach\'s Castle - Ursina'
window.borderless = False
window.size = (1280,720)
Sky()

# -- GROUND --
ground = Entity(model='plane', scale=(40,1,40), color=color.lime, texture='white_cube', texture_scale=(20,20), collider='box', y=0)

# -- PATHS/DETAILS --
for i in range(6):
    Entity(model='cube', scale=(2,0.1,8), position=(8*i-16,0.05,6), color=color.gray, texture='white_cube', texture_scale=(2,8))

# -- MOAT WATER --
water = Entity(model='plane', scale=(12,1,8), position=(0,0.02,11), color=color.azure, texture='white_cube', texture_scale=(6,4), collider=None)

# -- CASTLE BASE --
castle_base = Entity(model='cube', scale=(8,5,7), position=(0,2.5,12), color=color.white, texture='white_cube', texture_scale=(4,4))
castle_door = Entity(model='cube', scale=(2,3,0.1), position=(0,1.5,8.5), color=color.brown)

# -- CASTLE TOWERS --
for x in [-3, 3]:
    # Use spheres as placeholders for towers
    Entity(model='sphere', scale=(2,6,2), position=(x,5.5,9), color=color.light_gray)
    Entity(model='sphere', scale=(2.2,3,2.2), position=(x,9,9), color=color.red)

# -- MAIN TOWER --
Entity(model='sphere', scale=(3,10,3), position=(0,7,13), color=color.light_gray)
Entity(model='sphere', scale=(3.2,4,3.2), position=(0,13,13), color=color.red)

# -- SIMPLE TREES --
for i in range(10):
    x, z = uniform(-16,16), uniform(-16,4)
    trunk = Entity(model='cube', scale=(0.3,2,0.3), position=(x,1, z), color=color.brown)
    leaves = Entity(model='sphere', scale=(1.5,1.5,1.5), position=(x,2.8, z), color=color.green)

# -- PLAYER / CAMERA --
player = FirstPersonController(y=2, position=(0,3,0), speed=7)
player.bob_amount = 0      # disables camera bounce!
player.bob_speed = 0
camera.fov = 90

def update():
    # Prevent player from falling under ground
    if player.y < 1: player.y = 2

app.run()
