import pygame
import sys
import random

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Donkery Kong (No PNGs Allowed)")
clock = pygame.time.Clock()

# Colors
RED = (255, 0, 0)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
CREAM = (255, 253, 208)

# Game objects
dk = pygame.Rect(50, 50, 80, 60)  # Donkey Kong
jumpman = pygame.Rect(300, 300, 30, 50)  # "Mario"
barrels = []
ramps = [pygame.Rect(100, 150, 200, 20), pygame.Rect(300, 250, 200, 20)]

# Barrel spawn timer
barrel_timer = 0

def draw_dk(surface):
    # Draw DK as a red rectangle with eyes
    pygame.draw.rect(surface, RED, dk)
    pygame.draw.circle(surface, BLACK, (dk.x + 20, dk.y + 20), 5)  # Eye
    pygame.draw.circle(surface, BLACK, (dk.x + 60, dk.y + 20), 5)  # Eye

def draw_jumpman(surface):
    # Draw Jumpman (mustache included)
    pygame.draw.rect(surface, BLUE, jumpman)
    pygame.draw.rect(surface, BLACK, (jumpman.x, jumpman.y + 15, 30, 5))  # Mustache

def create_barrel():
    barrels.append({
        "rect": pygame.Rect(dk.x + 40, dk.y + 50, 20, 20),
        "speed": random.randint(2, 4)
    })

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Spawn barrels
    barrel_timer += 1
    if barrel_timer > 60:  # Every ~1 second
        create_barrel()
        barrel_timer = 0

    # Move barrels
    for barrel in barrels[:]:
        barrel["rect"].x += barrel["speed"]
        # Barrel ramp physics (simplified)
        for ramp in ramps:
            if barrel["rect"].colliderect(ramp):
                barrel["rect"].y = ramp.y - 20
        # Remove off-screen barrels
        if barrel["rect"].x > 600:
            barrels.remove(barrel)

    # Jumpman movement (arrow keys)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        jumpman.x -= 5
    if keys[pygame.K_RIGHT]:
        jumpman.x += 5
    if keys[pygame.K_UP]:
        jumpman.y -= 5
    if keys[pygame.K_DOWN]:
        jumpman.y += 5

    # Collision (game over if hit by barrel)
    for barrel in barrels:
        if jumpman.colliderect(barrel["rect"]):
            print("GAME OVER! 🍌")
            pygame.quit()
            sys.exit()

    # Draw everything
    screen.fill(CREAM)
    for ramp in ramps:
        pygame.draw.rect(screen, BROWN, ramp)
    draw_dk(screen)
    draw_jumpman(screen)
    for barrel in barrels:
        pygame.draw.circle(screen, BROWN, barrel["rect"].center, 10)

    pygame.display.flip()
    clock.tick(60)
