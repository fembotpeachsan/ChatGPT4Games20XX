import pygame
import random
import numpy as np
import tempfile
import wave
import os

################################################################################
# NES-STYLE CONSTANTS & DATA
################################################################################

# Screen, grid, and color settings
WIDTH, HEIGHT = 400, 600
GRID_SIZE = 20
COLS = WIDTH // GRID_SIZE
ROWS = HEIGHT // GRID_SIZE
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY  = (128, 128, 128)

# NES Tetris uses a specific gravity speed table depending on the level.
# Values here approximate the original's frames-per-gridcell but scaled for this game loop.
NES_GRAVITY_FRAMES = [
    48, 43, 38, 33, 28, 23, 18, 13, 8, 6, 5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2,
    2, 2, 2, 2, 2, 2, 2, 1  # Up to level 28, then use 1
]

# NES Tetris scoring (standard):
# Single  =  40 * (level+1)
# Double  = 100 * (level+1)
# Triple  = 300 * (level+1)
# Tetris  = 1200 * (level+1)
SCORE_TABLE = {1: 40, 2: 100, 3: 300, 4: 1200}

# In NES Tetris, you level up every 10 lines (or start at a higher level).
LINES_PER_LEVEL = 10

################################################################################
# NES-STYLE TETROMINOS
################################################################################

# We store shapes as 4 rotation states. Each state is a matrix of 4x4 cells (0 or 1).
# This approach approximates the “classic” rotation. We do not implement modern SRS kicks.
# The data below are typical "classic" shapes in 4 rotation states each.

NES_TETROMINOS = {
    'I': [
        ["....",
         "1111",
         "....",
         "...."],

        ["..1.",
         "..1.",
         "..1.",
         "..1."],

        ["....",
         "....",
         "1111",
         "...."],

        [".1..",
         ".1..",
         ".1..",
         ".1.."]
    ],
    'O': [
        [".11.",
         ".11.",
         "....",
         "...."],

        [".11.",
         ".11.",
         "....",
         "...."],

        [".11.",
         ".11.",
         "....",
         "...."],

        [".11.",
         ".11.",
         "....",
         "...."]
    ],
    'T': [
        [".1..",
         "111.",
         "....",
         "...."],

        [".1..",
         ".11.",
         ".1..",
         "...."],

        ["....",
         "111.",
         ".1..",
         "...."],

        [".1..",
         "11..",
         ".1..",
         "...."]
    ],
    'S': [
        ["..1.",
         ".11.",
         ".1..",
         "...."],

        [".11.",
         "..11",
         "....",
         "...."],

        ["..1.",
         ".11.",
         ".1..",
         "...."],

        [".11.",
         "..11",
         "....",
         "...."]
    ],
    'Z': [
        [".1..",
         ".11.",
         "..1.",
         "...."],

        ["..11",
         ".11.",
         "....",
         "...."],

        [".1..",
         ".11.",
         "..1.",
         "...."],

        ["..11",
         ".11.",
         "....",
         "...."]
    ],
    'J': [
        ["1...",
         "111.",
         "....",
         "...."],

        [".11.",
         ".1..",
         ".1..",
         "...."],

        ["....",
         "111.",
         "...1",
         "...."],

        [".1..",
         ".1..",
         "11..",
         "...."]
    ],
    'L': [
        ["...1",
         "111.",
         "....",
         "...."],

        [".1..",
         ".1..",
         ".11.",
         "...."],

        ["....",
         "111.",
         "1...",
         "...."],

        ["11..",
         ".1..",
         ".1..",
         "...."]
    ]
}

# We’ll map each shape letter to a color to simulate NES color variety
NES_COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 0, 255),
    'L': (255, 165, 0)
}

################################################################################
# RETRO SOUND ENGINE (TEAM HUMMER-INSPIRED)
################################################################################

