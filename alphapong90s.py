import pygame
import numpy as np
import threading
import time

# Initialize Pygame
pygame.init()

# Setup pygame mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Define all necessary notes with their frequencies
NOTES = {
    'E5': 659.25,
    'B4': 493.88,
    'C5': 523.25,
    'D5': 587.33,
    'A4': 440.00,
    'A3': 220.00,
    'E4': 329.63,
    'F5': 698.46,
    'G5': 783.99,
    'A5': 880.00
}

def generate_square_wave(frequency, duration=0.1, volume=0.3):
    """
    Generates a square wave sound for a given frequency and duration.
    """
    sample_rate = 44100
    num_samples = int(duration * sample_rate)
    amplitude = int(volume * 32767)  # Scale volume to int16 range
    t = np.linspace(0, duration, num_samples, endpoint=False)

    # Generate square wave
    wave = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))

    # Create stereo by duplicating the mono wave
    stereo_wave = np.column_stack((wave, wave)).astype(np.int16)

    return pygame.sndarray.make_sound(stereo_wave)

# Pre-generate all note sounds to improve performance
SOUNDS = {note: generate_square_wave(freq) for note, freq in NOTES.items()}

def play_tetris_theme():
    """
    Plays the Tetris theme melody in a continuous loop.
    """
    melody = [
        ('E5', 0.25), ('B4', 0.125), ('C5', 0.125), ('D5', 0.25), ('C5', 0.125),
        ('B4', 0.125), ('A4', 0.25), ('A4', 0.125), ('C5', 0.125), ('E5', 0.25),
        ('D5', 0.125), ('C5', 0.125), ('B4', 0.375), ('C5', 0.125), ('D5', 0.25),
        ('E5', 0.25), ('C5', 0.25), ('A4', 0.25), ('A4', 0.25), ('B4', 0.125),
        ('C5', 0.125), ('D5', 0.375), ('F5', 0.125), ('A5', 0.25), ('G5', 0.125),
        ('F5', 0.125), ('E5', 0.375)
    ]

    # Create a channel for the melody
    channel = pygame.mixer.Channel(0)

    while True:  # Continuous loop to replay the melody
        for note, duration in melody:
            if note not in SOUNDS:
                print(f"Note {note} not defined in NOTES dictionary.")
                continue  # Skip undefined notes

            sound = SOUNDS[note]
            channel.play(sound)
            time.sleep(duration)  # Use time.sleep to prevent blocking the main thread

# Start playing the theme in a separate thread to prevent blocking
theme_thread = threading.Thread(target=play_tetris_theme, daemon=True)
theme_thread.start()

# Main game loop (example)
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Tetris with Music")
clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)  # Limit to 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Your game logic and rendering code goes here

    screen.fill((0, 0, 0))  # Example: fill the screen with black
    pygame.display.flip()

pygame.quit()
