import pygame
import sys
import json
import os

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
    'player_start': (0, 255, 0),
    'flag': (255, 255, 255),
    'player': (0, 0, 255)
}
TILE_TYPES = ['ground', 'coin', 'enemy', 'flag', 'player_start', 'empty']

# --- Pygame Init ---
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Mario Maker II PC Port')
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont('Arial', 16)

# --- Level Data ---
def blank_level():
    return [['empty' for _ in range(COLS)] for _ in range(ROWS)]

level = blank_level()
player_start = [1, ROWS - 2]
player_pos = [float(player_start[0]), float(player_start[1])]
player_vel = [0.0, 0.0]
coins_collected = 0
total_coins = 0
game_over = False
level_complete = False

# --- Game State ---
edit_mode = True
current_tile = 'ground'

# --- Physics ---
GRAVITY = 0.5
JUMP_SPEED = -8
MOVE_SPEED = 4

LEVEL_FILE = 'level.json'

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

def save_level(path=LEVEL_FILE):
    data = {
        'level': level,
        'player_start': player_start
    }
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def load_level(path=LEVEL_FILE):
    global level, player_start, player_pos, coins_collected, total_coins, game_over, level_complete
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        level = data.get('level', blank_level())
        player_start = data.get('player_start', [1, ROWS - 2])
        player_pos[0], player_pos[1] = float(player_start[0]), float(player_start[1])
        coins_collected = 0
        total_coins = sum(row.count('coin') for row in level)
        game_over = False
        level_complete = False
    except Exception:
        pass

def reset_player():
    player_pos[0], player_pos[1] = float(player_start[0]), float(player_start[1])
    player_vel[0], player_vel[1] = 0.0, 0.0

def update_player(dt):
    global player_vel, player_pos, coins_collected, game_over, level_complete
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
        tile = level[int(ny)][int(px)]
        if tile == 'ground':
            if vy > 0:
                ny = int(ny) - 0.01
            vy = 0
        elif tile == 'coin':
            level[int(ny)][int(px)] = 'empty'
            coins_collected += 1
            py = ny
        elif tile == 'enemy':
            game_over = True
        elif tile == 'flag':
            level_complete = True
        else:
            py = ny

    player_pos[0] = px
    player_pos[1] = py
    player_vel[0] = vx
    player_vel[1] = vy

