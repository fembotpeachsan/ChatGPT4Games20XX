import pygame
import numpy as np
import threading
import time
import random

# Initialize Pygame
pygame.init()

# Setup pygame mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Screen dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 24  # Size of each block in pixels

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [
    (0, 255, 255),  # Cyan
    (0, 0, 255),    # Blue
    (255, 165, 0),  # Orange
    (255, 255, 0),  # Yellow
    (0, 255, 0),    # Green
    (128, 0, 128),  # Purple
    (255, 0, 0)     # Red
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]]   # J
]

# Define all necessary notes with their frequencies
NOTES = {
    'E5': 659.25,
    'B4': 493.88,
    'C5': 523.25,
    'D5': 587.33,
    'A4': 440.00,
    'A3': 220.00,
    'E4': 329.63,
    'F5': 698.46,
    'G5': 783.99,
    'A5': 880.00
}

def generate_square_wave(frequency, duration=0.1, volume=0.3):
    sample_rate = 44100
    num_samples = int(duration * sample_rate)
    amplitude = int(volume * 32767)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    wave = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
    stereo_wave = np.column_stack((wave, wave)).astype(np.int16)
    return pygame.sndarray.make_sound(stereo_wave)

SOUNDS = {note: generate_square_wave(freq) for note, freq in NOTES.items()}

def play_tetris_theme():
    melody = [
        ('E5', 0.25), ('B4', 0.125), ('C5', 0.125), ('D5', 0.25), ('C5', 0.125),
        ('B4', 0.125), ('A4', 0.25), ('A4', 0.125), ('C5', 0.125), ('E5', 0.25),
        ('D5', 0.125), ('C5', 0.125), ('B4', 0.375), ('C5', 0.125), ('D5', 0.25),
        ('E5', 0.25), ('C5', 0.25), ('A4', 0.25), ('A4', 0.25), ('B4', 0.125),
        ('C5', 0.125), ('D5', 0.375), ('F5', 0.125), ('A5', 0.25), ('G5', 0.125),
        ('F5', 0.125), ('E5', 0.375)
    ]
    channel = pygame.mixer.Channel(0)
    while True:
        for note, duration in melody:
            if note not in SOUNDS:
                continue
            sound = SOUNDS[note]
            channel.play(sound)
            time.sleep(duration)

theme_thread = threading.Thread(target=play_tetris_theme, daemon=True)
theme_thread.start()

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.current_x = GRID_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.current_y = 0
        self.score = 0

    def new_piece(self):
        return random.choice(SHAPES)

    def rotate_piece(self):
        self.current_piece = [list(row) for row in zip(*self.current_piece[::-1])]

    def move_piece(self, dx, dy):
        self.current_x += dx
        self.current_y += dy
        if self.check_collision():
            self.current_x -= dx
            self.current_y -= dy
            return False
        return True

    def check_collision(self):
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.current_x + x
                    new_y = self.current_y + y
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return True
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return True
        return False

    def lock_piece(self):
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_y + y][self.current_x + x] = 1
        self.clear_lines()
        self.current_piece = self.new_piece()
        self.current_x = GRID_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.current_y = 0
        if self.check_collision():
            self.__init__()  # Reset the game on collision

    def clear_lines(self):
        self.grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        while len(self.grid) < GRID_HEIGHT:
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        self.score += 1

    def draw(self, surface):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        surface, COLORS[cell - 1],
                        pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        surface, COLORS[1],
                        pygame.Rect(
                            (self.current_x + x) * BLOCK_SIZE,
                            (self.current_y + y) * BLOCK_SIZE,
                            BLOCK_SIZE, BLOCK_SIZE
                        )
                    )

tetris = Tetris()
screen = pygame.display.set_mode((GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
clock = pygame.time.Clock()
running = True
drop_time = 0

while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                tetris.move_piece(-1, 0)
            if event.key == pygame.K_RIGHT:
                tetris.move_piece(1, 0)
            if event.key == pygame.K_DOWN:
                tetris.move_piece(0, 1)
            if event.key == pygame.K_UP:
                tetris.rotate_piece()

    drop_time += clock.get_rawtime()
    clock.tick(30)
    if drop_time > 500:  # Move piece down every 500ms
        if not tetris.move_piece(0, 1):
            tetris.lock_piece()
        drop_time = 0

    tetris.draw(screen)
    pygame.display.flip()

pygame.quit()
