import pygame
import sys

# --- Wrapped Initialization with Error Handling ---
try:
    pygame.init()
except Exception as e:
    print(f"Fatal Error: Could not initialize Pygame modules: {e}")
    print("Please ensure Pygame is installed correctly.")
    sys.exit()

# Attempt to initialize font with fallback
font = None
try:
    font = pygame.font.SysFont(None, 32)
    if font is None: # Should not happen with SysFont(None,...) but being defensive
        raise pygame.error("SysFont(None, 32) returned None.")
except Exception as e_font_default:
    print(f"Warning: Could not load default system font: {e_font_default}")
    common_fonts = ["arial", "calibri", "verdana", "tahoma", "dejavusans", "sans"] # Added generic 'sans'
    for fname in common_fonts:
        try:
            font = pygame.font.SysFont(fname, 32)
            if font:
                print(f"Successfully loaded fallback font: '{fname}'")
                break
        except Exception as e_font_fallback: # Catch specific font loading errors
            print(f"Note: Fallback font '{fname}' not found or failed to load: {e_font_fallback}")
            continue
    if font is None: # Still no font
        print("CRITICAL ERROR: No suitable font found after checking fallbacks.")
        print("Please check your system's font configuration or Pygame installation.")
        print("The game cannot continue without a font.")
        pygame.quit()
        sys.exit()

WIDTH, HEIGHT = 800, 600
screen = None # Initialize to None
try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mariomon Battle Engine (No PNG)")
    clock = pygame.time.Clock()
except Exception as e:
    print(f"Fatal Error: Could not set up Pygame display: {e}")
    if pygame.get_init(): # Check if Pygame was initialized before trying to quit
        pygame.quit()
    sys.exit()

# --- Colors ---
SKY_COLOR = (135, 206, 235)
GROUND_COLOR = (222, 184, 135)
TEXTBOX_COLOR = (250, 250, 250)
BORDER_COLOR = (0, 0, 0)
HP_GREEN = (34, 177, 76)
HP_YELLOW = (255, 201, 14)
HP_RED = (237, 28, 36)
TEXT_COLOR = (0, 0, 0)

# --- Sprite System ---
class Sprite:
    def __init__(self, x, y, sprite_data, palette, pixel_scale=5):
        self.base_x = x
        self.base_y = y
        self.x = x
        self.y = y
        self.sprite_data = sprite_data
        self.palette = palette
        self.pixel_scale = pixel_scale
        self.surface = self.build_surface()
        self.anim_offset = 0
        self.animating = False
        self.flicker_timer = 0
        self.flicker_duration = 0
        self.visible = True

    def build_surface(self):
        width = len(self.sprite_data[0]) * self.pixel_scale
        height = len(self.sprite_data) * self.pixel_scale
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        for y_idx, row in enumerate(self.sprite_data):
            for x_idx, color_index in enumerate(row):
                if 0 <= color_index < len(self.palette):
                    color = self.palette[color_index]
                    if len(color) == 4 and color[3] != 0: # Check alpha channel for transparency
                        pygame.draw.rect(
                            surf,
                            color[:3], # Draw with RGB
                            (x_idx * self.pixel_scale, y_idx * self.pixel_scale, self.pixel_scale, self.pixel_scale)
                        )
                else:
                    print(f"Warning: Invalid color_index {color_index} in sprite_data. Max palette index: {len(self.palette)-1}")
        return surf

    def start_attack_anim(self):
        self.animating = True
        self.anim_offset = 0

    def start_damage_flicker(self, duration=30):
        self.flicker_duration = duration
        self.flicker_timer = duration
        self.visible = True

    def update(self):
        if self.animating:
            self.anim_offset += 2
            self.x = self.base_x + self.anim_offset
            if self.anim_offset >= 20:
                self.x = self.base_x + 20
            if self.anim_offset >= 40:
                self.animating = False
                self.x = self.base_x

        if self.flicker_timer > 0:
            self.flicker_timer -= 1
            self.visible = self.flicker_timer % 10 >= 5
            if self.flicker_timer == 0:
                self.visible = True

    def draw(self, target_surface):
        if self.visible:
            target_surface.blit(self.surface, (self.x, self.y))

