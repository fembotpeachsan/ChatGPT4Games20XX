import pygame
import random
import sys
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set the game window size
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
BLOCK_SIZE = 20

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set the clock for controlling FPS
clock = pygame.time.Clock()
FPS = 10  # Adjusted for a more classic Snake game speed

# Define fonts
font = pygame.font.SysFont('arial', 24)

# Create the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Classic Snake Game')

# Function to generate a NumPy sine wave sound
def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=4096):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return np.int16(wave).tobytes()

# Create sound effects
eat_sound = pygame.mixer.Sound(generate_sine_wave(440, 0.1))  # 440Hz (A4) for 0.1 seconds
game_over_sound = pygame.mixer.Sound(generate_sine_wave(220, 0.5))  # 220Hz (A3) for 0.5 seconds

# Snake class
class Snake:
    def __init__(self):
        self.body = [(100, 100), (80, 100), (60, 100)]
        self.direction = pygame.K_RIGHT

    def move(self):
        head_x, head_y = self.body[0]

        if self.direction == pygame.K_RIGHT:
            new_head = (head_x + BLOCK_SIZE, head_y)
        elif self.direction == pygame.K_LEFT:
            new_head = (head_x - BLOCK_SIZE, head_y)
        elif self.direction == pygame.K_UP:
            new_head = (head_x, head_y - BLOCK_SIZE)
        elif self.direction == pygame.K_DOWN:
            new_head = (head_x, head_y + BLOCK_SIZE)

        self.body = [new_head] + self.body[:-1]

    def grow(self):
        self.body.append(self.body[-1])

    def check_collision(self):
        # Check collision with walls
        head_x, head_y = self.body[0]
        if (head_x < 0 or head_x >= WINDOW_WIDTH or
                head_y < 0 or head_y >= WINDOW_HEIGHT):
            return True

        # Check collision with itself
        if len(self.body) > 1 and self.body[0] in self.body[1:]:
            return True

        return False

    def draw(self, surface):
        for block in self.body:
            pygame.draw.rect(surface, GREEN, pygame.Rect(block[0], block[1], BLOCK_SIZE, BLOCK_SIZE))

# Food class
class Food:
    def __init__(self):
        self.position = (random.randint(0, (WINDOW_WIDTH // BLOCK_SIZE) - 1) * BLOCK_SIZE,
                         random.randint(0, (WINDOW_HEIGHT // BLOCK_SIZE) - 1) * BLOCK_SIZE)

    def draw(self, surface):
        pygame.draw.rect(surface, RED, pygame.Rect(self.position[0], self.position[1], BLOCK_SIZE, BLOCK_SIZE))

def display_score(score):
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (10, 10))

# Main game loop
def game_loop():
    snake = Snake()
    food = Food()
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    if (event.key == pygame.K_LEFT and snake.direction != pygame.K_RIGHT or
                        event.key == pygame.K_RIGHT and snake.direction != pygame.K_LEFT or
                        event.key == pygame.K_UP and snake.direction != pygame.K_DOWN or
                        event.key == pygame.K_DOWN and snake.direction != pygame.K_UP):
                        snake.direction = event.key

        snake.move()

        # Check if snake eats the food
        if snake.body[0] == food.position:
            snake.grow()
            score += 1
            food = Food()
            eat_sound.play()

        # Check if the snake collides
        if snake.check_collision():
            game_over_sound.play()
            break

        # Fill the background
        screen.fill(BLACK)

        # Draw snake and food
        snake.draw(screen)
        food.draw(screen)

        # Display score
        display_score(score)

        # Update the display
        pygame.display.update()

        # Cap the frame rate
        clock.tick(FPS)

    # Game over
    game_over_text = font.render('Game Over! Press R to Restart or Q to Quit', True, WHITE)
    screen.blit(game_over_text, (WINDOW_WIDTH // 8, WINDOW_HEIGHT // 2))
    pygame.display.update()

    # Wait for restart or quit
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_loop()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# Start the game
game_loop()
