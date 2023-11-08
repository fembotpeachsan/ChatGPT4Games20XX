import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants for the game
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
PADDLE_WIDTH, PADDLE_HEIGHT = 60, 15
BALL_SIZE = 10
BRICK_WIDTH, BRICK_HEIGHT = 50, 30
PADDLE_Y_POSITION = SCREEN_HEIGHT - 40
BALL_SPEED_X, BALL_SPEED_Y = 5, -5
FPS = 60
BRICK_COLS = SCREEN_WIDTH // BRICK_WIDTH
BRICK_ROWS = 5

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Famicom Breakout')

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0)]

# Game variables
paddle_x = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
ball_x, ball_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
ball_speed_x, ball_speed_y = BALL_SPEED_X, BALL_SPEED_Y
bricks = []

# Initialize bricks with different colors
for i in range(BRICK_ROWS):
    row = []
    color = random.choice(COLORS)  # Randomly choose a color for each row
    for j in range(BRICK_COLS):
        brick_rect = pygame.Rect(j * BRICK_WIDTH, i * BRICK_HEIGHT, BRICK_WIDTH, BRICK_HEIGHT)
        row.append((brick_rect, color))
    bricks.append(row)

# Main game loop
clock = pygame.time.Clock()
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle_x > 0:
        paddle_x -= 5
    if keys[pygame.K_RIGHT] and paddle_x < SCREEN_WIDTH - PADDLE_WIDTH:
        paddle_x += 5

    # Ball movement and collision with walls
    ball_x += ball_speed_x
    ball_y += ball_speed_y
    if ball_x <= 0 or ball_x >= SCREEN_WIDTH - BALL_SIZE:
        ball_speed_x *= -1
    if ball_y <= 0:
        ball_speed_y *= -1
    if ball_y >= SCREEN_HEIGHT - BALL_SIZE:
        # Reset the ball position when it goes past the paddle
        ball_x, ball_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        ball_speed_x, ball_speed_y = BALL_SPEED_X, -BALL_SPEED_Y

    # Ball collision with paddle
    if ball_y + BALL_SIZE >= PADDLE_Y_POSITION and paddle_x < ball_x < paddle_x + PADDLE_WIDTH:
        ball_speed_y *= -1

    # Ball collision with bricks
    for row in bricks:
        for brick, color in row:
            if brick.colliderect(ball_x, ball_y, BALL_SIZE, BALL_SIZE):
                ball_speed_y *= -1
                row.remove((brick, color))
                break

    # Drawing the game state
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, (paddle_x, PADDLE_Y_POSITION, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.circle(screen, WHITE, (ball_x, ball_y), BALL_SIZE)
    for row in bricks:
        for brick, color in row:
            pygame.draw.rect(screen, color, brick)

    # Update the display
    pygame.display.flip()

    # Maintain the frame rate
    clock.tick(FPS)

# Clean up and exit
pygame.quit()
sys.exit()
