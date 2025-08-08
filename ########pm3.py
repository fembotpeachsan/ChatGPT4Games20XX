import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import math
import random
import pygame

# ============================================================
# Paper Mario x SMB3 — "Paper Bros 3" (Files=OFF, Vibes=ON, 60 FPS)
# Single-file prototype: placeholder paper art, SMB3-ish physics,
# partner field abilities, world map, no external assets.
# ============================================================

# -------------------------
# Config / Constants
# -------------------------
W, H = 1024, 576
SCALE = 1
TILE = 32
FPS = 60
GRAVITY = 0.7
JUMP_VEL = -12.5
JUMP_HOLD_GRAVITY_REDUCE = 0.35  # holding jump slightly lightens gravity
COYOTE_TIME = 0.12
JUMP_BUFFER = 0.12

BASE_ACC = 0.8
BASE_FRICTION = 0.85
BASE_MAXSPEED = 5.0
RUN_BOOST = 2.3
RUN_ACC_MULT = 1.25
PMETER_GAIN = 0.02
PMETER_DECAY = 0.015

PLAYER_W, PLAYER_H = 22, 30

# Partner timings
BOMB_FUSE = 1.5
SHADOW_TIME = 1.35
LAKITU_TIME = 0.9
GUST_TIME = 0.28
GUST_RANGE = 96
FLUTTER_TIME = 0.35
FLUTTER_GRAVITY = 0.22

# Level width in tiles
LEVEL_W_TILES = 64
LEVEL_H_TILES = H // TILE

# -------------------------
# Helpers
# -------------------------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def sign(x):
    return -1 if x < 0 else (1 if x > 0 else 0)

def rect_from_xywh(x, y, w, h):
    return pygame.Rect(int(x), int(y), int(w), int(h))

# -------------------------
# Themes / Colors (paper vibes)
# -------------------------
def lerp(a, b, t): return a + (b - a) * t

THEMES = [
    ("Verdant Valley",   ((78, 201, 176), (178, 255, 222), (28, 120, 90))),
    ("Scorching Dunes",  ((255, 198, 109), (255, 239, 178), (196, 140, 52))),
    ("Azure Isles",      ((119, 200, 255), (200, 240, 255), (40, 120, 196))),
    ("Whisper Woods",    ((136, 170, 120), (210, 230, 200), (60, 90, 70))),
    ("Skyward Skies",    ((180, 220, 255), (240, 250, 255), (120, 160, 210))),
    ("Frosted Fjords",   ((200, 230, 255), (235, 245, 255), (130, 170, 210))),
    ("Cogs & Pipes",     ((190, 180, 170), (220, 210, 200), (90, 85, 80))),
    ("Bowser’s Realm",   ((255, 120, 90),  (255, 180, 150), (160, 60, 40))),
]

# Tile legend (characters):
# ' ' empty
# '#' solid
# '=' ground
# '~' lava/water hazard (hurts)
# '^' spikes hazard (hurts)
# 'B' cracked (bomb breaks)
# 'S' switch (toggles Gates)
# 'G' gate (solid when gates_closed==True)
# 'L' leafy paper cover (wind gust removes)
# '|' shadow gate (passable only during shadow)
# 'X' goal
# 'C' checkpoint (not fully used here)
# 'E' enemy (simple goomba)
# 'P' player start
# '?' coin block (here: coin collectible)
# '.' background filler (empty)
SOLIDS = {'#', '=', 'G', 'B'}
HAZARDS = {'~', '^'}
SHADOW_ONLY = {'|'}  # passable unless not shadowing
REMOVABLE_BY_WIND = {'L'}

