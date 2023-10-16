import pygame
import sys

# Initialize pygame
pygame.init()

# Set up display
window_size = (800, 600)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('Simple Paper Mario Battle')

# Define classes for characters and actions
class Character:
    def __init__(self, name, hp):
        self.name = name
        self.hp = hp

class Action:
    def __init__(self, name, damage):
        self.name = name
        self.damage = damage

# Create some characters and actions
player = Character('Mario', 100)
enemy = Character('Goomba', 50)
jump_action = Action('Jump', 10)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle input (for simplicity, we'll assume a key press initiates an attack)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        enemy.hp -= jump_action.damage
        print(f'{player.name} used {jump_action.name} on {enemy.name}! {enemy.name} has {enemy.hp} HP remaining.')

    # Update display
    screen.fill((255, 255, 255))  # Fill screen with white
    # Render characters, UI, etc. here (omitted for simplicity)
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Exit cleanly
pygame.quit()
sys.exit()
