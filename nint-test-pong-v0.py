import pygame
import numpy as np

# --- Audio Configuration ---
SAMPLE_RATE = 44100  # Standard audio sample rate
DURATION = 0.1       # Length of sound effects in seconds

# Initialize Pygame Mixer Before Pygame
pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 512)
pygame.init()

# --- Constants ---
# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_COLOR = (0, 0, 0)  # Black

# Paddle dimensions and color
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 80
PADDLE_COLOR = (255, 255, 255)  # White
PADDLE_SPEED = 6

# Ball dimensions and color
BALL_SIZE = 15
BALL_COLOR = (255, 255, 255)  # White
BALL_SPEED_X = 5
BALL_SPEED_Y = 5

# Score
SCORE_COLOR = (255, 255, 255)

# --- Game Variables ---
left_paddle_x = 50
left_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
right_paddle_x = SCREEN_WIDTH - 50 - PADDLE_WIDTH
right_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2

ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2
ball_speed_x = BALL_SPEED_X
ball_speed_y = BALL_SPEED_Y

left_score = 0
right_score = 0

# --- Sound Generation Functions ---
def generate_square_wave(frequency, duration, amplitude=0.5):
    """Generate a square wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
    return (wave * 32767).astype(np.int16)

def generate_noise(duration, amplitude=0.5):
    """Generate white noise."""
    samples = np.random.uniform(-1, 1, int(SAMPLE_RATE * duration))
    return (samples * amplitude * 32767).astype(np.int16)

def generate_square_wave_sound(frequency, duration, amplitude=0.5):
    """Convert a square wave to a Pygame Sound object."""
    wave = generate_square_wave(frequency, duration, amplitude)
    sound = pygame.sndarray.make_sound(wave)
    return sound

def generate_noise_sound(duration, amplitude=0.5):
    """Convert noise to a Pygame Sound object."""
    wave = generate_noise(duration, amplitude)
    sound = pygame.sndarray.make_sound(wave)
    return sound

# --- Pre-generate Sound Effects ---
collision_sound = generate_square_wave_sound(440, DURATION)  # A4 note
paddle_hit_sound = generate_square_wave_sound(880, DURATION)  # A5 note
score_sound = generate_noise_sound(DURATION)  # White noise for scoring

# --- Drawing Function ---
def draw_objects():
    """Draws the paddles, ball, and scores on the screen."""
    screen.fill(SCREEN_COLOR)
    
    # Draw paddles
    pygame.draw.rect(screen, PADDLE_COLOR, (left_paddle_x, left_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(screen, PADDLE_COLOR, (right_paddle_x, right_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    
    # Draw ball
    pygame.draw.circle(screen, BALL_COLOR, (int(ball_x), int(ball_y)), BALL_SIZE // 2)
    
    # Draw scores
    left_score_text = font.render(str(left_score), True, SCORE_COLOR)
    right_score_text = font.render(str(right_score), True, SCORE_COLOR)
    screen.blit(left_score_text, (SCREEN_WIDTH // 4, 10))
    screen.blit(right_score_text, (SCREEN_WIDTH * 3 // 4 - right_score_text.get_width(), 10))

# --- Paddle Movement Function ---
def move_paddles():
    """Handles paddle movement based on key presses."""
    global left_paddle_y, right_paddle_y
    keys = pygame.key.get_pressed()
    
    # Left paddle controls (W/S)
    if keys[pygame.K_w] and left_paddle_y > 0:
        left_paddle_y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle_y < SCREEN_HEIGHT - PADDLE_HEIGHT:
        left_paddle_y += PADDLE_SPEED
    
    # Right paddle controls (Up/Down)
    if keys[pygame.K_UP] and right_paddle_y > 0:
        right_paddle_y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and right_paddle_y < SCREEN_HEIGHT - PADDLE_HEIGHT:
        right_paddle_y += PADDLE_SPEED

# --- Ball Movement Function ---
def move_ball():
    """Handles ball movement, collisions, and scoring."""
    global ball_x, ball_y, ball_speed_x, ball_speed_y, left_score, right_score
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Top and bottom collisions
    if ball_y - BALL_SIZE // 2 <= 0 or ball_y + BALL_SIZE // 2 >= SCREEN_HEIGHT:
        ball_speed_y *= -1
        collision_sound.play()

    # Paddle collisions
    if (
        left_paddle_x < ball_x < left_paddle_x + PADDLE_WIDTH
        and left_paddle_y < ball_y < left_paddle_y + PADDLE_HEIGHT
    ) or (
        right_paddle_x < ball_x < right_paddle_x + PADDLE_WIDTH
        and right_paddle_y < ball_y < right_paddle_y + PADDLE_HEIGHT
    ):
        ball_speed_x *= -1
        paddle_hit_sound.play()

    # Scoring
    if ball_x <= 0:
        right_score += 1
        score_sound.play()
        reset_ball()
    elif ball_x >= SCREEN_WIDTH:
        left_score += 1
        score_sound.play()
        reset_ball()

# --- Ball Reset Function ---
def reset_ball():
    """Resets the ball to the center of the screen with randomized direction."""
    global ball_x, ball_y, ball_speed_x, ball_speed_y
    ball_x = SCREEN_WIDTH // 2
    ball_y = SCREEN_HEIGHT // 2
    # Randomize initial direction
    ball_speed_x = BALL_SPEED_X if np.random.rand() > 0.5 else -BALL_SPEED_X
    ball_speed_y = BALL_SPEED_Y if np.random.rand() > 0.5 else -BALL_SPEED_Y

# --- Initialize Pygame Display ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Pong with NES Audio")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)  # Use default font

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update game objects
    move_paddles()
    move_ball()
    
    # Render everything
    draw_objects()
    
    # Update the display
    pygame.display.flip()
    
    # Maintain 60 FPS
    clock.tick(60)

# --- Quit Pygame ---
pygame.quit()
