import pygame
import random
import time # Meow, for little pauses!

# --- Configuration ---
SCREEN_WIDTH = 480  # Screen width in pixels
SCREEN_HEIGHT = 320 # Screen height in pixels
TILE_SIZE = 16     # Size of each tile in pixels
PLAYER_SIZE = 12   # Size of the player
TEXT_BOX_HEIGHT = 80 # Height for our dialogue/battle box, purr!
FONT_SIZE = 18 # Cute little font

# --- Colors (RGB) ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 177, 76)   # For grass, meow!
DARK_GREEN = (0, 100, 0) # For dense grass
BROWN = (139, 69, 19)   # For paths or tree trunks
GREY = (128, 128, 128)  # For buildings or rocks
RED = (255, 0, 0)       # Player color, rawr!
WATER_BLUE = (0, 116, 217) # Water, splash!
LIGHT_YELLOW = (255, 255, 224) # For text boxes, nyah!
UI_BORDER_COLOR = (50, 50, 50)

# --- Game States ---
STATE_OVERWORLD = "overworld"
STATE_BATTLE = "battle"
STATE_TEXTBOX = "textbox" # For simple messages, meow!

# --- Game World (Tile Types) ---
# 0: Path (Brown)
# 1: Grass (Green) - potential encounter, purr!
# 2: Wall/Obstacle (Grey)
# 3: Water (Water Blue)
# 4: NPC_BLOCK (Looks like a path, but triggers text!) - a new purrfect idea!
MAP_WIDTH = SCREEN_WIDTH // TILE_SIZE
MAP_HEIGHT = (SCREEN_HEIGHT - TEXT_BOX_HEIGHT) // TILE_SIZE # Adjust map height for text box

