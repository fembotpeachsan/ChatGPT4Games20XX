# Mario Arcade (NES vibes) — single-file, no assets, 60 FPS
# Controls: Left/Right = move, Z/Space = jump, P = pause, R = reset
# Requires: pygame (no external images/sounds/fonts)

import sys, math, random, array
import pygame

# --- init (mixer first for low-latency bleeps) ---
pygame.mixer.pre_init(22050, -16, 1, 256)
pygame.init()

# --- NES-ish setup ---
TILE = 8
W, H = 32 * TILE, 30 * TILE           # 256x240 (NES resolution)
SCALE = 3                              # integer scale for crisp pixels
FPS = 60

# Small NES-flavored palette (approximate)
COL = {
    "BLACK": (0, 0, 0),
    "SKY": (99, 155, 255),
    "WHITE": (236, 236, 236),
    "BRICK": (180, 64, 48),
    "BRICK_DK": (124, 44, 33),
    "PLAT": (52, 104, 86),
    "PLAT_LT": (96, 164, 126),
    "PIPE": (20, 168, 72),
    "PIPE_LT": (116, 224, 144),
    "RED": (188, 32, 40),
    "BROWN": (120, 72, 0),
    "SKIN": (255, 216, 168),
    "BLUE": (52, 104, 204),
    "YELL": (252, 216, 96),
}

SCREEN = pygame.display.set_mode((W * SCALE, H * SCALE))
pygame.display.set_caption("Mario Arcade — NES vibes (no files)")

BASE = pygame.Surface((W, H))          # we draw at NES res, then scale up
clock = pygame.time.Clock()
FONT = pygame.font.Font(None, 16)

# --- tiny square-wave bleep synth (no files) ---
def make_tone(freq=880, ms=90, vol=0.25):
    try:
        sr = 22050
        n = int(sr * ms / 1000)
        data = array.array("h")
        amp = int(32767 * max(0.0, min(1.0, vol)) * 0.35)
        for i in range(n):
            # square wave via sine sign
            v = math.sin(2 * math.pi * freq * (i / sr))
            data.append(amp if v >= 0 else -amp)
        return pygame.mixer.Sound(buffer=data.tobytes())
    except Exception:
        return None

SND_JUMP = make_tone(660, 90, 0.35)
SND_BONK = make_tone(110, 60, 0.45)
SND_FLIP = make_tone(440, 100, 0.30)
SND_TAG  = make_tone(988, 120, 0.40)

def play(snd):
    if snd:
        snd.play()

# --- tile art (drawn in code) ---
def tile_platform():
    t = pygame.Surface((TILE, TILE)).convert()
    t.fill(COL["PLAT"])
    # light top strip for NES-y bevel
    pygame.draw.rect(t, COL["PLAT_LT"], (0, 0, TILE, 2))
    # little rivet pixels
    t.set_at((2, 5), COL["BLACK"])
    t.set_at((5, 5), COL["BLACK"])
    return t

def tile_pipe():
    t = pygame.Surface((TILE, TILE)).convert()
    t.fill(COL["PIPE"])
    pygame.draw.rect(t, COL["PIPE_LT"], (0, 0, TILE, 2))
    pygame.draw.rect(t, COL["PIPE_LT"], (0, 3, TILE, 1))
    return t

