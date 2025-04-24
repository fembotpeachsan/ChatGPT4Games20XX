import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FPS = 60

# Colors
SKY = (107, 140, 255)      # Background
GROUND = (150, 75, 0)      # Ground (unused in drawing but defined)
PLAYER_COLOR = (255, 0, 0) # Mario (red)
BLOCK_COLOR = (255, 255, 0)# Platforms (yellow)
ENEMY_COLOR = (0, 255, 0)  # Enemies (green)
COIN_COLOR = (255, 215, 0) # Coins (gold)

# Setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros. Pygame")
clock = pygame.time.Clock()

# Player settings
player = pygame.Rect(50, SCREEN_HEIGHT - 100, 32, 32)
player_speed = 5
gravity = 0.5
velocity_y = 0
on_ground = False
score = 0

# Level data (expanded to include width, enemies, coins per level)
levels = [
    {  # Level 1 (inspired by World 1-1)
        'width': 2000,
        'blocks': [
            pygame.Rect(0, SCREEN_HEIGHT - 50, 1000, 50),    # Ground part 1
            pygame.Rect(1200, SCREEN_HEIGHT - 50, 800, 50),  # Ground part 2 (gap between)
            pygame.Rect(200, SCREEN_HEIGHT - 150, 50, 50),   # Platform 1
            pygame.Rect(400, SCREEN_HEIGHT - 200, 50, 50),   # Platform 2
            pygame.Rect(600, SCREEN_HEIGHT - 250, 50, 50),   # Platform 3
            pygame.Rect(1400, SCREEN_HEIGHT - 150, 50, 50),  # Platform 4
        ],
        'enemies': [
            {'rect': pygame.Rect(500, SCREEN_HEIGHT - 82, 32, 32), 'speed': 2},
            {'rect': pygame.Rect(1500, SCREEN_HEIGHT - 82, 32, 32), 'speed': -2},
        ],
        'coins': [
            pygame.Rect(210, SCREEN_HEIGHT - 180, 15, 15),
            pygame.Rect(410, SCREEN_HEIGHT - 230, 15, 15),
            pygame.Rect(610, SCREEN_HEIGHT - 280, 15, 15),
            pygame.Rect(1410, SCREEN_HEIGHT - 180, 15, 15),
        ]
    },
    {  # Level 2 (inspired by World 1-2 style, more platforms)
        'width': 2500,
        'blocks': [
            pygame.Rect(0, SCREEN_HEIGHT - 50, 1200, 50),    # Ground part 1
            pygame.Rect(1500, SCREEN_HEIGHT - 50, 1000, 50), # Ground part 2
            pygame.Rect(150, SCREEN_HEIGHT - 120, 50, 50),   # Platform 1
            pygame.Rect(350, SCREEN_HEIGHT - 170, 50, 50),   # Platform 2
            pygame.Rect(550, SCREEN_HEIGHT - 220, 50, 50),   # Platform 3
            pygame.Rect(750, SCREEN_HEIGHT - 270, 50, 50),   # Platform 4
            pygame.Rect(1700, SCREEN_HEIGHT - 150, 50, 50),  # Platform 5
        ],
        'enemies': [
            {'rect': pygame.Rect(300, SCREEN_HEIGHT - 82, 32, 32), 'speed': 3},
            {'rect': pygame.Rect(600, SCREEN_HEIGHT - 82, 32, 32), 'speed': -2},
            {'rect': pygame.Rect(1800, SCREEN_HEIGHT - 82, 32, 32), 'speed': 2},
        ],
        'coins': [
            pygame.Rect(160, SCREEN_HEIGHT - 150, 15, 15),
            pygame.Rect(360, SCREEN_HEIGHT - 200, 15, 15),
            pygame.Rect(560, SCREEN_HEIGHT - 250, 15, 15),
            pygame.Rect(760, SCREEN_HEIGHT - 300, 15, 15),
            pygame.Rect(1710, SCREEN_HEIGHT - 180, 15, 15),
        ]
    }
]
current_level = 0

