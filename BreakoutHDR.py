import pygame
import sys
import random
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game settings
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BRICK_COLS = 10
BRICK_ROWS = 5
BRICK_WIDTH = WIDTH // BRICK_COLS
BRICK_HEIGHT = 30
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
BALL_RADIUS = 10
FPS = 60

# Setup the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout Game")

# Function to generate a sound using numpy and pygame
def create_sound(freq, duration=0.1, volume=0.5):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * freq * t)
    wave = (wave * volume * (2**15 - 1)).astype(np.int16)  # Convert to 16-bit data
    sound = pygame.mixer.Sound(wave)
    return sound

# Sound effects
hit_paddle_sfx = create_sound(500, duration=0.1, volume=0.5)
hit_wall_sfx = create_sound(300, duration=0.1, volume=0.5)
hit_brick_sfx = create_sound(700, duration=0.1, volume=0.5)

# Game objects
class Paddle:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 8

    def move(self, dx):
        self.rect.x += dx
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - BALL_RADIUS, HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
        self.dx = random.choice([-4, 4])
        self.dy = -4

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.dx = -self.dx
            hit_wall_sfx.play()
        if self.rect.top <= 0:
            self.dy = -self.dy
            hit_wall_sfx.play()

    def draw(self, surface):
        pygame.draw.ellipse(surface, RED, self.rect)

class Brick:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.destroyed = False

    def draw(self, surface):
        if not self.destroyed:
            pygame.draw.rect(surface, BLUE, self.rect)

# Setup bricks
bricks = []
for row in range(BRICK_ROWS):
    for col in range(BRICK_COLS):
        brick = Brick(col * BRICK_WIDTH, row * BRICK_HEIGHT)
        bricks.append(brick)

# Setup paddle and ball
paddle = Paddle()
ball = Ball()

# Main game loop
def main():
    clock = pygame.time.Clock()

    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Move paddle
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move(-paddle.speed)
        if keys[pygame.K_RIGHT]:
            paddle.move(paddle.speed)

        # Move ball
        ball.move()

        # Ball collision with paddle
        if ball.rect.colliderect(paddle.rect):
            ball.dy = -ball.dy
            hit_paddle_sfx.play()

        # Ball collision with bricks
        for brick in bricks:
            if ball.rect.colliderect(brick.rect) and not brick.destroyed:
                ball.dy = -ball.dy
                brick.destroyed = True
                hit_brick_sfx.play()

        # Ball goes below the screen (game over condition)
        if ball.rect.bottom >= HEIGHT:
            pygame.quit()
            sys.exit()

        # Check if all bricks are destroyed (win condition)
        if all(brick.destroyed for brick in bricks):
            print("You Win!")
            pygame.quit()
            sys.exit()

        # Clear screen
        screen.fill(BLACK)

        # Draw game objects
        paddle.draw(screen)
        ball.draw(screen)
        for brick in bricks:
            brick.draw(screen)

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

if __name__ == "__main__":
    main()
