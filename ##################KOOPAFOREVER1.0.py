# koopa_broos_forever.py
# Resolution: 600x400, 60 FPS, zero external assets (graphics+sound generated)
# Inspired by SNES aesthetics + Mario Forever style flow. Everything is a Koopa.

import os, math, random, sys, time
import pygame

# --- Mixer setup (low latency) ---
try:
    pygame.mixer.pre_init(22050, -16, 1, 512)
except Exception:
    pass

pygame.init()
pygame.display.set_caption("Koopa Broos Forever — files=off vibes=on")

WIDTH, HEIGHT = 600, 400
FPS = 60
TILE = 20
GRAVITY = 0.55
JUMP_VELOCITY = -10.5
MAX_FALL = 12
MOVE_SPEED = 2.3
DASH_SPEED = 5.8
DASH_TIME = 14   # frames
CAMERA_LERP = 0.12

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 18)
BIG  = pygame.font.SysFont(None, 28)

# ---------------------------------------------
# Minimal math helpers
# ---------------------------------------------
def clamp(v, a, b): return a if v < a else b if v > b else v
def lerp(a, b, t): return a + (b - a) * t
def sgn(x): return -1 if x < 0 else 1 if x > 0 else 0

# ---------------------------------------------
# Palette / Worlds
# ---------------------------------------------
World = dict  # name, palette, sky, mode7, music scale/mood
WORLDS = [
    dict(
        name="Plains of Shells",
        sky=(24, 160, 248),
        palette=[(24,160,248),(88,200,112),(56,176,88),(40,72,40)],
        mode7=True,
        music=dict(scale="major_pent", bpm=112)
    ),
    dict(
        name="Coral Koopa Reef",
        sky=(8, 80, 160),
        palette=[(8,80,160),(24,120,200),(0,160,168),(0,56,96)],
        mode7=False,
        music=dict(scale="mixolydian", bpm=104)
    ),
    dict(
        name="Icy Shell Peaks",
        sky=(200, 232, 248),
        palette=[(200,232,248),(168,220,248),(112,160,200),(56,96,160)],
        mode7=True,
        music=dict(scale="lydian", bpm=118)
    ),
    dict(
        name="Magma Fortress",
        sky=(248, 88, 40),
        palette=[(248,88,40),(200,56,32),(120,24,16),(24,8,8)],
        mode7=False,
        music=dict(scale="phrygian", bpm=128)
    ),
    dict(
        name="Starry Skyway",
        sky=(16, 16, 40),
        palette=[(16,16,40),(32,48,96),(96,96,160),(208,208,248)],
        mode7=True,
        music=dict(scale="minor_pent", bpm=122)
    )
]

