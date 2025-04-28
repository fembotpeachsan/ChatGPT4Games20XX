# [COPYRIGHT NOVA] - DELTA-BUSTER Spell Activated: Generating source...
# Meow! This code is based on the user's request and public Tetris knowledge.

import pygame
import random
import os
import time # Added for timing

# Initialize Pygame
pygame.init()

# --- Game Constants ---
GAME_WIDTH = 10  # Grid width
GAME_HEIGHT = 20  # Grid height
BLOCK_SIZE = 16  # Size of each Tetromino block in pixels
BOARD_LEFT = 100 # Left edge of the Tetris board area
BOARD_TOP = 50 # Top edge of the Tetris board area
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400 # Increased height slightly for menu spacing
FPS = 60

# Colors (shades of gray for Game Boy feel)
WHITE = (224, 248, 208) # GB Lightest Green/Gray
LIGHT_GRAY = (136, 192, 112) # GB Light Green/Gray
MID_GRAY = (52, 104, 86) # GB Dark Green/Gray
DARK_GRAY = (8, 24, 32) # GB Darkest Green/Gray (used for text/borders)
BLACK = (8, 24, 32) # Using darkest GB shade as "black"

# Tetromino shapes (rotations) and colors
# Shapes are represented by a list of (row, col) offsets relative to a pivot
# Using standard Tetris piece representation for easier rotation logic
SHAPES = {
    'I': [[(1, 0), (1, 1), (1, 2), (1, 3)], # Centered around (1,1) roughly
          [(0, 2), (1, 2), (2, 2), (3, 2)],
          [(2, 0), (2, 1), (2, 2), (2, 3)],
          [(0, 1), (1, 1), (2, 1), (3, 1)]],
    'J': [[(0, 0), (1, 0), (1, 1), (1, 2)], # Pivot around (1,1)
          [(0, 1), (0, 2), (1, 1), (2, 1)],
          [(1, 0), (1, 1), (1, 2), (2, 2)],
          [(0, 1), (1, 1), (2, 0), (2, 1)]],
    'L': [[(0, 2), (1, 0), (1, 1), (1, 2)], # Pivot around (1,1)
          [(0, 1), (1, 1), (2, 1), (2, 2)],
          [(1, 0), (1, 1), (1, 2), (2, 0)],
          [(0, 0), (0, 1), (1, 1), (2, 1)]],
    'O': [[(0, 0), (0, 1), (1, 0), (1, 1)]], # Pivot doesn't matter much here
    'S': [[(0, 1), (0, 2), (1, 0), (1, 1)], # Pivot around (1,1)
          [(0, 1), (1, 1), (1, 2), (2, 2)],
          [(1, 1), (1, 2), (2, 0), (2, 1)], # Added 2 more rotations to match standard
          [(0, 0), (1, 0), (1, 1), (2, 1)]],
    'T': [[(0, 1), (1, 0), (1, 1), (1, 2)], # Pivot around (1,1)
          [(0, 1), (1, 1), (1, 2), (2, 1)],
          [(1, 0), (1, 1), (1, 2), (2, 1)],
          [(0, 1), (1, 0), (1, 1), (2, 1)]],
    'Z': [[(0, 0), (0, 1), (1, 1), (1, 2)], # Pivot around (1,1)
          [(0, 2), (1, 1), (1, 2), (2, 1)],
          [(1, 0), (1, 1), (2, 1), (2, 2)], # Added 2 more rotations to match standard
          [(0, 1), (1, 0), (1, 1), (2, 0)]]
}

# Colors for each shape (using GB shades indices)
# 0: Background, 1: Light, 2: Mid, 3: Dark
SHAPE_COLORS = {
    'I': 1, # Light
    'J': 2, # Mid
    'L': 3, # Dark
    'O': 1, # Light
    'S': 2, # Mid
    'T': 3, # Dark
    'Z': 1  # Light
}

# Color mapping for drawing
COLOR_MAP = {
    0: WHITE,      # Background
    1: LIGHT_GRAY, # Shape Color 1
    2: MID_GRAY,   # Shape Color 2
    3: DARK_GRAY   # Shape Color 3 (used for shapes and borders/text)
}

# Original Game Boy Tetris fall speeds (frames per gridcell)
# Source: Tetris Wiki (https://tetris.wiki/Tetris_(Game_Boy))
# Converted to seconds per row (Frames / 60 FPS) approximately
# Level: Frames -> Seconds/Row
FALL_SPEEDS_GB = {
     0: 48 / 60.0,  # ~0.800s
     1: 43 / 60.0,  # ~0.717s
     2: 38 / 60.0,  # ~0.633s
     3: 33 / 60.0,  # ~0.550s
     4: 28 / 60.0,  # ~0.467s
     5: 23 / 60.0,  # ~0.383s
     6: 18 / 60.0,  # ~0.300s
     7: 13 / 60.0,  # ~0.217s
     8: 8 / 60.0,   # ~0.133s
     9: 6 / 60.0,   # ~0.100s
    10: 5 / 60.0,  # ~0.083s (Levels 10-12)
    13: 4 / 60.0,  # ~0.067s (Levels 13-15)
    16: 3 / 60.0,  # ~0.050s (Levels 16-18)
    19: 2 / 60.0,  # ~0.033s (Level 19+)
    # Speed for levels 20+ in some versions is 1 frame/row (1/60.0)
    # We'll use the Level 19 speed for 20+ for simplicity based on common GB versions
}


# --- Game State Variables ---
grid = [[0 for _ in range(GAME_WIDTH)] for _ in range(GAME_HEIGHT)]
current_piece = None
next_piece = None
score = 0
level = 0
lines_cleared = 0
game_over = False
game_paused = False
game_type = 'A' # 'A' or 'B'
start_level = 0 # For menu selection
high_level = 0 # For B-Type menu selection
high_scores = [] # List of (score, name) tuples

# Movement/Timing Variables
fall_timer = 0.0 # Use floating point timer
current_fall_speed = FALL_SPEEDS_GB[0] # Initial fall speed

