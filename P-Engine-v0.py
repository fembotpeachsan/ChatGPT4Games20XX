import tkinter as tk # Not used in this version, but kept as per original
import pygame
import os
import time

# --- Game Constants ---
SCREEN_WIDTH = 800  # Width of the game screen in pixels
SCREEN_HEIGHT = 600 # Height of the game screen in pixels
TILE_SIZE = 32      # Size of each tile in pixels
MAP_WIDTH_TILES = SCREEN_WIDTH // TILE_SIZE # Map width in tiles
# Reserve 100 pixels at the bottom for dialogue box
DIALOGUE_BOX_HEIGHT = 100
GAME_AREA_HEIGHT = SCREEN_HEIGHT - DIALOGUE_BOX_HEIGHT
MAP_HEIGHT_TILES = GAME_AREA_HEIGHT // TILE_SIZE

FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 150, 0)   # Grass
GRAY = (100, 100, 100)  # Path / Wall
BLUE = (0, 0, 200)    # Player
RED = (200, 0, 0)     # NPC
YELLOW = (255, 255, 0) # Door
DIALOGUE_BG = (30, 30, 30) # Darker background for dialogue
DIALOGUE_TEXT_COLOR = WHITE
DIALOGUE_BORDER_COLOR = (150, 150, 150)

# Tile Types
T_GRASS = 0
T_WALL = 1
T_PATH = 2
T_NPC_SPAWN = 3 # Changed from T_NPC to differentiate map data from entity
T_DOOR = 4

# --- Game Map Data ---
# Adjusted to ensure it can fit within the defined MAP_HEIGHT_TILES
game_map_data = [
    [T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL],
    [T_WALL, T_GRASS, T_GRASS, T_PATH, T_PATH, T_PATH, T_GRASS, T_GRASS, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL, T_DOOR, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL],
    [T_WALL, T_GRASS, T_GRASS, T_PATH, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL, T_PATH, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL],
    [T_WALL, T_PATH, T_PATH, T_PATH, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL, T_PATH, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL],
    [T_WALL, T_GRASS, T_GRASS, T_PATH, T_GRASS, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL, T_PATH, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL],
    [T_WALL, T_GRASS, T_GRASS, T_PATH, T_GRASS, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_WALL, T_GRASS, T_GRASS, T_NPC_SPAWN, T_GRASS, T_GRASS, T_GRASS, T_WALL, T_PATH, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL],
    [T_WALL, T_GRASS, T_GRASS, T_PATH, T_GRASS, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL, T_PATH, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL],
    [T_WALL, T_GRASS, T_GRASS, T_PATH, T_GRASS, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL, T_PATH, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL],
    [T_WALL, T_PATH, T_PATH, T_PATH, T_PATH, T_PATH, T_PATH, T_PATH, T_PATH, T_PATH, T_PATH, T_PATH, T_PATH, T_PATH, T_PATH, T_PATH, T_PATH, T_PATH, T_WALL, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_GRASS, T_WALL],
    [T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL],
    [T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL],
    [T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL],
    [T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL],
    [T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL],
    [T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL, T_WALL],
]

# Ensure map_data dimensions match MAP_HEIGHT_TILES and MAP_WIDTH_TILES
# Pad with walls if necessary, or truncate.
if len(game_map_data) > MAP_HEIGHT_TILES:
    game_map_data = game_map_data[:MAP_HEIGHT_TILES]
else:
    for _ in range(MAP_HEIGHT_TILES - len(game_map_data)):
        game_map_data.append([T_WALL] * MAP_WIDTH_TILES)

for r_idx, row in enumerate(game_map_data):
    if len(row) > MAP_WIDTH_TILES:
        game_map_data[r_idx] = row[:MAP_WIDTH_TILES]
    else:
        game_map_data[r_idx].extend([T_WALL] * (MAP_WIDTH_TILES - len(row)))


