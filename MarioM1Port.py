import pygame
import json

pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
HUD_HEIGHT = 150
GRID_SIZE = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Define Themes
themes = {
    'Retro': {
        'ground': (139, 69, 19),        # Brown
        'brick': (205, 133, 63),        # Light Brown
        'question': (255, 223, 0),      # Yellow
        'coin': (255, 215, 0),          # Gold
        'enemy': (178, 34, 34),         # Firebrick
        'water': (0, 191, 255),         # Deep Sky Blue
        'background': (34, 34, 34),     # Dark Gray
    },
    'SMB 8-bit': {
        'ground': (165, 42, 42),         # Brown
        'brick': (255, 165, 0),          # Orange
        'question': (255, 255, 0),       # Bright Yellow
        'coin': (255, 223, 0),           # Gold
        'enemy': (255, 0, 0),            # Red
        'water': (0, 0, 255),            # Blue
        'background': (135, 206, 235),   # Sky Blue
    },
    'NSMB': {
        'ground': (160, 82, 45),         # Sienna
        'brick': (222, 184, 135),        # Burlywood
        'question': (255, 255, 224),     # Light Yellow
        'coin': (255, 223, 0),           # Gold
        'enemy': (220, 20, 60),          # Crimson
        'water': (64, 164, 223),         # Blue
        'background': (70, 130, 180),    # Steel Blue
    }
}

current_theme = 'Retro'  # Default theme

# Initialize the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT + HUD_HEIGHT))
pygame.display.set_caption("Mario Maker 3 PC/M1 Port")
game_clock = pygame.time.Clock()

