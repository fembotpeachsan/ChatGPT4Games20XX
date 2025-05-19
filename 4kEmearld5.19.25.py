import tkinter as tk # Not used in this version, but kept as per original
import pygame
import os
import time
import random # For potential future use (e.g., NPC movement)

# --- Game Constants ---
SCREEN_WIDTH = 800  # Width of the game screen in pixels (viewport)
SCREEN_HEIGHT = 600 # Height of the game screen in pixels (viewport)
TILE_SIZE = 32      # Size of each tile in pixels. For authentic GBA feel, 16x16 is common.
                    # If TILE_SIZE is changed, map data and entity scaling might need adjustments.

# Viewport dimensions in tiles
VIEWPORT_WIDTH_TILES = SCREEN_WIDTH // TILE_SIZE
VIEWPORT_HEIGHT_TILES = (SCREEN_HEIGHT - 100) // TILE_SIZE # Reserve 100px for dialogue

FPS = 60
DIALOGUE_BOX_HEIGHT = 100
GAME_AREA_HEIGHT = SCREEN_HEIGHT - DIALOGUE_BOX_HEIGHT


# --- Colors (Gen 3 Inspired - simplified) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Environment
C_PATH_GRASS = (136, 192, 112) # Light green for paths, general ground
C_GRASS_REGULAR = (104, 168, 88) # Standard grass
C_TALL_GRASS = (64, 128, 72)   # Darker green for tall grass
C_TREE_TRUNK = (112, 80, 48)   # Brown for tree trunks
C_TREE_LEAVES = (48, 96, 48)   # Dark green for tree leaves/tops
C_WATER = (80, 128, 200)       # Blue for water
C_FLOWER_RED = (208, 72, 48)
C_FLOWER_YELLOW = (248, 224, 96)
C_SAND = (216, 200, 160)

# Buildings & Structures
C_BUILDING_WALL_LIGHT = (200, 160, 120) # Light color for some building walls
C_BUILDING_WALL_DARK = (160, 128, 96)  # Darker variant for building walls
C_ROOF_RED = (192, 80, 48)       # Red roof (Player's house)
C_ROOF_BLUE = (80, 96, 160)      # Blue roof (Rival's house)
C_ROOF_GRAY = (128, 128, 128)    # Gray roof (Lab, PokeCenter-like)
C_DOOR = (96, 64, 32)          # Dark brown for doors
C_SIGN = (144, 112, 80)        # Wooden sign
C_LEDGE = (120, 176, 104)      # Ledge color, slightly different from grass
C_FENCE = (160, 144, 128)      # Fence color

# Entities & UI
C_PLAYER = (224, 80, 64)       # Player (can be replaced with sprite) - Reddish
C_NPC = (80, 144, 224)         # NPC (can be replaced with sprite) - Bluish
C_DIALOGUE_BG = (40, 40, 40)
C_DIALOGUE_TEXT = WHITE
C_DIALOGUE_BORDER = (100, 100, 100)

# --- Tile Types ---
# These are numeric constants used in the map data arrays.
# Environment
T_PATH_GRASS = 0    # Walkable light grass / dirt path mix
T_GRASS_REGULAR = 1 # Standard non-tall grass, walkable
T_TALL_GRASS = 2    # Tall grass (for encounters later), walkable
T_WATER = 3         # Impassable water
T_TREE = 4          # Impassable tree (could be multi-tile later)
T_FLOWER_RED = 5
T_FLOWER_YELLOW = 6
T_SAND = 7

# Buildings & Structures
T_BUILDING_WALL = 10     # Generic impassable building wall
T_PLAYER_HOUSE_WALL = 11 # Specific wall for player house
T_PLAYER_HOUSE_DOOR = 12 # Player's house door (interactive)
T_RIVAL_HOUSE_WALL = 13
T_RIVAL_HOUSE_DOOR = 14
T_LAB_WALL = 15
T_LAB_DOOR = 16
T_ROOF_PLAYER = 17       # Red roof tile
T_ROOF_RIVAL = 18        # Blue roof tile
T_ROOF_LAB = 19          # Gray/other roof tile
T_SIGN = 20              # Interactive sign
T_LEDGE_JUMP_DOWN = 21   # One-way jumpable ledge (jump downwards on map)
T_FENCE = 22

