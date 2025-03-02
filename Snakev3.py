import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Fonts
font = pygame.font.Font(None, 30)
title_font = pygame.font.Font(None, 50)

# Function to display text
def display_text(text, color, font_obj, x, y):
    text_surface = font_obj.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)

# Main Menu
def main_menu():
    while True:
        screen.fill(BLACK)
        display_text("Snake Game", GREEN, title_font, WIDTH // 2, HEIGHT // 3)
        display_text("Enter your name:", WHITE, font, WIDTH // 2, HEIGHT // 2)

        pygame.display.update()

        name = ""
        input_active = True
        while input_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode

            screen.fill(BLACK)
            display_text("Snake Game", GREEN, title_font, WIDTH // 2, HEIGHT // 3)
            display_text("Enter your name:", WHITE, font, WIDTH // 2, HEIGHT // 2 -30)
            display_text(name, WHITE, font, WIDTH // 2, HEIGHT // 2 )
            display_text("Press Enter to Start", WHITE, font, WIDTH //2, HEIGHT // 2 + 60)
            pygame.display.update()


        if len(name) > 0:
            return name


# Snake game logic
def game_loop(player_name):
    # Snake initial parameters
    snake_pos = [[100, 50], [90, 50], [80, 50]]
    snake_direction = "RIGHT"
    change_to = snake_direction

    # Food
    food_pos = [random.randrange(1, (WIDTH // 10)) * 10, random.randrange(1, (HEIGHT // 10)) * 10]
    food_spawn = True

    # Score
    score = 0

    # Game Over flag
    game_over = False

    clock = pygame.time.Clock()

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            # Keypresses for movement
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    change_to = "UP"
                if event.key == pygame.K_DOWN:
                    change_to = "DOWN"
                if event.key == pygame.K_LEFT:
                    change_to = "LEFT"
                if event.key == pygame.K_RIGHT:
                    change_to = "RIGHT"

        # If two keys are pressed simultaneously (Prevent 180 degree turns)
        if change_to == "UP" and snake_direction != "DOWN":
            snake_direction = "UP"
        if change_to == "DOWN" and snake_direction != "UP":
            snake_direction = "DOWN"
        if change_to == "LEFT" and snake_direction != "RIGHT":
            snake_direction = "LEFT"
        if change_to == "RIGHT" and snake_direction != "LEFT":
            snake_direction = "RIGHT"

        # Move the snake
        if snake_direction == "UP":
            new_head = [snake_pos[0][0], snake_pos[0][1] - 10]
        if snake_direction == "DOWN":
            new_head = [snake_pos[0][0], snake_pos[0][1] + 10]
        if snake_direction == "LEFT":
            new_head = [snake_pos[0][0] - 10, snake_pos[0][1]]
        if snake_direction == "RIGHT":
            new_head = [snake_pos[0][0] + 10, snake_pos[0][1]]

        snake_pos.insert(0, new_head)

        # Snake eating food
        if snake_pos[0] == food_pos:
            food_spawn = False
            score += 1
        else:
            snake_pos.pop()

        # Food re-spawning
        if not food_spawn:
            food_pos = [random.randrange(1, (WIDTH // 10)) * 10, random.randrange(1, (HEIGHT // 10)) * 10]
        food_spawn = True

        # Game Over conditions
        if snake_pos[0][0] >= WIDTH or snake_pos[0][0] < 0 or snake_pos[0][1] >= HEIGHT or snake_pos[0][1] < 0:
            game_over = True
        for block in snake_pos[1:]:
            if snake_pos[0] == block:
                game_over = True

        # Rendering
        screen.fill(BLACK)

        for pos in snake_pos:
            pygame.draw.rect(screen, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))

        pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

        # Score display
        display_text(f"Score: {score}", WHITE, font, WIDTH // 2, 20)
        display_text(f"Player: {player_name}", WHITE, font, WIDTH // 2, 50)

        pygame.display.update()

        clock.tick(15)  # Control game speed (snake movement speed)

    # Game Over screen
    screen.fill(BLACK)
    display_text(f"Game Over, {player_name}!", RED, title_font, WIDTH // 2, HEIGHT // 3)
    display_text(f"Final Score: {score}", WHITE, font, WIDTH // 2, HEIGHT // 2)
    display_text("Press Q to Quit or C to Play Again", WHITE, font, WIDTH // 2, HEIGHT // 1.5)

    pygame.display.update()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_c:
                    game_loop(player_name)

# Run the game
def run_game():
    player_name = main_menu()
    if player_name:
        game_loop(player_name)

run_game()