def draw_level():
    for y in range(ROWS):
        for x in range(COLS):
            tile = level[y][x]
            color = COLORS[tile]
            rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
            pygame.draw.rect(SCREEN, color, rect)
            # Draw coin as a circle
            if tile == 'coin':
                pygame.draw.circle(SCREEN, (255, 215, 0), rect.center, CELL // 3)
            # Draw enemy as a red face
            if tile == 'enemy':
                pygame.draw.circle(SCREEN, (255, 0, 0), rect.center, CELL // 2 - 2)
                pygame.draw.circle(SCREEN, (0, 0, 0), (rect.centerx - 3, rect.centery - 2), 2)
                pygame.draw.circle(SCREEN, (0, 0, 0), (rect.centerx + 3, rect.centery - 2), 2)
                pygame.draw.arc(SCREEN, (0, 0, 0), rect.inflate(-8, -8), 3.5, 6.0, 2)
            # Draw flag as a pole and flag
            if tile == 'flag':
                pygame.draw.line(SCREEN, (180, 180, 180), (rect.left + 4, rect.top + 2), (rect.left + 4, rect.bottom - 2), 3)
                pygame.draw.polygon(SCREEN, (255, 255, 0), [
                    (rect.left + 4, rect.top + 2),
                    (rect.left + 16, rect.top + 6),
                    (rect.left + 4, rect.top + 10)
                ])
            # Draw player start as a green square
            if tile == 'player_start':
                pygame.draw.rect(SCREEN, (0, 255, 0), rect.inflate(-6, -6))

def draw_player():
    px, py = int(player_pos[0]), int(player_pos[1])
    rect = pygame.Rect(px * CELL, py * CELL, CELL, CELL)
    pygame.draw.rect(SCREEN, COLORS['player'], rect)
    # Eyes
    pygame.draw.circle(SCREEN, (255, 255, 255), (rect.left + 6, rect.top + 8), 3)
    pygame.draw.circle(SCREEN, (255, 255, 255), (rect.left + 14, rect.top + 8), 3)
    pygame.draw.circle(SCREEN, (0, 0, 0), (rect.left + 6, rect.top + 8), 1)
    pygame.draw.circle(SCREEN, (0, 0, 0), (rect.left + 14, rect.top + 8), 1)

def set_player_start(x, y):
    global player_start
    # Remove old marker
    for row in range(ROWS):
        for col in range(COLS):
            if level[row][col] == 'player_start':
                level[row][col] = 'empty'
    level[y][x] = 'player_start'
    player_start = [x, y]

def handle_edit_click(mx, my):
    col, row = mx // CELL, my // CELL
    panel_x = WIDTH - PANEL_W
    if mx > panel_x:
        idx = (my - 40) // 30
        if 0 <= idx < len(TILE_TYPES):
            global current_tile
            current_tile = TILE_TYPES[idx]
    elif col < COLS and row < ROWS:
        if current_tile == 'player_start':
            set_player_start(col, row)
        else:
            # Don't allow more than one flag
            if current_tile == 'flag':
                for r in range(ROWS):
                    for c in range(COLS):
                        if level[r][c] == 'flag':
                            level[r][c] = 'empty'
            level[row][col] = current_tile

def auto_set_player_start():
    # If no player_start, set at [1, ROWS-2]
    found = False
    for y in range(ROWS):
        for x in range(COLS):
            if level[y][x] == 'player_start':
                found = True
    if not found:
        set_player_start(1, ROWS - 2)

def count_total_coins():
    return sum(row.count('coin') for row in level)

# --- Main Loop ---
load_level()
auto_set_player_start()
reset_player()
total_coins = count_total_coins()

running = True
while running:
    dt = CLOCK.tick(FPS) / 1000.0
    SCREEN.fill(BG)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_level()
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                edit_mode = not edit_mode
                if not edit_mode:
                    auto_set_player_start()
                    reset_player()
                    coins_collected = 0
                    total_coins = count_total_coins()
                    game_over = False
                    level_complete = False
            elif event.key == pygame.K_s:
                save_level()
            elif event.key == pygame.K_l:
                load_level()
                auto_set_player_start()
                reset_player()
                coins_collected = 0
                total_coins = count_total_coins()
                game_over = False
                level_complete = False
            elif not edit_mode and event.key == pygame.K_SPACE and abs(player_vel[1]) < 0.1:
                player_vel[1] = JUMP_SPEED
            elif not edit_mode and event.key == pygame.K_r:
                reset_player()
                coins_collected = 0
                game_over = False
                level_complete = False

        elif event.type == pygame.MOUSEBUTTONDOWN and edit_mode:
            mx, my = pygame.mouse.get_pos()
            handle_edit_click(mx, my)

    # Player input (play mode)
    keys = pygame.key.get_pressed()
    if not edit_mode and not game_over and not level_complete:
        player_vel[0] = 0
        if keys[pygame.K_LEFT]:
            player_vel[0] = -MOVE_SPEED
        if keys[pygame.K_RIGHT]:
            player_vel[0] = MOVE_SPEED
        update_player(dt)

    # Draw level
    draw_level()
    draw_grid()
    draw_panel()

    # Draw player (play mode)
    if not edit_mode and not game_over and not level_complete:
        draw_player()

    # Draw player start marker (edit mode)
    if edit_mode:
        for y in range(ROWS):
            for x in range(COLS):
                if level[y][x] == 'player_start':
                    pygame.draw.rect(SCREEN, (0, 255, 0), (x * CELL + 4, y * CELL + 4, CELL - 8, CELL - 8), 2)

    # UI
    mode = 'EDIT MODE' if edit_mode else 'PLAY MODE'
    SCREEN.blit(FONT.render(f'{mode} (E=toggle)', True, TEXT_COLOR), (10, HEIGHT - 20))
    if not edit_mode:
        SCREEN.blit(FONT.render(f'Coins: {coins_collected}/{total_coins}', True, (255, 223, 0)), (10, 10))
        SCREEN.blit(FONT.render('R=reset', True, TEXT_COLOR), (10, 30))
    if game_over:
        msg = FONT.render('GAME OVER! Press R to retry.', True, (255, 0, 0))
        SCREEN.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 20))
    if level_complete:
        msg = FONT.render('LEVEL COMPLETE! Press E to edit.', True, (0, 200, 0))
        SCREEN.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
