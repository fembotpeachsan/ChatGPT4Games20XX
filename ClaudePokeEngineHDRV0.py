import pygame
import sys

# Define tile constants
TRE = 0  # Tree
PTH = 1  # Path
WTR = 2  # Water
FNC = 3  # Fence
GRS = 4  # Grass
RPL = 5  # Roof Player's house
RRV = 6  # Roof Rival's house
PHW = 7  # Player House Wall
PHD = 8  # Player House Door
MRW = 9  # May/Rival House Wall
PCW = 10  # Pokémon Center Wall
PCD = 11  # Pokémon Center Door
TLG = 12  # Tall Grass
PSP = 13  # Player Spawn Point
LBW = 14  # Lab Wall
LBD = 15  # Lab Door
RLB = 16  # Roof Lab
FLY = 17  # Flowers

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_BROWN = (210, 180, 140)
LIGHT_BLUE = (173, 216, 230)

# Map data (already defined in your code)
littleroot_town_map_data = [
    # Row 0 - Northern trees and lab roof
    [TRE, TRE, TRE, TRE, TRE, TRE, RLB, RLB, RLB, RLB, RLB, RLB, RLB, RLB, RLB, RLB, RLB, RLB, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE],
    
    # Row 1 - Lab entrance path
    [TRE, TRE, TRE, TRE, TRE, PTH, PTH, LBD, LBW, LBW, LBW, LBW, LBW, LBW, LBW, LBW, LBW, LBD, PTH, PTH, TRE, TRE, WTR, WTR, WTR, WTR, TRE, TRE, TRE, TRE],
    
    # Row 2 - Lab walls
    [TRE, TRE, TRE, TRE, TRE, LBW, LBW, LBW, LBW, LBW, LBW, LBW, LBW, LBW, LBW, LBW, LBW, LBW, LBW, LBW, PTH, WTR, WTR, WTR, WTR, WTR, PTH, TRE, TRE, TRE],
    
    # Row 3 - South lab path
    [TRE, TRE, TRE, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, WTR, WTR, WTR, WTR, WTR, PTH, TRE, TRE, TRE],
    
    # Row 4 - Vertical main path
    [TRE, TRE, FNC, FNC, FNC, PTH, GRS, GRS, GRS, GRS, GRS, GRS, GRS, GRS, GRS, GRS, GRS, GRS, GRS, GRS, PTH, PTH, PTH, PTH, PTH, PTH, PTH, FNC, FNC, TRE],
    
    # Row 5 - Horizontal crossroads
    [TRE, PTH, PTH, PTH, PTH, PTH, RPL, RPL, RPL, RPL, RPL, RPL, RPL, RPL, RPL, RPL, RRV, RRV, RRV, RRV, PTH, FLY, FLY, FLY, FLY, FLY, PTH, PTH, PTH, TRE],
    
    # Row 6 - Player House (left) and Rival House (right)
    [TRE, PHW, PHW, PHW, PHW, PHW, PHW, PHW, PHW, PHW, PHW, PHD, PTH, RRV, RRV, RRV, RRV, RRV, RRV, RRV, RRV, RRV, RRV, RRV, RRV, RRV, RRV, RRV, RRV, TRE],
    
    # Row 7 - Player House interior
    [TRE, PHW, GRS, GRS, GRS, PHW, PHW, GRS, GRS, GRS, PHW, PHD, PTH, MRW, MRW, MRW, MRW, MRW, MRW, MRW, MRW, MRW, MRW, MRW, MRW, MRW, MRW, MRW, MRW, TRE],
    
    # Row 8 - Southern path
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PCD, PCW, PCW, PCW, PCW, PCW, PCW, PCW, PCW, PCW, PCW, PCW, PCW, PCW, PCD, PTH, TRE],
    
    # Row 9 - Grass and spawn points
    [TRE, TRE, TLG, TLG, TLG, TLG, TLG, PSP, TLG, TLG, TLG, TLG, TLG, TLG, TLG, TLG, TLG, TLG, TLG, TLG, TLG, TLG, TLG, TLG, TLG, TLG, TLG, TLG, TRE, TRE],
    
    # Row 10 - Southern trees
    [TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE]
]

# Player starting position (as specified)
player_x, player_y = 7, 9

# Initialize Pygame
pygame.init()

# Game settings
TILE_SIZE = 40
MAP_WIDTH = len(littleroot_town_map_data[0])
MAP_HEIGHT = len(littleroot_town_map_data)
SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE
SCREEN_HEIGHT = MAP_HEIGHT * TILE_SIZE

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Littleroot Town")

# Tile color mapping (simple representation)
tile_colors = {
    TRE: DARK_GREEN,       # Tree
    PTH: LIGHT_BROWN,      # Path
    WTR: BLUE,             # Water
    FNC: BROWN,            # Fence
    GRS: GREEN,            # Grass
    RPL: RED,              # Roof Player's house
    RRV: RED,              # Roof Rival's house
    PHW: LIGHT_BROWN,      # Player House Wall
    PHD: BROWN,            # Player House Door
    MRW: LIGHT_BROWN,      # May/Rival House Wall
    PCW: LIGHT_BLUE,       # Pokémon Center Wall
    PCD: BROWN,            # Pokémon Center Door
    TLG: DARK_GREEN,       # Tall Grass
    PSP: GREEN,            # Player Spawn Point (same as grass)
    LBW: LIGHT_BROWN,      # Lab Wall
    LBD: BROWN,            # Lab Door
    RLB: GRAY,             # Roof Lab
    FLY: YELLOW            # Flowers
}

# Player character settings
player_color = (255, 0, 0)  # Red
player_size = TILE_SIZE - 10  # Slightly smaller than a tile

# Function to check if the move is valid
def is_valid_move(x, y):
    # Check if the position is within map boundaries
    if x < 0 or x >= MAP_WIDTH or y < 0 or y >= MAP_HEIGHT:
        return False
    
    # Check if the tile is walkable
    tile_type = littleroot_town_map_data[y][x]
    walkable_tiles = [PTH, GRS, PSP, PHD, LBD, PCD]  # List of walkable tile types
    
    return tile_type in walkable_tiles

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle keyboard input
        if event.type == pygame.KEYDOWN:
            # Store the potential new position
            new_x, new_y = player_x, player_y
            
            if event.key == pygame.K_UP:
                new_y -= 1
            elif event.key == pygame.K_DOWN:
                new_y += 1
            elif event.key == pygame.K_LEFT:
                new_x -= 1
            elif event.key == pygame.K_RIGHT:
                new_x += 1
            
            # Move the player if the new position is valid
            if is_valid_move(new_x, new_y):
                player_x, player_y = new_x, new_y
    
    # Clear the screen
    screen.fill(BLACK)
    
    # Draw the map
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tile_type = littleroot_town_map_data[y][x]
            color = tile_colors.get(tile_type, BLACK)
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)
            
            # Add border to tiles for better visibility
            pygame.draw.rect(screen, BLACK, rect, 1)
    
    # Draw the player
    player_rect = pygame.Rect(
        player_x * TILE_SIZE + (TILE_SIZE - player_size) // 2,
        player_y * TILE_SIZE + (TILE_SIZE - player_size) // 2,
        player_size,
        player_size
    )
    pygame.draw.rect(screen, player_color, player_rect)
    
    # Update the display
    pygame.display.flip()
    
    # Control the game speed
    clock.tick(60)

# Clean up
pygame.quit()
sys.exit()