# ---------------------------------------------
# Zero-asset gfx: simple tiles & shapes
# ---------------------------------------------
def make_tile(color_fg, color_bg):
    s = pygame.Surface((TILE, TILE)).convert()
    s.fill(color_bg)
    # koopa-scale checker and little shell dot
    for y in range(0, TILE, 4):
        for x in range(0, TILE, 4):
            if (x//4 + y//4) % 2 == 0:
                s.fill(color_fg, (x, y, 4, 4))
    pygame.draw.circle(s, color_fg, (TILE//2, TILE//2), 3, 1)
    return s

def make_circle(color, r):
    s = pygame.Surface((r*2, r*2), pygame.SRCALPHA).convert_alpha()
    pygame.draw.circle(s, color, (r, r), r)
    return s

def draw_text_center(surface, text, font, color, y):
    img = font.render(text, True, color)
    surface.blit(img, (WIDTH//2 - img.get_width()//2, y))

# ---------------------------------------------
# Procedural OST (no files): tiny synth
# ---------------------------------------------
try:
    import numpy as np
except Exception:
    np = None

SAMPLE_RATE = 22050

SCALES = {
    "major_pent":    [0,2,4,7,9],
    "minor_pent":    [0,3,5,7,10],
    "mixolydian":    [0,2,4,5,7,9,10],
    "lydian":        [0,2,4,6,7,9,11],
    "phrygian":      [0,1,3,5,7,8,10],
}

def _np_or_list(n):
    return np.zeros(n, dtype=np.float32) if np else [0.0]*n

def _mix_into(buf, tone, vol=0.5):
    if np:
        buf[:len(tone)] += vol * tone
    else:
        for i in range(min(len(buf), len(tone))):
            buf[i] += vol * tone[i]

def _to_sound(buf):
    # clamp and convert to int16
    if np:
        b = np.clip(buf, -1.0, 1.0)
        i16 = (b * 32767).astype(np.int16).tobytes()
    else:
        clipped = [max(-1.0, min(1.0, v)) for v in buf]
        # pack little-endian 16-bit
        import struct
        i16 = b''.join(struct.pack('<h', int(v*32767)) for v in clipped)
    try:
        return pygame.mixer.Sound(buffer=i16)
    except Exception:
        return None

def _osc_square(freq, length_samples):
    if freq <= 0: freq = 1
    if np:
        t = (np.arange(length_samples) / SAMPLE_RATE)
        wave = np.sign(np.sin(2*math.pi*freq*t)).astype(np.float32)
        return wave * 0.8
    else:
        out = []
        period = SAMPLE_RATE / float(freq)
        acc = 0.0
        val = 1.0
        for i in range(length_samples):
            acc += 1
            if acc >= period/2:
                acc -= period/2
                val = -val
            out.append(val*0.8)
        return out

def _osc_triangle(freq, length_samples):
    if freq <= 0: freq = 1
    if np:
        t = (np.arange(length_samples)/SAMPLE_RATE)
        # Saw then fold to triangle
        saw = (2*((freq*t) % 1.0)-1.0).astype(np.float32)
        tri = 2.0 * np.abs(saw) - 1.0
        return tri * 0.6
    else:
        out=[]
        period = SAMPLE_RATE/float(freq)
        for i in range(length_samples):
            phase = (i % period)/period
            v = 2*abs(2*phase-1)-1
            out.append(v*0.6)
        return out

def _noise(length_samples):
    if np:
        return (np.random.rand(length_samples).astype(np.float32)*2-1)*0.3
    else:
        rnd = random.random
        return [(rnd()*2-1)*0.3 for _ in range(length_samples)]

def note_freq(base_hz, semis):
    return base_hz * (2.0 ** (semis/12.0))

class OST:
    def __init__(self):
        self.current = None
        self.channel = pygame.mixer.Channel(0) if pygame.mixer.get_init() else None
        self.seed = 0

    def build_loop(self, world_idx, boss=False):
        w = WORLDS[world_idx]
        scale_name = w["music"]["scale"]
        bpm = w["music"]["bpm"]
        if boss:
            bpm = int(bpm*1.15)
        steps = 16
        spb = 60.0 / bpm
        step_len = int(SAMPLE_RATE * (spb/2.0))  # 8th notes
        total_len = steps * step_len
        buf = _np_or_list(total_len)

        rnd = random.Random((world_idx+1)*997 + (2 if boss else 0))
        scale = SCALES.get(scale_name, SCALES["major_pent"])
        root = 196.0 if boss else 220.0  # boss slightly darker

        # Lead melody (square)
        lead_pattern = [rnd.choice(scale) + rnd.choice([0,12,24]) for _ in range(steps)]
        for i, semi in enumerate(lead_pattern):
            length = step_len
            f = note_freq(root, semi)
            tone = _osc_square(f, length)
            _mix_into(buf[i*step_len:(i+1)*step_len], tone, vol=0.35 if boss else 0.30)

        # Bass (triangle) on downbeats
        for i in range(0, steps, 2):
            semi = scale[0] + ( -12 if i%4==0 else -7 )
            length = step_len
            f = note_freq(root, semi)
            tone = _osc_triangle(f, length)
            _mix_into(buf[i*step_len:(i+1)*step_len], tone, vol=0.42)

        # Noise hats/snare
        for i in range(steps):
            n = _noise(int(step_len*0.25 if i%2==0 else step_len*0.10))
            _mix_into(buf[i*step_len:(i*step_len)+len(n)], n, vol=0.35 if boss else 0.25)

        return _to_sound(buf)

    def play_level(self, world_idx):
        if not pygame.mixer.get_init() or not pygame.mixer.get_init():
            return
        s = self.build_loop(world_idx, boss=False)
        self.current = s
        if self.channel and s:
            self.channel.play(s, loops=-1)

    def play_boss(self, world_idx):
        if not pygame.mixer.get_init():
            return
        s = self.build_loop(world_idx, boss=True)
        self.current = s
        if self.channel and s:
            self.channel.play(s, loops=-1)

OST_ENGINE = OST()

# ---------------------------------------------
# Vibes
# ---------------------------------------------
class Vibes:
    def __init__(self):
        self.on = True
        self.t = 0.0
        self.shake = 0.0
        self.particles = []

    def toggle(self):
        self.on = not self.on

    def kick(self, amt=4.0):
        self.shake = max(self.shake, amt)

    def update(self, dt):
        self.t += dt
        self.shake *= 0.9
        # particle decay
        for p in self.particles[:]:
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)
            else:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["vy"] += 0.1

    def add_burst(self, x, y, color):
        for _ in range(12):
            a = random.random()*math.tau
            sp = 1.5 + random.random()*2.0
            self.particles.append(dict(x=x, y=y, vx=math.cos(a)*sp, vy=math.sin(a)*sp, life=0.8+random.random()*0.6, color=color))

    def offset(self):
        if not self.on: return (0,0)
        dx = int((random.random()*2-1)*self.shake)
        dy = int((random.random()*2-1)*self.shake)
        return dx, dy

VIBES = Vibes()

# ---------------------------------------------
# Mode7-ish floor (scaled strips)
# ---------------------------------------------
class Mode7Floor:
    def __init__(self, palette):
        self.tex = pygame.Surface((64,64)).convert()
        # build a turtle-shell tile
        for y in range(64):
            for x in range(64):
                c = palette[2] if ((x//8 + y//8) % 2 == 0) else palette[3]
                self.tex.set_at((x,y), c)
        pygame.draw.circle(self.tex, palette[1], (32,32), 12, 2)
        self.scroll = 0.0

    def draw(self, surface, horizon, speed, palette):
        H = surface.get_height()
        self.scroll += speed
        strips = 64  # fewer strips for speed
        for i in range(strips):
            y0 = int(lerp(horizon, H, i/strips))
            y1 = int(lerp(horizon, H, (i+1)/strips))
            h = max(1, y1-y0)
            # perspective scale — closer to bottom = larger scale
            scale = 1.0 + (i/strips)*8.0
            src_w = int(64/scale)
            src_h = int(64/scale)
            # FIXED: Cap src_w and src_h to be less than 64 to avoid modulo by zero
            src_w = clamp(src_w, 2, 63)
            src_h = clamp(src_h, 2, 63)
            
            # source rect scroll
            u = int((self.scroll*0.5 + i*2) % (64-src_w))
            v = int((self.scroll*0.3 + i*1.5) % (64-src_h))
            src = pygame.Rect(u, v, src_w, src_h)
            strip = pygame.transform.scale(self.tex.subsurface(src), (WIDTH, h))
            surface.blit(strip, (0, y0))

# ---------------------------------------------
# Tiles & Level gen
# ---------------------------------------------
class Level:
    def __init__(self, world_idx, seed):
        self.world_idx = world_idx
        self.rnd = random.Random(seed)
        self.width_tiles = 180
        self.height_tiles = HEIGHT // TILE
        self.tiles = [[0 for _ in range(self.width_tiles)] for _ in range(self.height_tiles)]
        self.palette = WORLDS[world_idx]["palette"]
        self.solid_tile = make_tile(self.palette[2], self.palette[1])
        self.goal_x = (self.width_tiles-6)*TILE
        self._carve()
        self.koopas = []
        self._spawn_koopas()

    def _ground_profile(self, x):
        # smooth noisy ground
        base = self.height_tiles - 4
        h = int(2*math.sin(x*0.05) + 1.5*math.sin(x*0.11 + 5) + self.rnd.randint(-1,1))
        return clamp(base + h, 8, self.height_tiles-2)

    def _carve(self):
        for x in range(self.width_tiles):
            gy = self._ground_profile(x)
            for y in range(gy, self.height_tiles):
                self.tiles[y][x] = 1
            # occasional floating platforms
            if x % 23 == 0:
                py = gy - self.rnd.randint(3,5)
                if 3 < py < self.height_tiles-3:
                    for dx in range(4):
                        self.tiles[py][min(self.width_tiles-1, x+dx)] = 1

    def _spawn_koopas(self):
        for x in range(8, self.width_tiles-12, 18):
            gy = self._ground_profile(x)
            self.koopas.append(EnemyKoopa(x*TILE, (gy-1)*TILE))

    def rect_collide(self, rect):
        hits = []
        tx0 = clamp(rect.left//TILE, 0, self.width_tiles-1)
        tx1 = clamp(rect.right//TILE, 0, self.width_tiles-1)
        ty0 = clamp(rect.top//TILE, 0, self.height_tiles-1)
        ty1 = clamp(rect.bottom//TILE, 0, self.height_tiles-1)
        for ty in range(ty0, ty1+1):
            for tx in range(tx0, tx1+1):
                if self.tiles[ty][tx] == 1:
                    hits.append(pygame.Rect(tx*TILE, ty*TILE, TILE, TILE))
        return hits

    def draw(self, surf, camx):
        # background fill
        surf.fill(WORLDS[self.world_idx]["sky"])
        # parallax hills
        for layer, mul in enumerate([0.2, 0.5]):
            y = 200 + layer*30
            color = self.palette[0 if layer==0 else 1]
            for i in range(-1, 6):
                cx = int(-camx*mul + i*180) % (WIDTH+200) - 100
                pygame.draw.ellipse(surf, color, (cx, y, 240, 80))
        # tiles
        start = max(0, camx//TILE - 2)
        end   = min(self.width_tiles, (camx+WIDTH)//TILE + 3)
        for y in range(self.height_tiles):
            for x in range(start, end):
                if self.tiles[y][x] == 1:
                    surf.blit(self.solid_tile, (x*TILE - camx, y*TILE))

        # goal post (Koopa totem)
        gx = self.goal_x - camx
        pygame.draw.rect(surf, self.palette[3], (gx, 80, 8, HEIGHT-120))
        pygame.draw.circle(surf, self.palette[2], (gx+4, 78), 14, 3)
        pygame.draw.circle(surf, self.palette[1], (gx+4, 78), 6)

# ---------------------------------------------
# Entities
# ---------------------------------------------
class Entity:
    def __init__(self, x, y, w, h):
        self.x, self.y = x, y
        self.vx, self.vy = 0.0, 0.0
        self.w, self.h = w, h
        self.on_ground = False

    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

class Player(Entity):
    def __init__(self, x, y, palette):
        super().__init__(x, y, 16, 18)
        self.dir = 1
        self.dash_timer = 0
        self.coyote = 0
        self.palette = palette
        self.coins = 0
        self.hp = 3
        self.invul = 0
        self.shell = False

    def update(self, keys, level: Level):
        ax = 0.0
        if keys[pygame.K_LEFT]:  ax -= 1.0
        if keys[pygame.K_RIGHT]: ax += 1.0
        if ax != 0: self.dir = int(sgn(ax))
        speed = DASH_SPEED if self.dash_timer>0 else MOVE_SPEED
        self.vx = lerp(self.vx, ax*speed, 0.4)

        # Jump
        if self.on_ground: self.coyote = 6
        if self.coyote>0 and keys[pygame.K_z]:
            self.vy = JUMP_VELOCITY
            self.coyote = 0
            VIBES.kick(3)

        # Dash (shell spin)
        if self.dash_timer==0 and keys[pygame.K_x]:
            self.dash_timer = DASH_TIME
            self.shell = True
            VIBES.kick(4)
        if self.dash_timer>0:
            self.dash_timer -= 1
            if self.dash_timer==0:
                self.shell = False

        # Gravity
        self.vy = clamp(self.vy + GRAVITY, -999, MAX_FALL)

        # X movement with collision
        self._move(level, self.vx, 0)
        # Y movement with collision
        self.on_ground = False
        self._move(level, 0, self.vy)
        if self.on_ground: self.vy = max(0, self.vy)

        if self.invul>0: self.invul -= 1

    def _move(self, level, dx, dy):
        self.x += dx
        r = self.rect
        hits = level.rect_collide(r)
        for tile in hits:
            if dx>0 and r.right>tile.left and r.left < tile.left:
                self.x = tile.left - self.w
                self.vx = 0
            if dx<0 and r.left<tile.right and r.right > tile.right:
                self.x = tile.right
                self.vx = 0
        self.y += dy
        r = self.rect
        hits = level.rect_collide(r)
        for tile in hits:
            if dy>0 and r.bottom>tile.top and r.top < tile.top:
                self.y = tile.top - self.h
                self.on_ground = True
            if dy<0 and r.top<tile.bottom and r.bottom > tile.bottom:
                self.y = tile.bottom
                self.vy = 0

    def stomped(self):
        self.vy = -7.5
        VIBES.kick(2.5)

    def hurt(self):
        if self.invul>0: return
        self.hp -= 1
        self.invul = 60
        VIBES.kick(5)

    def draw(self, surf, camx):
        # Koopa body (simple shell dude)
        r = self.rect
        x, y = r.x - camx, r.y
        # flicker if invul
        if self.invul and (self.invul//4)%2==0:
            return
        shell_col = (48,160,64)
        border = (8,40,16)
        leg = (96,72,40)
        # body
        pygame.draw.ellipse(surf, shell_col, (x-2, y, self.w+4, self.h))
        pygame.draw.ellipse(surf, border, (x-2, y, self.w+4, self.h), 2)
        # head
        pygame.draw.circle(surf, shell_col, (x+self.w//2, y-6), 6)
        # legs
        pygame.draw.rect(surf, leg, (x+2, y+self.h-4, 4, 4))
        pygame.draw.rect(surf, leg, (x+self.w-6, y+self.h-4, 4, 4))
        # dash aura
        if self.shell:
            pygame.draw.circle(surf, self.palette[1], (x+self.w//2, y+self.h//2), 14, 2)

class EnemyKoopa(Entity):
    def __init__(self, x, y):
        super().__init__(x, y-16, 16, 16)
        self.speed = 1.1 * random.choice([-1, 1])
        self.alive = True

    def update(self, level: Level):
        if not self.alive: return
        self.vx = self.speed
        self.vy = clamp(self.vy + GRAVITY, -999, MAX_FALL)
        self._move(level, self.vx, self.vy)

    def _move(self, level, dx, dy):
        self.x += dx
        r = self.rect
        hits = level.rect_collide(r)
        for tile in hits:
            if dx>0: self.x = tile.left - self.w; self.speed *= -1
            if dx<0: self.x = tile.right; self.speed *= -1
        self.y += dy
        r = self.rect
        hits = level.rect_collide(r)
        for tile in hits:
            if dy>0 and r.bottom>tile.top:
                self.y = tile.top - self.h
                self.vy = 0
            if dy<0 and r.top<tile.bottom:
                self.y = tile.bottom; self.vy = 0

    def draw(self, surf, camx):
        if not self.alive: return
        x, y = self.rect.x - camx, self.rect.y
        pygame.draw.rect(surf, (40,120,56), (x, y, self.w, self.h))
        pygame.draw.rect(surf, (12,48,20), (x, y, self.w, self.h), 2)

class BoomBoom(Entity):
    def __init__(self, x, y, palette):
        super().__init__(x, y, 22, 22)
        self.hp = 3
        self.state = "pace"
        self.timer = 90
        self.palette = palette
        self.dir = -1

    def update(self, level: Level, player: Player):
        self.timer -= 1
        if self.state == "pace":
            self.vx = 1.6 * self.dir
            if self.timer <= 0:
                self.state = "jump"
                self.timer = 45
                self.vy = -9.5
        elif self.state == "jump":
            self.vx = 1.2 * sgn(player.x - self.x)
            if self.on_ground:
                self.state = "dash"
                self.timer = 50
                self.dir = sgn(player.x - self.x) or self.dir
        elif self.state == "dash":
            self.vx = 3.3 * self.dir
            if self.timer <= 0:
                self.state = "pace"
                self.timer = 90

        self.vy = clamp(self.vy + GRAVITY, -999, MAX_FALL)
        self._move(level, self.vx, self.vy)

    def _move(self, level, dx, dy):
        self.x += dx
        r = self.rect
        hits = level.rect_collide(r)
        for tile in hits:
            if dx>0: self.x = tile.left - self.w; self.dir *= -1
            if dx<0: self.x = tile.right; self.dir *= -1
        self.y += dy
        r = self.rect
        hits = level.rect_collide(r)
        self.on_ground = False
        for tile in hits:
            if dy>0 and r.bottom>tile.top:
                self.y = tile.top - self.h
                self.vy = 0
                self.on_ground = True
            if dy<0 and r.top<tile.bottom:
                self.y = tile.bottom; self.vy = 0

    def stomp(self, player: Player):
        self.hp -= 1
        player.stomped()
        VIBES.add_burst(self.rect.centerx, self.rect.top, self.palette[1])
        VIBES.kick(6)

    def draw(self, surf, camx):
        x, y = self.rect.x - camx, self.rect.y
        body = self.palette[2]
        border = self.palette[3]
        wing  = (248,248,248)
        # body
        pygame.draw.ellipse(surf, body, (x-2, y-2, self.w+4, self.h+4))
        pygame.draw.ellipse(surf, border, (x-2, y-2, self.w+4, self.h+4), 2)
        # wings (boom boom-ish)
        pygame.draw.polygon(surf, wing, [(x-6,y+4),(x-12,y-2),(x-4,y-6)])
        pygame.draw.polygon(surf, wing, [(x+self.w+6,y+4),(x+self.w+12,y-2),(x+self.w+4,y-6)])
        # hp pips
        for i in range(self.hp):
            pygame.draw.rect(surf, (248,232,88), (x + i*8, y-10, 6, 4))

# ---------------------------------------------
# Boss Arena
# ---------------------------------------------
class BossArena(Level):
    def __init__(self, world_idx):
        super().__init__(world_idx, seed=world_idx*777 + 42)
        self.width_tiles = 90
        self.height_tiles = HEIGHT//TILE
        self.tiles = [[0 for _ in range(self.width_tiles)] for _ in range(self.height_tiles)]
        # flat floor, walls, ceiling
        floor_y = self.height_tiles-3
        for x in range(self.width_tiles):
            for y in range(floor_y, self.height_tiles):
                self.tiles[y][x] = 1
        for y in range(self.height_tiles):
            self.tiles[y][2] = 1
            self.tiles[y][self.width_tiles-3] = 1
        for x in range(2, self.width_tiles-2):
            self.tiles[3][x] = 1

# ---------------------------------------------
# Game
# ---------------------------------------------
STATE_TITLE, STATE_LEVEL, STATE_BOSS, STATE_WORLD_CLEAR, STATE_CREDITS = range(5)

class Game:
    def __init__(self):
        self.state = STATE_TITLE
        self.world_idx = 0
        self.level = None
        self.player = None
        self.boss = None
        self.camx = 0.0
        self.horizon = 160
        self.mode7 = None
        self.victory_timer = 0
        self.title_bob = 0.0

    def start_world(self, idx):
        self.world_idx = idx
        self.level = Level(idx, seed=idx*1337 + 5)
        pal = WORLDS[idx]["palette"]
        self.player = Player(4*TILE, 8*TILE, pal)
        self.camx = 0.0
        self.mode7 = Mode7Floor(pal) if WORLDS[idx]["mode7"] else None
        OST_ENGINE.play_level(idx)

    def start_boss(self):
        idx = self.world_idx
        self.level = BossArena(idx)
        pal = WORLDS[idx]["palette"]
        self.player.x, self.player.y = 6*TILE, (self.level.height_tiles-6)*TILE
        self.boss = BoomBoom(62*TILE, (self.level.height_tiles-6)*TILE, pal)
        self.camx = 0.0
        OST_ENGINE.play_boss(idx)

    def update(self):
        dt = 1.0/FPS
        VIBES.update(dt)
        keys = pygame.key.get_pressed()

        if self.state == STATE_TITLE:
            self.title_bob += dt
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                self.start_world(0)
                self.state = STATE_LEVEL
            return

        if keys[pygame.K_v]:
            # light debounce (cheap)
            pygame.event.clear(pygame.KEYDOWN)
            VIBES.toggle()

        if self.state == STATE_LEVEL:
            self.player.update(keys, self.level)
            # enemy updates + interactions
            for e in self.level.koopas:
                e.update(self.level)
                if e.alive and self.player.rect.colliderect(e.rect):
                    if self.player.vy > 1.0 and self.player.rect.bottom-2 <= e.rect.top+6:
                        e.alive = False
                        self.player.stomped()
                        VIBES.add_burst(e.rect.centerx, e.rect.centery, self.level.palette[1])
                    else:
                        if self.player.shell:
                            e.alive = False
                            VIBES.add_burst(e.rect.centerx, e.rect.centery, self.level.palette[2])
                        else:
                            self.player.hurt()
                            if self.player.hp <= 0:
                                self.state = STATE_TITLE
                                return

            # goal reach?
            if self.player.x > self.level.goal_x:
                self.start_boss()
                self.state = STATE_BOSS

            # camera
            target = self.player.x - WIDTH*0.4
            self.camx = lerp(self.camx, clamp(target, 0, self.level.width_tiles*TILE - WIDTH), CAMERA_LERP)

        elif self.state == STATE_BOSS:
            self.player.update(keys, self.level)
            self.boss.update(self.level, self.player)

            # interactions
            if self.player.rect.colliderect(self.boss.rect):
                if self.player.vy > 1.0 and self.player.rect.bottom-2 <= self.boss.rect.top+8:
                    self.boss.stomp(self.player)
                else:
                    if self.player.shell:
                        self.boss.hp -= 1
                        VIBES.add_burst(self.boss.rect.centerx, self.boss.rect.centery, self.level.palette[2])
                        VIBES.kick(5)
                    else:
                        self.player.hurt()
                        if self.player.hp <= 0:
                            self.state = STATE_TITLE
                            return

            if self.boss.hp <= 0:
                self.state = STATE_WORLD_CLEAR
                self.victory_timer = FPS*2
                VIBES.kick(8)

            target = self.player.x - WIDTH*0.4
            self.camx = lerp(self.camx, clamp(target, 0, self.level.width_tiles*TILE - WIDTH), CAMERA_LERP)

        elif self.state == STATE_WORLD_CLEAR:
            self.victory_timer -= 1
            if self.victory_timer <= 0:
                if self.world_idx < len(WORLDS)-1:
                    self.start_world(self.world_idx+1)
                    self.state = STATE_LEVEL
                else:
                    self.state = STATE_CREDITS

        elif self.state == STATE_CREDITS:
            if pygame.key.get_pressed()[pygame.K_RETURN]:
                self.state = STATE_TITLE

    def draw(self):
        # base world sky or title
        if self.state == STATE_TITLE:
            w = WORLDS[self.world_idx]
            SCREEN.fill(w["sky"])
            draw_text_center(SCREEN, "KOOPA BROOS FOREVER", BIG, (248, 232, 120), 100)
            draw_text_center(SCREEN, "files=off • vibes=on • 600x400 • 60fps", FONT, (255,255,255), 140)
            draw_text_center(SCREEN, "Press ENTER to start", FONT, (255,255,255), 220)
            # subtle title bounce + mode7 flourish
            if WORLDS[self.world_idx]["mode7"]:
                if not hasattr(self, "_tmode7"):
                    self._tmode7 = Mode7Floor(WORLDS[self.world_idx]["palette"])
                self._tmode7.draw(SCREEN, 220, 0.8, WORLDS[self.world_idx]["palette"])
            self._draw_vibes_overlay()
            return

        # World backdrops
        self.level.draw(SCREEN, int(self.camx))

        # Mode7 floor for some worlds (under the ground)
        if self.mode7:
            self.mode7.draw(SCREEN, self.horizon, 1.2, self.level.palette)

        # Entities
        for e in self.level.koopas:
            e.draw(SCREEN, int(self.camx))
        self.player.draw(SCREEN, int(self.camx))
        if self.state == STATE_BOSS:
            self.boss.draw(SCREEN, int(self.camx))

        # HUD
        w = WORLDS[self.world_idx]
        pygame.draw.rect(SCREEN, (0,0,0), (0,0, WIDTH, 20))
        hud = f"WORLD {self.world_idx+1}/5  HP:{self.player.hp}  VIBES:{'ON' if VIBES.on else 'OFF'}"
        SCREEN.blit(FONT.render(hud, True, (248,248,248)), (6, 2))

        if self.state == STATE_WORLD_CLEAR:
            draw_text_center(SCREEN, "WORLD CLEAR!", BIG, (255,255,255), 140)
            draw_text_center(SCREEN, "Preparing next Koopa zone…", FONT, (255,255,255), 170)

        if self.state == STATE_CREDITS:
            SCREEN.fill((16,16,32))
            draw_text_center(SCREEN, "KOOPA BROOS FOREVER — THANKS FOR PLAYING!", BIG, (248,232,160), 130)
            draw_text_center(SCREEN, "Press ENTER to Replay", FONT, (240,240,240), 170)

        self._draw_vibes_overlay()

    def _draw_vibes_overlay(self):
        if not VIBES.on and len(VIBES.particles)==0:
            return
        # camera shake offset
        dx, dy = VIBES.offset()
        if dx or dy:
            SCREEN.blit(SCREEN.copy(), (dx, dy))
        # particles
        for p in VIBES.particles:
            pygame.draw.circle(SCREEN, p["color"], (int(p["x"]), int(p["y"])), 2)
        # color cycle scanline
        if VIBES.on:
            t = (time.time()*0.8) % 1.0
            for y in range(0, HEIGHT, 6):
                alpha = int(40 + 40*math.sin(t*math.tau + y*0.08))
                pygame.draw.rect(SCREEN, (255,255,255, alpha), (0, y, WIDTH, 3), 0)

# ---------------------------------------------
# Main loop
# ---------------------------------------------
def main():
    game = Game()
    running = True
    # title music for first world (lazy start)
    OST_ENGINE.play_level(0)

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running=False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: running=False

        game.update()
        game.draw()

        pygame.display.flip()
        CLOCK.tick(FPS)

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print("Error:", ex)
        pygame.quit()
        sys.exit(1)
