#!/usr/bin/env python3
"""
Neon‑Synthwave Breakout — single‑file edition
Window  : 600 × 400
Controls: Move the mouse left/right to steer the paddle
Sounds  : All “beep/boop/wa‑wa” tones are procedurally
          synthesized at run‑time (square waves, 44.1 kHz).
Author  : ChatGPT (2025)
"""

import math, sys, struct, random
import pygame as pg

# ------------------------------------------------------------
# === Configuration ==========================================
WIDTH, HEIGHT = 600, 400
FPS            = 60
BRICK_ROWS     = 6
BRICK_COLS     = 10
BRICK_W        = WIDTH // BRICK_COLS
BRICK_H        = 18
PADDLE_W       = 80
PADDLE_H       = 12
BALL_SIZE      = 8

# Neon / synthwave palette
BACKGROUND_CLR = (15, 0, 26)          # deep space purple
PADDLE_CLR     = (255, 47, 209)       # neon magenta
BALL_CLR       = (0, 234, 255)        # electric cyan
BRICK_CLRS     = [
    (255, 94, 0), (255, 0, 106), (171, 0, 255),
    (0, 106, 255), (0, 234, 255), (0, 255, 149)
]

# ------------------------------------------------------------
# === Tiny synth helper ======================================
SAMPLE_RATE = 44100
pg.mixer.pre_init(SAMPLE_RATE, size=-16, channels=1)
pg.init()

def square_wave(freq: float, duration: float, volume: float = 0.6) -> pg.mixer.Sound:
    """Return a pygame Sound containing a square‑wave burst."""
    frames = int(duration * SAMPLE_RATE)
    period = SAMPLE_RATE / freq
    hi = int(volume * 32767)
    lo = -hi
    buf = bytearray()
    for i in range(frames):
        buf += struct.pack("<h", hi if (i % period) < (period / 2) else lo)
    return pg.mixer.Sound(buffer=bytes(buf))

def descending_wa(duration: float = 1.0,
                  freq_hi: float = 980,
                  freq_lo: float = 220,
                  volume: float = 0.6) -> pg.mixer.Sound:
    """Generate one ‘wa‑wa’ descending tone."""
    frames = int(duration * SAMPLE_RATE)
    buf = bytearray()
    phase = 0.0
    for n in range(frames):
        t = n / frames
        freq = freq_hi + (freq_lo - freq_hi) * t  # linear slide
        phase += 2 * math.pi * freq / SAMPLE_RATE
        sample = int(volume * 32767 * (1 if math.sin(phase) >= 0 else -1))
        buf += struct.pack("<h", sample)
    return pg.mixer.Sound(buffer=bytes(buf))

# Pre‑bake common SFX
BEEP  = square_wave(880, 0.06)   # wall / brick
BOOP  = square_wave(660, 0.06)   # paddle
WA_WA = descending_wa(1.2)       # game‑over

# ------------------------------------------------------------
# === Game objects ===========================================
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Neon‑Synthwave Breakout")
clock = pg.time.Clock()

# Bricks: rects in a list
bricks = []
for row in range(BRICK_ROWS):
    for col in range(BRICK_COLS):
        bricks.append(pg.Rect(col * BRICK_W, 60 + row * BRICK_H, BRICK_W - 2, BRICK_H - 2))

# Paddle & ball
paddle = pg.Rect((WIDTH - PADDLE_W) // 2, HEIGHT - 40, PADDLE_W, PADDLE_H)
ball   = pg.Rect(WIDTH // 2, HEIGHT // 2, BALL_SIZE, BALL_SIZE)
ball_dx, ball_dy = random.choice([-4, 4]), -4

# ------------------------------------------------------------
# === Main loop ==============================================
running, game_over, victory = True, False, False
font = pg.font.SysFont("arial", 28, bold=True)

def reset():
    global ball_dx, ball_dy, ball, bricks, game_over, victory
    ball.topleft = (WIDTH // 2, HEIGHT // 2)
    ball_dx, ball_dy = random.choice([-4, 4]), -4
    bricks.clear()
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            bricks.append(pg.Rect(col * BRICK_W, 60 + row * BRICK_H, BRICK_W - 2, BRICK_H - 2))
    game_over = victory = False

while running:
    for e in pg.event.get():
        if e.type == pg.QUIT:
            running = False
        elif e.type == pg.KEYDOWN and e.key == pg.K_r:
            reset()

    if not game_over and not victory:
        # --- Paddle follows mouse ---
        mouse_x = pg.mouse.get_pos()[0]
        paddle.centerx = mouse_x
        paddle.clamp_ip(pg.Rect(0, 0, WIDTH, HEIGHT))

        # --- Move ball ---
        ball.x += ball_dx
        ball.y += ball_dy

        # Wall collisions
        if ball.left <= 0 or ball.right >= WIDTH:
            ball_dx = -ball_dx; BEEP.play()
        if ball.top <= 0:
            ball_dy = -ball_dy; BEEP.play()

        # Paddle collision
        if ball.colliderect(paddle) and ball_dy > 0:
            ball_dy = -ball_dy
            # tweak angle based on hit position
            offset = (ball.centerx - paddle.centerx) / (PADDLE_W // 2)
            ball_dx = max(-5, min(5, ball_dx + offset * 2))
            BOOP.play()

        # Brick collisions
        hit_idx = ball.collidelist(bricks)
        if hit_idx != -1:
            hit_rect = bricks.pop(hit_idx)
            # Determine rebound direction
            if abs(ball.bottom - hit_rect.top) < 8 and ball_dy > 0:
                ball_dy = -ball_dy
            elif abs(ball.top - hit_rect.bottom) < 8 and ball_dy < 0:
                ball_dy = -ball_dy
            else:
                ball_dx = -ball_dx
            BEEP.play()

        # Check for lose / win
        if ball.top >= HEIGHT:
            game_over = True
            WA_WA.play()
        if not bricks:
            victory = True

    # --- Drawing -------------------------------------------------
    screen.fill(BACKGROUND_CLR)

    # Bricks
    for i, rect in enumerate(bricks):
        clr = BRICK_CLRS[i // BRICK_COLS]
        pg.draw.rect(screen, clr, rect)

    # Paddle & ball
    pg.draw.rect(screen, PADDLE_CLR, paddle)
    pg.draw.rect(screen, BALL_CLR, ball)

    # UI text when finished
    if game_over:
        txt = font.render("GAME OVER  (press R to retry)", True, (255, 0, 106))
        screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2)))
    elif victory:
        txt = font.render("YOU WIN!  (press R to play again)", True, (0, 255, 149))
        screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2)))

    pg.display.flip()
    clock.tick(FPS)

pg.quit()
sys.exit()
