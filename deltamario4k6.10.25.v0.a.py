import pygame
import math
import random
import sys

# Initialize Pygame
pygame.init()
pygame.display.set_caption("Super Mario Bros")
screen = pygame.display.set_mode((600, 400))  # fixed window 600x400, not resizable by default

# Global game constants
WIN_WIDTH = 600
WIN_HEIGHT = 400
TILE_SIZE = 16  # size of one tile in pixels
ROWS = WIN_HEIGHT // TILE_SIZE  # number of tile rows visible
COLS = WIN_WIDTH // TILE_SIZE  # number of full tile columns visible

# Colors (RGB) for drawing pixel art and tiles
COLOR_TRANSPARENT = (0, 0, 0, 0)  # transparent (for surfaces with per-pixel alpha)
COLOR_BLUE = (0x6B, 0x8C, 0xFF)     # sky blue (background)
COLOR_RED = (0xB1, 0x34, 0x25)      # red (Mario hat/shirt)
COLOR_BROWN = (0x6A, 0x6B, 0x04)    # brown/green (Mario overalls/hair, ground)
COLOR_ORANGE = (0xE3, 0x9D, 0x25)   # orange (Mario skin)
COLOR_WHITE = (0xFC, 0xFC, 0xFC)    # white (eyes, etc.)
COLOR_BLACK = (0, 0, 0)            # black (pupils, outlines)
COLOR_GREEN = (0x00, 0xA8, 0x00)   # green (pipes)
COLOR_DARKGREEN = (0x00, 0x80, 0x00)
COLOR_GREY = (0x80, 0x80, 0x80)    # grey (castle blocks)
COLOR_YELLOW = (0xFF, 0xD8, 0x20)  # yellow (question blocks, coins)

# Helper function to create a surface with per-pixel alpha
def create_surface(width, height):
    return pygame.Surface((width, height), pygame.SRCALPHA)

# Create small Mario sprite (12x16 pixels drawn on a 12x16 surface)
small_mario_data = [
    [2,2,2,2,0,0,0,0,2,2,2,2],
    [0,2,2,2,0,0,0,0,2,2,2,0],
    [0,0,1,1,1,0,0,1,1,1,0,0],
    [3,3,1,1,1,1,1,1,1,1,3,3],
    [3,3,3,1,1,1,1,1,1,3,3,3],
    [3,3,2,1,3,1,1,3,1,2,3,3],
    [2,2,2,2,1,1,1,1,1,2,2,2],
    [0,2,2,2,1,2,1,2,2,2,2,0],
    [0,0,2,2,1,2,2,2,0,0,0,0],
    [0,0,0,3,3,3,3,3,3,3,3,0],
    [0,2,2,3,3,3,3,2,2,2,2,0],
    [0,2,3,2,2,3,3,3,2,3,3,3],
    [0,2,3,2,3,3,3,2,3,3,3,0],
    [0,0,2,2,2,3,3,2,3,2,0,0],
    [0,0,1,1,1,1,1,1,1,1,1,0],
    [0,0,0,1,1,1,1,1,0,0,0,0]
]
small_mario_surf = create_surface(12, 16)
for y, row in enumerate(small_mario_data):
    for x, pixel in enumerate(row):
        if pixel == 0:
            continue  # 0 = transparent background
        if pixel == 1:
            col = COLOR_RED
        elif pixel == 2:
            col = COLOR_BROWN
        elif pixel == 3:
            col = COLOR_ORANGE
        else:
            col = COLOR_BLACK
        small_mario_surf.set_at((x, y), col)
small_mario_surf.set_colorkey(COLOR_TRANSPARENT)

# Create big Mario sprite (16x32) by combining small Mario's head/torso and stretched legs
big_mario_surf = create_surface(16, 32)
# Place small Mario sprite centered (2px padding on each side) in top half
for y in range(16):
    for x in range(12):
        col = small_mario_surf.get_at((x, y))
        if col.a != 0:  # draw non-transparent pixels
            big_mario_surf.set_at((x+2, y), col)
# Stretch small Mario's leg portion (rows 8-15) to fill big Mario's lower 16px
for i in range(8, 16):
    for x in range(12):
        col = small_mario_surf.get_at((x, i))
        if col.a != 0:
            out_y1 = 16 + (i-8)*2
            out_y2 = out_y1 + 1
            big_mario_surf.set_at((x+2, out_y1), col)
            if out_y2 < 32:
                big_mario_surf.set_at((x+2, out_y2), col)
