# Since the user has requested a simple game simulation in Pygame without using any media files,
# let's create a Python script that simulates a basic "brick breaker" game using only Pygame's drawing functions.

import pygame
import random

# Initialize Pygame
pygame.init()

# Define constants for the game
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 20
BALL_RADIUS = 10
BRICK_WIDTH, BRICK_HEIGHT = 50, 30
NUM_BRICKS_PER_ROW = SCREEN_WIDTH // BRICK_WIDTH
NUM_ROWS_OF_BRICKS = 5
WHITE, RED, GREEN, BLUE, BLACK = (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Brick Breaker')

# Define the paddle
paddle = pygame.Rect((SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, SCREEN_HEIGHT - 40), (PADDLE_WIDTH, PADDLE_HEIGHT))

# Define the ball
ball = pygame.Rect((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), (BALL_RADIUS * 2, BALL_RADIUS * 2))
ball_velocity = [random.choice([-1, 1]) * 4, -4]

# Define the bricks
bricks = [pygame.Rect((x * BRICK_WIDTH, y * BRICK_HEIGHT), (BRICK_WIDTH, BRICK_HEIGHT))
          for y in range(NUM_ROWS_OF_BRICKS) for x in range(NUM_BRICKS_PER_ROW)]

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move paddle
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.move_ip(-6, 0)
    if keys[pygame.K_RIGHT] and paddle.right < SCREEN_WIDTH:
        paddle.move_ip(6, 0)

    # Move ball
    ball.move_ip(ball_velocity)
    # Bounce off walls
    if ball.left <= 0 or ball.right >= SCREEN_WIDTH:
        ball_velocity[0] = -ball_velocity[0]
    if ball.top <= 0:
        ball_velocity[1] = -ball_velocity[1]
    # Bounce off paddle
    if ball.colliderect(paddle):
        ball_velocity[1] = -ball_velocity[1]

    # Check for brick collisions
    for brick in bricks[:]:
        if ball.colliderect(brick):
            ball_velocity[1] = -ball_velocity[1]
            bricks.remove(brick)
            break

    # Check for game over
    if ball.bottom >= SCREEN_HEIGHT:
        running = False

    # Draw everything
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, paddle)
    pygame.draw.ellipse(screen, GREEN, ball)
    for brick in bricks:
        pygame.draw.rect(screen, RED, brick)

    # Update the display
    pygame.display.flip()
    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
