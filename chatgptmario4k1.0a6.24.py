import pygame, sys, random

# --- INIT ---
pygame.init()
WIDTH, HEIGHT, FPS = 640, 400, 60
TILE = 32
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Kaizo Mario World 3 – Final Stage & Boss (No PNG)")

# --- COLORS (SNES VIBE) ---
COL = {
    "bg": (80, 120, 240),      # Sky
    "ground": (100, 60, 20),
    "muncher": (24, 160, 24),
    "muncher_eye": (0,0,0),
    "player": (255, 220, 80),
    "hat": (200, 0, 0),
    "boss": (120, 120, 120),
    "boss_mouth": (220, 50, 50),
    "fireball": (255, 60, 40),
    "goal": (240, 64, 64),
    "platform": (190, 190, 230),
    "switch": (80, 80, 250),
    "bg2": (130, 200, 240)
}

# --- LEVEL DATA ---
LEVEL_MAP = [
#012345678901234567890123
"                            ",
"    M   M     MMM   M   M   ",
"     ###    ##   ###   ###  ",
"  ##M   M   #M#     M   M#  ",
"    ## ###  # #  ### ### #  ",
"  M   M      #   M   M   #  ",
"### ####   #### ### ### ### ",
"   M     M    M   M   M     ",
"###### ###### ###### #######",
"       #   #  #   #         ",
"   M   # M #  # M #   M     ",
"###### # # #### # ######  ##",
"      M# #  M  # #         ",
"####### # ###### # #########",
" P            B            ",
"###########################",
]
LEVEL_W, LEVEL_H = len(LEVEL_MAP[0]), len(LEVEL_MAP)
BOSS_TRIGGER_X = LEVEL_MAP[14].find("B")

# --- BOSS ROOM (separate map) ---
BOSS_MAP = [
"###########################",
"#                         #",
"#                         #",
"#                         #",
"#           O             #",
"#                         #",
"#                         #",
"#       S       S         #",
"###########################",
]
BOSS_W, BOSS_H = len(BOSS_MAP[0]), len(BOSS_MAP)

# --- PLAYER STATE ---
player_x, player_y = 1, 14
player_vx, player_vy = 0.0, 0.0
on_ground = False
dead_timer = 0
mode = "level"  # "level" or "boss" or "win"
cam_x = 0

# --- BOSS STATE ---
boss_x, boss_y = 11, 3
boss_hp = 5
boss_vx = 0.16
boss_fireballs = []
boss_timer = 0
player_win = False

# --- HELPERS ---
def get_tile(mapdata, x, y):
    if 0 <= y < len(mapdata) and 0 <= x < len(mapdata[0]):
        return mapdata[int(y)][int(x)]
    return "#"

