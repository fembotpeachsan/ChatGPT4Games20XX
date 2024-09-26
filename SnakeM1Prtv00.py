import pygame
import random
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the game window
width, height = 800, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Define game variables
cell_size = 20
fps = 10
clock = pygame.time.Clock()

# Define sound effects using proper waveforms
def generate_sound_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    stereo_wave = np.column_stack((wave, wave))  # Make it 2-dimensional for stereo
    return (stereo_wave * 32767).astype(np.int16)  # Convert to int16 for Pygame

eat_sound_data = generate_sound_wave(440, 0.1)  # 440 Hz for 0.1 seconds
eat_sound = pygame.sndarray.make_sound(eat_sound_data)

game_over_sound_data = generate_sound_wave(220, 0.1)  # 220 Hz for 0.1 seconds
game_over_sound = pygame.sndarray.make_sound(game_over_sound_data)

# Define the Snake class
class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [(width // 2, height // 2)]
        self.direction = random.choice([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT])
        self.grow_trigger = False

    def get_head_position(self):
        return self.positions[0]

    def turn(self, direction):
        if direction == pygame.K_UP and self.direction != pygame.K_DOWN:
            self.direction = pygame.K_UP
        elif direction == pygame.K_DOWN and self.direction != pygame.K_UP:
            self.direction = pygame.K_DOWN
        elif direction == pygame.K_LEFT and self.direction != pygame.K_RIGHT:
            self.direction = pygame.K_LEFT
        elif direction == pygame.K_RIGHT and self.direction != pygame.K_LEFT:
            self.direction = pygame.K_RIGHT

    def move(self):
        head_x, head_y = self.get_head_position()
        if self.direction == pygame.K_UP:
            head_y -= cell_size
        elif self.direction == pygame.K_DOWN:
            head_y += cell_size
        elif self.direction == pygame.K_LEFT:
            head_x -= cell_size
        elif self.direction == pygame.K_RIGHT:
            head_x += cell_size

        new_head = (head_x, head_y)
        if self.grow_trigger:
            self.positions = [new_head] + self.positions
            self.grow_trigger = False
        else:
            self.positions = [new_head] + self.positions[:-1]

    def grow(self):
        self.grow_trigger = True

    def draw(self, surface):
        for position in self.positions:
            pygame.draw.rect(surface, GREEN, pygame.Rect(position[0], position[1], cell_size, cell_size))

    def collide(self):
        head_x, head_y = self.get_head_position()
        # Check for collisions with walls
        if head_x < 0 or head_x >= width or head_y < 0 or head_y >= height:
            return True
        # Check for collisions with self
        for position in self.positions[1:]:
            if position == (head_x, head_y):
                return True
        return False

# Define the Food class
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, (width // cell_size) - 1) * cell_size, random.randint(0, (height // cell_size) - 1) * cell_size)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, pygame.Rect(self.position[0], self.position[1], cell_size, cell_size))

# Define the main game loop
def main():
    snake = Snake()
    food = Food()
    score = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                snake.turn(event.key)

        snake.move()
        # Check if the snake eats the food
        if snake.get_head_position() == food.position:
            snake.grow()
            food.randomize_position()
            score += 1
            eat_sound.play()

        # Check for collision (self or walls)
        if snake.collide():
            game_over_sound.play()
            running = False

        # Render everything
        window.fill(BLACK)
        snake.draw(window)
        food.draw(window)
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()

if __name__ == "__main__":
    main()
