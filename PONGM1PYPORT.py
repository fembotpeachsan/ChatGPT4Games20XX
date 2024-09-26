import pygame
import sys
import numpy as np

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)  # Ensure 16-bit stereo sound

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 90
PADDLE_SPEED = 5
BALL_SIZE = 15
BALL_SPEED = 5

# Screen and title
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Font
font = pygame.font.Font(None, 36)

# --- Sound Effects ---
def create_sfx(frequency, duration=0.1, sampling_rate=44100):
    """Create a simple stereo tone sound effect using NumPy."""
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    wave = np.sin(2 * np.pi * frequency * t)  # Mono signal

    # Convert to stereo by duplicating the channel
    stereo_wave = np.column_stack((wave, wave))

    # Scale the wave and convert to int16 for pygame compatibility
    stereo_wave = np.array(stereo_wave * 32767, dtype=np.int16)
    return stereo_wave

# Pre-create sound effects
paddle_hit_sound = pygame.sndarray.make_sound(create_sfx(440))  # A4 note
wall_hit_sound = pygame.sndarray.make_sound(create_sfx(220))    # A3 note
score_sound = pygame.sndarray.make_sound(create_sfx(880, 0.2))  # A5 note, longer

def show_title_screen():
    title_text = font.render("PONG", True, WHITE)
    press_space_text = font.render("Press SPACE to play", True, WHITE)
    screen.fill(BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
    screen.blit(press_space_text, (WIDTH // 2 - press_space_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  # Use sys.exit() for cleaner exit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

def game_loop():
    player1 = pygame.Rect(15, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    player2 = pygame.Rect(WIDTH - 15 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
    ball_dx = BALL_SPEED
    ball_dy = BALL_SPEED
    player1_score = 0
    player2_score = 0
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player1.top > 0:
            player1.y -= PADDLE_SPEED
        if keys[pygame.K_s] and player1.bottom < HEIGHT:
            player1.y += PADDLE_SPEED

        if keys[pygame.K_UP] and player2.top > 0:
            player2.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and player2.bottom < HEIGHT:
            player2.y += PADDLE_SPEED

        # Ball movement
        ball.x += ball_dx
        ball.y += ball_dy

        # Ball collision with top/bottom
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_dy *= -1
            wall_hit_sound.play()

        # Ball collision with paddles
        if ball.colliderect(player1) or ball.colliderect(player2):
            ball_dx *= -1
            paddle_hit_sound.play()

        # Ball out of bounds (scoring)
        if ball.left <= 0:
            player2_score += 1
            ball.x = WIDTH // 2 - BALL_SIZE // 2
            ball.y = HEIGHT // 2 - BALL_SIZE // 2
            ball_dx *= -1  # Reset ball direction
            score_sound.play()
        elif ball.right >= WIDTH:
            player1_score += 1
            ball.x = WIDTH // 2 - BALL_SIZE // 2
            ball.y = HEIGHT // 2 - BALL_SIZE // 2
            ball_dx *= -1  # Reset ball direction
            score_sound.play()

        # Draw everything
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, player1)
        pygame.draw.rect(screen, WHITE, player2)
        pygame.draw.ellipse(screen, WHITE, ball)

        # Display the score
        score_text = font.render(f"{player1_score} - {player2_score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

        pygame.display.flip()
        clock.tick(FPS)

# Initial title screen
show_title_screen()

# Start the game
game_loop()

pygame.quit()
sys.exit()  # Properly quit
