import pygame
import numpy as np
import sys
import random

# -------------------------------
# Initialize Pygame and Mixer
# -------------------------------
pygame.init()

# Parameters
SAMPLE_RATE = 44100  # Hertz

# Initialize Pygame mixer with desired parameters
pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, 512)  # Frequency, size, channels, buffer
pygame.mixer.init()

# -------------------------------
# Screen Configuration
# -------------------------------
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game')

# -------------------------------
# Colors
# -------------------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# -------------------------------
# Clock and Game Properties
# -------------------------------
clock = pygame.time.Clock()
SNAKE_BLOCK = 10
SNAKE_SPEED = 15

# -------------------------------
# Fonts
# -------------------------------
font_small = pygame.font.SysFont('arial', 25)
font_large = pygame.font.SysFont('arial', 50)

# -------------------------------
# Sound Generation Functions
# -------------------------------
def generate_square_wave(frequency, duration, volume=0.5, sample_rate=44100):
    """
    Generate a square wave at a given frequency and duration.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sign(np.sin(frequency * t * 2 * np.pi))
    audio = wave * volume
    return audio

def generate_simple_adsr(wave, attack=0.01, release=0.1, sample_rate=44100):
    """
    Apply a simple ADSR envelope to a waveform.
    Only attack and release phases are used for sharp sounds.
    """
    total_length = len(wave)
    attack_samples = int(sample_rate * attack)
    release_samples = int(sample_rate * release)
    sustain_samples = total_length - (attack_samples + release_samples)
    
    # Prevent negative sustain_samples
    if sustain_samples < 0:
        sustain_samples = 0
        release_samples = total_length - attack_samples
        if release_samples < 0:
            release_samples = 0
    
    # Create the ADSR envelope
    envelope = np.concatenate([
        np.linspace(0, 1, attack_samples),  # Attack
        np.ones(sustain_samples),           # Sustain
        np.linspace(1, 0, release_samples) # Release
    ])
    
    return wave[:len(envelope)] * envelope

def create_background_music():
    """
    Generate a simple looping background music using square waves.
    """
    frequencies = [440, 494, 523, 440]  # A4, B4, C5, A4
    duration = 0.5  # seconds per note
    melody = np.array([], dtype=np.float32)
    
    for freq in frequencies:
        wave = generate_square_wave(freq, duration, volume=0.3, sample_rate=SAMPLE_RATE)
        wave = generate_simple_adsr(wave, attack=0.05, release=0.05, sample_rate=SAMPLE_RATE)
        melody = np.concatenate((melody, wave))
    
    melody = np.tile(melody, 8)  # Repeat melody 8 times for longer background
    melody = np.int16(melody / np.max(np.abs(melody)) * 32767)
    sound = pygame.mixer.Sound(melody)
    return sound

def create_eat_sound():
    """
    Generate a short blip sound for eating food.
    """
    wave = generate_square_wave(660, 0.1, volume=0.7, sample_rate=SAMPLE_RATE)  # High pitch
    wave = generate_simple_adsr(wave, attack=0.02, release=0.02, sample_rate=SAMPLE_RATE)
    wave = np.int16(wave / np.max(np.abs(wave)) * 32767)
    sound = pygame.mixer.Sound(wave)
    return sound

def create_game_over_sound():
    """
    Generate a lower pitch blip sound for game over.
    """
    wave = generate_square_wave(330, 0.3, volume=0.7, sample_rate=SAMPLE_RATE)  # Lower pitch
    wave = generate_simple_adsr(wave, attack=0.05, release=0.1, sample_rate=SAMPLE_RATE)
    wave = np.int16(wave / np.max(np.abs(wave)) * 32767)
    sound = pygame.mixer.Sound(wave)
    return sound

# -------------------------------
# Create Sounds
# -------------------------------
background_music = create_background_music()
eat_sound = create_eat_sound()
game_over_sound = create_game_over_sound()

# Reserve a channel for background music
background_channel = pygame.mixer.Channel(0)

# -------------------------------
# Helper Functions
# -------------------------------
def display_message(msg, color, font, y_offset=0):
    """
    Display a message on the screen centered horizontally.
    """
    mesg = font.render(msg, True, color)
    text_rect = mesg.get_rect(center=(WIDTH / 2, HEIGHT / 3 + y_offset))
    screen.blit(mesg, text_rect)

def our_snake(snake_block, snake_list):
    """
    Draw the snake on the screen.
    """
    for x in snake_list:
        pygame.draw.rect(screen, GREEN, [x[0], x[1], snake_block, snake_block])

# -------------------------------
# Game Loop
# -------------------------------
def game_loop():
    # Play background music on loop using the dedicated channel
    background_channel.play(background_music, loops=-1)
    
    game_over = False
    game_close = False

    # Initial position of the snake
    x1 = WIDTH / 2
    y1 = HEIGHT / 2

    # Movement variables
    x1_change = 0
    y1_change = 0

    snake_list = []
    length_of_snake = 1

    # Initial food position
    foodx = round(random.randrange(0, WIDTH - SNAKE_BLOCK) / 10.0) * 10.0
    foody = round(random.randrange(0, HEIGHT - SNAKE_BLOCK) / 10.0) * 10.0

    while not game_over:

        while game_close:
            background_channel.pause()  # Pause background music
            game_over_sound.play()
            screen.fill(BLACK)
            display_message("You Lost!", RED, font_large, -50)
            display_message("Press Q to Quit or C to Play Again", WHITE, font_small, 50)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_c:
                        # Reset game state
                        background_channel.play(background_music, loops=-1)
                        game_close = False
                        # Reset snake position and length
                        x1 = WIDTH / 2
                        y1 = HEIGHT / 2
                        x1_change = 0
                        y1_change = 0
                        snake_list = []
                        length_of_snake = 1
                        # Reposition food
                        foodx = round(random.randrange(0, WIDTH - SNAKE_BLOCK) / 10.0) * 10.0
                        foody = round(random.randrange(0, HEIGHT - SNAKE_BLOCK) / 10.0) * 10.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if x1_change != SNAKE_BLOCK:  # Prevent reversing
                        x1_change = -SNAKE_BLOCK
                        y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    if x1_change != -SNAKE_BLOCK:
                        x1_change = SNAKE_BLOCK
                        y1_change = 0
                elif event.key == pygame.K_UP:
                    if y1_change != SNAKE_BLOCK:
                        y1_change = -SNAKE_BLOCK
                        x1_change = 0
                elif event.key == pygame.K_DOWN:
                    if y1_change != -SNAKE_BLOCK:
                        y1_change = SNAKE_BLOCK
                        x1_change = 0

        # Check for boundaries
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True

        # Update snake position
        x1 += x1_change
        y1 += y1_change
        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, [foodx, foody, SNAKE_BLOCK, SNAKE_BLOCK])
        snake_head = [x1, y1]
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Check for collision with itself
        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True

        our_snake(SNAKE_BLOCK, snake_list)
        pygame.display.update()

        # Check if snake has eaten the food
        if x1 == foodx and y1 == foody:
            eat_sound.play()
            foodx = round(random.randrange(0, WIDTH - SNAKE_BLOCK) / 10.0) * 10.0
            foody = round(random.randrange(0, HEIGHT - SNAKE_BLOCK) / 10.0) * 10.0
            length_of_snake += 1

        clock.tick(SNAKE_SPEED)

    pygame.quit()
    sys.exit()

# -------------------------------
# Main Menu
# -------------------------------
def main_menu():
    menu = True
    while menu:
        screen.fill(BLACK)
        display_message("Snake Game", GREEN, font_large, -100)
        display_message("Press S to Start or Q to Quit", WHITE, font_small, 50)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_s:
                    menu = False
                    game_loop()

# -------------------------------
# Entry Point
# -------------------------------
if __name__ == "__main__":
    main_menu()
