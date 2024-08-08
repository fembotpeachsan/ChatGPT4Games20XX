import pygame
from array import array
import sys

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Constants
WIDTH, HEIGHT = 640, 480
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 80
BALL_SIZE = 15
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PADDLE_SPEED = 5
BALL_SPEED_X = 3
BALL_SPEED_Y = 3

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pong with Dynamic Sound Engine')
clock = pygame.time.Clock()

# Define a function to generate beep sounds with varying frequencies
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * ((i // (sample_rate // frequency)) % 2)) for i in range(samples)]
    sound = pygame.mixer.Sound(buffer=array('h', wave))
    sound.set_volume(0.1)
    return sound

# Load or generate sounds
synth_wave_sound = generate_beep_sound(440, 0.1)  # A4
boop_sound = generate_beep_sound(523.25, 0.1)  # C5
score_sound = generate_beep_sound(587.33, 0.1)  # D5

# Paddle objects
paddle_a = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle_b = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Ball object
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
ball_speed_x = BALL_SPEED_X
ball_speed_y = BALL_SPEED_Y

# Initialize scores
score_a = 0
score_b = 0

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Movement of paddles
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and paddle_b.top > 0:
        paddle_b.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and paddle_b.bottom < HEIGHT:
        paddle_b.y += PADDLE_SPEED
    if keys[pygame.K_w] and paddle_a.top > 0:
        paddle_a.y -= PADDLE_SPEED
    if keys[pygame.K_s] and paddle_a.bottom < HEIGHT:
        paddle_a.y += PADDLE_SPEED

    # Ball movement
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Collision with top and bottom walls
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y = -ball_speed_y
        synth_wave_sound.play()

    # Collision with paddles
    if ball.colliderect(paddle_a) or ball.colliderect(paddle_b):
        ball_speed_x = -ball_speed_x
        boop_sound.play()

    # Scoring logic (when a player scores, the ball is reset to the center)
    if ball.left <= 0:
        ball.center = (WIDTH // 2, HEIGHT // 2)
        paddle_b.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        score_a += 1
        score_sound.play()
    elif ball.right >= WIDTH:
        ball.center = (WIDTH // 2, HEIGHT // 2)
        paddle_a.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        score_b += 1
        score_sound.play()

    # Drawing everything
    screen.fill(BLACK)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.rect(screen, WHITE, paddle_a)
    pygame.draw.rect(screen, WHITE, paddle_b)
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

    # Displaying scores
    font = pygame.font.Font(None, 36)
    score_text_a = font.render(str(score_a), True, WHITE)
    score_text_b = font.render(str(score_b), True, WHITE)
    screen.blit(score_text_a, (WIDTH // 4 - 20, 20))
    screen.blit(score_text_b, (3 * WIDTH // 4 - 20, 20))

    # Updating the display
    pygame.display.flip()
    clock.tick(60)
    ## [TEAM SNAKE CODEX 1.0]
