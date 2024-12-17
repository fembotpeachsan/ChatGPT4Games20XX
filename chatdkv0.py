

from turtle import write


# You said:
# write a simple donkey kong game in pygame no pngs
import pygame



 
import pygame
from array import array
import math

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Set screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("NX2 Augmenter Musicdisk - Team Hummer Tribute")

# Colors
black = (0, 0, 0)
green = (0, 128, 0)
light_green = (0, 255, 0)
retro_yellow = (255, 255, 0)

# Fonts
font_title = pygame.font.Font(None, 48)
font_text = pygame.font.Font(None, 24)
font_sound = pygame.font.Font(None, 36)

# Text elements
title = font_title.render("NX2 Augmenter Musicdisk", True, retro_yellow)
sub_title = font_text.render("Tribute to Team Hummer", True, light_green)
instructions = font_text.render("D-PAD LEFT/RIGHT: Browse Sounds | SPACE: Play Sound", True, green)

# Positions
title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 40))
sub_title_rect = sub_title.get_rect(center=(SCREEN_WIDTH // 2, 80))
instructions_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, 520))

# Define a function to generate beep sounds with varying frequencies
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)) for i in range(samples)]
    sound = pygame.mixer.Sound(buffer=array('h', wave))
    sound.set_volume(0.2)
    return sound

# Create a list of sound tuples (name, sound object)
sounds = [
    ("SND_1 - A4", generate_beep_sound(440, 0.5)),
    ("SND_2 - C5", generate_beep_sound(523.25, 0.5)),
    ("SND_3 - D5", generate_beep_sound(587.33, 0.5)),
    ("SND_4 - E5", generate_beep_sound(659.25, 0.5)),
    ("NES_SQ1", generate_beep_sound(440, 0.2)),
    ("NES_SQ2", generate_beep_sound(523.25, 0.2)),
    ("FAM_CLONE_SQ1", generate_beep_sound(660, 0.2)),
    ("GB_SQ1", generate_beep_sound(880, 0.2)),
]
current_sound_index = 0  # Index of the currently selected sound

# Function for rendering retro visualizer
def draw_visualizer(surface, sound_name, x, y, width, height):
    pygame.draw.rect(surface, light_green, (x, y, width, height), 2)
    text = font_text.render(sound_name, True, retro_yellow)
    text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
    surface.blit(text, text_rect)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Play the current sound
                print(f"Playing sound: {sounds[current_sound_index][0]}")  # Debug statement
                sounds[current_sound_index][1].play()
            elif event.key == pygame.K_RIGHT:
                # Cycle to the next sound
                current_sound_index = (current_sound_index + 1) % len(sounds)
                print(f"Selected sound: {sounds[current_sound_index][0]}")  # Debug statement
            elif event.key == pygame.K_LEFT:
                # Cycle to the previous sound
                current_sound_index = (current_sound_index - 1) % len(sounds)
                print(f"Selected sound: {sounds[current_sound_index][0]}")  # Debug statement

    # Fill background
    screen.fill(black)

    # Draw text elements
    screen.blit(title, title_rect)
    screen.blit(sub_title, sub_title_rect)
    screen.blit(instructions, instructions_rect)

    # Draw visualizer for the current sound
    draw_visualizer(screen, sounds[current_sound_index][0], 200, 250, 400, 100)

    pygame.display.flip()
    pygame.time.wait(30)

pygame.quit( ) 
 
import pygame
import random
import sys
import math
from array import array

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RETRO_YELLOW = (255, 255, 0)
LIGHT_GREEN = (0, 255, 0)

# Game settings
FPS = 60
PLAYER_SPEED = 5
BARREL_SPEED = 4

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Donkey Kong Clone with Music Disk")

# Fonts
font_title = pygame.font.Font(None, 48)
font_text = pygame.font.Font(None, 24)

# Text elements
title = font_title.render("NX2 Augmenter Musicdisk", True, RETRO_YELLOW)
sub_title = font_text.render("Tribute to Team Hummer", True, LIGHT_GREEN)
instructions = font_text.render("D-PAD LEFT/RIGHT: Browse Sounds | SPACE: Play Sound", True, GREEN)

# Positions
title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 40))
sub_title_rect = sub_title.get_rect(center=(SCREEN_WIDTH // 2, 80))
instructions_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, 360))

# Player properties
player = pygame.Rect(50, SCREEN_HEIGHT - 40, 30, 30)

# Platforms
platforms = [
    pygame.Rect(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20),
    pygame.Rect(50, 300, 500, 20),
    pygame.Rect(0, 200, 400, 20),
    pygame.Rect(200, 100, 400, 20)
]

# Ladders
ladders = [
    pygame.Rect(100, 300, 20, 100),
    pygame.Rect(350, 200, 20, 100)
]

