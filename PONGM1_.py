import pygame
from array import array
import random

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Screen setup - fixed size window
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Synthwave Pong")

# Colors
BLACK = (0, 0, 0)
NEON_CYAN = (0, 255, 255)
NEON_PINK = (255, 20, 147)
NEON_PURPLE = (199, 0, 255)
WHITE = (255, 255, 255)

# Generate beep sound function
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * ((i // (sample_rate // frequency)) % 2)) for i in range(samples)]
    sound = pygame.mixer.Sound(buffer=array('h', wave))
    sound.set_volume(0.1)
    return sound

# Load sounds
paddle_hit_sound = generate_beep_sound(440, 0.1)  # A4
wall_hit_sound = generate_beep_sound(523.25, 0.1)  # C5

# Game Constants
BALL_RADIUS = 15
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
PADDLE_SPEED = 6
BALL_SPEED_X = 5
BALL_SPEED_Y = 5

# Create game objects
ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_RADIUS, SCREEN_HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
left_paddle = pygame.Rect(10, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(SCREEN_WIDTH - 10 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

ball_dx = random.choice([-BALL_SPEED_X, BALL_SPEED_X])
ball_dy = random.choice([-BALL_SPEED_Y, BALL_SPEED_Y])

# Scoring variables
left_score = 0
right_score = 0
winning_score = 5

# Font for displaying score
font = pygame.font.Font(None, 74)

# Clock for controlling game speed
clock = pygame.time.Clock()

# Main game loop
running = True
left_paddle_speed = 0
right_paddle_speed = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                left_paddle_speed = -PADDLE_SPEED
            elif event.key == pygame.K_s:
                left_paddle_speed = PADDLE_SPEED
            elif event.key == pygame.K_UP:
                right_paddle_speed = -PADDLE_SPEED
            elif event.key == pygame.K_DOWN:
                right_paddle_speed = PADDLE_SPEED
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_s):
                left_paddle_speed = 0
            elif event.key in (pygame.K_UP, pygame.K_DOWN):
                right_paddle_speed = 0

    # Move paddles
    left_paddle.y += left_paddle_speed
    right_paddle.y += right_paddle_speed

    # Keep paddles on the screen
    left_paddle.y = max(0, min(SCREEN_HEIGHT - PADDLE_HEIGHT, left_paddle.y))
    right_paddle.y = max(0, min(SCREEN_HEIGHT - PADDLE_HEIGHT, right_paddle.y))

    # Move ball
    ball.x += ball_dx
    ball.y += ball_dy

    # Ball collision with top and bottom walls
    if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
        ball_dy = -ball_dy
        wall_hit_sound.play()

    # Ball collision with paddles
    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        ball_dx = -ball_dx
        paddle_hit_sound.play()

    # Ball out of bounds (reset to center and update score)
    if ball.left <= 0:
        right_score += 1
        ball.x = SCREEN_WIDTH // 2 - BALL_RADIUS
        ball.y = SCREEN_HEIGHT // 2 - BALL_RADIUS
        ball_dx = random.choice([-BALL_SPEED_X, BALL_SPEED_X])
        ball_dy = random.choice([-BALL_SPEED_Y, BALL_SPEED_Y])
    elif ball.right >= SCREEN_WIDTH:
        left_score += 1
        ball.x = SCREEN_WIDTH // 2 - BALL_RADIUS
        ball.y = SCREEN_HEIGHT // 2 - BALL_RADIUS
        ball_dx = random.choice([-BALL_SPEED_X, BALL_SPEED_X])
        ball_dy = random.choice([-BALL_SPEED_Y, BALL_SPEED_Y])

    # Check for game over
    if left_score == winning_score or right_score == winning_score:
        running = False
        winner = "Left Player" if left_score == winning_score else "Right Player"
        print(f"{winner} wins!")

    # Clear screen
    screen.fill(BLACK)

    # Draw paddles, ball, and score
    pygame.draw.rect(screen, NEON_CYAN, left_paddle)
    pygame.draw.rect(screen, NEON_PINK, right_paddle)
    pygame.draw.ellipse(screen, NEON_PURPLE, ball)
    pygame.draw.aaline(screen, NEON_CYAN, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))

    left_text = font.render(str(left_score), True, WHITE)
    right_text = font.render(str(right_score), True, WHITE)
    screen.blit(left_text, (SCREEN_WIDTH // 4, 20))
    screen.blit(right_text, (SCREEN_WIDTH * 3 // 4, 20))

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
