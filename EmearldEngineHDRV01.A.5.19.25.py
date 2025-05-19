import tkinter as tk # Not used in this version, but kept as per original
import pygame
import os
import time
import random # For potential future use (e.g., NPC movement)

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32

# Viewport dimensions in tiles
DIALOGUE_BOX_HEIGHT = 100
GAME_AREA_HEIGHT = SCREEN_HEIGHT - DIALOGUE_BOX_HEIGHT # Used for in-game viewport
VIEWPORT_WIDTH_TILES = SCREEN_WIDTH // TILE_SIZE
VIEWPORT_HEIGHT_TILES = GAME_AREA_HEIGHT // TILE_SIZE

FPS = 60

# --- Colors (Gen 3 Inspired - simplified) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Environment
C_PATH_GRASS = (136, 192, 112)
C_GRASS_REGULAR = (104, 168, 88)
C_TALL_GRASS = (64, 128, 72)
C_TREE_TRUNK = (112, 80, 48)
C_TREE_LEAVES = (48, 96, 48)
C_WATER = (80, 128, 200)
C_FLOWER_RED = (208, 72, 48)
C_FLOWER_YELLOW = (248, 224, 96)
C_SAND = (216, 200, 160)

# Buildings & Structures
C_BUILDING_WALL_LIGHT = (200, 160, 120)
C_BUILDING_WALL_DARK = (160, 128, 96)
C_ROOF_RED = (192, 80, 48)
C_ROOF_BLUE = (80, 96, 160)
C_ROOF_GRAY = (128, 128, 128)
C_DOOR = (96, 64, 32)
C_SIGN = (144, 112, 80)
C_LEDGE = (120, 176, 104)
C_FENCE = (160, 144, 128)

# Entities & UI
C_PLAYER = (224, 80, 64)
C_NPC = (80, 144, 224)
C_DIALOGUE_BG = (40, 40, 40)
C_DIALOGUE_TEXT = WHITE
C_DIALOGUE_BORDER = (100, 100, 100)

# --- Tile Types ---
T_PATH_GRASS = 0
T_GRASS_REGULAR = 1
T_TALL_GRASS = 2
T_WATER = 3
T_TREE = 4
T_FLOWER_RED = 5
T_FLOWER_YELLOW = 6
T_SAND = 7
T_BUILDING_WALL = 10
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
T_LEDGE_JUMP_DOWN = 21
T_FENCE = 22
T_NPC_SPAWN = 98
T_PLAYER_SPAWN = 99

# --- Littleroot Town Map Data ---
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
TLG = T_TALL_GRASS
FLR = T_FLOWER_RED
FLY = T_FLOWER_YELLOW
LJD = T_LEDGE_JUMP_DOWN
NSP = T_NPC_SPAWN
PSP = T_PLAYER_SPAWN

littleroot_town_map_data = [
    [TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, RLB, RLB, RLB, RLB, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, FLY, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, LBW, LBD, LBW, LBW, PTH, PTH, PTH, PTH, PTH, PTH, PTH, FLR, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, LBW, NSP, LBW, LBW, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, SGN, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, SGN, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, FNC, FNC, FNC, FNC, FNC, PTH, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, PTH, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, FNC, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, RPL, RPL, RPL, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, RRV, RRV, RRV, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PHW, PHD, PHW, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, RHW, RHD, RHW, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PHW, NSP, PHW, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, RHW, RHW, RHW, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PSP, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, TRE, TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, LJD, LJD, LJD, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TRE],
    [TRE, TLG, TLG, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, PTH, TLG, TLG, TLG, TRE],
    [TRE, TLG, TLG, PTH, PTH, PTH, PTH, WTR, WTR, WTR, PTH, PTH, PTH, PTH, PTH, PTH, WTR, WTR, WTR, PTH, PTH, PTH, PTH, PTH, PTH, TLG, TLG, TLG, TRE],
    [TRE, TRE, TRE, TRE, TRE, TRE, TRE, WTR, WTR, WTR, TRE, TRE, TRE, TRE, TRE, TRE, WTR, WTR, WTR, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE, TRE],
]

WORLD_MAP_HEIGHT_TILES = len(littleroot_town_map_data)
WORLD_MAP_WIDTH_TILES = len(littleroot_town_map_data[0]) if WORLD_MAP_HEIGHT_TILES > 0 else 0

# --- Game States ---
STATE_MAIN_MENU = 0
STATE_LITTLEROOT = 1