# Barrels
barrels = []
BARREL_INTERVAL = 2000  # Time between barrel spawns (ms)
last_barrel_time = pygame.time.get_ticks()

# Goal
goal = pygame.Rect(550, 80, 30, 20)

# Sounds
barrel_sound = generate_beep_sound(330, 0.5)
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)) for i in range(samples)]
    sound = pygame.mixer.Sound(buffer=array('h', wave))
    sound.set_volume(0.2)
    return sound

sounds = [
    ("SND_1 - A4", generate_beep_sound(440, 0.5)),
    ("SND_2 - C5", generate_beep_sound(523.25, 0.5)),
    ("SND_3 - D5", generate_beep_sound(587.33, 0.5)),
    ("SND_4 - E5", generate_beep_sound(659.25, 0.5))
]
current_sound_index = 0

# Game loop flag
running = True

# Clock object to control the frame rate
clock = pygame.time.Clock()

# Gravity
gravity = 1
player_velocity_y = 0
on_ground = False

# Function for rendering retro visualizer
def draw_visualizer(surface, sound_name, x, y, width, height):
    pygame.draw.rect(surface, LIGHT_GREEN, (x, y, width, height), 2)
    text = font_text.render(sound_name, True, RETRO_YELLOW)
    text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
    surface.blit(text, text_rect)

while running:
    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                sounds[current_sound_index][1].play()
            elif event.key == pygame.K_RIGHT:
                current_sound_index = (current_sound_index + 1) % len(sounds)
            elif event.key == pygame.K_LEFT:
                current_sound_index = (current_sound_index - 1) % len(sounds)

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        player.x += PLAYER_SPEED

    # Check for climbing
    climbing = False
    for ladder in ladders:
        if player.colliderect(ladder):
            climbing = True
            if keys[pygame.K_UP]:
                player.y -= PLAYER_SPEED
            if keys[pygame.K_DOWN]:
                player.y += PLAYER_SPEED

    # Apply gravity if not climbing
    if not climbing:
        player_velocity_y += gravity
    else:
        player_velocity_y = 0

    # Move player vertically
    player.y += player_velocity_y

    # Check collision with platforms
    on_ground = False
    for platform in platforms:
        if player.colliderect(platform) and player_velocity_y > 0:
            player.bottom = platform.top
            player_velocity_y = 0
            on_ground = True

    # Keep player within screen bounds
    player.x = max(0, min(SCREEN_WIDTH - player.width, player.x))
    player.y = max(0, min(SCREEN_HEIGHT - player.height, player.y))

    # Spawn barrels
    current_time = pygame.time.get_ticks()
    if current_time - last_barrel_time > BARREL_INTERVAL:
        barrels.append(pygame.Rect(550, 100, 20, 20))
        last_barrel_time = current_time

    # Move barrels
    for barrel in barrels[:]:
        barrel.x -= BARREL_SPEED
        if barrel.x < 0:
            barrels.remove(barrel)

    # Check for collisions with barrels
    for barrel in barrels:
        if player.colliderect(barrel):
            print("Game Over!")
            running = False

    # Check for reaching the goal
    if player.colliderect(goal):
        print("You Win!")
        running = False

    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(screen, BLUE, platform)

    # Draw ladders
    for ladder in ladders:
        pygame.draw.rect(screen, GREEN, ladder)

    # Draw barrels
    for barrel in barrels:
        pygame.draw.rect(screen, RED, barrel)

    # Draw player
    pygame.draw.rect(screen, WHITE, player)

    # Draw goal
    pygame.draw.rect(screen, GREEN, goal)

    # Draw text elements
    screen.blit(title, title_rect)
    screen.blit(sub_title, sub_title_rect)
    screen.blit(instructions, instructions_rect)

    # Draw visualizer for the current sound
    draw_visualizer(screen, sounds[current_sound_index][0], 100, 360, 400, 50)

    # Update display
    pygame.display.flip()

    # Cap the frame rate
clock.tick(FPS)




 
import pygame
import random
import sys
import math
from array import array

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RETRO_YELLOW = (255, 255, 0)
LIGHT_GREEN = (0, 255, 0)

# Game settings
FPS = 60
PLAYER_SPEED = 5
BARREL_SPEED = 4

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Donkey Kong Clone with Music Disk")

# Fonts
font_text = pygame.font.Font(None, 24)

# Player properties
player = pygame.Rect(50, SCREEN_HEIGHT - 40, 30, 30)

# Platforms
platforms = [
    pygame.Rect(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20),
    pygame.Rect(50, 300, 500, 20),
    pygame.Rect(0, 200, 400, 20),
    pygame.Rect(200, 100, 400, 20)
]

# Ladders
ladders = [
    pygame.Rect(100, 300, 20, 100),
    pygame.Rect(350, 200, 20, 100)
]

