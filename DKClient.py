import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Donkey Kong Clone")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Clock for controlling the frame rate
clock = pygame.time.Clock()
FPS = 60

# Player settings
PLAYER_SPEED = 3
JUMP_HEIGHT = 15
gravity = 0.8

# Barrel settings
BARREL_SPEED = 3
BARREL_SPAWN_TIME = 2000  # Spawn barrel every 2 seconds

# Platform and ladder positions
platforms = [
    pygame.Rect(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20),
    pygame.Rect(50, 400, 500, 20),
    pygame.Rect(0, 300, 400, 20),
    pygame.Rect(200, 200, 400, 20)
]

ladders = [
    pygame.Rect(150, 400, 20, 100),
    pygame.Rect(350, 300, 20, 100),
    pygame.Rect(450, 200, 20, 100)
]

# Player
player = pygame.Rect(50, SCREEN_HEIGHT - 50, 30, 30)
player_velocity_y = 0
is_jumping = False

# Goal (Princess)
goal = pygame.Rect(500, 170, 40, 40)

# Barrels
barrels = []
last_barrel_time = pygame.time.get_ticks()

# Donkey Kong (Stationary)
donkey_kong = pygame.Rect(450, 150, 60, 60)

# Game over flag
running = True
game_over = False

def spawn_barrel():
    """Spawns a barrel at Donkey Kong's position."""
    barrels.append(pygame.Rect(donkey_kong.x, donkey_kong.y + 50, 20, 20))

def move_barrels():
    """Moves barrels down the platforms and ladders."""
    for barrel in barrels[:]:
        barrel.x -= BARREL_SPEED  # Move barrel horizontally
        # Check if barrel can move down a ladder
        for ladder in ladders:
            if ladder.colliderect(barrel) and random.choice([True, False]):
                barrel.y += BARREL_SPEED
                break
        # Remove barrel if it goes off-screen
        if barrel.x < 0:
            barrels.remove(barrel)

def check_collision():
    """Check for collisions between player and barrels or goal."""
    global running, game_over
    for barrel in barrels:
        if player.colliderect(barrel):
            print("Game Over! You were hit by a barrel.")
            game_over = True
            running = False
    if player.colliderect(goal):
        print("You Win! You rescued the princess!")
        game_over = True
        running = False

def draw_elements():
    """Draws all game elements on the screen."""
    screen.fill(BLACK)
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
    # Draw goal (Princess)
    pygame.draw.rect(screen, YELLOW, goal)
    # Draw Donkey Kong
    pygame.draw.rect(screen, RED, donkey_kong)
    pygame.display.flip()

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not is_jumping:
                player_velocity_y = -JUMP_HEIGHT
                is_jumping = True

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        player.x += PLAYER_SPEED
    # Ladder climbing
    on_ladder = any(player.colliderect(ladder) for ladder in ladders)
    if on_ladder:
        if keys[pygame.K_UP]:
            player.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            player.y += PLAYER_SPEED
            is_jumping = False  # Cancel jumping on ladders

    # Apply gravity
    if not on_ladder:
        player_velocity_y += gravity
        player.y += player_velocity_y

    # Collision with platforms
    on_ground = False
    for platform in platforms:
        if player.colliderect(platform) and player_velocity_y > 0:
            player.bottom = platform.top
            player_velocity_y = 0
            on_ground = True
            is_jumping = False
    if not on_ground and not on_ladder:
        is_jumping = True

    # Keep player in bounds
    player.x = max(0, min(SCREEN_WIDTH - player.width, player.x))
    player.y = min(SCREEN_HEIGHT - player.height, player.y)

    # Spawn barrels
    if pygame.time.get_ticks() - last_barrel_time > BARREL_SPAWN_TIME:
        spawn_barrel()
        last_barrel_time = pygame.time.get_ticks()

    # Move barrels and check collisions
    move_barrels()
    check_collision()

    # Draw everything
    draw_elements()
    clock.tick(FPS)

pygame.quit()
sys.exit()