class DialogueBox:
    def __init__(self, screen, font_size=28):
        self.screen = screen
        self.font = pygame.font.Font(None, font_size)
        self.messages = []
        self.current_message_surface = None
        self.active = False
        self.rect = pygame.Rect(0, SCREEN_HEIGHT - DIALOGUE_BOX_HEIGHT, SCREEN_WIDTH, DIALOGUE_BOX_HEIGHT)
        self.text_rect = self.rect.inflate(-30, -30)

    def show_message(self, text):
        self.messages.append(text)
        if not self.active:
            self.next_message()

    def next_message(self):
        if self.messages:
            message = self.messages.pop(0)
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
            
            if lines:
                self.current_message_surface = self.font.render(lines[0].strip(), True, C_DIALOGUE_TEXT)
            else:
                self.current_message_surface = self.font.render("", True, C_DIALOGUE_TEXT)
            self.active = True
        else:
            self.active = False
            self.current_message_surface = None

    def draw(self):
        if self.active and self.current_message_surface:
            pygame.draw.rect(self.screen, C_DIALOGUE_BG, self.rect)
            pygame.draw.rect(self.screen, C_DIALOGUE_BORDER, self.rect, 3)
            self.screen.blit(self.current_message_surface, self.text_rect.topleft)

    def handle_input(self, event):
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_e:
                self.next_message()
                return True
        return False

class Entity:
    def __init__(self, x, y, color, game, name="Entity"):
        self.x = x
        self.y = y
        self.color = color
        self.game = game
        self.name = name

    def draw(self, surface, camera_x, camera_y):
        screen_x = self.x * TILE_SIZE - camera_x
        screen_y = self.y * TILE_SIZE - camera_y

        if screen_x + TILE_SIZE > 0 and screen_x < SCREEN_WIDTH and \
           screen_y + TILE_SIZE > 0 and screen_y < GAME_AREA_HEIGHT: # Culling against game area
            rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, self.color, rect)
            detail_size = TILE_SIZE // 3
            detail_rect = pygame.Rect(screen_x + detail_size, screen_y + detail_size, detail_size, detail_size)
            pygame.draw.rect(surface, BLACK, detail_rect)

class Player(Entity):
    def __init__(self, x, y, game):
        super().__init__(x, y, C_PLAYER, game, name="Player")

    def move(self, dx, dy):
        if self.game.dialogue_box.active:
            return False # Don't move if dialogue is active

        new_x, new_y = self.x + dx, self.y + dy

        if 0 <= new_x < WORLD_MAP_WIDTH_TILES and 0 <= new_y < WORLD_MAP_HEIGHT_TILES:
            target_tile_type = self.game.current_map_data[new_y][new_x]
            
            for npc in self.game.npcs:
                if npc.x == new_x and npc.y == new_y:
                    npc.interact(self)
                    return True 

            interaction_message = None
            if target_tile_type == T_PLAYER_HOUSE_DOOR:
                interaction_message = "My house."
            elif target_tile_type == T_RIVAL_HOUSE_DOOR:
                interaction_message = "This is [Rival]'s house. They're probably out training."
            elif target_tile_type == T_LAB_DOOR:
                interaction_message = "Professor Birch's Pokémon Lab."
            elif target_tile_type == T_SIGN:
                if new_x == 3 and new_y == 6: 
                    interaction_message = "Littleroot Town - A town that can't be shaded any hue."
                elif new_x == 22 and new_y == 6:
                    interaction_message = "Route 101 ahead."
                else:
                    interaction_message = "It's a wooden sign. It says something."

            if interaction_message:
                self.game.dialogue_box.show_message(interaction_message)
                return True

            impassable_tiles = [T_TREE, T_WATER, T_BUILDING_WALL, T_PLAYER_HOUSE_WALL,
                                T_RIVAL_HOUSE_WALL, T_LAB_WALL, T_ROOF_LAB, T_ROOF_PLAYER,
                                T_ROOF_RIVAL, T_FENCE]
            if target_tile_type in impassable_tiles:
                return False 

            if dy == -1 and self.game.current_map_data[self.y][self.x] == T_LEDGE_JUMP_DOWN:
                   return False 

            if target_tile_type == T_LEDGE_JUMP_DOWN:
                tile_above_player = self.game.current_map_data[self.y][self.x]
                if dy == 1 and tile_above_player != T_LEDGE_JUMP_DOWN : 
                    self.x = new_x
                    self.y = new_y + 1 
                    self.game.dialogue_box.show_message("Whee! Jumped the ledge.")
                    self.y = max(0, min(self.y, WORLD_MAP_HEIGHT_TILES -1))
                    return False 
                else: 
                    return False 

            self.x = new_x
            self.y = new_y
            return False # Moved, no specific interaction
        return False 

