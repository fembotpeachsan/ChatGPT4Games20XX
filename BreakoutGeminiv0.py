# snake_test.py
# Meow! A simple Snake game using Pygame! Nyaa~
# No external images needed, purrfect!

import pygame
import random
import sys

# --- Constants ---
# Screen dimensions, nya!
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400

# Colors (RGB), so pretty!
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)  # Snake color, meow!
RED = (255, 0, 0)    # Food color, yummy!
BLUE = (0, 0, 255)   # Score color, purr!

# Snake properties
SNAKE_BLOCK_SIZE = 10
SNAKE_SPEED = 10 # Adjust this for game speed, maybe start slower? Nyaa~

# Frames per second, gotta go fast!
FPS = 60

# --- Initialization ---
pygame.init()
pygame.mixer.init() # For potential future meows or purrs!

# Set up the display window, purr!
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Test! Meow!")

# Clock for controlling FPS, tick-tock!
clock = pygame.time.Clock()

# Font for score, nya!
font_style = pygame.font.SysFont(None, 35) # Default system font is fine!

# --- Helper Functions ---

def draw_our_snake(snake_block_size, snake_list):
    """Draws the snake on the screen, segment by segment!"""
    for x in snake_list:
        pygame.draw.rect(screen, GREEN, [x[0], x[1], snake_block_size, snake_block_size])
        # Optional: Add a little black border for definition, purr!
        pygame.draw.rect(screen, BLACK, [x[0], x[1], snake_block_size, snake_block_size], 1)


def display_message(msg, color, y_displace=0):
    """Displays messages on the screen, like score or game over!"""
    mesg = font_style.render(msg, True, color)
    mesg_rect = mesg.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + y_displace))
    screen.blit(mesg, mesg_rect)

def display_score(score):
    """Displays the current score in the top-left corner, nya!"""
    value = font_style.render("Your Score: " + str(score), True, BLUE)
    screen.blit(value, [10, 10]) # Position it nicely

# --- Game Loop ---
def game_loop():
    """The main loop where the game happens, meow!"""
    game_over = False
    game_close = False

    # Initial snake position (center of the screen, purr!)
    x1 = SCREEN_WIDTH / 2
    y1 = SCREEN_HEIGHT / 2

    # Initial change in position (not moving yet!)
    x1_change = 0
    y1_change = 0

    # Snake body list and initial length
    snake_list = []
    length_of_snake = 1

    # Place the first food randomly, yummy!
    # Ensure food doesn't spawn outside the grid
    food_x = round(random.randrange(0, SCREEN_WIDTH - SNAKE_BLOCK_SIZE) / SNAKE_BLOCK_SIZE) * SNAKE_BLOCK_SIZE
    food_y = round(random.randrange(0, SCREEN_HEIGHT - SNAKE_BLOCK_SIZE) / SNAKE_BLOCK_SIZE) * SNAKE_BLOCK_SIZE

    # --- Main Game Cycle ---
    while not game_over:

        # --- Game Over Screen ---
        while game_close:
            screen.fill(BLACK) # Dark background for game over, sad meow :(
            display_message("You Lost! Press C-Play Again or Q-Quit", RED, -50)
            display_score(length_of_snake - 1) # Show final score
            pygame.display.update()

            # Handle input on game over screen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False # Exit inner loop
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q: # Q to quit
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c: # C to play again
                        game_loop() # Restart the game loop, purr!

        # --- Event Handling (Keyboard Input) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Clicking the close button
                game_over = True
            if event.type == pygame.KEYDOWN:
                # Prevent reversing direction immediately, sneaky snake!
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -SNAKE_BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = SNAKE_BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -SNAKE_BLOCK_SIZE
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = SNAKE_BLOCK_SIZE
                    x1_change = 0

        # --- Game Logic ---

        # Boundary collision check, don't fall off the edge, kitty!
        if x1 >= SCREEN_WIDTH or x1 < 0 or y1 >= SCREEN_HEIGHT or y1 < 0:
            game_close = True # Go to game over screen

        # Update snake position
        x1 += x1_change
        y1 += y1_change

        # --- Drawing ---
        screen.fill(BLACK) # Clear screen each frame, fresh start!

        # Draw the food, nom nom!
        pygame.draw.rect(screen, RED, [food_x, food_y, SNAKE_BLOCK_SIZE, SNAKE_BLOCK_SIZE])

        # --- Snake Body Update ---
        snake_head = []
        snake_head.append(x1)
        snake_head.append(y1)
        snake_list.append(snake_head) # Add new head position

        # Keep snake length correct, trim the tail!
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Self-collision check (don't bite your tail, silly snake!)
        # Check against all segments *except* the very last one (the head itself)
        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True # Go to game over screen

        # Draw the snake
        draw_our_snake(SNAKE_BLOCK_SIZE, snake_list)

        # Display the score
        display_score(length_of_snake - 1)

        # --- Update Display ---
        pygame.display.update() # Show everything drawn!

        # --- Food Collision ---
        if x1 == food_x and y1 == food_y:
            # Spawn new food, make sure it's not where the snake is!
            while True:
                food_x = round(random.randrange(0, SCREEN_WIDTH - SNAKE_BLOCK_SIZE) / SNAKE_BLOCK_SIZE) * SNAKE_BLOCK_SIZE
                food_y = round(random.randrange(0, SCREEN_HEIGHT - SNAKE_BLOCK_SIZE) / SNAKE_BLOCK_SIZE) * SNAKE_BLOCK_SIZE
                # Check if new food position overlaps with snake body
                is_on_snake = False
                for segment in snake_list:
                    if segment[0] == food_x and segment[1] == food_y:
                        is_on_snake = True
                        break
                if not is_on_snake:
                    break # Found a good spot, purr!

            length_of_snake += 1 # Grow longer, nya!
            # Maybe increase speed slightly here? Optional challenge!
            # global SNAKE_SPEED # Need global if changing speed
            # SNAKE_SPEED += 0.1 # Example speed increase

        # --- Frame Rate Control ---
        clock.tick(FPS) # Keep the game running at the desired speed, meow!

    # --- Quitting Pygame ---
    pygame.quit()
    sys.exit() # Clean exit, purrfect!

# --- Start the Game ---
if __name__ == "__main__":
    game_loop()
