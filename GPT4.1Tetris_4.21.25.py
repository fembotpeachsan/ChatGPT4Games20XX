import pygame
import random
import numpy as np
import math

# Constants
BLOCK_SIZE = 30  # Size of each block in pixels
COLS = 10       # Number of columns in the game board
ROWS = 20       # Number of rows in the game board
WIDTH = COLS * BLOCK_SIZE   # Window width
HEIGHT = ROWS * BLOCK_SIZE  # Window height

# Tetrimino shapes, each with four rotations, defined as (x, y) coordinates within a 4x4 grid
shapes = [
    # I Tetrimino
    [
        [(0,1), (1,1), (2,1), (3,1)],  # Horizontal
        [(2,0), (2,1), (2,2), (2,3)],  # Vertical
        [(0,2), (1,2), (2,2), (3,2)],  # Horizontal
        [(1,0), (1,1), (1,2), (1,3)]   # Vertical
    ],
    # O Tetrimino
    [
        [(1,0), (2,0), (1,1), (2,1)],  # Square (all rotations are the same)
        [(1,0), (2,0), (1,1), (2,1)],
        [(1,0), (2,0), (1,1), (2,1)],
        [(1,0), (2,0), (1,1), (2,1)]
    ],
    # T Tetrimino
    [
        [(1,0), (0,1), (1,1), (2,1)],  # Pointing down
        [(1,0), (1,1), (2,1), (1,2)],  # Pointing left
        [(0,1), (1,1), (2,1), (1,2)],  # Pointing up
        [(1,0), (0,1), (1,1), (1,2)]   # Pointing right
    ],
    # S Tetrimino
    [
        [(1,0), (2,0), (0,1), (1,1)],  # Horizontal
        [(1,0), (1,1), (2,1), (2,2)],  # Vertical
        [(1,1), (2,1), (0,2), (1,2)],  # Horizontal
        [(0,0), (0,1), (1,1), (1,2)]   # Vertical
    ],
    # Z Tetrimino
    [
        [(0,0), (1,0), (1,1), (2,1)],  # Horizontal
        [(2,0), (1,1), (2,1), (1,2)],  # Vertical
        [(0,1), (1,1), (1,2), (2,2)],  # Horizontal
        [(1,0), (0,1), (1,1), (0,2)]   # Vertical
    ],
    # J Tetrimino
    [
        [(0,0), (0,1), (1,1), (2,1)],  # Pointing down
        [(1,0), (2,0), (1,1), (1,2)],  # Pointing left
        [(0,1), (1,1), (2,1), (2,2)],  # Pointing up
        [(1,0), (1,1), (0,2), (1,2)]   # Pointing right
    ],
    # L Tetrimino
    [
        [(2,0), (0,1), (1,1), (2,1)],  # Pointing down
        [(1,0), (1,1), (1,2), (2,2)],  # Pointing left
        [(0,1), (1,1), (2,1), (0,2)],  # Pointing up
        [(0,0), (1,0), (1,1), (1,2)]   # Pointing right
    ]
]

# Colors for each Tetrimino type (RGB values)
colors = [ 
    (0, 255, 255),  # Cyan
    (255, 165, 0),  # Orange
    (0, 0, 255),    # Blue
    (0, 255, 0),    # Green
    (255, 0, 0),    # Red
    (128, 0, 128),  # Purple
    (255, 255, 0)   # Yellow
]

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512) # Initialize mixer
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

# --- Sound Generation ---
def generate_beep(freq, duration_ms, volume=0.1):
    """Generates a simple beep sound."""
    sample_rate = pygame.mixer.get_init()[0]
    n_samples = int(sample_rate * duration_ms / 1000.0)
    buf = np.zeros((n_samples, 2), dtype=np.int16)
    max_sample = 2**(pygame.mixer.get_init()[1] * 8 - 1) - 1

    for i in range(n_samples):
        t = float(i) / sample_rate
        sine_val = math.sin(2.0 * math.pi * freq * t)
        sample = int(max_sample * volume * sine_val)
        buf[i][0] = sample  # Left channel
        buf[i][1] = sample  # Right channel

    sound = pygame.sndarray.make_sound(buf)
    return sound

