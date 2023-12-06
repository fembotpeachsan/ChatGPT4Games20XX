import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BRICK_WIDTH, BRICK_HEIGHT = 75, 30
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 15
BALL_RADIUS = 8
BALL_SPEED = 5
PADDLE_SPEED = 7
WHITE = (255, 255, 255)
BRICK_COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 128, 0),
                (0, 0, 255), (75, 0, 130), (238, 130, 238)]  # Red, Orange, Yellow, Green, Blue, Indigo, Violet
FPS = 60

# Setup display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Brick Breaker')

# Setup paddle
paddle = pygame.Rect((SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, SCREEN_HEIGHT - 50), (PADDLE_WIDTH, PADDLE_HEIGHT))

# Setup ball
ball = pygame.Rect((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), (BALL_RADIUS * 2, BALL_RADIUS * 2))
ball_speed = [BALL_SPEED, -BALL_SPEED]

# Setup bricks
bricks = []
for y in range(5):
    for x in range(SCREEN_WIDTH // BRICK_WIDTH):
        bricks.append(pygame.Rect(x * BRICK_WIDTH, y * BRICK_HEIGHT, BRICK_WIDTH, BRICK_HEIGHT))

# Main game loop
running = True
clock = pygame.time.Clock()
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.move_ip(-PADDLE_SPEED, 0)
    if keys[pygame.K_RIGHT] and paddle.right < SCREEN_WIDTH:
        paddle.move_ip(PADDLE_SPEED, 0)

    # Ball movement
    ball.move_ip(ball_speed)
    if ball.left <= 0 or ball.right >= SCREEN_WIDTH:
        ball_speed[0] = -ball_speed[0]
    if ball.top <= 0:
        ball_speed[1] = -ball_speed[1]
    if ball.colliderect(paddle):
        ball_speed[1] = -ball_speed[1]
    if ball.bottom >= SCREEN_HEIGHT:
        running = False  # End game if the ball touches the bottom

    # Ball and bricks collision
    for brick in bricks[:]:
        if ball.colliderect(brick):
            ball_speed[1] = -ball_speed[1]
            bricks.remove(brick)

    # Drawing
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, WHITE, paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    for brick_color, brick in zip(BRICK_COLORS * (len(bricks) // len(BRICK_COLORS) + 1), bricks):
        pygame.draw.rect(screen, brick_color, brick)

    # Update display
    pygame.display.flip()

    # Frame rate
    clock.tick(FPS)

pygame.quit()