class DialogueBox:
    """Handles displaying dialogue messages."""
    def __init__(self, screen, font_size=24):
        self.screen = screen
        self.font = pygame.font.Font(None, font_size) # Use default system font
        self.messages = [] # Queue of messages to display
        self.current_message_surface = None
        self.active = False
        self.rect = pygame.Rect(0, SCREEN_HEIGHT - DIALOGUE_BOX_HEIGHT, SCREEN_WIDTH, DIALOGUE_BOX_HEIGHT)
        self.text_rect = self.rect.inflate(-20, -20) # Padding for text

    def show_message(self, text):
        """Adds a message to be displayed."""
        self.messages.append(text)
        if not self.active:
            self.next_message()

    def next_message(self):
        """Advances to the next message or closes dialogue if queue is empty."""
        if self.messages:
            message = self.messages.pop(0)
            self.current_message_surface = self.font.render(message, True, DIALOGUE_TEXT_COLOR)
            self.active = True
        else:
            self.active = False
            self.current_message_surface = None

    def draw(self):
        """Draws the dialogue box if active."""
        if self.active and self.current_message_surface:
            pygame.draw.rect(self.screen, DIALOGUE_BG, self.rect)
            pygame.draw.rect(self.screen, DIALOGUE_BORDER_COLOR, self.rect, 2) # Border
            self.screen.blit(self.current_message_surface, self.text_rect.topleft)

    def handle_input(self, event):
        """Handles input for advancing dialogue."""
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.next_message()
                return True # Input was handled
        return False


class Entity:
    """Base class for game entities like Player and NPC."""
    def __init__(self, x, y, color, game):
        self.x = x  # Tile x-coordinate
        self.y = y  # Tile y-coordinate
        self.color = color
        self.game = game # Reference to the main game object

    def draw(self, surface):
        """Draws the entity on the Pygame surface."""
        rect = pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, self.color, rect)
        # Add a smaller black square for detail
        pygame.draw.rect(surface, BLACK, rect.inflate(-TILE_SIZE * 0.4, -TILE_SIZE * 0.4))


class Player(Entity):
    """Represents the player character."""
    def __init__(self, x, y, game):
        super().__init__(x, y, BLUE, game)

    def move(self, dx, dy):
        """Moves the player by dx, dy if the target tile is walkable.
           Returns True if an interaction occurred, False otherwise.
        """
        if self.game.dialogue_box.active: # Don't move if dialogue is active
            return False

        new_x, new_y = self.x + dx, self.y + dy

        if 0 <= new_x < MAP_WIDTH_TILES and 0 <= new_y < MAP_HEIGHT_TILES:
            tile_type = self.game.game_map[new_y][new_x] # Access map from game object
            
            # Check for NPC at the target location
            for npc in self.game.npcs:
                if npc.x == new_x and npc.y == new_y:
                    npc.interact()
                    return True # Interaction occurred

            if tile_type == T_DOOR:
                self.game.dialogue_box.show_message("The door is locked.")
                # In a more complex game, this could trigger a map change or key check.
                return True # Interaction occurred

            if tile_type not in [T_WALL, T_NPC_SPAWN]: # NPC_SPAWN is just for placement, not collision
                self.x = new_x
                self.y = new_y
                return False # Moved, no specific interaction
        return False # Could not move or no interaction


class NPC(Entity):
    """Represents a Non-Player Character."""
    def __init__(self, x, y, game, name="Mysterious Figure", dialogue=None):
        super().__init__(x, y, RED, game)
        self.name = name
        self.dialogue = dialogue if dialogue else ["Hello, traveler!", "Nice weather today."]
        self.dialogue_index = 0

    def interact(self):
        """Initiates dialogue with the NPC."""
        if self.dialogue:
            # Show dialogue in parts or all at once
            # For simplicity, let's show one line at a time and cycle
            self.game.dialogue_box.show_message(f"{self.name}: {self.dialogue[self.dialogue_index]}")
            self.dialogue_index = (self.dialogue_index + 1) % len(self.dialogue)
        else:
            self.game.dialogue_box.show_message(f"{self.name} has nothing to say.")


