import pygame
import sys
import random
import time
import os  # Added for system beep

# Initialize Pygame
pygame.init()

# Set screen dimensions
screen_width = 800
screen_height = 600

# Create the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mario Kart-Style Game")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

# Font for text
font = pygame.font.Font(None, 36)

# Function to play a melody using system beep
def play_melody(melody):
    for note in melody:
        os.system('say \a')  # Produces a beep sound on Mac
        time.sleep(0.5)  # Duration of each note in seconds

# Game state
file_select = True  # Initially in file select screen

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Check if "Start Game" button is clicked
            if file_select:
                if 300 <= mouse_x <= 500 and 400 <= mouse_y <= 460:
                    file_select = False  # Start the kart room
                    # Play the Mario Kart DS melody when transitioning
                    play_melody([1, 2, 3, 4, 5, 6, 7, 8])  # Dummy melody values

    # Fill the screen with white
    screen.fill(white)

    if file_select:
        # Draw the file select screen
        pygame.draw.rect(screen, red, (300, 400, 200, 60))
        start_text = font.render("Start Game", True, white)
        text_x = 400 - start_text.get_width() // 2
        text_y = 430 - start_text.get_height() // 2
        screen.blit(start_text, (text_x, text_y))
    else:
        # Draw the kart room
        pygame.draw.rect(screen, black, (100, 200, 200, 100))
        kart_text = font.render("Kart Room", True, white)
        text_x = 200 - kart_text.get_width() // 2
        text_y = 250 - kart_text.get_height() // 2
        screen.blit(kart_text, (text_x, text_y))

    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
