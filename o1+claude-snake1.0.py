import pygame
import random
import math
import numpy

# Initialize Pygame
pygame.init()

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red   = (255, 0, 0)
green = (0, 255, 0)

# Game settings
display_width  = 800
display_height = 600
block_size     = 10
snake_speed    = 15

# Set up display
game_display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Snake with Synthesized Sounds!")

# Font for text
font_style = pygame.font.SysFont(None, 30)

# Sound synthesis
def synthesize_sound(duration, frequency):
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    buffer = numpy.zeros((num_samples, 2), dtype=numpy.int16)
    max_int16 = 2**15 - 1
    for i in range(num_samples):
        t = float(i) / sample_rate
        value = int(max_int16 * math.sin(2 * math.pi * frequency * t))
        buffer[i] = [value, value]
    sound = pygame.sndarray.make_sound(buffer)
    return sound

# Create your sounds
eat_sound       = synthesize_sound(0.5, 880)   # 0.5-second sound at 880 Hz
game_over_sound = synthesize_sound(1.0, 440)   # 1-second sound at 440 Hz

# Helper functions
def draw_snake(block_size, snake_list):
    """Draws each segment of the snake."""
    for x, y in snake_list:
        pygame.draw.rect(game_display, green, [x, y, block_size, block_size])

def show_message(msg, color, x_offset=0, y_offset=0):
    """Displays a message at roughly the center of the screen."""
    text_surface = font_style.render(msg, True, color)
    text_rect = text_surface.get_rect()
    # Position at center + offsets
    text_rect.center = (display_width // 2 + x_offset, display_height // 2 + y_offset)
    game_display.blit(text_surface, text_rect)

def show_score(score):
    """Displays the score in the top-left corner."""
    value = font_style.render("Score: " + str(score), True, black)
    game_display.blit(value, [0, 0])

def game_loop():
    # Initial position for the snake
    x1 = display_width // 2
    y1 = display_height // 2

    # Movement deltas
    x1_change = 0
    y1_change = 0

    # Snake body tracking
    snake_list = []
    length_of_snake = 1

    # Generate initial food position
    food_x = round(random.randrange(0, display_width - block_size) / 10.0) * 10.0
    food_y = round(random.randrange(0, display_height - block_size) / 10.0) * 10.0

    clock = pygame.time.Clock()

    game_over = False
    game_close = False

    while not game_over:
        while game_close:
            # Clear screen
            game_display.fill(white)
            show_message("You Lost! Press C-Play Again or Q-Quit", red, 0, -20)
            show_score(length_of_snake - 1)
            pygame.display.update()

            # Listen for user input to continue or quit
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    elif event.key == pygame.K_c:
                        game_loop()  # restart the game
                elif event.type == pygame.QUIT:
                    game_over = True
                    game_close = False

        # Main event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -block_size
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = block_size
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -block_size
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = block_size
                    x1_change = 0

        # If snake goes out of bounds -> game over
        if x1 >= display_width or x1 < 0 or y1 >= display_height or y1 < 0:
            game_over_sound.play()
            game_close = True

        # Update snake position
        x1 += x1_change
        y1 += y1_change
        game_display.fill(white)

        # Draw food
        pygame.draw.rect(game_display, red, [food_x, food_y, block_size, block_size])

        # Snake movement and growth
        snake_head = (x1, y1)
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Check if snake bumps into itself
        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_over_sound.play()
                game_close = True

        draw_snake(block_size, snake_list)
        show_score(length_of_snake - 1)

        pygame.display.update()

        # Check if snake eats food
        if x1 == food_x and y1 == food_y:
            eat_sound.play()
            food_x = round(random.randrange(0, display_width - block_size) / 10.0) * 10.0
            food_y = round(random.randrange(0, display_height - block_size) / 10.0) * 10.0
            length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

# Run the game
game_loop()
