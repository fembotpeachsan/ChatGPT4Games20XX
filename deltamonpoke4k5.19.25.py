import tkinter as tk # Not used in this version, but kept as per original
import pygame
import os # Not used in this snippet directly, but often useful
import time # Not used in this snippet directly
import random # For potential future use (e.g., NPC movement)

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32

# Viewport dimensions in tiles
DIALOGUE_BOX_HEIGHT = 100 # Height of the dialogue box in pixels
GAME_AREA_HEIGHT = SCREEN_HEIGHT - DIALOGUE_BOX_HEIGHT # Used for in-game viewport
VIEWPORT_WIDTH_TILES = SCREEN_WIDTH // TILE_SIZE
VIEWPORT_HEIGHT_TILES = GAME_AREA_HEIGHT // TILE_SIZE

FPS = 60

# --- Colors (Gen 3 Inspired - simplified) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
C_PATH_GRASS = (136, 192, 112)
C_GRASS_REGULAR = (104, 168, 88)
C_TALL_GRASS = (64, 128, 72)
C_TREE_TRUNK = (112, 80, 48) # Not directly used for T_TREE color, but good for reference
C_TREE_LEAVES = (48, 96, 48) # Main color for T_TREE
C_WATER = (80, 128, 200)
C_FLOWER_RED = (208, 72, 48)
C_FLOWER_YELLOW = (248, 224, 96)
C_SAND = (216, 200, 160) # Not used in current maps, but defined
C_BUILDING_WALL_LIGHT = (200, 160, 120) # Generic building wall
C_BUILDING_WALL_DARK = (160, 128, 96)  # Generic building wall
C_ROOF_RED = (192, 80, 48)
C_ROOF_BLUE = (80, 96, 160)
C_ROOF_GRAY = (128, 128, 128) # Lab, PokeCenter-like
C_ROOF_MART = (60, 120, 180) # Mart-like building roof
C_DOOR = (96, 64, 32)
C_SIGN = (144, 112, 80)
C_LEDGE = (120, 176, 104) # Color for ledge tiles
C_FENCE = (160, 144, 128)
C_PLAYER = (224, 80, 64)
C_NPC = (80, 144, 224)
C_DIALOGUE_BG = (40, 40, 40)
C_DIALOGUE_TEXT = WHITE
C_DIALOGUE_BORDER = (100, 100, 100)
C_PC_WALL = (230, 190, 190) # PokeCenter-like wall
C_MART_WALL = (180, 200, 230) # Mart-like wall

# --- Tile Types ---
T_PATH_GRASS = 0
T_GRASS_REGULAR = 1
T_TALL_GRASS = 2
T_WATER = 3
T_TREE = 4
T_FLOWER_RED = 5
T_FLOWER_YELLOW = 6
T_SAND = 7
T_BUILDING_WALL = 10 # Generic
T_PLAYER_HOUSE_WALL = 11
T_PLAYER_HOUSE_DOOR = 12
T_RIVAL_HOUSE_WALL = 13
T_RIVAL_HOUSE_DOOR = 14
T_LAB_WALL = 15
T_LAB_DOOR = 16
T_ROOF_PLAYER = 17
T_ROOF_RIVAL = 18
T_ROOF_LAB = 19
T_SIGN = 20
T_LEDGE_JUMP_DOWN = 21 # This tile is the "cliff edge" you jump off
T_FENCE = 22
T_PC_WALL = 23 # PokeCenter-like wall
T_PC_DOOR = 24
T_MART_WALL = 25 # Mart-like wall
T_MART_DOOR = 26
T_ROOF_PC = 27
T_ROOF_MART = 28

T_NPC_SPAWN = 98 # Used to place NPCs, not a walkable tile itself usually
T_PLAYER_SPAWN = 99 # Only for initial game start

# --- Map IDs ---
MAP_LITTLEROOT = "littleroot_town"
MAP_ROUTE_101 = "route_101"
MAP_OLDALE = "oldale_town"

# --- Helper variables for map creation ---
PHW, PHD = T_PLAYER_HOUSE_WALL, T_PLAYER_HOUSE_DOOR
RHW, RHD = T_RIVAL_HOUSE_WALL, T_RIVAL_HOUSE_DOOR
LBW, LBD = T_LAB_WALL, T_LAB_DOOR
PCW, PCD = T_PC_WALL, T_PC_DOOR
MRW, MRD = T_MART_WALL, T_MART_DOOR
RPL, RRV, RLB, RPC, RMR = T_ROOF_PLAYER, T_ROOF_RIVAL, T_ROOF_LAB, T_ROOF_PC, T_ROOF_MART
TRE, PTH, SGN, FNC, WTR, TLG, FLR, FLY, LJD, NSP, PSP = \
    T_TREE, T_PATH_GRASS, T_SIGN, T_FENCE, T_WATER, T_TALL_GRASS, \
    T_FLOWER_RED, T_FLOWER_YELLOW, T_LEDGE_JUMP_DOWN, T_NPC_SPAWN, T_PLAYER_SPAWN
