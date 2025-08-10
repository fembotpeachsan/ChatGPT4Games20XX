#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mario Bros (Arcade-ish) — GBA speed, SNES vibes
Single-file, no external assets. Pygame 2.x
Controls:
  Arrow keys or A/D = move
  Z / Space = jump
  Down + Z near the POW block = trigger POW (if charges remain)
  V = toggle Vibes Mode (post-process + particles + trails)
  S = toggle scanlines
  P = pause, R = reset, Esc = quit

Notes:
- This is an homage/fan mini-game for educational purposes. No assets are used; visuals and audio are generated.
- Resolution is SNES-like (256x224) upscaled to a window.
- Gameplay is simplified but keeps the core flip-then-kick loop.
"""

import sys, math, random, time
from dataclasses import dataclass, field
from array import array

try:
    import pygame
except Exception as e:
    print("This game requires pygame 2.x. Install with: pip install pygame")
    raise

# ------------- Config -------------
BASE_W, BASE_H = 256, 224  # SNES native like
SCALE = 3                   # window scale (3x -> 768x672)
FPS = 60

# Palette (SNES-ish, handpicked)
PALETTE = {
    "bg_dark":   (16, 24, 40),
    "bg_mid":    (28, 44, 72),
    "bg_light":  (52, 84, 120),
    "platform":  (48, 120, 152),
    "platform_hi": (92, 180, 212),
    "pow_body":  (64, 72, 160),
    "pow_text":  (248, 248, 248),
    "pipe":      (20, 140, 84),
    "pipe_d":    (14, 98, 64),
    "mario":     (228, 56, 56),
    "mario_dark":(184, 24, 24),
    "luigi":     (52, 184, 72),
    "coin":      (248, 200, 56),
    "coin_d":    (212, 168, 40),
    "enemy":     (40, 160, 184),
    "enemy_d":   (24, 104, 120),
    "crab":      (232, 92, 80),
    "crab_d":    (172, 44, 40),
    "fly":       (208, 208, 72),
    "white":     (240, 240, 240),
    "black":     (12, 12, 12),
    "ui":        (236, 236, 236),
    "shadow":    (0, 0, 0),
}

# ------------- Tiny synth (no numpy) -------------
class TinySynth:
    def __init__(self, freq=22050):
        self.freq = freq
        try:
            pygame.mixer.pre_init(self.freq, size=-16, channels=1, buffer=512)
        except Exception:
            pass
        pygame.mixer.init(self.freq, size=-16, channels=1, buffer=512)
        self.cache = {}

    def square(self, hz, ms, vol=0.35):
        key = ("sq", hz, ms, vol)
        if key in self.cache:
            return self.cache[key]
        n = int(self.freq * ms / 1000)
        a = array('h')
        amp = int(32767 * vol)
        p = int(self.freq / max(1, hz))
        half = p // 2
        s = 0
        for i in range(n):
            # quick square without sin()
            s += 1
            if s % p < half:
                a.append(amp)
            else:
                a.append(-amp)
        snd = pygame.mixer.Sound(buffer=a.tobytes())
        self.cache[key] = snd
        return snd

    def noise(self, ms, vol=0.25):
        key = ("ns", ms, vol)
        if key in self.cache:
            return self.cache[key]
        n = int(self.freq * ms / 1000)
        a = array('h')
        amp = int(32767 * vol)
        seed = 0xACE1
        for _ in range(n):
            # simple LFSR noise
            bit = ((seed >> 0) ^ (seed >> 2) ^ (seed >> 3) ^ (seed >> 5)) & 1
            seed = (seed >> 1) | (bit << 15)
            val = amp if (seed & 1) else -amp
            a.append(val)
        snd = pygame.mixer.Sound(buffer=a.tobytes())
        self.cache[key] = snd
        return snd

    def beep(self): self.square(880, 70).play()
    def jump(self): self.square(620, 80, 0.4).play()
    def coin(self): self.square(1400, 70, 0.42).play()
    def pow(self): self.noise(130, 0.35).play()
    def flip(self): self.square(300, 90, 0.4).play()
    def kick(self): self.square(190, 60, 0.42).play()
    def hurt(self): self.square(120, 250, 0.5).play()
    def phase(self): self.square(520, 220, 0.4).play()

# ------------- Geometry helpers -------------
def wrap_x(x):
    if x < -8: return BASE_W + 8
    if x > BASE_W + 8: return -8
    return x

def clamp(v, lo, hi): return lo if v < lo else hi if v > hi else v

# ------------- Level layout -------------
@dataclass
class Platform:
    rect: pygame.Rect
    bump_t: float = 0.0  # bump animation timer

@dataclass
class PowBlock:
    rect: pygame.Rect
    charges: int = 3

@dataclass
class Pipe:
    rect: pygame.Rect

# ------------- Particles -------------
@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    t: float
    color: tuple

# ------------- Enemies -------------
ENEMY_WALK, ENEMY_FLIPPED, ENEMY_SLIDING = 0, 1, 2

class Enemy:
    def __init__(self, x, y, kind="shell"):
        self.x = x
        self.y = y
        self.vx = random.choice([-0.8, 0.8])
        self.vy = 0
        self.w = 12; self.h = 12
        self.kind = kind  # "shell", "crab", "fly"
        self.state = ENEMY_WALK
        self.flip_timer = 0.0
        self.angry = 0  # for crab
        self.on_ground = False
        self.spawn_drop = True  # falling from pipe

    def rect(self):
        return pygame.Rect(int(self.x - self.w/2), int(self.y - self.h/2), self.w, self.h)

    def update(self, dt, level, vibes):
        g = 0.14
        sp = 0.6 if self.kind != "fly" else 0.5
        if self.kind == "crab" and self.angry > 0 and self.state == ENEMY_WALK:
            sp *= 1.55

        if self.state == ENEMY_SLIDING:
            sp = 2.0

        # Gravity (flies hop)
        if self.kind == "fly":
            # periodic hop
            if random.random() < 0.01 and self.on_ground:
                self.vy = -2.3
        self.vy += g
        self.on_ground = False

        # Move X
        self.x += (self.vx * sp)
        self.x = wrap_x(self.x)

        # Move Y and resolve with platforms
        for pf in level.platforms:
            r = pf.rect
            # Land on top
            if (self.y <= r.top <= self.y + self.vy + 4) and (r.left-10 <= self.x <= r.right+10) and self.vy >= 0:
                # On top
                self.y = r.top
                self.vy = 0
                self.on_ground = True
        # Bottom floor
        if self.y + self.vy >= level.floor_y:
            self.y = level.floor_y
            self.vy = 0
            self.on_ground = True
        else:
            self.y += self.vy

        # Unflip timer
        if self.state == ENEMY_FLIPPED:
            self.flip_timer -= dt
            if self.flip_timer <= 0:
                self.state = ENEMY_WALK

        # Bounce from pipe lips
        for p in level.pipes:
            if self.rect().colliderect(p.rect.inflate(0, -6)):
                self.vx *= -1

    def draw(self, surf):
        r = self.rect()
        if self.kind == "shell":
            c, d = PALETTE["enemy"], PALETTE["enemy_d"]
        elif self.kind == "crab":
            c, d = PALETTE["crab"], PALETTE["crab_d"]
        else:
            c, d = PALETTE["fly"], PALETTE["black"]

        if self.state == ENEMY_FLIPPED:
            # draw flipped (on back)
            pygame.draw.rect(surf, d, r.inflate(2,2))
            pygame.draw.rect(surf, c, r)
            # little legs
            pygame.draw.line(surf, d, (r.left, r.bottom), (r.left+4, r.bottom), 1)
            pygame.draw.line(surf, d, (r.right-4, r.bottom), (r.right, r.bottom), 1)
        else:
            pygame.draw.rect(surf, c, r)
            pygame.draw.rect(surf, d, r.inflate(-4,-4))

# ------------- Player -------------
class Player:
    def __init__(self, x, y, color="mario"):
        self.x = x; self.y = y
        self.vx = 0.0; self.vy = 0.0
        self.w = 10; self.h = 14
        self.on_ground = False
        self.coyote = 0.0
        self.color = color
        self.lives = 3
        self.invuln = 0.0
        self.score = 0
        self.coins = 0

    def rect(self):
        return pygame.Rect(int(self.x - self.w/2), int(self.y - self.h), self.w, self.h)

    def update(self, keys, dt, level, synth, sfx_on=True):
        accel = 0.12
        max_vx = 1.4
        fric = 0.10
        jump_v = -2.9

        ax = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: ax -= accel
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: ax += accel

        self.vx += ax
        if ax == 0 and self.on_ground:
            # friction
            if abs(self.vx) < fric: self.vx = 0
            else: self.vx -= fric * (1 if self.vx>0 else -1)
        self.vx = clamp(self.vx, -max_vx, max_vx)

        # gravity
        g = 0.15
        self.vy += g

        # position tentative
        self.x += self.vx
        self.x = wrap_x(self.x)

        # Y movement + collisions with platforms (top only)
        self.on_ground = False
        ny = self.y + self.vy

        # Check bump (hit underside of platforms/POW)
        head = pygame.Rect(int(self.x-4), int(self.y - self.h - 2), 8, 2)
        if self.vy < 0:
            # hit underside?
            for pf in level.platforms:
                if head.colliderect(pf.rect):
                    # reposition below platform
                    self.vy = 0.6  # slight push down
                    self.y = pf.rect.bottom + self.h + 0.1
                    pf.bump_t = 0.25
                    level.bump_platform(pf, synth)
                    break
            # POW hit
            if level.pow and head.colliderect(level.pow.rect):
                # trigger POW
                if level.pow.charges > 0:
                    level.trigger_pow(synth)

        # Land on platforms
        for pf in level.platforms:
            r = pf.rect
            if (self.y <= r.top <= ny) and (r.left-8 <= self.x <= r.right+8) and self.vy >= 0:
                self.y = r.top
                self.vy = 0
                self.on_ground = True
                self.coyote = 0.08
        # Floor
        if ny >= level.floor_y:
            self.y = level.floor_y
            self.vy = 0
            self.on_ground = True
            self.coyote = 0.08
        else:
            if not self.on_ground:
                self.y = ny
                self.coyote -= dt

        # Jump
        if (keys[pygame.K_z] or keys[pygame.K_SPACE] or keys[pygame.K_k]) and (self.on_ground or self.coyote>0):
            # basic jump buffering not included; single press check below
            pass

    def jump(self, synth):
        # separate function to call once on keydown
        self.vy = -2.9
        self.on_ground = False
        if synth: synth.jump()

    def draw(self, surf, t):
        r = self.rect()
        col = PALETTE["mario"] if self.color=="mario" else PALETTE["luigi"]
        d = PALETTE["mario_dark"] if self.color=="mario" else (32, 120, 48)
        if self.invuln>0 and int(t*20)%2==0:
            # blink
            col = PALETTE["white"]; d = PALETTE["black"]
        # simple body
        pygame.draw.rect(surf, d, r.inflate(2,2))
        pygame.draw.rect(surf, col, r)
        # hat
        pygame.draw.rect(surf, d, (r.left, r.top-3, r.w, 3))
        # face
        pygame.draw.rect(surf, PALETTE["white"], (r.centerx-2, r.top, 4, 3))

# ------------- Level / Game -------------
class Level:
    def __init__(self):
        # Floor Y
        self.floor_y = BASE_H - 16
        self.platforms = []
        self.pipes = []
        self.pow = None
        self.phase = 1
        self.spawn_timer = 0
        self.enemies = []
        self.particles = []
        self.shake = 0.0
        self.vibes = True
        self.scanlines = True

        self._build_layout()
        self._spawn_wave(self.phase)

    def _build_layout(self):
        # Platforms: (x,y,w,h) with symmetrical gaps reminiscent of arcade
        plats = [
            (8, 164, 84, 8),
            (164,164, 84, 8),
            (40, 120, 72, 8),
            (144,120, 72, 8),
            (8,  76, 84, 8),
            (164, 76, 84, 8),
        ]
        for x,y,w,h in plats:
            self.platforms.append(Platform(pygame.Rect(x,y,w,h)))
        # Floor ledge (drawn only)
        # Pipes (top left/right)
        self.pipes = [
            Pipe(pygame.Rect(0, 36, 28, 40)),
            Pipe(pygame.Rect(BASE_W-28, 36, 28, 40)),
        ]
        # POW block in center
        self.pow = PowBlock(pygame.Rect(BASE_W//2-12, self.floor_y-8, 24, 8), charges=3)

    def _spawn_wave(self, phase):
        # spawn based on phase: more / tougher enemies
        types = []
        if phase == 1:
            types = ["shell", "shell"]
        elif phase == 2:
            types = ["shell", "crab"]
        elif phase == 3:
            types = ["shell", "crab", "fly"]
        else:
            # mix
            choices = ["shell"]*3 + ["crab"]*2 + ["fly"]
            n = 2 + min(5, phase//2)
            types = [random.choice(choices) for _ in range(n)]
        for k in types:
            side = random.choice([0,1])
            x = 12 if side==0 else BASE_W-12
            y = 36  # top of pipe
            e = Enemy(x, y, k)
            e.vy = 0.2
            e.vx = 0.6 if side==0 else -0.6
            self.enemies.append(e)
        self.spawn_timer = 0.0

    def bump_platform(self, pf, synth):
        # flip enemies sitting on this platform
        flipped = 0
        top = pf.rect.top
        for e in self.enemies:
            er = e.rect()
            if abs(er.bottom - top) <= 3 and (pf.rect.left-8 <= e.x <= pf.rect.right+8):
                if e.kind == "crab" and e.angry == 0 and e.state == ENEMY_WALK:
                    e.angry = 1  # first hit enrages
                elif e.state != ENEMY_SLIDING:
                    e.state = ENEMY_FLIPPED
                    e.flip_timer = 3.0
                    e.vy = -1.3
                    flipped += 1
        if flipped and synth: synth.flip()

    def trigger_pow(self, synth):
        if not self.pow or self.pow.charges <= 0: return
        self.pow.charges -= 1
        # global flip
        for e in self.enemies:
            if e.kind == "crab" and e.angry == 0 and e.state == ENEMY_WALK:
                e.angry = 1
            elif e.state != ENEMY_SLIDING:
                e.state = ENEMY_FLIPPED
                e.flip_timer = 3.0
                e.vy = -1.5
        self.shake = 0.35
        if synth: synth.pow()

    def add_particles(self, x, y, color, n=8):
        for _ in range(n):
            a = random.random() * math.tau
            sp = random.uniform(0.6, 1.6)
            self.particles.append(Particle(x, y, math.cos(a)*sp, math.sin(a)*sp, 0.45, color))

    def update_particles(self, dt):
        out = []
        for p in self.particles:
            p.t -= dt
            if p.t > 0:
                p.x += p.vx
                p.y += p.vy
                p.vy += 0.05
                out.append(p)
        self.particles = out

    def all_defeated(self):
        return all(e.state == ENEMY_SLIDING and abs(e.vx)<0.001 for e in self.enemies) or len(self.enemies)==0

# ------------- Drawing helpers -------------
def draw_bg(surface, t, vibes):
    # gradient background + subtle pulse
    if vibes:
        k = (math.sin(t*0.8)*0.5+0.5)*0.2
    else:
        k = 0.0
    top = tuple(clamp(int(PALETTE["bg_dark"][i] + k*40), 0,255) for i in range(3))
    mid = tuple(clamp(int(PALETTE["bg_mid"][i] + k*50), 0,255) for i in range(3))
    low = tuple(clamp(int(PALETTE["bg_light"][i] + k*30), 0,255) for i in range(3))

    for y in range(BASE_H):
        # simple vertical gradient
        if y < BASE_H//3:
            c = top
        elif y < 2*BASE_H//3:
            c = mid
        else:
            c = low
        surface.fill(c, rect=pygame.Rect(0,y,BASE_W,1))

def draw_platforms(surface, level, t):
    for pf in level.platforms:
        r = pf.rect.copy()
        # bump wobble
        if pf.bump_t > 0:
            off = int(math.sin((0.25-pf.bump_t)*40) * 2)
            r.y += off
            pf.bump_t -= 1.0/FPS
        pygame.draw.rect(surface, PALETTE["platform"], r)
        pygame.draw.rect(surface, PALETTE["platform_hi"], r.inflate(-2,-2))

    # floor
    fr = pygame.Rect(0, level.floor_y, BASE_W, 8)
    pygame.draw.rect(surface, PALETTE["platform"], fr)
    pygame.draw.rect(surface, PALETTE["platform_hi"], fr.inflate(0,-2))

def draw_pipes(surface, level):
    for p in level.pipes:
        r = p.rect
        pygame.draw.rect(surface, PALETTE["pipe_d"], r.inflate(4,4))
        pygame.draw.rect(surface, PALETTE["pipe"], r)
        # rim
        pygame.draw.rect(surface, PALETTE["pipe_d"], (r.x-2, r.y-6, r.w+4, 6))

def draw_pow(surface, level):
    if not level.pow: return
    r = level.pow.rect
    pygame.draw.rect(surface, PALETTE["pow_body"], r.inflate(2,2))
    pygame.draw.rect(surface, PALETTE["white"], r)
    # letters (tiny)
    # stylized 'POW' using rectangles
    cx = r.centerx
    pygame.draw.rect(surface, PALETTE["pow_body"], (r.x+3, r.y+2, 4, 4)) # P stem
    pygame.draw.rect(surface, PALETTE["pow_body"], (r.x+3, r.y+2, 6, 2)) # P top
    pygame.draw.rect(surface, PALETTE["pow_body"], (r.x+3, r.y+4, 6, 2)) # P mid
    pygame.draw.rect(surface, PALETTE["pow_body"], (cx-2,   r.y+2, 4, 4)) # O
    pygame.draw.rect(surface, PALETTE["pow_body"], (r.right-9, r.y+2, 2, 4)) # W
    pygame.draw.rect(surface, PALETTE["pow_body"], (r.right-7, r.y+2, 2, 2))
    pygame.draw.rect(surface, PALETTE["pow_body"], (r.right-5, r.y+2, 2, 4))

    # charges display
    for i in range(level.pow.charges):
        pygame.draw.rect(surface, PALETTE["pow_text"], (r.x + 3 + i*6, r.y-4, 4, 2))

def draw_particles(surface, level):
    for p in level.particles:
        c = p.color
        surface.fill(c, (int(p.x), int(p.y), 2, 2))

def draw_ui(surface, game, font):
    l = game.player.lives
    s = game.player.score
    c = game.player.coins
    txt = f"LIVES {l}   SCORE {s:06d}   COINS {c}   PHASE {game.level.phase}"
    img = font.render(txt, False, PALETTE["ui"])
    # shadow
    sh = font.render(txt, False, PALETTE["shadow"])
    surface.blit(sh, (8, 8+1))
    surface.blit(img, (8, 8))

def crt_scanlines(screen):
    # draw horizontal lines across the window size
    w,h = screen.get_size()
    sl = pygame.Surface((w,h), pygame.SRCALPHA)
    for y in range(0,h,2):
        pygame.draw.line(sl, (0,0,0,36), (0,y), (w,y))
    screen.blit(sl, (0,0))

# ------------- Game orchestrator -------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Mario Bros — GBA speed, SNES vibes (single-file)")
        self.window = pygame.display.set_mode((BASE_W*SCALE, BASE_H*SCALE))
        self.frame = pygame.Surface((BASE_W, BASE_H)).convert()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier", 8)

        self.synth = TinySynth(freq=22050)

        self.level = Level()
        self.player = Player(BASE_W//2, self.level.floor_y, color="mario")
        self.keys = pygame.key.get_pressed()
        self.prev_jump = False

        # trails surface for vibes
        self.trail = pygame.Surface((BASE_W, BASE_H), pygame.SRCALPHA)

    def reset(self):
        self.level = Level()
        self.player = Player(BASE_W//2, self.level.floor_y, color="mario")
        self.prev_jump = False

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit(0)
                if ev.key == pygame.K_v:
                    self.level.vibes = not self.level.vibes
                    self.synth.beep()
                if ev.key == pygame.K_s:
                    self.level.scanlines = not self.level.scanlines
                    self.synth.beep()
                if ev.key == pygame.K_r:
                    self.reset()
                if ev.key in (pygame.K_z, pygame.K_SPACE, pygame.K_k):
                    # Pow trigger via Down+Jump near POW
                    if self.player.on_ground:
                        # if overlapping pow from top, will trigger below on impact; here: "stomp" pow
                        pass

        self.keys = pygame.key.get_pressed()

        # One-shot jump
        jump_pressed = self.keys[pygame.K_z] or self.keys[pygame.K_SPACE] or self.keys[pygame.K_k]
        if jump_pressed and not self.prev_jump and (self.player.on_ground or self.player.coyote>0):
            self.player.jump(self.synth)
        self.prev_jump = jump_pressed

        # Down+Jump on floor near POW -> trigger
        if (self.keys[pygame.K_DOWN] or self.keys[pygame.K_s]) and jump_pressed and self.player.on_ground:
            if self.level.pow and abs(self.player.x - self.level.pow.rect.centerx) < 24:
                self.level.trigger_pow(self.synth)

    def logic(self, dt):
        self.player.update(self.keys, dt, self.level, self.synth)

        # Update enemies
        for e in self.level.enemies:
            e.update(dt, self.level, self.level.vibes)

        # Player vs enemies
        self.collisions_player_enemies()

        # Enemy state: sliding friction
        for e in self.level.enemies:
            if e.state == ENEMY_SLIDING:
                e.vx *= 0.98
                if abs(e.vx) < 0.02:
                    e.vx = 0

        # Remove defeated (sliding stopped) -> turn into coin
        survivors = []
        for e in self.level.enemies:
            if e.state == ENEMY_SLIDING and abs(e.vx) < 0.001:
                # defeated -> coin
                self.level.add_particles(e.x, e.y-6, PALETTE["coin"], 10)
                self.player.score += 800
                self.player.coins += 1
                self.synth.coin()
            else:
                survivors.append(e)
        self.level.enemies = survivors

        # All defeated -> next phase
        if len(self.level.enemies) == 0:
            self.level.phase += 1
            self.synth.phase()
            self.level._spawn_wave(self.level.phase)

        # Particles
        self.level.update_particles(dt)

        # Shake decay
        if self.level.shake > 0:
            self.level.shake -= dt
            if self.level.shake < 0: self.level.shake = 0

        # Player invulnerability timer
        if self.player.invuln > 0:
            self.player.invuln -= dt
            if self.player.invuln < 0: self.player.invuln = 0

    def collisions_player_enemies(self):
        pr = self.player.rect()

        for e in self.level.enemies:
            er = e.rect()
            if pr.colliderect(er):
                # Determine relative
                if e.state == ENEMY_FLIPPED:
                    # kick!
                    e.state = ENEMY_SLIDING
                    e.vx = 2.6 if self.player.x <= e.x else -2.6
                    self.player.score += 400
                    self.level.add_particles(e.x, e.y, PALETTE["white"], 12)
                    self.synth.kick()
                elif e.state == ENEMY_WALK:
                    if self.player.invuln <= 0:
                        # hurt
                        self.player.lives -= 1
                        self.player.invuln = 2.0
                        self.synth.hurt()
                        self.level.shake = 0.3
                        # respawn player
                        self.player.x = BASE_W//2
                        self.player.y = self.level.floor_y
                        self.player.vx = self.player.vy = 0

        # Bump flips (already handled in Level.bump_platform)

    def draw(self, t):
        # background
        draw_bg(self.frame, t, self.level.vibes)

        # vibes trails
        if self.level.vibes:
            self.trail.fill((0,0,0,0))
            self.trail.blit(self.frame, (0,0))
            self.trail.fill((255,255,255,16), special_flags=pygame.BLEND_RGBA_MIN)

        # pipes/platforms/POW
        draw_pipes(self.frame, self.level)
        draw_platforms(self.frame, self.level, t)
        draw_pow(self.frame, self.level)

        # enemies
        for e in self.level.enemies:
            e.draw(self.frame)

        # player
        self.player.draw(self.frame, t)

        # particles
        draw_particles(self.frame, self.level)

        # UI
        draw_ui(self.frame, self, self.font)

        # screen shake & blit to window (scaled)
        ox = oy = 0
        if self.level.shake > 0:
            mag = 2 if not self.level.vibes else 4
            ox = random.randint(-mag, mag)
            oy = random.randint(-mag, mag)

        # vibes: subtle palette shift overlay
        if self.level.vibes:
            col = (int(16+16*math.sin(t*1.4)), int(16+16*math.sin(t*1.2+1)), int(16+16*math.sin(t*1.6+2)), 40)
            tint = pygame.Surface((BASE_W, BASE_H), pygame.SRCALPHA)
            tint.fill(col)
            self.frame.blit(tint, (0,0), special_flags=pygame.BLEND_RGBA_ADD)

        # Scale and present
        scaled = pygame.transform.scale(self.frame, self.window.get_size())
        self.window.fill((0,0,0))
        self.window.blit(scaled, (ox, oy))

        if self.level.scanlines:
            crt_scanlines(self.window)

        pygame.display.flip()

    def run(self):
        t0 = time.time()
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            t = time.time() - t0

            self.handle_events()
            self.logic(dt)
            self.draw(t)

def main():
    Game().run()

if __name__ == "__main__":
    main()
