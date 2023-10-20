import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BALL_RADIUS = 10
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up the display
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Pong')

# Initialize variables
paddle1_pos = [0, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2]
paddle2_pos = [SCREEN_WIDTH - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2]
ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
ball_vel = [2, 2]
paddle1_vel = 0
paddle2_vel = 0
score1 = 0
score2 = 0

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                paddle2_vel = -4
            elif event.key == pygame.K_DOWN:
                paddle2_vel = 4
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                paddle2_vel = 0

    # AI for the left paddle
    if ball_pos[1] > paddle1_pos[1] + PADDLE_HEIGHT // 2:
        paddle1_vel = 4
    elif ball_pos[1] < paddle1_pos[1] + PADDLE_HEIGHT // 2:
        paddle1_vel = -4
    else:
        paddle1_vel = 0

    # Update paddle and ball positions
    paddle1_pos[1] += paddle1_vel
    paddle2_pos[1] += paddle2_vel
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Ball collision check on top and bottom walls
    if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= SCREEN_HEIGHT - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]

    # Ball goes off to the left or right to score points
    if ball_pos[0] < 0:
        score2 += 1
        ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
    elif ball_pos[0] > SCREEN_WIDTH:
        score1 += 1
        ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]

    # Paddle collision check
    if paddle1_pos[1] <= 0:
        paddle1_pos[1] = 0
    if paddle1_pos[1] >= SCREEN_HEIGHT - PADDLE_HEIGHT:
        paddle1_pos[1] = SCREEN_HEIGHT - PADDLE_HEIGHT

    if paddle2_pos[1] <= 0:
        paddle2_pos[1] = 0
    if paddle2_pos[1] >= SCREEN_HEIGHT - PADDLE_HEIGHT:
        paddle2_pos[1] = SCREEN_HEIGHT - PADDLE_HEIGHT

    # Ball hits paddles
    if BALL_RADIUS + PADDLE_WIDTH > ball_pos[0] > PADDLE_WIDTH and paddle1_pos[1] < ball_pos[1] < paddle1_pos[1] + PADDLE_HEIGHT:
        ball_vel[0] = -ball_vel[0]
    elif SCREEN_WIDTH - PADDLE_WIDTH - BALL_RADIUS < ball_pos[0] < SCREEN_WIDTH - PADDLE_WIDTH and paddle2_pos[1] < ball_pos[1] < paddle2_pos[1] + PADDLE_HEIGHT:
        ball_vel[0] = -ball_vel[0]

    # Draw everything
    window.fill(BLACK)
    pygame.draw.circle(window, WHITE, ball_pos, BALL_RADIUS)
    pygame.draw.rect(window, WHITE, pygame.Rect(paddle1_pos[0], paddle1_pos[1], PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(window, WHITE, pygame.Rect(paddle2_pos[0], paddle2_pos[1], PADDLE_WIDTH, PADDLE_HEIGHT))

    # Draw scores
    font = pygame.font.Font(None, 36)
    score_display = font.render(f"{score1} - {score2}", True, WHITE)
    window.blit(score_display, (SCREEN_WIDTH // 2 - score_display.get_width() // 2, 10))

    pygame.display.update()
    pygame.time.delay(16)