GRS = T_GRASS_REGULAR # Regular Grass shorthand

# --- Littleroot Town Map Data ---
littleroot_town_map_data = [
    # Row 0: Connection to Route 101 (North) - Centered path
    [TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, PTH, PTH, PTH, PTH, PTH, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, RLB, RLB, RLB, RLB, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, FLY, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, LBW, LBD, LBW, LBW, PTH, PTH, PTH, PTH, PTH, PTH, PTH, FLR, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, LBW, NSP, LBW, LBW, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE], # Prof Birch
    [TRE, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, SGN, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, SGN, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, FNC, FNC, FNC, FNC, FNC, PTH, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, PTH, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, RPL, RPL, RPL, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, RRV, RRV, RRV, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PHW, PHD, PHW, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, RHW, RHD, RHW, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PHW, NSP, PHW, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, RHW, RHW, RHW, PTH, PTH, PTH, PTH, PTH, TRE], # Mom
    [TRE, PTH, PTH, PSP, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE], # Player Spawn
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, LJD, LJD, LJD, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, TLG, TLG, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TLG, TLG, TLG, TRE],
    [TRE, TLG, TLG, PTH, PTH, PTH, PTH, WTR, WTR, WTR, PTH, PTH, PTH, PTH, PTH, PTH, WTR, WTR, WTR, PTH, PTH, PTH, PTH, PTH, PTH, TLG, TLG, TLG, TRE],
    [TRE, TRE, TRE, TRE, TRE, TRE, TRE, WTR, WTR, WTR, TRE, TRE, TRE, TRE, TRE, TRE, WTR, WTR, WTR, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE],
]

# --- Route 101 Map Data (Connects Littleroot North to Oldale South) ---
# Width: 15 tiles, Height: 25 tiles
route_101_map_data = [
    # Row 0: Connection to Oldale Town (North)
    [TRE, TRE, TRE, TRE, TRE, PTH, PTH, PTH, PTH, PTH, TRE, TRE, TRE, TRE, TRE],
    [TRE, TLG, TLG, TLG, PTH, PTH, GRS, GRS, PTH, PTH, PTH, TLG, TLG, TLG, TRE],
    [TRE, TLG, GRS, TLG, PTH, GRS, GRS, NSP, GRS, GRS, PTH, TLG, GRS, TLG, TRE], # NPC on Route
    [TRE, TLG, GRS, TLG, PTH, GRS, GRS, GRS, GRS, GRS, PTH, TLG, GRS, TLG, TRE],
    [TRE, TRE, GRS, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE, GRS, TRE, TRE],
    [TRE, GRS, GRS, GRS, PTH, GRS, GRS, GRS, GRS, GRS, PTH, GRS, GRS, GRS, TRE],
    [TRE, GRS, TRE, GRS, PTH, GRS, TLG, TLG, TLG, GRS, PTH, GRS, TRE, GRS, TRE],
    [TRE, GRS, TRE, GRS, PTH, GRS, TLG, NSP, TLG, GRS, PTH, GRS, TRE, GRS, TRE], # Another NPC
    [TRE, GRS, TRE, GRS, PTH, GRS, TLG, TLG, TLG, GRS, PTH, GRS, TRE, GRS, TRE],
    [TRE, GRS, GRS, GRS, PTH, GRS, GRS, GRS, GRS, GRS, PTH, GRS, GRS, GRS, TRE],
    [TRE, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, TRE],
    [TRE, TLG, TLG, PTH, GRS, GRS, GRS, GRS, GRS, GRS, GRS, PTH, TLG, TLG, TRE],
    [TRE, GRS, TLG, PTH, GRS, TLG, TLG, TLG, TLG, TLG, GRS, PTH, TLG, GRS, TRE],
    [TRE, GRS, GRS, PTH, GRS, TLG, GRS, GRS, GRS, TLG, GRS, PTH, GRS, GRS, TRE],
    [TRE, GRS, GRS, PTH, GRS, TLG, GRS, NSP, GRS, TLG, GRS, PTH, GRS, GRS, TRE], # Youngster NPC
    [TRE, GRS, GRS, PTH, GRS, TLG, GRS, GRS, GRS, TLG, GRS, PTH, GRS, GRS, TRE],
    [TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE],
    [TRE, TLG, PTH, GRS, GRS, GRS, TLG, TLG, TLG, GRS, GRS, GRS, PTH, TLG, TRE],
    [TRE, TLG, PTH, GRS, TLG, TLG, TLG, GRS, TLG, TLG, TLG, GRS, PTH, TLG, TRE],
    [TRE, PTH, PTH, GRS, GRS, GRS, GRS, GRS, GRS, GRS, GRS, GRS, PTH, PTH, TRE],
    [TRE, PTH, GRS, GRS, TRE, TRE, TRE, NSP, TRE, TRE, TRE, GRS, GRS, PTH, TRE], # Lass NPC
    [TRE, PTH, GRS, GRS, TRE, PTH, PTH, PTH, PTH, PTH, TRE, GRS, GRS, PTH, TRE],
    [TRE, PTH, PTH, PTH, TRE, PTH, GRS, GRS, GRS, PTH, TRE, PTH, PTH, PTH, TRE],
    [TRE, TRE, TRE, TRE, TRE, PTH, GRS, GRS, GRS, PTH, TRE, TRE, TRE, TRE, TRE],
    # Row 24: Connection to Littleroot (South)
    [TRE, TRE, TRE, TRE, TRE, PTH, PTH, PTH, PTH, PTH, TRE, TRE, TRE, TRE, TRE],
]