big_mario_surf.set_colorkey(COLOR_TRANSPARENT)

# Create a simple Goomba enemy sprite (16x16)
goomba_surf = create_surface(16, 16)
# Draw a basic mushroom-like head
for x in range(4, 12):
    goomba_surf.set_at((x, 6), COLOR_BROWN)
for x in range(3, 13):
    for y in range(7, 12):
        goomba_surf.set_at((x, y), COLOR_BROWN)
        if y == 11:
            goomba_surf.set_at((x, y), COLOR_DARKGREEN)  # feet in darker color
# Eyes
goomba_surf.set_at((6, 9), COLOR_WHITE)
goomba_surf.set_at((9, 9), COLOR_WHITE)
goomba_surf.set_at((7, 9), COLOR_BLACK)
goomba_surf.set_at((8, 9), COLOR_BLACK)
goomba_surf.set_colorkey(COLOR_TRANSPARENT)

# Create a simple Koopa Troopa sprite (16x24)
koopa_surf = create_surface(16, 24)
# Draw green shell and orange head
for x in range(4, 12):
    koopa_surf.set_at((x, 10), COLOR_GREEN)
for x in range(5, 11):
    for y in range(11, 17):
        koopa_surf.set_at((x, y), COLOR_GREEN)
# Head
for x in range(6, 10):
    for y in range(5, 9):
        koopa_surf.set_at((x, y), COLOR_ORANGE)
# Eyes
koopa_surf.set_at((7, 7), COLOR_BLACK)
koopa_surf.set_at((8, 7), COLOR_BLACK)
koopa_surf.set_colorkey(COLOR_TRANSPARENT)

# Level data definitions: Each level as a list of strings (tile map)
levels = {}

# World 1-1 (overworld)
level_1_1 = [
    "                                                                                             ",
    "                                                                                             ",
    "                                                                                             ",
    "                                                                                             ",
    "                                                                                             ",
    "                                                                                             ",
    "                                                                                             ",
    "                                                                                             ",
    "                                                                                             ",
    "                                                                                             ",
    "                                                                                             ",
    "                 C                                                                           ",
    "                                                  C                                          ",
    "                                                                                             ",
    "                       ?    B?B                           P   P   P                           ",
    "                                                B                                            ",
    "       ?                                                                                     ",
    "                                E      E                            E                        ",
    "================================     ==========================     ========================="
]
levels["1-1"] = level_1_1

# World 1-1 bonus (coin room underground via pipe)
level_1_1_bonus = [
    "                    ",
    "                    ",
    "                    ",
    "                    ",
    "                    ",
    "   C C C C C C C C   ",
    "                    ",
    "===================="
]
levels["1-1-bonus"] = level_1_1_bonus

# World 1-2 (underground)
level_1_2 = [
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "====================   =======           =======================================",
    "====================   =======           ======================================="
]
levels["1-2"] = level_1_2

# World 1-3 (sky platforms)
level_1_3 = [
    "                                                                               ",
    "                                                                               ",
    "                                                                               ",
    "                                                                               ",
    "               ====                                                           F",
    "                                                                               ",
    "       ====                ===        ===                                      ",
    "                                                                               ",
    "====================                          ================================ ",
    "                                                                               "
]
levels["1-3"] = level_1_3

# World 1-4 (castle)
level_1_4 = [
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "      E                                E                                        ",
    "====================    ====================    ===============================",
    "====================    ====================    ==============================="
]
levels["1-4"] = level_1_4

# Generate placeholder levels for worlds 2 through 8 by reusing patterns
for w in range(2, 9):
    for s in range(1, 5):
        key = f"{w}-{s}"
        if s == 2:
            # Underwater levels for 2-2 and 7-2, else reuse underground
            if w in (2, 7):
                # simple water: mostly empty space and ground at bottom
                lvl = [" " * 80 for _ in range(14)]
                lvl.append("                                                                                ")
                lvl.append("===============================================================================")
            else:
                lvl = level_1_2
        elif s == 3:
            lvl = level_1_3
        elif s == 4:
            lvl = level_1_4
        else:
            lvl = level_1_1
        levels[key] = lvl

# Game state variables
current_world = 1
current_stage = 1
lives = 3
score = 0
coins_collected = 0
time_left = 400
game_over = False