# -------------------------
# Simple Level Generator
# -------------------------
def generate_level(seed=0, theme_idx=0):
    random.seed(seed)
    # Build a simple scrolling course with ground, platforms, a switch-gate, bomb wall, etc.
    w, h = LEVEL_W_TILES, LEVEL_H_TILES
    grid = [['.' for _ in range(w)] for _ in range(h)]
    # Baseline ground
    ground_y = h - 3
    for x in range(w):
        grid[ground_y][x] = '='
        grid[ground_y+1][x] = '='
        grid[ground_y+2][x] = '='

    # Place hazards pits
    for pit in range(3):
        px = random.randint(6 + pit*18, 10 + pit*18)
        for x in range(px, px+3):
            grid[ground_y][x] = ' '
            grid[ground_y+1][x] = ' '
            grid[ground_y+2][x] = ' '

        # Fill bottom with lava/water
        grid[h-1][px+1] = '~'

    # Platforms
    for i in range(12):
        px = random.randint(4, w-8)
        py = random.randint(5, ground_y-3)
        for x in range(px, px+random.randint(2,5)):
            if 0 < x < w and 0 < py < h:
                grid[py][x] = '#'

    # Cracked wall (bomb)
    bx = random.randint(18, 22)
    for y in range(ground_y-4, ground_y-1):
        grid[y][bx] = 'B'
        grid[y][bx+1] = 'B'

    # Switch + gate segment
    sx = random.randint(28, 31)
    grid[ground_y-1][sx] = 'S'
    for gx in range(sx+3, sx+3+4):
        for gy in range(ground_y-5, ground_y):
            if gy % 2 == 0:
                grid[gy][gx] = 'G'

    # Shadow gate shortcut
    for y in range(ground_y-6, ground_y-2):
        grid[y][sx-8] = '|'

    # Leafy cover to blow away
    for x in range(40, 46):
        grid[ground_y-2][x] = 'L'

    # Coin blocks
    for x in [8, 12, 16, 35, 38]:
        grid[ground_y-5][x] = '?'

    # Enemies
    for i in range(8):
        ex = random.randint(6, w-4)
        grid[ground_y-1][ex] = 'E'

    # Goal
    grid[ground_y-6][w-6] = 'X'

    # Player start
    grid[ground_y-4][3] = 'P'

    return grid

# -------------------------
# Entity classes
# -------------------------
class Goomba:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx = random.choice([-1.0, 1.0])
        self.vy = 0
        self.w, self.h = 24, 22
        self.alive = True
        self.on_ground = False
    @property
    def rect(self):
        return rect_from_xywh(self.x, self.y, self.w, self.h)

class Shell:
    def __init__(self, x, y, dir_):
        self.x, self.y = x, y
        self.vx = 7.0 * dir_
        self.vy = 0
        self.w, self.h = 20, 16
        self.active = True
    @property
    def rect(self):
        return rect_from_xywh(self.x, self.y, self.w, self.h)

class Bomb:
    def __init__(self, x, y, vx, vy, fuse=BOMB_FUSE):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.w, self.h = 16, 16
        self.timer = fuse
        self.exploded = False
    @property
    def rect(self):
        return rect_from_xywh(self.x, self.y, self.w, self.h)

class Explosion:
    def __init__(self, cx, cy, radius=48, time=0.24):
        self.cx, self.cy = cx, cy
        self.radius = radius
        self.time = time

class Gust:
    def __init__(self, rect, time=GUST_TIME):
        self.rect = rect
        self.time = time

class YoshiMount:
    def __init__(self):
        self.active = False

# -------------------------
# Player
# -------------------------
class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx, self.vy = 0.0, 0.0
        self.w, self.h = PLAYER_W, PLAYER_H
        self.facing = 1
        self.on_ground = False
        self.coyote = 0.0
        self.jump_buf = 0.0
        self.run = False
        self.p_meter = 0.0
        self.hp = 3
        self.inv = 0.0
        # Partner state flags
        self.shadow_timer = 0.0
        self.lakitu_timer = 0.0
        self.flutter_timer = 0.0
        self.riding_yoshi = False

    @property
    def rect(self):
        return rect_from_xywh(self.x, self.y, self.w, self.h)

# -------------------------
# Partners
# -------------------------
class PartnerBase:
    name = "Base"
    def use(self, game, level, player):
        pass

