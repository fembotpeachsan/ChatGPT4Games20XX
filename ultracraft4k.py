from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import numpy as np
from perlin_noise import PerlinNoise

# Initialize the application and set frame rate to 60 FPS
app = Ursina()
window.size = (1200, 800)
window.fps_counter.enabled = True
window.vsync = False
application.target_frame_rate = 60

# Perlin Noise Setup
terrain_noise = PerlinNoise(octaves=3, seed=random.randint(0, 1000))  # 2D Noise for terrain height
cave_noise = PerlinNoise(octaves=2, seed=random.randint(0, 1000))     # 3D Noise for cave generation

# Constants
CHUNK_SIZE = 16
RENDER_DISTANCE = 4
BLOCK_SIZE = 1
CAVE_THRESHOLD = 0.3  # Threshold for cave generation, below which space is considered air

# Block types and textures
block_types = {
    'grass': load_texture('assets/grass_block.png'),  # Ensure these textures exist
    'stone': load_texture('assets/stone_block.png'),
    'dirt': load_texture('assets/dirt_block.png'),
}

# Current selected block for placing
current_block_type = 'grass'

# Player setup
player = FirstPersonController()
player.gravity = 0.3
player.speed = 5

# Steve AI setup (initialize direction attribute)
steve = Entity(model='cube', color=color.azure, scale=(1, 2, 1), position=(10, 10, 10), collider='box')
steve.speed = 4
steve.jump_height = 2
steve.gravity = 0.5
steve.is_jumping = False
steve.jump_duration = 0.3
steve.direction = Vec3(0, 0, 0)

# Light setup
light = PointLight(parent=player, position=(0, 10, 0), color=color.white, shadows=True)

# Dictionary for chunks
chunks = {}

# Function to generate terrain and caves using Perlin noise
def generate_chunk(chunk_x, chunk_z):
    if (chunk_x, chunk_z) in chunks:
        return

    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            # Generate the terrain height using 2D Perlin noise
            world_x = chunk_x * CHUNK_SIZE + x
            world_z = chunk_z * CHUNK_SIZE + z
            height = int(terrain_noise([world_x * 0.1, world_z * 0.1]) * 10 + 10)  # Terrain height

            # Generate blocks for terrain and caves
            for y in range(height + 5):  # Add extra layers below the surface for caves
                world_y = y

                # Generate cave structure using 3D Perlin noise
                cave_value = cave_noise([world_x * 0.1, world_y * 0.1, world_z * 0.1])

                if cave_value > CAVE_THRESHOLD:  # If above threshold, consider it solid ground
                    if y == height:
                        block_texture = block_types['grass']
                    elif y > height - 3:
                        block_texture = block_types['dirt']
                    else:
                        block_texture = block_types['stone']

                    block = Entity(
                        model='cube',
                        texture=block_texture,
                        position=(world_x, y, world_z),
                        scale=BLOCK_SIZE,
                        collider='box'
                    )

    chunks[(chunk_x, chunk_z)] = True

# Function to update chunks around the player
def update_chunks():
    player_chunk_x = int(player.x // CHUNK_SIZE)
    player_chunk_z = int(player.z // CHUNK_SIZE)

    for x in range(player_chunk_x - RENDER_DISTANCE, player_chunk_x + RENDER_DISTANCE):
        for z in range(player_chunk_z - RENDER_DISTANCE, player_chunk_z + RENDER_DISTANCE):
            generate_chunk(x, z)

# Function to unload chunks outside render distance
def unload_chunks():
    player_chunk_x = int(player.x // CHUNK_SIZE)
    player_chunk_z = int(player.z // CHUNK_SIZE)
    keys_to_remove = []
    for chunk_key in chunks.keys():
        chunk_x, chunk_z = chunk_key
        if abs(chunk_x - player_chunk_x) > RENDER_DISTANCE or abs(chunk_z - player_chunk_z) > RENDER_DISTANCE:
            keys_to_remove.append(chunk_key)

    for key in keys_to_remove:
        chunk = chunks.pop(key)
        destroy(chunk)

# Block breaking function
def break_block():
    hit_info = raycast(player.position, camera.forward, distance=5)
    if hit_info.hit and hit_info.entity:
        destroy(hit_info.entity)

# Block placing function
def place_block():
    hit_info = raycast(player.position, camera.forward, distance=5)
    if hit_info.hit:
        block_position = hit_info.entity.position + hit_info.normal
        block_position = block_position // BLOCK_SIZE * BLOCK_SIZE
        Entity(model='cube', texture=block_types[current_block_type], position=block_position, collider='box')

# Input handling for block placement, breaking, and inventory opening
def input(key):
    global current_block_type
    if key == 'left mouse down':
        break_block()
    elif key == 'right mouse down':
        place_block()
    elif key == '1':
        current_block_type = 'grass'
    elif key == '2':
        current_block_type = 'stone'
    elif key == '3':
        current_block_type = 'dirt'

# Steve's AI: Jumping towards player when in range
def steve_ai():
    distance_to_player = distance(steve.position, player.position)

    if distance_to_player < 5 and not steve.is_jumping:
        steve.is_jumping = True
        steve.direction = (player.position - steve.position).normalized() * steve.speed
        steve.animate_y(steve.y + steve.jump_height, duration=steve.jump_duration, curve=curve.out_sine)
        invoke(reset_steve_jump, delay=steve.jump_duration)

def reset_steve_jump():
    steve.is_jumping = False

# Update loop
def update():
    update_chunks()
    unload_chunks()
    steve_ai()
    steve.position += steve.direction * time.dt

# Set the player's initial spawn position on top of the terrain
spawn_position = Vec3(0, 10, 0)
player.position = spawn_position

# Start the game
app.run()
