
import pygame
import sys
import asyncio
import platform

# --- Initialization ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mariomon Overworld (No PNG)")
clock = pygame.time.Clock()

# --- Constants ---
TILE_SIZE = 16
MAP_WIDTH = 20
MAP_HEIGHT = 20
FPS = 60
PLAYER_SPEED = 2

# --- Colors ---
palette = [
    (0, 0, 0, 0),    # 0: transparent
    (0, 255, 0, 255),  # 1: green (grass)
    (139, 69, 19, 255),  # 2: brown (path)
    (0, 0, 255, 255),  # 3: blue (water)
    (255, 0, 0, 255),  # 4: red (building)
]

# --- Tile Data ---
grass_tile = [[1 for _ in range(16)] for _ in range(16)]
path_tile = [[2 for _ in range(16)] for _ in range(16)]
water_tile = [[3 for _ in range(16)] for _ in range(16)]
building_tile = [[4 for _ in range(16)] for _ in range(16)]

tile_surfaces = []

# --- Map Data ---
map_data = [
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
]
walkable_tiles = [0, 1]  # grass and path

# --- Player Data ---
player_overworld_data = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,4,4,4,4,4,4,4,4,0,0,0,0],
    [0,0,0,4,4,4,4,4,4,4,4,4,4,0,0,0],
    [0,0,0,4,4,4,4,4,4,4,4,4,4,0,0,0],
    [0,0,0,4,4,4,4,4,4,4,4,4,4,0,0,0],
    [0,0,0,0,4,4,4,4,4,4,4,4,0,0,0,0],
    [0,0,0,0,0,2,2,2,2,2,2,0,0,0,0,0],
    [0,0,0,0,0,2,2,2,2,2,2,0,0,0,0,0],
    [0,0,0,0,0,2,2,2,2,2,2,0,0,0,0,0],
    [0,0,0,0,0,2,2,2,2,2,2,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
]

# --- Game State ---
player_x = 10 * TILE_SIZE
player_y = 10 * TILE_SIZE
velocity_x = 0
velocity_y = 0

# --- Helper Functions ---
def create_surface(data, palette, size):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    for y in range(len(data)):
        for x in range(len(data[0])):
            color_index = data[y][x]
            if color_index != 0:
                color = palette[color_index]
                surf.set_at((x, y), color[:3])  # Use RGB, alpha handled by SRCALPHA
    return surf

def check_collision(x, y):
    left_tile = int(x // TILE_SIZE)
    right_tile = int((x + TILE_SIZE - 1) // TILE_SIZE)
    top_tile = int(y // TILE_SIZE)
    bottom_tile = int((y + TILE_SIZE - 1) // TILE_SIZE)
    for ty in range(top_tile, bottom_tile + 1):
        for tx in range(left_tile, right_tile + 1):
            if 0 <= tx < MAP_WIDTH and 0 <= ty < MAP_HEIGHT:
                if map_data[ty][tx] not in walkable_tiles:
                    return True
    return False

# --- Setup ---
def setup():
    global tile_surfaces, player_surf
    tile_surfaces = [
        create_surface(grass_tile, palette, (TILE_SIZE, TILE_SIZE)),
        create_surface(path_tile, palette, (TILE_SIZE, TILE_SIZE)),
        create_surface(water_tile, palette, (TILE_SIZE, TILE_SIZE)),
        create_surface(building_tile, palette, (TILE_SIZE, TILE_SIZE)),
    ]
    player_surf = create_surface(player_overworld_data, palette, (TILE_SIZE, TILE_SIZE))

# --- Update Loop ---
def update_loop():
    global player_x, player_y, velocity_x, velocity_y

    # Handle input
    keys = pygame.key.get_pressed()
    velocity_x = 0
    velocity_y = 0
    if keys[pygame.K_LEFT]:
        velocity_x = -PLAYER_SPEED
    elif keys[pygame.K_RIGHT]:
        velocity_x = PLAYER_SPEED
    if keys[pygame.K_UP]:
        velocity_y = -PLAYER_SPEED
    elif keys[pygame.K_DOWN]:
        velocity_y = PLAYER_SPEED

    # Update player position with collision
    new_x = player_x + velocity_x
    if not check_collision(new_x, player_y):
        player_x = new_x
    new_y = player_y + velocity_y
    if not check_collision(player_x, new_y):
        player_y = new_y

    # Update camera
    if MAP_WIDTH * TILE_SIZE <= WIDTH:
        cam_x = (MAP_WIDTH * TILE_SIZE - WIDTH) / 2
    else:
        ideal_cam_x = player_x - WIDTH / 2
        cam_x = max(0, min(ideal_cam_x, MAP_WIDTH * TILE_SIZE - WIDTH))

    if MAP_HEIGHT * TILE_SIZE <= HEIGHT:
        cam_y = (MAP_HEIGHT * TILE_SIZE - HEIGHT) / 2
    else:
        ideal_cam_y = player_y - HEIGHT / 2
        cam_y = max(0, min(ideal_cam_y, MAP_HEIGHT * TILE_SIZE - HEIGHT))

    # Render
    screen.fill((0, 0, 0))
    start_tx = max(0, int(cam_x // TILE_SIZE))
    end_tx = min(MAP_WIDTH, int((cam_x + WIDTH) // TILE_SIZE) + 1)
    start_ty = max(0, int(cam_y // TILE_SIZE))
    end_ty = min(MAP_HEIGHT, int((cam_y + HEIGHT) // TILE_SIZE) + 1)
    for ty in range(start_ty, end_ty):
        for tx in range(start_tx, end_tx):
            tile_index = map_data[ty][tx]
            tile_surf = tile_surfaces[tile_index]
            screen_x = tx * TILE_SIZE - cam_x
            screen_y = ty * TILE_SIZE - cam_y
            screen.blit(tile_surf, (screen_x, screen_y))

    player_screen_x = player_x - cam_x
    player_screen_y = player_y - cam_y
    screen.blit(player_surf, (player_screen_x, player_screen_y))

    pygame.display.flip()

# --- Main Loop ---
async def main():
    setup()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
