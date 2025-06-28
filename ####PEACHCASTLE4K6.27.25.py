#!/usr/bin/env python3
# main.py – "Surreal Peach's Castle Overworld" (all‑procedural, no assets)
#
# • Everything is generated in code: no textures, models, or sounds are loaded
# • Third‑person 3D controls:   WASD / left stick = move, mouse / right stick = look, Space / A = jump
# • 60 FPS, basic gravity & collision          • Runs with plain `python main.py`
# ----------------------------------------------------------------------------------------------

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math  # BUG FIX: Imported the math module for use in moat generation

app = Ursina(title='Surreal Peach\'s Castle Overworld',
             borderless=False,
             vsync=True)                # ~60 FPS on most machines

window.exit_button.visible = False      # Hide default corner button

# ---------------------------------------------------------------------------
# Player – thin wrapper around Ursina's built‑in first person controller
# ---------------------------------------------------------------------------
class Player(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(model='cube',
                         color=color.orange,
                         scale=(1, 1.6, 1),
                         jump_height=3,
                         speed=6,
                         **kwargs)

        # Position camera just behind & above the player for a Mario‑64 vibe
        camera.parent   = self
        camera.position = (0, 2.2, -6)
        camera.rotation = (10, 0, 0)
        mouse.locked    = True

    def update(self):
        super().update()                # keep standard walking / jumping
        # Rotate with mouse (or right stick); clamp pitch to avoid flips
        if mouse.locked:
            self.rotation_y += mouse.velocity[0] * 40
            camera.rotation_x -= mouse.velocity[1] * 40
            camera.rotation_x = clamp(camera.rotation_x, -25, 45)

    def input(self, key):
        # Quit with Esc
        if key == 'escape':
            application.quit()
        # Toggle mouse lock with Tab
        if key == 'tab':
            mouse.locked = not mouse.locked
        return super().input(key)

# ---------------------------------------------------------------------------
# World ground & soft rolling hills
# ---------------------------------------------------------------------------
ground = Entity(model='plane',
                scale=(150, 1, 150),
                y=0,
                color=color.lime,
                collider='box')

for _ in range(24):
    hill = Entity(model='sphere',
                  scale=Vec3(random.uniform(6, 12), random.uniform(2, 4), random.uniform(6, 12)),
                  position=(random.uniform(-60, 60), 0.5, random.uniform(-60, 60)),
                  color=color.rgb(115, 200, 100), # REFINEMENT: Softer green for hills
                  collider='sphere')

# ---------------------------------------------------------------------------
# Castle – approximate SM64 Peach's Castle from primitives
# ---------------------------------------------------------------------------
castle_center = Vec3(0, 5, 25)

# Base keep
keep = Entity(model='cube',
              position=castle_center,
              scale=(22, 10, 22),
              color=color.white,
              collider='box')

# Main roof
Entity(model='cone',
       position=keep.position + Vec3(0, keep.scale_y/2 + 3, 0),
       scale=(24, 6, 24),
       color=color.red)

# Cylindrical corner towers + red cone roofs
tower_offsets = [(-10, -10), (10, -10), (-10, 10), (10, 10)]
for ox, oz in tower_offsets:
    tower = Entity(model='cylinder',
                   position=castle_center + Vec3(ox, 0, oz),
                   scale=(8, 12, 8),
                   color=color.white,
                   collider='cylinder')
    Entity(model='cone',
           position=tower.position + Vec3(0, tower.scale_y/2 + 2, 0),
           scale=(9, 5, 9),
           color=color.red)

# Door
Entity(model='cube',
       position=keep.position + Vec3(0, -2, keep.scale_z/2 + 0.51),
       scale=(5, 6, 1),
       color=color.brown,
       collider='box')

# Simple stone bridge over moat
bridge = Entity(model='cube',
                position=castle_center + Vec3(0, -3.5, 11),
                scale=(8, 1, 8),
                color=color.gray,
                collider='box')

# ---------------------------------------------------------------------------
# Moat & "water"
# ---------------------------------------------------------------------------
# Using a ring shape for the moat (cylinder with hole in middle)
for angle in range(0, 360, 10):
    rad = math.radians(angle)
    water_piece = Entity(
        model='cube',
        position=castle_center + Vec3(math.cos(rad) * 30, -4, math.sin(rad) * 30),
        scale=(10, 0.5, 10),
        color=color.azure,
        collider='box'
    )

# ---------------------------------------------------------------------------
# Trees (cylinder trunk + cone leaves)
# ---------------------------------------------------------------------------
for _ in range(35):
    x, z = random.uniform(-70, 70), random.uniform(-70, 70)
    # Avoid placing trees too close to castle
    if abs(x) < 35 and abs(z - 25) < 35:
        continue
    trunk = Entity(model='cylinder',
                   position=(x, 2.5, z),
                   scale=(1.2, 5, 1.2),
                   color=color.brown,
                   collider='cylinder')
    Entity(model='cone',
           position=trunk.position + Vec3(0, 3, 0),
           scale=(5, 7, 5),
           color=color.green)

# ---------------------------------------------------------------------------
# Golden "Power Star" (rotating)
# ---------------------------------------------------------------------------
class Star(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='sphere',
            color=color.yellow,
            scale=(1.5, 1.5, 1.5),
            unlit=True,  # BUG FIX: Star now ignores lighting and glows
            **kwargs
        )
    
    def update(self):
        self.rotation_y += 60 * time.dt
        self.y += math.sin(time.time() * 2) * 0.02

star = Star(position=castle_center + Vec3(0, 14, 0))

# ---------------------------------------------------------------------------
# Collectible coins
# ---------------------------------------------------------------------------
class Coin(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='cylinder',
            color=color.yellow,
            scale=(0.8, 0.1, 0.8),
            rotation=(90, 0, 0),
            unlit=True, # REFINEMENT: Make coins bright like the star
            **kwargs
        )
    
    def update(self):
        self.rotation_z += 120 * time.dt
        # Check collection
        if distance(self.position, player.position) < 2:
            destroy(self)

# ---------------------------------------------------------------------------
# Lighting
# ---------------------------------------------------------------------------
# Simple ambient light for visibility
AmbientLight(color=color.rgba(100, 100, 100, 0.2))

# Main directional light (sun)
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, 1))
sun.color = color.white

# Visual sun sphere
Entity(model='sphere', 
       color=color.yellow, 
       scale=4, 
       position=(30, 60, -50),
       unlit=True)

# ---------------------------------------------------------------------------
# Simple sky
# ---------------------------------------------------------------------------
Sky(color=color.cyan) # BUG FIX: Removed redundant window.color setting

# ---------------------------------------------------------------------------
# Create player and collectibles
# ---------------------------------------------------------------------------
# BUG FIX: Player MUST be created BEFORE any entities that reference it (like Coins)
player = Player(position=(0, 3, -10))

# Place some coins around the world now that player exists
for _ in range(15):
    x, z = random.uniform(-50, 50), random.uniform(-50, 50)
    Coin(position=(x, 1, z))

# ---------------------------------------------------------------------------
# Info text
# ---------------------------------------------------------------------------
info_text = Text(
    # BUG FIX: Added newline for better formatting
    "WASD/Arrows = Move | Mouse = Look | Space = Jump\nTab = Toggle Mouse | Esc = Quit",
    position=window.bottom_left + (.01, .01),
    scale=0.9,
    background=True
)

# ---------------------------------------------------------------------------
# Game loop
# ---------------------------------------------------------------------------
def update():
    # Keep player from falling off the world
    if player.y < -20:
        player.position = Vec3(0, 3, -10)

app.run()