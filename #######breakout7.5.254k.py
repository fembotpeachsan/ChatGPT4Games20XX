"""
Breakout Classic – retro code‑only edition
Python 3.x + Pygame (2.x) – 600 × 400 window – Windows‑friendly
No external assets: all graphics are colored rects, all sounds are synthesized on‑the‑fly
"""

import pygame, random, math, array, sys

# ---------- user‑tweakable constants ----------
WIN_W, WIN_H          = 600, 400
BRICK_COLS, BRICK_ROWS = 10, 5
BRICK_W, BRICK_H      = WIN_W // BRICK_COLS, 20
PADDLE_W, PADDLE_H    = 80, 10
BALL_SIZE             = 10
BALL_SPEED            = 4.0            # initial scalar speed
FPS                   = 60
# ---------------------------------------------

pygame.init()
# 16‑bit mono mixer so we can feed signed‑short arrays directly
pygame.mixer.init(frequency=44_100, size=-16, channels=1)
screen  = pygame.display.set_mode((WIN_W, WIN_H))
clock   = pygame.time.Clock()
pygame.display.set_caption("Breakout Classic")

def synth_tone(freq_hz=880, dur_ms=100, vol=0.5):
    """Generate a pygame.Sound of a sine‑wave tone (no numpy needed)."""
    sample_rate = 44_100
    n_samples   = int(sample_rate * dur_ms / 1000)
    buf = array.array("h")  # signed short
    amplitude = int(32_767 * vol)
    for i in range(n_samples):
        t = i / sample_rate
        sample = amplitude * math.sin(2 * math.pi * freq_hz * t)
        buf.append(int(sample))
    return pygame.mixer.Sound(buffer=buf)

SND_BEEP = synth_tone(1000, 80, 0.6)     # paddle / wall
SND_BOOP = synth_tone(500,  80, 0.6)     # brick

def make_bricks():
    bricks = []
    colors = [(231, 76, 60), (241, 196, 15), (46, 204, 113),
              (52, 152, 219), (155, 89, 182)]
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            rect = pygame.Rect(col*BRICK_W+1, row*BRICK_H+1,
                               BRICK_W-2, BRICK_H-2)
            bricks.append((rect, colors[row % len(colors)]))
    return bricks

def reset():
    paddle = pygame.Rect((WIN_W-PADDLE_W)//2, WIN_H-40, PADDLE_W, PADDLE_H)
    ball   = pygame.Rect(paddle.centerx-BALL_SIZE//2, paddle.y-BALL_SIZE,
                         BALL_SIZE, BALL_SIZE)
    angle  = random.uniform(math.radians(30), math.radians(150))
    vel    = [BALL_SPEED*math.cos(angle), -BALL_SPEED*math.sin(angle)]
    return paddle, ball, vel, make_bricks(), False

paddle, ball, vel, bricks, game_over = reset()

font_big  = pygame.font.SysFont("consolas", 32, bold=True)
font_small= pygame.font.SysFont("consolas", 18)

running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE and game_over:
            paddle, ball, vel, bricks, game_over = reset()

    # paddle follows mouse x
    mx, _ = pygame.mouse.get_pos()
    paddle.centerx = mx
    paddle.clamp_ip(screen.get_rect())

    if not game_over:
        # move ball
        ball.x += vel[0]
        ball.y += vel[1]

        # wall collisions
        if ball.left <= 0 or ball.right >= WIN_W:
            vel[0] = -vel[0]; SND_BEEP.play()
        if ball.top <= 0:
            vel[1] = -vel[1]; SND_BEEP.play()

        # paddle collision
        if ball.colliderect(paddle) and vel[1] > 0:
            # reflection with simple "english" off paddle
            hit_pos = (ball.centerx - paddle.centerx) / (PADDLE_W/2)
            angle   = hit_pos * math.radians(60)   # ±60°
            speed   = math.hypot(*vel)
            vel[0]  = speed * math.sin(angle)
            vel[1]  = -abs(speed * math.cos(angle))
            SND_BEEP.play()

        # brick collisions
        for idx, (b_rect, b_color) in enumerate(bricks):
            if ball.colliderect(b_rect):
                # basic direction reflection
                if abs(ball.bottom - b_rect.top) < 6 and vel[1] > 0:
                    vel[1] = -vel[1]
                elif abs(ball.top - b_rect.bottom) < 6 and vel[1] < 0:
                    vel[1] = -vel[1]
                else:
                    vel[0] = -vel[0]
                bricks.pop(idx)
                SND_BOOP.play()
                break

        # lose condition
        if ball.top > WIN_H:
            game_over = True

        # win condition → recreate bricks
        if not bricks:
            bricks = make_bricks()
            SND_BEEP.play()

    # ------- drawing -------
    screen.fill((25, 25, 25))
    for b_rect, b_color in bricks:
        pygame.draw.rect(screen, b_color, b_rect)
    pygame.draw.rect(screen, (200,200,200), paddle)
    pygame.draw.rect(screen, (255,255,255), ball)

    if game_over:
        text = font_big.render("GAME OVER", True, (255,255,255))
        tip  = font_small.render("Press SPACE to restart", True, (200,200,200))
        screen.blit(text, text.get_rect(center=(WIN_W//2, WIN_H//2-20)))
        screen.blit(tip,  tip.get_rect(center=(WIN_W//2, WIN_H//2+20)))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
