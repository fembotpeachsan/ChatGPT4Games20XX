import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 256, 240  # NES resolution
TILE_SIZE = 16  # NES sprite size
LEVEL_WIDTH, LEVEL_HEIGHT = 16, 15  # 16x15 tiles
PLAYER_SIZE = TILE_SIZE
NPC_SIZE = TILE_SIZE

# NES-like Colors
WHITE = (255, 255, 255)
GREEN = (0, 240, 0)
RED = (240, 0, 0)
BLUE = (0, 0, 240)
BROWN = (139, 69, 19)

# Initialize screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Zelda/Cave Story-like Game')
clock = pygame.time.Clock()

# Initialize player position and stats
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]

# Initialize NPC position
npc_pos = [random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)]

# Initialize font for HUD
font = pygame.font.Font(None, 16)

# Game state managed by AI
game_state = "NORMAL"

# Initialize Level with random tiles
level = [[random.choice([0, 1]) for _ in range(LEVEL_HEIGHT)] for _ in range(LEVEL_WIDTH)]

# Function to draw Zelda-like Link sprite
def draw_link(x, y, size):
    pygame.draw.rect(screen, GREEN, (x, y + size // 4, size, size // 2))
    pygame.draw.rect(screen, WHITE, (x + size // 4, y, size // 2, size // 4))

# Function to draw NPC
def draw_npc(x, y, size):
    pygame.draw.rect(screen, BLUE, (x, y, size, size))

# Function to draw level
def draw_level(level):
    for x in range(LEVEL_WIDTH):
        for y in range(LEVEL_HEIGHT):
            tile = level[x][y]
            if tile == 1:  # Wall
                pygame.draw.rect(screen, BROWN, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

# Main Game Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Handle player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_pos[0] -= 2
    if keys[pygame.K_RIGHT]:
        player_pos[0] += 2
    if keys[pygame.K_UP]:
        player_pos[1] -= 2
    if keys[pygame.K_DOWN]:
        player_pos[1] += 2

    # Clear screen
    screen.fill(WHITE)

    # Draw level
    draw_level(level)

    # Draw player (Zelda-like Link)
    draw_link(player_pos[0], player_pos[1], PLAYER_SIZE)

    # Draw NPC
    draw_npc(npc_pos[0], npc_pos[1], NPC_SIZE)

    # Draw HUD
    hud_text = font.render(f"Pos: {player_pos}  State: {game_state}", True, WHITE)
    screen.blit(hud_text, (10, 10))

    pygame.display.update()
    clock.tick(30)

    ## - Flames LLC 20XX