# Special / Meta
T_NPC_SPAWN = 98    # For placing NPCs during init, then replaced
T_PLAYER_SPAWN = 99 # For placing player during init

# --- Littleroot Town Map Data (Example) ---
# This map is larger than the screen to demonstrate camera scrolling.
# Dimensions: 30 tiles wide, 25 tiles high
# (0,0) is top-left. Player's house bottom-left-ish, Rival's bottom-right-ish, Lab top-center-ish.

# Helper variables for readability in map creation
PHW = T_PLAYER_HOUSE_WALL
PHD = T_PLAYER_HOUSE_DOOR
RHW = T_RIVAL_HOUSE_WALL
RHD = T_RIVAL_HOUSE_DOOR
LBW = T_LAB_WALL
LBD = T_LAB_DOOR
RPL = T_ROOF_PLAYER
RRV = T_ROOF_RIVAL
RLB = T_ROOF_LAB
TRE = T_TREE
PTH = T_PATH_GRASS
SGN = T_SIGN
FNC = T_FENCE
WTR = T_WATER
TLG = T_TALL_GRASS # Tall Grass
FLR = T_FLOWER_RED
FLY = T_FLOWER_YELLOW
LJD = T_LEDGE_JUMP_DOWN
NSP = T_NPC_SPAWN # NPC Spawn Point
PSP = T_PLAYER_SPAWN # Player Spawn Point

littleroot_town_map_data = [
    [TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, RLB, RLB, RLB, RLB, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, FLY, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, LBW, LBD, LBW, LBW, PTH, PTH, PTH, PTH, PTH, PTH, PTH, FLR, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, LBW, NSP, LBW, LBW, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE], # NPC in Lab
    [TRE, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, SGN, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, SGN, PTH, PTH, PTH, PTH, PTH, PTH, TRE], # Signs
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, FNC, FNC, FNC, FNC, FNC, PTH, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, PTH, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, PTH, TRE], # Fence line
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, RPL, RPL, RPL, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, RRV, RRV, RRV, PTH, PTH, PTH, PTH, PTH, TRE], # Roofs
    [TRE, PTH, PHW, PHD, PHW, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, RHW, RHD, RHW, PTH, PTH, PTH, PTH, PTH, TRE], # Doors
    [TRE, PTH, PHW, NSP, PHW, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, RHW, RHW, RHW, PTH, PTH, PTH, PTH, PTH, TRE], # Player's Mom NPC
    [TRE, PTH, PTH, PSP, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE], # Player Spawn
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, LJD, LJD, LJD, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE], # Ledges
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, TLG, TLG, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TLG, TLG, TLG, TRE], # Route 101 start (Tall Grass)
    [TRE, TLG, TLG, PTH, PTH, PTH, PTH, WTR, WTR, WTR, PTH, PTH, PTH, PTH, PTH, PTH, WTR, WTR, WTR, PTH, PTH, PTH, PTH, PTH, PTH, TLG, TLG, TLG, TRE], # Water
    [TRE, TRE, TRE, TRE, TRE, TRE, TRE, WTR, WTR, WTR, TRE, TRE, TRE, TRE, TRE, TRE, WTR, WTR, WTR, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE],
]


# Calculate world map dimensions from the map data
WORLD_MAP_HEIGHT_TILES = len(littleroot_town_map_data)
WORLD_MAP_WIDTH_TILES = len(littleroot_town_map_data[0]) if WORLD_MAP_HEIGHT_TILES > 0 else 0


