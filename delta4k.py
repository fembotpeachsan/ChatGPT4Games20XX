import pygame
import sys
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (DS-inspired palette)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (237, 28, 36)
GREEN = (34, 177, 76)
BLUE = (63, 72, 204)
BROWN = (139, 69, 19)
YELLOW = (255, 216, 0)
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (124, 252, 0)
BRICK_RED = (178, 34, 34)
MUSHROOM_RED = (255, 48, 48)
TOAD_BLUE = (65, 105, 225)

# Player Constants
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAVITY = 0.8
PLAYER_JUMP = -15

# Platform Constants
PLATFORM_THICKNESS = 20

# --- Helper Functions ---
def load_level_data(world_index, level_index):
    """
    Returns level data including platforms, enemies, coins, and goal.
    Format: {'platforms': [(x, y, w, h), ...], 'enemies': [(x, y), ...], 'coins': [(x, y), ...], 'goal': (x, y, w, h)}
    """
    print(f"Loading World {world_index+1}, Level {level_index+1}")
    if world_index == 0 and level_index == 0:
        platforms = [
            (0, SCREEN_HEIGHT - PLATFORM_THICKNESS, SCREEN_WIDTH * 2, PLATFORM_THICKNESS),  # Ground
            (200, SCREEN_HEIGHT - 100, 100, PLATFORM_THICKNESS),
            (400, SCREEN_HEIGHT - 200, 150, PLATFORM_THICKNESS),
            (600, SCREEN_HEIGHT - 300, 50, PLATFORM_THICKNESS),
            (50, SCREEN_HEIGHT - 400, 100, 80),
        ]
        enemies = [
            (300, SCREEN_HEIGHT - PLATFORM_THICKNESS),  # On ground
            (450, SCREEN_HEIGHT - 200),                 # On platform
        ]
        coins = [
            (100, SCREEN_HEIGHT - 50),   # Above ground
            (250, SCREEN_HEIGHT - 130),  # Above platform
        ]
        goal = (1550, SCREEN_HEIGHT - 200, 10, 200)  # Flagpole at level end
        return {'platforms': platforms, 'enemies': enemies, 'coins': coins, 'goal': goal}
    else:
        # Default level with ground only
        platforms = [(0, SCREEN_HEIGHT - PLATFORM_THICKNESS, SCREEN_WIDTH * 2, PLATFORM_THICKNESS)]
        return {'platforms': platforms, 'enemies': [], 'coins': [], 'goal': None}

def draw_mario(surface, width, height):
    """Draw a Mario-like character using basic shapes"""
    # Create transparent surface
    char_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Red cap and shirt
    pygame.draw.rect(char_surface, RED, (2, 2, width-4, height//3))
    pygame.draw.rect(char_surface, RED, (2, height//2, width-4, height//3))
    
    # Blue overalls
    pygame.draw.rect(char_surface, BLUE, (2, height//3, width-4, height//6))
    
    # Face
    pygame.draw
