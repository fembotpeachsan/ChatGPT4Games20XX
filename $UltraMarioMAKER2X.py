import pygame
import sys
import json

# --- Config ---
WIDTH, HEIGHT = 600, 400
CELL = 20
COLS, ROWS = WIDTH // CELL, HEIGHT // CELL
PANEL_W = 150
FPS = 60

# --- Colors ---
BG = (135, 206, 235)  # Sky blue
COLOR_GRID = (200, 200, 200)
COLOR_PANEL = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)
COLORS = {
    'empty': BG,
    'ground': (139, 69, 19),
    'coin': (255, 223, 0),
    'enemy': (255, 0, 0),
    'player': (0, 0, 255)
}
TILE_TYPES = ['ground', 'coin', 'enemy', 'empty']

# --- Pygame Init ---
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Mario Maker II PC Port')
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont('Arial', 16)

# --- Level Data ---
level = [['empty' for _ in range(COLS)] for _ in range(ROWS)]
player_pos = [1.0, ROWS - 2.0]
player_vel = [0.0, 0.0]

# --- Game State ---
edit_mode = True
current_tile = 'ground'

# --- Physics ---
GRAVITY = 0.5
JUMP_SPEED = -8
MOVE_SPEED = 4

# --- Helper Functions ---

def draw_grid():
    for x in range(COLS):
        pygame.draw.line(SCREEN, COLOR_GRID, (x * CELL, 0), (x * CELL, HEIGHT))
    for y in range(ROWS):
        pygame.draw.line(SCREEN, COLOR_GRID, (0, y * CELL), (WIDTH, y * CELL))

def draw_panel():
    panel_x = WIDTH - PANEL_W
    pygame.draw.rect(SCREEN, COLOR_PANEL, (panel_x, 0, PANEL_W, HEIGHT))
    title = FONT.render('Tile Palette', True, TEXT_COLOR)
    SCREEN.blit(title, (panel_x + 10, 10))
    for i, tile in enumerate(TILE_TYPES):
        y = 40 + i * 30
        rect = pygame.Rect(panel_x + 10, y, 20, 20)
        pygame.draw.rect(SCREEN, COLORS[tile], rect)
        label = FONT.render(tile, True, TEXT_COLOR)
        SCREEN.blit(label, (panel_x + 40, y))
        if tile == current_tile:
            pygame.draw.rect(SCREEN, TEXT_COLOR, rect, 2)

def save_level(path='level.json'):
    data = {'level': level, 'player': player_pos}
    with open(path, 'w') as f:
        json.dump(data, f)

def load_level(path='level.json'):
    global level, player_pos
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        level = data.get('level', level)
        player_pos = data.get('player', player_pos)
    except Exception:
        pass

def update_player(dt):
    global player_vel, player_pos
    px, py = player_pos
    vx, vy = player_vel

    # Apply gravity
    vy += GRAVITY * dt * FPS

    # Horizontal movement
    nx = px + vx * dt * FPS
    if 0 <= nx < COLS:
        if level[int(py)][int(nx)] != 'ground':
            px = nx
        else:
            vx = 0

    # Vertical movement
    ny = py + vy * dt * FPS
    if ny >= ROWS:
        ny = ROWS - 1
        vy = 0
    if 0 <= ny < ROWS:
        if level[int(ny)][int(px)] == 'ground':
            if vy > 0:
                ny = int(ny) - 0.01
            vy = 0
        else:
            py = ny

    player_pos[0] = px
    player_pos[1] = py
    player_vel[0] = vx
    player_vel[1] = vy

# --- Main Loop ---
running = True
while running:
    dt = CLOCK.tick(FPS) / 1000.0
    SCREEN.fill(BG)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                edit_mode = not edit_mode
            elif event.key == pygame.K_s:
                save_level()
            elif event.key == pygame.K_l:
                load_level()
            elif not edit_mode and event.key == pygame.K_SPACE and abs(player_vel[1]) < 0.1:
                player_vel[1] = JUMP_SPEED

        elif event.type == pygame.MOUSEBUTTONDOWN and edit_mode:
            mx, my = pygame.mouse.get_pos()
            col, row = mx // CELL, my // CELL
            panel_x = WIDTH - PANEL_W
            if mx > panel_x:
                idx = (my - 40) // 30
                if 0 <= idx < len(TILE_TYPES):
                    current_tile = TILE_TYPES[idx]
            elif col < COLS and row < ROWS:
                level[row][col] = current_tile

    # Player input (play mode)
    keys = pygame.key.get_pressed()
    if not edit_mode:
        player_vel[0] = 0
        if keys[pygame.K_LEFT]:
            player_vel[0] = -MOVE_SPEED
        if keys[pygame.K_RIGHT]:
            player_vel[0] = MOVE_SPEED
        update_player(dt)

    # Draw level
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(SCREEN, COLORS[level[y][x]], (x * CELL, y * CELL, CELL, CELL))

    draw_grid()
    draw_panel()

    # Draw player (play mode)
    if not edit_mode:
        px, py = int(player_pos[0]), int(player_pos[1])
        pygame.draw.rect(SCREEN, COLORS['player'], (px * CELL, py * CELL, CELL, CELL))

    # Mode label
    mode = 'EDIT MODE' if edit_mode else 'PLAY MODE'
    SCREEN.blit(FONT.render(f'{mode} (E=toggle)', True, TEXT_COLOR), (10, HEIGHT - 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
# Save level on exit
