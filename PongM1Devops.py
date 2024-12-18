import pygame
import sys
import random
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the game window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pong")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddle properties
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
PADDLE_SPEED = 5

# Ball properties
BALL_SIZE = 10
BALL_SPEED_X = 3
BALL_SPEED_Y = 3

# Create paddles
left_paddle = pygame.Rect(50, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WINDOW_WIDTH - 50 - PADDLE_WIDTH, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Create ball
ball = pygame.Rect(WINDOW_WIDTH // 2 - BALL_SIZE // 2, WINDOW_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
ball_speed_x = BALL_SPEED_X * random.choice((-1, 1))
ball_speed_y = BALL_SPEED_Y * random.choice((-1, 1))

# Sound properties
sample_rate = 44100
frequency_beep = 440  # A4 note
frequency_boop = 880  # A5 note
duration = 0.1  # 100 ms

def generate_sound(frequency, duration, sample_rate=44100):
    """
    Generate a sound wave for a given frequency and duration.
    Returns a Pygame Sound object.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(frequency * t * 2 * np.pi)
    # Ensure the wave is in the range [-1, 1]
    wave = wave * 0.5
    # Convert to 16-bit PCM
    sound_array = np.int16(wave * 32767)
    # Create a stereo sound by duplicating the mono wave
    stereo_sound = np.column_stack((sound_array, sound_array))
    return pygame.sndarray.make_sound(stereo_sound)

# Generate beep and boop sounds
beep_sound = generate_sound(frequency_beep, duration)
boop_sound = generate_sound(frequency_boop, duration)

# Game loop
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Move paddles based on user input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle.bottom < WINDOW_HEIGHT:
        left_paddle.y += PADDLE_SPEED
    if keys[pygame.K_UP] and right_paddle.top > 0:
        right_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and right_paddle.bottom < WINDOW_HEIGHT:
        right_paddle.y += PADDLE_SPEED

    # Move the ball
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Check for collision with paddles
    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        ball_speed_x = -ball_speed_x
        beep_sound.play()

    # Check for collision with top/bottom walls
    if ball.top <= 0 or ball.bottom >= WINDOW_HEIGHT:
        ball_speed_y = -ball_speed_y
        boop_sound.play()

    # Check if ball goes out of bounds (score)
    if ball.left <= 0 or ball.right >= WINDOW_WIDTH:
        ball.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        ball_speed_x = BALL_SPEED_X * random.choice((-1, 1))
        ball_speed_y = BALL_SPEED_Y * random.choice((-1, 1))

    # Clear the window
    window.fill(BLACK)

    # Draw the paddles and ball
    pygame.draw.rect(window, WHITE, left_paddle)
    pygame.draw.rect(window, WHITE, right_paddle)
    pygame.draw.ellipse(window, WHITE, ball)  # Use ellipse for a circular ball

    # Update the display
    pygame.display.flip()

    # Set the frame rate
    clock.tick(60)  # 60 frames per second
