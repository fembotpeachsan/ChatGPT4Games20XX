#!/usr/bin/env python3
# test.py — Stanleycraft Oneshot (Zero‑Shot Fast Edition)

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random, math

# ──────────────── GLOBAL CONFIG ────────────────
CHUNK_SIZE   = 16
RENDER_DIST  = 4           # how many chunks in X/Z each direction
AMP_Y        = 8           # terrain amplitude
SEA_LEVEL    = 0           # for simple demo; no water mesh
SURFACE_COL  = color.rgb(106, 167, 90)   # grass
DIRT_COL     = color.rgb(134,  96, 67)
STONE_COL    = color.rgb(100, 100,100)
BLOCKS       = [SURFACE_COL, DIRT_COL, STONE_COL]

# ──────────────── APP / SCENE ────────────────
app = Ursina(title='Stanleycraft Oneshot ⤫ Zero‑Shot Fast',
             borderless=False, vsync=True)
window.color = color.rgb(135, 206, 235)   # sky
window.fps_counter.enabled = True
Sky()                                     # simple sky dome

# ──────────────── NOISE ────────────────
def fast_terrain_height(x: int, z: int, seed: int) -> int:
    """
    Very light‑weight pseudo‑noise: integer column height in range ≈‑3 … +AMP_Y‑3
    Perfect for quick demos – one trig & one hash per column.
    """
    key = (x // 8, z // 8, seed)
    rnd = (hash(key) & 0xffffffff) / 0xffffffff     # deterministic [0,1)
    h   = math.sin((x + seed) * 0.11) + math.cos((z - seed) * 0.13)
    h  += rnd * 0.4                                 # sprinkle randomness
    return int(h * AMP_Y) - 4

# ──────────────── WORLD STRUCTURES ────────────────
class Voxel(Button):
    def __init__(self, position, col):
        super().__init__(
            parent   = scene,
            model    = 'cube',
            position = position,
            origin_y = 0.5,
            color    = col,
            scale    = 1,
            collider = 'box',
            highlight_color = col.tint(-.18)
        )

class Chunk:
    """Keeps track of entities for quick unload"""
    def __init__(self, cx: int, cz: int, seed: int):
        self.cx, self.cz = cx, cz
        self.entities    = []
        self.populate(seed)

    def populate(self, seed: int):
        bx, bz = self.cx * CHUNK_SIZE, self.cz * CHUNK_SIZE
        for x in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                wx, wz = bx + x, bz + z
                h      = fast_terrain_height(wx, wz, seed)

                # surface voxel
                self.entities.append(
                    Voxel((wx, h, wz), SURFACE_COL)
                )
                # thin crust of dirt/stone below surface (y‑1, y‑2)
                if h-1 >= -3:
                    self.entities.append(
                        Voxel((wx, h-1, wz), DIRT_COL)
                    )
                if h-2 >= -3:
                    self.entities.append(
                        Voxel((wx, h-2, wz), STONE_COL)
                    )

    def unload(self):
        for e in self.entities:
            destroy(e)
        self.entities.clear()

# ──────────────── GAME STATE ────────────────
chunks       = {}          # {(cx,cz): Chunk}
seed         = random.randint(0, 999_999)
player       = FirstPersonController(
    y              = 14,
    gravity        = 0.6,
    jump_height    = 1.5,
    speed          = 7,
    mouse_sensitivity = Vec2(70,70)
)
player.cursor.visible = True
current_block_color   = SURFACE_COL

# highlight mesh
highlighter = Entity(model='cube', scale=1.02, color=color.rgba(255,255,0,90),
                     visible=False)

# ──────────────── CHUNK HELPERS ────────────────
def chunk_coords(x: float, z: float):
    return int(x) // CHUNK_SIZE, int(z) // CHUNK_SIZE

def ensure_chunk(cx: int, cz: int):
    if (cx, cz) not in chunks:
        chunks[(cx, cz)] = Chunk(cx, cz, seed)

def maintain_chunk_ring():
    """Load nearby chunks, unload far ones"""
    pcx, pcz = chunk_coords(player.x, player.z)
    # load
    for dx in range(-RENDER_DIST, RENDER_DIST + 1):
        for dz in range(-RENDER_DIST, RENDER_DIST + 1):
            ensure_chunk(pcx + dx, pcz + dz)
    # unload
    for (cx, cz) in list(chunks):
        if abs(cx - pcx) > RENDER_DIST or abs(cz - pcz) > RENDER_DIST:
            chunks.pop((cx, cz)).unload()

# ──────────────── INPUT / UPDATE ────────────────
def input(key):
    # instant new world
    global seed
    if key == 'r':
        seed = random.randint(0, 999_999)
        # wipe & reload
        for ch in list(chunks.values()):
            ch.unload()
        chunks.clear()
        maintain_chunk_ring()

def update():
    maintain_chunk_ring()

    # highlight logic
    highlighter.visible = False
    if mouse.hovered_entity and isinstance(mouse.hovered_entity, Voxel):
        highlighter.position = mouse.hovered_entity.position
        highlighter.visible  = True

    # break / place
    if held_keys['left mouse'] and mouse.hovered_entity:
        destroy(mouse.hovered_entity)
    if held_keys['right mouse'] and mouse.hovered_entity:
        target = mouse.hovered_entity
        pos    = target.position + mouse.normal
        Voxel(pos, current_block_color)

app.run()
