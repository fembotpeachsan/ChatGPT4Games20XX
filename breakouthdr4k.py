# Breakout — PURE VIBES (Files‑Off | 60 FPS | NES-ish)
# Single-file Pygame 2.x. No external assets. Deterministic via VIBE_CODE.
# Windows-friendly: vsync when available, fixed 60 FPS logic, no disk I/O.

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
os.environ["SDL_VIDEO_CENTERED"] = "1"
os.environ.setdefault("SDL_AUDIODRIVER", "directsound")  # helpful on Windows
os.environ["SDL_WINDOWS_DPI_AWARE"] = "1"

import math, random
from array import array

import pygame

# ---------- Config ----------
LOGICAL_W, LOGICAL_H = 256, 240        # NES-ish logical resolution
FPS = 60
FIXED_DT = 1.0 / FPS
TITLE = "Breakout — PURE VIBES (Files‑Off | 60 FPS | NES)"
VIBE_CODE = "pure-vibes-1.0a"          # change to spawn a different (deterministic) layout

# ---------- NES-ish palette (tiny subset) ----------
PALETTES = [
    # Deep night
    [(12,12,12),(29,43,83),(0,135,81),(251,242,54),(255,255,255)],
    # Sunset
    [(12,12,12),(111,38,61),(223,113,38),(255,204,111),(255,255,255)],
    # Ocean
    [(12,12,12),(0,40,104),(0,118,163),(0,170,204),(255,255,255)],
    # Mint
    [(12,12,12),(32,52,41),(86,125,70),(140,193,99),(255,255,255)],
]
palette_index = 0
BG, INK, C1, C2, WHITE = PALETTES[palette_index]

# ---------- Audio (square/triangle; no numpy needed) ----------
RATE = 44100
pygame.mixer.pre_init(RATE, -16, 1, 512)  # mono, small buffer for snappy SFX
pygame.init()

def tone(freq=440.0, ms=100, vol=0.25, wave="square"):
    """Generate a short tone as a pygame.Sound using pure Python (no numpy)."""
    n = int(RATE * (ms / 1000.0))
    amp = int(32767 * max(0.0, min(1.0, vol)))
    buf = array('h')
    phase = 0.0
    step = 2.0 * math.pi * float(freq) / RATE
    if wave == "square":
        for i in range(n):
            s = math.sin(phase)
            buf.append(amp if s >= 0.0 else -amp)
            phase += step
    elif wave == "triangle":
        for i in range(n):
            s = math.asin(math.sin(phase))  # triangle via asin(sin())
            buf.append(int((2 * amp / math.pi) * s))
            phase += step
    else:
        for i in range(n):
            s = math.sin(phase)
            buf.append(int(amp * s))
            phase += step
    return pygame.mixer.Sound(buffer=buf.tobytes())

SND_PADDLE = tone(220, 45, 0.25, "square")
SND_WALL   = tone(330, 45, 0.22, "square")
SND_BRICK  = tone(490, 38, 0.28, "square")
SND_LOST   = tone(110, 220, 0.25, "triangle")

# ---------- Window / surface ----------
FLAGS = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SCALED
try:
    screen = pygame.display.set_mode((LOGICAL_W, LOGICAL_H), FLAGS, vsync=1)
except TypeError:
    # Older SDL/Pygame versions without vsync kwarg
    screen = pygame.display.set_mode((LOGICAL_W, LOGICAL_H), FLAGS)

pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 16)

# ---------- Deterministic RNG from vibe-code ----------
def vibe_seed(text: str) -> int:
    """FNV-1a style hash -> 32-bit seed (deterministic)."""
    h = 2166136261
    for b in text.encode("utf-8"):
        h ^= b
        h = (h * 16777619) & 0xFFFFFFFF
    return h

rng = random.Random(vibe_seed(VIBE_CODE))

# ---------- Game objects ----------
def clamp(v, lo, hi): return lo if v < lo else hi if v > hi else v

