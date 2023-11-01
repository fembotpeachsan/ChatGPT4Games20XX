# Let's optimize and clean up the provided Pygame code for a Pong-like game.

import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 400
BALL_RADIUS = 5
PADDLE_HEIGHT = 60
PADDLE_WIDTH = 10
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FPS = 30

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pong Game')

# Initialize clock
clock = pygame.time.Clock()

# Initialize paddles and ball
paddle_left = pygame.Rect(0, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle_right = pygame.Rect(WIDTH - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_RADIUS, BALL_RADIUS)
ball_velocity = [5, 5]

def reset_ball():
    ball.x = WIDTH // 2
    ball.y = HEIGHT // 2

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_s, pygame.K_UP, pygame.K_DOWN):
                shift = 10 if event.key in (pygame.K_s, pygame.K_DOWN) else -10
                target_paddle = paddle_left if event.key in (pygame.K_w, pygame.K_s) else paddle_right
                target_paddle.y += shift

    # Update ball position
    ball.x += ball_velocity[0]
    ball.y += ball_velocity[1]

    # Ball collision with top and bottom
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_velocity[1] *= -1

    # Ball collision with paddles
    if ball.colliderect(paddle_left) or ball.colliderect(paddle_right):
        ball_velocity[0] *= -1

    # Scoring logic
    if ball.left <= 0:
        print("Player 2 scores!")
        reset_ball()
    elif ball.right >= WIDTH:
        print("Player 1 scores!")
        reset_ball()

    # Draw everything
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, paddle_left)
    pygame.draw.rect(screen, WHITE, paddle_right)
    pygame.draw.ellipse(screen, WHITE, ball)

    pygame.display.flip()
    clock.tick(FPS)
