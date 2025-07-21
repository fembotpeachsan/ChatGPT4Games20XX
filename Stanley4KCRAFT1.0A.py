#!/usr/bin/env python3
# teastt.py — Stanleycraft Oneshot, Vibes Only

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random, math

app = Ursina(title='Stanleycraft Oneshot', borderless=False)
window.color = color.rgb(135, 206, 235)
window.fps_counter.enabled = True

CHUNK_SIZE = 16
RENDER_DIST = 4
AMP_Y = 8

def perlin(x, z, seed):
    random.seed(hash((x//8, z//8, seed)))
    return math.sin(x * 0.12 + seed) + math.cos(z * 0.14 - seed/2)

BLOCKS = [color.rgb(106, 167, 90), color.rgb(134, 96, 67), color.rgb(100,100,100)]

class Voxel(Button):
    def __init__(self, position, col):
        super().__init__(
            parent=scene,
            model='cube',
            origin_y=0.5,
            color=col,
            position=position,
            scale=1,
            highlight_color=col.tint(-.18),
            collider='box'
        )

chunks = {}
seed = random.randint(0,999999)
player = FirstPersonController(y=14, gravity=0.6, jump_height=1.5, speed=7)
player.cursor.visible = True

def spawn_chunk(cx, cz):
    if (cx,cz) in chunks: return
    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            wx, wz = cx*CHUNK_SIZE + x, cz*CHUNK_SIZE + z
            h = int(perlin(wx, wz, seed) * AMP_Y) - 4
            for y in range(-3, h+1):
                c = BLOCKS[min(max(y+3,0),2)]
                Voxel((wx,y,wz), c)
    chunks[(cx,cz)] = True

def update():
    cx, cz = int(player.x)//CHUNK_SIZE, int(player.z)//CHUNK_SIZE
    for dx in range(-RENDER_DIST, RENDER_DIST+1):
        for dz in range(-RENDER_DIST, RENDER_DIST+1):
            spawn_chunk(cx+dx, cz+dz)
    if held_keys['left mouse']:
        hit = mouse.hovered_entity
        if hit: destroy(hit)
    if held_keys['right mouse']:
        hit = mouse.hovered_entity
        if hit: Voxel(hit.position + mouse.normal, color.rgb(255, 222, 100))

Sky()

app.run()