# --- Oldale Town Map Data ---
# Width: 25 tiles, Height: 20 tiles
oldale_town_map_data = [
    # Row 0: North Edge
    [TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, GRS, GRS, RPC, RPC, RPC, PTH, GRS, GRS, RMR, RMR, RMR, PTH, PTH, SGN, PTH, GRS, GRS, GRS, GRS, GRS, GRS, PTH, TRE], # Roofs
    [TRE, PTH, GRS, GRS, PCW, PCD, PCW, PTH, GRS, GRS, MRW, MRD, MRW, PTH, NSP, PTH, PTH, GRS, GRS, GRS, GRS, GRS, GRS, PTH, TRE], # Doors, NPC
    [TRE, PTH, GRS, GRS, PCW, NSP, PCW, PTH, GRS, GRS, MRW, MRW, MRW, PTH, PTH, PTH, PTH, GRS, GRS, FLY, GRS, FLR, GRS, PTH, TRE], # NPC in PC
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, GRS, GRS, GRS, GRS, GRS, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, GRS, GRS, GRS, GRS, GRS, GRS, PTH, TRE],
    [TRE, PTH, GRS, TRE, TRE, TRE, GRS, PTH, FNC, FNC, FNC, FNC, FNC, FNC, FNC, PTH, GRS, TRE, TRE, TRE, TRE, TRE, GRS, PTH, TRE],
    [TRE, PTH, GRS, TRE, NSP, TRE, GRS, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, GRS, TRE, NSP, TRE, GRS, TRE, GRS, PTH, TRE], # NPCs by trees
    [TRE, PTH, GRS, TRE, TRE, TRE, GRS, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, GRS, TRE, TRE, TRE, GRS, TRE, GRS, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, GRS, GRS, GRS, GRS, GRS, GRS, GRS, PTH, PTH, PTH, PTH, PTH, GRS, GRS, GRS, GRS, GRS, GRS, GRS, GRS, GRS, PTH, TRE],
    [TRE, PTH, GRS, TLG, TLG, GRS, GRS, GRS, GRS, PTH, SGN, PTH, PTH, PTH, GRS, TLG, TLG, GRS, GRS, FLR, GRS, FLY, GRS, PTH, TRE],
    [TRE, PTH, GRS, TLG, TLG, GRS, GRS, GRS, GRS, PTH, PTH, PTH, PTH, PTH, GRS, TLG, TLG, GRS, GRS, GRS, GRS, GRS, GRS, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, PTH, PTH, PTH, PTH, PTH, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE],
    [TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, PTH, GRS, GRS, GRS, PTH, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE],
    [TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, PTH, GRS, GRS, GRS, PTH, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE],
    # Row 19: Connection to Route 101 (South)
    [TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, PTH, PTH, PTH, PTH, PTH, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE],
]


# --- Game States ---
STATE_MAIN_MENU = 0 # Not used in this snippet
STATE_GAMEPLAY = 1  # Not used in this snippet