# Global variables for level-specific objects
current_level_data = None
enemies = []
coins = []

def load_level(level_index):
    """Load or reset the specified level."""
    global player, velocity_y, on_ground, score, enemies, coins, current_level_data
    current_level_data = levels[level_index]
    player.x, player.y = 50, SCREEN_HEIGHT - 100  # Reset player position
    velocity_y = 0
    on_ground = False
    # score = 0  # Uncomment to reset score per level; keeping it persistent here
    enemies = [{'rect': enemy['rect'].copy(), 'speed': enemy['speed']} 
               for enemy in current_level_data['enemies']]
    coins = [coin.copy() for coin in current_level_data['coins']]

# Initial level load
load_level(current_level)

# Game loop
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Player input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= player_speed
        if player.x < 0:  # Prevent moving off left edge
            player.x = 0
    if keys[pygame.K_RIGHT]:
        player.x += player_speed
    if keys[pygame.K_UP] and on_ground:
        velocity_y = -10  # Jump
        on_ground = False

    # Apply gravity
    velocity_y += gravity
    player.y += velocity_y

    # Collision with blocks
    on_ground = False
    for block in current_level_data['blocks']:
        if player.colliderect(block) and velocity_y >= 0:
            player.bottom = block.top
            velocity_y = 0
            on_ground = True

    # Enemy movement
    for enemy in enemies:
        enemy['rect'].x += enemy['speed']
        # Bounce at level boundaries
        if (enemy['rect'].right > current_level_data['width'] or 
            enemy['rect'].left < 0):
            enemy['speed'] = -enemy['speed']

    # Player-enemy collision
    for enemy in enemies:
        if player.colliderect(enemy['rect']):
            player.x, player.y = 50, SCREEN_HEIGHT - 100  # Reset position
            velocity_y = 0
            on_ground = False
            # score = 0  # Uncomment to reset score; keeping it for now

    # Collect coins
    for coin in coins[:]:  # Use a copy to modify list during iteration
        if player.colliderect(coin):
            coins.remove(coin)
            score += 1

    # Death by falling
    if player.y > SCREEN_HEIGHT:
        player.x, player.y = 50, SCREEN_HEIGHT - 100
        velocity_y = 0
        on_ground = False
        # score = 0  # Uncomment to penalize; keeping score persistent

    # Level progression
    if player.x > current_level_data['width']:
        current_level = (current_level + 1) % len(levels)
        load_level(current_level)

    # Camera scrolling
    level_width = current_level_data['width']
    max_offset = max(0, level_width - SCREEN_WIDTH)  # No negative offset
    camera_offset = min(max(player.x - SCREEN_WIDTH / 2, 0), max_offset)

    # Drawing
    screen.fill(SKY)

    # Draw blocks
    for block in current_level_data['blocks']:
        draw_rect = pygame.Rect(block.x - camera_offset, block.y, 
                               block.width, block.height)
        pygame.draw.rect(screen, BLOCK_COLOR, draw_rect)

    # Draw enemies
    for enemy in enemies:
        draw_rect = pygame.Rect(enemy['rect'].x - camera_offset, enemy['rect'].y, 
                               enemy['rect'].width, enemy['rect'].height)
        pygame.draw.rect(screen, ENEMY_COLOR, draw_rect)

    # Draw coins
    for coin in coins:
        draw_pos = (int(coin.x - camera_offset + 8), int(coin.y + 8))
        pygame.draw.circle(screen, COIN_COLOR, draw_pos, 8)

    # Draw player
    draw_rect = pygame.Rect(player.x - camera_offset, player.y, 
                           player.width, player.height)
    pygame.draw.rect(screen, PLAYER_COLOR, draw_rect)

    # Display score
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    # Update display
    pygame.display.flip()
    clock.tick(FPS)
