import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up constants
WIDTH, HEIGHT = 640, 480
FPS = 60  # Keep 60 FPS for smooth movement
SNAKE_SIZE = 20
# SNAKE_SPEED is not used; movement is controlled by MOVE_DELAY
MOVE_DELAY = 150  # Milliseconds between moves for better control

# Set up the display
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Set up the clock
clock = pygame.time.Clock()

# Initial snake setup
snake_position = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
direction = 'RIGHT'
next_direction = direction  # Add buffer for smoother turning

# Initial food setup
food_position = [
    random.randrange(1, WIDTH // SNAKE_SIZE) * SNAKE_SIZE,
    random.randrange(1, HEIGHT // SNAKE_SIZE) * SNAKE_SIZE
]
food_spawn = True

# Score
score = 0

# Movement timer
move_timer = 0

# Fonts
pygame.font.init()
score_font = pygame.font.SysFont(None, 36)
game_over_font = pygame.font.SysFont(None, 70)

def game_over_screen(final_score):
    WIN.fill((0, 0, 0))
    game_over_text = game_over_font.render('Game Over', True, (255, 255, 255))
    score_text = score_font.render(f'Final Score: {final_score}', True, (255, 255, 255))
    
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    
    WIN.blit(game_over_text, game_over_rect)
    WIN.blit(score_text, score_rect)
    pygame.display.flip()
    
    # Wait for the player to close the window
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
    pygame.quit()
    sys.exit()

# Game loop
running = True
while running:
    dt = clock.tick(FPS)
    move_timer += dt
    
    # Process input (events)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != 'DOWN':
                next_direction = 'UP'
            elif event.key == pygame.K_DOWN and direction != 'UP':
                next_direction = 'DOWN'
            elif event.key == pygame.K_LEFT and direction != 'RIGHT':
                next_direction = 'LEFT'
            elif event.key == pygame.K_RIGHT and direction != 'LEFT':
                next_direction = 'RIGHT'
    
    # Update snake position on timer
    if move_timer >= MOVE_DELAY:
        move_timer = 0
        direction = next_direction
        
        # Update the snake position
        if direction == 'UP':
            snake_position[1] -= SNAKE_SIZE
        elif direction == 'DOWN':
            snake_position[1] += SNAKE_SIZE
        elif direction == 'LEFT':
            snake_position[0] -= SNAKE_SIZE
        elif direction == 'RIGHT':
            snake_position[0] += SNAKE_SIZE
        
        # Snake body mechanics
        snake_body.insert(0, list(snake_position))
        
        # Check if snake ate food
        if snake_position == food_position:
            score += 1
            food_spawn = False
        else:
            snake_body.pop()
    
    # Spawn new food
    if not food_spawn:
        while True:
            new_food = [
                random.randrange(1, WIDTH // SNAKE_SIZE) * SNAKE_SIZE,
                random.randrange(1, HEIGHT // SNAKE_SIZE) * SNAKE_SIZE
            ]
            if new_food not in snake_body:
                food_position = new_food
                break
        food_spawn = True
    
    # Check for collisions
    # Wall collision
    if (snake_position[0] < 0 or snake_position[0] >= WIDTH or 
        snake_position[1] < 0 or snake_position[1] >= HEIGHT):
        game_over_screen(score)
    
    # Self collision
    if snake_position in snake_body[1:]:
        game_over_screen(score)
    
    # Drawing
    WIN.fill((0, 0, 0))  # Black background
    
    # Draw snake
    for pos in snake_body:
        pygame.draw.rect(WIN, (0, 255, 0), pygame.Rect(pos[0], pos[1], SNAKE_SIZE, SNAKE_SIZE))
    
    # Draw food
    pygame.draw.rect(WIN, (255, 0, 0), pygame.Rect(food_position[0], food_position[1], SNAKE_SIZE, SNAKE_SIZE))
    
    # Draw score
    score_text = score_font.render(f'Score: {score}', True, (255, 255, 255))
    WIN.blit(score_text, (10, 10))
    
    pygame.display.flip()

# Ensure pygame quits properly if the loop is exited without game over
pygame.quit()
sys.exit()