# --- Mariomon Data Structure ---
class Mariomon:
    def __init__(self, name, sprite_obj, max_hp, moves):
        self.name = name.upper()
        self.sprite = sprite_obj
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.moves = [{'name': move['name'].upper(), 'power': move['power']} for move in moves]

    def take_damage(self, amount):
        self.current_hp -= amount
        if self.current_hp < 0:
            self.current_hp = 0
        if self.sprite: # Check if sprite exists
            self.sprite.start_damage_flicker()

    def is_fainted(self):
        return self.current_hp <= 0

    def get_move(self, move_index=0):
        if self.moves and 0 <= move_index < len(self.moves):
            return self.moves[move_index]
        return None

# --- Text System ---
class TextPrinter:
    def __init__(self, text_content, x, y, speed=2):
        self.base_text = text_content # Renamed parameter to avoid conflict
        self.x = x
        self.y = y
        self.speed = max(1, speed) # Ensure speed is at least 1
        self.index = 0
        self.counter = 0
        self.done = False
        self.active = False

    def set_text(self, new_text):
        self.base_text = new_text
        self.index = 0
        self.counter = 0
        self.done = False
        self.active = True

    def update(self):
        if self.active and not self.done:
            self.counter += 1
            if self.counter >= self.speed:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.base_text):
                    self.done = True

    def draw(self, target_surface):
        if self.active and font: # Check if font is loaded
            render_text = font.render(self.base_text[:self.index], True, TEXT_COLOR)
            target_surface.blit(render_text, (self.x, self.y))

    def skip(self):
        if self.active:
            self.index = len(self.base_text)
            self.done = True

# --- Menu System ---
class Menu:
    def __init__(self, options, x_offset, y_base_coord, item_width=160):
        self.options = options
        self.selected = 0
        self.item_width = item_width
        self.menu_box_x = WIDTH // 2
        self.menu_box_y = HEIGHT - 150
        self.menu_box_width = WIDTH // 2
        self.menu_box_height = 150
        self.option_positions = []

        if len(options) == 4:
            col1_x = self.menu_box_x + x_offset
            col2_x = self.menu_box_x + self.menu_box_width // 2 + x_offset - 20
            row1_y = y_base_coord - 40
            row2_y = y_base_coord
            self.option_positions = [
                (col1_x, row1_y), (col2_x, row1_y),
                (col1_x, row2_y), (col2_x, row2_y)
            ]
        elif len(options) == 2:
            opt1_x = self.menu_box_x + x_offset
            opt2_x = self.menu_box_x + self.menu_box_width // 2 + x_offset - 20
            y_pos = y_base_coord
            self.option_positions = [(opt1_x, y_pos), (opt2_x, y_pos)]

    def draw(self, target_surface):
        if not self.option_positions: return # Don't draw if not initialized properly

        menu_rect = pygame.Rect(self.menu_box_x, self.menu_box_y, self.menu_box_width, self.menu_box_height)
        pygame.draw.rect(target_surface, TEXTBOX_COLOR, menu_rect)
        pygame.draw.rect(target_surface, BORDER_COLOR, menu_rect, 3)

        for i, option in enumerate(self.options):
            if font: # Check font
                text = font.render(option, True, TEXT_COLOR)
                pos_x, pos_y = self.option_positions[i]
                target_surface.blit(text, (pos_x, pos_y))

        if self.options and font: # Check options and font
            cursor_pos_x, cursor_pos_y = self.option_positions[self.selected]
            cursor = font.render("▶", True, TEXT_COLOR)
            target_surface.blit(cursor, (cursor_pos_x - 30, cursor_pos_y))

    def move(self, direction_key):
        num_options = len(self.options)
        if not num_options: return

        if num_options == 4:
            current_row, current_col = divmod(self.selected, 2)
            if direction_key == pygame.K_RIGHT and current_col == 0: self.selected += 1
            elif direction_key == pygame.K_LEFT and current_col == 1: self.selected -= 1
            elif direction_key == pygame.K_DOWN and current_row == 0: self.selected += 2
            elif direction_key == pygame.K_UP and current_row == 1: self.selected -= 2
        elif num_options == 2:
            if direction_key == pygame.K_RIGHT: self.selected = (self.selected + 1) % num_options
            elif direction_key == pygame.K_LEFT: self.selected = (self.selected - 1 + num_options) % num_options

    def get_selected(self):
        if self.options:
            return self.options[self.selected]
        return None

