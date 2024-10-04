import pygame
import sys
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 20
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Pong Game")

# Sound settings
SAMPLE_RATE = 44100  # Hertz

def generate_sound(frequency, duration=0.1, volume=0.5):
    """
    Generate a sound wave for a given frequency and duration, formatted for stereo.
    """
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = np.sin(frequency * 2 * np.pi * t)
    # Ensure that highest value is in 16-bit range
    audio = wave * (2**15 - 1) * volume
    # Convert to 16-bit data
    audio = audio.astype(np.int16)

    # Make the audio 2D for stereo
    stereo_audio = np.column_stack((audio, audio))
    return stereo_audio

try:
    # Generate sounds
    paddle_sound = pygame.sndarray.make_sound(generate_sound(440))  # A4 note
    wall_sound = pygame.sndarray.make_sound(generate_sound(220))    # A3 note
    score_sound = pygame.sndarray.make_sound(generate_sound(660, duration=0.2))  # E5 note
except pygame.error:
    # Fallback if the sound cannot be generated or if there's an issue with the system's sound
    paddle_sound = None
    wall_sound = None
    score_sound = None

class Paddle:
    def __init__(self, x):
        self.x = x
        self.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.speed = 5

    def move_up(self):
        if self.y > 0:
            self.y -= self.speed

    def move_down(self):
        if self.y < HEIGHT - PADDLE_HEIGHT:
            self.y += self.speed

    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT))

class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = WIDTH // 2 - BALL_SIZE // 2
        self.y = HEIGHT // 2 - BALL_SIZE // 2
        # Randomize initial direction
        self.speed_x = 5 if np.random.rand() > 0.5 else -5
        self.speed_y = 5 if np.random.rand() > 0.5 else -5

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        # Collision with top and bottom walls
        if self.y <= 0 or self.y >= HEIGHT - BALL_SIZE:
            self.speed_y *= -1
            if wall_sound:
                wall_sound.play()

    def draw(self):
        pygame.draw.ellipse(screen, WHITE, (self.x, self.y, BALL_SIZE, BALL_SIZE))

def draw_text(text, x, y, size=36):
    # If 'pressstart2p' font is not available, use the default system font
    font = pygame.font.Font(pygame.font.match_font('pressstart2p', bold=True) or None, size)
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, (x, y))

def play_game():
    clock = pygame.time.Clock()
    ball = Ball()
    paddle1 = Paddle(10)
    paddle2 = Paddle(WIDTH - 20)

    score1 = 0
    score2 = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            paddle1.move_up()
        if keys[pygame.K_s]:
            paddle1.move_down()
        if keys[pygame.K_UP]:
            paddle2.move_up()
        if keys[pygame.K_DOWN]:
            paddle2.move_down()

        ball.move()

        # Collision with paddles
        if (ball.x < paddle1.x + PADDLE_WIDTH and
            paddle1.y < ball.y + BALL_SIZE and
            ball.y < paddle1.y + PADDLE_HEIGHT):
            ball.speed_x *= -1
            ball.x = paddle1.x + PADDLE_WIDTH  # Prevent sticking
            if paddle_sound:
                paddle_sound.play()
        elif (ball.x > paddle2.x - BALL_SIZE and
              paddle2.y < ball.y + BALL_SIZE and
              ball.y < paddle2.y + PADDLE_HEIGHT):
            ball.speed_x *= -1
            ball.x = paddle2.x - BALL_SIZE  # Prevent sticking
            if paddle_sound:
                paddle_sound.play()

        # Scoring
        if ball.x < 0:
            score2 += 1
            if score_sound:
                score_sound.play()
            ball.reset()
        elif ball.x > WIDTH - BALL_SIZE:
            score1 += 1
            if score_sound:
                score_sound.play()
            ball.reset()

        # Drawing
        screen.fill(BLACK)
        paddle1.draw()
        paddle2.draw()
        ball.draw()

        draw_text(str(score1), WIDTH // 4, 20, size=48)
        draw_text(str(score2), WIDTH * 3 // 4, 20, size=48)

        # Check for win
        if score1 == 10:
            screen.fill(BLACK)
            draw_text("Player 1 Wins!", WIDTH // 2 - 150, HEIGHT // 2 - 24, size=48)
            pygame.display.flip()
            pygame.time.wait(2000)
            return
        elif score2 == 10:
            screen.fill(BLACK)
            draw_text("Player 2 Wins!", WIDTH // 2 - 150, HEIGHT // 2 - 24, size=48)
            pygame.display.flip()
            pygame.time.wait(2000)
            return

        # Update display
        pygame.display.flip()
        clock.tick(FPS)

def main_menu():
    screen.fill(BLACK)
    draw_text("Press SPACE to Play", WIDTH // 2 - 200, HEIGHT // 2 - 24, size=48)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return

def main():
    while True:
        main_menu()
        play_game()

if __name__ == "__main__":
    main()
