#!/usr/bin/env python3

import pygame
import sys
import random
import numpy as np

# -----------------------------
# Configurable Game Parameters
# -----------------------------
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# Dimensions of each grid cell for the snake and food
CELL_SIZE = 20

# Frames per second (speed of the game)
FPS = 10

# Colors (R, G, B)
COLOR_BG      = (  0,   0,   0)   # Black
COLOR_SNAKE   = ( 50, 205,  50)   # LimeGreen
COLOR_FOOD    = (220,  20,  60)   # Crimson
COLOR_TEXT    = (255, 255, 255)   # White
COLOR_GRID    = ( 40,  40,  40)   # Dark grey for grid lines (optional)

# -----------------------------
# Initialize Pygame
# -----------------------------
pygame.init()
pygame.display.set_caption("Synthwave Snake - M1 Mac Compatible")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
pygame.mixer.init()

# -----------------------------
# Generate Synthwave Sound Effects
# -----------------------------
def generate_sine_wave(frequency, duration, sample_rate=44100):
    """Generate a sine wave for sound effects."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    sound = (wave * 32767).astype(np.int16)
    sound = np.repeat(sound[:, np.newaxis], 2, axis=1)
    return pygame.mixer.Sound(buffer=sound.tobytes())

# Create simple beeps
beep_food = generate_sine_wave(880, 0.1)  # Higher-pitched beep for food
beep_gameover = generate_sine_wave(220, 0.3)  # Lower-pitched beep for game over

# -----------------------------
# Helper Functions
# -----------------------------
def draw_text(surface, text, x, y, color=COLOR_TEXT):
    """Draw text on the given surface at (x, y)."""
    img = font.render(text, True, color)
    rect = img.get_rect()
    rect.topleft = (x, y)
    surface.blit(img, rect)

def random_food_position():
    """Return a (x, y) for food, snapped to the grid."""
    x_cells = SCREEN_WIDTH // CELL_SIZE
    y_cells = SCREEN_HEIGHT // CELL_SIZE
    return (random.randint(0, x_cells - 1) * CELL_SIZE,
            random.randint(0, y_cells - 1) * CELL_SIZE)

# -----------------------------
# Main Game Loop
# -----------------------------
def run_game():
    snake = [(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)]
    direction = (CELL_SIZE, 0)
    snake_length = 3
    food_pos = random_food_position()
    game_over = False

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key in (pygame.K_LEFT, pygame.K_a) and direction != (CELL_SIZE, 0):
                        direction = (-CELL_SIZE, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-CELL_SIZE, 0):
                        direction = (CELL_SIZE, 0)
                    elif event.key in (pygame.K_UP, pygame.K_w) and direction != (0, CELL_SIZE):
                        direction = (0, -CELL_SIZE)
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -CELL_SIZE):
                        direction = (0, CELL_SIZE)

                if game_over and event.key == pygame.K_r:
                    return

        if not game_over:
            head_x, head_y = snake[0]
            new_head = (head_x + direction[0], head_y + direction[1])
            snake.insert(0, new_head)

            if new_head == food_pos:
                snake_length += 1
                food_pos = random_food_position()
                beep_food.play()
            else:
                if len(snake) > snake_length:
                    snake.pop()

            if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or
                new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT or
                new_head in snake[1:]):
                game_over = True
                beep_gameover.play()

        screen.fill(COLOR_BG)
        for segment in snake:
            pygame.draw.rect(screen, COLOR_SNAKE, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, COLOR_FOOD, (food_pos[0], food_pos[1], CELL_SIZE, CELL_SIZE))

        if game_over:
            draw_text(screen, "GAME OVER", SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 - 30)
            draw_text(screen, "Press R to Restart or Q to Quit", SCREEN_WIDTH//2 - 160, SCREEN_HEIGHT//2 + 10)

        pygame.display.flip()

        if game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return
                    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

def main():
    while True:
        run_game()

if __name__ == "__main__":
    main()
