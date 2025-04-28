import pygame
import math
import asyncio
import platform
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
TILE_SIZE = 32
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
DARK_GRAY = (100, 100, 100)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Setup display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Metal Gear Solid 1 - Pygame")

# Clock for controlling FPS
clock = pygame.time.Clock()

# Tile map (0: floor, 1: wall)
tile_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Player properties
player_x, player_y = 100, 100
player_speed = 5
player_health = 100
inventory = ['keycard']

# Enemy properties
enemy_x, enemy_y = 200, 200
enemy_speed = 2
enemy_state = 'patrol'
patrol_points = [(200, 200), (300, 200), (300, 300), (200, 300)]
current_patrol_index = 0

# Camera offset
camera_x, camera_y = 0, 0

# Generate simple sound data (since no file I/O is allowed)
def generate_footstep_sound():
    sample_rate = 44100
    duration = 0.1  # 100ms
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)
    audio = np.sin(440 * 2 * np.pi * t) * 0.5  # Simple sine wave
    audio = (audio * 32767).astype(np.int16)  # Convert to 16-bit
    stereo_audio = np.column_stack((audio, audio))  # Stereo
    return pygame.sndarray.make_sound(stereo_audio)

footstep_sound = generate_footstep_sound()

# Font for text
font = pygame.font.Font(None, 36)

def draw_tile_map():
    for y, row in enumerate(tile_map):
        for x, tile in enumerate(row):
            if tile == 0:
                pygame.draw.rect(screen, GRAY, (x * TILE_SIZE - camera_x, y * TILE_SIZE - camera_y, TILE_SIZE, TILE_SIZE))
            elif tile == 1:
                pygame.draw.rect(screen, DARK_GRAY, (x * TILE_SIZE - camera_x, y * TILE_SIZE - camera_y, TILE_SIZE, TILE_SIZE))

def draw_player():
    pygame.draw.rect(screen, BLUE, (player_x - camera_x, player_y - camera_y, 20, 30))  # Body
    pygame.draw.circle(screen, (255, 200, 150), (int(player_x + 10 - camera_x), int(player_y - 5 - camera_y)), 5)  # Head
    pygame.draw.rect(screen, BLUE, (player_x - 5 - camera_x, player_y + 10 - camera_y, 5, 15))  # Left arm
    pygame.draw.rect(screen, BLUE, (player_x + 20 - camera_x, player_y + 10 - camera_y, 5, 15))  # Right arm

def draw_enemy():
    pygame.draw.rect(screen, RED, (enemy_x - camera_x, enemy_y - camera_y, 20, 30))

def move_player(dx, dy):
    global player_x, player_y
    new_x = player_x + dx
    new_y = player_y + dy
    if not collision(new_x, new_y):
        player_x = new_x
        player_y = new_y
        footstep_sound.play()

def collision(x, y):
    tile_x = int(x // TILE_SIZE)
    tile_y = int(y // TILE_SIZE)
    if 0 <= tile_x < len(tile_map[0]) and 0 <= tile_y < len(tile_map):
        return tile_map[tile_y][tile_x] == 1
    return True

def enemy_ai():
    global enemy_x, enemy_y, enemy_state, current_patrol_index
    if enemy_state == 'patrol':
        target_x, target_y = patrol_points[current_patrol_index]
        if abs(enemy_x - target_x) < enemy_speed and abs(enemy_y - target_y) < enemy_speed:
            current_patrol_index = (current_patrol_index + 1) % len(patrol_points)
        else:
            angle = math.atan2(target_y - enemy_y, target_x - enemy_x)
            enemy_x += enemy_speed * math.cos(angle)
            enemy_y += enemy_speed * math.sin(angle)
    elif enemy_state == 'chase':
        angle = math.atan2(player_y - enemy_y, player_x - enemy_x)
        enemy_x += enemy_speed * math.cos(angle)
        enemy_y += enemy_speed * math.sin(angle)

def check_line_of_sight():
    distance = math.hypot(player_x - enemy_x, player_y - enemy_y)
    if distance < 100:  # Simple distance check for line of sight
        return True
    return False

def update_camera():
    global camera_x, camera_y
    camera_x = player_x - WINDOW_WIDTH // 2
    camera_y = player_y - WINDOW_HEIGHT // 2

def draw_hud():
    # Health bar
    pygame.draw.rect(screen, RED, (10, 10, player_health, 20))
    # Inventory
    for i, item in enumerate(inventory):
        text = font.render(item, True, WHITE)
        screen.blit(text, (10, 40 + i * 30))

def draw_dialogue(text):
    dialogue_box = pygame.Surface((WINDOW_WIDTH - 100, 100))
    dialogue_box.fill(BLACK)
    dialogue_text = font.render(text, True, WHITE)
    dialogue_box.blit(dialogue_text, (10, 10))
    screen.blit(dialogue_box, (50, WINDOW_HEIGHT - 150))

def setup():
    pass  # Initialization already handled above

def update_loop():
    global enemy_state
    
    # Player input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        move_player(0, -player_speed)
    if keys[pygame.K_s]:
        move_player(0, player_speed)
    if keys[pygame.K_a]:
        move_player(-player_speed, 0)
    if keys[pygame.K_d]:
        move_player(player_speed, 0)

    # Update enemy AI
    if check_line_of_sight():
        enemy_state = 'chase'
    else:
        enemy_state = 'patrol'
    enemy_ai()

    # Update camera
    update_camera()

    # Clear screen
    screen.fill(BLACK)

    # Draw game world
    draw_tile_map()
    draw_player()
    draw_enemy()

    # Draw HUD
    draw_hud()

    # Draw dialogue (example)
    draw_dialogue("Snake, infiltrate the facility.")

    # Update display
    pygame.display.flip()

async def main():
    setup()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