class Paddle:
    def __init__(self):
        self.w, self.h = 32, 5
        self.x = (LOGICAL_W - self.w) * 0.5
        self.y = LOGICAL_H - 22
        self.speed = 150.0  # px/s

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt, left, right):
        dx = 0.0
        if left:  dx -= 1.0
        if right: dx += 1.0
        self.x += dx * self.speed * dt
        self.x = clamp(self.x, 4, LOGICAL_W - self.w - 4)

    def draw(self, surf):
        pygame.draw.rect(surf, WHITE, self.rect)
        # NES-ish notch
        pygame.draw.rect(surf, C2, self.rect.inflate(-self.w//2, -self.h+1))

class Ball:
    def __init__(self):
        self.r = 2
        self.reset()

    def reset(self, serve_from=None):
        self.speed = 110.0
        self.x = (LOGICAL_W * 0.5) - self.r
        self.y = LOGICAL_H * 0.6
        angle = math.radians(225 if rng.random() < 0.5 else 315)
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        if serve_from is not None:
            self.x = serve_from.x + serve_from.w * 0.5 - self.r
            self.y = serve_from.y - 8

    @property
    def rect(self):
        d = self.r * 2
        return pygame.Rect(int(self.x), int(self.y), d, d)

    def move_axis(self, bricks, axis, dt, paddle, game):
        # Move and handle collisions against walls/bricks/paddle, axis-wise for stability.
        old = self.x if axis == 'x' else self.y
        brick_hit = None  # Track brick hit to return
        if axis == 'x':
            self.x += self.vx * dt
            r = self.rect
            if r.left <= 0:
                self.x = 0
                self.vx = abs(self.vx)
                SND_WALL.play()
            elif r.right >= LOGICAL_W:
                self.x = LOGICAL_W - r.w
                self.vx = -abs(self.vx)
                SND_WALL.play()
            # Bricks X
            hit = r.collidelist(bricks.rects)
            if hit != -1:
                b = bricks.blocks[hit]
                if self.vx > 0: self.x = b.rect.left - r.w
                else:           self.x = b.rect.right
                self.vx = -self.vx
                brick_hit = hit
        else:
            self.y += self.vy * dt
            r = self.rect
            if r.top <= 0:
                self.y = 0
                self.vy = abs(self.vy)
                SND_WALL.play()
            # Paddle Y
            if r.colliderect(paddle.rect) and self.vy > 0:
                # Reflect with angle based on hit position
                hitpos = ( (self.x + self.r) - (paddle.x + paddle.w*0.5) ) / (paddle.w*0.5)
                hitpos = clamp(hitpos, -1.0, 1.0)
                angle = math.radians(300 + 30 * hitpos)  # 300° ± 30°
                self.vx = math.cos(angle) * self.speed
                self.vy = math.sin(angle) * self.speed
                # Nudge out
                self.y = paddle.y - r.h - 0.5
                SND_PADDLE.play()
            # Bricks Y
            hit = r.collidelist(bricks.rects)
            if hit != -1:
                b = bricks.blocks[hit]
                if self.vy > 0: self.y = b.rect.top - r.h
                else:           self.y = b.rect.bottom
                self.vy = -self.vy
                brick_hit = hit
        return brick_hit

    def update(self, dt, bricks, paddle, game):
        # Keep speed constant (avoid numeric drift)
        sp = math.hypot(self.vx, self.vy)
        if sp != 0:
            scale = self.speed / sp
            self.vx *= scale
            self.vy *= scale

        # Process collisions and collect hit bricks
        hit_x = self.move_axis(bricks, 'x', dt, paddle, game)
        hit_y = self.move_axis(bricks, 'y', dt, paddle, game)
        
        # Damage bricks after both axis checks (prevents index shifting issues)
        damaged = set()
        if hit_x is not None and hit_x not in damaged:
            bricks.damage(hit_x, game)
            damaged.add(hit_x)
        if hit_y is not None and hit_y not in damaged and hit_y < len(bricks.blocks):
            bricks.damage(hit_y, game)

    def draw(self, surf):
        r = self.rect
        pygame.draw.rect(surf, WHITE, r)
        pygame.draw.rect(surf, C1, r.inflate(-1, -1))

class Brick:
    __slots__ = ("x","y","w","h","hp","color")
    def __init__(self, x, y, w, h, hp, color):
        self.x, self.y, self.w, self.h, self.hp, self.color = x, y, w, h, hp, color
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.w), int(self.h))

