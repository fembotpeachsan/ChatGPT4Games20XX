import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 640, 480
BALL_SIZE = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 80
FPS = 60

# Set up the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the paddles and ball
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_SIZE, BALL_SIZE)
paddle1 = pygame.Rect(0, HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = pygame.Rect(WIDTH - PADDLE_WIDTH, HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Set up the ball speed and direction
ball_dx = 3
ball_dy = 3

# Set up the paddle speed
paddle_speed = 2

# Set up the game clock
clock = pygame.time.Clock()

# Initialize scores
score1 = 0
score2 = 0

# Set up a font
font = pygame.font.Font(None, 36)

# Game loop
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        paddle1.move_ip(0, -paddle_speed)
    if keys[pygame.K_s]:
        paddle1.move_ip(0, paddle_speed)
    if keys[pygame.K_UP]:
        paddle2.move_ip(0, -paddle_speed)
    if keys[pygame.K_DOWN]:
        paddle2.move_ip(0, paddle_speed)

    # Keep paddles on the screen
    if paddle1.top < 0:
        paddle1.top = 0
    if paddle1.bottom > HEIGHT:
        paddle1.bottom = HEIGHT
    if paddle2.top < 0:
        paddle2.top = 0
    if paddle2.bottom > HEIGHT:
        paddle2.bottom = HEIGHT

    # Ball movement
    ball.move_ip(ball_dx, ball_dy)

    # Ball collision with paddles
    if ball.colliderect(paddle1) or ball.colliderect(paddle2):
        ball_dx *= -1
    # Ball collision with top and bottom
    elif ball.top < 0 or ball.bottom > HEIGHT:
        ball_dy *= -1
    # Ball collision with left and right
    elif ball.left < 0:
        score2 += 1
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_dx *= -1
    elif ball.right > WIDTH:
        score1 += 1
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_dx *= -1

    # Fill the screen
    screen.fill((0, 0, 0))

    # Draw everything
    pygame.draw.rect(screen, (200, 200, 200), paddle1)
    pygame.draw.rect(screen, (200, 200, 200), paddle2)
    pygame.draw.ellipse(screen, (200, 200, 200), ball)
    pygame.draw.aaline(screen, (200, 200, 200), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

    # Draw scores
    score_text = font.render(f"{score1}   {score2}", True, (200, 200, 200))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

    # Flip the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)
