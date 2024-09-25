import pygame
import random
import time  # Import the time module for delays

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Donkey Kong Clone - Pygame')

# Game settings
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Font settings for countdown
font = pygame.font.Font(None, 74)

# Player settings (Mario)
player_width, player_height = 30, 40
player_x, player_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT - player_height
player_speed = 5
player_jump = False
jump_height = 15
gravity = 1
velocity_y = 0

# Donkey Kong, Pauline, Barrels
donkey_kong_rect = pygame.Rect(100, 50, 80, 60)  # Placeholder for Donkey Kong
pauline_rect = pygame.Rect(300, 50, 30, 50)  # Placeholder for Pauline
barrels = []

# Platforms
platforms = [
    pygame.Rect(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 20),
    pygame.Rect(0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 20),
    pygame.Rect(0, SCREEN_HEIGHT - 300, SCREEN_WIDTH, 20),
    pygame.Rect(0, SCREEN_HEIGHT - 450, SCREEN_WIDTH, 20)
]

# Ladders
ladders = [
    pygame.Rect(200, SCREEN_HEIGHT - 150, 30, 90),
    pygame.Rect(600, SCREEN_HEIGHT - 300, 30, 90)
]

# Collision detection function
def check_collision(rect, platforms):
    for platform in platforms:
        if rect.colliderect(platform):
            return platform
    return None

# Countdown display function
def show_countdown():
    countdown_text = ["3", "2", "1", "READY", "GO!"]
    for text in countdown_text:
        screen.fill(BLACK)
        label = font.render(text, True, WHITE)
        label_rect = label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(label, label_rect)
        pygame.display.update()
        time.sleep(1)  # Wait 1 second between each countdown

# Show countdown before starting the game
show_countdown()

# Main game loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - player_width:
        player_x += player_speed
    if not player_jump:
        if keys[pygame.K_SPACE]:
            player_jump = True
            velocity_y = -jump_height
    else:
        # Gravity and jump physics
        player_y += velocity_y
        velocity_y += gravity

    # Player collision with platforms (stop falling)
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    collided_platform = check_collision(player_rect, platforms)
    if collided_platform:
        player_y = collided_platform.top - player_height
        player_jump = False
        velocity_y = 0

    # Draw player (Mario)
    pygame.draw.rect(screen, BLUE, player_rect)

    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(screen, GREEN, platform)

    # Draw ladders
    for ladder in ladders:
        pygame.draw.rect(screen, WHITE, ladder)

    # Draw Donkey Kong and Pauline
    pygame.draw.rect(screen, RED, donkey_kong_rect)
    pygame.draw.rect(screen, WHITE, pauline_rect)

    # Barrel spawning logic
    if random.randint(1, 100) == 1:  # Random chance of a barrel spawning
        barrels.append(pygame.Rect(donkey_kong_rect.centerx, donkey_kong_rect.bottom, 20, 20))

    # Update and draw barrels
    for barrel in barrels[:]:
        barrel.move_ip(random.choice([-1, 1]), 5)  # Barrels move sideways and down
        pygame.draw.rect(screen, RED, barrel)
        
        # Remove barrels once they fall off the screen
        if barrel.top > SCREEN_HEIGHT:
            barrels.remove(barrel)
        
        # Collision with Mario (end game)
        if barrel.colliderect(player_rect):
            print("Game Over!")
            running = False

    # Check if Mario reaches Pauline (win condition)
    if player_rect.colliderect(pauline_rect):
        print("You win!")
        running = False

    # Refresh screen
    pygame.display.update()

    # Check for quit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# End game
pygame.quit()
