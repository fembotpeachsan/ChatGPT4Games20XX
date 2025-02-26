import pygame
import sys
import math
import random
import array

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)

# Constants
WIDTH = 600
HEIGHT = 400
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BALL_SPEED = 5
PADDLE_SPEED = 5
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 50
BALL_SIZE = 10
MAX_SCORE = 5

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong - M1 Optimized")

# Font setup
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Sound generation function
def generate_tone(frequency, duration=0.1):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buffer = [int(32767 * 0.5 * math.sin(2.0 * math.pi * frequency * x / sample_rate))
              for x in range(n_samples)]
    return pygame.mixer.Sound(array.array('h', buffer).tobytes())

# Sound effects
paddle_hit = generate_tone(440)  # 440 Hz for paddle hit
wall_hit = generate_tone(220)    # 220 Hz for wall hit
score_sound = generate_tone(330) # 330 Hz for score

# Game objects
def reset_ball():
    return pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)

ball = reset_ball()
paddle1 = pygame.Rect(0, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = pygame.Rect(WIDTH - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Game variables
ball_dx = BALL_SPEED * random.choice((1, -1))
ball_dy = BALL_SPEED * random.choice((1, -1))
player1_score = 0
player2_score = 0

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
state = MENU

# Drawing functions
def draw_menu():
    screen.fill(BLACK)
    text = font.render("Press Any Key to Start", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, text_rect)
    pygame.display.flip()

def draw_game():
    screen.fill(BLACK)
    # Draw dotted middle line
    for y in range(0, HEIGHT, 20):
        pygame.draw.line(screen, GRAY, (WIDTH//2, y), (WIDTH//2, y + 10), 2)
    # Draw paddles and ball
    pygame.draw.rect(screen, WHITE, paddle1)
    pygame.draw.rect(screen, WHITE, paddle2)
    pygame.draw.rect(screen, WHITE, ball)
    # Draw scores
    score1_text = small_font.render(str(player1_score), True, WHITE)
    score2_text = small_font.render(str(player2_score), True, WHITE)
    screen.blit(score1_text, (WIDTH//4, 20))
    screen.blit(score2_text, (3*WIDTH//4, 20))
    pygame.display.flip()

def draw_game_over(winner):
    screen.fill(BLACK)
    text = font.render(f"{winner} Wins!", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
    screen.blit(text, text_rect)
    restart_text = small_font.render("R to Restart, Q to Quit", True, GRAY)
    restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
    screen.blit(restart_text, restart_rect)
    pygame.display.flip()

# Main game loop
clock = pygame.time.Clock()

def main():
    global state, ball, ball_dx, ball_dy, player1_score, player2_score

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if state == MENU and event.type == pygame.KEYDOWN:
                state = PLAYING
                player1_score = 0
                player2_score = 0
                ball = reset_ball()
                ball_dx = BALL_SPEED * random.choice((1, -1))
                ball_dy = BALL_SPEED * random.choice((1, -1))
            elif state == GAME_OVER and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    state = MENU
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

        if state == MENU:
            draw_menu()
        elif state == PLAYING:
            # Paddle movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] and paddle1.top > 0:
                paddle1.y -= PADDLE_SPEED
            if keys[pygame.K_s] and paddle1.bottom < HEIGHT:
                paddle1.y += PADDLE_SPEED
            if keys[pygame.K_UP] and paddle2.top > 0:
                paddle2.y -= PADDLE_SPEED
            if keys[pygame.K_DOWN] and paddle2.bottom < HEIGHT:
                paddle2.y += PADDLE_SPEED

            # Ball movement
            ball.x += ball_dx
            ball.y += ball_dy

            # Ball collisions
            if ball.top <= 0 or ball.bottom >= HEIGHT:
                ball_dy = -ball_dy
                wall_hit.play()
            if ball.colliderect(paddle1) or ball.colliderect(paddle2):
                ball_dx = -ball_dx
                paddle_hit.play()

            # Scoring
            if ball.left <= 0:
                player2_score += 1
                score_sound.play()
                ball = reset_ball()
                ball_dx = BALL_SPEED * random.choice((1, -1))
                ball_dy = BALL_SPEED * random.choice((1, -1))
            elif ball.right >= WIDTH:
                player1_score += 1
                score_sound.play()
                ball = reset_ball()
                ball_dx = BALL_SPEED * random.choice((1, -1))
                ball_dy = BALL_SPEED * random.choice((1, -1))

            # Check for game over
            if player1_score >= MAX_SCORE:
                state = GAME_OVER
                winner = "Player 1"
            elif player2_score >= MAX_SCORE:
                state = GAME_OVER
                winner = "Player 2"

            draw_game()
        elif state == GAME_OVER:
            draw_game_over(winner)
            pygame.time.wait(100)  # Slight delay to reduce CPU usage

        clock.tick(60)

if __name__ == "__main__":
    main()
