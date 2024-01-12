import pygame
import random
import numpy as np

# Function to initialize Pygame and its Mixer
def initialize_pygame():
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Function to generate and play C64-style square wave tone
def generate_and_play_c64_style_tone(frequency, duration):
    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = np.sign(np.sin(2 * np.pi * frequency * t))
    stereo_wave = np.vstack((wave, wave)).T  # Create a stereo sound
    contiguous_wave = np.ascontiguousarray(stereo_wave, dtype=np.int16)
    sound = pygame.sndarray.make_sound(contiguous_wave * 32767)
    sound.play()

# Function to display the main menu
def main_menu(win, font, width, height):
    menu_run = True
    while menu_run:
        win.fill(black)
        menu_text = font.render("SNAKE - PRESS Z OR ENTER", True, white)
        win.blit(menu_text, (width // 2 - menu_text.get_width() // 2, height // 2 - menu_text.get_height() // 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z or event.key == pygame.K_RETURN:
                    return True

# Initialize Pygame and Mixer
initialize_pygame()

# Game window dimensions and setup
width, height = 640, 480
win = pygame.display.set_mode((width, height))

# Color definitions
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)

# Snake properties initialization
snake_pos = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
snake_speed = 15
direction = 'RIGHT'
change_to = direction

# Food properties initialization
food_pos = [random.randrange(1, (width // 10)) * 10, random.randrange(1, (height // 10)) * 10]
food_spawn = True

# Score initialization
score = 0

# Font setup
font = pygame.font.SysFont('arial', 25)

# Display the main menu
if not main_menu(win, font, width, height):
    pygame.quit()
    quit()

# Game loop
run = True
clock = pygame.time.Clock()
while run:
    # Handle key events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                change_to = 'UP'
            elif event.key == pygame.K_DOWN:
                change_to = 'DOWN'
            elif event.key == pygame.K_LEFT:
                change_to = 'LEFT'
            elif event.key == pygame.K_RIGHT:
                change_to = 'RIGHT'

    # Prevent opposite direction change
    if change_to == 'UP' and direction != 'DOWN':
        direction = 'UP'
    elif change_to == 'DOWN' and direction != 'UP':
        direction = 'DOWN'
    elif change_to == 'LEFT' and direction != 'RIGHT':
        direction = 'LEFT'
    elif change_to == 'RIGHT' and direction != 'LEFT':
        direction = 'RIGHT'

    # Move the snake
    if direction == 'UP':
        snake_pos[1] -= 10
    elif direction == 'DOWN':
        snake_pos[1] += 10
    elif direction == 'LEFT':
        snake_pos[0] -= 10
    elif direction == 'RIGHT':
        snake_pos[0] += 10

    # Snake body growth mechanism
    snake_body.insert(0, list(snake_pos))
    if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
        score += 1
        food_spawn = False
        generate_and_play_c64_style_tone(440, 0.1)  # Play a C64-style tone at 440 Hz for 0.1 seconds
    else:
        snake_body.pop()

    # Spawn food
    if not food_spawn:
        food_pos = [random.randrange(1, (width // 10)) * 10, random.randrange(1, (height // 10)) * 10]
    food_spawn = True

    # Game Over conditions
    if snake_pos[0] < 0 or snake_pos[0] > width - 10 or snake_pos[1] < 0 or snake_pos[1] > height - 10:
        run = False
    for block in snake_body[1:]:
        if block == snake_pos:
            run = False

    # Drawing the snake, food, and score
    win.fill(black)
    for pos in snake_body:
        pygame.draw.rect(win, green, pygame.Rect(pos[0], pos[1], 10, 10))
    pygame.draw.rect(win, red, pygame.Rect(food_pos[0], food_pos[1], 10, 10))
    score_text = font.render("Score: " + str(score), True, white)
    win.blit(score_text, [0, 0])

    # Update display and set refresh rate to 60 FPS
    pygame.display.update()
    clock.tick(60)

# Quit the game when loop ends
pygame.quit()
import pygame
import random
import numpy as np

# Function to initialize Pygame and its Mixer
def initialize_pygame():
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Function to generate and play C64-style square wave tone
def generate_and_play_c64_style_tone(frequency, duration):
    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = np.sign(np.sin(2 * np.pi * frequency * t))
    stereo_wave = np.vstack((wave, wave)).T  # Create a stereo sound
    contiguous_wave = np.ascontiguousarray(stereo_wave, dtype=np.int16)
    sound = pygame.sndarray.make_sound(contiguous_wave * 32767)
    sound.play()

# Function to display the main menu
def main_menu(win, font, width, height):
    menu_run = True
    while menu_run:
        win.fill(black)
        menu_text = font.render("SNAKE - PRESS Z OR ENTER", True, white)
        win.blit(menu_text, (width // 2 - menu_text.get_width() // 2, height // 2 - menu_text.get_height() // 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z or event.key == pygame.K_RETURN:
                    return True

# Initialize Pygame and Mixer
initialize_pygame()

# Game window dimensions and setup
width, height = 640, 480
win = pygame.display.set_mode((width, height))

# Color definitions
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)

# Snake properties initialization
snake_pos = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
snake_speed = 15
direction = 'RIGHT'
change_to = direction

# Food properties initialization
food_pos = [random.randrange(1, (width // 10)) * 10, random.randrange(1, (height // 10)) * 10]
food_spawn = True

# Score initialization
score = 0

# Font setup
font = pygame.font.SysFont('arial', 25)

# Display the main menu
if not main_menu(win, font, width, height):
    pygame.quit()
    quit()

# Game loop
run = True
clock = pygame.time.Clock()
while run:
    # Handle key events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                change_to = 'UP'
            elif event.key == pygame.K_DOWN:
                change_to = 'DOWN'
            elif event.key == pygame.K_LEFT:
                change_to = 'LEFT'
            elif event.key == pygame.K_RIGHT:
                change_to = 'RIGHT'

    # Prevent opposite direction change
    if change_to == 'UP' and direction != 'DOWN':
        direction = 'UP'
    elif change_to == 'DOWN' and direction != 'UP':
        direction = 'DOWN'
    elif change_to == 'LEFT' and direction != 'RIGHT':
        direction = 'LEFT'
    elif change_to == 'RIGHT' and direction != 'LEFT':
        direction = 'RIGHT'

    # Move the snake
    if direction == 'UP':
        snake_pos[1] -= 10
    elif direction == 'DOWN':
        snake_pos[1] += 10
    elif direction == 'LEFT':
        snake_pos[0] -= 10
    elif direction == 'RIGHT':
        snake_pos[0] += 10

    # Snake body growth mechanism
    snake_body.insert(0, list(snake_pos))
    if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
        score += 1
        food_spawn = False
        generate_and_play_c64_style_tone(440, 0.1)  # Play a C64-style tone at 440 Hz for 0.1 seconds
    else:
        snake_body.pop()

    # Spawn food
    if not food_spawn:
        food_pos = [random.randrange(1, (width // 10)) * 10, random.randrange(1, (height // 10)) * 10]
    food_spawn = True

    # Game Over conditions
    if snake_pos[0] < 0 or snake_pos[0] > width - 10 or snake_pos[1] < 0 or snake_pos[1] > height - 10:
        run = False
    for block in snake_body[1:]:
        if block == snake_pos:
            run = False

    # Drawing the snake, food, and score
    win.fill(black)
    for pos in snake_body:
        pygame.draw.rect(win, green, pygame.Rect(pos[0], pos[1], 10, 10))
    pygame.draw.rect(win, red, pygame.Rect(food_pos[0], food_pos[1], 10, 10))
    score_text = font.render("Score: " + str(score), True, white)
    win.blit(score_text, [0, 0])

    # Update display and set refresh rate to [20] FPS
    pygame.display.update()
    clock.tick(20)

# Quit the game when loop ends
pygame.quit()
