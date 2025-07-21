#!/usr/bin/env python3
# snake_famicon.py — single‑file Snake with retro NES vibes
# • 600×400 window (30×20 tiles) @ 60 FPS
# • No external assets: colours are classic Famicom palette
# • Square‑wave SFX are synthesised on‑the‑fly (eat / death “beep‑boop”)

import pygame, random, math, sys, numpy as np

# ───────────────────────── Config ──────────────────────────
WIDTH, HEIGHT      = 600, 400          # window size
TILE               = 20                # 30×20 grid
FPS                = 60
MOVE_TICK_MS       = 100               # snake moves every 100 ms (~10 Hz)

# Famicom palette (a few hand‑picked tones)
COL_BG   = ( 16,  16,  16)   # dark charcoal
COL_GRID = ( 48,  48,  48)   # subtle grid
COL_HEAD = (  0, 221,  80)   # bright green
COL_BODY = (  0, 171,  40)   # darker green
COL_FOOD = (228,  56,  64)   # tomato red
COL_TEXT = (255, 255, 255)

# ─────────────── Helper: generate square‑wave SFX ──────────
def make_beep(freq=440, dur=0.1, vol=0.4):
    sr = 44100
    t  = np.linspace(0, dur, int(sr*dur), False)
    wave = vol * np.sign(np.sin(2*math.pi*freq*t))
    audio = np.int16(wave * 32767)
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo.copy())

SFX_EAT   = make_beep(880, 0.07, 0.5)      # higher “blip”
SFX_DIE   = make_beep(110, 0.25, 0.6)      # low “boop”

# ───────────────────── Game state class ────────────────────
class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.dir      = (1, 0)                       # start moving right
        self.snake    = [(10, 10), (9, 10), (8, 10)]
        self.spawn_food()
        self.alive    = True
        self.timer    = 0

    def spawn_food(self):
        while True:
            self.food = (random.randrange(0, WIDTH//TILE),
                          random.randrange(0, HEIGHT//TILE))
            if self.food not in self.snake:
                break

    # ───────── Update (called every MOVETICK_MS) ──────────
    def step(self):
        if not self.alive:
            return
        x, y = self.snake[0]
        dx, dy = self.dir
        new_head = ((x + dx) % (WIDTH//TILE),
                    (y + dy) % (HEIGHT//TILE))

        # collision with self?
        if new_head in self.snake:
            self.alive = False
            SFX_DIE.play()
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            SFX_EAT.play()
            self.spawn_food()
        else:
            self.snake.pop()  # move forwards

    # ─────────── Render to a surface ────────────
    def draw(self, surf):
        surf.fill(COL_BG)
        # optional grid for vibes
        for x in range(0, WIDTH, TILE):
            pygame.draw.line(surf, COL_GRID, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILE):
            pygame.draw.line(surf, COL_GRID, (0, y), (WIDTH, y))

        # food
        fx, fy = self.food
        pygame.draw.rect(surf, COL_FOOD,
                         (fx*TILE, fy*TILE, TILE, TILE))

        # snake
        for i, (sx, sy) in enumerate(self.snake):
            col = COL_HEAD if i == 0 else COL_BODY
            pygame.draw.rect(surf, col,
                             (sx*TILE, sy*TILE, TILE, TILE))

        if not self.alive:
            font = pygame.font.SysFont("PressStart2P,monospace", 20)
            txt  = font.render("GAME OVER – Press R to restart", True, COL_TEXT)
            surf.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2)))

# ────────────────────────── Main loop ──────────────────────
def main():
    pygame.init()
    pygame.display.set_caption("SNAKE ‑ 8‑bit vibes")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock  = pygame.time.Clock()
    game   = SnakeGame()

    move_event = pygame.USEREVENT + 1
    pygame.time.set_timer(move_event, MOVE_TICK_MS)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w) and game.dir != (0, 1):
                    game.dir = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s) and game.dir != (0, -1):
                    game.dir = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a) and game.dir != (1, 0):
                    game.dir = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and game.dir != (-1, 0):
                    game.dir = (1, 0)
                elif event.key == pygame.K_r and not game.alive:
                    game.reset()

            elif event.type == move_event:
                game.step()

        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