# Barrels
barrels = []
BARREL_INTERVAL = 2000  # Time between barrel spawns (ms)
last_barrel_time = pygame.time.get_ticks()

# Goal
goal = pygame.Rect(550, 80, 30, 20)

# Sounds
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)) for i in range(samples)]
    sound = pygame.mixer.Sound(buffer=array('h', wave))
    sound.set_volume(0.2)
    return sound

sounds = [
    ("SND_1 - A4", generate_beep_sound(440, 0.5)),
    ("SND_2 - C5", generate_beep_sound(523.25, 0.5)),
    ("SND_3 - D5", generate_beep_sound(587.33, 0.5)),
    ("SND_4 - E5", generate_beep_sound(659.25, 0.5))
]
current_sound_index = 0

# Game loop flag
running = True

# Clock object to control the frame rate
clock = pygame.time.Clock()

# Gravity
gravity = 1
player_velocity_y = 0
on_ground = False

# Function for rendering retro visualizer
def draw_visualizer(surface, sound_name, x, y, width, height):
    pygame.draw.rect(surface, LIGHT_GREEN, (x, y, width, height), 2)
    text = font_text.render(sound_name, True, RETRO_YELLOW)
    text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
    surface.blit(text, text_rect)

while running:
    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                sounds[current_sound_index][1].play()
            elif event.key == pygame.K_RIGHT:
                current_sound_index = (current_sound_index + 1) % len(sounds)
            elif event.key == pygame.K_LEFT:
                current_sound_index = (current_sound_index - 1) % len(sounds)

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        player.x += PLAYER_SPEED

    # Check for climbing
    climbing = False
    for ladder in ladders:
        if player.colliderect(ladder):
            climbing = True
            if keys[pygame.K_UP]:
                player.y -= PLAYER_SPEED
            if keys[pygame.K_DOWN]:
                player.y += PLAYER_SPEED

    # Apply gravity if not climbing
    if not climbing:
        player_velocity_y += gravity
    else:
        player_velocity_y = 0

    # Move player vertically
    player.y += player_velocity_y

    # Check collision with platforms
    on_ground = False
    for platform in platforms:
        if player.colliderect(platform) and player_velocity_y > 0:
            player.bottom = platform.top
            player_velocity_y = 0
            on_ground = True

    # Keep player within screen bounds
    player.x = max(0, min(SCREEN_WIDTH - player.width, player.x))
    player.y = max(0, min(SCREEN_HEIGHT - player.height, player.y))

    # Spawn barrels
    current_time = pygame.time.get_ticks()
    if current_time - last_barrel_time > BARREL_INTERVAL:
        barrels.append(pygame.Rect(550, 100, 20, 20))
        last_barrel_time = current_time

    # Move barrels
    for barrel in barrels[:]:
        barrel.x -= BARREL_SPEED
        if barrel.x < 0:
            barrels.remove(barrel)

    # Check for collisions with barrels
    for barrel in barrels:
        if player.colliderect(barrel):
            print("Game Over!")
            running = False

    # Check for reaching the goal
    if player.colliderect(goal):
        print("You Win!")
        running = False

    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(screen, BLUE, platform)

    # Draw ladders
    for ladder in ladders:
        pygame.draw.rect(screen, GREEN, ladder)

    # Draw barrels
    for barrel in barrels:
        pygame.draw.rect(screen, RED, barrel)

    # Draw player
    pygame.draw.rect(screen, WHITE, player)

    # Draw goal
    pygame.draw.rect(screen, GREEN, goal)

    # Draw visualizer for the current sound
    draw_visualizer(screen, sounds[current_sound_index][0], 100, 360, 400, 50)

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS) # This will make the game run at 60 FPS




 







 
import pygame
last_barrel_time = current_time

# Move barrels
for barrel in barrels[:]:
    barrel.x -= BARREL_SPEED
    barrel_sound.play()
    if barrel.x < 0:
        barrels.remove(barrel)

# Check for collisions with barrels
for barrel in barrels:
    if player.colliderect(barrel):
        print("Game Over!")
        running = False

# Check for reaching the goal
if player.colliderect(goal):
    print("You Win!")
    running = False

# Draw platforms
for platform in platforms:
    pygame.draw.rect(screen, BLUE, platform)

# Draw ladders
for ladder in ladders:
    pygame.draw.rect(screen, GREEN, ladder)

# Draw barrels
for barrel in barrels:
    pygame.draw.rect(screen, RED, barrel)

# Draw player
pygame.draw.rect(screen, WHITE, player)

# Draw goal
pygame.draw.rect(screen, GREEN, goal)

# Update display
pygame.display.flip()

# Cap the frame rate
clock.tick(FPS)

 
