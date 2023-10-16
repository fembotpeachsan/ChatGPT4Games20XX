import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Initialize screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ultra Mario")
clock = pygame.time.Clock()

# Initialize font
font = pygame.font.Font(None, 36)

# ASCII Art of Fire Flower
fire_flower = [
    "    **    ",
    "   ****   ",
    "  ******  ",
    "**********",
    "  **  **  ",
    " **    ** ",
    "**********",
    "  ******  ",
    "   ****   ",
    "    **    "
]

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Draw background
    screen.fill(BLACK)

    # Draw "ULTRA MARIO" at the top
    text = font.render("ULTRA MARIO", True, RED)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 10))

    # Draw ASCII Art of Fire Flower
    y_offset = SCREEN_HEIGHT // 2 - len(fire_flower) // 2 * 20
    for i, line in enumerate(fire_flower):
        x_offset = SCREEN_WIDTH // 2 - len(line) // 2 * 20
        for j, char in enumerate(line):
            if char == '*':
                pygame.draw.rect(screen, RED, (x_offset + j * 20, y_offset + i * 20, 18, 18))
    # Update the display
    pygame.display.update()

    # Cap the frame rate
    clock.tick(30)