# Create sound effects
move_sound = generate_beep(880, 50)      # Higher pitch for move/rotate
rotate_sound = generate_beep(980, 50)     # Slightly higher for rotate
land_sound = generate_beep(440, 80)      # Lower pitch for landing
clear_line_sound = generate_beep(1200, 200) # Higher pitch for clearing line
game_over_sound = generate_beep(220, 500)  # Low pitch for game over
# --- End Sound Generation ---

# Game variables
board = [[0 for _ in range(COLS)] for _ in range(ROWS)]  # Game board: 0 is empty, 1-7 indicate Tetrimino type
current_shape = random.randint(0, 6)  # Index of current Tetrimino (0 to 6)
current_rotation = 0  # Current rotation index (0 to 3)
current_col = 3      # Starting column (top-left of 4x4 grid)
current_row = 0      # Starting row (top-left of 4x4 grid)
fall_speed = 0.5     # Time between automatic falls in seconds
fall_time = 0        # Accumulated time for falling
game_over = False    # Game state

# Function to check if the current Tetrimino collides at a given position and rotation
def collides(col, row, rotation):
    for dx, dy in shapes[current_shape][rotation]:
        r = row + dy
        c = col + dx
        # Check if out of bounds or overlapping with a placed block
        if r >= ROWS or c < 0 or c >= COLS or (0 <= r < ROWS and 0 <= c < COLS and board[r][c] != 0):
            return True
    return False

# Main game loop
while not game_over:
    dt = clock.tick(60) / 1000  # Delta time in seconds, targeting 60 FPS
    fall_time += dt
    
    # Move Tetrimino down periodically
    if fall_time >= fall_speed:
        if not collides(current_col, current_row + 1, current_rotation):
            current_row += 1
        else:
            # Place the Tetrimino on the board
            for dx, dy in shapes[current_shape][current_rotation]:
                board[current_row + dy][current_col + dx] = current_shape + 1  # 1-7 for shapes
            land_sound.play() # Play landing sound
            
            # Check for completed rows
            full_rows = [row for row in range(ROWS) if all(board[row][col] != 0 for col in range(COLS))]
            num_full = len(full_rows)
            if num_full > 0:
                clear_line_sound.play() # Play line clear sound
                # Remove full rows and add new empty rows at the top
                new_board = [[0]*COLS for _ in range(num_full)] + [board[row] for row in range(ROWS) if row not in full_rows]
                board = new_board + [[0]*COLS] * (ROWS - len(new_board))  # Ensure board remains 20 rows
            
            # Spawn a new Tetrimino
            current_shape = random.randint(0, 6)
            current_rotation = 0
            current_col = 3
            current_row = 0
            if collides(current_col, current_row, current_rotation):
                game_over = True  # Game over if new Tetrimino cannot spawn
                game_over_sound.play() # Play game over sound
        fall_time = 0

    # Handle user input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if not collides(current_col - 1, current_row, current_rotation):
                    current_col -= 1
                    move_sound.play()
            elif event.key == pygame.K_RIGHT:
                if not collides(current_col + 1, current_row, current_rotation):
                    current_col += 1
                    move_sound.play()
            elif event.key == pygame.K_DOWN:
                if not collides(current_col, current_row + 1, current_rotation):
                    current_row += 1
                    move_sound.play()
                fall_time = 0 # Reset fall timer on manual down
            elif event.key == pygame.K_UP:
                new_rotation = (current_rotation + 1) % 4
                if not collides(current_col, current_row, new_rotation):
                    current_rotation = new_rotation
                    rotate_sound.play()

    # Draw the game
    screen.fill((0, 0, 0))  # Clear screen with black
    
    # Draw the board (placed Tetriminos)
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] != 0:
                # Use the possibly reordered colors; ensure index is valid
                color_index = (board[row][col] - 1) % len(colors) 
                color = colors[color_index] 
                pygame.draw.rect(screen, color, (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    
    # Draw the current falling Tetrimino
    for dx, dy in shapes[current_shape][current_rotation]:
        col = current_col + dx
        row = current_row + dy
        if 0 <= row < ROWS and 0 <= col < COLS:
             # Use the possibly reordered colors; ensure index is valid
            color_index = current_shape % len(colors)
            color = colors[color_index]
            pygame.draw.rect(screen, color, (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    
    pygame.display.flip()  # Update the display

# Cleanup
pygame.mixer.quit() # Quit mixer first
pygame.quit()

