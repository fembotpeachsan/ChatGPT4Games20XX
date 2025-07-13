# === UNIVERSAL GAME DEV IMPORTS (B3313/Ursina/Hybrid) ===
import os
import sys
import math
import random
import time as pytime
from functools import lru_cache

# Ursina Engine Core
from ursina import (
    Ursina, Entity, camera, window, color, held_keys, mouse, time, clamp,
    Vec2, Vec3,
    Mesh, DirectionalLight, AmbientLight,
    destroy,
    Sky, Button, Audio, scene, raycast
)

# (Optional, for extended asset/audio)
try:
    import pygame
    from pygame import mixer
    pygame.mixer.init()
    HAS_PYGAME = True
except ImportError:
    print('[warn] Pygame not found; skipping legacy audio features.')
    HAS_PYGAME = False

# Panda3D backend (optional, for deep 3D hacks)
try:
    from panda3d.core import Vec3 as PandaVec3, AmbientLight as PandaAmbientLight
    HAS_PANDA3D = True
except ImportError:
    HAS_PANDA3D = False

import platform
import pathlib
import threading

# (Optional) Modern power
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ========== REST OF YOUR ENGINE BELOW THIS LINE ==========
# --------- combine() compatibility fix ---------
def combine(entities, name=None):
    """Simplified combine function for compatibility"""
    if not entities:
        return None
    # Create a parent entity to hold all others
    parent = Entity(name=name or "combined")
    for e in entities:
        e.parent = parent
    return parent

# Custom Player Class with B3313-inspired controls (jumpy, eerie movement)
class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(model='cube', color=color.blue, scale=(1,2,1), collider='box', **kwargs)
        self.speed = 5
        self.jump_height = 10
        self.gravity = 1
        self.y_velocity = 0
        self.is_grounded = False
        camera.parent = self
        camera.position = (0, 2, -10)
        camera.rotation_x = 15

    def update(self):
        # Movement
        direction = Vec3(
            held_keys['d'] - held_keys['a'],
            0,
            held_keys['w'] - held_keys['s']
        ).normalized()
        self.position += direction * self.speed * time.dt

        # Jumping and gravity
        hit_info = raycast(self.world_position + (0,0.1,0), self.down, ignore=(self,))
        self.is_grounded = hit_info.hit and hit_info.distance < 0.1
        if self.is_grounded:
            self.y_velocity = 0
            if held_keys['space']:
                self.y_velocity = self.jump_height
        else:
            self.y_velocity -= self.gravity
        self.y += self.y_velocity * time.dt

        # Liminal vibe: subtle random teleport if out of bounds
        if self.y < -50:
            self.position = (random.uniform(-10,10), 10, random.uniform(-10,10))

# Procedural Level Generator (B3313 liminal spaces: endless rooms/platforms)
class LevelGenerator:
    def __init__(self, seed=42):
        random.seed(seed)
        self.entities = []

    def generate(self, size=10):
        # Ground platform
        ground = Entity(model='cube', color=color.gray, scale=(size*2, 1, size*2), collider='box', texture='white_cube')
        self.entities.append(ground)

        # Floating platforms (Comet Observatory style)
        for i in range(20):
            plat = Entity(model='cube', color=color.random_color(), scale=(random.uniform(2,5), 1, random.uniform(2,5)),
                          position=(random.uniform(-size,size), random.uniform(5,20), random.uniform(-size,size)),
                          collider='box')
            self.entities.append(plat)

        # Eerie walls for liminal feel
        for _ in range(5):
            wall = Entity(model='cube', color=color.dark_gray, scale=(1, 10, random.uniform(10,20)),
                          position=(random.uniform(-size,size), 5, random.uniform(-size,size)),
                          rotation=(0, random.uniform(0,360), 0), collider='box')
            self.entities.append(wall)

        # Collectibles (stars like in Galaxy)
        for _ in range(10):
            star = Button(color=color.yellow, model='sphere', scale=0.5,
                          position=(random.uniform(-size,size), random.uniform(2,15), random.uniform(-size,size)),
                          on_click=self.collect_star)
            self.entities.append(star)

        return combine(self.entities, name="level")

    def collect_star(self):
        print("Star collected!")
        destroy(self)  # 'self' here is the button instance

# Simple Enemy AI (ghost-like for B3313 horror)
class Enemy(Entity):
    def __init__(self, position=Vec3(0,0,0)):
        super().__init__(model='sphere', color=color.red, scale=2, collider='sphere', position=position)
        self.target = None

    def update(self):
        if self.target:
            direction = (self.target.position - self.position).normalized()
            self.position += direction * 3 * time.dt
            if self.intersects(self.target).hit:
                print("Game Over! Enemy caught you.")
                app.close()  # End game

# Audio Manager (threaded for background music)
class AudioManager:
    def __init__(self):
        if HAS_PYGAME:
            self.thread = threading.Thread(target=self.play_bgm)
            self.thread.start()

    def play_bgm(self):
        mixer.music.load('path/to/eerie_bgm.mp3')  # Replace with actual path or use Ursina Audio
        mixer.music.play(-1)

# Main Engine Class
class Engine:
    def __init__(self):
        self.app = Ursina(vsync=True, development_mode=False, size=(1280, 720), borderless=False, fullscreen=False)
        window.title = "B3313 Engine - Comet Observatory (Stable)"
        window.color = color.rgb(8, 10, 22)
        window.fps_counter.enabled = True
        window.entity_counter.enabled = True  # Fixed typo from original

        # Lighting
        DirectionalLight(parent=scene, y=10, z=0.5, rotation=(45, -45, 0))
        AmbientLight(color=color.rgba(100,100,100,0.5))

        # Sky
        Sky()

        # Player
        self.player = Player(position=(0,5,0))

        # Level
        gen = LevelGenerator()
        self.level = gen.generate(size=50)

        # Enemies
        for _ in range(5):
            Enemy(position=(random.uniform(-20,20), 5, random.uniform(-20,20)))
            Enemy.target = self.player  # Fixed: set target to player

        # Audio (if HAS_PYGAME:  # Typo fix
            AudioManager()

        # Optional Panda3D hack for advanced lighting
        if HAS_PANDA3D:
            panda_light = PandaAmbientLight('panda_ambient')
            panda_light.set_color((0.3, 0.3,0.3,1))
            # Integrate with Ursina scene if needed

        # Optional numpy optimization (e.g., for vector calcs)
        if HAS_NUMPY:
            print("Numpy enabled for math boosts.")

    def run(self):
        self.app.run()

# 🚀 Engine Bootstrap
if __name__ == "__main__":
    engine = Engine()
    engine.run()