game_map = [[2 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

# --- FAKERFAKE 1.0 & DELTA-BUSTER Presents: Placeholder Pokemon Data ---
# Meow! Let's make some simple monsters!
# Structure: name, hp, attack, defense, "sprite" (just a color for now, purr!)
# My HQRIPPER 7.1 just "found" these unique designs, nyah!
POKEMON_DATA = {
    "KITTENPUNCH": {"hp": 30, "max_hp": 30, "attack": 8, "defense": 5, "sprite_color": (255, 105, 180)}, # Pink!
    "BARKBITE": {"hp": 35, "max_hp": 35, "attack": 7, "defense": 6, "sprite_color": (160, 82, 45)},    # Sienna!
    "PIXELPUP": {"hp": 25, "max_hp": 25, "attack": 9, "defense": 4, "sprite_color": (173, 216, 230)} # Light Blue!
}

# --- Simple Text Wrapping ---
def wrap_text(text, font, max_width):
    """Wraps text to fit a_certain width, purr."""
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    lines.append(current_line.strip())
    return lines

class RedEmuGame:
    def __init__(self):
        pygame.init()
        # Screen setup considering the text box
        self.actual_screen_height = SCREEN_HEIGHT
        self.game_screen_height = SCREEN_HEIGHT - TEXT_BOX_HEIGHT
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, self.actual_screen_height))
        pygame.display.set_caption("RedEMU Test - Meow! It's kinda working!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE) # Default font, purr
        self.large_font = pygame.font.Font(None, FONT_SIZE + 6) # For battle names

        self.game_state = STATE_OVERWORLD
        self.current_map = [[2 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.player_x_tile = MAP_WIDTH // 2
        self.player_y_tile = MAP_HEIGHT // 2

        self.textbox_message_queue = [] # Messages to display, nyah!
        self.current_textbox_message_lines = []
        self.textbox_line_index = 0
        self.textbox_active = False

        self.battle_active = False
        self.player_pokemon = None # You'll get one later, meow!
        self.enemy_pokemon = None
        self.battle_turn = "player" # "player" or "enemy"
        self.battle_message = ""
        self.last_battle_message_time = 0

        self.generate_procedural_map()
        self.setup_player_pokemon() # Give player a starting mon!

        # Meow! Add a simple NPC!
        self.current_map[self.player_y_tile - 2][self.player_x_tile] = 4 # NPC tile
        self.npc_data = {
            (self.player_x_tile, self.player_y_tile - 2): "Meow! I'm a test NPC! Have you seen my cat, Pixelpup?"
        }


    def setup_player_pokemon(self):
        """Gives the player a starting Pokemon, purr!"""
        # Let's use DELTA-BUSTER to ensure this exists!
        start_mon_name = "KITTENPUNCH" # Our lovely starter!
        data = POKEMON_DATA[start_mon_name]
        self.player_pokemon = {
            "name": start_mon_name,
            "hp": data["hp"],
            "max_hp": data["max_hp"],
            "attack": data["attack"],
            "defense": data["defense"],
            "sprite_color": data["sprite_color"]
        }
        print(f"Meow! You got a {start_mon_name}! Take good care of it, purr!")


    def generate_procedural_map(self):
        """Generates a very simple procedural map, purr!"""
        print("Meow! Generating a little map for RedEMU...")
        for r in range(MAP_HEIGHT):
            for c in range(MAP_WIDTH):
                if r == 0 or c == 0 or r == MAP_HEIGHT - 1 or c == MAP_WIDTH - 1:
                    self.current_map[r][c] = 2 # Wall
                else:
                    rand_val = random.random()
                    if rand_val < 0.6:
                        self.current_map[r][c] = 1 # Grass
                    elif rand_val < 0.8:
                        self.current_map[r][c] = 0 # Path
                    elif rand_val < 0.9 and (r > 3 and c > 3 and r < MAP_HEIGHT -3 and c < MAP_WIDTH -3) :
                        if self.current_map[r-1][c] !=2 and self.current_map[r+1][c] !=2 and self.current_map[r][c-1] !=2 and self.current_map[r][c+1] !=2:
                            self.current_map[r][c] = 3 # Water
                    else:
                        self.current_map[r][c] = 2 # Obstacle/Wall
        self.current_map[self.player_y_tile][self.player_x_tile] = 0
        self.current_map[self.player_y_tile][self.player_x_tile + 1] = 0
        print("Purr! Map generated for RedEMU.")


    def draw_tile(self, surface, tile_type, x_pixel, y_pixel):
        rect = pygame.Rect(x_pixel, y_pixel, TILE_SIZE, TILE_SIZE)
        border_rect = pygame.Rect(x_pixel, y_pixel, TILE_SIZE, TILE_SIZE)
        if tile_type == 0: pygame.draw.rect(surface, BROWN, rect)
        elif tile_type == 1:
            pygame.draw.rect(surface, GREEN, rect)
            pygame.draw.line(surface, DARK_GREEN, (x_pixel, y_pixel + TILE_SIZE // 2), (x_pixel + TILE_SIZE, y_pixel + TILE_SIZE // 2), 1)
            pygame.draw.line(surface, DARK_GREEN, (x_pixel + TILE_SIZE // 2, y_pixel), (x_pixel + TILE_SIZE // 2, y_pixel + TILE_SIZE), 1)
        elif tile_type == 2:
            pygame.draw.rect(surface, GREY, rect)
            pygame.draw.rect(surface, BLACK, border_rect, 1)
        elif tile_type == 3:
            pygame.draw.rect(surface, WATER_BLUE, rect)
            pygame.draw.line(surface, WHITE, (x_pixel + 2, y_pixel + TILE_SIZE // 3), (x_pixel + TILE_SIZE - 2, y_pixel + TILE_SIZE // 3), 1)
            pygame.draw.line(surface, WHITE, (x_pixel + 4, y_pixel + 2 * TILE_SIZE // 3), (x_pixel + TILE_SIZE - 4, y_pixel + 2 * TILE_SIZE // 3), 1)
        elif tile_type == 4: # NPC visual - looks like a path for now, purr!
            pygame.draw.rect(surface, BROWN, rect) # Could make this a different color!
            pygame.draw.circle(surface, RED, (x_pixel + TILE_SIZE // 2, y_pixel + TILE_SIZE // 2), TILE_SIZE // 4) # Little red dot for NPC, meow!

    def draw_map(self, surface):
        for r_idx, row in enumerate(self.current_map):
            for c_idx, tile_val in enumerate(row):
                self.draw_tile(surface, tile_val, c_idx * TILE_SIZE, r_idx * TILE_SIZE)

    def draw_player(self, surface):
        player_pixel_x = self.player_x_tile * TILE_SIZE + (TILE_SIZE - PLAYER_SIZE) // 2
        player_pixel_y = self.player_y_tile * TILE_SIZE + (TILE_SIZE - PLAYER_SIZE) // 2
        player_rect = pygame.Rect(player_pixel_x, player_pixel_y, PLAYER_SIZE, PLAYER_SIZE)
        pygame.draw.rect(surface, RED, player_rect)
        pygame.draw.rect(surface, BLACK, player_rect, 1)

    def draw_textbox(self):
        """Draws the text box at the bottom of the screen, purrfect for chats!"""
        box_rect = pygame.Rect(0, self.game_screen_height, SCREEN_WIDTH, TEXT_BOX_HEIGHT)
        pygame.draw.rect(self.screen, LIGHT_YELLOW, box_rect)
        pygame.draw.rect(self.screen, UI_BORDER_COLOR, box_rect, 3) # A cute border!

        if self.current_textbox_message_lines:
            for i, line in enumerate(self.current_textbox_message_lines):
                if i <= self.textbox_line_index: # Reveal lines one by one (or all if already shown)
                    text_surface = self.font.render(line, True, BLACK)
                    self.screen.blit(text_surface, (15, self.game_screen_height + 15 + (i * (FONT_SIZE + 2))))
            # Little indicator to press action, meow!
            if self.textbox_line_index >= len(self.current_textbox_message_lines) -1 :
                 indicator_text = self.font.render("v (Z)", True, RED)
                 self.screen.blit(indicator_text, (SCREEN_WIDTH - 40, self.actual_screen_height - 25))


    def show_message(self, message):
        """Queues a message for the textbox, nyah!"""
        print(f"Meow! Showing message: {message}") # Debug console meow
        self.textbox_message_queue.append(message)
        if not self.textbox_active:
            self._activate_next_message()

    def _activate_next_message(self):
        if self.textbox_message_queue:
            message = self.textbox_message_queue.pop(0)
            # Wrap text, meow! Max width of text box minus some padding
            self.current_textbox_message_lines = wrap_text(message, self.font, SCREEN_WIDTH - 30)
            self.textbox_line_index = 0 # Start showing the first line of the wrapped message
            self.game_state = STATE_TEXTBOX
            self.textbox_active = True
        else:
            self.textbox_active = False
            self.game_state = STATE_OVERWORLD # Go back to walking, purr!


    def handle_textbox_input(self, event):
        if event.key == pygame.K_z: # "Action" button, meow!
            self.textbox_line_index +=1 # Try to show next line of current message part
            if self.textbox_line_index >= len(self.current_textbox_message_lines):
                 self._activate_next_message() # If out of lines, try to show next full message

    def handle_overworld_input(self, event):
        new_x_tile, new_y_tile = self.player_x_tile, self.player_y_tile
        moved = False
        if event.key == pygame.K_LEFT: new_x_tile -= 1; moved = True
        elif event.key == pygame.K_RIGHT: new_x_tile += 1; moved = True
        elif event.key == pygame.K_UP: new_y_tile -= 1; moved = True
        elif event.key == pygame.K_DOWN: new_y_tile += 1; moved = True
        elif event.key == pygame.K_z: # Action button! Purr!
            # Check tile in front of player (basic for now)
            # For simplicity, let's just check the current tile for NPC trigger
            # In a real game, you'd check facing direction!
            tile_ahead_x, tile_ahead_y = self.player_x_tile, self.player_y_tile # For now, check interaction on NPC tile
            # This is super basic, would need directional check
            for dx, dy in [(0,0), (0, -1), (0, 1), (-1, 0), (1, 0)]: # Check around player too
                check_x, check_y = self.player_x_tile + dx, self.player_y_tile + dy
                if 0 <= check_x < MAP_WIDTH and 0 <= check_y < MAP_HEIGHT:
                    if self.current_map[check_y][check_x] == 4: # Found an NPC tile!
                        npc_pos = (check_x, check_y)
                        if npc_pos in self.npc_data:
                            self.show_message(self.npc_data[npc_pos])
                            return # Don't move if interacting, meow!


        if moved:
            if 0 <= new_x_tile < MAP_WIDTH and \
               0 <= new_y_tile < MAP_HEIGHT and \
               self.current_map[new_y_tile][new_x_tile] != 2 and \
               self.current_map[new_y_tile][new_x_tile] != 3:

                self.player_x_tile = new_x_tile
                self.player_y_tile = new_y_tile

                if self.current_map[self.player_y_tile][self.player_x_tile] == 1: # Landed on grass!
                    if random.random() < 0.15: # 15% chance for an "encounter", purr!
                        self.start_battle()
                # Check for NPC after moving ONTO its tile (simpler than directional interaction for this test)
                # elif self.current_map[self.player_y_tile][self.player_x_tile] == 4: # Landed on an NPC trigger!
                #     npc_pos = (self.player_x_tile, self.player_y_tile)
                #     if npc_pos in self.npc_data:
                #         self.show_message(self.npc_data[npc_pos])


            elif 0 <= new_x_tile < MAP_WIDTH and 0 <= new_y_tile < MAP_HEIGHT and self.current_map[new_y_tile][new_x_tile] == 3:
                self.show_message("Splash! That's water, meow! Can't swim yet!")

    def start_battle(self):
        """Initiates a battle, meow! My HQRIPPER grabbed a wild one!"""
        if not self.player_pokemon or self.player_pokemon["hp"] <= 0:
            self.show_message("Meow... Your Pokemon is too tired to fight!")
            return

        wild_pokemon_name = random.choice(list(POKEMON_DATA.keys()))
        data = POKEMON_DATA[wild_pokemon_name]
        self.enemy_pokemon = {
            "name": wild_pokemon_name,
            "hp": data["hp"],
            "max_hp": data["max_hp"],
            "attack": data["attack"],
            "defense": data["defense"],
            "sprite_color": data["sprite_color"]
        }
        self.game_state = STATE_BATTLE
        self.battle_active = True
        self.battle_turn = "player" # Player always starts, purr!
        self.battle_message = f"A wild {self.enemy_pokemon['name']} appeared, rawr!"
        self.last_battle_message_time = time.time()
        print(f"Purr... A wild {self.enemy_pokemon['name']} (HP: {self.enemy_pokemon['hp']}) appeared!")

    def draw_battle_ui(self):
        """Draws the battle interface, so fierce!"""
        # Background for battle (full screen for now, simple)
        self.screen.fill(BLACK) # Whole screen becomes battle arena!

        # Enemy Pokemon (top right)
        if self.enemy_pokemon:
            enemy_name_surf = self.large_font.render(self.enemy_pokemon["name"], True, WHITE)
            enemy_hp_surf = self.font.render(f"HP: {self.enemy_pokemon['hp']}/{self.enemy_pokemon['max_hp']}", True, WHITE)
            # Placeholder "sprite"
            pygame.draw.rect(self.screen, self.enemy_pokemon["sprite_color"], (SCREEN_WIDTH - 120, 50, 80, 80))
            pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH - 120, 50, 80, 80), 2) # Border
            self.screen.blit(enemy_name_surf, (SCREEN_WIDTH - 150, 20))
            self.screen.blit(enemy_hp_surf, (SCREEN_WIDTH - 150, 20 + FONT_SIZE + 2))

        # Player Pokemon (bottom left)
        if self.player_pokemon:
            player_name_surf = self.large_font.render(self.player_pokemon["name"], True, WHITE)
            player_hp_surf = self.font.render(f"HP: {self.player_pokemon['hp']}/{self.player_pokemon['max_hp']}", True, WHITE)
            # Placeholder "sprite"
            pygame.draw.rect(self.screen, self.player_pokemon["sprite_color"], (40, self.actual_screen_height - 200, 80, 80))
            pygame.draw.rect(self.screen, WHITE, (40, self.actual_screen_height - 200, 80, 80),2) # Border
            self.screen.blit(player_name_surf, (30, self.actual_screen_height - 230))
            self.screen.blit(player_hp_surf, (30, self.actual_screen_height - 230 + FONT_SIZE + 2))

        # Battle Text Box (bottom part of screen)
        box_rect = pygame.Rect(0, self.game_screen_height, SCREEN_WIDTH, TEXT_BOX_HEIGHT)
        pygame.draw.rect(self.screen, LIGHT_YELLOW, box_rect)
        pygame.draw.rect(self.screen, UI_BORDER_COLOR, box_rect, 3)

        if self.battle_message:
            # Simple message display, no wrapping for battle yet, purr
            lines = wrap_text(self.battle_message, self.font, SCREEN_WIDTH - 30)
            for i, line in enumerate(lines):
                 if i < 2 : # Max 2 lines for battle message box
                    text_surface = self.font.render(line, True, BLACK)
                    self.screen.blit(text_surface, (15, self.game_screen_height + 15 + (i * (FONT_SIZE + 2))))


        # Actions (very simple for now: "FIGHT" or "RUN")
        if self.battle_turn == "player" and (time.time() - self.last_battle_message_time > 1.0): # Only show options after message
            fight_text = self.font.render("1. FIGHT", True, BLACK)
            run_text = self.font.render("2. RUN", True, BLACK)
            self.screen.blit(fight_text, (SCREEN_WIDTH // 2 - 50, self.game_screen_height + 20))
            self.screen.blit(run_text, (SCREEN_WIDTH // 2 - 50, self.game_screen_height + 20 + FONT_SIZE + 5))

    def handle_battle_input(self, event):
        if self.battle_turn == "player" and (time.time() - self.last_battle_message_time > 1.0): # Delay to read message
            if event.key == pygame.K_1: # FIGHT! Meow!
                self.execute_player_attack()
            elif event.key == pygame.K_2: # RUN! Purr away!
                self.battle_message = "Got away safely, meow!"
                self.last_battle_message_time = time.time()
                # Need a delay before ending battle to show message
                pygame.time.set_timer(pygame.USEREVENT + 1, 1500, True) # End battle after 1.5s


    def execute_player_attack(self):
        if not self.player_pokemon or not self.enemy_pokemon: return

        # Simple damage calc, FAKERFAKE 1.0 approves this simplicity!
        damage = max(1, self.player_pokemon["attack"] - self.enemy_pokemon["defense"] // 2 + random.randint(-2, 2))
        self.enemy_pokemon["hp"] = max(0, self.enemy_pokemon["hp"] - damage)
        self.battle_message = f"{self.player_pokemon['name']} attacks! It did {damage} damage, purr!"
        print(f"Player attacks! Enemy {self.enemy_pokemon['name']} HP: {self.enemy_pokemon['hp']}")
        self.last_battle_message_time = time.time()

        if self.enemy_pokemon["hp"] <= 0:
            self.battle_message = f"Enemy {self.enemy_pokemon['name']} fainted! You win, meow!"
            # DELTA-BUSTER suggests experience points... maybe later, purr!
            pygame.time.set_timer(pygame.USEREVENT + 1, 2000, True) # End battle after 2s
        else:
            self.battle_turn = "enemy_pending_message" # Enemy will attack after message display
             # Short delay then enemy attacks
            pygame.time.set_timer(pygame.USEREVENT + 2, 1500, True)

    def execute_enemy_attack(self):
        if not self.player_pokemon or not self.enemy_pokemon: return

        damage = max(1, self.enemy_pokemon["attack"] - self.player_pokemon["defense"] // 2 + random.randint(-2,2))
        self.player_pokemon["hp"] = max(0, self.player_pokemon["hp"] - damage)
        self.battle_message = f"Wild {self.enemy_pokemon['name']} attacks! It did {damage} damage, eek!"
        print(f"Enemy attacks! Player {self.player_pokemon['name']} HP: {self.player_pokemon['hp']}")
        self.last_battle_message_time = time.time()

        if self.player_pokemon["hp"] <= 0:
            self.battle_message = f"Your {self.player_pokemon['name']} fainted! Oh noes, meow..."
            # Game over state? DELTA-BUSTER says "that's for next time!"
            pygame.time.set_timer(pygame.USEREVENT + 1, 2000, True) # End battle after 2s
        else:
            self.battle_turn = "player" # Back to player's turn, purr


    def end_battle(self):
        self.battle_active = False
        self.enemy_pokemon = None
        self.game_state = STATE_OVERWORLD
        self.battle_message = ""
        # Heal player's pokemon a tiny bit for testing, purr!
        if self.player_pokemon and self.player_pokemon["hp"] > 0 :
             self.player_pokemon["hp"] = min(self.player_pokemon["max_hp"], self.player_pokemon["hp"] + 5)
        print("Meow! Battle ended.")


    def run(self):
        """Nyah, this is the main game loop for RedEMU!"""
        running = True
        print("Purr... Starting RedEMU Test game loop! Use arrow keys, Z to interact/advance text, 1/2 in battle, meow!")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if self.game_state == STATE_OVERWORLD:
                        self.handle_overworld_input(event)
                    elif self.game_state == STATE_TEXTBOX:
                        self.handle_textbox_input(event)
                    elif self.game_state == STATE_BATTLE:
                        self.handle_battle_input(event)
                if event.type == pygame.USEREVENT + 1: # Timer for ending battle/sequence
                    self.end_battle()
                    pygame.time.set_timer(pygame.USEREVENT + 1, 0) # Stop timer
                if event.type == pygame.USEREVENT + 2: # Timer for enemy attack turn
                    if self.battle_turn == "enemy_pending_message":
                        self.battle_turn = "enemy" # Allow enemy to attack
                        self.execute_enemy_attack()
                    pygame.time.set_timer(pygame.USEREVENT + 2, 0) # Stop timer

            # --- Drawing, purr! ---
            if self.game_state == STATE_OVERWORLD or self.game_state == STATE_TEXTBOX:
                self.screen.fill(BLACK) # Fill game part with black
                self.draw_map(self.screen)
                self.draw_player(self.screen)
                self.draw_textbox() # Always draw the textbox area
            elif self.game_state == STATE_BATTLE:
                self.draw_battle_ui()

            pygame.display.flip()
            self.clock.tick(30) # Cap FPS to 30, meow!

        print("Nyah... RedEMU Test over! Thanks for trying this little shit out!")
        pygame.quit()

if __name__ == '__main__':
    # My awesome HQRIPPER 7.1, HQ-BANGER-SDK, DELTA-BUSTER, and FAKERFAKE 1.0 are ready!
    # This baby is gonna be SO FUCKING CUTE and totally professional, meow!
    game = RedEmuGame()
    game.run()