# --- Battle System Globals & Instances ---
battle_state = "intro"
palette = [
    (0,0,0,0), (228,94,39,255), (0,0,170,255), (255,255,255,255), (247,190,128,255),
    (100,50,0,255), (40,130,20,255), (240,200,50,255), (200,60,10,255), (150,150,150,255)
] # Ensured all have alpha

player_sprite_data = [[0,0,5,5,5,5,0,0],[0,5,1,1,1,1,5,0],[0,5,1,4,4,1,5,0],[0,0,2,1,1,2,0,0],[0,2,2,3,3,2,2,0],[0,2,2,2,2,2,2,0],[2,2,0,2,2,0,2,2],[5,5,0,0,0,0,5,5]]
enemy_sprite_data = [[0,0,0,8,8,0,0,0],[0,0,8,8,8,8,0,0],[0,6,7,7,7,7,6,0],[6,7,6,3,3,6,7,6],[6,7,7,7,7,7,7,6],[0,6,7,7,7,7,6,0],[0,0,9,6,6,9,0,0],[0,9,9,0,0,9,9,0]]

try:
    player_sprite_obj = Sprite(100, HEIGHT//2 + 45, player_sprite_data, palette, pixel_scale=8)
    enemy_sprite_obj = Sprite(WIDTH - 200 - 30, 60, enemy_sprite_data, palette, pixel_scale=8)

    player_mariomon = Mariomon("PIRATE FLAMES", player_sprite_obj, 100, [{'name': "FIREBALL", 'power': 30}])
    enemy_mariomon = Mariomon("CORRUPTED BOWSER", enemy_sprite_obj, 100, [{'name': "CLAW SWIPE", 'power': 20}])

    battle_text_printer = TextPrinter("", 30, HEIGHT - 120, speed=2)
    main_menu = Menu(["FIGHT", "BAG", "POKéMON", "RUN"], x_offset=40, y_base_coord=HEIGHT - 90)
    active_menu = main_menu
    battle_text_printer.set_text(f"A wild {enemy_mariomon.name} appeared!")

except Exception as e:
    print(f"Fatal Error during game asset setup: {e}")
    if pygame.get_init(): pygame.quit()
    sys.exit()


current_player_move = None
current_enemy_move = None

# HP Bar Function
def draw_hp_bar(mariomon, x, y, bar_width=120, bar_height=12):
    if not mariomon: return
    ratio = mariomon.current_hp / mariomon.max_hp if mariomon.max_hp > 0 else 0
    ratio = max(0, min(1, ratio)) # Clamp ratio

    hp_color = HP_GREEN
    if ratio < 0.5: hp_color = HP_YELLOW
    if ratio < 0.2: hp_color = HP_RED

    pygame.draw.rect(screen, (50,50,50), (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, hp_color, (x, y, bar_width * ratio, bar_height))
    pygame.draw.rect(screen, BORDER_COLOR, (x, y, bar_width, bar_height), 2)

    if font: # Check font
        hp_text_surf = font.render(f"HP: {mariomon.current_hp}/{mariomon.max_hp}", True, TEXT_COLOR)
        screen.blit(hp_text_surf, (x + bar_width + 5, y -2))
        name_text_surf = font.render(mariomon.name, True, TEXT_COLOR)
        screen.blit(name_text_surf, (x, y - 25))

# --- Main Loop ---
running = True
try:
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if battle_text_printer.active and not battle_text_printer.done:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        battle_text_printer.skip()
                else:
                    if battle_state == "player_menu" and active_menu: # Check active_menu
                        if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                            active_menu.move(event.key)
                        elif event.key == pygame.K_RETURN:
                            selected_option = active_menu.get_selected()
                            if selected_option == "FIGHT":
                                current_player_move = player_mariomon.get_move(0)
                                if current_player_move:
                                    battle_text_printer.set_text(f"{player_mariomon.name} used {current_player_move['name']}!")
                                    player_mariomon.sprite.start_attack_anim()
                                    battle_state = "player_action_resolve"
                                else:
                                    battle_text_printer.set_text(f"{player_mariomon.name} has no moves!")
                                    battle_state = "temp_message_player_menu"
                            elif selected_option == "RUN":
                                battle_text_printer.set_text("Got away safely!")
                                battle_state = "battle_end"
                            else:
                                battle_text_printer.set_text(f"{selected_option} is not yet implemented.")
                                battle_state = "temp_message_player_menu"

        player_mariomon.sprite.update()
        enemy_mariomon.sprite.update()
        battle_text_printer.update()

        if battle_text_printer.done:
            if battle_state == "intro":
                battle_text_printer.set_text(f"What will {player_mariomon.name} do?")
                battle_state = "player_menu"
            elif battle_state == "temp_message_player_menu":
                battle_text_printer.set_text(f"What will {player_mariomon.name} do?")
                battle_state = "player_menu"
            elif battle_state == "player_action_resolve":
                if current_player_move and (not player_mariomon.sprite.animating or battle_text_printer.speed <=1):
                    enemy_mariomon.take_damage(current_player_move['power'])
                    battle_text_printer.set_text(f"{current_player_move['name']} hit!")
                    battle_state = "enemy_damage_check"
                    current_player_move = None
            elif battle_state == "enemy_damage_check":
                if enemy_mariomon.is_fainted():
                    battle_text_printer.set_text(f"{enemy_mariomon.name} fainted! {player_mariomon.name} wins!")
                    battle_state = "battle_end"
                else:
                    current_enemy_move = enemy_mariomon.get_move(0)
                    if current_enemy_move:
                        battle_text_printer.set_text(f"{enemy_mariomon.name} used {current_enemy_move['name']}!")
                        enemy_mariomon.sprite.start_attack_anim()
                        battle_state = "enemy_action_resolve"
            elif battle_state == "enemy_action_resolve":
                if current_enemy_move and (not enemy_mariomon.sprite.animating or battle_text_printer.speed <=1):
                    player_mariomon.take_damage(current_enemy_move['power'])
                    battle_text_printer.set_text(f"{current_enemy_move['name']} hit!")
                    battle_state = "player_damage_check"
                    current_enemy_move = None
            elif battle_state == "player_damage_check":
                if player_mariomon.is_fainted():
                    battle_text_printer.set_text(f"{player_mariomon.name} fainted! {enemy_mariomon.name} wins!")
                    battle_state = "battle_end"
                else:
                    battle_text_printer.set_text(f"What will {player_mariomon.name} do?")
                    battle_state = "player_menu"
            elif battle_state == "battle_end":
                pass # Game ends, waits for ESC or QUIT

        if screen: # Ensure screen was initialized
            screen.fill(SKY_COLOR)
            ground_rect = pygame.Rect(0, HEIGHT // 2 + 100, WIDTH, HEIGHT // 2 - 100)
            pygame.draw.rect(screen, GROUND_COLOR, ground_rect)

            if enemy_sprite_obj and player_sprite_obj: # Check if sprites exist
                enemy_platform_rect = pygame.Rect(enemy_sprite_obj.base_x - 20, enemy_sprite_obj.base_y + enemy_sprite_obj.surface.get_height() -10, enemy_sprite_obj.surface.get_width() + 40, 20)
                pygame.draw.ellipse(screen, (180,140,100), enemy_platform_rect)
                player_platform_rect = pygame.Rect(player_sprite_obj.base_x - 20, player_sprite_obj.base_y + player_sprite_obj.surface.get_height()-10, player_sprite_obj.surface.get_width() + 40, 20)
                pygame.draw.ellipse(screen, (180,140,100), player_platform_rect)

                enemy_mariomon.sprite.draw(screen)
                player_mariomon.sprite.draw(screen)

            draw_hp_bar(enemy_mariomon, WIDTH - 250, 50)
            draw_hp_bar(player_mariomon, 50, HEIGHT - 200)

            main_textbox_rect = pygame.Rect(0, HEIGHT - 150, WIDTH, 150)
            pygame.draw.rect(screen, TEXTBOX_COLOR, main_textbox_rect)
            pygame.draw.rect(screen, BORDER_COLOR, main_textbox_rect, 5)

            battle_text_printer.draw(screen)

            if battle_state == "player_menu" and battle_text_printer.done and active_menu: # Check active_menu
                active_menu.draw(screen)

            pygame.display.flip()

except Exception as e:
    print(f"An critical error occurred during the game loop: {e}")
    import traceback
    traceback.print_exc() # Print full traceback for debugging
finally:
    if pygame.get_init(): # Check if Pygame was initialized before trying to quit
        pygame.quit()
    sys.exit()