def draw_level():
    # Sky
    screen.fill(COL["bg"])
    # Tiles
    for y, row in enumerate(LEVEL_MAP):
        for x, tile in enumerate(row):
            px, py = (x-cam_x)*TILE, y*TILE
            if tile == "#":
                pygame.draw.rect(screen, COL["ground"], (px, py, TILE, TILE))
            elif tile == "M":
                pygame.draw.rect(screen, COL["muncher"], (px, py+TILE//2, TILE, TILE//2))
                pygame.draw.circle(screen, COL["muncher_eye"], (px+8, py+TILE-10), 2)
                pygame.draw.circle(screen, COL["muncher_eye"], (px+TILE-8, py+TILE-10), 2)
                pygame.draw.rect(screen, COL["muncher_eye"], (px+10, py+TILE-6, 12, 2))
            elif tile == "B":
                pygame.draw.rect(screen, (255,180,32), (px, py, TILE, TILE))
            elif tile == " ":
                pass

def draw_boss_room():
    # Boss background
    screen.fill(COL["bg2"])
    # Tiles
    for y, row in enumerate(BOSS_MAP):
        for x, tile in enumerate(row):
            px, py = x*TILE, y*TILE
            if tile == "#":
                pygame.draw.rect(screen, COL["ground"], (px, py, TILE, TILE))
            elif tile == "O":
                # Draw switch/goal
                pygame.draw.rect(screen, COL["switch"], (px+8, py+16, 16, 12))
                pygame.draw.rect(screen, (255,255,0), (px+12, py+20, 8, 4))
            elif tile == "S":
                pygame.draw.rect(screen, COL["platform"], (px, py+TILE-8, TILE, 8))

def draw_player(px, py):
    pygame.draw.rect(screen, COL["player"], (px+8, py+8, 16, 20))
    pygame.draw.rect(screen, COL["hat"], (px+12, py+4, 12, 8))

def reset_player():
    global player_x, player_y, player_vx, player_vy, dead_timer
    if mode == "level":
        player_x, player_y = 1, 14
    else:
        player_x, player_y = 5, 6
    player_vx = 0
    player_vy = 0
    dead_timer = 20

# --- MAIN GAME LOOP ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    keys = pygame.key.get_pressed()
    # Restart if dead
    if dead_timer > 0:
        dead_timer -= 1
        pygame.display.flip()
        clock.tick(FPS)
        continue

    # --- PLAYER INPUT ---
    move = 0
    if keys[pygame.K_LEFT]: move = -1
    if keys[pygame.K_RIGHT]: move = 1
    if mode == "level":
        # --- LEVEL PHYSICS ---
        if move != 0:
            player_vx = move * 2.2
        else:
            player_vx *= 0.7
        if abs(player_vx) < 0.1: player_vx = 0
        # Jump
        if keys[pygame.K_z] or keys[pygame.K_SPACE]:
            if on_ground: player_vy = -6.2
        player_vy += 0.4
        if player_vy > 7: player_vy = 7
        # Try move (X)
        next_x = player_x + player_vx * 0.08
        next_y = player_y
        if player_vx > 0 and get_tile(LEVEL_MAP, int(next_x+0.6), int(next_y)) == "#":
            next_x = int(next_x+0.6)-0.6
            player_vx = 0
        if player_vx < 0 and get_tile(LEVEL_MAP, int(next_x), int(next_y)) == "#":
            next_x = int(next_x)+1
            player_vx = 0
        # Try move (Y)
        next_y += player_vy * 0.11
        on_ground = False
        if player_vy > 0 and get_tile(LEVEL_MAP, int(next_x), int(next_y+1)) == "#":
            next_y = int(next_y+1)-1
            player_vy = 0
            on_ground = True
        if player_vy < 0 and get_tile(LEVEL_MAP, int(next_x), int(next_y)) == "#":
            next_y = int(next_y)+1
            player_vy = 0
        # Death: muncher
        if get_tile(LEVEL_MAP, int(next_x), int(next_y)) == "M":
            reset_player()
            continue
        # Boss room entry
        if int(next_y) == 14 and int(next_x) == BOSS_TRIGGER_X:
            mode = "boss"
            player_x, player_y = 5, 6
            boss_hp = 5
            boss_fireballs = []
            boss_x, boss_y = 11, 3
            boss_timer = 0
            continue
        # Win
        if get_tile(LEVEL_MAP, int(next_x), int(next_y)) == "G":
            mode = "win"
            continue
        player_x, player_y = next_x, next_y
        # Camera
        cam_x = int(player_x) - 7
        if cam_x < 0: cam_x = 0
        if cam_x > LEVEL_W - 18: cam_x = LEVEL_W - 18

        # --- DRAW ---
        draw_level()
        px, py = int((player_x-cam_x)*TILE), int(player_y*TILE)
        draw_player(px, py)
        # UI
        font = pygame.font.SysFont("Arial", 18)
        txt = font.render("KAIZO MARIO FINAL – GET TO THE B!", 1, (255,255,255))
        screen.blit(txt, (10, 4))
    elif mode == "boss":
        # --- BOSS ROOM PHYSICS ---
        # Controls/platforms
        if move != 0:
            player_vx = move * 2
        else:
            player_vx *= 0.7
        if abs(player_vx) < 0.1: player_vx = 0
        # Jump
        if (keys[pygame.K_z] or keys[pygame.K_SPACE]) and on_ground:
            player_vy = -6
        player_vy += 0.35
        if player_vy > 7: player_vy = 7
        # Horizontal collision
        next_x = player_x + player_vx * 0.07
        next_y = player_y
        if player_vx > 0 and get_tile(BOSS_MAP, int(next_x+0.6), int(next_y)) == "#":
            next_x = int(next_x+0.6)-0.6
            player_vx = 0
        if player_vx < 0 and get_tile(BOSS_MAP, int(next_x), int(next_y)) == "#":
            next_x = int(next_x)+1
            player_vx = 0
        # Platforms
        standing_on_platform = False
        if get_tile(BOSS_MAP, int(next_x), int(next_y+1)) == "S":
            standing_on_platform = True
        # Vertical collision
        next_y += player_vy * 0.12
        on_ground = False
        if player_vy > 0 and (get_tile(BOSS_MAP, int(next_x), int(next_y+1)) == "#" or standing_on_platform):
            next_y = int(next_y+1)-1
            player_vy = 0
            on_ground = True
        if player_vy < 0 and get_tile(BOSS_MAP, int(next_x), int(next_y)) == "#":
            next_y = int(next_y)+1
            player_vy = 0
        # Lava floor
        if next_y > BOSS_H-2:
            reset_player()
            continue
        # Switch/goal
        if get_tile(BOSS_MAP, int(next_x), int(next_y)) == "O":
            player_win = True
            mode = "win"
            continue
        player_x, player_y = next_x, next_y

        # --- BOSS LOGIC ---
        boss_timer += 1
        if boss_timer % 60 == 0:
            # Boss moves randomly and fires
            boss_vx = random.choice([-0.16, 0.16])
        boss_x += boss_vx
        if boss_x < 2 or boss_x > 20: boss_vx *= -1
        # Fireballs (every 50 frames)
        if boss_timer % 50 == 0:
            fy = boss_y+1
            dx = -1 if player_x < boss_x else 1
            boss_fireballs.append([boss_x+1, fy, dx*0.23, 0.0])
        # Update fireballs
        for fb in boss_fireballs:
            fb[0] += fb[2]
            fb[1] += 0.18
        # Remove offscreen fireballs
        boss_fireballs = [fb for fb in boss_fireballs if 0 <= fb[0] < BOSS_W and 0 <= fb[1] < BOSS_H]
        # Hit by fireball
        for fb in boss_fireballs:
            if abs(fb[0]-player_x)<0.5 and abs(fb[1]-player_y)<0.5:
                reset_player()
                break

        # --- DRAW ---
        draw_boss_room()
        # Boss (big rectangle)
        bx, by = int(boss_x*TILE), int(boss_y*TILE)
        pygame.draw.rect(screen, COL["boss"], (bx, by, TILE*2, TILE*2))
        # Boss face/mouth
        pygame.draw.rect(screen, COL["boss_mouth"], (bx+20, by+30, 24, 12))
        # HP bar
        pygame.draw.rect(screen, (0,0,0), (240,12,160,16))
        pygame.draw.rect(screen, (240,60,60), (242,14, (boss_hp/5)*156,12))
        # Fireballs
        for fb in boss_fireballs:
            fx, fy = int(fb[0]*TILE), int(fb[1]*TILE)
            pygame.draw.circle(screen, COL["fireball"], (fx+TILE//2, fy+TILE//2), 10)
        # Platforms/switch handled in map draw
        # Player
        px, py = int(player_x*TILE), int(player_y*TILE)
        draw_player(px, py)
        # UI
        font = pygame.font.SysFont("Arial", 18)
        txt = font.render("FINAL BOSS – TOUCH SWITCH TO WIN!", 1, (255,255,255))
        screen.blit(txt, (10, 4))
        # Boss hitbox (if you want to jump on him: optional)
        if abs(player_x-(boss_x+1))<1.5 and abs(player_y-(boss_y+2))<0.4 and player_vy>0:
            boss_hp -= 1
            player_vy = -6
            if boss_hp <= 0:
                # Reveal switch
                for y, row in enumerate(BOSS_MAP):
                    BOSS_MAP[y] = row.replace("O", " ")
                BOSS_MAP[4] = BOSS_MAP[4][:11]+"O"+BOSS_MAP[4][12:]
    elif mode == "win":
        screen.fill((0,0,0))
        font = pygame.font.SysFont("Arial", 36)
        msg = font.render("YOU WIN!", 1, (255,255,64))
        screen.blit(msg, (WIDTH//2-80, HEIGHT//2-40))
        font2 = pygame.font.SysFont("Arial", 22)
        txt = font2.render("CONGRATULATIONS! KAIZO CLEARED!", 1, (255,255,255))
        screen.blit(txt, (WIDTH//2-160, HEIGHT//2+10))
        pygame.display.flip()
        pygame.time.wait(4000)
        pygame.quit()
        sys.exit()
    pygame.display.flip()
    clock.tick(FPS)
