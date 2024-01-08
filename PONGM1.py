import pygame
from pygame.locals import *
import random

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH = 800
HEIGHT = 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Define game parameters
FPS = 60
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Paddle parameters
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 60
PADDLE_SPEED = 5

# Ball parameters
BALL_RADIUS = 10
BALL_SPEED_X = 4
BALL_SPEED_Y = 4

# Create paddles
paddle1 = pygame.Rect(50, HEIGHT/2 - PADDLE_HEIGHT/2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT/2 - PADDLE_HEIGHT/2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Create ball
ball = pygame.Rect(WIDTH/2 - BALL_RADIUS/2, HEIGHT/2 - BALL_RADIUS/2, BALL_RADIUS, BALL_RADIUS)
ball_speed_x = BALL_SPEED_X
ball_speed_y = BALL_SPEED_Y

# Initialize score
score1 = 0
score2 = 0

# Game loop
running = True
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    # Move paddle1
    keys = pygame.key.get_pressed()
    if keys[K_w] and paddle1.y > 0:
        paddle1.y -= PADDLE_SPEED
    if keys[K_s] and paddle1.y < HEIGHT - PADDLE_HEIGHT:
        paddle1.y += PADDLE_SPEED

    # Move paddle2 (AI-controlled)
    if paddle2.y < ball.y:
        paddle2.y += PADDLE_SPEED
    if paddle2.y > ball.y:
        paddle2.y -= PADDLE_SPEED

    # Move ball
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Ball collision with paddles
    if ball.colliderect(paddle1) or ball.colliderect(paddle2):
        ball_speed_x *= -1

    # Ball collision with walls
    if ball.y < 0 or ball.y > HEIGHT - BALL_RADIUS:
        ball_speed_y *= -1

    # Ball out of bounds
    if ball.x < 0:
        score2 += 1
        ball_speed_x = BALL_SPEED_X
        ball_speed_y = BALL_SPEED_Y
        ball.x = WIDTH/2 - BALL_RADIUS/2
        ball.y = HEIGHT/2 - BALL_RADIUS/2
    if ball.x > WIDTH - BALL_RADIUS:
        score1 += 1
        ball_speed_x = -BALL_SPEED_X
        ball_speed_y = BALL_SPEED_Y
        ball.x = WIDTH/2 - BALL_RADIUS/2
        ball.y = HEIGHT/2 - BALL_RADIUS/2

    # Clear the screen
    win.fill(BLACK)

    # Draw paddles and ball
    pygame.draw.rect(win, WHITE, paddle1)
    pygame.draw.rect(win, WHITE, paddle2)
    pygame.draw.ellipse(win, WHITE, ball)

    # Draw scores
    score_text = font.render(str(score1) + " - " + str(score2), True, WHITE)
    win.blit(score_text, (WIDTH/2 - score_text.get_width()/2, 10))

    # Update the display
    pygame.display.update()

    # Limit the frame rate
    clock.tick(60)

# Quit the game
pygame.quit()
