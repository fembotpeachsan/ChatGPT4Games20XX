import sys
import pygame
from array import array

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Game constants
WIDTH, HEIGHT = 640, 480
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 60
BALL_SIZE = 10
PADDLE_SPEED = 5
BALL_SPEED = 3
SPEED_INCREMENT = 0.1

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Create game window and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultra Pong M1")
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

# Create sound effects
hit_sound = generate_beep_sound(440, 0.1)  # Sound when the ball hits a paddle
wall_sound = generate_beep_sound(330, 0.1)  # Sound when the ball hits a wall
score_sound = generate_beep_sound(220, 0.1)  # Sound when a player scores

# Paddle and Ball classes
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.dy = 0

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

    def move(self):
        self.rect.y += self.dy
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT

class Ball:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BALL_SIZE, BALL_SIZE)
        self.dx = BALL_SPEED
        self.dy = BALL_SPEED

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

    def update(self, paddle1, paddle2):
        # Ball collision with paddles
        if self.rect.colliderect(paddle1.rect) or self.rect.colliderect(paddle2.rect):
            self.dx *= -1
            hit_sound.play()  # Play sound when hitting a paddle

        # Ball collision with top/bottom walls
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy *= -1
            wall_sound.play()  # Play sound when hitting a wall

        # Update ball position
        self.rect.x += self.dx
        self.rect.y += self.dy

    def reset(self):
        # Reset the ball to the center
        self.rect.x = WIDTH // 2 - BALL_SIZE // 2
        self.rect.y = HEIGHT // 2 - BALL_SIZE // 2
        self.dx = BALL_SPEED * (1 if self.dx < 0 else -1)
        self.dy = BALL_SPEED * (1 if self.dy < 0 else -1)
        score_sound.play()  # Play sound when a player scores

# Create paddles and ball
paddle1 = Paddle(PADDLE_WIDTH // 2, HEIGHT // 2 - PADDLE_HEIGHT // 2)
paddle2 = Paddle(WIDTH - PADDLE_WIDTH // 2 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2)
ball = Ball(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2)

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                paddle1.dy = -PADDLE_SPEED
            if event.key == pygame.K_s:
                paddle1.dy = PADDLE_SPEED
            if event.key == pygame.K_UP:
                paddle2.dy = -PADDLE_SPEED
            if event.key == pygame.K_DOWN:
                paddle2.dy = PADDLE_SPEED

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_s:
                paddle1.dy = 0
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                paddle2.dy = 0

    # Update game objects
    paddle1.move()
    paddle2.move()
    ball.update(paddle1, paddle2)

    # Check for scoring
    if ball.rect.left <= 0 or ball.rect.right >= WIDTH:
        ball.reset()  # Reset ball position and speed

    # Draw objects
    screen.fill(BLACK)
    paddle1.draw()
    paddle2.draw()
    ball.draw()

    # Update the display
    pygame.display.update()

    # Limit frame rate
    clock.tick(60)