class BrickGrid:
    def __init__(self, rng, level=1):
        self.level = level
        self.blocks = []
        self.rects = []

        cols = 12
        brick_w = 20
        brick_h = 10
        left_margin = (LOGICAL_W - cols * brick_w) // 2
        top = 36
        rows = 6 + (level - 1) % 3  # modest growth
        rows = min(rows, 10)

        # Deterministic pattern from vibe RNG (holes + hp bands)
        holes = set()
        # Fix for Python 3.13 - convert tuple to string for seeding
        seed_value = f"{rng.random():.10f}_{level}"
        rng2 = random.Random(seed_value)
        hole_count = 6 + level  # light sparsity
        for _ in range(hole_count):
            holes.add((rng2.randrange(rows), rng2.randrange(cols)))

        row_colors = [INK, C1, C2, WHITE]
        for r in range(rows):
            for c in range(cols):
                if (r, c) in holes and r > 1:
                    continue
                x = left_margin + c * brick_w
                y = top + r * (brick_h + 2)
                hp = 1 + (r // 3)  # harder rows are higher
                color = row_colors[(r // 2) % len(row_colors)]
                b = Brick(x, y, brick_w-1, brick_h, hp, color)
                self.blocks.append(b)
                self.rects.append(b.rect)

    def damage(self, idx, game):
        b = self.blocks[idx]
        b.hp -= 1
        if b.hp <= 0:
            # Remove brick and add score
            del self.blocks[idx]
            del self.rects[idx]
            game.score += 50  # Score per brick destroyed
            SND_BRICK.play()
        else:
            SND_WALL.play()

    def draw(self, surf):
        for b in self.blocks:
            pygame.draw.rect(surf, b.color, b.rect)
            # tiny shine line for NES-ish depth
            top = pygame.Rect(b.rect.x, b.rect.y, b.rect.w, 1)
            pygame.draw.rect(surf, WHITE, top)

# ---------- Game state ----------
class Game:
    def __init__(self):
        self.reset_all()

    def reset_all(self):
        global BG, INK, C1, C2, WHITE
        self.score = 0
        self.lives = 3
        self.level = 1
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = BrickGrid(rng, self.level)
        self.serving = True
        self.paused = False
        # Palette (re-sync globals from current index)
        BG, INK, C1, C2, WHITE = PALETTES[palette_index]

    def next_level(self):
        self.level += 1
        self.paddle = Paddle()
        self.ball = Ball()
        self.ball.speed += min(40, 5*self.level)
        self.bricks = BrickGrid(rng, self.level)
        self.serving = True

    def lose_life(self):
        self.lives -= 1
        SND_LOST.play()
        if self.lives < 0:
            self.reset_all()
        else:
            self.ball = Ball()
            self.serving = True

    def update(self, dt, input_left, input_right, launch):
        if self.paused:
            return
        self.paddle.update(dt, input_left, input_right)

        # Serve (stick ball to paddle until launch)
        if self.serving:
            self.ball.x = self.paddle.x + self.paddle.w * 0.5 - self.ball.r
            self.ball.y = self.paddle.y - 8
            if launch:
                self.serving = False
        else:
            self.ball.update(dt, self.bricks, self.paddle, self)

            # Out of bounds (bottom)
            if self.ball.rect.top > LOGICAL_H:
                self.lose_life()

            # Level clear
            if len(self.bricks.blocks) == 0:
                self.score += 1000
                self.next_level()

    def draw_hud(self, surf):
        text = f"SCORE {self.score:06d}   LIVES {max(0,self.lives)}   LV {self.level}   VIBE {VIBE_CODE}"
        img = font.render(text, True, WHITE)
        surf.blit(img, (8, 8))

def main():
    global palette_index, BG, INK, C1, C2, WHITE

    game = Game()

    run = True
    accumulator = 0.0

    # Subtle starfield vibe (procedural)
    stars = [(rng.randrange(LOGICAL_W), rng.randrange(LOGICAL_H//2), rng.choice([INK, C1, C2])) for _ in range(36)]

    while run:
        # ---- Timing ----
        dt_real = clock.tick(FPS) / 1000.0
        accumulator += dt_real

        # ---- Input ----
        launch = False
        left = right = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    run = False
                elif e.key == pygame.K_p:
                    game.paused = not game.paused
                elif e.key == pygame.K_r:
                    game.reset_all()
                elif e.key == pygame.K_F1:
                    palette_index = (palette_index + 1) % len(PALETTES)
                    BG, INK, C1, C2, WHITE = PALETTES[palette_index]
                elif e.key == pygame.K_SPACE:
                    launch = True

        keys = pygame.key.get_pressed()
        left  = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        # ---- Fixed-step update (deterministic) ----
        while accumulator >= FIXED_DT:
            game.update(FIXED_DT, left, right, launch)
            accumulator -= FIXED_DT

        # ---- Draw ----
        screen.fill(BG)

        # starfield vibe
        for i, (sx, sy, col) in enumerate(stars):
            screen.set_at((sx, (sy + pygame.time.get_ticks() // 20) % (LOGICAL_H-120)), col)

        # playfield frame
        pygame.draw.rect(screen, INK, pygame.Rect(2, 24, LOGICAL_W-4, LOGICAL_H-28), 2)

        # entities
        game.bricks.draw(screen)
        game.paddle.draw(screen)
        game.ball.draw(screen)

        # HUD
        game.draw_hud(screen)

        # Serve prompt / paused
        if game.paused:
            t = font.render("PAUSED", True, WHITE)
            screen.blit(t, (LOGICAL_W//2 - t.get_width()//2, LOGICAL_H//2 - 8))
        elif game.serving:
            t = font.render("SPACE TO SERVE", True, WHITE)
            screen.blit(t, (LOGICAL_W//2 - t.get_width()//2, LOGICAL_H//2 - 8))

        # tiny footer
        footer = font.render("F1: palette  ·  P: pause  ·  R: reset  ·  ESC: quit", True, C2)
        screen.blit(footer, (8, LOGICAL_H - 16))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
