#!/usr/bin/env python3
"""
O3 PRO – Atari‑Style Pong
Author: OpenAI o3

• 640 × 480 classic window
• Left paddle:  W/S  (A/D = tiny left/right nudge)
• Right paddle: ↑/↓
• First to 5 wins – big GAME OVER banner
• Press Y to restart, N to quit
• Pure code‑drawn retro visuals, no external assets
• Optional bounce beep (falls back gracefully if mixer unavailable)
All control & restart logic is explicit and auditable.
"""

import random
import sys

import pygame

# ── Runtime constants ────────────────────────────────────────────────────────
WIDTH, HEIGHT     = 640, 480
FPS               = 60
PADDLE_W, PADDLE_H = 10, 70
BALL_SZ           = 10
SCORE_TO_WIN      = 5
WHITE, BLACK      = (250, 250, 250), (0, 0, 0)
FONT_NAME         = pygame.font.get_default_font()

# ── Utility helpers ──────────────────────────────────────────────────────────
def center_text(surf: pygame.Surface, msg: str, size: int, y_offset: int = 0):
    font  = pygame.font.Font(FONT_NAME, size)
    rend  = font.render(msg, True, WHITE)
    rect  = rend.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    surf.blit(rend, rect)


def reset_ball(rect: pygame.Rect, vel: list[int]):
    rect.center = (WIDTH // 2, HEIGHT // 2)
    vel[0]      = random.choice([-4, 4])
    vel[1]      = random.choice([-3, -2, -1, 1, 2, 3])


# ── Main game loop ───────────────────────────────────────────────────────────
def main() -> None:
    # ── Init Pygame core & mixer (sound optional) ────────────────────────────
    pygame.init()
    try:
        pygame.mixer.init()
        beep = pygame.mixer.Sound(buffer=b'\x7F' * 2048)  # tiny click
    except pygame.error:
        beep = None  # Sound unavailable (e.g., headless or ALSA issue)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("O3 PRO – Atari Pong")
    clock  = pygame.time.Clock()

    # ── Entities ─────────────────────────────────────────────────────────────
    left  = pygame.Rect(30,            HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
    right = pygame.Rect(WIDTH - 40,    HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
    ball  = pygame.Rect(0, 0, BALL_SZ, BALL_SZ)
    ball_vel = [0, 0]
    reset_ball(ball, ball_vel)

    score = [0, 0]      # [left, right]
    game_over = False   # flag

    # ── Game loop ────────────────────────────────────────────────────────────
    while True:
        clock.tick(FPS)

        # ── Event handling ───────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:      # restart
                    score     = [0, 0]
                    game_over = False
                    left.topleft  = (30, HEIGHT // 2 - PADDLE_H // 2)
                    right.topright = (WIDTH - 30 - PADDLE_W, HEIGHT // 2 - PADDLE_H // 2)
                    reset_ball(ball, ball_vel)
                elif event.key == pygame.K_n:    # immediate graceful exit
                    pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()

        # ── Logic update (skip when frozen on Game Over) ─────────────────────
        if not game_over:
            # Left paddle (W/S vertical, A/D horizontal nudge)
            if keys[pygame.K_w] and left.top > 0:
                left.y -= 5
            if keys[pygame.K_s] and left.bottom < HEIGHT:
                left.y += 5
            if keys[pygame.K_a] and left.left > 0:
                left.x -= 3
            if keys[pygame.K_d] and left.right < WIDTH // 2 - 20:
                left.x += 3

            # Right paddle (arrow keys)
            if keys[pygame.K_UP] and right.top > 0:
                right.y -= 5
            if keys[pygame.K_DOWN] and right.bottom < HEIGHT:
                right.y += 5

            # Move ball
            ball.x += ball_vel[0]
            ball.y += ball_vel[1]

            # Collision: walls
            if ball.top <= 0 or ball.bottom >= HEIGHT:
                ball_vel[1] *= -1
                if beep: beep.play()

            # Collision: paddles
            if ball.colliderect(left) and ball_vel[0] < 0:
                ball.left  = left.right
                ball_vel[0] *= -1
                if beep: beep.play()
            if ball.colliderect(right) and ball_vel[0] > 0:
                ball.right = right.left
                ball_vel[0] *= -1
                if beep: beep.play()

            # Scoring
            if ball.left <= 0:
                score[1] += 1
                if beep: beep.play()
                reset_ball(ball, ball_vel)
            if ball.right >= WIDTH:
                score[0] += 1
                if beep: beep.play()
                reset_ball(ball, ball_vel)

            # Victory?
            if score[0] >= SCORE_TO_WIN or score[1] >= SCORE_TO_WIN:
                game_over = True

        # ── Drawing ─────────────────────────────────────────────────────────
        screen.fill(BLACK)

        # Center net (dashed)
        for y in range(0, HEIGHT, 20):
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 2, y, 4, 10))

        pygame.draw.rect(screen, WHITE, left)
        pygame.draw.rect(screen, WHITE, right)
        pygame.draw.rect(screen, WHITE, ball)

        # Scoreboard
        font = pygame.font.Font(FONT_NAME, 36)
        score_surf = font.render(f"{score[0]}   {score[1]}", True, WHITE)
        screen.blit(score_surf, score_surf.get_rect(center=(WIDTH // 2, 30)))

        # Game‑over banner
        if game_over:
            champ = "LEFT" if score[0] > score[1] else "RIGHT"
            center_text(screen, f"{champ} PLAYER WINS!", 48, -40)
            center_text(screen, "Press Y to play again", 28, 15)
            center_text(screen, "Press N to quit",       28, 55)

        pygame.display.flip()


# ── Entrypoint ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
