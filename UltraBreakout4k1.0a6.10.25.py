# test.py

import pygame
import sys
import random
import math
import numpy as np

"""Breakout clone – single file, zero‑asset, Atari‑style sound
Features added in this revision:
• Proper win condition – when all bricks are gone you see a "YOU WIN – Play again? Y/N" prompt
• Proper game‑over – after last life is lost shows "GAME OVER – Play again? Y/N"
• Press **Y** (or **y**) to restart instantly, **N** (or **ESC/Q**) to quit
• Ball deflection off the paddle mimics the original Breakout angle algorithm
The whole game sits inside a main‑loop that can relaunch itself without having to respawn a new
process – so restart is instant and state is fully reset.
"""

# === Configuration ===
SCREEN_WIDTH   = 800
SCREEN_HEIGHT  = 600
FPS            = 60

BRICK_ROWS     = 6
BRICK_COLS     = 12
BRICK_WIDTH    = SCREEN_WIDTH // BRICK_COLS
BRICK_HEIGHT   = 25
BRICK_PADDING  = 5

PADDLE_WIDTH   = 100
PADDLE_HEIGHT  = 15
PADDLE_Y       = SCREEN_HEIGHT - 40

BALL_RADIUS    = 10
BALL_SPEED     = 5

LIVES_START    = 3

# Colors
WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)
BROWN  = (153,  76,   0)
ORANGE = (255, 165,   0)
PURPLE = (160,  32, 240)
GRAY   = (192, 192, 192)
RED    = (255,   0,   0)
GREEN  = (  0, 255,   0)
BLUE   = (  0,   0, 255)

# === Atari‑style Sound Manager (stereo‑safe) ===
class AtariSoundManager:
    def __init__(self):
        pygame.mixer.pre_init(44_100, -16, 1, 256)
        pygame.mixer.init()

    def _tone(self, freq: int, duration: float):
        sr = 44_100
        n = int(sr * duration)
        t = np.linspace(0, duration, n, False)
        mono_wave = 0.5 * np.sign(np.sin(2 * math.pi * freq * t))
        samples = (mono_wave * 32_767).astype(np.int16)
        # duplicate for stereo if mixer ended‑up stereo
        _, _, ch = pygame.mixer.get_init()
        if ch == 2:
            samples = np.column_stack((samples, samples))
        return pygame.sndarray.make_sound(samples)

    def play(self, freq: int, dur: float = 0.07):
        self._tone(freq, dur).play()

    def bounce(self):      self.play(440, 0.04)
    def brick(self):       self.play(880, 0.05)
    def lost_life(self):   self.play(220, 0.30)

# === Game Objects ===
class Paddle:
    def __init__(self):
        self.rect = pygame.Rect((SCREEN_WIDTH - PADDLE_WIDTH)//2, PADDLE_Y, PADDLE_WIDTH, PADDLE_HEIGHT)

    def update(self):
        mx, _ = pygame.mouse.get_pos()
        self.rect.centerx = mx
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def draw(self, surf):
        pygame.draw.rect(surf, WHITE, self.rect)

class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x, self.y = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
        ang = random.uniform(-math.pi/4, math.pi/4) + math.pi
        self.vx = BALL_SPEED * math.cos(ang)
        self.vy = BALL_SPEED * math.sin(ang)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # Walls
        if self.x - BALL_RADIUS <= 0 or self.x + BALL_RADIUS >= SCREEN_WIDTH:
            self.vx *= -1; sounds.bounce()
        if self.y - BALL_RADIUS <= 0:
            self.vy *= -1; sounds.bounce()

    def rect(self):
        return pygame.Rect(self.x-BALL_RADIUS, self.y-BALL_RADIUS, BALL_RADIUS*2, BALL_RADIUS*2)

    def draw(self, surf):
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), BALL_RADIUS)

class Brick:
    palette = [BROWN, ORANGE, PURPLE, GRAY, RED, GREEN]
    def __init__(self, c, r):
        self.rect = pygame.Rect(c*BRICK_WIDTH+BRICK_PADDING, r*BRICK_HEIGHT+BRICK_PADDING+40,
                                BRICK_WIDTH-BRICK_PADDING*2, BRICK_HEIGHT-BRICK_PADDING*2)
        self.color = Brick.palette[r % len(Brick.palette)]
    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)

# === Core helpers ===

def draw_hud(surface, font, score, lives):
    surface.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    surface.blit(font.render(f"Lives: {lives}", True, WHITE), (SCREEN_WIDTH-110, 10))


def end_screen(surface, font, message):
    surface.fill(BLACK)
    msg = font.render(message, True, RED)
    sub = font.render("Play again? Y/N", True, WHITE)
    surface.blit(msg, ((SCREEN_WIDTH-msg.get_width())//2, SCREEN_HEIGHT//2-30))
    surface.blit(sub, ((SCREEN_WIDTH-sub.get_width())//2, SCREEN_HEIGHT//2+10))
    pygame.display.flip()


def run_once():
    """Runs a single game session. Returns True if player won, False if out of lives"""
    bricks = [Brick(c, r) for r in range(BRICK_ROWS) for c in range(BRICK_COLS)]
    paddle = Paddle()
    ball   = Ball()
    score  = 0
    lives  = LIVES_START
    font = pygame.font.SysFont("arial", 24)

    playing = True
    while playing:
        dt = clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        # update
        paddle.update()
        ball.update()

        # paddle collision with breakout deflection
        if ball.rect().colliderect(paddle.rect):
            offset = (ball.x - paddle.rect.centerx) / (PADDLE_WIDTH/2)
            angle = offset * (math.pi/3)
            speed = BALL_SPEED
            ball.vx = speed * math.sin(angle)
            ball.vy = -abs(speed * math.cos(angle))
            ball.y = PADDLE_Y - BALL_RADIUS
            sounds.bounce()

        # brick collisions
        hit_idx = ball.rect().collidelist([b.rect for b in bricks])
        if hit_idx != -1:
            del bricks[hit_idx]
            ball.vy *= -1
            score += 1
            sounds.brick()

        # life lost
        if ball.y - BALL_RADIUS > SCREEN_HEIGHT:
            lives -= 1
            sounds.lost_life()
            if lives == 0:
                return False, score  # lost
            ball.reset()

        # win check
        if not bricks:
            return True, score  # win

        # draw
        screen.fill(BLACK)
        draw_hud(screen, font, score, lives)
        for br in bricks: br.draw(screen)
        paddle.draw(screen)
        ball.draw(screen)
        pygame.display.flip()


def wait_choice():
    """Wait for Y/N, returns True to restart, False to quit"""
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_y: return True
                if ev.key in (pygame.K_n, pygame.K_ESCAPE, pygame.K_q): return False
        clock.tick(30)

# === Pygame Init ===
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Breakout – Press Y to Restart, N to Quit")
clock  = pygame.time.Clock()
pygame.mouse.set_visible(False)
sounds = AtariSoundManager()

# === Main restart loop ===
while True:
    won, final_score = run_once()
    msg = "YOU WIN!" if won else "GAME OVER"
    end_screen(screen, pygame.font.SysFont("arial", 28, bold=True), msg)
    if not wait_choice():
        break

pygame.quit()
sys.exit()