class RetroSoundEngine:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
        self.sounds = {}

    def generate_wave(self, frequency, duration, volume=1.0, wave_type="square", modulation=None):
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

        if wave_type == "square":
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == "sine":
            wave = np.sin(2 * np.pi * frequency * t)
        elif wave_type == "triangle":
            # Triangle wave approximation
            wave = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        elif wave_type == "sawtooth":
            # Sawtooth wave approximation
            wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        else:
            raise ValueError("Unsupported wave type. Use 'square', 'sine', 'triangle', or 'sawtooth'.")

        if modulation:
            wave *= modulation(t)

        wave = (volume * 32767 * wave).astype(np.int16)
        return wave

    def create_sound(self, name, frequency, duration, volume=1.0, wave_type="square", modulation=None):
        wave_data = self.generate_wave(frequency, duration, volume, wave_type, modulation)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file_name = temp_file.name
            with wave.open(temp_file_name, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16 bits
                wf.setframerate(44100)
                wf.writeframes(wave_data.tobytes())
            self.sounds[name] = pygame.mixer.Sound(temp_file_name)
            os.unlink(temp_file_name)

    def play_sound(self, name, loops=0):
        if name in self.sounds:
            self.sounds[name].play(loops=loops)
        else:
            print(f"Sound '{name}' not found.")

    def stop_sound(self, name):
        if name in self.sounds:
            self.sounds[name].stop()

################################################################################
# TETROMINO CLASS
################################################################################

class Tetromino:
    """
    Approximates the NES piece style: we pick a letter (I, O, T, S, Z, J, L),
    store rotation states from NES_TETROMINOS, and track current rotation index.
    """
    def __init__(self, shape_letter):
        self.shape_letter = shape_letter
        self.rotation_index = 0
        self.x = COLS // 2 - 2
        self.y = 0

    @property
    def shape_matrix(self):
        """Return the current 4x4 matrix representing the piece, from NES_TETROMINOS."""
        return NES_TETROMINOS[self.shape_letter][self.rotation_index]

    @property
    def color(self):
        return NES_COLORS[self.shape_letter]

    def rotate(self):
        # NES does simple rotation: index + 1 mod # of states
        # (All shapes have 4 states in our data, even O which is repeated.)
        old_index = self.rotation_index
        self.rotation_index = (self.rotation_index + 1) % 4
        return old_index  # for potential undo if invalid

################################################################################
# BOARD CLASS
################################################################################

class Board:
    def __init__(self):
        # The board is stored as a 2D array of colors. BLACK = empty cell.
        self.grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]

    def is_valid_position(self, tetromino: Tetromino):
        """
        Check if the tetromino's current x, y, and rotation state
        are valid (no collisions and within bounds).
        """
        mat = tetromino.shape_matrix
        for row_idx in range(4):
            for col_idx in range(4):
                if mat[row_idx][col_idx] == '1':
                    x = tetromino.x + col_idx
                    y = tetromino.y + row_idx
                    # If out of horizontal bounds or below bottom, invalid
                    if x < 0 or x >= COLS or y >= ROWS:
                        return False
                    # If above top row (y < 0) that's okay for NES Tetris—just keep going
                    if y >= 0:
                        # Check collision
                        if self.grid[y][x] != BLACK:
                            return False
        return True

    def lock_tetromino(self, tetromino: Tetromino):
        """
        Write the tetromino's blocks into the board.
        """
        mat = tetromino.shape_matrix
        for row_idx in range(4):
            for col_idx in range(4):
                if mat[row_idx][col_idx] == '1':
                    x = tetromino.x + col_idx
                    y = tetromino.y + row_idx
                    if y >= 0:  # Only write to board if it's on-screen
                        self.grid[y][x] = tetromino.color

    def clear_lines(self):
        """
        Remove fully filled lines, return the count of cleared lines.
        """
        lines_cleared = 0
        # Check from top to bottom in case multiple lines
        for row_idx in range(ROWS):
            if all(self.grid[row_idx][col] != BLACK for col in range(COLS)):
                # Remove this row
                del self.grid[row_idx]
                # Insert a blank row at the top
                self.grid.insert(0, [BLACK for _ in range(COLS)])
                lines_cleared += 1
        return lines_cleared

    def draw(self, screen):
        """
        Draw the board with its placed blocks.
        """
        for r in range(ROWS):
            for c in range(COLS):
                pygame.draw.rect(screen, GRAY,
                                 (c * GRID_SIZE, r * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)
                if self.grid[r][c] != BLACK:
                    pygame.draw.rect(screen, self.grid[r][c],
                                     (c * GRID_SIZE, r * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def draw_tetromino(self, screen, tetromino: Tetromino):
        """
        Overlays the active tetromino on top of the board.
        """
        mat = tetromino.shape_matrix
        for row_idx in range(4):
            for col_idx in range(4):
                if mat[row_idx][col_idx] == '1':
                    x = (tetromino.x + col_idx) * GRID_SIZE
                    y = (tetromino.y + row_idx) * GRID_SIZE
                    if (0 <= x < WIDTH) and (0 <= y < HEIGHT):
                        pygame.draw.rect(screen, tetromino.color, (x, y, GRID_SIZE, GRID_SIZE))

################################################################################
# NES-STYLE SCORING & LEVEL
################################################################################

def nes_calculate_score(lines_cleared, level):
    """
    Return the points gained for the given number of lines cleared
    at the provided level (level starts at 0 in code but is conceptually 1-based).
    """
    if lines_cleared in SCORE_TABLE:
        return SCORE_TABLE[lines_cleared] * (level + 1)
    return 0

def get_gravity_frames_for_level(level):
    """
    Return how many frames pass before a piece falls by 1 cell.
    If level > len(NES_GRAVITY_FRAMES)-1, clamp to the last entry.
    """
    index = min(level, len(NES_GRAVITY_FRAMES) - 1)
    return NES_GRAVITY_FRAMES[index]

################################################################################
# INPUT HANDLING
################################################################################

def handle_input(tetromino: Tetromino, board: Board, sound_engine: RetroSoundEngine):
    """
    NES Tetris style: left/right move, up to rotate, down to speed up fall,
    space for instant drop (not strictly NES, but convenient).
    """
    keys = pygame.key.get_pressed()

    # Left
    if keys[pygame.K_LEFT]:
        old_x = tetromino.x
        tetromino.x -= 1
        if not board.is_valid_position(tetromino):
            tetromino.x = old_x
        else:
            sound_engine.play_sound("move")

    # Right
    if keys[pygame.K_RIGHT]:
        old_x = tetromino.x
        tetromino.x += 1
        if not board.is_valid_position(tetromino):
            tetromino.x = old_x
        else:
            sound_engine.play_sound("move")

    # Down - soft drop (faster falling)
    if keys[pygame.K_DOWN]:
        old_y = tetromino.y
        tetromino.y += 1
        if not board.is_valid_position(tetromino):
            tetromino.y = old_y

    # Up = rotate
    if keys[pygame.K_UP]:
        old_rotation = tetromino.rotate()
        if not board.is_valid_position(tetromino):
            tetromino.rotation_index = old_rotation  # revert
        else:
            sound_engine.play_sound("rotate")

    # Space = Hard drop (not strictly NES, but often used for convenience)
    if keys[pygame.K_SPACE]:
        while board.is_valid_position(tetromino):
            tetromino.y += 1
        tetromino.y -= 1
        return True  # means we locked the piece

    return False

################################################################################
# MAIN GAME LOOP
################################################################################

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("NES-Style Tetris")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 24, bold=True)

    board = Board()
    # List of possible shape letters
    shape_letters = list(NES_TETROMINOS.keys())

    current_piece = Tetromino(random.choice(shape_letters))
    next_piece    = Tetromino(random.choice(shape_letters))

    # Sound engine
    sound_engine = RetroSoundEngine()
    # Create some sounds
    sound_engine.create_sound("line_clear", 880, 0.2, wave_type="square")
    sound_engine.create_sound("move",       440, 0.1, wave_type="sawtooth")
    sound_engine.create_sound("rotate",     660, 0.1, wave_type="triangle")
    # "Game over" with a quick pitch modulation
    sound_engine.create_sound("game_over",  220, 0.5, wave_type="sine",
                              modulation=lambda t: np.sin(2 * np.pi * 5 * t))

    score = 0
    level = 0
    total_lines_cleared = 0

    # Gravity timing
    fall_counter = 0          # counts frames
    frames_per_drop = get_gravity_frames_for_level(level)

    running = True
    while running:
        screen.fill(BLACK)
        dt = clock.tick(FPS)  # milliseconds since last frame
        fall_counter += 1

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Input (moving/rotating piece)
        locked = handle_input(current_piece, board, sound_engine)
        if locked:
            # Lock piece
            board.lock_tetromino(current_piece)
            # Clear lines
            lines_cleared = board.clear_lines()
            if lines_cleared > 0:
                score_add = nes_calculate_score(lines_cleared, level)
                score += score_add
                total_lines_cleared += lines_cleared
                sound_engine.play_sound("line_clear")

                # Increase level after every 10 lines
                if total_lines_cleared // LINES_PER_LEVEL > level:
                    level = total_lines_cleared // LINES_PER_LEVEL
                    frames_per_drop = get_gravity_frames_for_level(level)

            # Spawn next
            current_piece = next_piece
            next_piece = Tetromino(random.choice(shape_letters))

            # Check if new piece is invalid from the start => game over
            if not board.is_valid_position(current_piece):
                sound_engine.play_sound("game_over")
                pygame.time.wait(2000)
                running = False

        # Gravity-based fall
        if fall_counter >= frames_per_drop:
            fall_counter = 0
            old_y = current_piece.y
            current_piece.y += 1
            # If invalid, revert and lock
            if not board.is_valid_position(current_piece):
                current_piece.y = old_y
                board.lock_tetromino(current_piece)
                # Clear lines
                lines_cleared = board.clear_lines()
                if lines_cleared > 0:
                    score_add = nes_calculate_score(lines_cleared, level)
                    score += score_add
                    total_lines_cleared += lines_cleared
                    sound_engine.play_sound("line_clear")

                    if total_lines_cleared // LINES_PER_LEVEL > level:
                        level = total_lines_cleared // LINES_PER_LEVEL
                        frames_per_drop = get_gravity_frames_for_level(level)

                # Spawn next
                current_piece = next_piece
                next_piece = Tetromino(random.choice(shape_letters))

                # Check game over condition
                if not board.is_valid_position(current_piece):
                    sound_engine.play_sound("game_over")
                    pygame.time.wait(2000)
                    running = False

        # Draw board & piece
        board.draw(screen)
        board.draw_tetromino(screen, current_piece)

        # Next piece preview (draw in top-right corner)
        preview_x = (COLS - 6) * GRID_SIZE
        preview_y = 1 * GRID_SIZE
        next_shape = next_piece.shape_matrix
        for r in range(4):
            for c in range(4):
                if next_shape[r][c] == '1':
                    pygame.draw.rect(
                        screen, next_piece.color,
                        (preview_x + c * GRID_SIZE, preview_y + r * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                    )

        # Display score & level
        score_surf = font.render(f"Score: {score}", True, WHITE)
        level_surf = font.render(f"Level: {level}", True, WHITE)
        lines_surf = font.render(f"Lines: {total_lines_cleared}", True, WHITE)
        screen.blit(score_surf, (10, 10))
        screen.blit(level_surf, (10, 40))
        screen.blit(lines_surf, (10, 70))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