class DialogueBox:
    """Handles displaying dialogue messages."""
    def __init__(self, screen, font_size=28): # Slightly larger font
        self.screen = screen
        self.font = pygame.font.Font(None, font_size)
        self.messages = []
        self.current_message_surface = None
        self.active = False
        self.rect = pygame.Rect(0, SCREEN_HEIGHT - DIALOGUE_BOX_HEIGHT, SCREEN_WIDTH, DIALOGUE_BOX_HEIGHT)
        # Padding for text, increased slightly
        self.text_rect = self.rect.inflate(-30, -30)

    def show_message(self, text):
        self.messages.append(text)
        if not self.active:
            self.next_message()

    def next_message(self):
        if self.messages:
            message = self.messages.pop(0)
            # Basic word wrapping
            words = message.split(' ')
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if self.font.size(test_line)[0] < self.text_rect.width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)
            
            # For simplicity, we'll take the first line for now.
            # A more robust solution would handle multi-line display within the box.
            # Or, pass each line as a separate message.
            if lines:
                 self.current_message_surface = self.font.render(lines[0].strip(), True, C_DIALOGUE_TEXT)
            else: # Should not happen if message has text
                 self.current_message_surface = self.font.render("", True, C_DIALOGUE_TEXT)

            self.active = True
        else:
            self.active = False
            self.current_message_surface = None

    def draw(self):
        if self.active and self.current_message_surface:
            pygame.draw.rect(self.screen, C_DIALOGUE_BG, self.rect)
            pygame.draw.rect(self.screen, C_DIALOGUE_BORDER, self.rect, 3) # Thicker border
            self.screen.blit(self.current_message_surface, self.text_rect.topleft)

    def handle_input(self, event):
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_e:
                self.next_message()
                return True
        return False

class Entity:
    """Base class for game entities like Player and NPC."""
    def __init__(self, x, y, color, game, name="Entity"):
        self.x = x  # Tile x-coordinate in world space
        self.y = y  # Tile y-coordinate in world space
        self.color = color
        self.game = game
        self.name = name

    def draw(self, surface, camera_x, camera_y):
        """Draws the entity on the Pygame surface, adjusted by camera."""
        # Calculate screen position based on camera
        screen_x = self.x * TILE_SIZE - camera_x
        screen_y = self.y * TILE_SIZE - camera_y

        # Only draw if visible on screen (basic culling)
        if screen_x + TILE_SIZE > 0 and screen_x < SCREEN_WIDTH and \
           screen_y + TILE_SIZE > 0 and screen_y < GAME_AREA_HEIGHT:
            rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, self.color, rect)
            # Simple detail (e.g. eyes or a smaller inner square)
            detail_size = TILE_SIZE // 3
            detail_rect = pygame.Rect(screen_x + detail_size, screen_y + detail_size, detail_size, detail_size)
            pygame.draw.rect(surface, BLACK, detail_rect)
            # In a real game, you'd blit a sprite here:
            # surface.blit(self.sprite_image, (screen_x, screen_y))


