#!/usr/bin/env python3
"""
Minimal Voxel Engine in Ursina @ 600x400
Tested on Python 3.x (M1 Mac)
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

# Set up a small window size (600 x 400)
window.borderless = False
window.size = (600, 400)
window.title = "Minimal Voxel Engine (600x400)"

CHUNK_SIZE = 8
MAX_HEIGHT = 3

def generate_random_color():
    """Generate a random color using HSV for vibrant colors."""
    hue = random.random()
    saturation = 1
    value = random.uniform(0.9, 1)
    return color.hsv(hue, saturation, value)

class Voxel(Button):
    def __init__(self, position=(0,0,0), block_color=color.white):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture='white_cube',
            color=block_color,
            scale=1,
            highlight_color=color.hsv(0, 1, 1),  # Bright highlight using HSV
        )

    def input(self, key):
        # Basic block placing/removing
        if self.hovered:
            if key == 'right mouse down':
                # Place a new block adjacent to the current one
                Voxel(position=self.position + mouse.normal)
            if key == 'left mouse down':
                # Destroy this block
                destroy(self)

def generate_chunk(cx, cz):
    """
    Generate a small chunk at chunk coordinates (cx, cz).
    Each chunk is deterministically generated based on its coordinates.
    """
    random.seed(cx + cz * 9999)  # Ensure deterministic chunk generation
    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            # Random height up to MAX_HEIGHT
            h = random.randint(1, MAX_HEIGHT)
            for y in range(h):
                # Generate a vibrant random color
                block_color = generate_random_color()
                Voxel(
                    position=(cx * CHUNK_SIZE + x, y, cz * CHUNK_SIZE + z),
                    block_color=block_color
                )

def main():
    app = Ursina()
    Sky()

    # Generate a basic terrain chunk at (0,0)
    generate_chunk(cx=0, cz=0)

    # Add a player to explore the voxel world
    player = FirstPersonController(
        position=(CHUNK_SIZE // 2, 10, CHUNK_SIZE // 2),
        speed=5
    )

    # Lighting for better visibility
    DirectionalLight().look_at((1, -1, -1))
    AmbientLight(color=color.rgba(100, 100, 100, 0.5))

    app.run()

if __name__ == '__main__':
    main()  # Correctly call main without a dot
