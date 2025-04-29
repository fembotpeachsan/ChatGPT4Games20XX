import pygame
import sys

pygame.init()

# Screen setup
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong - RIP Version")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddle setup
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
paddle_speed = 5

player1 = pygame.Rect(10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
player2 = pygame.Rect(WIDTH - 20, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Ball setup
ball = pygame.Rect(WIDTH//2 - 7, HEIGHT//2 - 7, 14, 14)
ball_speed_x = 4
ball_speed_y = 4

# Clock for 60 FPS
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: player1.y -= paddle_speed
    if keys[pygame.K_s]: player1.y += paddle_speed
    if keys[pygame.K_UP]: player2.y -= paddle_speed
    if keys[pygame.K_DOWN]: player2.y += paddle_speed

    # Ball movement
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Ball collisions
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1
    if ball.colliderect(player1) or ball.colliderect(player2):
        ball_speed_x *= -1

    # Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, player1)
    pygame.draw.rect(screen, WHITE, player2)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

    pygame.display.flip()
    clock.tick(60)
