import pygame
import sys
import random

# Initializing Pygame
pygame.init()

# Setting up some constants
WIDTH = 800
HEIGHT = 600
BALL_SPEED = [2, 2]
PADDLE_SPEED = 5
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60 # Frames per second

# Creating the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Creating the paddles and ball
paddle1 = pygame.Rect(50, HEIGHT//2-50, 10, 100)
paddle2 = pygame.Rect(WIDTH-60, HEIGHT//2-50, 10, 100)
ball = pygame.Rect(WIDTH//2 - 7.5, HEIGHT//2 - 7.5, 15, 15)

# Initializing the score and random starting direction for the ball
score1 = score2 = 0
BALL_SPEED[0] *= random.choice([-1, 1])
BALL_SPEED[1] *= random.choice([-1, 1])

# Setting up the clock for controlling the frame rate
clock = pygame.time.Clock()

while True:
    # Handling events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    # Moving the paddles when keys are pressed
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and paddle1.top > 0:
        paddle1.move_ip(0, -PADDLE_SPEED)
    if keys[pygame.K_s] and paddle1.bottom < HEIGHT:
        paddle1.move_ip(0, PADDLE_SPEED)
    if keys[pygame.K_UP] and paddle2.top > 0:
        paddle2.move_ip(0, -PADDLE_SPEED)
    if keys[pygame.K_DOWN] and paddle2.bottom < HEIGHT:
        paddle2.move_ip(0, PADDLE_SPEED)

    # Moving the ball
    ball.move_ip(BALL_SPEED[0], BALL_SPEED[1])

    # Collisions with the paddles
    if ball.colliderect(paddle1) or ball.colliderect(paddle2):
        BALL_SPEED[0] *= -1

    # Collisions with the walls
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        BALL_SPEED[1] *= -1

    # Scoring and resetting the ball's position
    if ball.left <= 0:
        score2 += 1
        print("Player 1: ", score1, " Player 2: ", score2)
        ball = pygame.Rect(WIDTH//2 - 7.5, HEIGHT//2 - 7.5, 15, 15)
        BALL_SPEED[0] *= random.choice([-1, 1])
    elif ball.right >= WIDTH:
        score1 += 1
        print("Player 1: ", score1, " Player 2: ", score2)
        ball = pygame.Rect(WIDTH//2 - 7.5, HEIGHT//2 - 7.5, 15, 15)
        BALL_SPEED[0] *= random.choice([-1, 1])

    # Ending the game when a player reaches a score of 10
    if score1 >= 10 or score2 >= 10:
        print("Player 1: ", score1)
        print("Player 2: ", score2)
        sys.exit()

    # Rendering the screen
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, paddle1)
    pygame.draw.rect(screen, WHITE, paddle2)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.display.update()

    # Controlling the frame rate
    clock.tick(FPS)
