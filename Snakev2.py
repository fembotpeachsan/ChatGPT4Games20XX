import pygame
import random

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Personalized Snake Game")

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Set up fonts
font = pygame.font.SysFont('arial', 25)
title_font = pygame.font.SysFont('arial', 40)

# Function to display text
def display_text(message, color, font, x, y):
    text_surface = font.render(message, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Main menu
def main_menu():
    while True:
        screen.fill(BLACK)
        display_text("Welcome to Snake!", WHITE, title_font, WIDTH // 2, HEIGHT // 4)
        display_text("Enter your name:", WHITE, font, WIDTH // 2, HEIGHT // 2 - 50)
        
        name = ""
        typing = True
        while typing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        typing = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode
            
            screen.fill(BLACK)
            display_text("Welcome to Snake!", WHITE, title_font, WIDTH // 2, HEIGHT // 4)
            display_text("Enter your name:", WHITE, font, WIDTH // 2, HEIGHT // 2 - 50)
            display_text(name, GREEN, font, WIDTH // 2, HEIGHT // 2)
            display_text("Press Enter to Start", WHITE, font, WIDTH // 2, HEIGHT // 2 + 50)
            pygame.display.update()
        
        if name:
            return name

# Game over screen with Y/N prompt
def game_over_screen(score, name):
    while True:
        screen.fill(BLACK)
        display_text(f"Game Over, {name}!", RED, title_font, WIDTH // 2, HEIGHT // 4)
        display_text(f"Score: {score}", WHITE, font, WIDTH // 2, HEIGHT // 2 - 50)
        display_text("Play again? (Y/N)", WHITE, font, WIDTH // 2, HEIGHT // 2 + 50)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                if event.key == pygame.K_n:
                    return False

# Main game function
def play_game(name):
    snake_pos = [100, 50]
    snake_body = [[100, 50], [90, 50], [80, 50]]
    snake_direction = 'RIGHT'
    change_to = snake_direction
    speed = 10
    food_pos = [random.randrange(1, (WIDTH//10)) * 10, random.randrange(1, (HEIGHT//10)) * 10]
    food_spawn = True
    score = 0

    run = True
    while run:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    change_to = 'UP'
                if event.key == pygame.K_DOWN:
                    change_to = 'DOWN'
                if event.key == pygame.K_LEFT:
                    change_to = 'LEFT'
                if event.key == pygame.K_RIGHT:
                    change_to = 'RIGHT'

        # Snake direction logic
        if change_to == 'UP' and snake_direction != 'DOWN':
            snake_direction = 'UP'
        if change_to == 'DOWN' and snake_direction != 'UP':
            snake_direction = 'DOWN'
        if change_to == 'LEFT' and snake_direction != 'RIGHT':
            snake_direction = 'LEFT'
        if change_to == 'RIGHT' and snake_direction != 'LEFT':
            snake_direction = 'RIGHT'

        # Move snake
        if snake_direction == 'UP':
            snake_pos[1] -= 10
        if snake_direction == 'DOWN':
            snake_pos[1] += 10
        if snake_direction == 'LEFT':
            snake_pos[0] -= 10
        if snake_direction == 'RIGHT':
            snake_pos[0] += 10

        # Snake body growing
        snake_body.insert(0, list(snake_pos))
        if snake_pos == food_pos:
            score += 1
            food_spawn = False
        else:
            snake_body.pop()

        # Food spawn
        if not food_spawn:
            food_pos = [random.randrange(1, (WIDTH//10)) * 10, random.randrange(1, (HEIGHT//10)) * 10]
        food_spawn = True

        # Draw elements
        pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0], food_pos[1], 10, 10))
        for block in snake_body:
            pygame.draw.rect(screen, GREEN, pygame.Rect(block[0], block[1], 10, 10))
        
        # Collision checks
        if (snake_pos[0] >= WIDTH or snake_pos[0] < 0 or 
            snake_pos[1] >= HEIGHT or snake_pos[1] < 0 or
            snake_pos in snake_body[1:]):
            run = False

        # Display score
        display_text(f"{name}'s Score: {score}", WHITE, font, WIDTH // 2, 20)

        pygame.display.update()
        pygame.time.Clock().tick(speed)

    return score

# Main loop
while True:
    name = main_menu()
    if name is None:
        break
    
    score = play_game(name)
    if not game_over_screen(score, name):
        break

pygame.quit()
