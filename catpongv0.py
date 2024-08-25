# Importing necessary modules
import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH = 600
HEIGHT = 400
BALL_RADIUS = 20
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 80
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up the ball and paddles
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_RADIUS, BALL_RADIUS)
paddle1 = pygame.Rect(0, HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = pygame.Rect(WIDTH - PADDLE_WIDTH, HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Set up the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the ball speed and direction
ball_speed = [2, 2]

# Set up the paddle speed
paddle_speed = 2

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Update the game state
    ball.move_ip(ball_speed)
    if ball.left < 0 or ball.right > WIDTH:
        ball_speed[0] = -ball_speed[0]
    if ball.top < 0 or ball.bottom > HEIGHT:
        ball_speed[1] = -ball_speed[1]

    # Move the paddles
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        paddle1.move_ip(0, -paddle_speed)
    if keys[pygame.K_s]:
        paddle1.move_ip(0, paddle_speed)
    if keys[pygame.K_UP]:
        paddle2.move_ip(0, -paddle_speed)
    if keys[pygame.K_DOWN]:
        paddle2.move_ip(0, paddle_speed)

    # Keep the paddles inside the window
    if paddle1.top < 0:
        paddle1.top = 0
    if paddle1.bottom > HEIGHT:
        paddle1.bottom = HEIGHT
    if paddle2.top < 0:
        paddle2.top = 0
    if paddle2.bottom > HEIGHT:
        paddle2.bottom = HEIGHT

    # Draw everything
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, paddle1)
    pygame.draw.rect(screen, WHITE, paddle2)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0),(WIDTH // 2, HEIGHT))

    # Flip the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(FPS)
