#!/usr/bin/env python3
"""
test.py — Pong with Pygame, no media assets, pure vibes, Famicom-style sound.
Features:
- Left paddle controlled by mouse
- Right paddle AI-driven
- First to 5 points triggers GAME OVER screen
- 'Y' to restart, 'N' to quit
"""
import sys
import pygame
import numpy as np

# Game settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddle settings
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
PADDLE_SPEED = 5

# Ball settings
BALL_SIZE = 16
BALL_SPEED_X = 4
BALL_SPEED_Y = 4

# Sound settings
SAMPLE_RATE = 44100


def generate_tone(frequency, duration, volume=0.5):
    """Generate a square wave tone, auto-adjusting for mixer channels."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    wave = np.sign(np.sin(2 * np.pi * frequency * t))
    audio = (volume * wave * 32767).astype(np.int16)
    init_info = pygame.mixer.get_init()
    channels = init_info[2] if init_info else 1
    if channels > 1:
        audio = np.repeat(audio[:, np.newaxis], channels, axis=1)
    return pygame.sndarray.make_sound(audio)


def game_loop(screen, clock, font):
    # Initialize positions
    left_paddle = pygame.Rect(10, (WINDOW_HEIGHT - PADDLE_HEIGHT)//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(WINDOW_WIDTH - 10 - PADDLE_WIDTH, (WINDOW_HEIGHT - PADDLE_HEIGHT)//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect((WINDOW_WIDTH - BALL_SIZE)//2, (WINDOW_HEIGHT - BALL_SIZE)//2, BALL_SIZE, BALL_SIZE)
    ball_speed_x = BALL_SPEED_X * np.random.choice([-1, 1])
    ball_speed_y = BALL_SPEED_Y * np.random.choice([-1, 1])

    sound_paddle = generate_tone(440, 0.1, volume=0.3)
    sound_wall = generate_tone(880, 0.1, volume=0.3)
    sound_score = generate_tone(220, 0.2, volume=0.5)

    score_left = 0
    score_right = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # exit entire game
        # Left paddle follows mouse
        _, mouse_y = pygame.mouse.get_pos()
        left_paddle.centery = np.clip(mouse_y, PADDLE_HEIGHT//2, WINDOW_HEIGHT - PADDLE_HEIGHT//2)
        # Right paddle AI: follow ball
        if right_paddle.centery < ball.centery:
            right_paddle.y += PADDLE_SPEED
        elif right_paddle.centery > ball.centery:
            right_paddle.y -= PADDLE_SPEED
        # Clamp right paddle
        right_paddle.y = np.clip(right_paddle.y, 0, WINDOW_HEIGHT - PADDLE_HEIGHT)

        # Move ball
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Collisions
        if ball.top <= 0 or ball.bottom >= WINDOW_HEIGHT:
            ball_speed_y *= -1
            sound_wall.play()
        if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
            ball_speed_x *= -1
            sound_paddle.play()

        # Scoring
        if ball.left <= 0:
            score_right += 1
            sound_score.play()
            ball.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
            ball_speed_x *= -1
        if ball.right >= WINDOW_WIDTH:
            score_left += 1
            sound_score.play()
            ball.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
            ball_speed_x *= -1

        # Check for game over
        if score_left >= 5 or score_right >= 5:
            return (score_left, score_right)

        # Draw
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, left_paddle)
        pygame.draw.rect(screen, WHITE, right_paddle)
        pygame.draw.ellipse(screen, WHITE, ball)
        pygame.draw.aaline(screen, WHITE, (WINDOW_WIDTH//2, 0), (WINDOW_WIDTH//2, WINDOW_HEIGHT))
        # Scores
        text_l = font.render(str(score_left), True, WHITE)
        text_r = font.render(str(score_right), True, WHITE)
        screen.blit(text_l, (WINDOW_WIDTH//4 - text_l.get_width()//2, 20))
        screen.blit(text_r, (WINDOW_WIDTH * 3//4 - text_r.get_width()//2, 20))

        pygame.display.flip()
        clock.tick(FPS)
    return False


def show_game_over(screen, clock, font, score_left, score_right):
    msg = f"GAME OVER! {score_left}:{score_right}. Y=Restart N=Quit"
    text = font.render(msg, True, WHITE)
    rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                if event.key == pygame.K_n:
                    return False
        screen.fill(BLACK)
        screen.blit(text, rect)
        pygame.display.flip()
        clock.tick(15)


def main():
    pygame.init()
    pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pure Vibes Pong")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 48)

    while True:
        result = game_loop(screen, clock, font)
        if not result:
            break
        score_l, score_r = result
        if not show_game_over(screen, clock, font, score_l, score_r):
            break
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
