from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from math import sin, cos, pi
from time import localtime

app = Ursina()
window.color = color.rgb(135, 206, 235)

# Terrain Generation
for x in range(-20, 20):
    for z in range(-20, 20):
        Entity(model='cube', collider='box', color=color.green, position=(x, -1, z), texture='grass')

player = FirstPersonController(gravity=0.5, jump_height=1.5)
player.y = 2

# Sun & Moon
sun = Entity(model='sphere', color=color.yellow, scale=3, position=(0, 20, 0))
moon = Entity(model='sphere', color=color.white66, scale=2.5, position=(0, -20, 0))

# Minecraft-like Day/Night

def update():
    t = localtime().tm_hour + localtime().tm_min / 60
    angle = ((t / 24) * 360) - 90
    rad = angle * pi / 180

    sun.y = sin(rad) * 20
    sun.x = cos(rad) * 20

    moon.y = -sun.y
    moon.x = -sun.x

    if sun.y > 0:
        window.color = lerp(color.rgb(255, 140, 0), color.rgb(135, 206, 235), sun.y / 20)
        sun.enabled = True
        moon.enabled = False
    else:
        window.color = lerp(color.rgb(10, 10, 40), color.rgb(255, 140, 0), -sun.y / 20)
        sun.enabled = False
        moon.enabled = True

app.run()
