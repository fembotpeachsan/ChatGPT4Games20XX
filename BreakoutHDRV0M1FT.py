import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BreakoutHDR")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Game variables
ball_speed_x = 7 * random.choice((1, -1))
ball_speed_y = 7 * random.choice((1, -1))
paddle_speed = 10
score = 0

# Ball
ball = pygame.Rect(WIDTH // 2 - 15, HEIGHT // 2 - 15, 30, 30)

# Paddle
paddle = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 20, 120, 10)

# Bricks
brick_rows = 5
brick_cols = 7
brick_width = 80
brick_height = 30
bricks = []

for row in range(brick_rows):
    for col in range(brick_cols):
        brick = pygame.Rect(col * (brick_width + 10) + 35, row * (brick_height + 10) + 35, brick_width, brick_height)
        bricks.append(brick)

# Function to draw game objects
def draw_objects():
    screen.fill(BLACK)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.rect(screen, GREEN, paddle)

    for brick in bricks:
        pygame.draw.rect(screen, RED, brick)

    # Display score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

# Function to handle ball movement
def move_ball():
    global ball_speed_x, ball_speed_y, score

    ball.x += ball_speed_x
    ball.y += ball_speed_y

    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1
    if ball.left <= 0 or ball.right >= WIDTH:
        ball_speed_x *= -1

    if ball.colliderect(paddle):
        ball_speed_y *= -1
        score += 1

    for brick in bricks[:]:
        if ball.colliderect(brick):
            ball_speed_y *= -1
            bricks.remove(brick)
            score += 3

# Function to handle paddle movement
def move_paddle():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.x -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.x += paddle_speed

# Function to check for game over
def check_game_over():
    if ball.bottom >= HEIGHT:
        return True
    return False

# Main game loop
running = True
font = pygame.font.Font(None, 36)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    move_ball()
    move_paddle()

    if check_game_over():
        running = False

    draw_objects()
    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()
