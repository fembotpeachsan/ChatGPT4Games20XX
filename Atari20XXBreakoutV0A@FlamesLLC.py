import pygame
import sys
import time

# Game parameters
SCREEN_SIZE = (600, 400)
BALL_RADIUS = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 80, 10
BRICK_WIDTH, BRICK_HEIGHT = 50, 20
BRICK_ROWS, BRICK_COLS = 5, 10
FPS = 60

# Color constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Pygame initialization
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

def reset_game():
    global paddle, ball, ball_dx, ball_dy, bricks, score

    # Game objects
    paddle = pygame.Rect(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] - 50, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2, BALL_RADIUS, BALL_RADIUS)
    ball_dx, ball_dy = 3, 3

    # Brick grid
    bricks = [pygame.Rect(j * (BRICK_WIDTH + 2), i * (BRICK_HEIGHT + 2) + 50, BRICK_WIDTH, BRICK_HEIGHT) 
            for i in range(BRICK_ROWS) for j in range(BRICK_COLS)]

    score = 0

reset_game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Paddle control
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and paddle.left > 0:
        paddle.left -= 5
    if keys[pygame.K_d] and paddle.right < SCREEN_SIZE[0]:
        paddle.right += 5

    # Ball movement
    ball.left += ball_dx
    ball.top += ball_dy

    # Collision with walls
    if ball.left < 0 or ball.right > SCREEN_SIZE[0]:
        ball_dx *= -1
    if ball.top < 0:
        ball_dy *= -1

    # Collision with paddle
    if ball.colliderect(paddle):
        ball_dy *= -1

    # Collision with bricks
    for brick in bricks:
        if ball.colliderect(brick):
            ball_dy *= -1
            bricks.remove(brick)
            score += 10
            break

    # Win condition
    if len(bricks) == 0:
        print("You win! Would you like to restart? (y/n)")
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        reset_game()
                    elif event.key == pygame.K_n:
                        print("Okay, goodbye!")
                        pygame.quit()
                        sys.exit()

    # Game over condition
    if ball.top > SCREEN_SIZE[1]:
        print("Game over!")
        break

    # Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, paddle)
    pygame.draw.ellipse(screen, WHITE, ball)

    for brick in bricks:
        pygame.draw.rect(screen, RED, brick)
    
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)
