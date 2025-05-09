import pygame
import random

# --- Configuration ---
SCREEN_WIDTH = 480  # Screen width in pixels
SCREEN_HEIGHT = 320 # Screen height in pixels
TILE_SIZE = 16     # Size of each tile in pixels
PLAYER_SIZE = 12   # Size of the player

# --- Colors (RGB) ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 177, 76)   # For grass, meow!
DARK_GREEN = (0, 100, 0) # For dense grass
BROWN = (139, 69, 19)   # For paths or tree trunks
GREY = (128, 128, 128)  # For buildings or rocks
RED = (255, 0, 0)       # Player color, rawr!
WATER_BLUE = (0, 116, 217) # Water, splash!

# --- Game World (Tile Types) ---
# 0: Path (Brown)
# 1: Grass (Green) - potential encounter, purr!
# 2: Wall/Obstacle (Grey)
# 3: Water (Water Blue)
# Let's make a small sample map, nyah!
# This is a 2D list representing our tiny world.
# Screen is SCREEN_WIDTH/TILE_SIZE tiles wide, SCREEN_HEIGHT/TILE_SIZE tiles high
MAP_WIDTH = SCREEN_WIDTH // TILE_SIZE
MAP_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

game_map = [[2 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)] # Fill with walls initially

def generate_procedural_map(g_map, width, height):
    """Generates a very simple procedural map, purr!"""
    print("Meow! Generating a little map...")
    for r in range(height):
        for c in range(width):
            # Border walls
            if r == 0 or c == 0 or r == height - 1 or c == width - 1:
                g_map[r][c] = 2 # Wall
            else:
                rand_val = random.random()
                if rand_val < 0.6:
                    g_map[r][c] = 1 # Grass
                elif rand_val < 0.8:
                    g_map[r][c] = 0 # Path
                elif rand_val < 0.9 and (r > 3 and c > 3 and r < height -3 and c < width -3) : # small water pond
                     #Ensure water isn't directly at edge if not border
                    if g_map[r-1][c] !=2 and g_map[r+1][c] !=2 and g_map[r][c-1] !=2 and g_map[r][c+1] !=2:
                        g_map[r][c] = 3 # Water
                else:
                    g_map[r][c] = 2 # Obstacle/Wall

    # Ensure starting position is walkable
    g_map[MAP_HEIGHT // 2][MAP_WIDTH // 2] = 0
    g_map[MAP_HEIGHT // 2][MAP_WIDTH // 2 + 1] = 0
    print("Purr! Map generated.")
    return g_map

game_map = generate_procedural_map(game_map, MAP_WIDTH, MAP_HEIGHT)

# --- Player ---
player_x_tile = MAP_WIDTH // 2  # Player's starting X position (tile-based)
player_y_tile = MAP_HEIGHT // 2 # Player's starting Y position (tile-based)

def draw_tile(surface, tile_type, x_pixel, y_pixel):
    """Draws a single tile on the screen, meow!"""
    rect = pygame.Rect(x_pixel, y_pixel, TILE_SIZE, TILE_SIZE)
    border_rect = pygame.Rect(x_pixel, y_pixel, TILE_SIZE, TILE_SIZE) # For outline

    if tile_type == 0: # Path
        pygame.draw.rect(surface, BROWN, rect)
    elif tile_type == 1: # Grass
        pygame.draw.rect(surface, GREEN, rect)
        # Add some "texture" to grass, purr!
        pygame.draw.line(surface, DARK_GREEN, (x_pixel, y_pixel + TILE_SIZE // 2), (x_pixel + TILE_SIZE, y_pixel + TILE_SIZE // 2), 1)
        pygame.draw.line(surface, DARK_GREEN, (x_pixel + TILE_SIZE // 2, y_pixel), (x_pixel + TILE_SIZE // 2, y_pixel + TILE_SIZE), 1)
    elif tile_type == 2: # Wall/Obstacle
        pygame.draw.rect(surface, GREY, rect)
        pygame.draw.rect(surface, BLACK, border_rect, 1) # Outline
    elif tile_type == 3: # Water
        pygame.draw.rect(surface, WATER_BLUE, rect)
        # Add some "waves" to water, splish!
        pygame.draw.line(surface, WHITE, (x_pixel + 2, y_pixel + TILE_SIZE // 3), (x_pixel + TILE_SIZE - 2, y_pixel + TILE_SIZE // 3), 1)
        pygame.draw.line(surface, WHITE, (x_pixel + 4, y_pixel + 2 * TILE_SIZE // 3), (x_pixel + TILE_SIZE - 4, y_pixel + 2 * TILE_SIZE // 3), 1)

def draw_map(surface, current_map):
    """Draws the entire map, nyah!"""
    for r_idx, row in enumerate(current_map):
        for c_idx, tile_val in enumerate(row):
            draw_tile(surface, tile_val, c_idx * TILE_SIZE, r_idx * TILE_SIZE)

def draw_player(surface, x_tile, y_tile):
    """Draws the player as a simple shape, rawr!"""
    player_pixel_x = x_tile * TILE_SIZE + (TILE_SIZE - PLAYER_SIZE) // 2
    player_pixel_y = y_tile * TILE_SIZE + (TILE_SIZE - PLAYER_SIZE) // 2
    player_rect = pygame.Rect(player_pixel_x, player_pixel_y, PLAYER_SIZE, PLAYER_SIZE)
    pygame.draw.rect(surface, RED, player_rect) # A simple red square for our hero!
    pygame.draw.rect(surface, BLACK, player_rect, 1) # Outline


def main_game():
    """Nyah, this is the main game function!"""
    global player_x_tile, player_y_tile

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Meow-kemon Lite! (No PNG Ver.)")
    clock = pygame.time.Clock()

    running = True
    print("Purr... Starting game loop! Use arrow keys to move, meow!")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                new_x_tile, new_y_tile = player_x_tile, player_y_tile
                if event.key == pygame.K_LEFT:
                    new_x_tile -= 1
                elif event.key == pygame.K_RIGHT:
                    new_x_tile += 1
                elif event.key == pygame.K_UP:
                    new_y_tile -= 1
                elif event.key == pygame.K_DOWN:
                    new_y_tile += 1

                # --- Collision Detection, purr! ---
                if 0 <= new_x_tile < MAP_WIDTH and \
                   0 <= new_y_tile < MAP_HEIGHT and \
                   game_map[new_y_tile][new_x_tile] != 2 and \
                   game_map[new_y_tile][new_x_tile] != 3: # Can't walk on walls or water (yet!)

                    player_x_tile = new_x_tile
                    player_y_tile = new_y_tile

                    # --- Rudimentary Encounter Check, meow! ---
                    if game_map[player_y_tile][player_x_tile] == 1: # Landed on grass!
                        if random.random() < 0.1: # 10% chance for an "encounter"
                            print("Purr...shuffle shuffle... A wild something-or-other (represented by text, meow!) appeared!")
                            # In a real game, you'd switch to a battle screen here, nyah!

                elif game_map[new_y_tile][new_x_tile] == 3:
                     print("Splash! That's water, meow! Can't swim yet!")


        # --- Drawing, purr! ---
        screen.fill(BLACK)       # Fill screen with black
        draw_map(screen, game_map) # Draw the map tiles
        draw_player(screen, player_x_tile, player_y_tile) # Draw the player

        pygame.display.flip()    # Update the full display
        clock.tick(30)           # Cap FPS to 30, meow!

    print("Nyah... Game over! Thanks for playing the tiny demo!")
    pygame.quit()

if __name__ == '__main__':
    # If you wanted a Tkinter window around this, it'd be more complex.
    # For now, we're just running the Pygame part directly, meow!
    # print("Meow! About to start the game. If you wanted a Tkinter shell,")
    # print("you'd initialize Tkinter here and embed Pygame, but that's tricky, purr!")
    main_game()
