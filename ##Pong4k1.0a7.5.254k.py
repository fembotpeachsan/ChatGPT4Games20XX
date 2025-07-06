#!/usr/bin/env python3
"""
Retro Atari‑style PONG — single‑file Pygame edition
Features:
  • Main menu with 1‑Player / 2‑Player / How‑To / Exit
  • Simple AI for right paddle in 1‑Player
  • First to 11 wins
  • Pure code beeps via winsound (Windows) or silent fallback
  • No external assets, just vibes ✨
"""
import pygame
import random
import sys
from enum import Enum

# ────────────────────────────────────────────────────────────────────────────
# Optional beeper (Windows) — otherwise silent fallback
# ────────────────────────────────────────────────────────────────────────────
try:
    import winsound

    def beep(freq: int = 440, dur_ms: int = 100):
        winsound.Beep(int(freq), int(dur_ms))
except Exception:  # pragma: no cover – non‑Windows or winsound missing

    def beep(freq: int = 440, dur_ms: int = 100):
        pass  # noop

# ────────────────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 640, 480
PADDLE_W, PADDLE_H = 8, 80
PADDLE_SPEED = 6
BALL_SIZE = 8
BALL_SPEED = 5
WIN_SCORE = 11
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ────────────────────────────────────────────────────────────────────────────
# Game State Enum
# ────────────────────────────────────────────────────────────────────────────

class GameState(Enum):
    MENU = 0
    HOW = 1
    PLAY = 2
    OVER = 3


# ────────────────────────────────────────────────────────────────────────────
# Helper functions
# ────────────────────────────────────────────────────────────────────────────

def reset_ball(dir_x: int):
    """Centre the ball and launch it left (‑1) or right (+1) with a random slope."""
    ball.x = WIDTH // 2 - BALL_SIZE // 2
    ball.y = HEIGHT // 2 - BALL_SIZE // 2
    angle = random.uniform(-0.25, 0.25)
    ball_vel.x = dir_x * BALL_SPEED
    ball_vel.y = BALL_SPEED * angle


def reset_game():
    left_paddle.centery = right_paddle.centery = HEIGHT // 2
    scores[0] = scores[1] = 0
    reset_ball(random.choice((-1, 1)))


def ai_move():
    """Very simple, slightly imperfect AI for right paddle."""
    center = right_paddle.centery
    target = ball.centery
    if abs(center - target) > 10:
        if center < target:
            right_paddle.y += int(PADDLE_SPEED * 0.85)
        else:
            right_paddle.y -= int(PADDLE_SPEED * 0.85)
    right_paddle.clamp_ip(screen_rect)


def draw_text(text: str, y: int, size: int = 18, center: bool = True):
    font = pygame.font.Font(font_path, size)
    surf = font.render(text, True, WHITE)
    rect = surf.get_rect()
    if center:
        rect.centerx = WIDTH // 2
    else:
        rect.x = 0
    rect.y = y
    screen.blit(surf, rect)


# ────────────────────────────────────────────────────────────────────────────
# Init Pygame
# ────────────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()  # (even if silent, keeps API consistent)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PONG")
clock = pygame.time.Clock()

# Minimal fallback font (monospace‑ish)
font_path = pygame.font.match_font("dejavusansmono, consolas, courier, monospace")

