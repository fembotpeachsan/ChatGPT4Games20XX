# The user has requested to create a Pong game using Pygame with no sound and no media assets.
# We'll create a simple version of Pong with basic gameplay mechanics.

import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pong")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddle properties
paddle_width, paddle_height = 15, 60
paddle_speed = 10

# Ball properties
ball_size = 15
ball_speed_x, ball_speed_y = 7 * random.choice((1, -1)), 7 * random.choice((1, -1))

# Define the paddles and ball
player_paddle = pygame.Rect(width - paddle_width - 20, height // 2 - paddle_height // 2, paddle_width, paddle_height)
opponent_paddle = pygame.Rect(20, height // 2 - paddle_height // 2, paddle_width, paddle_height)
ball = pygame.Rect(width // 2 - ball_size // 2, height // 2 - ball_size // 2, ball_size, ball_size)

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the paddles
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and player_paddle.top > 0:
        player_paddle.y -= paddle_speed
    if keys[pygame.K_DOWN] and player_paddle.bottom < height:
        player_paddle.y += paddle_speed
    
    # Let the opponent paddle follow the ball
    if opponent_paddle.top < ball.y:
        opponent_paddle.y += paddle_speed
    if opponent_paddle.bottom > ball.y:
        opponent_paddle.y -= paddle_speed

    # Move the ball
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Ball collision (top or bottom)
    if ball.top <= 0 or ball.bottom >= height:
        ball_speed_y *= -1
    
    # Ball collision (paddles)
    if ball.colliderect(player_paddle) or ball.colliderect(opponent_paddle):
        ball_speed_x *= -1
    
    # Ball out of bounds
    if ball.left <= 0 or ball.right >= width:
        ball = pygame.Rect(width // 2 - ball_size // 2, height // 2 - ball_size // 2, ball_size, ball_size)
        ball_speed_x *= random.choice((1, -1))
        ball_speed_y *= random.choice((1, -1))

    # Fill the background
    screen.fill(BLACK)

    # Draw the paddles and the ball
    pygame.draw.rect(screen, WHITE, player_paddle)
    pygame.draw.rect(screen, WHITE, opponent_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)

    # Updating the window
    pygame.display.flip()
    clock.tick(60) # 60 frames per second

# Quit Pygame
pygame.quit()