# Player class and initialization
class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.big = False
        self.fire = False
        self.invincible_timer = 0
        self.dir = 1  # 1 facing right, -1 facing left
        self.sprite = small_mario_surf
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
    def update_sprite(self):
        # Update sprite based on current state (size and facing)
        self.sprite = big_mario_surf if self.big else small_mario_surf
        if self.dir == -1:
            self.sprite = pygame.transform.flip(self.sprite, True, False)

player = Player()

# Enemy class
class Enemy:
    def __init__(self, x, y, kind="goomba"):
        self.x = x
        self.y = y
        self.vx = -1  # move left by default
        self.vy = 0
        self.kind = kind
        if kind == "goomba":
            self.sprite = goomba_surf
            self.width = 16
            self.height = 16
        elif kind == "koopa":
            self.sprite = koopa_surf
            self.width = 16
            self.height = 24
        self.on_ground = False
        self.alive = True
    def update(self, level_map):
        # Gravity
        self.vy += 0.5
        if self.vy > 5: self.vy = 5
        # Horizontal movement
        self.x += self.vx
        # Wall collision: if hitting solid tile, reverse direction
        if check_tile_collision(self.x, self.y, self.width, self.height, level_map):
            self.x -= self.vx
            self.vx *= -1
        # Vertical movement
        self.y += self.vy
        # Ground/ceiling collision
        if check_tile_collision(self.x, self.y, self.width, self.height, level_map):
            if self.vy > 0:
                # land on ground
                self.y = math.floor(self.y / TILE_SIZE) * TILE_SIZE
                self.on_ground = True
            self.vy = 0
        else:
            self.on_ground = False
        # If falls off bottom of screen, mark as dead (remove)
        if self.y > WIN_HEIGHT:
            self.alive = False

