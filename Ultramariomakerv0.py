# test_patched.py
# Meow! Mario Worker Style Editor with BETTER Procedural Graphics! Nyaa~! V3.1 (Patched by CATSDK!)
import pygame
import sys
import os
import json # Nyaa~ for saving and loading our purrfect levels!
import math # For drawing cute shapes, teehee!

# --- Purrfect Constants ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
GRID_SIZE = 32
# Make the world bigger, nya!
WORLD_WIDTH_TILES = 100
WORLD_HEIGHT_TILES = 24 # Matches screen height roughly for now
PALETTE_HEIGHT = 120 # Needs a bit more space for drawings, nya!
PALETTE_X = 0
PALETTE_Y = SCREEN_HEIGHT - PALETTE_HEIGHT
FPS = 60 # Super speedy, nyaa! [4]

# --- Cute Colors (More detailed!) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRID_COLOR = (200, 200, 200)
PALETTE_BG = (180, 180, 220) # Lighter purple, nya!
HIGHLIGHT_COLOR = (255, 255, 0) # Yellow highlight, meow!

# --- Colors for *Improved* Procedural Graphics ---
GROUND_COLOR_TOP = (160, 82, 45) # Sienna
GROUND_COLOR_BOTTOM = (139, 69, 19) # SaddleBrown
GROUND_DETAIL = (92, 64, 51) # Darker brown

BRICK_COLOR_LIGHT = (210, 105, 30) # Chocolate
BRICK_COLOR_DARK = (160, 82, 45) # Sienna
BRICK_LINE_COLOR = (100, 50, 10) # Dark brown for mortar

BLOCK_Q_COLOR = (255, 215, 0) # Gold
BLOCK_Q_SHADOW = (200, 150, 0) # Darker Gold
BLOCK_Q_HIGHLIGHT = (255, 235, 100) # Lighter Gold
BLOCK_Q_MARK = BLACK
BLOCK_Q_RIVET = (80, 80, 80)

BLOCK_SOLID_COLOR_LIGHT = (211, 211, 211) # LightGray
BLOCK_SOLID_COLOR_DARK = (169, 169, 169) # DarkGray
BLOCK_SOLID_SHADOW = (105, 105, 105) # DimGray

PIPE_COLOR = (0, 200, 0) # Brighter Green
PIPE_SHADOW = (0, 100, 0) # Dark Green
PIPE_HIGHLIGHT = (152, 251, 152) # Pale Green
PIPE_DARK_LINE = (0, 60, 0)

COIN_COLOR = (255, 223, 0) # Gold Coin
COIN_SHADOW = (204, 178, 0) # Darker Gold
COIN_HIGHLIGHT = (255, 255, 150) # Pale Yellow

GOOMBA_BODY = (165, 42, 42) # Brownish Red
GOOMBA_FEET = (100, 20, 20) # Darker Red/Brown
GOOMBA_EYES = WHITE
GOOMBA_PUPILS = BLACK
GOOMBA_HIGHLIGHT = (200, 80, 80)

PLAYER_START_COLOR = (50, 50, 255) # Blue
PLAYER_START_SYMBOL = WHITE

ERASER_COLOR = (50, 50, 50) # Gray for eraser
ERASER_X = (255, 0, 0) # Red X

# --- Let's get Pygame ready! Purrrr ---
pygame.init()
pygame.font.init() # For text later, maybe! meow!
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("CATSDK's Procedural Graphics Editor! Nyaa~ (Patched!)")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24) # A small font for labels
small_font = pygame.font.SysFont(None, 18) # For tiny labels maybe

# --- Level Data Storage (A cozy dictionary!) ---
# Maps (grid_x, grid_y) tuple to TILE NAME string
level_data = {}

# --- Helper: Draw gradient rect ---
def draw_gradient_rect(surface, top_color, bottom_color, rect):
    """Draws a vertical gradient filling the rectangle. Fucking magic!"""
    steps = rect.height
    if steps <= 0: return # Avoid division by zero if rect has no height, fucker
    try:
        color_step = [(bottom_color[i] - top_color[i]) / steps for i in range(3)]
    except ZeroDivisionError: # Should be caught by steps <= 0, but belt and suspenders, motherfucker
        pygame.draw.rect(surface, top_color, rect) # Just draw flat color if steps is fucked
        return

    for y in range(steps):
        current_color = [top_color[i] + color_step[i] * y for i in range(3)]
        # Clamp colors to valid range, goddamnit
        current_color = [max(0, min(255, int(c))) for c in current_color]
        pygame.draw.line(surface, current_color, (rect.left, rect.top + y), (rect.right - 1, rect.top + y)) # -1 on right? sometimes helps

# --- Procedural Drawing Functions! Meow Magic! (IMPROVED AS FUCK!) ---
# Each function draws a tile onto the 'surface' at 'rect' [7, 9, 10, 12]