class DialogueBox:
    def __init__(self, screen, font_size=28):
        self.screen = screen
        self.font = pygame.font.Font(None, font_size) # Use default system font
        self.messages = [] # Queue of full messages
        self.active = False
        self.rect = pygame.Rect(0, SCREEN_HEIGHT - DIALOGUE_BOX_HEIGHT, SCREEN_WIDTH, DIALOGUE_BOX_HEIGHT)
        self.text_rect = self.rect.inflate(-30, -30) # Padding for text within the box
        
        # For displaying the current message (can be multi-line)
        self.current_message_surfaces = [] # List of surfaces, one for each line of the current message
        self.line_height = self.font.get_linesize()

    def show_message(self, text):
        """Adds a new message to the queue. If dialogue wasn't active, starts displaying."""
        self.messages.append(text)
        if not self.active:
            self.next_message()

    def next_message(self):
        """Processes the next message from the queue and prepares it for display."""
        if self.messages:
            self.active = True
            current_text = self.messages.pop(0)
            self.current_message_surfaces = [] # Clear previous lines

            words = current_text.split(' ')
            current_line_text = ""
            
            # Word wrapping logic
            for word in words:
                test_line = current_line_text + word + " "
                if self.font.size(test_line.strip())[0] <= self.text_rect.width:
                    current_line_text = test_line
                else:
                    # Render the completed line
                    line_surf = self.font.render(current_line_text.strip(), True, C_DIALOGUE_TEXT)
                    self.current_message_surfaces.append(line_surf)
                    current_line_text = word + " " # Start new line with current word
            
            # Add the last line
            if current_line_text.strip():
                line_surf = self.font.render(current_line_text.strip(), True, C_DIALOGUE_TEXT)
                self.current_message_surfaces.append(line_surf)
            
            # Ensure we don't try to display too many lines (truncate if necessary)
            max_lines = self.text_rect.height // self.line_height
            if len(self.current_message_surfaces) > max_lines:
                # This basic version just truncates. A more advanced version might have pages.
                self.current_message_surfaces = self.current_message_surfaces[:max_lines]
                # Optionally, re-queue the rest of the message or indicate more text.
                # For now, we just show what fits.

        else: # No more messages in the queue
            self.active = False
            self.current_message_surfaces = []

    def draw(self):
        """Draws the dialogue box and the current message if active."""
        if self.active and self.current_message_surfaces:
            pygame.draw.rect(self.screen, C_DIALOGUE_BG, self.rect)
            pygame.draw.rect(self.screen, C_DIALOGUE_BORDER, self.rect, 3) # Border

            current_y = self.text_rect.top
            for i, line_surf in enumerate(self.current_message_surfaces):
                if current_y + self.line_height <= self.text_rect.bottom: # Check if line fits
                    self.screen.blit(line_surf, (self.text_rect.left, current_y))
                    current_y += self.line_height
                else:
                    break # Stop drawing if lines exceed box height

    def handle_input(self, event):
        """Handles input for advancing dialogue."""
        if self.active and event.type == pygame.KEYDOWN:
            # Common keys to advance dialogue
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_e:
                self.next_message() # Try to display the next message in the queue
                return True # Input was handled
        return False

class Entity:
    def __init__(self, x, y, color, game, name="Entity"):
        self.x = x  # Tile x-coordinate in world space of the current map
        self.y = y  # Tile y-coordinate in world space of the current map
        self.color = color
        self.game = game # Reference to the main game object (assumed to exist)
        self.name = name

    def draw(self, surface, camera_x, camera_y):
        """Draws the entity on the screen relative to the camera."""
        screen_x = self.x * TILE_SIZE - camera_x
        screen_y = self.y * TILE_SIZE - camera_y

        # Basic culling: Only draw if visible on screen (within game area)
        if screen_x + TILE_SIZE > 0 and screen_x < SCREEN_WIDTH and \
           screen_y + TILE_SIZE > 0 and screen_y < GAME_AREA_HEIGHT:
            rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, self.color, rect)
            # Simple detail (e.g. eyes or a smaller inner square)
            detail_size = TILE_SIZE // 3
            detail_offset = (TILE_SIZE - detail_size) // 2 # Center the detail
            detail_rect = pygame.Rect(screen_x + detail_offset, screen_y + detail_offset, detail_size, detail_size)
            pygame.draw.rect(surface, BLACK, detail_rect)

