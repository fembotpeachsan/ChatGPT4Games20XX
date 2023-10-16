import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BARRIER_HEIGHT = 20
FPS = 60
MAX_SCORE = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()

# Function to reset game
def reset_game():
    global paddle1_y, paddle2_y, score1, score2
    paddle1_y = HEIGHT // 2
    paddle2_y = HEIGHT // 2
    score1, score2 = 0, 0
    reset_ball()

# Function to reset ball
def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_dx = random.choice([-4, 4])
    ball_dy = random.choice([-4, 4])

# Initialize game variables and reset game
paddle1_y = paddle2_y = ball_x = ball_y = score1 = score2 = 0
reset_game()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and paddle2_y > BARRIER_HEIGHT:
        paddle2_y -= 5
    if keys[pygame.K_DOWN] and paddle2_y < HEIGHT - BARRIER_HEIGHT - PADDLE_HEIGHT:
        paddle2_y += 5

    # Simple AI for left paddle
    if ball_y > paddle1_y + PADDLE_HEIGHT // 2 and paddle1_y < HEIGHT - BARRIER_HEIGHT - PADDLE_HEIGHT:
        paddle1_y += 4
    elif ball_y < paddle1_y + PADDLE_HEIGHT // 2 and paddle1_y > BARRIER_HEIGHT:
        paddle1_y -= 4

    # Update ball
    ball_x += ball_dx
    ball_y += ball_dy

    if ball_y <= BARRIER_HEIGHT or ball_y >= HEIGHT - BARRIER_HEIGHT:
        ball_dy *= -1

    # Ball and paddle collision
    if ball_x <= PADDLE_WIDTH and paddle1_y <= ball_y <= paddle1_y + PADDLE_HEIGHT:
        ball_dx *= -1
    if ball_x >= WIDTH - PADDLE_WIDTH and paddle2_y <= ball_y <= paddle2_y + PADDLE_HEIGHT:
        ball_dx *= -1

    # Scoring
    if ball_x < 0:
        score2 += 1
        if score2 == MAX_SCORE:
            print("You Win!")
            reset_game()
        else:
            reset_ball()
    if ball_x > WIDTH:
        score1 += 1
        if score1 == MAX_SCORE:
            print("AI Wins!")
            reset_game()
        else:
            reset_ball()

    # Draw everything
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, (0, paddle1_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(screen, WHITE, (WIDTH - PADDLE_WIDTH, paddle2_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.circle(screen, WHITE, (ball_x, ball_y), BALL_RADIUS)
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, BARRIER_HEIGHT))  # Top barrier
    pygame.draw.rect(screen, WHITE, (0, HEIGHT - BARRIER_HEIGHT, WIDTH, BARRIER_HEIGHT))  # Bottom barrier

    # Draw score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"{score1} - {score2}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
