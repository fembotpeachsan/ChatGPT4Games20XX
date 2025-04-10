import pygame
import sys
import numpy as np
import random

# -------------------------------------------------------------------
# Generate beep/boop sounds without external media
# -------------------------------------------------------------------
def generate_sound(frequency=440, duration=0.1, volume=1.0):
    """
    Generate a synthetic sine wave sound using NumPy and return a pygame Sound object.
    :param frequency: The frequency of the tone in Hz.
    :param duration:  The duration of the sound in seconds.
    :param volume:    The volume (0.0 to 1.0).
    """
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    # Generate time array
    t = np.linspace(0, duration, n_samples, endpoint=False)
    # Generate sine wave
    wave = np.sin(2 * np.pi * frequency * t)

    # Convert to 16-bit signed samples
    wave_integers = np.int16(wave * volume * 32767)

    # Make it stereo by duplicating the wave for left/right channels
    stereo_wave = np.column_stack((wave_integers, wave_integers))

    # Convert to a pygame Sound object
    sound = pygame.sndarray.make_sound(stereo_wave)
    return sound

def main():
    pygame.init()
    # Initialize audio mixer for beep sounds
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    # Screen dimensions
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong")

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # Paddle dimensions
    PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
    BALL_SIZE = 10

    # Speeds
    paddle_speed = 6
    ball_speed_x = random.choice([-4, 4])
    ball_speed_y = random.choice([-4, 4])

    # Rect objects for paddles and ball
    left_paddle = pygame.Rect(50, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)

    # Scores
    score_left = 0
    score_right = 0

    # Font
    font = pygame.font.SysFont(None, 48)

    # Create beep/boop sounds
    beep_hit = generate_sound(frequency=600, duration=0.06, volume=0.5)   # for paddle/edge hits
    beep_score = generate_sound(frequency=300, duration=0.2, volume=0.5) # for scoring

    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(60)  # Limit frame rate to 60 FPS

        # --------------------
        # Handle Events
        # --------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --------------------
        # Player Input
        # --------------------
        keys = pygame.key.get_pressed()

        # Left paddle controls (W/S)
        if keys[pygame.K_w] and left_paddle.top > 0:
            left_paddle.y -= paddle_speed
        if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
            left_paddle.y += paddle_speed

        # Right paddle controls (UP/DOWN)
        if keys[pygame.K_UP] and right_paddle.top > 0:
            right_paddle.y -= paddle_speed
        if keys[pygame.K_DOWN] and right_paddle.bottom < HEIGHT:
            right_paddle.y += paddle_speed

        # --------------------
        # Ball Movement
        # --------------------
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Ball collisions with top/bottom
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_speed_y *= -1
            beep_hit.play()

        # Ball collisions with paddles
        if ball.colliderect(left_paddle):
            ball_speed_x *= -1
            beep_hit.play()
        elif ball.colliderect(right_paddle):
            ball_speed_x *= -1
            beep_hit.play()

        # If the ball goes off the left side
        if ball.left <= 0:
            score_right += 1
            beep_score.play()
            # Reset ball to center
            ball.center = (WIDTH//2, HEIGHT//2)
            ball_speed_x = random.choice([-4, 4])
            ball_speed_y = random.choice([-4, 4])

        # If the ball goes off the right side
        if ball.right >= WIDTH:
            score_left += 1
            beep_score.play()
            # Reset ball
            ball.center = (WIDTH//2, HEIGHT//2)
            ball_speed_x = random.choice([-4, 4])
            ball_speed_y = random.choice([-4, 4])

        # --------------------
        # Draw Everything
        # --------------------
        screen.fill(BLACK)

        # Paddles and ball
        pygame.draw.rect(screen, WHITE, left_paddle)
        pygame.draw.rect(screen, WHITE, right_paddle)
        pygame.draw.ellipse(screen, WHITE, ball)

        # Draw center line
        pygame.draw.line(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)

        # Scores
        score_text_left = font.render(str(score_left), True, WHITE)
        score_text_right = font.render(str(score_right), True, WHITE)
        screen.blit(score_text_left, (WIDTH//4 - score_text_left.get_width()//2, 20))
        screen.blit(score_text_right, (3*WIDTH//4 - score_text_right.get_width()//2, 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