# --- ADDED: Basic NPC Class ---
class NPC(Entity):
    def __init__(self, x, y, game, name="NPC", dialogue="Hello there, traveler!"):
        super().__init__(x, y, C_NPC, game, name=name)
        self.dialogue = dialogue

    def interact(self, interactor): # Interactor is usually the player
        """Called when the player interacts with this NPC."""
        # Replace [Rival] with actual rival name if implemented
        formatted_dialogue = self.dialogue.replace("[Rival]", self.game.rival_name if hasattr(self.game, 'rival_name') else "your Rival")
        self.game.dialogue_box.show_message(f"{self.name}: {formatted_dialogue}")
        # NPCs could have more complex interaction logic (e.g. face player)

# --- ADDED: is_walkable function ---
def is_walkable(tile_type):
    """Checks if a tile type is generally walkable."""
    walkable_tiles = [
        T_PATH_GRASS,
        T_GRASS_REGULAR,
        T_TALL_GRASS,
        T_FLOWER_RED, # Can walk on flowers
        T_FLOWER_YELLOW,
        T_SAND,
        # T_LEDGE_JUMP_DOWN is handled specially, not "walkable" in generic sense
    ]
    # Tiles that are part of buildings but might be spawn points (NPCs inside)
    # The player shouldn't walk ON these, but NPCs might be on them.
    # Actual entry into buildings would be via door tiles.
    non_walkable_by_player = [
        T_PLAYER_SPAWN, # Player starts here, but it's usually on a walkable tile type
        T_NPC_SPAWN,    # NPCs spawn here, usually on a walkable tile type
    ]

    if tile_type in walkable_tiles:
        return True
    # Add any other specific non-walkable tiles here if needed
    if tile_type in [T_TREE, T_WATER, T_BUILDING_WALL, T_PLAYER_HOUSE_WALL,
                     T_RIVAL_HOUSE_WALL, T_LAB_WALL, T_ROOF_PLAYER, T_ROOF_RIVAL,
                     T_ROOF_LAB, T_FENCE, T_PC_WALL, T_MART_WALL, T_ROOF_PC, T_ROOF_MART]:
        return False
    # Doors and signs are not "walkable" in the sense of passing through; they trigger interactions.
    # Ledges are also special.
    return False # Default to not walkable if not specified

