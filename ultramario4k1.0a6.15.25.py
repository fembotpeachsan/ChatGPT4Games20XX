import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ultra Maker Bro.s 3")

# Colors for drawing (no PNGs, using solid colors)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Player settings
PLAYER_RADIUS = 20
player_pos = [100, SCREEN_HEIGHT - 100]  # Start position
player_vel = [0, 0]  # Velocity (x, y)
player_speed = 5
jump_power = -15
gravity = 0.8

# Platform settings (simple level layout)
platforms = [
    # Ground
    {"x": 0, "y": SCREEN_HEIGHT - 40, "width": SCREEN_WIDTH, "height": 40},
    # Floating platforms
    {"x": 200, "y": 400, "width": 200, "height": 20},
    {"x": 500, "y": 300, "width": 150, "height": 20},
]

# Game loop settings
clock = pygame.time.Clock()
FPS = 60

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and player_vel[1] == 0:  # Jump only when on ground
                player_vel[1] = jump_power

    # Keyboard input for movement
    keys = pygame.key.get_pressed()
    player_vel[0] = 0
    if keys[pygame.K_LEFT]:
        player_vel[0] = -player_speed
    if keys[pygame.K_RIGHT]:
        player_vel[0] = player_speed

    # Apply gravity
    player_vel[1] += gravity

    # Update player position
    player_pos[0] += player_vel[0]
    player_pos[1] += player_vel[1]

    # Collision detection with platforms
    player_rect = pygame.Rect(
        player_pos[0] - PLAYER_RADIUS,
        player_pos[1] - PLAYER_RADIUS,
        PLAYER_RADIUS * 2,
        PLAYER_RADIUS * 2,
    )
    for platform in platforms:
        plat_rect = pygame.Rect(
            platform["x"], platform["y"], platform["width"], platform["height"]
        )
        if player_rect.colliderect(plat_rect):
            # Handle vertical collision
            if player_vel[1] > 0:  # Falling
                player_pos[1] = platform["y"] - PLAYER_RADIUS
                player_vel[1] = 0
            elif player_vel[1] < 0:  # Jumping
                player_pos[1] = platform["y"] + platform["height"] + PLAYER_RADIUS
                player_vel[1] = 0

    # Keep player within screen bounds
    player_pos[0] = max(PLAYER_RADIUS, min(SCREEN_WIDTH - PLAYER_RADIUS, player_pos[0]))
    if player_pos[1] > SCREEN_HEIGHT - PLAYER_RADIUS:
        player_pos[1] = SCREEN_HEIGHT - PLAYER_RADIUS
        player_vel[1] = 0

    # Clear screen
    screen.fill(WHITE)

    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(
            screen,
            BLUE,
            (platform["x"], platform["y"], platform["width"], platform["height"]),
        )

    # Draw player
    pygame.draw.circle(screen, RED, (int(player_pos[0]), int(player_pos[1])), PLAYER_RADIUS)

    # Update display
    pygame.display.flip()

    # Cap frame rate at 60 FPS
    clock.tick(FPS)

# Cleanup
pygame.quit()
sys.exit()
