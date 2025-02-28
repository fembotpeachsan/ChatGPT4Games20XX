import pygame
import sys
import random
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 600
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Breakout")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
red = (255, 0, 0)

# Paddle
paddle_width = 80
paddle_height = 10
paddle_speed = 7
paddle = pygame.Rect(screen_width // 2 - paddle_width // 2, screen_height - 30, paddle_width, paddle_height)

# Ball
ball_radius = 8
ball_speed = [4, -4]
ball = pygame.Rect(screen_width // 2, screen_height // 2, ball_radius * 2, ball_radius * 2)

# Bricks
brick_rows = 5
brick_cols = 8
brick_width = screen_width // brick_cols
brick_height = 20
bricks = []
for row in range(brick_rows):
    for col in range(brick_cols):
        brick = pygame.Rect(col * brick_width, row * brick_height, brick_width, brick_height)
        bricks.append(brick)

# Font
font = pygame.font.Font(None, 36)

# Game variables
lives = 3
score = 0

# Sound frequencies
paddle_hit_freq = 500  # Frequency for paddle hit sound
brick_hit_freq = 700   # Frequency for brick hit sound
wall_hit_freq = 300    # Frequency for wall hit sound

# Function to generate a sound (fixed for stereo mixer)
def generate_sound(frequency, duration=0.1, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    waveform = 0.5 * np.sin(2 * np.pi * frequency * t)
    waveform_integers = np.int16(waveform * 32767)
    # Convert to stereo by duplicating the mono channel
    stereo_waveform = np.column_stack((waveform_integers, waveform_integers))
    sound = pygame.sndarray.make_sound(stereo_waveform)
    return sound

# Generate sounds
paddle_hit_sound = generate_sound(paddle_hit_freq)
brick_hit_sound = generate_sound(brick_hit_freq)
wall_hit_sound = generate_sound(wall_hit_freq)

clock = pygame.time.Clock()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move paddle
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.left -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle.right < screen_width:
        paddle.right += paddle_speed

    # Move ball
    ball.x += ball_speed[0]
    ball.y += ball_speed[1]

    # Ball collision with walls
    if ball.left <= 0 or ball.right >= screen_width:
        ball_speed[0] = -ball_speed[0]
        wall_hit_sound.play()
    if ball.top <= 0:
        ball_speed[1] = -ball_speed[1]
        wall_hit_sound.play()
    if ball.bottom >= screen_height:
        lives -= 1
        ball.x = screen_width // 2
        ball.y = screen_height // 2
        ball_speed = [4 * random.choice((1, -1)), -4]

    # Ball collision with paddle
    if ball.colliderect(paddle) and ball_speed[1] > 0:
        ball_speed[1] = -ball_speed[1]
        paddle_hit_sound.play()

    # Ball collision with bricks
    hit_index = ball.collidelist(bricks)
    if hit_index != -1:
        hit_rect = bricks.pop(hit_index)
        score += 10
        brick_hit_sound.play()
        # Determine collision side
        if abs(ball.bottom - hit_rect.top) < 10 and ball_speed[1] > 0:
            ball_speed[1] = -ball_speed[1]
        elif abs(ball.top - hit_rect.bottom) < 10 and ball_speed[1] < 0:
            ball_speed[1] = -ball_speed[1]
        elif abs(ball.right - hit_rect.left) < 10 and ball_speed[0] > 0:
            ball_speed[0] = -ball_speed[0]
        elif abs(ball.left - hit_rect.right) < 10 and ball_speed[0] < 0:
            ball_speed[0] = -ball_speed[0]

    # Check for game over
    if lives <= 0:
        running = False

    # Drawing
    screen.fill(black)
    pygame.draw.rect(screen, blue, paddle)
    pygame.draw.ellipse(screen, white, ball)
    for brick in bricks:
        pygame.draw.rect(screen, red, brick)
    score_text = font.render(f"Score: {score}", True, white)
    lives_text = font.render(f"Lives: {lives}", True, white)
    screen.blit(score_text, (5, 5))
    screen.blit(lives_text, (screen_width - 100, 5))
    pygame.display.flip()

    # Frame rate
    clock.tick(60)

pygame.quit()
sys.exit()