class Player(Entity):
    def __init__(self, x, y, game):
        super().__init__(x, y, C_PLAYER, game, name="Player") # Name can be changed later

    def move(self, dx, dy):
        """Attempts to move the player by dx, dy tiles."""
        if self.game.dialogue_box.active:
            return "blocked_dialogue" # Cannot move if dialogue is active

        new_x, new_y = self.x + dx, self.y + dy

        # --- Handle Map Transitions (Order: Before boundary checks of current map) ---
        # From Littleroot to Route 101 (North Exit)
        if self.game.current_map_id == MAP_LITTLEROOT and new_y < 0 and 11 <= self.x <= 15: # Path is from x=11 to x=15
            # Route 101 south entrance path is x=5 to x=9 (5 tiles wide)
            # Littleroot x=11 maps to R101 x=5; Littleroot x=15 maps to R101 x=9
            self.game.change_map(MAP_ROUTE_101, (self.x - 11) + 5, self.game.maps_data[MAP_ROUTE_101]['height'] - 1)
            return "map_changed"
        # From Route 101 to Littleroot (South Exit)
        elif self.game.current_map_id == MAP_ROUTE_101 and new_y >= self.game.current_map_height_tiles and 5 <= self.x <= 9:
            self.game.change_map(MAP_LITTLEROOT, (self.x - 5) + 11, 0)
            return "map_changed"
        # From Route 101 to Oldale (North Exit)
        elif self.game.current_map_id == MAP_ROUTE_101 and new_y < 0 and 5 <= self.x <= 9:
            # Oldale south entrance path is x=9 to x=13 (5 tiles wide)
            # R101 x=5 maps to Oldale x=9; R101 x=9 maps to Oldale x=13
            self.game.change_map(MAP_OLDALE, (self.x - 5) + 9, self.game.maps_data[MAP_OLDALE]['height'] - 1)
            return "map_changed"
        # From Oldale to Route 101 (South Exit)
        elif self.game.current_map_id == MAP_OLDALE and new_y >= self.game.current_map_height_tiles and 9 <= self.x <= 13:
            self.game.change_map(MAP_ROUTE_101, (self.x - 9) + 5, 0)
            return "map_changed"

        # --- Standard Movement & Collision within current map ---
        # Check map boundaries for the new position
        if not (0 <= new_x < self.game.current_map_width_tiles and \
                0 <= new_y < self.game.current_map_height_tiles):
            return "blocked_boundary" # Tried to move off map where there's no connection

        target_tile_type = self.game.current_map_data[new_y][new_x]
        
        # Check for NPC at the target location (NPCs block movement)
        for npc in self.game.npcs: # Assuming game object has a list of npcs
            if npc.x == new_x and npc.y == new_y:
                npc.interact(self) # Player interacts with NPC
                return "interacted_npc" # Movement blocked by NPC

        # Tile-based interactions (Signs, Doors). These usually block movement to the tile.
        interaction_message = None
        # --- COMPLETED: Player.move interaction logic ---
        if target_tile_type == T_PLAYER_HOUSE_DOOR: interaction_message = "My house. It's cozy inside!"
        elif target_tile_type == T_RIVAL_HOUSE_DOOR: interaction_message = f"This is {self.game.rival_name if hasattr(self.game, 'rival_name') else '[Rival]'}'s house."
        elif target_tile_type == T_LAB_DOOR: interaction_message = "Professor Birch's Pokémon Lab. I wonder if he's in?"
        elif target_tile_type == T_PC_DOOR: interaction_message = "It's a Pokémon Center. Let's heal up!" # Placeholder for actual healing
        elif target_tile_type == T_MART_DOOR: interaction_message = "It's a Poké Mart. Need anything?" # Placeholder for shop
        elif target_tile_type == T_SIGN:
            # Sign messages could be map-specific or globally defined by x,y + map_id
            if self.game.current_map_id == MAP_LITTLEROOT:
                if new_x == 3 and new_y == 6: interaction_message = "LITTLEROOT TOWN - A town that can't be shaded any hue."
                elif new_x == 22 and new_y == 6: interaction_message = "ROUTE 101 ahead. Tall grass! Wild Pokémon live there!"
            elif self.game.current_map_id == MAP_OLDALE:
                if new_x == 15 and new_y == 2 : interaction_message = "OLDALE TOWN - Where things get started."
                elif new_x == 10 and new_y == 12: interaction_message = "North: Route 103. West: Petalburg Woods. (Not yet implemented)"
            else: interaction_message = "It's a wooden sign. It's surprisingly informative."
        
        if interaction_message:
            self.game.dialogue_box.show_message(interaction_message)
            return "interacted_tile" # Player interacted, movement blocked for this attempt

        # --- ADDED: Ledge Jumping Logic ---
        # Player is trying to move ONTO a ledge tile.
        if target_tile_type == T_LEDGE_JUMP_DOWN:
            if dy == 1: # Moving downwards onto the ledge tile
                self.x = new_x
                # Player lands one tile BELOW the ledge tile they "jumped from"
                # So, if new_y is the ledge tile, they land at new_y + 1
                self.y = new_y + 1 
                
                # Ensure the landing spot is within map bounds
                if not (0 <= self.y < self.game.current_map_height_tiles):
                    # This case should ideally not happen with good map design,
                    # but as a fallback, revert to ledge tile if landing is out of bounds.
                    self.y = new_y
                    return "blocked_ledge_fall_boundary" # Or handle as error

                # Check if landing spot is walkable (e.g., not into a tree or water after jump)
                # This requires checking the tile at self.x, self.y (the new landing spot)
                landing_tile_type = self.game.current_map_data[self.y][self.x]
                if not is_walkable(landing_tile_type) and landing_tile_type != T_LEDGE_JUMP_DOWN: # Can't jump onto another ledge immediately
                     # Stuck! Revert to before the ledge.
                     self.x -= dx # Revert x
                     self.y = new_y -1 # Revert y to tile before ledge
                     return "blocked_ledge_landing"

                self.game.dialogue_box.show_message("Jumped down the ledge!") # Optional feedback
                return "jumped_ledge"
            else: # Trying to move onto a ledge from sides, or upwards from below it
                return "blocked_collision_ledge" # Ledges are one-way (down)

        # Standard walkable check
        if is_walkable(target_tile_type):
            self.x = new_x
            self.y = new_y
            # Check for tall grass for potential encounters (logic to be added in game loop)
            if target_tile_type == T_TALL_GRASS:
                return "moved_tall_grass"
            return "moved"
        else:
            # If it's not walkable and not any special interaction tile, it's a collision
            return "blocked_collision_solid"