class Player(Entity):
    """Represents the player character."""
    def __init__(self, x, y, game):
        super().__init__(x, y, C_PLAYER, game, name="Player")
        # Add any player-specific attributes here (e.g., inventory, party)

    def move(self, dx, dy):
        if self.game.dialogue_box.active:
            return False

        new_x, new_y = self.x + dx, self.y + dy

        if 0 <= new_x < WORLD_MAP_WIDTH_TILES and 0 <= new_y < WORLD_MAP_HEIGHT_TILES:
            target_tile_type = self.game.current_map_data[new_y][new_x]
            
            # Check for NPC at the target location
            for npc in self.game.npcs:
                if npc.x == new_x and npc.y == new_y:
                    npc.interact(self) # Pass player to NPC for context
                    return True # Interaction occurred

            # Tile-based interactions
            interaction_message = None
            if target_tile_type == T_PLAYER_HOUSE_DOOR:
                interaction_message = "My house."
            elif target_tile_type == T_RIVAL_HOUSE_DOOR:
                interaction_message = "This is [Rival]'s house. They're probably out training."
            elif target_tile_type == T_LAB_DOOR:
                interaction_message = "Professor Birch's Pokémon Lab."
            elif target_tile_type == T_SIGN:
                # You could have different signs with different messages
                # For now, a generic one. Could be based on sign's x,y.
                if new_x == 3 and new_y == 6: # Example specific sign
                     interaction_message = "Littleroot Town - A town that can't be shaded any hue."
                elif new_x == 22 and new_y == 6:
                     interaction_message = "Route 101 ahead."
                else:
                     interaction_message = "It's a wooden sign. It says something."


            if interaction_message:
                self.game.dialogue_box.show_message(interaction_message)
                return True # Interaction occurred, don't move into door/sign

            # Check for impassable tiles
            impassable_tiles = [T_TREE, T_WATER, T_BUILDING_WALL, T_PLAYER_HOUSE_WALL,
                                T_RIVAL_HOUSE_WALL, T_LAB_WALL, T_ROOF_LAB, T_ROOF_PLAYER,
                                T_ROOF_RIVAL, T_FENCE]
            if target_tile_type in impassable_tiles:
                return False # Collision with wall/obstacle

            # Handle Ledges
            # If player is trying to move UP onto the bottom of a ledge, block it.
            if dy == -1 and self.game.current_map_data[self.y][self.x] == T_LEDGE_JUMP_DOWN:
                 return False # Cannot jump up a ledge

            # If moving onto a ledge tile from above it
            if target_tile_type == T_LEDGE_JUMP_DOWN:
                # Check if player is *above* the ledge tile before moving onto it
                tile_above_player = self.game.current_map_data[self.y][self.x]
                # Allow jump if moving from a non-ledge tile onto a ledge tile in the jump direction
                if dy == 1 and tile_above_player != T_LEDGE_JUMP_DOWN : # Moving down onto a ledge
                    self.x = new_x
                    self.y = new_y + 1 # Automatically jump one more tile down
                    self.game.dialogue_box.show_message("Whee! Jumped the ledge.")
                    # Clamp y to prevent going out of bounds after jump
                    self.y = max(0, min(self.y, WORLD_MAP_HEIGHT_TILES -1))
                    return False # Moved
                else: # Trying to walk onto ledge from side or walk up it
                    return False # Block walking onto ledge sideways or up

            # If no collision or interaction, move the player
            self.x = new_x
            self.y = new_y
            return False # Moved, no specific interaction
        return False # Out of bounds

class NPC(Entity):
    """Represents a Non-Player Character."""
    def __init__(self, x, y, game, name="Villager", dialogue=None, color=C_NPC):
        super().__init__(x, y, color, game, name=name)
        self.dialogue = dialogue if dialogue else [f"Hello, {game.player.name if game.player else 'trainer'}!", "It's a fine day."]
        self.dialogue_index = 0

    def interact(self, interactor): # Interactor is usually the player
        """Initiates dialogue with the NPC."""
        if self.dialogue:
            # Personalize if possible
            current_dialogue = self.dialogue[self.dialogue_index]
            if self.game.player:
                current_dialogue = current_dialogue.replace("{player_name}", self.game.player.name)
            
            self.game.dialogue_box.show_message(f"{self.name}: {current_dialogue}")
            self.dialogue_index = (self.dialogue_index + 1) % len(self.dialogue)
        else:
            self.game.dialogue_box.show_message(f"{self.name} doesn't have much to say.")
    
    # Placeholder for future NPC movement or AI
    def update(self):
        pass


