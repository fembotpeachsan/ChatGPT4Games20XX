import pygame
import sys

pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FPS = 60

# Colors
SKY = (107, 140, 255)
GROUND = (150, 75, 0)
PLAYER_COLOR = (255, 0, 0)
BLOCK_COLOR = (255, 255, 0)
ENEMY_COLOR = (0, 255, 0)
COIN_COLOR = (255, 215, 0)

# Setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Pygame - Full")
clock = pygame.time.Clock()

# Player settings
player = pygame.Rect(50, SCREEN_HEIGHT-100, 32, 32)
player_speed = 5
gravity = 0.5
velocity_y = 0
on_ground = False
score = 0

# Levels data
levels = [
    [  # Level 1
        pygame.Rect(0, SCREEN_HEIGHT-50, SCREEN_WIDTH, 50),
        pygame.Rect(200, SCREEN_HEIGHT-150, 50, 50),
        pygame.Rect(400, SCREEN_HEIGHT-200, 50, 50),
        pygame.Rect(600, SCREEN_HEIGHT-250, 50, 50)
    ],
    [  # Level 2
        pygame.Rect(0, SCREEN_HEIGHT-50, SCREEN_WIDTH, 50),
        pygame.Rect(150, SCREEN_HEIGHT-120, 50, 50),
        pygame.Rect(350, SCREEN_HEIGHT-170, 50, 50),
        pygame.Rect(550, SCREEN_HEIGHT-220, 50, 50),
        pygame.Rect(750, SCREEN_HEIGHT-270, 50, 50)
    ]
]
current_level = 0

# Enemies
enemy = pygame.Rect(500, SCREEN_HEIGHT-82, 32, 32)
enemy_speed = 2

# Coins
coins = [pygame.Rect(210, SCREEN_HEIGHT-180, 15, 15), pygame.Rect(410, SCREEN_HEIGHT-230, 15, 15)]

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player.x += player_speed
    if keys[pygame.K_UP] and on_ground:
        velocity_y = -10
        on_ground = False

    velocity_y += gravity
    player.y += velocity_y

    # Player collision with ground
    on_ground = False
    for block in levels[current_level]:
        if player.colliderect(block) and velocity_y >= 0:
            player.bottom = block.top
            velocity_y = 0
            on_ground = True

    # Enemy movement
    enemy.x += enemy_speed
    if enemy.right > SCREEN_WIDTH or enemy.left < 0:
        enemy_speed = -enemy_speed

    # Collision with enemy
    if player.colliderect(enemy):
        player.x, player.y = 50, SCREEN_HEIGHT-100
        score = 0

    # Collect coins
    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            score += 1

    # Next level condition
    if player.x > SCREEN_WIDTH:
        current_level = (current_level + 1) % len(levels)
        player.x = 0

    # Drawing
    screen.fill(SKY)

    pygame.draw.rect(screen, PLAYER_COLOR, player)
    pygame.draw.rect(screen, ENEMY_COLOR, enemy)

    for block in levels[current_level]:
        pygame.draw.rect(screen, BLOCK_COLOR, block)

    for coin in coins:
        pygame.draw.circle(screen, COIN_COLOR, (coin.x + 8, coin.y + 8), 8)

    # Score display
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)