# Helper function for tile collision detection
def check_tile_collision(x, y, w, h, level_map):
    # Check all tiles overlapping the rectangle (x,y,w,h)
    top_tile = int(y // TILE_SIZE)
    bottom_tile = int((y + h - 1) // TILE_SIZE)
    left_tile = int(x // TILE_SIZE)
    right_tile = int((x + w - 1) // TILE_SIZE)
    for ty in range(top_tile, bottom_tile + 1):
        if ty < 0 or ty >= len(level_map): 
            continue
        row = level_map[ty]
        for tx in range(left_tile, right_tile + 1):
            if tx < 0 or tx >= len(row):
                continue
            tile = row[tx]
            # Solid tile types
            if tile in "=X#" or tile in ("P", "p", "B", "?", "F"):
                return True
    return False

# Current level map and enemy list
current_level_map = []
enemy_list = []

# Load level function
def load_level(world, stage, sub=None):
    global current_level_map, enemy_list, player, time_left
    key = sub if sub else f"{world}-{stage}"
    if key not in levels:
        key = "1-1"  # fallback to 1-1 if not found
        world = 1; stage = 1
    time_left = 400
    base_map = levels[key]
    current_level_map = []
    # Pad top with empty rows so total rows = ROWS (for consistent rendering)
    empty_line = " " * len(base_map[0])
    if len(base_map) < ROWS:
        pad = ROWS - len(base_map)
        current_level_map.extend([empty_line] * pad)
    current_level_map.extend(base_map)
    # Initialize player position
    player = Player()
    player.x = 2 * TILE_SIZE
    # Determine ground height at player's starting column
    start_col = int(player.x // TILE_SIZE)
    for ty in range(len(current_level_map)-1, -1, -1):
        if current_level_map[ty][start_col] in "=X":
            start_y_tile = ty
            player.y = start_y_tile * TILE_SIZE - player.height
            break
    else:
        player.y = (len(current_level_map) - 2) * TILE_SIZE  # default to bottom
    # Spawn enemies from map markers
    enemy_list = []
    for ty, row in enumerate(current_level_map):
        for tx, ch in enumerate(row):
            if ch == 'E':  # Goomba
                enemy_list.append(Enemy(tx * TILE_SIZE, ty * TILE_SIZE - 8, "goomba"))
            elif ch == 'K':  # Koopa
                enemy_list.append(Enemy(tx * TILE_SIZE, ty * TILE_SIZE - 8, "koopa"))

# Progress to next level
def next_level():
    global current_world, current_stage
    if current_stage < 4:
        current_stage += 1
    else:
        if current_world < 8:
            current_world += 1
            current_stage = 1
        else:
            # Reached 8-4, game completed
            print("YOU WIN!")
            pygame.quit()
            sys.exit(0)
    load_level(current_world, current_stage)

# Load the initial level
load_level(current_world, current_stage)

clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

running = True
while running:
    dt = clock.tick(60)  # maintain ~60 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if game_over:
                # Restart game on any key press after Game Over
                current_world = 1
                current_stage = 1
                lives = 3
                score = 0
                coins_collected = 0
                game_over = False
                load_level(current_world, current_stage)
                continue
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_z:
                # Jump (if on ground or swimming)
                if player.on_ground:
                    player.vy = -8
                    player.on_ground = False
            if event.key == pygame.K_DOWN:
                # Enter pipe downward if standing on pipe 'P'
                px = int((player.x + player.width/2) // TILE_SIZE)
                py = int((player.y + player.height) // TILE_SIZE)
                if py < len(current_level_map):
                    tile = current_level_map[py][px] if 0 <= px < len(current_level_map[py]) else ' '
                    if tile == 'P':
                        # Warp to bonus level if available (only implemented for 1-1 in this example)
                        if f"{current_world}-1-bonus" in levels:
                            load_level(current_world, current_stage, sub=f"{current_world}-1-bonus")
                        elif f"{current_world}-{current_stage}-bonus" in levels:
                            load_level(current_world, current_stage, sub=f"{current_world}-{current_stage}-bonus")
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                player.vx = 0

    if not game_over:
        # Movement input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.vx = -3
            player.dir = -1
        if keys[pygame.K_RIGHT]:
            player.vx = 3
            player.dir = 1

        # Apply gravity or swimming physics
        underwater = (current_stage == 2 and current_world in (2, 7))
        if underwater:
            # Swimming: pressing jump (space/z) gives upward thrust
            if keys[pygame.K_SPACE] or keys[pygame.K_z] or keys[pygame.K_UP]:
                player.vy -= 0.2
            else:
                player.vy += 0.2
            if player.vy > 2: player.vy = 2
            if player.vy < -2: player.vy = -2
        else:
            player.vy += 0.5  # normal gravity
            if player.vy > 8: player.vy = 8

        # Horizontal movement & collision
        player.x += player.vx
        if check_tile_collision(player.x, player.y, player.width, player.height, current_level_map):
            # If hitting wall, undo move
            player.x -= player.vx
            player.vx = 0

        # Vertical movement & collision
        player.y += player.vy
        if check_tile_collision(player.x, player.y, player.width, player.height, current_level_map):
            if player.vy > 0:
                # Land on ground
                player.on_ground = True
                player.y = math.floor(player.y / TILE_SIZE) * TILE_SIZE
            else:
                # Hit head on ceiling or block
                hit_tile_y = math.floor(player.y // TILE_SIZE)
                hit_tile_x = math.floor((player.x + player.width/2) // TILE_SIZE)
                if 0 <= hit_tile_y < len(current_level_map) and 0 <= hit_tile_x < len(current_level_map[hit_tile_y]):
                    tile = current_level_map[hit_tile_y][hit_tile_x]
                    if tile == '?':
                        # Coin block: collect coin
                        coins_collected += 1
                        score += 200
                        # Remove the '?' block (becomes empty)
                        current_level_map[hit_tile_y] = current_level_map[hit_tile_y][:hit_tile_x] + ' ' + current_level_map[hit_tile_y][hit_tile_x+1:]
                    elif tile == 'B':
                        # Breakable brick: break if big Mario
                        if player.big:
                            current_level_map[hit_tile_y] = current_level_map[hit_tile_y][:hit_tile_x] + ' ' + current_level_map[hit_tile_y][hit_tile_x+1:]
                    elif tile == 'M':
                        # Power-up block: grant mushroom (make Mario big)
                        current_level_map[hit_tile_y] = current_level_map[hit_tile_y][:hit_tile_x] + ' ' + current_level_map[hit_tile_y][hit_tile_x+1:]
                        player.big = True
                player.vy = 0
            if player.vy < 0: 
                player.vy = 0
        else:
            player.on_ground = False

        # Keep player in bounds horizontally
        if player.x < 0:
            player.x = 0

        # Check if player fell into a pit (below screen)
        if player.y > WIN_HEIGHT:
            lives -= 1
            if lives <= 0:
                game_over = True
            else:
                load_level(current_world, current_stage)
            continue

        # Update enemies
        for enemy in list(enemy_list):
            enemy.update(current_level_map)
            if not enemy.alive:
                enemy_list.remove(enemy)

        # Check collisions with enemies
        for enemy in list(enemy_list):
            if abs(player.x - enemy.x) < 16 and abs(player.y - enemy.y) < 16:
                if player.vy > 0 and player.y < enemy.y:
                    # Stomp enemy from above
                    enemy_list.remove(enemy)
                    score += 100
                    player.vy = -5  # bounce up after stomp
                else:
                    # Hit by enemy
                    if player.invincible_timer <= 0:
                        if player.big:
                            player.big = False
                            player.invincible_timer = 120  # temporary invincibility after shrink
                        else:
                            lives -= 1
                            if lives <= 0:
                                game_over = True
                            else:
                                load_level(current_world, current_stage)
                            break

        # Decrease invincibility timer if set
        if player.invincible_timer > 0:
            player.invincible_timer -= 1

        # Check for reaching flagpole/end of level
        flag_reached = False
        for ty, row in enumerate(current_level_map):
            if 'F' in row:
                fx = row.index('F')
                # If Mario passes the flagpole's x position
                if player.x >= fx * TILE_SIZE:
                    flag_reached = True
                    break
        if flag_reached:
            score += int(time_left) * 10  # bonus for remaining time
            next_level()
            continue

    # Draw background (blue sky or black for underwater/castle)
    if current_stage == 4 or (current_stage == 2 and current_world in (2, 7)):
        # castle or underwater -> black background
        screen.fill((0, 0, 0))
    else:
        screen.fill(COLOR_BLUE)

    # Simple camera: follow Mario horizontally
    cam_x = player.x - WIN_WIDTH / 2 + player.width
    if cam_x < 0: cam_x = 0
    max_cam_x = len(current_level_map[0]) * TILE_SIZE - WIN_WIDTH
    if cam_x > max_cam_x: cam_x = max_cam_x

    # Draw level tiles
    for ty, row in enumerate(current_level_map):
        for tx, ch in enumerate(row):
            draw_x = tx * TILE_SIZE - cam_x
            draw_y = ty * TILE_SIZE
            if ch in ['=', 'X']:
                # Ground or platform block
                pygame.draw.rect(screen, COLOR_BROWN if current_stage != 4 else COLOR_GREY, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
            elif ch == 'B':
                # Floating brick
                pygame.draw.rect(screen, COLOR_BROWN if current_stage != 4 else COLOR_GREY, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
            elif ch == '?':
                # Question block
                pygame.draw.rect(screen, COLOR_YELLOW, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
            elif ch == 'P' or ch == 'p':
                # Pipe (green)
                pygame.draw.rect(screen, COLOR_GREEN, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
            elif ch == 'C':
                # Coin
                pygame.draw.circle(screen, COLOR_YELLOW, (draw_x + TILE_SIZE//2, draw_y + TILE_SIZE//2), TILE_SIZE//2 - 2)
            elif ch == 'F':
                # Flagpole: draw pole and flag
                pole_x = draw_x + 3
                pole_top_y = draw_y - 10 * TILE_SIZE
                pygame.draw.line(screen, COLOR_WHITE, (pole_x, pole_top_y), (pole_x, draw_y), 2)
                pygame.draw.polygon(screen, COLOR_RED, [(pole_x, pole_top_y), (pole_x, pole_top_y + 7), (pole_x + 7, pole_top_y + 4)])

    # Draw enemies
    for enemy in enemy_list:
        ex = enemy.x - cam_x
        ey = enemy.y
        screen.blit(enemy.sprite, (ex, ey))

    # Draw Mario
    player.update_sprite()
    screen.blit(player.sprite, (player.x - cam_x, player.y))

    # Draw HUD (score, coins, world, time, lives)
    hud_text = f"MARIO {score:06d}   COINS {coins_collected:02d}   WORLD {current_world}-{current_stage}   LIVES {lives}   TIME {int(time_left)}"
    hud_surf = font.render(hud_text, True, (255, 255, 255))
    screen.blit(hud_surf, (20, 20))

    # Draw Game Over text if applicable
    if game_over:
        go_text = font.render("GAME OVER - Press any key to restart", True, (255, 255, 255))
        screen.blit(go_text, (WIN_WIDTH//2 - go_text.get_width()//2, WIN_HEIGHT//2))

    pygame.display.flip()

    # Decrement timer
    time_left -= 1/60
    if time_left <= 0:
        # Time up: lose a life
        lives -= 1
        if lives <= 0:
            game_over = True
        else:
            load_level(current_world, current_stage)
