import pygame
import sys
import random
from array import array

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Screen dimensions
WIDTH, HEIGHT = 640, 480
CELL_SIZE = 20
CELL_WIDTH = WIDTH // CELL_SIZE
CELL_HEIGHT = HEIGHT // CELL_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game')

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Define a function to generate beep sounds with varying frequencies
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * ((i // (sample_rate // frequency)) % 2)) for i in range(samples)]
    sound = pygame.mixer.Sound(buffer=array('h', wave))
    sound.set_volume(0.1)
    return sound

# Create a list of sound tuples (name, sound object)
sounds = {
    "eat": generate_beep_sound(440, 0.1),  # A4
    "game_over": generate_beep_sound(523.25, 0.1),  # C5
}

# Snake class
class Snake:
    def __init__(self):
        self.positions = [(CELL_WIDTH // 2, CELL_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.grow = False
        self.hp = 3  # Health points

    def get_head_position(self):
        return self.positions[0]

    def move(self):
        head_x, head_y = self.get_head_position()
        new_x = head_x + self.direction[0]
        new_y = head_y + self.direction[1]

        if new_x < 0 or new_x >= CELL_WIDTH or new_y < 0 or new_y >= CELL_HEIGHT or (new_x, new_y) in self.positions:
            self.hp -= 1
            sounds["game_over"].play()
            if self.hp == 0:
                raise ValueError("Game Over")
            else:
                self.positions = [(CELL_WIDTH // 2, CELL_HEIGHT // 2)]
                self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        else:
            new_position = (new_x, new_y)
            self.positions.insert(0, new_position)

            if not self.grow:
                self.positions.pop()
            else:
                self.grow = False

    def change_direction(self, direction):
        if direction == UP and self.direction != DOWN:
            self.direction = UP
        elif direction == DOWN and self.direction != UP:
            self.direction = DOWN
        elif direction == LEFT and self.direction != RIGHT:
            self.direction = LEFT
        elif direction == RIGHT and self.direction != LEFT:
            self.direction = RIGHT

    def grow_snake(self):
        self.grow = True

    def draw(self, surface):
        for position in self.positions:
            rect = pygame.Rect(position[0] * CELL_SIZE, position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, GREEN, rect)

# Food class
class Food:
    def __init__(self):
        self.position = (random.randint(0, CELL_WIDTH - 1), random.randint(0, CELL_HEIGHT - 1))

    def respawn(self):
        self.position = (random.randint(0, CELL_WIDTH - 1), random.randint(0, CELL_HEIGHT - 1))

    def draw(self, surface):
        rect = pygame.Rect(self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, RED, rect)

# Title screen function
def show_title_screen():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    text = font.render("SNAKE", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    font = pygame.font.Font(None, 36)
    text = font.render("Press any key to start", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.flip()
    wait_for_key()

# Function to wait for a key press
def wait_for_key():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# Main game loop
def main():
    snake = Snake()
    food = Food()
    show_title_screen()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction(UP)
                elif event.key == pygame.K_DOWN:
                    snake.change_direction(DOWN)
                elif event.key == pygame.K_LEFT:
                    snake.change_direction(LEFT)
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction(RIGHT)

        try:
            snake.move()
        except ValueError as e:
            print(e)
            pygame.quit()
            sys.exit()

        if snake.get_head_position() == food.position:
            snake.grow_snake()
            food.respawn()
            sounds["eat"].play()

        screen.fill(BLACK)
        snake.draw(screen)
        food.draw(screen)

        # Draw the HUD
        font = pygame.font.Font(None, 36)
        hud_text = font.render(f"HP: {snake.hp}", True, WHITE)
        screen.blit(hud_text, (WIDTH - hud_text.get_width() - 10, 10))

        pygame.display.update()
        clock.tick(10)

if __name__ == "__main__":
    main()