class Game:
    """Main class to manage game state, updates, and rendering."""
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("GBA Style Tile Game")
        self.clock = pygame.time.Clock()
        self.running = True

        self.current_map_data = littleroot_town_map_data # Start with Littleroot
        self.dialogue_box = DialogueBox(self.screen)

        self.player = None # Initialized in _initialize_entities
        self.npcs = []
        self._initialize_entities() # This will also set self.player

        # Camera state
        self.camera_x = 0
        self.camera_y = 0
        self.update_camera() # Initial camera position

    def _initialize_entities(self):
        """Scans the map for player start and NPC locations."""
        player_spawn_pos = None
        for r, row in enumerate(self.current_map_data):
            for c, tile in enumerate(row):
                if tile == T_PLAYER_SPAWN and self.player is None:
                    self.player = Player(c, r, self)
                    player_spawn_pos = (c,r)
                    # Replace spawn tile with path/grass after player is created
                    self.current_map_data[r][c] = T_PATH_GRASS
                elif tile == T_NPC_SPAWN:
                    # Example NPC definitions
                    if c == 3 and r == 12: # Approximate Player's house interior
                        mom_dialogue = [
                            "Oh, {player_name}! Off on an adventure?",
                            "Don't forget to change your underwear!",
                            "Professor Birch was looking for you earlier."
                        ]
                        self.npcs.append(NPC(c, r, self, name="Mom", dialogue=mom_dialogue, color=(230,100,120)))
                    elif c == 12 and r == 3: # Approximate Lab interior
                         prof_dialogue = [
                             "Welcome to the world of Pokémon!",
                             "I'm Professor Birch. This is my lab.",
                             "Are you ready to choose your first Pokémon?" # Tease for future
                         ]
                         self.npcs.append(NPC(c,r,self, name="Prof. Birch", dialogue=prof_dialogue, color=(100,100,100)))
                    else: # Generic NPC
                        self.npcs.append(NPC(c, r, self, name=f"Villager {len(self.npcs)+1}"))
                    # Replace spawn tile
                    self.current_map_data[r][c] = T_PATH_GRASS


        if self.player is None: # Fallback if no T_PLAYER_SPAWN found
            print("Warning: No T_PLAYER_SPAWN found. Placing player at (5,5) on current map.")
            self.player = Player(5, 5, self)
            if self.current_map_data[5][5] in [T_TREE, T_WATER, T_BUILDING_WALL]: # Ensure it's not a wall
                self.current_map_data[5][5] = T_PATH_GRASS
        
        # If player name is default, give a default name
        if self.player and self.player.name == "Player": # Default from Entity
            self.player.name = "Ash" # Or get from user input later


    def update_camera(self):
        """Updates camera position to follow the player, centered."""
        if self.player:
            # Target camera position to center player
            target_cam_x = self.player.x * TILE_SIZE - SCREEN_WIDTH // 2 + TILE_SIZE // 2
            target_cam_y = self.player.y * TILE_SIZE - GAME_AREA_HEIGHT // 2 + TILE_SIZE // 2

            # Clamp camera to map boundaries
            self.camera_x = max(0, min(target_cam_x, WORLD_MAP_WIDTH_TILES * TILE_SIZE - SCREEN_WIDTH))
            self.camera_y = max(0, min(target_cam_y, WORLD_MAP_HEIGHT_TILES * TILE_SIZE - GAME_AREA_HEIGHT))
            
            # Handle cases where map is smaller than screen (camera stays at 0,0)
            if WORLD_MAP_WIDTH_TILES * TILE_SIZE < SCREEN_WIDTH:
                self.camera_x = 0
            if WORLD_MAP_HEIGHT_TILES * TILE_SIZE < GAME_AREA_HEIGHT:
                self.camera_y = 0


    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.dialogue_box.handle_input(event):
                continue

            if event.type == pygame.KEYDOWN:
                if self.player:
                    moved_or_interacted = False
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        moved_or_interacted = self.player.move(-1, 0)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        moved_or_interacted = self.player.move(1, 0)
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        moved_or_interacted = self.player.move(0, -1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        moved_or_interacted = self.player.move(0, 1)
                    
                    if not moved_or_interacted: # if player actually moved (not just interacted)
                        self.update_camera()


    def _update(self):
        for npc in self.npcs:
            npc.update() # For future NPC AI
        # Other game logic updates here
        pass

    def _draw_map(self):
        # Determine which tiles are visible
        start_col = self.camera_x // TILE_SIZE
        end_col = start_col + VIEWPORT_WIDTH_TILES + 1 # +1 to draw partially visible tiles
        start_row = self.camera_y // TILE_SIZE
        end_row = start_row + VIEWPORT_HEIGHT_TILES + 1

        for r in range(start_row, min(end_row, WORLD_MAP_HEIGHT_TILES)):
            for c in range(start_col, min(end_col, WORLD_MAP_WIDTH_TILES)):
                tile_type = self.current_map_data[r][c]
                
                # Calculate screen position for this tile
                screen_x = c * TILE_SIZE - self.camera_x
                screen_y = r * TILE_SIZE - self.camera_y
                
                rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                
                # --- This is where you'd draw tiles from a tileset image ---
                # Example: self.screen.blit(tileset_image, rect, area_for_tile_type)
                # For now, drawing colored rectangles:
                color = C_PATH_GRASS # Default
                if tile_type == T_PATH_GRASS: color = C_PATH_GRASS
                elif tile_type == T_GRASS_REGULAR: color = C_GRASS_REGULAR
                elif tile_type == T_TALL_GRASS: color = C_TALL_GRASS
                elif tile_type == T_WATER: color = C_WATER
                elif tile_type == T_TREE: # Simple two-tone tree
                    pygame.draw.rect(self.screen, C_TREE_TRUNK, rect)
                    leaves_rect = pygame.Rect(screen_x, screen_y - TILE_SIZE // 2, TILE_SIZE, TILE_SIZE)
                    pygame.draw.ellipse(self.screen, C_TREE_LEAVES, leaves_rect) # Draw leaves as ellipse on top
                    continue # Skip default rect draw for tree
                elif tile_type == T_FLOWER_RED: color = C_FLOWER_RED
                elif tile_type == T_FLOWER_YELLOW: color = C_FLOWER_YELLOW
                elif tile_type == T_SAND: color = C_SAND
                elif tile_type == T_BUILDING_WALL: color = C_BUILDING_WALL_DARK
                elif tile_type == T_PLAYER_HOUSE_WALL: color = C_BUILDING_WALL_LIGHT
                elif tile_type == T_PLAYER_HOUSE_DOOR: color = C_DOOR
                elif tile_type == T_RIVAL_HOUSE_WALL: color = C_BUILDING_WALL_LIGHT
                elif tile_type == T_RIVAL_HOUSE_DOOR: color = C_DOOR
                elif tile_type == T_LAB_WALL: color = (180, 180, 190) # Light grey lab wall
                elif tile_type == T_LAB_DOOR: color = C_DOOR
                elif tile_type == T_ROOF_PLAYER: color = C_ROOF_RED
                elif tile_type == T_ROOF_RIVAL: color = C_ROOF_BLUE
                elif tile_type == T_ROOF_LAB: color = C_ROOF_GRAY
                elif tile_type == T_SIGN: color = C_SIGN
                elif tile_type == T_LEDGE_JUMP_DOWN: color = C_LEDGE
                elif tile_type == T_FENCE: color = C_FENCE
                # T_NPC_SPAWN and T_PLAYER_SPAWN should be replaced by other tiles during init
                
                pygame.draw.rect(self.screen, color, rect)
                # Optional: Draw grid lines for debugging camera/tiles
                # pygame.draw.rect(self.screen, BLACK, rect, 1)

    def _draw_entities(self):
        if self.player:
            self.player.draw(self.screen, self.camera_x, self.camera_y)
        for npc in self.npcs:
            npc.draw(self.screen, self.camera_x, self.camera_y)

    def _draw(self):
        self.screen.fill(BLACK) # Fill area outside map, or a default bg color
        self._draw_map()
        self._draw_entities()
        self.dialogue_box.draw()
        pygame.display.flip()

    def run(self):
        while self.running:
            self._handle_input()
            self._update()
            self._draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == '__main__':
    if VIEWPORT_HEIGHT_TILES <= 0 or VIEWPORT_WIDTH_TILES <= 0:
        print(f"Error: Calculated viewport dimensions are invalid.")
        print(f"VP Height Tiles: {VIEWPORT_HEIGHT_TILES}, VP Width Tiles: {VIEWPORT_WIDTH_TILES}")
        print(f"Game Area Height: {GAME_AREA_HEIGHT}, Screen Width: {SCREEN_WIDTH}, Tile Size: {TILE_SIZE}")
    elif WORLD_MAP_WIDTH_TILES == 0 or WORLD_MAP_HEIGHT_TILES == 0:
        print(f"Error: World map data is empty or invalid.")
    else:
        game = Game()
        game.run()