# Classes for various game elements
class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, tile_type):
        super().__init__()
        self.tile_type = tile_type
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.rect = self.image.get_rect(topleft=pos)
        self.update_image()

    def update_image(self):
        theme_colors = themes[current_theme]
        if self.tile_type == 'ground':
            self.image.fill(theme_colors['ground'])
        elif self.tile_type == 'brick':
            self.image.fill(theme_colors['brick'])
        elif self.tile_type == 'question':
            self.image.fill(theme_colors['question'])
            pygame.draw.line(self.image, BLACK, (10, 10), (30, 10), 3)
            pygame.draw.line(self.image, BLACK, (10, 10), (10, 30), 3)
        elif self.tile_type == 'coin':
            self.image.fill(theme_colors['coin'])
            pygame.draw.circle(self.image, (255, 255, 255), (GRID_SIZE // 2, GRID_SIZE // 2), GRID_SIZE // 2 - 5)
        elif self.tile_type == 'enemy':
            self.image.fill(theme_colors['enemy'])
        elif self.tile_type == 'water':
            self.image.fill(theme_colors['water'])
            pygame.draw.rect(self.image, BLUE, (10, 10, 20, 20))  # Simple wave pattern
        else:
            self.image.fill(WHITE)

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=pos)
        self.velocity = pygame.Vector2(0, 0)

    def update(self, solid_tiles):
        keys = pygame.key.get_pressed()
        self.velocity.x = 0

        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.velocity.x = -5
        elif keys[pygame.K_RIGHT]:
            self.velocity.x = 5

        # Gravity and vertical movement
        self.velocity.y += 0.5  # Gravity
        self.velocity.y = min(self.velocity.y, 10)  # Limit falling speed

        # Move horizontally and handle collisions
        self.rect.x += self.velocity.x
        self.handle_collisions(self.velocity.x, 0, solid_tiles)

        # Move vertically and handle collisions
        self.rect.y += self.velocity.y
        self.handle_collisions(0, self.velocity.y, solid_tiles)

        # Prevent player from falling below the screen
        if self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.velocity.y = 0

    def handle_collisions(self, vel_x, vel_y, solid_tiles):
        collisions = pygame.sprite.spritecollide(self, solid_tiles, False)
        for tile in collisions:
            if vel_x > 0:  # Moving right; Hit the left side of the tile
                self.rect.right = tile.rect.left
            elif vel_x < 0:  # Moving left; Hit the right side of the tile
                self.rect.left = tile.rect.right
            if vel_y > 0:  # Moving down; Hit the top side of the tile
                self.rect.bottom = tile.rect.top
                self.velocity.y = 0
            elif vel_y < 0:  # Moving up; Hit the bottom side of the tile
                self.rect.top = tile.rect.bottom
                self.velocity.y = 0

    def jump(self):
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.velocity.y = -12

# Helper functions
def snap_to_grid(pos, size):
    return (pos[0] // size) * size, (pos[1] // size) * size

# Save and Load Functions
def save_level(filename="level.json"):
    level_data = {
        "tiles": [],
        "theme": current_theme
    }
    for tile in tiles_group:
        tile_data = {
            "x": tile.rect.x,
            "y": tile.rect.y,
            "type": tile.tile_type
        }
        level_data["tiles"].append(tile_data)
    with open(filename, "w") as file:
        json.dump(level_data, file, indent=4)
    print(f"Level saved to {filename}.")

def load_level(filename="level.json"):
    global current_theme
    try:
        with open(filename, "r") as file:
            level_data = json.load(file)
            theme = level_data.get("theme", "Retro")
            set_theme(theme)
            tiles_group.empty()
            all_sprites.empty()
            all_sprites.add(player)

            for tile_data in level_data["tiles"]:
                tile = Tile((tile_data["x"], tile_data["y"]), tile_data["type"])
                tiles_group.add(tile)
                all_sprites.add(tile)
        print(f"Level loaded from {filename}.")
    except FileNotFoundError:
        print(f"File {filename} not found.")

# Set the theme
def set_theme(theme_name):
    global current_theme
    if theme_name in themes:
        current_theme = theme_name
        for tile in tiles_group:
            tile.update_image()
        print(f"Theme set to '{theme_name}'.")
    else:
        print(f"Theme '{theme_name}' does not exist.")

# Example level data for Mario Construct/Flash-like levels
construct_level_data = [
    "                    ",
    "                    ",
    "   GGGGGGGGGGGGGGG  ",
    "                    ",
    "      B    Q        ",
    "     WWWWWWWW       ",
    "    GGG    C    GGG ",
    "    W     W         ",
    "    WWWWWW          ",
    "GGGGGGGGGGGGGGGGGGGG"
]

# Groups for sprites
tiles_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

# Create the player
player = Player((400, 300))
all_sprites.add(player)

# HUD Setup
HUD_RECT = pygame.Rect(0, WINDOW_HEIGHT, WINDOW_WIDTH, HUD_HEIGHT)

# Define tile types and their icons
tile_types = ['ground', 'brick', 'question', 'coin', 'enemy', 'water']
tile_icons = {}

# Initialize tile icons
for index, tile_type in enumerate(tile_types):
    icon = pygame.Surface((40, 40))
    theme_colors = themes[current_theme]
    if tile_type == 'ground':
        icon.fill(theme_colors['ground'])
    elif tile_type == 'brick':
        icon.fill(theme_colors['brick'])
    elif tile_type == 'question':
        icon.fill(theme_colors['question'])
    elif tile_type == 'coin':
        icon.fill(theme_colors['coin'])
    elif tile_type == 'enemy':
        icon.fill(theme_colors['enemy'])
    elif tile_type == 'water':
        icon.fill(theme_colors['water'])
    else:
        icon.fill(WHITE)
    tile_icons[tile_type] = icon

# HUD buttons positions
button_positions = {}
for i, tile_type in enumerate(tile_types):
    x = 10 + i * 60  # Adjusted spacing for better layout
    y = WINDOW_HEIGHT + 10
    button_positions[tile_type] = pygame.Rect(x, y, 40, 40)

# Theme selection buttons
theme_names = list(themes.keys())
theme_buttons = {}
for i, theme_name in enumerate(theme_names):
    x = 10 + i * 110
    y = WINDOW_HEIGHT + 60
    theme_buttons[theme_name] = pygame.Rect(x, y, 100, 30)

# Save and Load buttons
buttons = {
    "save": pygame.Rect(400, WINDOW_HEIGHT + 60, 80, 30),
    "load": pygame.Rect(490, WINDOW_HEIGHT + 60, 80, 30),
    "load_construct": pygame.Rect(580, WINDOW_HEIGHT + 60, 120, 30),  # Additional load button for construct levels
}

selected_tile_type = 'ground'  # Default selected tile type

# Main loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Check if clicking on HUD tile icons
            for tile_type, rect in button_positions.items():
                if rect.collidepoint(mouse_pos):
                    selected_tile_type = tile_type

            # Check if clicking on Theme buttons
            for theme_name, rect in theme_buttons.items():
                if rect.collidepoint(mouse_pos):
                    set_theme(theme_name)

            # Check if clicking on Save/Load buttons
            if buttons["save"].collidepoint(mouse_pos):
                save_level()
            elif buttons["load"].collidepoint(mouse_pos):
                load_level()
            elif buttons.get("load_construct") and buttons["load_construct"].collidepoint(mouse_pos):
                load_construct_level(construct_level_data, theme_name='Retro') # type: ignore

            # Placing or removing tiles
            if mouse_pos[1] < WINDOW_HEIGHT:  # Ensure we are not clicking on the HUD
                grid_pos = snap_to_grid(mouse_pos, GRID_SIZE)
                if event.button == 1:  # Left click to add a tile
                    for tile in tiles_group:
                        if tile.rect.topleft == grid_pos:
                            tile.kill()
                    tile = Tile(grid_pos, selected_tile_type)
                    tiles_group.add(tile)
                    all_sprites.add(tile)
                elif event.button == 3:  # Right click to remove a tile
                    for tile in tiles_group:
                        if tile.rect.collidepoint(mouse_pos):
                            tile.kill()
                            break

    # Update sprites
    solid_tiles = pygame.sprite.Group([tile for tile in tiles_group if tile.tile_type in ['ground', 'brick', 'question']])
    all_sprites.update(solid_tiles)

    # Draw everything
    window.fill(themes[current_theme]['background'])

    # Draw all tiles
    tiles_group.draw(window)
    window.blit(player.image, player.rect)

    # Draw HUD background
    pygame.draw.rect(window, GRAY, HUD_RECT)

    # Draw tile selection icons
    for tile_type, rect in button_positions.items():
        window.blit(tile_icons[tile_type], rect.topleft)
        if tile_type == selected_tile_type:
            pygame.draw.rect(window, GREEN, rect, 3)
        else:
            pygame.draw.rect(window, BLACK, rect, 1)

    # Draw Theme selection buttons
    for theme_name, rect in theme_buttons.items():
        pygame.draw.rect(window, BLACK, rect, 2)
        font = pygame.font.Font(None, 24)
        theme_text = font.render(theme_name, True, BLACK)
        text_rect = theme_text.get_rect(center=rect.center)
        window.blit(theme_text, text_rect)

    # Draw Save and Load buttons
    pygame.draw.rect(window, BLACK, buttons["save"])
    pygame.draw.rect(window, BLACK, buttons["load"])
    pygame.draw.rect(window, BLACK, buttons["load_construct"])
    font = pygame.font.Font(None, 24)
    save_text = font.render("Save", True, WHITE)
    load_text = font.render("Load", True, WHITE)
    load_construct_text = font.render("Load Construct", True, WHITE)
    window.blit(save_text, buttons["save"].move(20, 5).topleft)
    window.blit(load_text, buttons["load"].move(20, 5).topleft)
    window.blit(load_construct_text, buttons["load_construct"].move(10, 5).topleft)

    # Update display
    pygame.display.update()
    game_clock.tick(60)

pygame.quit()
