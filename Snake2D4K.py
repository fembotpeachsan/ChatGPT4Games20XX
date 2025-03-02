import pygame
import random
import numpy as np

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Personalized Snake Game with OST")

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Snake and food variables
snake_pos = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
snake_direction = 'RIGHT'
change_to = snake_direction
speed = 10  # Speed for level difficulty
food_pos = [random.randrange(1, (WIDTH//10)) * 10, random.randrange(1, (HEIGHT//10)) * 10]
food_spawn = True

# Game variables
score = 0
levels = ["Level 1", "Level 2", "BS Mario Mode", "Satellaview Mode"]
current_level = 0

# Set up fonts
font = pygame.font.SysFont('arial', 25)
score_font = pygame.font.SysFont('arial', 35)

# Function to display score
def show_score(choice, color, font, size):
    score_surface = score_font.render("Score: " + str(score), True, color)
    score_rect = score_surface.get_rect()
    screen.blit(score_surface, score_rect)

# Function to display message
def display_message(message, color, font, size):
    message_surface = font.render(message, True, color)
    message_rect = message_surface.get_rect()
    message_rect.center = (WIDTH // 2, HEIGHT // 4)
    screen.blit(message_surface, message_rect)

# Function to increase game difficulty
def increase_difficulty():
    global speed
    if score > 5:
        speed = 12  # Faster snake when score is above 5
    if score > 10:
        speed = 15  # Even faster for higher scores

# Function to generate raw sound data
def generate_sound(frequency, duration):
    sample_rate = 44100  # Samples per second
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio_data = np.sin(2 * np.pi * frequency * t) * 32767
    audio_data = audio_data.astype(np.int16)

    # Create stereo by duplicating the 1D array
    stereo_audio_data = np.column_stack((audio_data, audio_data))
    return stereo_audio_data

# Function to play sound
def play_sound(frequency, duration):
    audio_data = generate_sound(frequency, duration)
    sound = pygame.sndarray.make_sound(audio_data)
    sound.play()

# Main game loop
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

    # If two keys are pressed simultaneously, we don't change direction
    if change_to == 'UP' and snake_direction != 'DOWN':
        snake_direction = 'UP'
    if change_to == 'DOWN' and snake_direction != 'UP':
        snake_direction = 'DOWN'
    if change_to == 'LEFT' and snake_direction != 'RIGHT':
        snake_direction = 'LEFT'
    if change_to == 'RIGHT' and snake_direction != 'LEFT':
        snake_direction = 'RIGHT'

    # Move the snake
    if snake_direction == 'UP':
        snake_pos[1] -= 10
    if snake_direction == 'DOWN':
        snake_pos[1] += 10
    if snake_direction == 'LEFT':
        snake_pos[0] -= 10
    if snake_direction == 'RIGHT':
        snake_pos[0] += 10

    # Snake body growing mechanism
    snake_body.insert(0, list(snake_pos))
    if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
        score += 1
        food_spawn = False
        play_sound(440, 0.1)  # Play a sound when food is eaten (A4 note)
    else:
        snake_body.pop()

    # Food spawn
    if not food_spawn:
        food_pos = [random.randrange(1, (WIDTH//10)) * 10, random.randrange(1, (HEIGHT//10)) * 10]
    food_spawn = True

    # Draw food
    pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

    # Draw snake body
    for block in snake_body:
        pygame.draw.rect(screen, GREEN, pygame.Rect(block[0], block[1], 10, 10))

    # Check if the snake hits the boundaries or itself
    if snake_pos[0] >= WIDTH or snake_pos[0] < 0 or snake_pos[1] >= HEIGHT or snake_pos[1] < 0:
        play_sound(220, 0.2)  # Play a sound on game over (A3 note)
        run = False
    for body_part in snake_body[1:]:
        if snake_pos[0] == body_part[0] and snake_pos[1] == body_part[1]:
            play_sound(220, 0.2)  # Play sound on collision (A3 note)
            run = False

    # Increase difficulty based on score
    increase_difficulty()

    # Display score and level
    show_score(1, WHITE, font, 35)
    display_message(f"Current Level: {levels[current_level]}", BLUE, font, 25)

    # Level progression system
    if score >= 10:
        current_level = 1
    if score >= 20:
        current_level = 2
    if score >= 30:
        current_level = 3

    # Update the display
    pygame.display.update()

    # Frame Per Second (FPS) controller
    pygame.time.Clock().tick(speed)

# Quit Pygame
pygame.quit()