def draw_ground(surface, rect):
    # Vertical gradient for ground, fancy!
    draw_gradient_rect(surface, GROUND_COLOR_TOP, GROUND_COLOR_BOTTOM, rect)
    # Add some fucking details, purrr
    # Draw horizontal lines
    pygame.draw.line(surface, GROUND_DETAIL, rect.topleft + pygame.Vector2(0, rect.height // 4), rect.topright + pygame.Vector2(0, rect.height // 4), 1)
    pygame.draw.line(surface, GROUND_DETAIL, rect.midleft + pygame.Vector2(0, rect.height // 8), rect.midright + pygame.Vector2(0, rect.height // 8), 1)
    # Draw some pebbles maybe? Fucking random pebbles!
    try:
        pygame.draw.circle(surface, GROUND_DETAIL, rect.center + pygame.Vector2(-rect.width // 4, rect.height // 3), 2)
        pygame.draw.circle(surface, GROUND_DETAIL, rect.center + pygame.Vector2(rect.width // 4, rect.height // 4), 1)
    except pygame.error as e: # Catch potential errors if rect is too small, fuck it
        print(f"Warning: Couldn't draw ground detail, maybe rect too small? {e}, meow.")


def draw_brick(surface, rect):
    # Slightly nicer brick background
    pygame.draw.rect(surface, BRICK_COLOR_DARK, rect)
    pygame.draw.rect(surface, BRICK_COLOR_LIGHT, rect.inflate(-2, -2))

    # Draw fucking mortar lines [7]
    hw = rect.width // 2
    hh = rect.height // 2
    lw = max(1, rect.width // 16) # Line width scales a bit, holy shit!

    # Horizontal lines
    pygame.draw.line(surface, BRICK_LINE_COLOR, (rect.left, rect.centery), (rect.right, rect.centery), lw)
    # Vertical lines (staggered like a real fucking brick wall)
    pygame.draw.line(surface, BRICK_LINE_COLOR, (rect.centerx, rect.top), (rect.centerx, rect.centery), lw)
    pygame.draw.line(surface, BRICK_LINE_COLOR, (rect.left + hw // 2, rect.centery), (rect.left + hw // 2, rect.bottom), lw)
    pygame.draw.line(surface, BRICK_LINE_COLOR, (rect.right - hw // 2, rect.centery), (rect.right - hw // 2, rect.bottom), lw)

def draw_q_block(surface, rect):
    # Base block with gradient
    draw_gradient_rect(surface, BLOCK_Q_HIGHLIGHT, BLOCK_Q_COLOR, rect)
    pygame.draw.rect(surface, BLOCK_Q_SHADOW, rect.inflate(-4, -4), border_radius=2) # Inner shadow with rounded corners! Fancy as fuck!

    # Draw a better '?' mark, nyaa! [10]
    q_font_size = int(rect.height * 0.7)
    q_surf = None
    try:
        # Try a bolder font first, motherfucker
        q_font = pygame.font.SysFont('Impact', q_font_size, bold=True)
        q_surf = q_font.render("?", True, BLOCK_Q_MARK)
    except Exception as e: # If font is missing or some shit
        print(f"Meow! Couldn't load Impact font for Q block: {e}. Using default font.")
        try:
            q_font = pygame.font.SysFont(None, q_font_size + 4, bold=True) # Fallback font, still bold!
            q_surf = q_font.render("?", True, BLOCK_Q_MARK)
        except Exception as e2:
             print(f"FUCK! Couldn't even load fallback font: {e2}. Skipping '?' drawing.")


    if q_surf: # Only blit if we actually rendered the fucking thing
        q_rect = q_surf.get_rect(center=(rect.centerx, rect.centery + 2)) # Slight offset maybe
        surface.blit(q_surf, q_rect)

    # Rivets, meow! [10]
    rivet_size = max(2, rect.width // 10)
    rivet_offset = rivet_size // 2 + 1
    # Draw border and fill for rivets, looks better
    pygame.draw.circle(surface, BLACK, rect.topleft + pygame.Vector2(rivet_offset, rivet_offset), rivet_size // 2 + 1) # Outer black
    pygame.draw.circle(surface, BLOCK_Q_RIVET, rect.topleft + pygame.Vector2(rivet_offset, rivet_offset), rivet_size // 2) # Inner gray
    pygame.draw.circle(surface, BLACK, rect.topright + pygame.Vector2(-rivet_offset, rivet_offset), rivet_size // 2 + 1)
    pygame.draw.circle(surface, BLOCK_Q_RIVET, rect.topright + pygame.Vector2(-rivet_offset, rivet_offset), rivet_size // 2)
    pygame.draw.circle(surface, BLACK, rect.bottomleft + pygame.Vector2(rivet_offset, -rivet_offset), rivet_size // 2 + 1)
    pygame.draw.circle(surface, BLOCK_Q_RIVET, rect.bottomleft + pygame.Vector2(rivet_offset, -rivet_offset), rivet_size // 2)
    pygame.draw.circle(surface, BLACK, rect.bottomright + pygame.Vector2(-rivet_offset, -rivet_offset), rivet_size // 2 + 1)
    pygame.draw.circle(surface, BLOCK_Q_RIVET, rect.bottomright + pygame.Vector2(-rivet_offset, -rivet_offset), rivet_size // 2)


def draw_solid_block(surface, rect):
    # Use gradient for a bit more depth
    draw_gradient_rect(surface, BLOCK_SOLID_COLOR_LIGHT, BLOCK_SOLID_COLOR_DARK, rect)
    # Inner shadow/bevel
    pygame.draw.rect(surface, BLOCK_SOLID_SHADOW, rect.inflate(-3, -3), border_radius=3) # Rounded bevel, ooh la la!
    # Outer border
    pygame.draw.rect(surface, BLACK, rect, 1, border_radius=3) # Rounded border too! Consistent as fuck!

def draw_pipe_top_left(surface, rect):
    # Base pipe color
    pygame.draw.rect(surface, PIPE_COLOR, rect, border_top_left_radius=5, border_top_right_radius=5) # Rounded top corners
    lip_height = rect.height // 4
    body_rect = pygame.Rect(rect.left, rect.top + lip_height, rect.width, rect.height - lip_height)

    # Top Lip (Thicker and more defined)
    lip_rect = pygame.Rect(rect.left, rect.top, rect.width, lip_height)
    pygame.draw.rect(surface, PIPE_SHADOW, lip_rect, border_top_left_radius=5, border_top_right_radius=5)
    pygame.draw.rect(surface, PIPE_HIGHLIGHT, lip_rect.inflate(-4, -4), border_top_left_radius=3, border_top_right_radius=3)
    pygame.draw.line(surface, PIPE_DARK_LINE, lip_rect.bottomleft, lip_rect.bottomright, 2) # Dark line under lip

    # Body Shading (Curved look with gradient maybe? Fuck it, simple rects are fine for now)
    pygame.draw.rect(surface, PIPE_SHADOW, (body_rect.left, body_rect.top, body_rect.width // 3, body_rect.height))
    pygame.draw.rect(surface, PIPE_HIGHLIGHT, (body_rect.left + body_rect.width // 2, body_rect.top, body_rect.width // 2 - 2, body_rect.height))

def draw_pipe_top_right(surface, rect):
     # Base pipe color
    pygame.draw.rect(surface, PIPE_COLOR, rect, border_top_left_radius=5, border_top_right_radius=5)
    lip_height = rect.height // 4
    body_rect = pygame.Rect(rect.left, rect.top + lip_height, rect.width, rect.height - lip_height)

    # Top Lip (Thicker)
    lip_rect = pygame.Rect(rect.left, rect.top, rect.width, lip_height)
    pygame.draw.rect(surface, PIPE_SHADOW, lip_rect, border_top_left_radius=5, border_top_right_radius=5)
    pygame.draw.rect(surface, PIPE_HIGHLIGHT, lip_rect.inflate(-4, -4), border_top_left_radius=3, border_top_right_radius=3)
    pygame.draw.line(surface, PIPE_DARK_LINE, lip_rect.bottomleft, lip_rect.bottomright, 2) # Dark line under lip

    # Body Shading (Curved look - reversed)
    pygame.draw.rect(surface, PIPE_HIGHLIGHT, (body_rect.left + 2, body_rect.top, body_rect.width // 2 -2, body_rect.height))
    pygame.draw.rect(surface, PIPE_SHADOW, (body_rect.left + body_rect.width * 2 // 3, body_rect.top, body_rect.width // 3, body_rect.height))

def draw_pipe_left(surface, rect):
    pygame.draw.rect(surface, PIPE_COLOR, rect)
    # Body shading (Curved look)
    pygame.draw.rect(surface, PIPE_SHADOW, (rect.left, rect.top, rect.width // 3, rect.height))
    pygame.draw.rect(surface, PIPE_HIGHLIGHT, (rect.left + rect.width // 2, rect.top, rect.width // 2 - 2, rect.height))
    pygame.draw.line(surface, PIPE_DARK_LINE, rect.topright, rect.bottomright, 2) # Dark line on right edge

def draw_pipe_right(surface, rect):
    pygame.draw.rect(surface, PIPE_COLOR, rect)
    # Body shading (Curved look - reversed)
    pygame.draw.rect(surface, PIPE_HIGHLIGHT, (rect.left + 2, rect.top, rect.width // 2 - 2, rect.height))
    pygame.draw.rect(surface, PIPE_SHADOW, (rect.left + rect.width * 2 // 3, rect.top, rect.width // 3, rect.height))
    pygame.draw.line(surface, PIPE_DARK_LINE, rect.topleft, rect.bottomleft, 2) # Dark line on left edge

def draw_coin(surface, rect):
    # Nicer fucking coin, nya! [10]
    center = rect.center
    radius = min(rect.width, rect.height) // 2 - 2
    if radius < 1: return # Too small to fucking draw, meow

    # Draw outer darker circle, then inner lighter circle
    pygame.draw.circle(surface, COIN_SHADOW, center, radius)
    pygame.draw.circle(surface, COIN_COLOR, center, radius - 1)

    # Shine effect - a small, bright ellipse [9]
    shine_radius_x = max(1, radius // 3)
    shine_radius_y = max(1, radius // 2)
    shine_rect = pygame.Rect(0, 0, shine_radius_x * 2, shine_radius_y * 2)
    shine_rect.center = center + pygame.Vector2(-radius // 3, -radius // 3)
    try:
        pygame.draw.ellipse(surface, COIN_HIGHLIGHT, shine_rect)
    except pygame.error: # If rect is fucked for ellipse
         pygame.draw.circle(surface, COIN_HIGHLIGHT, shine_rect.center, 1) # Just draw a dot lol


def draw_goomba(surface, rect):
    # Still abstract, but maybe a little fucking cuter, meow!
    if rect.width < 4 or rect.height < 4: return # Too damn small

    # Feet
    feet_height = max(1, rect.height // 4)
    feet_rect = pygame.Rect(rect.left, rect.bottom - feet_height, rect.width, feet_height)
    pygame.draw.rect(surface, GOOMBA_FEET, feet_rect, border_bottom_left_radius=3, border_bottom_right_radius=3)

    # Body (Ellipse with highlight)
    body_height = rect.height - feet_height
    body_rect = pygame.Rect(rect.left + rect.width // 8, rect.top, rect.width * 3 // 4, body_height * 4 // 5)
    if body_rect.width < 1 or body_rect.height < 1: return # Fucking impossible body rect

    try:
        pygame.draw.ellipse(surface, GOOMBA_BODY, body_rect)

        # Highlight on top
        highlight_rect = body_rect.copy()
        highlight_rect.height = max(1, highlight_rect.height // 2)
        highlight_rect.width = max(1, highlight_rect.width // 2)
        highlight_rect.centerx = body_rect.centerx
        highlight_rect.top = body_rect.top + 2
        if highlight_rect.width > 0 and highlight_rect.height > 0:
            pygame.draw.ellipse(surface, GOOMBA_HIGHLIGHT, highlight_rect)
    except pygame.error:
        print(f"Meow! Goomba body drawing error.") # Just skip if it's fucked


    # Angry Eyes >:( Nyaa! Make sure they fit!
    eye_y = body_rect.centery - body_rect.height // 6
    eye_sep = max(1, rect.width // 6)
    eye_width = max(2, rect.width // 7)
    eye_height = max(2, rect.height // 6)
    pupil_radius = max(1, eye_width // 4)


    try:
        # Left eye (slanted polygon)
        left_eye_points = [
            (body_rect.centerx - eye_sep, eye_y - eye_height // 2), # Top Inner
            (body_rect.centerx - eye_sep - eye_width, eye_y - eye_height // 3), # Top Outer
            (body_rect.centerx - eye_sep - eye_width, eye_y + eye_height // 2), # Bottom Outer
            (body_rect.centerx - eye_sep, eye_y + eye_height // 3) # Bottom Inner
        ]
        pygame.draw.polygon(surface, GOOMBA_EYES, left_eye_points)
        pygame.draw.circle(surface, GOOMBA_PUPILS, (int(body_rect.centerx - eye_sep - eye_width/2), int(eye_y)), pupil_radius)

        # Right eye (slanted polygon)
        right_eye_points = [
            (body_rect.centerx + eye_sep, eye_y - eye_height // 2), # Top Inner
            (body_rect.centerx + eye_sep + eye_width, eye_y - eye_height // 3), # Top Outer
            (body_rect.centerx + eye_sep + eye_width, eye_y + eye_height // 2), # Bottom Outer
            (body_rect.centerx + eye_sep, eye_y + eye_height // 3) # Bottom Inner
        ]
        pygame.draw.polygon(surface, GOOMBA_EYES, right_eye_points)
        pygame.draw.circle(surface, GOOMBA_PUPILS, (int(body_rect.centerx + eye_sep + eye_width/2), int(eye_y)), pupil_radius)
    except (ValueError, pygame.error) as e: # Catch bad polygon points or draw errors
         print(f"Warning: Couldn't draw Goomba eyes, meow! {e}")


def draw_player_start(surface, rect):
    # A slightly nicer marker
    pygame.draw.rect(surface, PLAYER_START_COLOR, rect, border_radius=3)
    pygame.draw.rect(surface, WHITE, rect.inflate(-4,-4), 1, border_radius=3) # Inner border
    # Draw a simple 'P', nya! [10]
    p_font_size = int(rect.height * 0.7)
    p_surf = None
    try:
        # Try a bold font
        p_font = pygame.font.SysFont('Arial Black', p_font_size, bold=True)
        p_surf = p_font.render("P", True, PLAYER_START_SYMBOL)
    except Exception: # Fallback if font fails
        try:
            p_font = pygame.font.SysFont(None, p_font_size + 3, bold=True)
            p_surf = p_font.render("P", True, PLAYER_START_SYMBOL)
        except Exception as e2:
             print(f"FUCK! Player Start font failed completely: {e2}")

    if p_surf:
        p_rect = p_surf.get_rect(center=rect.center)
        surface.blit(p_surf, p_rect)

def draw_eraser(surface, rect):
    pygame.draw.rect(surface, ERASER_COLOR, rect, border_radius=5)
    # Draw a thicker red 'X', meow!
    line_width = max(3, rect.width // 8)
    # Add padding so the X doesn't touch the fucking edges
    padding = line_width // 2 + 1
    try:
        pygame.draw.line(surface, ERASER_X, rect.topleft + pygame.Vector2(padding, padding), rect.bottomright + pygame.Vector2(-padding, -padding), line_width)
        pygame.draw.line(surface, ERASER_X, rect.topright + pygame.Vector2(-padding, padding), rect.bottomleft + pygame.Vector2(padding, -padding), line_width)
    except pygame.error:
        print("Mrow! Eraser rect too small to draw X.") # Shit happens

# Map tile NAME to drawing function (No changes here, fuckface)
TILE_DRAWERS = {
    "Ground": draw_ground,
    "Brick": draw_brick,
    "? Block": draw_q_block,
    "Solid Block": draw_solid_block,
    "Pipe Top Left": draw_pipe_top_left,
    "Pipe Top Right": draw_pipe_top_right,
    "Pipe Left": draw_pipe_left,
    "Pipe Right": draw_pipe_right,
    "Coin": draw_coin,
    "Goomba": draw_goomba,
    "Player Start": draw_player_start,
    "Eraser": draw_eraser,
}

# --- Palette Elements (Our graphical toys!) ---
# Stores tile name, drawing function, and rectangle for clicking
palette_items = []
item_x = 10
item_y = PALETTE_Y + 10
item_padding = 10
palette_grid_size = GRID_SIZE + 10 # Slightly larger space for palette items
max_palette_width = SCREEN_WIDTH - 20 # Allow some padding

# Regenerate palette surfaces ONCE for performance maybe? Nah, fuck it for now. [3, 5]
for name, drawer in TILE_DRAWERS.items():
    rect = pygame.Rect(item_x, item_y, GRID_SIZE, GRID_SIZE)
    palette_items.append({"name": name, "drawer": drawer, "rect": rect})
    item_x += palette_grid_size + item_padding
    if item_x + palette_grid_size > max_palette_width: # Wrap palette items, nya!
        item_x = 10
        item_y += palette_grid_size + item_padding # Move to next row

selected_tile_name = "Ground" # Start with ground, teehee!

# --- Camera/Scroll Offset (For exploring our big world!) ---
camera_offset_x = 0
camera_offset_y = 0 # We won't scroll vertically for now, like classic Mario!
camera_speed = 15 # Faster scroll, nya!

# --- Helper Function: World to Screen Coords ---
def world_to_screen(grid_x, grid_y):
    screen_x = grid_x * GRID_SIZE - camera_offset_x
    screen_y = grid_y * GRID_SIZE # - camera_offset_y # Vertical scroll disabled for now
    return int(screen_x), int(screen_y) # Return ints, nya!

# --- Helper Function: Screen to World Coords ---
def screen_to_world(screen_x, screen_y):
    # Ensure division by zero doesn't happen if GRID_SIZE is fucked somehow
    if GRID_SIZE == 0: return 0, 0
    grid_x = (screen_x + camera_offset_x) // GRID_SIZE
    grid_y = screen_y // GRID_SIZE # Adjust for camera later!
    # Clamp to world boundaries, nya!
    grid_x = max(0, min(grid_x, WORLD_WIDTH_TILES - 1))
    grid_y = max(0, min(grid_y, WORLD_HEIGHT_TILES - 1))
    return grid_x, grid_y

# --- Save/Load Functions, meow! (Using HQRIPPER 7.1 logic!) ---
def save_level(filename="level_gfx_improved.json"): # Changed default name again, fucker
    try:
        # HQRIPPER 7.1 ACTIVATED! Saving this awesome shit... purrrr...
        save_data = {
            "level": {f"{x},{y}": name for (x, y), name in level_data.items()},
            "camera_x": camera_offset_x,
            "world_w": WORLD_WIDTH_TILES, # Save world size too, maybe?
            "world_h": WORLD_HEIGHT_TILES
        }
        # Ensure filename is somewhat safe, replace weird chars maybe? Fuck it.
        safe_filename = "".join(c for c in filename if c.isalnum() or c in ('_', '.', '-')) # Basic sanitization? Nah too much work.
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=4)
        print(f"Level saved purrfectly to {filename}, nyaa!")
    except Exception as e:
        print(f"Oh FUCKING noes! Couldn't save level: {e}, meow!") # More profanity on error!

def load_level(filename="level_gfx_improved.json"):
    global level_data, camera_offset_x, WORLD_WIDTH_TILES, WORLD_HEIGHT_TILES # Allow modifying world size on load
    if not os.path.exists(filename):
        print(f"Mrow! File not found: {filename}. Starting fresh, you dumbass!")
        level_data = {}
        camera_offset_x = 0
        # Keep default world size if file not found
        return

    try:
        # HQRIPPER 7.1 ACTIVATED! Ripping data back... meow!
        with open(filename, 'r') as f:
            load_data = json.load(f)

        level_data.clear() # Clear current level first, nya!
        raw_level = load_data.get("level", {})
        loaded_count = 0
        skipped_count = 0
        corrupted_count = 0
        for key, name in raw_level.items():
            try:
                x_str, y_str = key.split(',')
                coord = (int(x_str), int(y_str))
                # Check if the tile name is still valid (exists in our drawers), nya!
                if name in TILE_DRAWERS:
                     level_data[coord] = name
                     loaded_count += 1
                else:
                    print(f"Warning: Unknown tile name '{name}' at {coord} in save file. Skipping this piece of shit, meow.")
                    skipped_count += 1
            except (ValueError, TypeError): # Catch more potential fuckups in key format
                print(f"Warning: Invalid coordinate format '{key}' in save file. Fucking skipping, meow.")
                corrupted_count += 1

        camera_offset_x = load_data.get("camera_x", 0)
        # Load world size if it exists in the file
        WORLD_WIDTH_TILES = load_data.get("world_w", WORLD_WIDTH_TILES)
        WORLD_HEIGHT_TILES = load_data.get("world_h", WORLD_HEIGHT_TILES)

        print(f"Level loaded from {filename}! Loaded {loaded_count} tiles, skipped {skipped_count} unknown shits, {corrupted_count} corrupted coord motherfuckers. World size: {WORLD_WIDTH_TILES}x{WORLD_HEIGHT_TILES}. Let's fucking edit, nya!")

    except json.JSONDecodeError as e:
        print(f"GOD FUCKING DAMMIT! File '{filename}' is corrupted JSON: {e}")
        level_data = {} # Reset to empty state on error
        camera_offset_x = 0
    except Exception as e:
        print(f"Meow-ouch! Couldn't load level for some other bullshit reason: {e}")
        level_data = {} # Reset to empty state on error
        camera_offset_x = 0


# --- Meow Game Loop! ---
running = True
mouse_dragging = False # Are we holding the mouse button? Nyaa~
right_mouse_dragging = False # For erasing, purr!

# --- Performance Optimization Idea: Tile Cache ---
# Pre-render tiles to surfaces? Could speed up drawing if many static tiles. [3, 5]
# Let's NOT implement this right now, keep it simple, fucker.
# Could be done by creating a dictionary: tile_name -> Surface
# Then just blit the cached surface instead of calling the draw function every frame.
# Would need to regenerate cache if GRID_SIZE changes. This is some advanced shit.

# Load default level on start if it exists
load_level()

while running:
    # --- Handle Input (What is the mouse/keyboard doing? purr) ---
    keys = pygame.key.get_pressed() # Get state of all keys, nya!

    # Camera Scrolling Input
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        camera_offset_x -= camera_speed
        camera_offset_x = max(0, camera_offset_x) # Prevent scrolling too far left, dumbass
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        camera_offset_x += camera_speed
        # Prevent scrolling too far right
        max_camera_x = max(0, (WORLD_WIDTH_TILES * GRID_SIZE) - SCREEN_WIDTH) # Ensure max is not negative, holy fuck
        camera_offset_x = min(max_camera_x, camera_offset_x)

    # --- Event Processing ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard shortcuts for save/load, nya!
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL: # Ctrl+S to save
                save_level()
            if event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL: # Ctrl+L to load
                load_level() # Load the potentially improved shit!

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # --- Palette Interaction ---
            palette_clicked = False
            if PALETTE_Y <= mouse_y < SCREEN_HEIGHT: # Click is in the palette area
                for item in palette_items:
                    # Use the stored rect for collision detection
                    if item["rect"].collidepoint(mouse_x, mouse_y):
                        selected_tile_name = item["name"]
                        palette_clicked = True
                        print(f"Selected {selected_tile_name}, you fucking furry!")
                        break # Found our toy!

            # --- Grid Interaction ---
            elif mouse_y < PALETTE_Y: # Click is in the grid area
                grid_x, grid_y = screen_to_world(mouse_x, mouse_y)
                coord = (grid_x, grid_y)

                # Check if coord is valid (within world bounds, although screen_to_world should clamp it)
                if 0 <= grid_x < WORLD_WIDTH_TILES and 0 <= grid_y < WORLD_HEIGHT_TILES:
                    if event.button == 1: # Left click: Place Tile / Start Drag Place
                        if selected_tile_name != "Eraser":
                            if level_data.get(coord) != selected_tile_name: # Only place if different or empty
                                 level_data[coord] = selected_tile_name # Place the fucking block!
                            mouse_dragging = True # Start dragging!
                        else: # If eraser is selected, act like right-click erase on left click too, because fuck consistency
                             if coord in level_data:
                                del level_data[coord] # Erase it, poof! You destructive bastard!
                             mouse_dragging = True # Allow drag-erase even with left click if eraser selected

                    elif event.button == 3: # Right click: Erase Tile / Start Drag Erase
                         if coord in level_data:
                             del level_data[coord] # Erase it, poof! Die tile, die!
                         right_mouse_dragging = True # Start right-drag

        if event.type == pygame.MOUSEBUTTONUP:
             if event.button == 1: # Left click released
                 mouse_dragging = False # Stop dragging, nya! Lazy fuck.
             if event.button == 3: # Right click released
                 right_mouse_dragging = False

        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            if mouse_y < PALETTE_Y: # Only interact with grid if mouse is above palette
                grid_x, grid_y = screen_to_world(mouse_x, mouse_y)
                coord = (grid_x, grid_y)

                # Check if coord is valid before trying to place/erase
                if 0 <= grid_x < WORLD_WIDTH_TILES and 0 <= grid_y < WORLD_HEIGHT_TILES:
                    current_tile_at_coord = level_data.get(coord) # Check tile *after* validating coord

                    if mouse_dragging: # Dragging with left mouse button
                        if selected_tile_name == "Eraser":
                            if current_tile_at_coord is not None: # Erase if dragging with eraser selected and tile exists
                                del level_data[coord] # More destruction! Muahaha!
                        else: # Place if dragging with a tile selected
                            # Only place if different or not already there for efficiency
                            if current_tile_at_coord != selected_tile_name:
                                level_data[coord] = selected_tile_name # Slap that shit down!

                    elif right_mouse_dragging: # Dragging with right mouse button (always erase)
                         if current_tile_at_coord is not None:
                            del level_data[coord] # Drag erase! Genocide!

    # --- Purrrocessing / Updates (Not much yet, teehee!) ---
    # Future: Update animations, check game logic if testing, etc. Fucking boring part.

    # --- Drawing Time! Let's make it pretty! Nyaa~ ---
    screen.fill(WHITE) # Clear screen with white background, like your fucking soul isn't

    # --- Draw the Grid (Relative to Camera) ---
    # Calculate visible grid range based on camera
    start_col = camera_offset_x // GRID_SIZE
    end_col = start_col + (SCREEN_WIDTH // GRID_SIZE) + 2 # Add buffer for partial tiles
    start_row = 0 # camera_offset_y // GRID_SIZE # Vertical scroll disabled
    end_row = WORLD_HEIGHT_TILES

    # Draw vertical lines
    for x_idx in range(start_col, end_col):
        screen_x, _ = world_to_screen(x_idx, 0) # Use helper for x coord
        if 0 <= screen_x <= SCREEN_WIDTH: # Only draw lines on screen, duh
             pygame.draw.line(screen, GRID_COLOR, (screen_x, 0), (screen_x, SCREEN_HEIGHT - PALETTE_HEIGHT))
    # Draw horizontal lines
    for y_idx in range(start_row, end_row + 1):
        _, screen_y = world_to_screen(0, y_idx) # Use helper for y coord
        if 0 <= screen_y <= SCREEN_HEIGHT - PALETTE_HEIGHT:
            pygame.draw.line(screen, GRID_COLOR, (0, screen_y), (SCREEN_WIDTH, screen_y))


    # --- Draw Placed Blocks (Our fucking beautiful level!) ---
    # Optimize drawing only visible blocks, nya! [1]
    visible_start_col = camera_offset_x // GRID_SIZE
    visible_end_col = visible_start_col + (SCREEN_WIDTH // GRID_SIZE) + 1
    visible_start_row = 0 # camera_offset_y // GRID_SIZE
    visible_end_row = (SCREEN_HEIGHT - PALETTE_HEIGHT) // GRID_SIZE + 1

    for (grid_x, grid_y), tile_name in level_data.items():
        # Check if the block is within the visible grid range
        if visible_start_col <= grid_x < visible_end_col and visible_start_row <= grid_y < visible_end_row:
            drawer = TILE_DRAWERS.get(tile_name) # Get the drawing function
            if drawer: # Make sure we have a function, nya! Otherwise shit breaks!
                screen_x, screen_y = world_to_screen(grid_x, grid_y)
                block_rect = pygame.Rect(screen_x, screen_y, GRID_SIZE, GRID_SIZE)
                # More precise check: only draw if rect overlaps screen [8]
                if screen.get_rect().colliderect(block_rect):
                    # Using procedural drawing means we redraw each frame. [3, 5]
                    # If performance becomes a bitch, caching drawn tiles to Surfaces is the way. [3] But fuck that for now.
                    try:
                        drawer(screen, block_rect) # Call the specific drawing function! Purrr!
                    except Exception as e:
                        print(f"HOLY FUCK! Error drawing tile {tile_name} at ({grid_x},{grid_y}): {e}")
                        # Maybe draw a fallback error tile? Nah, just crash and burn, meow.


    # --- Draw the Palette (Where the fucking toys are!) ---
    pygame.draw.rect(screen, PALETTE_BG, (PALETTE_X, PALETTE_Y, SCREEN_WIDTH, PALETTE_HEIGHT))
    for item in palette_items:
        # Draw the tile representation in the palette box! Meow!
        # Create a slightly padded inner rect for drawing to avoid border overlap
        draw_rect = item['rect'].inflate(-2, -2)
        try:
            item['drawer'](screen, draw_rect) # Draw the actual fucking tile preview
        except Exception as e:
             print(f"FUCKED UP drawing palette item {item['name']}: {e}")
             pygame.draw.rect(screen, (255,0,0), draw_rect) # Draw a red error box if it fails

        # Draw border (highlight if selected)
        border_color = HIGHLIGHT_COLOR if item["name"] == selected_tile_name else BLACK
        border_width = 3 if item["name"] == selected_tile_name else 1
        pygame.draw.rect(screen, border_color, item["rect"], border_width, border_radius=3) # Rounded corners are cute!


    # Draw selected tool text, nya!
    try:
        # Find the position after the last wrapped item
        last_item = palette_items[-1] if palette_items else None
        if last_item:
            text_x = last_item.rect.right + 20
            text_y = PALETTE_Y + 15 # Align near top of palette
            # Check if this position overlaps with any palette item rects, if so move below
            temp_text_rect = pygame.Rect(text_x, text_y, 150, 30) # Estimate size
            if any(p_item['rect'].colliderect(temp_text_rect) for p_item in palette_items) or text_x > SCREEN_WIDTH - 150 :
                 text_x = 10
                 text_y = max(p_item['rect'].bottom for p_item in palette_items) + 5 # Place below the lowest item

        else: # Default position if no palette items (shouldn't happen lol)
            text_x = 10
            text_y = PALETTE_Y + 10


        selected_text_surface = font.render(f"Selected: {selected_tile_name}", True, BLACK, PALETTE_BG) # Text with background
        text_rect = selected_text_surface.get_rect(topleft=(text_x, text_y))
        screen.blit(selected_text_surface, text_rect)
    except pygame.error as e:
        print(f"Mrow! Error rendering font for selected text: {e}") # Handle font rendering errors
    except IndexError:
        pass # No items in palette yet? What the fuck.
    except Exception as e:
        print(f"Some other bullshit error drawing selected text: {e}")

    # Draw current grid coordinates under mouse, meow!
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if mouse_y < PALETTE_Y: # Only show grid coords if mouse is in the editor area
        grid_x, grid_y = screen_to_world(mouse_x, mouse_y)
        coord_text = f"({grid_x}, {grid_y})"
        try:
            # Render with a background for visibility
            coord_text_surface = font.render(coord_text, True, BLACK, WHITE)
            coord_rect = coord_text_surface.get_rect(topleft=(mouse_x + 15, mouse_y + 10))
            # Ensure it doesn't go off screen, because that's fucking annoying
            coord_rect.right = min(coord_rect.right, SCREEN_WIDTH - 5)
            coord_rect.bottom = min(coord_rect.bottom, PALETTE_Y - 5)
            screen.blit(coord_text_surface, coord_rect)
        except pygame.error as e:
            print(f"Couldn't render coord text font, meow: {e}")
        except Exception as e:
             print(f"Couldn't draw coord text for unknown reason: {e}")


    # --- Flip the display (Show our goddamn masterpiece!) ---
    pygame.display.flip()

    # --- Keep it smooth, like a cat's fur! (FPS Control) ---
    dt = clock.tick(FPS) / 1000.0 # Get delta time in seconds, useful for physics/animations later maybe. Maybe. Probably fucking not.

# --- Bye bye! Clean up time! ---
pygame.quit()
sys.exit()
