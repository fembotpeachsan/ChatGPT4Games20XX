import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
FPS = 10  # Frames per second

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('4KSNAKE')

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Font for score and messages
font = pygame.font.SysFont('arial', 24)

def draw_grid():
    """Optional: Draw grid lines for better visualization."""
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y))

def random_food_position(snake):
    """Generate a random position for food not occupied by the snake."""
    while True:
        position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if position not in snake:
            return position

def display_score(score):
    """Display the current score on the screen."""
    score_surface = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_surface, (10, 10))

def game_over_screen(score):
    """Display the game over screen with the final score."""
    screen.fill(BLACK)
    game_over_text = font.render('GAME OVER', True, RED)
    score_text = font.render(f'Final Score: {score}', True, WHITE)
    restart_text = font.render('Press R to Restart or Q to Quit', True, WHITE)

    # Get rectangles for centering
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))

    # Blit texts
    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    screen.blit(restart_text, restart_rect)
    pygame.display.flip()

    # Wait for player input to restart or quit
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()  # Restart the game
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def main():
    # Initialize game variables
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    snake_direction = (0, 1)  # Start moving down
    snake_length = 1
    food = random_food_position(snake)

    # Game loop variables
    game_over = False
    score = 0

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Change direction based on key presses, prevent reversing
                if event.key == pygame.K_UP and snake_direction != (0, 1):
                    snake_direction = (0, -1)
                elif event.key == pygame.K_DOWN and snake_direction != (0, -1):
                    snake_direction = (0, 1)
                elif event.key == pygame.K_LEFT and snake_direction != (1, 0):
                    snake_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and snake_direction != (-1, 0):
                    snake_direction = (1, 0)

        # Update the position of the snake
        head = snake[0]
        new_head = (head[0] + snake_direction[0], head[1] + snake_direction[1])
        snake.insert(0, new_head)

        # Check if the snake has eaten the food
        if snake[0] == food:
            score += 1
            snake_length += 1
            food = random_food_position(snake)
        else:
            snake.pop()  # Remove the tail segment if not eating

        # Check for collisions with the walls
        if not (0 <= snake[0][0] < GRID_WIDTH) or not (0 <= snake[0][1] < GRID_HEIGHT):
            game_over = True

        # Check for collisions with itself
        if snake[0] in snake[1:]:
            game_over = True

        # Clear the screen
        screen.fill(BLACK)

        # Optional: Draw grid lines
        # draw_grid()

        # Draw the food
        pygame.draw.rect(screen, RED, (food[0] * GRID_SIZE, food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Draw the snake
        for segment in snake:
            pygame.draw.rect(screen, GREEN, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Display the score
        display_score(score)

        # Update the display
        pygame.display.flip()

        # Control the frame rate
        clock.tick(FPS)

    # Game over, show the game over screen
    game_over_screen(score)

if __name__ == "__main__":
    main()