# --- Placeholder for Game Class (to make the snippet runnable for testing parts) ---
# This would normally be a much larger class managing the game loop, state, etc.
class GameMock:
    def __init__(self):
        pygame.init() # Initialize Pygame here if running this snippet standalone for testing
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.dialogue_box = DialogueBox(self.screen)
        self.player = None # Will be set after map load
        self.npcs = []
        
        # Mock map data for testing
        self.maps_data = {
            MAP_LITTLEROOT: {'data': littleroot_town_map_data, 'width': len(littleroot_town_map_data[0]), 'height': len(littleroot_town_map_data)},
            MAP_ROUTE_101: {'data': route_101_map_data, 'width': len(route_101_map_data[0]), 'height': len(route_101_map_data)},
            MAP_OLDALE: {'data': oldale_town_map_data, 'width': len(oldale_town_map_data[0]), 'height': len(oldale_town_map_data)},
        }
        self.current_map_id = MAP_LITTLEROOT
        self.current_map_data = self.maps_data[self.current_map_id]['data']
        self.current_map_width_tiles = self.maps_data[self.current_map_id]['width']
        self.current_map_height_tiles = self.maps_data[self.current_map_id]['height']
        self.rival_name = "Brendan" # Example rival name

        self.load_map(self.current_map_id)


    def load_map(self, map_id):
        """Loads map data, finds player spawn, and creates NPCs."""
        if map_id not in self.maps_data:
            print(f"Error: Map ID {map_id} not found.")
            return

        self.current_map_id = map_id
        map_info = self.maps_data[map_id]
        self.current_map_data = map_info['data']
        self.current_map_width_tiles = map_info['width']
        self.current_map_height_tiles = map_info['height']
        
        self.npcs = [] # Clear NPCs from previous map
        player_spawn_pos = None

        for r, row in enumerate(self.current_map_data):
            for c, tile in enumerate(row):
                if tile == T_PLAYER_SPAWN and self.player is None: # Only use initial spawn once
                    player_spawn_pos = (c, r)
                    # Replace spawn marker with a walkable tile (e.g., path)
                    self.current_map_data[r][c] = T_PATH_GRASS 
                elif tile == T_NPC_SPAWN:
                    # Example: Add specific NPCs based on map and location
                    npc_name = "Youngster"
                    npc_dialogue = "I like shorts! They're comfy and easy to wear!"
                    if map_id == MAP_LITTLEROOT and c == 12 and r == 3: # Prof Birch
                        npc_name = "Prof. Birch"
                        npc_dialogue = "Welcome to the world of Pokémon! Are you ready for an adventure?"
                    elif map_id == MAP_LITTLEROOT and c == 3 and r == 12: # Mom
                        npc_name = "Mom"
                        npc_dialogue = "Be careful out there, sweetie! And don't forget to change your underwear!"
                    
                    self.npcs.append(NPC(c, r, self, name=npc_name, dialogue=npc_dialogue))
                    # Replace NPC spawn marker with a walkable tile
                    self.current_map_data[r][c] = T_PATH_GRASS 
        
        if self.player is None and player_spawn_pos:
            self.player = Player(player_spawn_pos[0], player_spawn_pos[1], self)
        elif self.player: # Player already exists, update position if needed (handled by change_map)
            pass


    def change_map(self, new_map_id, player_new_x, player_new_y):
        """Handles changing maps and repositioning the player."""
        print(f"Changing map from {self.current_map_id} to {new_map_id}. Player to ({player_new_x}, {player_new_y})")
        self.current_map_id = new_map_id
        map_info = self.maps_data[self.current_map_id]
        self.current_map_data = map_info['data']
        self.current_map_width_tiles = map_info['width']
        self.current_map_height_tiles = map_info['height']
        
        self.player.x = player_new_x
        self.player.y = player_new_y
        
        self.load_map(new_map_id) # Reload NPCs for the new map
        # Important: load_map will clear and repopulate self.npcs.
        # Player position is set before load_map so it's not overwritten if T_PLAYER_SPAWN logic runs.

    def run_basic_test(self):
        """A very simple test loop for dialogue and player movement."""
        if not self.player:
            print("Player not initialized. Cannot run test.")
            return

        clock = pygame.time.Clock()
        running = True
        
        # Test Dialogue
        self.dialogue_box.show_message("This is a very long test message to see how the wrapping behaves and if it correctly displays multiple lines across the screen without any issues. Let's add even more text to really push it to its limits and ensure everything is A-Okay!")
        self.dialogue_box.show_message("This is a second, shorter message.")

        camera_x, camera_y = 0,0 # Simple camera

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Dialogue input handling first
                if self.dialogue_box.handle_input(event):
                    continue # Dialogue handled input, skip player movement

                # Player movement input (only if dialogue is not active)
                if not self.dialogue_box.active and event.type == pygame.KEYDOWN:
                    action_result = ""
                    if event.key == pygame.K_LEFT:
                        action_result = self.player.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        action_result = self.player.move(1, 0)
                    elif event.key == pygame.K_UP:
                        action_result = self.player.move(0, -1)
                    elif event.key == pygame.K_DOWN:
                        action_result = self.player.move(0, 1)
                    if action_result: print(f"Player action: {action_result}, New Pos: ({self.player.x}, {self.player.y}) on {self.current_map_id}")


            # Update camera to follow player (simple version)
            camera_x = self.player.x * TILE_SIZE - SCREEN_WIDTH // 2 + TILE_SIZE // 2
            camera_y = self.player.y * TILE_SIZE - GAME_AREA_HEIGHT // 2 + TILE_SIZE // 2

            # Clamp camera to map boundaries
            camera_x = max(0, min(camera_x, self.current_map_width_tiles * TILE_SIZE - SCREEN_WIDTH))
            camera_y = max(0, min(camera_y, self.current_map_height_tiles * TILE_SIZE - GAME_AREA_HEIGHT))


            # Drawing
            self.screen.fill(C_GRASS_REGULAR) # Default background for game area

            # Draw Tiles (basic example, real game would be more optimized)
            for r_idx, row_val in enumerate(self.current_map_data):
                for c_idx, tile_val in enumerate(row_val):
                    tile_screen_x = c_idx * TILE_SIZE - camera_x
                    tile_screen_y = r_idx * TILE_SIZE - camera_y
                    
                    # Cull tiles not on screen
                    if tile_screen_x + TILE_SIZE < 0 or tile_screen_x > SCREEN_WIDTH or \
                       tile_screen_y + TILE_SIZE < 0 or tile_screen_y > GAME_AREA_HEIGHT:
                        continue

                    color = BLACK # Default for unknown tiles
                    if tile_val == T_PATH_GRASS: color = C_PATH_GRASS
                    elif tile_val == T_GRASS_REGULAR: color = C_GRASS_REGULAR
                    elif tile_val == T_TALL_GRASS: color = C_TALL_GRASS
                    elif tile_val == T_TREE: color = C_TREE_LEAVES # Use leaves color for main tree block
                    elif tile_val == T_WATER: color = C_WATER
                    elif tile_val == T_FLOWER_RED: color = C_FLOWER_RED
                    elif tile_val == T_FLOWER_YELLOW: color = C_FLOWER_YELLOW
                    elif tile_val == T_FENCE: color = C_FENCE
                    elif tile_val == T_LEDGE_JUMP_DOWN: color = C_LEDGE
                    # Building parts
                    elif tile_val in [T_PLAYER_HOUSE_WALL, T_RIVAL_HOUSE_WALL, T_LAB_WALL, T_PC_WALL, T_MART_WALL, T_BUILDING_WALL]:
                        color = C_BUILDING_WALL_LIGHT # Generic wall color
                        if tile_val == T_PC_WALL: color = C_PC_WALL
                        if tile_val == T_MART_WALL: color = C_MART_WALL
                    elif tile_val in [T_PLAYER_HOUSE_DOOR, T_RIVAL_HOUSE_DOOR, T_LAB_DOOR, T_PC_DOOR, T_MART_DOOR]:
                        color = C_DOOR
                    elif tile_val in [T_ROOF_PLAYER, T_ROOF_RIVAL, T_ROOF_LAB, T_ROOF_PC, T_ROOF_MART]:
                        color = C_ROOF_GRAY # Generic roof
                        if tile_val == T_ROOF_PLAYER or tile_val == T_ROOF_RIVAL : color = C_ROOF_RED
                        if tile_val == T_ROOF_PC: color = C_ROOF_GRAY
                        if tile_val == T_ROOF_MART: color = C_ROOF_MART
                    elif tile_val == T_SIGN: color = C_SIGN
                    
                    pygame.draw.rect(self.screen, color, (tile_screen_x, tile_screen_y, TILE_SIZE, TILE_SIZE))

            # Draw NPCs
            for npc in self.npcs:
                npc.draw(self.screen, camera_x, camera_y)
            
            # Draw Player
            if self.player:
                self.player.draw(self.screen, camera_x, camera_y)

            # Draw Dialogue Box on top
            self.dialogue_box.draw()
            
            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()

if __name__ == '__main__':
    # This allows you to run this file directly to test the implemented features.
    # Note: This is a MOCK game loop. A full game would have more states,
    # a proper Game class, event handling, etc.
    game_test = GameMock()
    game_test.run_basic_test()