class NPC(Entity):
    def __init__(self, x, y, game, name="Villager", dialogue=None, color=C_NPC):
        super().__init__(x, y, color, game, name=name)
        self.dialogue_template = dialogue if dialogue else ["Hello, {player_name}!", "It's a fine day."]
        self.dialogue_index = 0

    def interact(self, interactor):
        if self.dialogue_template:
            current_template = self.dialogue_template[self.dialogue_index]
            player_name_to_use = self.game.player.name if self.game.player and self.game.player.name else "trainer"
            current_dialogue = current_template.replace("{player_name}", player_name_to_use)
            
            self.game.dialogue_box.show_message(f"{self.name}: {current_dialogue}")
            self.dialogue_index = (self.dialogue_index + 1) % len(self.dialogue_template)
        else:
            self.game.dialogue_box.show_message(f"{self.name} doesn't have much to say.")
    
    def update(self):
        pass

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PokeEmeraldPy Engine")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.game_state = STATE_MAIN_MENU

        # Fonts for main menu
        self.title_font = pygame.font.Font(None, 60) 
        self.prompt_font = pygame.font.Font(None, 36)
        self.engine_title_font = pygame.font.Font(None, 74)


        # In-game components (initialized but used when state is STATE_LITTLEROOT)
        self.current_map_data = littleroot_town_map_data
        self.dialogue_box = DialogueBox(self.screen)
        self.player = None 
        self.npcs = []
        self._initialize_entities() # Creates player and NPCs

        self.camera_x = 0
        self.camera_y = 0
        # self.update_camera() will be called when game starts or player moves

    def _initialize_entities(self):
        player_spawn_pos = None
        for r, row in enumerate(self.current_map_data):
            for c, tile in enumerate(row):
                if tile == T_PLAYER_SPAWN and self.player is None:
                    self.player = Player(c, r, self)
                    player_spawn_pos = (c,r)
                    self.current_map_data[r][c] = T_PATH_GRASS
                elif tile == T_NPC_SPAWN:
                    if c == 3 and r == 12: 
                        mom_dialogue = [
                            "Oh, {player_name}! Off on an adventure?",
                            "Don't forget to change your underwear!",
                            "Professor Birch was looking for you earlier."
                        ]
                        self.npcs.append(NPC(c, r, self, name="Mom", dialogue=mom_dialogue, color=(230,100,120)))
                    elif c == 12 and r == 3: 
                        prof_dialogue = [
                            "Welcome to the world of Pokémon, {player_name}!",
                            "I'm Professor Birch. This is my lab.",
                            "Are you ready to choose your first Pokémon?" 
                        ]
                        self.npcs.append(NPC(c,r,self, name="Prof. Birch", dialogue=prof_dialogue, color=(100,100,100)))
                    else: 
                        self.npcs.append(NPC(c, r, self, name=f"Villager {len(self.npcs)+1}"))
                    self.current_map_data[r][c] = T_PATH_GRASS

        if self.player is None:
            print("Warning: No T_PLAYER_SPAWN found. Placing player at (5,5).")
            self.player = Player(5, 5, self)
            if self.current_map_data[5][5] in [T_TREE, T_WATER, T_BUILDING_WALL]:
                self.current_map_data[5][5] = T_PATH_GRASS
        
        # Player name will be set when transitioning from menu

    def update_camera(self):
        if self.player:
            target_cam_x = self.player.x * TILE_SIZE - SCREEN_WIDTH // 2 + TILE_SIZE // 2
            target_cam_y = self.player.y * TILE_SIZE - GAME_AREA_HEIGHT // 2 + TILE_SIZE // 2

            self.camera_x = max(0, min(target_cam_x, WORLD_MAP_WIDTH_TILES * TILE_SIZE - SCREEN_WIDTH))
            self.camera_y = max(0, min(target_cam_y, WORLD_MAP_HEIGHT_TILES * TILE_SIZE - GAME_AREA_HEIGHT))
            
            if WORLD_MAP_WIDTH_TILES * TILE_SIZE < SCREEN_WIDTH:
                self.camera_x = 0
            if WORLD_MAP_HEIGHT_TILES * TILE_SIZE < GAME_AREA_HEIGHT:
                self.camera_y = 0

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_state == STATE_MAIN_MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.game_state = STATE_LITTLEROOT
                        if self.player: # Ensure player exists
                            self.player.name = "Emerald" # Set player name
                        self.update_camera() # Initialize camera for game start
            
            elif self.game_state == STATE_LITTLEROOT:
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
                        
                        # Only update camera if player *actually* moved,
                        # not just if an interaction occurred that prevented movement.
                        # The player.move() returns True for interaction, False for actual move or blocked.
                        # This logic seems a bit off. Let's adjust:
                        # player.move should ideally return:
                        # "moved", "interacted", "blocked"
                        # For now, if it's False, it means either moved or blocked.
                        # If it's True, it means interaction.
                        # We update camera if not interacted (meaning either moved or blocked by wall,
                        # camera update is still fine if blocked)
                        if not moved_or_interacted:
                             self.update_camera()


    def _update(self):
        if self.game_state == STATE_LITTLEROOT:
            for npc in self.npcs:
                npc.update()
        # No updates for main menu in this simple version

    def _draw_stylized_rayquaza(self, surface, center_x, base_y):
        # Simple representation of Rayquaza (serpentine)
        body_color = (20, 120, 50)    # Dark Green
        accent_color = (250, 200, 0)  # Yellow
        fin_color = (180, 60, 40)     # Reddish fins
        eye_color = (200, 0, 0)       # Red

        num_segments = 7
        segment_radius_y = 18
        segment_radius_x = 25
        overlap = 15
        wave_amplitude = 20
        wave_frequency = 0.5

        # Draw body segments with a slight wave
        for i in range(num_segments):
            # Calculate position for wave effect
            angle = i * wave_frequency
            offset_x = (num_segments - 1 - i) * (segment_radius_x * 2 - overlap) # Draw from tail to head
            current_x = center_x - (num_segments * (segment_radius_x*2-overlap)) //2 + offset_x
            current_y = base_y + int(wave_amplitude * pygame.math.Vector2(1,0).rotate(pygame.time.get_ticks() * 0.1 + angle).y)


            # Body segment
            pygame.draw.ellipse(surface, body_color, 
                                (current_x - segment_radius_x, current_y - segment_radius_y,
                                 segment_radius_x * 2, segment_radius_y * 2))
            
            # Yellow ring accent
            if i < num_segments -1: # Not on head
                pygame.draw.ellipse(surface, accent_color,
                                (current_x - segment_radius_x/1.5, current_y - segment_radius_y/1.5,
                                segment_radius_x * 2 / 1.5, segment_radius_y * 2 / 1.5), 3)


            # Small side fins (simplified)
            if i % 2 == 0 and i < num_segments -1 and i > 0:
                fin_length = 25
                fin_width = 10
                # Left fin
                pygame.draw.polygon(surface, fin_color, [
                    (current_x - segment_radius_x, current_y),
                    (current_x - segment_radius_x - fin_length, current_y - fin_width),
                    (current_x - segment_radius_x - fin_length, current_y + fin_width)
                ])
                # Right fin
                pygame.draw.polygon(surface, fin_color, [
                    (current_x + segment_radius_x, current_y),
                    (current_x + segment_radius_x + fin_length, current_y - fin_width),
                    (current_x + segment_radius_x + fin_length, current_y + fin_width)
                ])

        # Head (last segment, slightly larger)
        head_x = current_x # Re-use last segment's x for consistency if needed
        head_y = current_y
        
        head_radius_x = segment_radius_x + 5
        head_radius_y = segment_radius_y + 5
        pygame.draw.ellipse(surface, body_color, 
                            (head_x - head_radius_x, head_y - head_radius_y,
                             head_radius_x * 2, head_radius_y * 2))
        # Eyes
        eye_offset_x = head_radius_x * 0.4
        eye_offset_y = head_radius_y * 0.3
        eye_radius = 4
        pygame.draw.circle(surface, eye_color, (int(head_x - eye_offset_x), int(head_y - eye_offset_y)), eye_radius)
        pygame.draw.circle(surface, WHITE, (int(head_x - eye_offset_x + 1), int(head_y - eye_offset_y - 1)), eye_radius // 2) # Highlight
        pygame.draw.circle(surface, eye_color, (int(head_x + eye_offset_x), int(head_y - eye_offset_y)), eye_radius)
        pygame.draw.circle(surface, WHITE, (int(head_x + eye_offset_x+1), int(head_y - eye_offset_y-1)), eye_radius // 2) # Highlight


    def _draw_main_menu(self):
        self.screen.fill((30, 50, 30)) # Dark green background for menu

        # Draw Stylized Rayquaza
        # Position Rayquaza above the center, allowing space for title and prompt
        rayquaza_center_x = SCREEN_WIDTH // 2
        rayquaza_base_y = SCREEN_HEIGHT // 2.8 # Adjusted Y position
        self._draw_stylized_rayquaza(self.screen, rayquaza_center_x, rayquaza_base_y)


        # Engine Title
        title_surface = self.engine_title_font.render("PokeEmeraldPy Engine", True, C_GRASS_REGULAR)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6))
        self.screen.blit(title_surface, title_rect)

        # Prompt
        prompt_surface = self.prompt_font.render("Press SPACE to Start", True, WHITE)
        prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.80))
        self.screen.blit(prompt_surface, prompt_rect)

        pygame.display.flip()


    def _draw_map(self):
        start_col = self.camera_x // TILE_SIZE
        end_col = start_col + VIEWPORT_WIDTH_TILES + 1
        start_row = self.camera_y // TILE_SIZE
        end_row = start_row + VIEWPORT_HEIGHT_TILES + 1

        for r in range(start_row, min(end_row, WORLD_MAP_HEIGHT_TILES)):
            for c in range(start_col, min(end_col, WORLD_MAP_WIDTH_TILES)):
                tile_type = self.current_map_data[r][c]
                screen_x = c * TILE_SIZE - self.camera_x
                screen_y = r * TILE_SIZE - self.camera_y
                rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                
                color = C_PATH_GRASS 
                if tile_type == T_PATH_GRASS: color = C_PATH_GRASS
                elif tile_type == T_GRASS_REGULAR: color = C_GRASS_REGULAR
                elif tile_type == T_TALL_GRASS: color = C_TALL_GRASS
                elif tile_type == T_WATER: color = C_WATER
                elif tile_type == T_TREE:
                    pygame.draw.rect(self.screen, C_TREE_TRUNK, rect)
                    leaves_rect = pygame.Rect(screen_x, screen_y - TILE_SIZE // 2, TILE_SIZE, TILE_SIZE)
                    pygame.draw.ellipse(self.screen, C_TREE_LEAVES, leaves_rect)
                    continue 
                elif tile_type == T_FLOWER_RED: color = C_FLOWER_RED
                elif tile_type == T_FLOWER_YELLOW: color = C_FLOWER_YELLOW
                elif tile_type == T_SAND: color = C_SAND
                elif tile_type == T_BUILDING_WALL: color = C_BUILDING_WALL_DARK
                elif tile_type == T_PLAYER_HOUSE_WALL: color = C_BUILDING_WALL_LIGHT
                elif tile_type == T_PLAYER_HOUSE_DOOR: color = C_DOOR
                elif tile_type == T_RIVAL_HOUSE_WALL: color = C_BUILDING_WALL_LIGHT
                elif tile_type == T_RIVAL_HOUSE_DOOR: color = C_DOOR
                elif tile_type == T_LAB_WALL: color = (180, 180, 190) 
                elif tile_type == T_LAB_DOOR: color = C_DOOR
                elif tile_type == T_ROOF_PLAYER: color = C_ROOF_RED
                elif tile_type == T_ROOF_RIVAL: color = C_ROOF_BLUE
                elif tile_type == T_ROOF_LAB: color = C_ROOF_GRAY
                elif tile_type == T_SIGN: color = C_SIGN
                elif tile_type == T_LEDGE_JUMP_DOWN: color = C_LEDGE
                elif tile_type == T_FENCE: color = C_FENCE
                
                pygame.draw.rect(self.screen, color, rect)

    def _draw_entities(self):
        if self.player:
            self.player.draw(self.screen, self.camera_x, self.camera_y)
        for npc in self.npcs:
            npc.draw(self.screen, self.camera_x, self.camera_y)

    def _draw(self):
        if self.game_state == STATE_MAIN_MENU:
            self._draw_main_menu()
        elif self.game_state == STATE_LITTLEROOT:
            self.screen.fill(BLACK) 
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
