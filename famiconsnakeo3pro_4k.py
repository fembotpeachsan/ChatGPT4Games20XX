"""
Snake (Famicom‑style) – single‑file edition
Author: ChatGPT‑o3
Requirements: pygame, numpy
Tested with: Python 3.11, pygame 2.5, numpy 1.26
"""

import sys
import random
import math
import pygame as pg
import numpy as np

# ──────────────────────────────── #
# Configuration & Famicom palette #
# ──────────────────────────────── #

# Window / grid
WIN_W, WIN_H = 600, 400
CELL      = 20          # each grid cell = 20×20 px
GRID_W    = WIN_W // CELL
GRID_H    = WIN_H // CELL

FPS          = 60        # fixed refresh
START_DELAY  = 10        # frames between moves at score 0   (60 FPS / 10 = 6 moves/s)
MIN_DELAY    = 2         # fastest (≈30 moves/s @60 FPS)
SPEED_FACTOR = 5         # speed up every N points

# Colours (approximate NTSC NES palette)
COL_BG   = (  0,   0,   0)  # black
COL_SNAKE= ( 48, 190,  48)  # bright green
COL_APP  = (208,  32,  32)  # red
COL_BDR  = (224, 224, 224)  # off‑white for border / UI
COL_TXT  = COL_BDR

# ────────────────── #
# Helpers – sounds   #
# ────────────────── #

SAMPLE_RATE = 44100

def _square_wave(freq: float, dur: float, vol: float = .4) -> pg.mixer.Sound:
    """Return a pygame Sound with a square wave of given frequency/duration."""
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), False)
    wave = np.sign(np.sin(2 * np.pi * freq * t)) * vol
    buf = np.int16(wave * 32767).tobytes()
    return pg.mixer.Sound(buffer=buf)

def _triangle_wave(freq: float, dur: float, vol: float = .4) -> pg.mixer.Sound:
    """Return a pygame Sound with a triangle wave (less harsh)."""
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), False)
    wave = (2 / np.pi) * np.arcsin(np.sin(2 * np.pi * freq * t)) * vol
    buf = np.int16(wave * 32767).tobytes()
    return pg.mixer.Sound(buffer=buf)

def load_sfx() -> dict[str, pg.mixer.Sound]:
    """Generate and cache beeps/boops."""
    return {
        "move": _triangle_wave(440, 0.05, .25),
        "eat" : _square_wave  (660, 0.10, .4 ),
        "die" : _square_wave  (110, 0.40, .6 ),
    }

# ────────────────── #
# Game objects       #
# ────────────────── #

Vec2 = pg.math.Vector2

class Snake:
    """Grid‑based snake; head is element 0 in the body list."""
    def __init__(self):
        self.body = [Vec2(GRID_W//2, GRID_H//2)]
        self.dir  = Vec2(1, 0)     # start moving right
        self.grow = 0              # segments to add after eating

    def change_dir(self, new_dir: Vec2):
        """Change direction if not opposite (no 180° turns)."""
        if (self.dir + new_dir) != Vec2():  # not opposite
            self.dir = new_dir

    def move(self):
        new_head = self.body[0] + self.dir
        self.body.insert(0, new_head)
        if self.grow > 0:
            self.grow -= 1
        else:
            self.body.pop()        # drop tail

    def collide_self(self) -> bool:
        return self.body[0] in self.body[1:]

    def collide_wall(self) -> bool:
        x, y = self.body[0]
        return not (0 <= x < GRID_W and 0 <= y < GRID_H)

# ────────────────── #
# Main game class    #
# ────────────────── #

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.pre_init(SAMPLE_RATE, -16, 1, 512)
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIN_W, WIN_H))
        pg.display.set_caption("Snake – Famicom Edition")
        self.clock = pg.time.Clock()
        self.font  = pg.font.SysFont("Courier", 18, bold=True)
        self.sfx   = load_sfx()

        self.reset()

    # ------------ Game state ------------ #
    def reset(self):
        self.snake = Snake()
        self.spawn_apple()
        self.score      = 0
        self.delay      = START_DELAY
        self.frames     = 0      # frame counter for timing moves
        self.game_over  = False

    def spawn_apple(self):
        """Place apple at random empty grid position."""
        empties = [Vec2(x, y)
                   for x in range(GRID_W)
                   for y in range(GRID_H)
                   if Vec2(x, y) not in self.snake.body]
        self.apple = random.choice(empties)

    # ------------ Update / logic ------------ #
    def update(self):
        keys = pg.key.get_pressed()
        if not self.game_over:
            # Direction input (WASD only)
            if keys[pg.K_w]: self.snake.change_dir(Vec2(0, -1))
            elif keys[pg.K_s]: self.snake.change_dir(Vec2(0,  1))
            elif keys[pg.K_a]: self.snake.change_dir(Vec2(-1, 0))
            elif keys[pg.K_d]: self.snake.change_dir(Vec2( 1, 0))

            # Move at fixed "tick" speed
            self.frames += 1
            if self.frames >= self.delay:
                self.frames = 0
                self.snake.move()
                self.sfx["move"].play()

                # Check collisions
                if self.snake.collide_wall() or self.snake.collide_self():
                    self.sfx["die"].play()
                    self.game_over = True
                # Check apple
                elif self.snake.body[0] == self.apple:
                    self.score += 1
                    self.snake.grow += 1
                    self.sfx["eat"].play()
                    self.spawn_apple()
                    # speed up
                    self.delay = max(MIN_DELAY, START_DELAY - self.score // SPEED_FACTOR)

        else:
            # Wait for R to restart
            if keys[pg.K_r]:
                self.reset()

    # ------------ Render ------------ #
    def draw_cell(self, pos: Vec2, colour):
        r = pg.Rect(int(pos.x * CELL), int(pos.y * CELL), CELL, CELL)
        pg.draw.rect(self.screen, colour, r)

    def render(self):
        self.screen.fill(COL_BG)

        # Draw border (optional aesthetic)
        pg.draw.rect(self.screen, COL_BDR, pg.Rect(0, 0, WIN_W, WIN_H), 2)

        # Apple
        self.draw_cell(self.apple, COL_APP)

        # Snake
        for segment in self.snake.body:
            self.draw_cell(segment, COL_SNAKE)

        # UI – score
        txt = self.font.render(f"Score: {self.score}", True, COL_TXT)
        self.screen.blit(txt, (8, 8))

        # Game‑over overlay
        if self.game_over:
            overlay = self.font.render("GAME OVER – PRESS R", True, COL_TXT)
            rect = overlay.get_rect(center=(WIN_W//2, WIN_H//2))
            self.screen.blit(overlay, rect)

        pg.display.flip()

    # ------------ Game loop ------------ #
    def run(self):
        while True:
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit(); sys.exit()

            self.update()
            self.render()
            self.clock.tick(FPS)

# ────────────────── #
# Entrypoint         #
# ────────────────── #

if __name__ == "__main__":
    Game().run()
