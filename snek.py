import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400
GRID_SIZE = 20
SNAKE_SPEED = 10
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0,0,0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Snake")

# Snake initial position and direction
snake_pos = [(WIDTH // 2, HEIGHT // 2)]
snake_dir = (GRID_SIZE, 0)  # Start moving right

# Food initial position
food_pos = (random.randrange(0, WIDTH // GRID_SIZE) * GRID_SIZE, 
            random.randrange(0, HEIGHT // GRID_SIZE) * GRID_SIZE)

# Clock for controlling game speed
clock = pygame.time.Clock()

game_over = False

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        for y in range(0, HEIGHT, GRID_SIZE):
            rect = pygame.Rect(x,y,GRID_SIZE,GRID_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)

# Function to draw the snake
def draw_snake():
    for pos in snake_pos:
        pygame.draw.rect(screen, GREEN, (pos[0], pos[1], GRID_SIZE, GRID_SIZE))

# Function to draw food
def draw_food():
    pygame.draw.rect(screen, RED, (food_pos[0], food_pos[1], GRID_SIZE, GRID_SIZE))

# Game loop
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_dir != (0, GRID_SIZE):
                snake_dir = (0, -GRID_SIZE)
            elif event.key == pygame.K_DOWN and snake_dir != (0, -GRID_SIZE):
                snake_dir = (0, GRID_SIZE)
            elif event.key == pygame.K_LEFT and snake_dir != (GRID_SIZE, 0):
                snake_dir = (-GRID_SIZE, 0)
            elif event.key == pygame.K_RIGHT and snake_dir != (-GRID_SIZE, 0):
                snake_dir = (GRID_SIZE, 0)

    # Move the snake
    new_head = (snake_pos[0][0] + snake_dir[0], snake_pos[0][1] + snake_dir[1])
    snake_pos.insert(0, new_head)

    # Check if snake ate food
    if new_head == food_pos:
        food_pos = (random.randrange(0, WIDTH // GRID_SIZE) * GRID_SIZE, 
                    random.randrange(0, HEIGHT // GRID_SIZE) * GRID_SIZE)
    else:
        snake_pos.pop()

    # Check for collision with wall or self
    if (new_head[0] < 0 or new_head[0] >= WIDTH or
        new_head[1] < 0 or new_head[1] >= HEIGHT or
        new_head in snake_pos[1:]):
            game_over = True


    # Drawing
    screen.fill(WHITE)
    draw_grid()
    draw_snake()
    draw_food()
    pygame.display.flip()

    # Control game speed
    clock.tick(SNAKE_SPEED)

# Quit Pygame
pygame.quit()