# Rects for paddles and ball
left_paddle = pygame.Rect(0, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
right_paddle = pygame.Rect(WIDTH - PADDLE_W, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_SIZE, BALL_SIZE)
ball_vel = pygame.Vector2(BALL_SPEED, 0)

screen_rect = screen.get_rect()

# Game vars
state = GameState.MENU
menu_items = ["1 PLAYER", "2 PLAYER", "HOW TO PLAY", "EXIT"]
menu_idx = 0
is_1p = True
scores = [0, 0]  # left, right

reset_game()

# ────────────────────────────────────────────────────────────────────────────
# Main loop
# ────────────────────────────────────────────────────────────────────────────
while True:
    # ── Event handling ────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            key = event.key
            if state == GameState.MENU:
                if key in (pygame.K_UP, pygame.K_w):
                    menu_idx = (menu_idx - 1) % len(menu_items)
                    beep(300, 80)
                elif key in (pygame.K_DOWN, pygame.K_s):
                    menu_idx = (menu_idx + 1) % len(menu_items)
                    beep(300, 80)
                elif key == pygame.K_RETURN:
                    beep(500, 120)
                    if menu_idx == 0:
                        is_1p = True
                        reset_game()
                        state = GameState.PLAY
                    elif menu_idx == 1:
                        is_1p = False
                        reset_game()
                        state = GameState.PLAY
                    elif menu_idx == 2:
                        state = GameState.HOW
                    elif menu_idx == 3:
                        pygame.quit()
                        sys.exit()
            elif state == GameState.HOW:
                if key == pygame.K_RETURN:
                    state = GameState.MENU
            elif state == GameState.OVER:
                if key == pygame.K_RETURN:
                    state = GameState.MENU
            elif state == GameState.PLAY:
                if key == pygame.K_ESCAPE:
                    state = GameState.MENU
    # ── Update ────────────────────────────────────────────────
    screen.fill(BLACK)
    if state == GameState.MENU:
        draw_text("PONG", 120, 32)
        for i, item in enumerate(menu_items):
            prefix = "> " if i == menu_idx else "  "
            draw_text(prefix + item, 200 + i * 40)
    elif state == GameState.HOW:
        draw_text("HOW TO PLAY", 100, 24)
        draw_text("PLAYER 1: W / S", 180, 18)
        draw_text("PLAYER 2: UP / DOWN", 220, 18)
        draw_text("FIRST TO 11 WINS", 260, 18)
        draw_text("ENTER = BACK", 340, 16)
    elif state == GameState.PLAY:
        # Player input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            left_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_s]:
            left_paddle.y += PADDLE_SPEED
        left_paddle.clamp_ip(screen_rect)

        if is_1p:
            ai_move()
        else:
            if keys[pygame.K_UP]:
                right_paddle.y -= PADDLE_SPEED
            if keys[pygame.K_DOWN]:
                right_paddle.y += PADDLE_SPEED
            right_paddle.clamp_ip(screen_rect)

        # Move ball
        ball.x += int(ball_vel.x)
        ball.y += int(ball_vel.y)

        # Wall collision
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_vel.y *= -1
            beep(800, 60)

        # Paddle collision
        if ball.colliderect(left_paddle):
            ball.left = left_paddle.right  # avoid sticking
            ball_vel.x *= -1
            # tweak vert speed based on hit position
            offset = ((ball.centery - left_paddle.centery) / (PADDLE_H / 2))
            ball_vel.y = BALL_SPEED * offset
            beep(600, 60)
        elif ball.colliderect(right_paddle):
            ball.right = right_paddle.left
            ball_vel.x *= -1
            offset = ((ball.centery - right_paddle.centery) / (PADDLE_H / 2))
            ball_vel.y = BALL_SPEED * offset
            beep(600, 60)

        # Scoring
        if ball.right < 0:
            scores[1] += 1
            beep(400, 150)
            if scores[1] >= WIN_SCORE:
                state = GameState.OVER
            else:
                reset_ball(1)
        elif ball.left > WIDTH:
            scores[0] += 1
            beep(400, 150)
            if scores[0] >= WIN_SCORE:
                state = GameState.OVER
            else:
                reset_ball(-1)

        # Draw net
        for i in range(0, HEIGHT, 20):
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 2, i, 4, 10))

        # Draw paddles and ball
        pygame.draw.rect(screen, WHITE, left_paddle)
        pygame.draw.rect(screen, WHITE, right_paddle)
        pygame.draw.rect(screen, WHITE, ball)

        # Draw scores
        draw_text(str(scores[0]), 30, 24)
        draw_text(str(scores[1]), 30, 24)
    elif state == GameState.OVER:
        winner = "PLAYER 1" if scores[0] > scores[1] else "PLAYER 2"
        draw_text(f"{winner} WINS!", 200, 28)
        draw_text("PRESS ENTER", 260, 18)

    pygame.display.flip()
    clock.tick(FPS)