# Soft drop multiplier (how much faster it falls when holding down)
SOFT_DROP_MULTIPLIER = 5 # Fall 5 times faster

# DAS (Delayed Auto Shift) and ARR (Auto Repeat Rate) simulation
key_down_time = {'LEFT': 0, 'RIGHT': 0}
das_triggered = {'LEFT': False, 'RIGHT': False}
DAS_DELAY = 0.166 # Delay before auto-shift starts (approx 10 frames)
ARR_DELAY = 0.066 # Delay between auto-shifts (approx 4 frames)

# --- Sound effects (placeholders) ---
# Add actual sound loading later

# --- Functions ---

def create_piece(shape_name=None):
    """Creates a new Tetromino piece."""
    if shape_name is None:
        shape_name = random.choice(list(SHAPES.keys()))

    shape_patterns = SHAPES[shape_name]
    initial_rotation_index = 0 # Start with the base rotation
    pattern = shape_patterns[initial_rotation_index]
    color = SHAPE_COLORS[shape_name]

    # Calculate initial position (top center, slightly adjusted for piece width)
    min_c = min(p[1] for p in pattern)
    max_c = max(p[1] for p in pattern)
    piece_width = max_c - min_c + 1
    col = (GAME_WIDTH // 2) - (piece_width // 2) - min_c # Centering logic

    # Adjust row to ensure piece starts just above the visible grid if possible
    min_r = min(p[0] for p in pattern)
    row = -min_r # Start at the effective top

    # Initial check: If starting position is invalid, try shifting down slightly
    temp_piece = {'shape': shape_name, 'pattern': pattern, 'color': color, 'row': row, 'col': col, 'rotation': initial_rotation_index}
    while not is_valid_position(temp_piece, grid) and temp_piece['row'] < 0:
         temp_piece['row'] += 1
    row = temp_piece['row']

    return {'shape': shape_name, 'pattern': pattern, 'color': color, 'row': row, 'col': col, 'rotation': initial_rotation_index}

def is_valid_position(piece, board):
    """Checks if the piece is in a valid position on the board."""
    for r_offset, c_offset in piece['pattern']:
        r, c = piece['row'] + r_offset, piece['col'] + c_offset
        # Check boundaries
        if not (0 <= c < GAME_WIDTH): # Check horizontal bounds first
            return False
        if r >= GAME_HEIGHT: # Check bottom boundary
            return False
        # Check collision with existing blocks only if inside the grid vertically
        if r >= 0 and board[r][c] != 0:
            return False
    return True

def rotate_piece(piece, board, clockwise=True):
    """Rotates the piece and checks for validity, includes basic wall kicks."""
    shape_patterns = SHAPES[piece['shape']]
    num_rotations = len(shape_patterns)
    if num_rotations <= 1: # Cannot rotate 'O' piece
        return False

    current_rotation = piece['rotation']
    if clockwise:
        next_rotation = (current_rotation + 1) % num_rotations
    else: # Counter-clockwise (Not standard GB, but can be added)
        next_rotation = (current_rotation - 1 + num_rotations) % num_rotations

    next_pattern = shape_patterns[next_rotation]

    original_row, original_col = piece['row'], piece['col']
    test_piece = piece.copy()
    test_piece['pattern'] = next_pattern
    test_piece['rotation'] = next_rotation

    # Test potential positions (Basic Wall Kick - try moving left/right 1 unit)
    # More complex SRS kicks are not implemented here, just simple adjacent checks
    kick_offsets = [(0, 0), (0, -1), (0, 1), (0, -2), (0, 2)] # Standard kicks are more complex, this is basic
    if piece['shape'] == 'I': # 'I' piece has different kick rules usually
        kick_offsets = [(0, 0), (0, -1), (0, 1), (0, -2), (0, 2), (1, 0), (-1, 0)] # Include vertical for I

    for dr_kick, dc_kick in kick_offsets:
        test_piece['row'] = original_row + dr_kick
        test_piece['col'] = original_col + dc_kick
        if is_valid_position(test_piece, board):
            piece.update(test_piece)
            return True

    return False # Rotation failed after checking kicks

def move_piece(piece, dr, dc, board):
    """Moves the piece by dr rows and dc columns and checks for validity."""
    if piece is None: return False # Safety check
    new_piece = piece.copy()
    new_piece['row'] += dr
    new_piece['col'] += dc

    if is_valid_position(new_piece, board):
        piece.update(new_piece)
        return True
    return False # Move failed

def hard_drop(piece, board):
    """Instantly drops the piece to the lowest valid position."""
    if piece is None: return 0
    rows_dropped = 0
    while is_valid_position(piece, board):
        piece['row'] += 1
        rows_dropped += 1
    piece['row'] -= 1 # Move back up one step to the last valid position
    rows_dropped -=1
    # Score for hard drop (GB Tetris doesn't score hard drop itself, only soft drop)
    # Some modern versions add points, let's stick to GB style (no points for hard drop action)
    lock_piece(piece, board)
    return rows_dropped # Return rows dropped for potential scoring


def lock_piece(piece, board):
    """Locks the current piece into the board."""
    if piece is None: return False
    piece_locked = False
    for r_offset, c_offset in piece['pattern']:
        r, c = piece['row'] + r_offset, piece['col'] + c_offset
        # Only lock blocks within the valid grid height
        if 0 <= r < GAME_HEIGHT and 0 <= c < GAME_WIDTH:
            board[r][c] = piece['color']
            piece_locked = True
        # Check if lock happens above the visible area (Game Over condition)
        elif r < 0 and 0 <= c < GAME_WIDTH:
             global game_over, current_state
             game_over = True
             current_state = STATE_GAME_OVER
             return True # Indicate game over lock

    # Play lock sound effect here (placeholder)
    # print("Play lock sound")

    # Clear lines after locking
    lines_cleared_count = clear_lines(board)
    return piece_locked

def clear_lines(board):
    """Checks for and clears full lines, updates score and line count. Returns number of lines cleared."""
    global score, lines_cleared, level, current_fall_speed # Need to update these globals
    lines_to_clear = []
    for r in range(GAME_HEIGHT):
        if all(board[r][c] != 0 for c in range(GAME_WIDTH)):
            lines_to_clear.append(r)

    num_cleared = len(lines_to_clear)

    if num_cleared == 0:
        return 0

    # Score calculation (Classic Tetris Game Boy A-Type)
    # Points are added when lines are cleared, multiplied by level + 1
    points_per_line = {1: 40, 2: 100, 3: 300, 4: 1200} # "Tetris" for 4 lines
    if num_cleared in points_per_line:
         score += points_per_line[num_cleared] * (level + 1)
         # Play line clear sound effect here (placeholder)
         # print(f"Play clear sound for {num_cleared} lines")


    # Remove lines from bottom up to avoid index issues
    lines_cleared_indices = sorted(lines_to_clear, reverse=True)
    for r_index in lines_cleared_indices:
        board.pop(r_index)
        board.insert(0, [0 for _ in range(GAME_WIDTH)]) # Add empty line at the top

    lines_cleared += num_cleared

    # Level progression (every 10 lines in A-Type)
    # Level increases when lines_cleared crosses a multiple of 10
    # Example: Start Level 0. Clear 10 lines -> Level 1. Clear 20 lines -> Level 2.
    # Start Level 5. Clear 10 lines -> Level 6 (at total 10 lines for this game).
    # GB Logic: Level increases based on `start_level` and `lines_cleared`.
    # Transition happens when `lines_cleared >= next_level_threshold`.
    # Thresholds: Level 1 at 10, Level 2 at 20, ..., Level N at N*10
    # More accurately, transition happens when `lines // 10 >= level + 1` (assuming level 0 start)
    # Or `level = max(start_level, lines_cleared // 10)` ? No, it's cumulative.
    # Let's use the formula from Tetris Wiki: `level = start_level` initially.
    # Level transition happens when `lines_cleared >= min(start_level * 10 + 10, max(100, start_level * 10 + 10))`.
    # Simpler: Transition level = start_level + 1. Lines needed = transition_level * 10.
    # If current_lines >= transition_level * 10, increase level.

    prev_level = level
    # Calculate target lines for next level based on start level
    target_lines_for_next_level_up = (level + 1) * 10
    if start_level > level: # Handle cases starting at higher level, need fewer lines for first increase
         target_lines_for_next_level_up = (start_level + 1) * 10 - (start_level * 10) # Need 10 lines for first level up

    # This logic seems overly complex. Let's use the simpler: level increases every 10 lines CLEARED IN THIS GAME.
    next_level_threshold = (level - start_level + 1) * 10
    if lines_cleared >= next_level_threshold:
        level += 1
        # Play level up sound (placeholder)
        # print("Level Up!")

    # Update fall speed based on the NEW level
    current_fall_speed = calculate_fall_speed(level)

    return num_cleared # Return how many lines were cleared


def calculate_fall_speed(current_level):
     """Gets the fall speed in seconds per row for the current level."""
     if current_level <= 9:
         return FALL_SPEEDS_GB.get(current_level, FALL_SPEEDS_GB[9]) # Default to level 9 speed if somehow level < 0
     elif current_level <= 12:
         return FALL_SPEEDS_GB[10]
     elif current_level <= 15:
         return FALL_SPEEDS_GB[13]
     elif current_level <= 18:
         return FALL_SPEEDS_GB[16]
     else: # Level 19 and above
         return FALL_SPEEDS_GB[19]

def draw_board(surface, board):
    """Draws the game board and locked pieces."""
    # Draw background for the board area
    board_bg_rect = pygame.Rect(BOARD_LEFT, BOARD_TOP, GAME_WIDTH * BLOCK_SIZE, GAME_HEIGHT * BLOCK_SIZE)
    pygame.draw.rect(surface, WHITE, board_bg_rect)

    # Draw the grid lines (optional, GB didn't really have them)
    # for r in range(GAME_HEIGHT):
    #     pygame.draw.line(surface, LIGHT_GRAY, (BOARD_LEFT, BOARD_TOP + r * BLOCK_SIZE), (BOARD_LEFT + GAME_WIDTH * BLOCK_SIZE, BOARD_TOP + r * BLOCK_SIZE))
    # for c in range(GAME_WIDTH):
    #      pygame.draw.line(surface, LIGHT_GRAY, (BOARD_LEFT + c * BLOCK_SIZE, BOARD_TOP), (BOARD_LEFT + c * BLOCK_SIZE, BOARD_TOP + GAME_HEIGHT * BLOCK_SIZE))


    # Draw the blocks
    for r in range(GAME_HEIGHT):
        for c in range(GAME_WIDTH):
            block_color_index = board[r][c]
            if block_color_index != 0: # Don't draw empty blocks
                block_color = COLOR_MAP[block_color_index]
                block_rect = pygame.Rect(BOARD_LEFT + c * BLOCK_SIZE, BOARD_TOP + r * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(surface, block_color, block_rect)
                # Optional: Add inner shadow/highlight for 3D effect? GB was flat.
                # pygame.draw.rect(surface, BLACK, block_rect, 1) # 1 pixel border (use darkest color)

    # Draw board border
    border_thickness = 2
    border_rect = pygame.Rect(BOARD_LEFT - border_thickness,
                              BOARD_TOP - border_thickness,
                              GAME_WIDTH * BLOCK_SIZE + 2 * border_thickness,
                              GAME_HEIGHT * BLOCK_SIZE + 2 * border_thickness)
    pygame.draw.rect(surface, DARK_GRAY, border_rect, border_thickness)


def draw_piece(surface, piece):
    """Draws the current Tetromino piece."""
    if piece is None:
        return
    block_color = COLOR_MAP[piece['color']]
    for r_offset, c_offset in piece['pattern']:
        r, c = piece['row'] + r_offset, piece['col'] + c_offset
        # Only draw if the block is within the visible game area height
        if r >= 0 and 0 <= c < GAME_WIDTH:
             block_rect = pygame.Rect(BOARD_LEFT + c * BLOCK_SIZE, BOARD_TOP + r * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
             pygame.draw.rect(surface, block_color, block_rect)
             # pygame.draw.rect(surface, BLACK, block_rect, 1) # Optional border


def draw_ui(surface):
    """Draws the score, level, lines, and next piece UI."""
    # Use a simple monospaced font if available, otherwise default
    try:
        # Try loading a pixel font if you have one (e.g., PressStart2P)
        font_path = None # Or path to your font file
        font = pygame.font.Font(font_path, 16) # Small pixel font size
        font_large = pygame.font.Font(font_path, 20)
    except:
        font = pygame.font.Font(None, 24) # Fallback default font
        font_large = pygame.font.Font(None, 30)


    ui_x_base = BOARD_LEFT + GAME_WIDTH * BLOCK_SIZE + 25 # Position UI to the right
    ui_y_base = BOARD_TOP + 10

    # Score
    score_label = font.render(f"SCORE", True, BLACK)
    score_value = font_large.render(f"{score:06}", True, BLACK)
    surface.blit(score_label, (ui_x_base, ui_y_base))
    surface.blit(score_value, (ui_x_base, ui_y_base + 20))

    # Level
    level_label = font.render(f"LEVEL", True, BLACK)
    level_value = font_large.render(f"{level:02}", True, BLACK) # GB doesn't show heart icon
    surface.blit(level_label, (ui_x_base, ui_y_base + 60))
    surface.blit(level_value, (ui_x_base, ui_y_base + 80))

    # Lines
    lines_label = font.render(f"LINES", True, BLACK)
    lines_value = font_large.render(f"{lines_cleared:03}", True, BLACK)
    surface.blit(lines_label, (ui_x_base, ui_y_base + 120))
    surface.blit(lines_value, (ui_x_base, ui_y_base + 140))

    # Next Piece Box
    next_label = font.render("NEXT", True, BLACK)
    surface.blit(next_label, (ui_x_base, ui_y_base + 180))
    next_box_rect = pygame.Rect(ui_x_base, ui_y_base + 200, 4 * BLOCK_SIZE, 4 * BLOCK_SIZE)
    pygame.draw.rect(surface, WHITE, next_box_rect) # Background for next box
    pygame.draw.rect(surface, DARK_GRAY, next_box_rect, 2) # Border for next box

    if next_piece:
        next_piece_preview = next_piece.copy()
        preview_pattern = SHAPES[next_piece_preview['shape']][0] # Use base rotation for preview

        # Center the preview piece in the box
        min_r = min(p[0] for p in preview_pattern)
        max_r = max(p[0] for p in preview_pattern)
        min_c = min(p[1] for p in preview_pattern)
        max_c = max(p[1] for p in preview_pattern)
        shape_height = max_r - min_r + 1
        shape_width = max_c - min_c + 1

        # Calculate offset to center within the 4x4 block area
        col_offset = (4 - shape_width) // 2 - min_c
        row_offset = (4 - shape_height) // 2 - min_r

        block_color = COLOR_MAP[next_piece_preview['color']]
        for r_p, c_p in preview_pattern:
            draw_r = row_offset + r_p
            draw_c = col_offset + c_p
            # Draw inside the next_box_rect boundaries
            block_rect = pygame.Rect(next_box_rect.left + draw_c * BLOCK_SIZE,
                                      next_box_rect.top + draw_r * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(surface, block_color, block_rect)
            # pygame.draw.rect(surface, BLACK, block_rect, 1) # Optional border


def draw_game_over(surface):
    """Draws the Game Over screen."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 24, 32, 200)) # Semi-transparent dark overlay matching theme
    surface.blit(overlay, (0, 0))

    try:
        font_path = None # Or path to your font file
        font_large = pygame.font.Font(font_path, 36)
        font_medium = pygame.font.Font(font_path, 20)
    except:
        font_large = pygame.font.Font(None, 50)
        font_medium = pygame.font.Font(None, 30)


    game_over_text = font_large.render("GAME OVER", True, WHITE)
    # GB often had character animations here, just text for now
    try_again_text = font_medium.render("PRESS START", True, WHITE) # Or Enter key

    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
    try_again_rect = try_again_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))

    surface.blit(game_over_text, game_over_rect)
    surface.blit(try_again_text, try_again_rect)

def load_high_scores(filename="highscores.txt"):
    """Loads high scores from a file."""
    scores = []
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                for line in f:
                    try:
                        s, n = line.strip().split(",")
                        scores.append((int(s), n))
                    except ValueError:
                        continue # Skip malformed lines
        except IOError:
             print(f"Warning: Could not read high score file: {filename}") # Meow! File issues!
    # Return top 3 scores, sorted highest first
    return sorted(scores, key=lambda item: item[0], reverse=True)[:3]

def save_high_scores(scores, filename="highscores.txt"):
    """Saves high scores to a file."""
    try:
        with open(filename, "w") as f:
            for s, n in scores:
                f.write(f"{s},{n}\n")
    except IOError:
        print(f"Warning: Could not save high scores to {filename}") # Hiss! Cannot save!

def check_and_add_high_score(current_score):
    """Checks if the score is a high score and prompts for name if it is."""
    global high_scores
    player_name = "AAA" # Default name

    if len(high_scores) < 3 or current_score > high_scores[-1][0]:
        # --- Simple Text Input ---
        # This part is tricky in Pygame without a dedicated input box widget.
        # We'll do a very basic console input for now.
        # For a real game, you'd implement a Pygame text input loop here.
        print(f"\n*** New High Score: {current_score} ***")
        try:
             input_name = input("Enter your name (3 chars): ")
             player_name = input_name.strip().upper()[:3].ljust(3, 'A') # Format: 3 chars, uppercase, pad with A
        except EOFError: # Handle environments where input() might fail
             print("Could not get name input, using AAA.")
             player_name = "AAA"

        high_scores.append((current_score, player_name))
        high_scores = sorted(high_scores, key=lambda item: item[0], reverse=True)[:3]
        save_high_scores(high_scores)
        return True # Indicate new high score was added
    return False # No new high score

# --- Game Initialization ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Meowtris GB") # Cute name!
clock = pygame.time.Clock()

# Load initial game state
high_scores = load_high_scores()

def reset_game(start_lvl=0, start_high=0, game_mode='A'):
    """Resets the game state."""
    global grid, current_piece, next_piece, score, level, lines_cleared, game_over, fall_timer, current_fall_speed, game_type, high_level, start_level
    global key_down_time, das_triggered # Reset DAS state

    game_type = game_mode
    start_level = start_lvl # Store the chosen start level
    level = start_level   # Current level starts at chosen level
    high_level = start_high # Only relevant for B-Type starting lines
    score = 0
    lines_cleared = 0
    game_over = False
    fall_timer = 0.0
    current_fall_speed = calculate_fall_speed(level) # Set speed for start level

    key_down_time = {'LEFT': 0, 'RIGHT': 0}
    das_triggered = {'LEFT': False, 'RIGHT': False}

    grid = [[0 for _ in range(GAME_WIDTH)] for _ in range(GAME_HEIGHT)]

    if game_type == 'B':
        # Add initial garbage lines for B-Type
        # GB 'High' parameter: 0=5 lines, 1=8, 2=10, 3=12, 4=14, 5=16 lines of garbage
        lines_of_garbage = [5, 8, 10, 12, 14, 16]
        num_garbage_rows = lines_of_garbage[high_level] if 0 <= high_level < len(lines_of_garbage) else 0
        num_garbage_rows = min(num_garbage_rows, GAME_HEIGHT - 5) # Leave some space at top

        for r in range(GAME_HEIGHT - num_garbage_rows, GAME_HEIGHT):
            # Fill row with random blocks, ensuring at least one gap
            gap_col = random.randint(0, GAME_WIDTH - 1)
            for c in range(GAME_WIDTH):
                 if c != gap_col:
                     grid[r][c] = random.randint(1, 3) # Random gray block color index

    # Create first pieces
    current_piece = create_piece()
    next_piece = create_piece()

    # Initial check for game over immediately (e.g., B-Type starts too high)
    if current_piece and not is_valid_position(current_piece, grid):
        # Try shifting piece down if it starts invalidly obstructed
        temp_piece = current_piece.copy()
        shifted = False
        for r_start in range(1, 3): # Try shifting down 1 or 2 rows
             temp_piece['row'] = -min(p[0] for p in temp_piece['pattern']) + r_start
             if is_valid_position(temp_piece, grid):
                 current_piece['row'] = temp_piece['row']
                 shifted = True
                 break
        if not shifted:
             game_over = True
             # Don't change state here yet, let the main loop handle it


# --- Game Loop States ---
STATE_TITLE = 0
STATE_MENU = 1
STATE_PLAYING = 2
STATE_GAME_OVER = 3
STATE_HIGHSCORE_ENTRY = 4 # New state for name entry (if implemented visually)
STATE_HIGHSCORE_DISPLAY = 5

current_state = STATE_TITLE
menu_selection = 'A-TYPE' # Initial menu selection
menu_level_selection = 0
menu_high_selection = 0

# --- Menu/Title Screen Logic ---
def draw_title(surface):
     surface.fill(WHITE) # GB background color
     try:
        font_path = None # Path to font
        font_large = pygame.font.Font(font_path, 48)
        font_small = pygame.font.Font(font_path, 24)
     except:
        font_large = pygame.font.Font(None, 60)
        font_small = pygame.font.Font(None, 30)


     title_text = font_large.render("MEOWTRIS", True, BLACK) # Cute title!
     title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
     surface.blit(title_text, title_rect)

     prompt_text = font_small.render("PRESS START (ENTER)", True, BLACK)
     prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))
     surface.blit(prompt_text, prompt_rect)

     # Removed the moscow.png loading
     pygame.display.flip()

def handle_title_input(event):
     global current_state
     if event.type == pygame.KEYDOWN:
         if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER: # Use Enter as Start
            current_state = STATE_MENU
            # Play menu start sound (placeholder)
            # print("Play menu sound")

def draw_menu(surface, selected_option, current_game_type, current_level, current_high):
    surface.fill(WHITE) # GB background

    # Optional: Draw subtle background pattern like dots
    # for x in range(0, SCREEN_WIDTH, 8):
    #     for y in range(0, SCREEN_HEIGHT, 8):
    #         pygame.draw.circle(surface, LIGHT_GRAY, (x, y), 1)

    try:
        font_path = None # Path to font
        font_head = pygame.font.Font(font_path, 24)
        font_opt = pygame.font.Font(font_path, 20)
        font_num = pygame.font.Font(font_path, 18)
    except:
        font_head = pygame.font.Font(None, 30)
        font_opt = pygame.font.Font(None, 28)
        font_num = pygame.font.Font(None, 24)

    # --- Game Type selection ---
    type_y = 50
    game_type_text = font_head.render("GAME TYPE", True, BLACK)
    surface.blit(game_type_text, (SCREEN_WIDTH // 2 - game_type_text.get_width() // 2, type_y))

    a_type_text = font_opt.render("A-TYPE", True, BLACK)
    b_type_text = font_opt.render("B-TYPE", True, BLACK)
    a_rect = a_type_text.get_rect(center=(SCREEN_WIDTH // 2 - 60, type_y + 40))
    b_rect = b_type_text.get_rect(center=(SCREEN_WIDTH // 2 + 60, type_y + 40))

    # Highlight selected type
    if selected_option == 'A-TYPE':
        pygame.draw.rect(surface, MID_GRAY, a_rect.inflate(10, 5)) # Highlight box
    elif selected_option == 'B-TYPE':
        pygame.draw.rect(surface, MID_GRAY, b_rect.inflate(10, 5))

    # Draw selector triangle (like original GB)
    selector_y = type_y + 40
    if current_game_type == 'A':
        pygame.draw.polygon(surface, BLACK, [(a_rect.left - 15, selector_y - 5), (a_rect.left - 15, selector_y + 5), (a_rect.left - 8, selector_y)])
    else:
        pygame.draw.polygon(surface, BLACK, [(b_rect.left - 15, selector_y - 5), (b_rect.left - 15, selector_y + 5), (b_rect.left - 8, selector_y)])


    surface.blit(a_type_text, a_rect)
    surface.blit(b_type_text, b_rect)


    # --- Level selection (0-9) ---
    level_y = type_y + 90
    level_text = font_head.render("LEVEL", True, BLACK)
    surface.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, level_y))

    level_num_text = font_opt.render(f"{current_level:02}", True, BLACK) # Display selected level
    level_num_rect = level_num_text.get_rect(center=(SCREEN_WIDTH // 2, level_y + 40))
    surface.blit(level_num_text, level_num_rect)

    # Highlight if selected
    if selected_option == 'LEVEL':
         pygame.draw.rect(surface, MID_GRAY, level_num_rect.inflate(10, 5)) # Highlight box
         pygame.draw.polygon(surface, BLACK, [(level_num_rect.left - 15, level_y + 40 - 5), (level_num_rect.left - 15, level_y + 40 + 5), (level_num_rect.left - 8, level_y + 40)])


    # --- High selection (for B-Type, 0-5) ---
    high_y = level_y + 90
    if current_game_type == 'B':
        high_text = font_head.render("HIGH", True, BLACK)
        surface.blit(high_text, (SCREEN_WIDTH // 2 - high_text.get_width() // 2, high_y))

        high_num_text = font_opt.render(f"{current_high:01}", True, BLACK) # Display selected high
        high_num_rect = high_num_text.get_rect(center=(SCREEN_WIDTH // 2, high_y + 40))
        surface.blit(high_num_text, high_num_rect)

        # Highlight if selected
        if selected_option == 'HIGH':
             pygame.draw.rect(surface, MID_GRAY, high_num_rect.inflate(10, 5)) # Highlight box
             pygame.draw.polygon(surface, BLACK, [(high_num_rect.left - 15, high_y + 40 - 5), (high_num_rect.left - 15, high_y + 40 + 5), (high_num_rect.left - 8, high_y + 40)])

    # --- High Score Display Option ---
    score_y = high_y + (80 if current_game_type == 'B' else 0)
    score_opt_text = font_opt.render("TOP SCORES", True, BLACK)
    score_opt_rect = score_opt_text.get_rect(center=(SCREEN_WIDTH // 2, score_y + 40))

    if selected_option == 'TOP-SCORES':
         pygame.draw.rect(surface, MID_GRAY, score_opt_rect.inflate(10, 5)) # Highlight box
         pygame.draw.polygon(surface, BLACK, [(score_opt_rect.left - 15, score_y + 40 - 5), (score_opt_rect.left - 15, score_y + 40 + 5), (score_opt_rect.left - 8, score_y + 40)])

    surface.blit(score_opt_text, score_opt_rect)


    pygame.display.flip()


def handle_menu_input(event):
     global current_state, menu_selection, menu_level_selection, menu_high_selection, game_type, high_level, start_level

     if event.type == pygame.KEYDOWN:
         # Play menu navigation sound (placeholder)
         # print("Play nav sound")

         if event.key == pygame.K_DOWN:
             if menu_selection == 'A-TYPE' or menu_selection == 'B-TYPE':
                 menu_selection = 'LEVEL'
             elif menu_selection == 'LEVEL':
                 if game_type == 'B':
                     menu_selection = 'HIGH'
                 else:
                     menu_selection = 'TOP-SCORES'
             elif menu_selection == 'HIGH':
                 menu_selection = 'TOP-SCORES'
             elif menu_selection == 'TOP-SCORES':
                 menu_selection = 'A-TYPE' # Loop back to top

         elif event.key == pygame.K_UP:
             if menu_selection == 'A-TYPE' or menu_selection == 'B-TYPE':
                  menu_selection = 'TOP-SCORES' # Loop back to bottom
             elif menu_selection == 'LEVEL':
                 menu_selection = 'A-TYPE' # Assumes A-TYPE/B-TYPE are the same row conceptually
             elif menu_selection == 'HIGH':
                 menu_selection = 'LEVEL'
             elif menu_selection == 'TOP-SCORES':
                 if game_type == 'B':
                      menu_selection = 'HIGH'
                 else:
                      menu_selection = 'LEVEL'

         elif event.key == pygame.K_LEFT:
             if menu_selection == 'A-TYPE' or menu_selection == 'B-TYPE':
                 game_type = 'A' if game_type == 'B' else 'B'
                 menu_selection = game_type + '-TYPE' # Update selection text
             elif menu_selection == 'LEVEL':
                 menu_level_selection = (menu_level_selection - 1 + 10) % 10 # Decrement level 0-9
             elif menu_selection == 'HIGH':
                 menu_high_selection = (menu_high_selection - 1 + 6) % 6 # Decrement high 0-5

         elif event.key == pygame.K_RIGHT:
             if menu_selection == 'A-TYPE' or menu_selection == 'B-TYPE':
                 game_type = 'A' if game_type == 'B' else 'B'
                 menu_selection = game_type + '-TYPE' # Update selection text
             elif menu_selection == 'LEVEL':
                 menu_level_selection = (menu_level_selection + 1) % 10 # Increment level 0-9
             elif menu_selection == 'HIGH':
                 menu_high_selection = (menu_high_selection + 1) % 6 # Increment high 0-5

         elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER: # Start game or select option
             # Play selection sound (placeholder)
             # print("Play select sound")
             if menu_selection == 'A-TYPE' or menu_selection == 'B-TYPE' or menu_selection == 'LEVEL' or menu_selection == 'HIGH':
                 start_level = menu_level_selection
                 high_level = menu_high_selection
                 reset_game(start_lvl=start_level, start_high=high_level, game_mode=game_type)
                 current_state = STATE_PLAYING
                 # Play game start sound (placeholder)
                 # print("Play game start sound")
             elif menu_selection == 'TOP-SCORES':
                  current_state = STATE_HIGHSCORE_DISPLAY

     # Update state variables based on menu selections
     start_level = menu_level_selection
     high_level = menu_high_selection


def draw_high_score_display(surface):
    surface.fill(WHITE) # GB background
    try:
        font_path = None # Path to font
        font_large = pygame.font.Font(font_path, 36)
        font_medium = pygame.font.Font(font_path, 24)
        font_small = pygame.font.Font(font_path, 20)
    except:
        font_large = pygame.font.Font(None, 40)
        font_medium = pygame.font.Font(None, 30)
        font_small = pygame.font.Font(None, 25)

    title_text = font_large.render("TOP SCORES", True, BLACK)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
    surface.blit(title_text, title_rect)

    score_y_start = 120
    score_y_gap = 40
    for i, (s, n) in enumerate(high_scores):
        rank_text = font_medium.render(f"{i+1}.", True, BLACK)
        name_text = font_medium.render(f"{n}", True, BLACK)
        score_text = font_medium.render(f"{s:06}", True, BLACK) # Pad score

        rank_pos = (SCREEN_WIDTH // 2 - 100, score_y_start + i * score_y_gap)
        name_pos = (SCREEN_WIDTH // 2 - 60, score_y_start + i * score_y_gap)
        score_pos = (SCREEN_WIDTH // 2 + 40, score_y_start + i * score_y_gap)

        surface.blit(rank_text, rank_pos)
        surface.blit(name_text, name_pos)
        surface.blit(score_text, score_pos)

    # Fill remaining slots if less than 3 scores
    for i in range(len(high_scores), 3):
        rank_text = font_medium.render(f"{i+1}.", True, BLACK)
        name_text = font_medium.render("---", True, BLACK)
        score_text = font_medium.render("000000", True, BLACK)

        rank_pos = (SCREEN_WIDTH // 2 - 100, score_y_start + i * score_y_gap)
        name_pos = (SCREEN_WIDTH // 2 - 60, score_y_start + i * score_y_gap)
        score_pos = (SCREEN_WIDTH // 2 + 40, score_y_start + i * score_y_gap)

        surface.blit(rank_text, rank_pos)
        surface.blit(name_text, name_pos)
        surface.blit(score_text, score_pos)


    prompt_text = font_small.render("PRESS START (ENTER) TO RETURN", True, BLACK)
    prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
    surface.blit(prompt_text, prompt_rect)

    pygame.display.flip()

def handle_high_score_input(event):
    global current_state
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
             current_state = STATE_MENU # Go back to menu
             # Play back sound (placeholder)
             # print("Play back sound")


# --- Game Loop ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0 # Delta time in seconds
    current_time = time.time() # Get current time for DAS/ARR

    # --- Event Handling ---
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # Handle state-specific input
        if current_state == STATE_TITLE:
            handle_title_input(event)
        elif current_state == STATE_MENU:
            handle_menu_input(event)
        elif current_state == STATE_HIGHSCORE_DISPLAY:
            handle_high_score_input(event)
        elif current_state == STATE_GAME_OVER:
            # Handle input on game over screen (e.g., press key to return to menu)
            if event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                     check_and_add_high_score(score) # Check score before leaving
                     current_state = STATE_MENU
                     menu_selection = 'A-TYPE' # Reset menu selection
                     # Play confirm/back sound (placeholder)
                     # print("Play back sound")


        elif current_state == STATE_PLAYING:
            # Handle player input during gameplay (key DOWN events)
            if not game_paused and not game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if move_piece(current_piece, 0, -1, grid):
                             key_down_time['LEFT'] = current_time # Start DAS timer
                             das_triggered['LEFT'] = False
                             # Play move sound (placeholder)
                             # print("Play move sound")
                    elif event.key == pygame.K_RIGHT:
                        if move_piece(current_piece, 0, 1, grid):
                             key_down_time['RIGHT'] = current_time # Start DAS timer
                             das_triggered['RIGHT'] = False
                             # Play move sound (placeholder)
                             # print("Play move sound")
                    elif event.key == pygame.K_DOWN:
                         # Soft drop starts immediately on key press
                         fall_timer = current_fall_speed # Force next drop faster
                         score += 1 # GB scores 1 point per row of soft drop distance
                    elif event.key == pygame.K_UP or event.key == pygame.K_x: # Rotate Clockwise (X is common too)
                        if rotate_piece(current_piece, grid, clockwise=True):
                           # Play rotate sound (placeholder)
                           # print("Play rotate sound")
                           pass
                    elif event.key == pygame.K_z or event.key == pygame.K_LCTRL: # Rotate Counter-Clockwise (Z or Ctrl)
                         if rotate_piece(current_piece, grid, clockwise=False):
                             # Play rotate sound (placeholder)
                             # print("Play rotate sound")
                             pass
                    elif event.key == pygame.K_SPACE:
                         # Hard drop - Instantly drop and lock
                         if current_piece:
                             rows_dropped = hard_drop(current_piece, grid)
                             # Score for hard drop distance? GB doesn't, modern Tetris does (e.g., 2 points per row)
                             # score += rows_dropped * 2 # Optional scoring
                             current_piece = None # Signal to create new piece
                             fall_timer = current_fall_speed # Reset fall timer to avoid instant drop of next piece

                    elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE: # Pause (P or Esc)
                        game_paused = True
                        # Play pause sound (placeholder)
                        # print("Play pause sound")

                elif event.type == pygame.KEYUP:
                     if event.key == pygame.K_LEFT:
                         key_down_time['LEFT'] = 0 # Stop DAS timer
                         das_triggered['LEFT'] = False
                     elif event.key == pygame.K_RIGHT:
                         key_down_time['RIGHT'] = 0 # Stop DAS timer
                         das_triggered['RIGHT'] = False
                     # No action needed for KEYUP on other keys like DOWN, UP, SPACE etc.


            # Handle unpause
            elif event.type == pygame.KEYDOWN and (event.key == pygame.K_p or event.key == pygame.K_ESCAPE) and game_paused:
                 game_paused = False
                 # Play unpause sound (placeholder)
                 # print("Play unpause sound")


    # --- Game Logic (State-based) ---
    if current_state == STATE_PLAYING and not game_paused and not game_over:

        # --- Handle DAS/ARR ---
        keys = pygame.key.get_pressed()

        # Left Movement
        if keys[pygame.K_LEFT] and key_down_time['LEFT'] > 0:
            if not das_triggered['LEFT'] and current_time - key_down_time['LEFT'] >= DAS_DELAY:
                # DAS triggered, start ARR
                das_triggered['LEFT'] = True
                key_down_time['LEFT'] = current_time # Reset timer for ARR
                if move_piece(current_piece, 0, -1, grid):
                     # Play move sound (placeholder)
                     # print("Play move sound")
                     pass
            elif das_triggered['LEFT'] and current_time - key_down_time['LEFT'] >= ARR_DELAY:
                 # ARR repeat
                 key_down_time['LEFT'] = current_time # Reset timer for next ARR
                 if move_piece(current_piece, 0, -1, grid):
                      # Play move sound (placeholder)
                      # print("Play move sound")
                      pass
        elif not keys[pygame.K_LEFT]: # Key released
             key_down_time['LEFT'] = 0
             das_triggered['LEFT'] = False

        # Right Movement (Similar logic)
        if keys[pygame.K_RIGHT] and key_down_time['RIGHT'] > 0:
             if not das_triggered['RIGHT'] and current_time - key_down_time['RIGHT'] >= DAS_DELAY:
                 das_triggered['RIGHT'] = True
                 key_down_time['RIGHT'] = current_time
                 if move_piece(current_piece, 0, 1, grid):
                      # Play move sound (placeholder)
                      # print("Play move sound")
                      pass
             elif das_triggered['RIGHT'] and current_time - key_down_time['RIGHT'] >= ARR_DELAY:
                  key_down_time['RIGHT'] = current_time
                  if move_piece(current_piece, 0, 1, grid):
                       # Play move sound (placeholder)
                       # print("Play move sound")
                       pass
        elif not keys[pygame.K_RIGHT]:
             key_down_time['RIGHT'] = 0
             das_triggered['RIGHT'] = False


        # --- Handle Piece Falling ---
        fall_timer += dt

        # Soft Drop Check
        if keys[pygame.K_DOWN] and current_piece:
            # Apply soft drop speed multiplier if DOWN is held
            effective_fall_speed = current_fall_speed / SOFT_DROP_MULTIPLIER
            if fall_timer >= effective_fall_speed:
                 fall_timer = 0 # Reset timer after move
                 if move_piece(current_piece, 1, 0, grid):
                     score += 1 # Score 1 point per row dropped via soft drop
                 else:
                     # Landed while soft dropping
                     if lock_piece(current_piece, grid): # Lock piece, check for game over lock
                          current_piece = None # Signal next piece
                          fall_timer = current_fall_speed # Reset fall timer fully

        # Normal Gravity Check (only if not soft dropping or DOWN key is not pressed)
        elif fall_timer >= current_fall_speed and current_piece:
            fall_timer = 0 # Reset timer after move attempt

            if not move_piece(current_piece, 1, 0, grid):
                # Piece landed naturally
                 if lock_piece(current_piece, grid): # Lock piece, check for game over lock
                      current_piece = None # Signal next piece
                      fall_timer = current_fall_speed # Reset fall timer fully


        # --- Spawn New Piece ---
        if current_piece is None and not game_over:
            current_piece = next_piece
            next_piece = create_piece()

            # Check for game over on spawn (lock out)
            if not is_valid_position(current_piece, grid):
                 # Try shifting piece down if it starts invalidly obstructed
                 temp_piece = current_piece.copy()
                 shifted = False
                 for r_start in range(1, 3): # Try shifting down 1 or 2 rows
                      temp_piece['row'] = -min(p[0] for p in temp_piece['pattern']) + r_start
                      if is_valid_position(temp_piece, grid):
                          current_piece['row'] = temp_piece['row']
                          shifted = True
                          break
                 if not shifted:
                      game_over = True
                      current_state = STATE_GAME_OVER # Change state immediately
                      # Play game over sound (placeholder)
                      # print("Play game over sound")



    # --- Drawing (State-based) ---
    screen.fill(WHITE) # Background color

    if current_state == STATE_TITLE:
        draw_title(screen)
    elif current_state == STATE_MENU:
        draw_menu(screen, menu_selection, game_type, menu_level_selection, menu_high_selection)
    elif current_state == STATE_PLAYING:
        draw_board(screen, grid)
        draw_piece(screen, current_piece)
        draw_ui(screen)
        if game_paused:
             # Draw pause overlay (e.g., PAUSED text)
             overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
             overlay.fill((8, 24, 32, 180)) # Semi-transparent dark overlay
             screen.blit(overlay, (0, 0))
             try:
                 font_path = None # Path to font
                 font_pause = pygame.font.Font(font_path, 48)
             except:
                 font_pause = pygame.font.Font(None, 60)

             pause_text = font_pause.render("PAUSED", True, WHITE)
             pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
             screen.blit(pause_text, pause_rect)

    elif current_state == STATE_GAME_OVER:
        # Draw the final board state THEN the game over overlay
        draw_board(screen, grid)
        draw_ui(screen) # Show final score/lines
        draw_game_over(screen) # Draw overlay and text
    elif current_state == STATE_HIGHSCORE_DISPLAY:
         draw_high_score_display(screen)


    pygame.display.flip() # Update the full screen

pygame.quit()
# Meow! Hope you like it! Let me know if you want more changes!
