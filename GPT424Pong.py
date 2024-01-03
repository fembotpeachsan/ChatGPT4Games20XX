# Pong.py
# Import the Pygame library
import pygame
import sys

# Initialize Pygame
pygame.init()

# Define the game window size and other constants
WIDTH, HEIGHT = 800, 600
BALL_SPEED = 7
PADDLE_SPEED = 7
BALL_SIZE = 20
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pong')

# Define the ball and paddles as rectangles
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
left_paddle = pygame.Rect(10, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WIDTH - 10 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Define the ball's movement vector
ball_dx = BALL_SPEED
ball_dy = BALL_SPEED

# Initialize score variables
score_left = 0
score_right = 0

# Set up the font for displaying the score
score_font = pygame.font.Font(None, 36)

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle paddle movement based on key presses
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
        left_paddle.y += PADDLE_SPEED
    if keys[pygame.K_UP] and right_paddle.top > 0:
        right_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and right_paddle.bottom < HEIGHT:
        right_paddle.y += PADDLE_SPEED

    # Update the ball's movement
    ball.x += ball_dx
    ball.y += ball_dy

    # Handle ball collision with the top and bottom of the window
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_dy = -ball_dy

    # Handle ball collision with the paddles
    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        ball_dx = -ball_dx

    # Handle scoring
    if ball.left <= 0:
        score_right += 1
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_dx = -ball_dx
    if ball.right >= WIDTH:
        score_left += 1
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_dx = -ball_dx

    # Draw everything
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

    # Display the score
    score_text = score_font.render(f"{score_left}    {score_right}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

    # Update the display
    pygame.display.flip()

    # Limit the frame rate to 60 frames per second
    pygame.time.Clock().tick(60)

# Quit Pygame when the main loop is finished
pygame.quit()
sys.exit()