class Game:
    """Main class to manage game state, updates, and rendering."""
    def __init__(self):
        pygame.init()
        pygame.font.init() # Initialize font module

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tile Game Engine")
        self.clock = pygame.time.Clock()
        self.running = True

        self.game_map = game_map_data # Load the map data
        self.dialogue_box = DialogueBox(self.screen)

        self.player = None # Will be initialized based on map
        self.npcs = []
        self._initialize_entities()


    def _initialize_entities(self):
        """Scans the map for player start and NPC locations."""
        player_spawned = False
        for r, row in enumerate(self.game_map):
            for c, tile in enumerate(row):
                if tile == T_NPC_SPAWN and not any(npc.x == c and npc.y == r for npc in self.npcs) : # Check if NPC already there
                    # Simple NPC placement for now
                    if len(self.npcs) == 0:
                         self.npcs.append(NPC(c, r, self, name="Old Man", dialogue=["Welcome to our village!", "Beware the northern path... it's quite drafty."]))
                         self.game_map[r][c] = T_GRASS # Replace spawn tile with grass after NPC is created
                    # Add more NPCs with different dialogues/names if needed
                # For simplicity, player starts at the first path tile found if not already spawned
                # A more robust way would be a specific T_PLAYER_SPAWN tile
                if not player_spawned and (tile == T_PATH or tile == T_GRASS):
                    # Try to find a non-wall starting point
                    if self.player is None: # ensure player is only created once
                        self.player = Player(c, r, self)
                        player_spawned = True

        if self.player is None: # Fallback if no suitable spawn found
            print("Warning: No suitable player spawn found. Placing at (1,1).")
            self.player = Player(1, 1, self)
            if self.game_map[1][1] == T_WALL: # Make sure it's not a wall
                self.game_map[1][1] = T_GRASS


    def _handle_input(self):
        """Handles user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.dialogue_box.handle_input(event):
                continue # Dialogue box handled the input

            if event.type == pygame.KEYDOWN:
                if self.player: # Ensure player exists
                    interaction_occurred = False
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        interaction_occurred = self.player.move(-1, 0)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        interaction_occurred = self.player.move(1, 0)
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        interaction_occurred = self.player.move(0, -1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        interaction_occurred = self.player.move(0, 1)
                    # elif event.key == pygame.K_e: # Example: Explicit interaction key
                    #     self.player.interact_ सामने() # Need to implement this method

    def _update(self):
        """Updates game state (currently empty as most logic is event-driven)."""
        # Player movement is handled in _handle_input
        # NPC logic (like random movement) could go here if needed
        pass

    def _draw_map(self):
        """Draws the game map."""
        for r, row in enumerate(self.game_map):
            for c, tile_type in enumerate(row):
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                color = GRAY # Default to wall color
                if tile_type == T_GRASS:
                    color = GREEN
                elif tile_type == T_PATH:
                    color = (150, 120, 80) # Brownish path
                elif tile_type == T_DOOR:
                    color = YELLOW
                elif tile_type == T_WALL:
                    color = GRAY
                # T_NPC_SPAWN will be drawn as its underlying tile (e.g. grass)
                # if an NPC is on it, the NPC's draw method handles it.
                # If not, it should have been replaced during init.
                
                pygame.draw.rect(self.screen, color, rect)
                # Optional: Draw grid lines for clarity
                # pygame.draw.rect(self.screen, BLACK, rect, 1)


    def _draw_entities(self):
        """Draws all entities (player, NPCs)."""
        if self.player:
            self.player.draw(self.screen)
        for npc in self.npcs:
            npc.draw(self.screen)

    def _draw(self):
        """Draws everything to the screen."""
        self.screen.fill(BLACK) # Fill background, though map usually covers it
        self._draw_map()
        self._draw_entities()
        self.dialogue_box.draw() # Draw dialogue box on top
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            self._handle_input()
            self._update()
            self._draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == '__main__':
    # Check if MAP_HEIGHT_TILES is reasonable
    if MAP_HEIGHT_TILES <= 0:
        print(f"Error: Calculated MAP_HEIGHT_TILES is {MAP_HEIGHT_TILES}. Check SCREEN_HEIGHT, DIALOGUE_BOX_HEIGHT, and TILE_SIZE.")
        print(f"GAME_AREA_HEIGHT: {GAME_AREA_HEIGHT}, TILE_SIZE: {TILE_SIZE}")
    else:
        game = Game()
        game.run()
