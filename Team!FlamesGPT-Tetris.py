import pygame
import random
import numpy as np
import tempfile
import wave
import os

# Constants
WIDTH = 400
HEIGHT = 600
GRID_SIZE = 20
COLS = WIDTH // GRID_SIZE
ROWS = HEIGHT // GRID_SIZE
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Define Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]]   # J
]

COLORS = [
    (0, 255, 255),  # Cyan (I)
    (255, 255, 0),  # Yellow (O)
    (128, 0, 128),  # Purple (T)
    (255, 0, 0),    # Red (Z)
    (0, 255, 0),    # Green (S)
    (255, 165, 0),  # Orange (L)
    (0, 0, 255)     # Blue (J)
]

# NES Bootleg Sound Engine
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
            wave = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        elif wave_type == "sawtooth":
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

    def fade_out_sound(self, name, time):
        if name in self.sounds:
            self.sounds[name].fadeout(time)

# Tetromino class
class Tetromino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.rotation = 0
        self.color = random.choice(COLORS)

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape)

# Board class
class Board:
    def __init__(self, width, height, grid_size):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]

    def is_valid_position(self, tetromino):
        for y, row in enumerate(tetromino.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = tetromino.x + x
                    new_y = tetromino.y + y
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS or (new_y >= 0 and self.grid[new_y][new_x] != BLACK):
                        return False
        return True

    def add_tetromino(self, tetromino):
        for y, row in enumerate(tetromino.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[tetromino.y + y][tetromino.x + x] = tetromino.color

    def clear_lines(self):
        lines_cleared = 0
        for y in range(ROWS - 1, -1, -1):
            if all(self.grid[y][x] != BLACK for x in range(COLS)):
                del self.grid[y]
                self.grid.insert(0, [BLACK for _ in range(COLS)])
                lines_cleared += 1
        return lines_cleared

    def draw_grid(self, screen):
        for y in range(ROWS):
            for x in range(COLS):
                pygame.draw.rect(screen, GRAY, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)
                if self.grid[y][x] != BLACK:
                    pygame.draw.rect(screen, self.grid[y][x], (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def draw_tetromino(self, screen, tetromino):
        for y, row in enumerate(tetromino.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, tetromino.color,
                                     ((tetromino.x + x) * GRID_SIZE, (tetromino.y + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE))

# Handle input
def handle_input(tetromino, board, sound_manager):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        tetromino.x -= 1
        if not board.is_valid_position(tetromino):
            tetromino.x += 1
        else:
            sound_manager.play_sound("move")
    if keys[pygame.K_RIGHT]:
        tetromino.x += 1
        if not board.is_valid_position(tetromino):
            tetromino.x -= 1
        else:
            sound_manager.play_sound("move")
    if keys[pygame.K_DOWN]:
        tetromino.y += 1
        if not board.is_valid_position(tetromino):
            tetromino.y -= 1
    if keys[pygame.K_UP]:
        tetromino.rotate()
        if not board.is_valid_position(tetromino):
            tetromino.rotation -= 1
        else:
            sound_manager.play_sound("rotate")
    if keys[pygame.K_SPACE]:
        while board.is_valid_position(tetromino):
            tetromino.y += 1
        tetromino.y -= 1
        return True
    return False

# Main game loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Retro Tetris")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    board = Board(WIDTH, HEIGHT, GRID_SIZE)
    current_tetromino = Tetromino(COLS // 2 - 2, 0, random.choice(SHAPES))
    next_tetromino = Tetromino(COLS // 2 - 2, 0, random.choice(SHAPES))
    sound_manager = RetroSoundEngine()

    # Initialize sounds
    sound_manager.create_sound("line_clear", 880, 0.2, wave_type="square")
    sound_manager.create_sound("move", 440, 0.1, wave_type="sawtooth")
    sound_manager.create_sound("rotate", 660, 0.1, wave_type="triangle")
    sound_manager.create_sound("game_over", 220, 0.5, wave_type="sine", modulation=lambda t: np.sin(2 * np.pi * 5 * t))

    fall_time = 0
    fall_speed = 0.5
    score = 0

    running = True
    while running:
        screen.fill(BLACK)
        fall_time += clock.get_rawtime() / 1000
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if fall_time >= fall_speed:
            fall_time = 0
            current_tetromino.y += 1
            if not board.is_valid_position(current_tetromino):
                current_tetromino.y -= 1
                board.add_tetromino(current_tetromino)
                lines_cleared = board.clear_lines()
                if lines_cleared > 0:
                    sound_manager.play_sound("line_clear")
                    score += lines_cleared * 100
                current_tetromino = next_tetromino
                next_tetromino = Tetromino(COLS // 2 - 2, 0, random.choice(SHAPES))
                if not board.is_valid_position(current_tetromino):
                    sound_manager.play_sound("game_over")
                    pygame.time.wait(500)
                    running = False

        hard_drop = handle_input(current_tetromino, board, sound_manager)
        if hard_drop:
            board.add_tetromino(current_tetromino)
            lines_cleared = board.clear_lines()
            if lines_cleared > 0:
                sound_manager.play_sound("line_clear")
                score += lines_cleared * 100
            current_tetromino = next_tetromino
            next_tetromino = Tetromino(COLS // 2 - 2, 0, random.choice(SHAPES))
            if not board.is_valid_position(current_tetromino):
                sound_manager.play_sound("game_over")
                pygame.time.wait(500)
                running = False

        board.draw_grid(screen)
        board.draw_tetromino(screen, current_tetromino)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