def tile_brick():
    t = pygame.Surface((TILE, TILE)).convert()
    t.fill(COL["BRICK"])
    pygame.draw.rect(t, COL["BRICK_DK"], (0, TILE-2, TILE, 2))
    pygame.draw.line(t, COL["BLACK"], (0, 3), (TILE-1, 3))
    pygame.draw.line(t, COL["BLACK"], (TILE//2, 0), (TILE//2, TILE-1))
    return t

def tile_pow(ch):
    t = pygame.Surface((TILE, TILE), pygame.SRCALPHA).convert_alpha()
    # simple 2x2 block spells POW when assembled
    base = pygame.Surface((TILE, TILE)).convert()
    base.fill(COL["BLUE"])
    pygame.draw.rect(base, COL["WHITE"], (0, 0, TILE, 1))
    pygame.draw.rect(base, COL["WHITE"], (0, TILE-1, TILE, 1))
    t.blit(base, (0, 0))
    # tiny letter pixels
    pix = COL["WHITE"]
    if ch == 'P':
        for px,py in [(2,3),(3,3),(4,3),(2,4),(2,5),(3,5),(4,5),(2,6)]:
            t.set_at((px, py), pix)
    elif ch == 'O':
        for px,py in [(2,3),(3,3),(4,3),(2,4),(4,4),(2,5),(4,5),(2,6),(3,6),(4,6)]:
            t.set_at((px, py), pix)
    elif ch == 'W':
        for px,py in [(2,3),(4,3),(2,4),(3,5),(4,4),(2,6),(4,6)]:
            t.set_at((px, py), pix)
    return t

TILES = {
    '#': tile_platform(),
    'b': tile_brick(),
    'p': tile_pipe(),
    'P': tile_pow('P'), 'O': tile_pow('O'), 'W': tile_pow('W'),
}

SOLID = {'#', 'b', 'p', 'P', 'O', 'W'}

# --- level layout: single-screen arena with pipes + POW ---
# 32x30 characters (each 8x8). spaces = empty air.
def build_level():
    g = [[' ' for _ in range(32)] for _ in range(30)]
    # Floor
    for x in range(32):
        g[28][x] = '#'
    # Mid platforms
    for x in range(2, 13): g[21][x] = '#'
    for x in range(19, 30): g[21][x] = '#'
    for x in range(6, 26): g[14][x] = '#'
    for x in [3, 4, 27, 28]: g[7][x] = '#'
    # Top pipes (spawn points)
    for y in range(2, 6):
        g[y][1] = 'p'; g[y][2] = 'p'
        g[y][29] = 'p'; g[y][30] = 'p'
    # POW block (2x2)
    g[27][15] = 'P'; g[27][16] = 'O'
    g[26][15] = 'W'; g[26][16] = 'P'
    return g

LEVEL = build_level()

def draw_level(surf, camera=(0,0)):
    ox, oy = camera
    for ty, row in enumerate(LEVEL):
        for tx, ch in enumerate(row):
            if ch != ' ':
                t = TILES[ch]
                surf.blit(t, (tx*TILE - ox, ty*TILE - oy))

def rect_for_tile(tx, ty):
    return pygame.Rect(tx*TILE, ty*TILE, TILE, TILE)

def is_solid(tx, ty):
    if 0 <= ty < len(LEVEL) and 0 <= tx < len(LEVEL[0]):
        return LEVEL[ty][tx] in SOLID
    return False

# --- simple 8-bit sprites (code-drawn) ---
def make_mario_frames():
    def base():
        s = pygame.Surface((16,16), pygame.SRCALPHA).convert_alpha()
        return s
    def draw_mario(s, step=0):
        # hat
        pygame.draw.rect(s, COL["RED"], (3,1,10,3))
        pygame.draw.rect(s, COL["RED"], (2,4,7,2))
        # face
        pygame.draw.rect(s, COL["SKIN"], (6,5,6,5))
        # moustache
        pygame.draw.rect(s, COL["BROWN"], (6,9,6,1))
        # body (shirt)
        pygame.draw.rect(s, COL["RED"], (4,10,8,3))
        # overalls
        pygame.draw.rect(s, COL["BLUE"], (6,10,4,5))
        # legs (animate step)
        if step == 0:
            pygame.draw.rect(s, COL["BROWN"], (4,14,4,2))
            pygame.draw.rect(s, COL["BROWN"], (10,14,4,2))
        else:
            pygame.draw.rect(s, COL["BROWN"], (3,14,5,2))
            pygame.draw.rect(s, COL["BROWN"], (9,14,5,2))
        # nose pixel
        s.set_at((12,7), COL["SKIN"])
        return s
    f0 = base(); draw_mario(f0, 0)
    f1 = base(); draw_mario(f1, 1)
    f0L = pygame.transform.flip(f0, True, False)
    f1L = pygame.transform.flip(f1, True, False)
    jumpR = base(); pygame.draw.rect(jumpR, COL["RED"], (3,1,10,3)); pygame.draw.rect(jumpR, COL["SKIN"], (6,5,6,5)); pygame.draw.rect(jumpR, COL["RED"], (4,10,8,3)); pygame.draw.rect(jumpR, COL["BLUE"], (6,10,4,5)); pygame.draw.rect(jumpR, COL["BROWN"], (4,14,8,2))
    jumpL = pygame.transform.flip(jumpR, True, False)
    return {
        "R0": f0, "R1": f1, "L0": f0L, "L1": f1L,
        "JR": jumpR, "JL": jumpL
    }

def make_goomba_frames():
    def g(step=0):
        s = pygame.Surface((16,16), pygame.SRCALPHA).convert_alpha()
        body = COL["BROWN"]
        eye = COL["WHITE"]
        pygame.draw.ellipse(s, body, (2,4,12,10))
        pygame.draw.rect(s, body, (2,9,12,5))
        # feet wiggle
        if step == 0:
            pygame.draw.rect(s, COL["BLACK"], (3,13,4,2))
            pygame.draw.rect(s, COL["BLACK"], (9,13,4,2))
        else:
            pygame.draw.rect(s, COL["BLACK"], (2,13,5,2))
            pygame.draw.rect(s, COL["BLACK"], (9,13,5,2))
        # eyes
        pygame.draw.rect(s, eye, (5,7,2,2))
        pygame.draw.rect(s, eye, (9,7,2,2))
        return s
    f0 = g(0); f1 = g(1)
    flipped = pygame.transform.flip(f0, False, True)  # on back
    return {"0": f0, "1": f1, "F": flipped}

MARIO_FR = make_mario_frames()
GOOM_FR  = make_goomba_frames()

# --- helpers ---
def wrap_x(x):
    if x < -16: return W
    if x > W: return -16
    return x

def aabb_vs_level(rect, vx, vy):
    # Move axis by axis with tile collision
    hit_under_tiles = []   # tiles we bonked while moving upward
    # Horizontal
    rect.x += vx
    # collide walls
    tiles = tiles_overlapping(rect)
    for tx,ty in tiles:
        if is_solid(tx, ty):
            tile_r = rect_for_tile(tx, ty)
            if vx > 0 and rect.right > tile_r.left and rect.left < tile_r.left:
                rect.right = tile_r.left
            elif vx < 0 and rect.left < tile_r.right and rect.right > tile_r.right:
                rect.left = tile_r.right
    # Vertical
    rect.y += vy
    tiles = tiles_overlapping(rect)
    on_ground = False
    head_bonk = False
    for tx,ty in tiles:
        if is_solid(tx, ty):
            tile_r = rect_for_tile(tx, ty)
            if vy > 0 and rect.bottom > tile_r.top and rect.top < tile_r.top:
                rect.bottom = tile_r.top
                on_ground = True
            elif vy < 0 and rect.top < tile_r.bottom and rect.bottom > tile_r.bottom:
                rect.top = tile_r.bottom
                head_bonk = True
                hit_under_tiles.append(tile_r)
    return rect, on_ground, head_bonk, hit_under_tiles

def tiles_overlapping(rect):
    tx0 = rect.left // TILE
    ty0 = rect.top // TILE
    tx1 = (rect.right - 1) // TILE
    ty1 = (rect.bottom - 1) // TILE
    out = []
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            out.append((tx, ty))
    return out

# --- Entities ---
class Player:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.rect = pygame.Rect(int(x), int(y), 14, 16)
        self.on_ground = False
        self.face = 1  # 1 right, -1 left
        self.invuln = 0  # frames after hit
        self.score = 0
        self.coins = 0

    def update(self, keys, enemies):
        ACC = 0.25
        MAX = 2.0
        FRI = 0.85
        GRAV = 0.35
        JUMP = 6.0

        # horizontal input
        ax = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            ax -= ACC
            self.face = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            ax += ACC
            self.face = 1

        self.vel.x += ax
        if abs(self.vel.x) > MAX:
            self.vel.x = math.copysign(MAX, self.vel.x)
        if ax == 0 and self.on_ground:
            self.vel.x *= FRI

        # jump
        want_jump = keys[pygame.K_z] or keys[pygame.K_SPACE]
        if want_jump and self.on_ground:
            self.vel.y = -JUMP
            self.on_ground = False
            play(SND_JUMP)

        # gravity
        self.vel.y += GRAV
        if self.vel.y > 7: self.vel.y = 7

        # move vs tiles
        new_rect = self.rect.copy()
        new_rect, on_ground, head_bonk, tiles_hit = aabb_vs_level(new_rect, self.vel.x, self.vel.y)
        # handle bonk -> flip enemies on platform above
        if head_bonk and tiles_hit:
            play(SND_BONK)
            for tile_r in tiles_hit:
                shock_rect = tile_r.copy()
                shock_rect.y -= 2  # just above tile
                shock_rect.height = 4
                shock_rect.inflate_ip(16, 0)  # small horizontal forgiveness
                for e in enemies:
                    if not e.dead and not e.flipped and e.rect.colliderect(shock_rect):
                        e.flip()
                        play(SND_FLIP)

        # apply move
        self.rect = new_rect
        self.on_ground = on_ground
        self.pos.update(self.rect.x, self.rect.y)
        self.rect.x = int(self.rect.x); self.rect.y = int(self.rect.y)

        # screen wrap
        self.pos.x = wrap_x(self.pos.x)
        self.rect.x = int(self.pos.x)

        # collide with enemies
        self.invuln = max(0, self.invuln - 1)
        for e in enemies:
            if e.dead: continue
            if self.rect.colliderect(e.rect):
                # stomp from above if falling
                if self.vel.y > 0 and self.rect.bottom - e.rect.top <= 6:
                    e.kill()
                    self.vel.y = -4.0
                    self.score += 200
                    self.coins += 1
                    play(SND_TAG)
                else:
                    # if enemy flipped -> tag (kick) it
                    if e.flipped:
                        e.kill()
                        self.score += 800
                        self.coins += 1
                        play(SND_TAG)
                    elif self.invuln == 0:
                        # simple knockback
                        self.invuln = FPS // 2
                        self.vel.x = -self.face * 2.5
                        self.vel.y = -3.5

    def draw(self, surf, t):
        if not self.on_ground and self.vel.y < 0:
            frame = "JR" if self.face > 0 else "JL"
        else:
            step = (t // 8) % 2
            if self.face > 0:
                frame = f"R{step}"
            else:
                frame = f"L{step}"
        spr = MARIO_FR[frame]
        surf.blit(spr, (self.rect.x - 1, self.rect.y))  # tiny offset looks nicer

class Goomba:
    def __init__(self, x, y, dir=-1):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(dir * 0.8, 0)
        self.rect = pygame.Rect(int(x), int(y), 16, 16)
        self.flipped = False
        self.flip_timer = 0
        self.dead = False

    def flip(self):
        if not self.flipped and not self.dead:
            self.flipped = True
            self.flip_timer = FPS * 4  # 4 seconds
            self.vel.x = 0
            self.vel.y = -1.0

    def kill(self):
        self.dead = True

    def update(self):
        if self.dead:
            return
        GRAV = 0.35
        if self.flipped:
            self.flip_timer -= 1
            if self.flip_timer <= 0:
                self.flipped = False
                self.vel.x = random.choice([-1, 1]) * 0.8

        self.vel.y += GRAV
        if self.vel.y > 7: self.vel.y = 7

        # if moving normally, walk; if flipped, minimal drift
        vx = self.vel.x if not self.flipped else 0
        vy = self.vel.y

        new_rect = self.rect.copy()
        before_x = new_rect.x
        new_rect, on_ground, head_bonk, _ = aabb_vs_level(new_rect, vx, vy)

        # turn around on horizontal collision
        if new_rect.x != before_x and not self.flipped:
            self.vel.x = -self.vel.x

        # apply
        self.rect = new_rect
        self.pos.update(self.rect.x, self.rect.y)

        # wrap
        self.pos.x = wrap_x(self.pos.x)
        self.rect.x = int(self.pos.x)

    def draw(self, surf, t):
        if self.dead: return
        if self.flipped:
            spr = GOOM_FR["F"]
        else:
            spr = GOOM_FR["0"] if (t // 10) % 2 == 0 else GOOM_FR["1"]
        surf.blit(spr, (self.rect.x, self.rect.y))

# --- POW block logic (flips everyone; 3 uses) ---
class PowBlock:
    def __init__(self):
        # find POW block tiles (2x2) center-ish
        self.tiles = []
        for ty,row in enumerate(LEVEL):
            for tx,ch in enumerate(row):
                if ch in {'P','O','W'}:
                    self.tiles.append((tx,ty))
        self.uses = 3
        self.cooldown = 0

    def rect(self):
        # compute combined rect
        txs = [tx for tx,ty in self.tiles]
        tys = [ty for tx,ty in self.tiles]
        left = min(txs)*TILE; right = (max(txs)+1)*TILE
        top = min(tys)*TILE; bottom = (max(tys)+1)*TILE
        return pygame.Rect(left, top, right-left, bottom-top)

    def try_use(self, player, enemies):
        if self.uses <= 0 or self.cooldown > 0:
            return
        if player.rect.colliderect(self.rect()):
            self.uses -= 1
            self.cooldown = FPS // 2
            for e in enemies:
                if not e.dead:
                    e.flip()
            play(SND_FLIP)

    def update(self):
        self.cooldown = max(0, self.cooldown - 1)

    def draw_overlay(self, surf):
        # draw uses as small white pips
        r = self.rect()
        for i in range(self.uses):
            pygame.draw.rect(surf, COL["WHITE"], (r.x + 3 + i*4, r.y - 5, 3, 3))

# --- spawner (pipes) ---
class Spawner:
    def __init__(self):
        self.timer = 0
        self.interval = FPS * 3
        self.spawn_points = [(2*TILE, 2*TILE), (29*TILE, 2*TILE)]
        self.max_enemies = 6

    def update(self, enemies):
        alive = [e for e in enemies if not e.dead]
        if len(alive) >= self.max_enemies:
            self.timer = 0
            return
        self.timer += 1
        if self.timer >= self.interval:
            self.timer = 0
            sx, sy = random.choice(self.spawn_points)
            enemies.append(Goomba(sx, sy, dir=random.choice([-1,1])))

# --- game state ---
def reset_game():
    player = Player(16*TILE, 24*TILE)
    enemies = []
    powb = PowBlock()
    spawn = Spawner()
    time_left = 200  # seconds-ish counter (decrements in frames)
    return player, enemies, powb, spawn, time_left*FPS, 0  # score2 not used (placeholder)

def draw_hud(surf, player, time_frames):
    tsec = max(0, time_frames // FPS)
    text = f"SCORE {player.score:06d}   COINS {player.coins:02d}   TIME {tsec:03d}"
    img = FONT.render(text, True, COL["WHITE"])
    surf.blit(img, (6, 6))

def main():
    rng = random.Random(0xC0FE)
    player, enemies, powb, spawner, time_frames, wave = reset_game()
    paused = False
    t = 0

    while True:
        dt_ms = clock.tick(FPS)  # hard cap to 60
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p: paused = not paused
                if e.key == pygame.K_r:
                    player, enemies, powb, spawner, time_frames, wave = reset_game()
                if e.key in (pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_DOWN):
                    powb.try_use(player, enemies)

        keys = pygame.key.get_pressed()
        if not paused:
            # update
            spawner.update(enemies)
            player.update(keys, enemies)
            for goom in enemies:
                goom.update()
            powb.update()
            time_frames = max(0, time_frames - 1)

        # draw
        BASE.fill(COL["SKY"])
        draw_level(BASE)
        powb.draw_overlay(BASE)
        for goom in enemies:
            goom.draw(BASE, t)
        player.draw(BASE, t)
        draw_hud(BASE, player, time_frames)

        # pause overlay
        if paused:
            txt = FONT.render("PAUSED", True, COL["WHITE"])
            BASE.blit(txt, (W//2 - txt.get_width()//2, H//2 - 8))

        # scale up (nearest-neighbor)
        pygame.transform.scale(BASE, SCREEN.get_size(), SCREEN)
        pygame.display.flip()
        t += 1

if __name__ == "__main__":
    main()