class KoopaPartner(PartnerBase):
    name = "Koopa (Shell)"
    def use(self, game, level, player):
        # Fire a shell forward
        spawn_x = player.x + (player.w//2) + player.facing*20
        spawn_y = player.y + player.h//2
        level.shells.append(Shell(spawn_x, spawn_y, player.facing))

class BombPartner(PartnerBase):
    name = "Bob-omb (Throw)"
    def use(self, game, level, player):
        # Throw arc
        vx = 4.0 * player.facing
        vy = -7.5
        level.bombs.append(Bomb(player.x + player.w//2, player.y, vx, vy, BOMB_FUSE))

class WindPartner(PartnerBase):
    name = "Flurry (Gust)"
    def use(self, game, level, player):
        # Create gust rect ahead
        r = player.rect.copy()
        r.width = GUST_RANGE
        if player.facing < 0:
            r.left -= GUST_RANGE
        else:
            r.right += GUST_RANGE
        level.gusts.append(Gust(r, GUST_TIME))

class YoshiPartner(PartnerBase):
    name = "Yoshi (Ride/Flutter)"
    def use(self, game, level, player):
        # Toggle ride; when airborne, enable flutter window
        player.riding_yoshi = not player.riding_yoshi
        if player.riding_yoshi:
            player.flutter_timer = FLUTTER_TIME

class ShadowPartner(PartnerBase):
    name = "Vivian (Shadow)"
    def use(self, game, level, player):
        player.shadow_timer = SHADOW_TIME

class LakituPartner(PartnerBase):
    name = "Lakitu (Lift)"
    def use(self, game, level, player):
        player.lakitu_timer = LAKITU_TIME

PARTNERS = [KoopaPartner(), BombPartner(), WindPartner(),
            YoshiPartner(), ShadowPartner(), LakituPartner()]

# -------------------------
# Level container
# -------------------------
class Level:
    def __init__(self, grid, theme_idx=0):
        self.grid = grid
        self.theme_idx = theme_idx
        self.gates_closed = True
        self.entities = []
        self.goombas = []
        self.shells = []
        self.bombs = []
        self.explosions = []
        self.gusts = []
        self.coins = 0
        self.goal_reached = False
        self.checkpoints = []
        self.player_start = self.find_player_start()
        self.populate()

    def find_player_start(self):
        for y,row in enumerate(self.grid):
            for x,ch in enumerate(row):
                if ch == 'P':
                    return x*TILE+4, y*TILE+2
        return 64, 64

    def populate(self):
        for y,row in enumerate(self.grid):
            for x,ch in enumerate(row):
                if ch == 'E':
                    self.goombas.append(Goomba(x*TILE+4, y*TILE+8))

    def tile_at(self, tx, ty):
        if 0 <= ty < len(self.grid) and 0 <= tx < len(self.grid[0]):
            return self.grid[ty][tx]
        return ' '

    def set_tile(self, tx, ty, ch):
        if 0 <= ty < len(self.grid) and 0 <= tx < len(self.grid[0]):
            self.grid[ty][tx] = ch

    def rect_collides_solid(self, r, player_shadowing=False):
        # collision with solid tiles, considering gates and shadow-only tiles
        tiles = []
        min_tx = r.left // TILE
        max_tx = r.right // TILE
        min_ty = r.top // TILE
        max_ty = r.bottom // TILE
        for ty in range(min_ty, max_ty+1):
            for tx in range(min_tx, max_tx+1):
                ch = self.tile_at(tx, ty)
                solid = False
                if ch in SOLIDS:
                    if ch == 'G':
                        solid = self.gates_closed
                    else:
                        solid = True
                if ch in SHADOW_ONLY:
                    # solid unless player is shadowing
                    solid = not player_shadowing
                if solid:
                    tiles.append(pygame.Rect(tx*TILE, ty*TILE, TILE, TILE))
        for t in tiles:
            if r.colliderect(t):
                return True
        return False

    def hazards_overlap(self, r):
        min_tx = r.left // TILE
        max_tx = r.right // TILE
        min_ty = r.top // TILE
        max_ty = r.bottom // TILE
        for ty in range(min_ty, max_ty+1):
            for tx in range(min_tx, max_tx+1):
                ch = self.tile_at(tx, ty)
                if ch in HAZARDS:
                    if r.colliderect(pygame.Rect(tx*TILE, ty*TILE, TILE, TILE)):
                        return True
        return False

# -------------------------
# Game
# -------------------------
class Game:
    def __init__(self):
        pygame.init()
        flags = pygame.SCALED
        self.screen = pygame.display.set_mode((W, H), flags)
        pygame.display.set_caption("Paper Bros 3 — Files:OFF  Vibes:ON  60FPS")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MAP"
        self.vibes = True
        self.world_idx = 0
        self.map_cursor = 0
        # Create worlds (8). Each world has a seed so the layout changes.
        self.worlds = []
        for i in range(8):
            grid = generate_level(seed=100+i*7, theme_idx=i)
            self.worlds.append(grid)
        # Progress
        self.cleared_worlds = set()  # e.g., {0, 1}
        # Build first level
        self.level = None
        self.player = None
        # Partners / selection
        self.partners = PARTNERS[:]  # all available from start
        self.partner_idx = 0
        # Confetti vibe particles
        self.confetti = []

    # ---------------------
    # Main Loop
    # ---------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                if e.type == pygame.KEYDOWN and e.key == pygame.K_v:
                    self.vibes = not self.vibes

            if self.state == "MAP":
                self.update_map(dt)
                self.draw_map(dt)
            elif self.state == "LEVEL":
                self.update_level(dt)
                self.draw_level(dt)
            elif self.state == "PAUSE":
                self.draw_pause()

            pygame.display.flip()
        pygame.quit()

    # ---------------------
    # Map State
    # ---------------------
    def update_map(self, dt):
        keys = pygame.key.get_pressed()
        moved = False
        if keys[pygame.K_LEFT]:
            self.map_cursor = max(0, self.map_cursor - 1); moved=True
        if keys[pygame.K_RIGHT]:
            self.map_cursor = min(7, self.map_cursor + 1); moved=True
        if keys[pygame.K_UP]:
            self.map_cursor = max(0, self.map_cursor - 2); moved=True
        if keys[pygame.K_DOWN]:
            self.map_cursor = min(7, self.map_cursor + 2); moved=True

        # Snap input to avoid repeat too fast
        if moved:
            pygame.time.delay(120)

        # Number keys jump world
        for i in range(8):
            if pygame.key.get_pressed()[pygame.K_1 + i]:
                self.map_cursor = i
                pygame.time.delay(120)

        if keys[pygame.K_RETURN]:
            self.start_level(self.map_cursor)
            pygame.time.delay(120)

        # vibes confetti
        if self.vibes and random.random() < 0.25:
            self.spawn_confetti()

    def draw_map(self, dt):
        self.draw_paper_background(self.world_idx if self.level else self.map_cursor, time=pygame.time.get_ticks()/1000.0)
        surf = self.screen
        # Title
        title = f"World Select — choose 1..8 or arrows, Enter to start"
        self.draw_ui_text(title, 24, (W//2, 30), center=True, color=(20,20,20))
        # Draw 8 "world cards"
        margin_x = 72
        gap = (W - margin_x*2) // 7
        y = H//2
        for idx in range(8):
            x = margin_x + idx*gap
            name, _ = THEMES[idx][0], THEMES[idx][1]
            cleared = idx in self.cleared_worlds
            r = pygame.Rect(x-50, y-40, 100, 80)
            pygame.draw.rect(surf, (255,255,255), r, border_radius=12)
            pygame.draw.rect(surf, (0,0,0), r, 2, border_radius=12)
            self.draw_ui_text(f"{idx+1}", 22, (x, y-18), center=True, color=(0,0,0))
            self.draw_ui_text(THEMES[idx][0].split()[0], 16, (x, y+8), center=True, color=(0,0,0))
            if cleared:
                self.draw_ui_text("✓", 22, (x+34, y-36), center=True, color=(0,150,0))
        # Cursor
        cx = margin_x + self.map_cursor*gap
        pygame.draw.polygon(surf, (0,0,0), [(cx, y+60), (cx-10, y+80), (cx+10, y+80)])
        # HUD
        self.draw_ui_text(f"Vibes: {'ON' if self.vibes else 'OFF'}   FPS ~ {int(self.clock.get_fps())}", 18, (10, H-26), color=(20,20,20))

    def start_level(self, world_idx):
        self.world_idx = world_idx
        grid = self.worlds[world_idx]
        self.level = Level(grid, theme_idx=world_idx)
        self.player = Player(*self.level.player_start)
        self.state = "LEVEL"

    # ---------------------
    # Level State
    # ---------------------
    def update_level(self, dt):
        keys = pygame.key.get_pressed()
        # Pause
        if keys[pygame.K_ESCAPE]:
            self.state = "MAP"
            pygame.time.delay(160)
            return

        # Partner switching
        if keys[pygame.K_q]:
            self.partner_idx = (self.partner_idx - 1) % len(self.partners)
            pygame.time.delay(120)
        if keys[pygame.K_e]:
            self.partner_idx = (self.partner_idx + 1) % len(self.partners)
            pygame.time.delay(120)
        for i in range(min(9, len(self.partners))):
            if keys[pygame.K_1 + i]:
                self.partner_idx = i
                pygame.time.delay(120)

        # Use partner ability
        if keys[pygame.K_k]:
            self.partners[self.partner_idx].use(self, self.level, self.player)
            pygame.time.delay(120)

        # Player movement / physics
        self.player.run = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        ax = 0.0
        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        if left:  ax -= BASE_ACC * (RUN_ACC_MULT if self.player.run else 1.0)
        if right: ax += BASE_ACC * (RUN_ACC_MULT if self.player.run else 1.0)
        if left or right:
            self.player.facing = 1 if right else -1

        maxspeed = BASE_MAXSPEED + (RUN_BOOST if self.player.run else 0.0)
        if self.player.riding_yoshi:
            maxspeed += 1.2
        self.player.vx += ax
        self.player.vx = clamp(self.player.vx, -maxspeed, maxspeed)

        # friction
        if not (left or right):
            self.player.vx *= BASE_FRICTION

        # P-meter (for fun visual only)
        if self.player.run and abs(self.player.vx) > BASE_MAXSPEED*0.75:
            self.player.p_meter = clamp(self.player.p_meter + PMETER_GAIN, 0.0, 1.0)
        else:
            self.player.p_meter = clamp(self.player.p_meter - PMETER_DECAY, 0.0, 1.0)

        # Jump handling (buffer + coyote)
        jump_pressed = keys[pygame.K_SPACE]
        if jump_pressed:
            self.player.jump_buf = JUMP_BUFFER
        else:
            self.player.jump_buf = max(0.0, self.player.jump_buf - dt)

        # Gravity
        g = GRAVITY
        if jump_pressed and self.player.vy < 0:
            g *= (1.0 - JUMP_HOLD_GRAVITY_REDUCE)
        if self.player.riding_yoshi and self.player.flutter_timer > 0 and not self.player.on_ground and jump_pressed and self.player.vy > -1:
            # flutter hover
            g = FLUTTER_GRAVITY
            self.player.flutter_timer -= dt
        self.player.vy += g

        # Lakitu lift (brief float up)
        if self.player.lakitu_timer > 0:
            self.player.vy = min(self.player.vy, -3.0)
            self.player.lakitu_timer -= dt

        # Shadow timer decay
        if self.player.shadow_timer > 0:
            self.player.shadow_timer -= dt

        # Integrate + collide (X then Y)
        self.integrate_player(dt)

        # Jump trigger after collision resolution
        if self.player.jump_buf > 0 and (self.player.on_ground or self.player.coyote > 0):
            self.player.vy = JUMP_VEL - (self.player.p_meter * 2.2)  # little boost with p-meter
            self.player.on_ground = False
            self.player.coyote = 0.0
            self.player.jump_buf = 0.0
            # refresh flutter
            if self.player.riding_yoshi:
                self.player.flutter_timer = FLUTTER_TIME

        # Damage from hazards if not shadowing
        if self.player.inv > 0:
            self.player.inv -= dt
        if self.level.hazards_overlap(self.player.rect) and self.player.shadow_timer <= 0 and self.player.inv <= 0:
            self.player.hp -= 1
            self.player.inv = 1.0
            if self.player.hp <= 0:
                # respawn
                self.player = Player(*self.level.player_start)

        # Shells
        for s in list(self.level.shells):
            s.vy += GRAVITY
            s.x += s.vx
            s.y += s.vy
            r = s.rect
            # collide walls
            if self.level.rect_collides_solid(r, player_shadowing=False):
                s.active = False
            # hit switch
            tx = r.centerx // TILE
            ty = r.centery // TILE
            if self.level.tile_at(tx, ty) == 'S':
                self.level.gates_closed = not self.level.gates_closed
            # cleanup
            if not s.active or r.top > H+200 or r.right < -100 or r.left > LEVEL_W_TILES*TILE+100:
                self.level.shells.remove(s)

        # Bombs / explosions
        for b in list(self.level.bombs):
            b.vy += GRAVITY*0.9
            b.x += b.vx
            b.y += b.vy
            b.timer -= dt
            # bounce simple
            r = b.rect
            if self.level.rect_collides_solid(r, player_shadowing=False):
                b.vx *= 0.6
                b.vy *= -0.4
                b.y -= 4
            if b.timer <= 0 and not b.exploded:
                b.exploded = True
                self.level.explosions.append(Explosion(b.x, b.y))
                self.level.bombs.remove(b)

        for ex in list(self.level.explosions):
            ex.time -= dt
            if ex.time <= 0:
                self.level.explosions.remove(ex)
                continue
            # affect tiles
            min_tx = int((ex.cx - ex.radius)//TILE)
            max_tx = int((ex.cx + ex.radius)//TILE)
            min_ty = int((ex.cy - ex.radius)//TILE)
            max_ty = int((ex.cy + ex.radius)//TILE)
            for ty in range(min_ty, max_ty+1):
                for tx in range(min_tx, max_tx+1):
                    if 0 <= ty < LEVEL_H_TILES and 0 <= tx < LEVEL_W_TILES:
                        ch = self.level.tile_at(tx, ty)
                        # break cracked walls
                        if ch == 'B':
                            self.level.set_tile(tx, ty, ' ')
            # knock back goombas
            for g in self.level.goombas:
                dx = g.x - ex.cx
                dy = g.y - ex.cy
                d2 = dx*dx + dy*dy
                if d2 < (ex.radius*ex.radius):
                    g.vx += sign(dx) * 2.0
                    g.vy -= 4.0

        # Gusts
        for gs in list(self.level.gusts):
            gs.time -= dt
            if gs.time <= 0:
                self.level.gusts.remove(gs)
                continue
            # remove leafy covers
            min_tx = gs.rect.left // TILE
            max_tx = gs.rect.right // TILE
            min_ty = gs.rect.top // TILE
            max_ty = gs.rect.bottom // TILE
            for ty in range(min_ty, max_ty+1):
                for tx in range(min_tx, max_tx+1):
                    if self.level.tile_at(tx, ty) in REMOVABLE_BY_WIND:
                        self.level.set_tile(tx, ty, ' ')
            # push goombas
            for g in self.level.goombas:
                if gs.rect.colliderect(g.rect):
                    g.vx += 1.2 * self.player.facing

        # Goombas
        for g in list(self.level.goombas):
            g.vy += GRAVITY
            # move x
            g.x += g.vx
            if self.level.rect_collides_solid(g.rect, player_shadowing=False):
                g.x -= g.vx
                g.vx *= -1
            # move y
            g.y += g.vy
            if self.level.rect_collides_solid(g.rect, player_shadowing=False):
                g.y -= g.vy
                g.vy = 0
                g.on_ground = True
            else:
                g.on_ground = False
            # stomp?
            if g.alive and self.player.rect.colliderect(g.rect) and self.player.vy > 0 and self.player.y < g.y:
                g.alive = False
                self.level.goombas.remove(g)
                self.player.vy = -8
            # hit player?
            elif g.alive and self.player.rect.colliderect(g.rect) and self.player.inv <= 0 and self.player.shadow_timer <= 0:
                self.player.hp -= 1
                self.player.inv = 1.0
                if self.player.hp <= 0:
                    self.player = Player(*self.level.player_start)

        # Goal check
        pr = self.player.rect
        tx = pr.centerx // TILE
        ty = pr.centery // TILE
        if self.level.tile_at(tx, ty) == 'X':
            self.level.goal_reached = True
            self.cleared_worlds.add(self.world_idx)
            # Return to map with a tiny delay so you can see the banner
            if pygame.key.get_pressed()[pygame.K_RETURN]:
                self.state = "MAP"
                pygame.time.delay(150)

        # vibes confetti
        if self.vibes and random.random() < 0.3:
            self.spawn_confetti()

    def integrate_player(self, dt):
        p = self.player
        level = self.level
        # apply X
        p.x += p.vx
        if level.rect_collides_solid(p.rect, player_shadowing=(p.shadow_timer>0)):
            # backtrack
            step = sign(p.vx)
            while step != 0 and level.rect_collides_solid(p.rect, player_shadowing=(p.shadow_timer>0)):
                p.x -= step
            p.vx = 0.0

        # apply Y
        p.y += p.vy
        if level.rect_collides_solid(p.rect, player_shadowing=(p.shadow_timer>0)):
            step = sign(p.vy)
            while step != 0 and level.rect_collides_solid(p.rect, player_shadowing=(p.shadow_timer>0)):
                p.y -= step
            if p.vy > 0:
                p.on_ground = True
                p.coyote = COYOTE_TIME
            p.vy = 0.0
        else:
            # air
            if p.on_ground:
                p.coyote = COYOTE_TIME
            else:
                p.coyote = max(0.0, p.coyote - dt)
            p.on_ground = False

    def draw_level(self, dt):
        self.draw_paper_background(self.world_idx, time=pygame.time.get_ticks()/1000.0)
        surf = self.screen
        # camera follow
        cam_x = clamp(self.player.x + self.player.w//2 - W//2, 0, LEVEL_W_TILES*TILE - W)
        cam_y = 0

        # draw tiles
        for y,row in enumerate(self.level.grid):
            for x,ch in enumerate(row):
                rx = x*TILE - cam_x
                ry = y*TILE - cam_y
                r = pygame.Rect(rx, ry, TILE, TILE)
                if ch in ('=', '#', 'G', 'B', '|'):
                    col = (230,230,230) if ch == '#' else (210,200,190)
                    if ch == '=': col = (180, 150, 120)
                    if ch == 'G':
                        col = (120, 90, 70) if self.level.gates_closed else (200, 180, 160)
                    if ch == 'B':
                        col = (180, 120, 120)
                    if ch == '|':
                        col = (110, 80, 140)
                    pygame.draw.rect(surf, col, r)
                    pygame.draw.rect(surf, (0,0,0), r, 1)
                elif ch == '~':
                    pygame.draw.rect(surf, (255,100,90), r)
                elif ch == '^':
                    pygame.draw.polygon(surf, (180,180,180), [(rx,ry+TILE),(rx+TILE//2,ry+6),(rx+TILE,ry+TILE)])
                elif ch == 'S':
                    pygame.draw.rect(surf, (80,80,80), r)
                    pygame.draw.rect(surf, (255,255,0), r.inflate(-10,-10), 2)
                elif ch == 'L':
                    # leafy paper cover
                    pygame.draw.rect(surf, (100,180,120), r)
                    pygame.draw.rect(surf, (0,60,30), r, 2)
                elif ch == '?':
                    pygame.draw.rect(surf, (255, 230, 120), r)
                    pygame.draw.rect(surf, (0,0,0), r, 2)
                    self.draw_ui_text("?", 18, (rx+TILE//2, ry+TILE//2+2), center=True, color=(0,0,0))
                elif ch == 'X':
                    pygame.draw.rect(surf, (255,255,255), r)
                    pygame.draw.rect(surf, (0,0,0), r, 2)
                    self.draw_ui_text("GOAL", 14, (rx+TILE//2, ry+TILE//2+2), center=True, color=(0,0,0))

        # gusts
        for gs in self.level.gusts:
            gr = pygame.Rect(gs.rect.left - cam_x, gs.rect.top - cam_y, gs.rect.width, gs.rect.height)
            pygame.draw.rect(surf, (180,220,255), gr, 2)

        # bombs
        for b in self.level.bombs:
            br = rect_from_xywh(b.x - cam_x, b.y - cam_y, b.w, b.h)
            pygame.draw.circle(surf, (40,40,40), br.center, 8)
            # fuse indicator
            t = max(0.0, b.timer)
            w = int(16 * (t / BOMB_FUSE))
            pygame.draw.rect(surf, (255,120,60), pygame.Rect(br.left, br.top-6, w, 4))

        # explosions
        for ex in self.level.explosions:
            pygame.draw.circle(surf, (255,200,100), (int(ex.cx - cam_x), int(ex.cy - cam_y)), int(ex.radius), 2)

        # shells
        for s in self.level.shells:
            sr = rect_from_xywh(s.x - cam_x, s.y - cam_y, s.w, s.h)
            pygame.draw.rect(surf, (120, 220, 160), sr)
            pygame.draw.rect(surf, (0,0,0), sr, 2)

        # goombas
        for g in self.level.goombas:
            gr = rect_from_xywh(g.x - cam_x, g.y - cam_y, g.w, g.h)
            pygame.draw.rect(surf, (170,120,80), gr)
            pygame.draw.rect(surf, (0,0,0), gr, 2)

        # player (paper cutout)
        pr = rect_from_xywh(self.player.x - cam_x, self.player.y - cam_y, self.player.w, self.player.h)
        base = (255,255,255)
        if self.player.inv > 0 and int(pygame.time.get_ticks()*0.02) % 2 == 0:
            base = (240, 180, 180)
        pygame.draw.rect(surf, base, pr, border_radius=4)
        pygame.draw.rect(surf, (0,0,0), pr, 2, border_radius=4)
        # face line to show direction
        eye_x = pr.centerx + self.player.facing*6
        pygame.draw.circle(surf, (0,0,0), (eye_x, pr.centery-6), 2)

        # UI / HUD
        self.draw_level_hud()

        # goal banner
        if self.level.goal_reached:
            self.draw_banner_center("COURSE CLEAR!  (Enter to exit)")

        # confetti
        self.update_draw_confetti()

    def draw_level_hud(self):
        surf = self.screen
        # HP hearts
        for i in range(3):
            x = 16 + i*24
            y = 14
            col = (240,80,80) if i < self.player.hp else (150,120,120)
            pygame.draw.circle(surf, col, (x, y), 8)
            pygame.draw.circle(surf, col, (x+10, y), 8)
            pygame.draw.polygon(surf, col, [(x-8, y), (x+18, y), (x+5, y+14)])
            pygame.draw.rect(surf, (0,0,0), pygame.Rect(x-10, y-10, 26, 26), 1)
        # P-meter bar
        bx, by = 100, 10
        pygame.draw.rect(surf, (0,0,0), pygame.Rect(bx-2, by-2, 160+4, 12+4), 2)
        pygame.draw.rect(surf, (255,220,120), pygame.Rect(bx, by, int(160*self.player.p_meter), 12))
        self.draw_ui_text("P", 16, (bx-12, by+6), center=True, color=(0,0,0))
        # Partner label
        pname = self.partners[self.partner_idx].name
        self.draw_ui_text(f"[Q/E or 1..6] Partner: {pname}   [K] Use", 18, (W-10, 18), color=(20,20,20), right=True)
        self.draw_ui_text(f"Vibes: {'ON' if self.vibes else 'OFF'}   FPS {int(self.clock.get_fps())}", 16, (W-10, 42), color=(20,20,20), right=True)

    # ---------------------
    # Drawing helpers
    # ---------------------
    def draw_paper_background(self, theme_idx, time=0.0):
        name, cols = THEMES[theme_idx][0], THEMES[theme_idx][1]
        a, b, accent = cols
        t = (math.sin(time*0.5)+1)/2
        top = (int(lerp(a[0], b[0], t)), int(lerp(a[1], b[1], t)), int(lerp(a[2], b[2], t)))
        bottom = (int(lerp(b[0], a[0], t)), int(lerp(b[1], a[1], t)), int(lerp(b[2], a[2], t)))
        # vertical gradient
        for y in range(0, H, 8):
            yy = y / H
            c = (int(lerp(top[0], bottom[0], yy)),
                 int(lerp(top[1], bottom[1], yy)),
                 int(lerp(top[2], bottom[2], yy)))
            pygame.draw.rect(self.screen, c, pygame.Rect(0, y, W, 8))
        # simple parallax paper circles
        if self.vibes:
            for layer in range(3):
                r = 60 + layer*30
                cx = int((time*20 * (layer+1)) % (W+r)) - r
                cy = 120 + layer*120
                pygame.draw.circle(self.screen, accent, (cx, cy), r, 2)

    def draw_ui_text(self, text, size, pos, center=False, right=False, color=(0,0,0)):
        font = pygame.font.SysFont(None, size)
        s = font.render(text, True, color)
        r = s.get_rect()
        if center:
            r.center = pos
        elif right:
            r.midright = pos
        else:
            r.topleft = pos
        self.screen.blit(s, r)

    def draw_banner_center(self, text):
        box = pygame.Rect(W//2-220, H//2-40, 440, 80)
        pygame.draw.rect(self.screen, (255,255,255), box, border_radius=12)
        pygame.draw.rect(self.screen, (0,0,0), box, 2, border_radius=12)
        self.draw_ui_text(text, 24, box.center, center=True, color=(0,0,0))

    # ---------------------
    # Confetti Vibes
    # ---------------------
    def spawn_confetti(self):
        self.confetti.append([
            random.randint(0, W), -10,
            random.uniform(-20, 20), random.uniform(30, 80),
            random.choice([(255,120,120),(120,255,180),(120,160,255),(255,230,120),(220,120,255)])
        ])

    def update_draw_confetti(self):
        keep=[]
        for x,y,vx,vy,col in self.confetti:
            x += vx*0.016
            y += vy*0.016
            if y < H+12:
                keep.append([x,y,vx,vy,col])
            pygame.draw.rect(self.screen, col, pygame.Rect(int(x), int(y), 6, 8))
            pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(int(x), int(y), 6, 8),1)
        self.confetti = keep

    # ---------------------
    # Pause (simple)
    # ---------------------
    def draw_pause(self):
        self.draw_banner_center("PAUSED — Press ESC to return")


if __name__ == "__main__":
    Game().run()
