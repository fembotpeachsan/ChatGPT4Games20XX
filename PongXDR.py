import pygame
import numpy as np
import tempfile
import wave

# Function to generate a sine wave and save it as a .wav file
def generate_beep(frequency, duration, volume=0.5, sample_rate=44100):
    # Create a sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave_data = np.sin(2 * np.pi * frequency * t) * volume
    wave_data = (wave_data * 32767).astype(np.int16)  # Convert to 16-bit data

    # Create a temporary .wav file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
        with wave.open(f.name, 'w') as wave_file:
            # Set up the .wav file parameters
            wave_file.setnchannels(1)  # Mono
            wave_file.setsampwidth(2)  # 16 bits per sample
            wave_file.setframerate(sample_rate)
            wave_file.writeframes(wave_data.tobytes())
        return f.name

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 600
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))

# Set up the clock for FPS control
clock = pygame.time.Clock()
fps = 60  # Set the frame rate to 60 FPS

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)  # For bricks

# --- Initialize game elements ---

# Paddle
paddle_width = 80
paddle_height = 10
paddle_x = screen_width // 2 - paddle_width // 2
paddle_y = screen_height - 50
paddle_speed = 5

# Ball
ball_radius = 10
ball_x = screen_width // 2
ball_y = screen_height // 2
ball_speed_x = 2  # Slow down the ball speed
ball_speed_y = -2  # Slow down the ball speed

# Bricks (rows, columns)
brick_rows = 3
brick_cols = 8
brick_width = 70
brick_height = 20
brick_padding = 10  # Space between bricks
brick_offset_top = 30  # Top margin
brick_offset_left = 30  # Left margin

# Create bricks array (1 for present, 0 for broken)
bricks = np.ones((brick_rows, brick_cols))

# Generate beep sound using NumPy
beep_wav_file = generate_beep(frequency=440, duration=0.1)
beep_sound = pygame.mixer.Sound(beep_wav_file)

# --- Game loop ---
running = True
while running:
    # Maintain 60 FPS
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Handle paddle movement ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle_x > 0:
        paddle_x -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle_x < screen_width - paddle_width:
        paddle_x += paddle_speed

    # --- Ball movement ---
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # --- Collision detection ---
    # Ball with walls
    if ball_x <= 0 or ball_x >= screen_width - ball_radius * 2:
        ball_speed_x *= -1
    if ball_y <= 0:
        ball_speed_y *= -1
    if ball_y >= screen_height:  # Game Over condition (ball goes past paddle)
        running = False

    # Ball with paddle
    if (ball_y + ball_radius * 2 >= paddle_y and
            ball_x + ball_radius >= paddle_x and
            ball_x <= paddle_x + paddle_width):
        ball_speed_y *= -1
        beep_sound.play()  # Play beep on paddle collision

    # Ball with bricks
    for row in range(brick_rows):
        for col in range(brick_cols):
            if bricks[row][col] == 1:
                brick_x = brick_offset_left + col * (brick_width + brick_padding)
                brick_y = brick_offset_top + row * (brick_height + brick_padding)

                if (ball_x + ball_radius * 2 > brick_x and
                        ball_x < brick_x + brick_width and
                        ball_y + ball_radius * 2 > brick_y and
                        ball_y < brick_y + brick_height):
                    bricks[row][col] = 0  # Mark brick as broken
                    ball_speed_y *= -1
                    beep_sound.play()

    # --- Drawing ---
    screen.fill(BLACK)

    # Draw paddle
    pygame.draw.rect(screen, WHITE, (paddle_x, paddle_y, paddle_width, paddle_height))

    # Draw ball
    pygame.draw.circle(screen, WHITE, (ball_x + ball_radius, ball_y + ball_radius), ball_radius)

    # Draw bricks
    for row in range(brick_rows):
        for col in range(brick_cols):
            if bricks[row][col] == 1:  # Draw only if brick is present
                brick_x = brick_offset_left + col * (brick_width + brick_padding)
                brick_y = brick_offset_top + row * (brick_height + brick_padding)
                pygame.draw.rect(screen, RED, (brick_x, brick_y, brick_width, brick_height))

    pygame.display.flip()  # Update the display

pygame.quit()
## [C] Team Flames 20XX
