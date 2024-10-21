import pygame
import random

# Initialize Pygame
pygame.init()

# Set the dimensions of the game window
window_width = 600
window_height = 400

# Create the game window
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Snake Game')

# Set the dimensions of the snake
snake_width = 10
snake_height = 10

# Set the initial position of the snake
snake_x = window_width // 2
snake_y = window_height // 2

# Set the speed of the snake
speed = snake_width  # Move one snake width per frame

# Initialize the direction of the snake
direction = 'RIGHT'

# Set the dimensions of the food
food_width = 10
food_height = 10

# Set the initial position of the food
food_x = random.randrange(0, window_width - food_width, snake_width)
food_y = random.randrange(0, window_height - food_height, snake_height)

# Set the initial score
score = 0

# Set up the game clock
clock = pygame.time.Clock()
fps = 15  # Frames per second

# Initialize the snake's body
snake_body = []
snake_length = 1

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Handle key presses
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and direction != 'RIGHT':
                direction = 'LEFT'
            if event.key == pygame.K_RIGHT and direction != 'LEFT':
                direction = 'RIGHT'
            if event.key == pygame.K_UP and direction != 'DOWN':
                direction = 'UP'
            if event.key == pygame.K_DOWN and direction != 'UP':
                direction = 'DOWN'

    # Move the snake
    if direction == 'LEFT':
        snake_x -= speed
    if direction == 'RIGHT':
        snake_x += speed
    if direction == 'UP':
        snake_y -= speed
    if direction == 'DOWN':
        snake_y += speed

    # Check for wall collisions
    if snake_x < 0 or snake_x >= window_width or snake_y < 0 or snake_y >= window_height:
        running = False  # Game over

    # Check if the snake has eaten the food
    if snake_x == food_x and snake_y == food_y:
        score += 1
        snake_length += 1
        food_x = random.randrange(0, window_width - food_width, snake_width)
        food_y = random.randrange(0, window_height - food_height, snake_height)

    # Update the snake's body
    snake_head = [snake_x, snake_y]
    snake_body.append(snake_head)
    if len(snake_body) > snake_length:
        del snake_body[0]

    # Check for self-collision
    for segment in snake_body[:-1]:
        if segment == snake_head:
            running = False  # Game over

    # Clear the screen
    window.fill((0, 0, 0))

    # Draw the snake
    for segment in snake_body:
        pygame.draw.rect(window, (0, 255, 0), [segment[0], segment[1], snake_width, snake_height])

    # Draw the food
    pygame.draw.rect(window, (255, 0, 0), [food_x, food_y, food_width, food_height])

    # Update the game display
    pygame.display.update()

    # Control the frame rate
    clock.tick(fps)

# Quit Pygame
pygame.quit()
