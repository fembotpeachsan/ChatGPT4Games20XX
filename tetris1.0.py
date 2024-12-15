import random
import pygame
from pygame.locals import *
import math
import numpy as np

# M1 Mac optimizations
pygame.mixer.pre_init(44100, -16, 2, 512)  # Set up the mixer for stereo sound
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
PINK = (255, 20, 147)

# Screen dimensions
SIZE = 30
WIDTH = 10
HEIGHT = 20
SCREEN_WIDTH = WIDTH * SIZE
SCREEN_HEIGHT = HEIGHT * SIZE + 100
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris M1 Port')

# Shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[0, 1, 1], [1, 1, 0]]   # S
]
SHAPES_COLORS = [CYAN, YELLOW, PURPLE, BLUE, ORANGE, GREEN, RED]

# Font setup
pygame.font.init()
FONT = pygame.font.SysFont('Courier', 24, bold=True)

# Generate beep sounds
def generate_beep(frequency=440, duration=0.1, volume=0.5):
    sample_rate = 44100
    n_samples = int(round(duration * sample_rate))
    buf = np.sin(2 * np.pi * np.arange(n_samples) * frequency / sample_rate).astype(np.float32)
    stereo_buf = np.array([buf, buf]).T
    stereo_buf = np.ascontiguousarray(stereo_buf)
    sound = pygame.sndarray.make_sound((stereo_buf * 32767).astype(np.int16))
    sound.set_volume(volume)
    return sound

fall_sound = generate_beep(880, 0.05, 0.3)
clear_sound = generate_beep(440, 0.2, 0.5)
move_sound = generate_beep(660, 0.05, 0.3)
rotate_sound = generate_beep(550, 0.1, 0.4)

def new_piece():
    shape = random.choice(SHAPES)
    color = random.choice(SHAPES_COLORS)
    return {
        'shape': shape,
        'color': color,
        'rotation': 0,
        'x': WIDTH // 2 - len(shape[0]) // 2,
        'y': 0
    }

def check_collision(board, piece):
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                new_x = piece['x'] + x
                new_y = piece['y'] + y
                if new_y >= HEIGHT or new_x < 0 or new_x >= WIDTH or board[new_y][new_x]:
                    return True
    return False

def join_piece(board, piece):
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                board[piece['y'] + y][piece['x'] + x] = piece['color']
    fall_sound.play()

def clear_rows(board):
    lines_cleared = 0
    y = HEIGHT - 1
    while y >= 0:
        if all(board[y]):
            del board[y]
            board.insert(0, [0 for _ in range(WIDTH)])
            lines_cleared += 1
            clear_sound.play()
        else:
            y -= 1
    return lines_cleared

def rotate_piece(piece):
    rotated = list(zip(*piece['shape'][::-1]))
    return [list(row) for row in rotated]

def draw_piece(piece):
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, piece['color'],
                                 ((piece['x'] + x) * SIZE,
                                  (piece['y'] + y) * SIZE,
                                  SIZE, SIZE), 0)
                glow_color = tuple(min(255, c + 100) for c in piece['color'])
                glow_surface = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, glow_color + (50,), (0, 0, SIZE, SIZE))
                screen.blit(glow_surface, ((piece['x'] + x) * SIZE, (piece['y'] + y) * SIZE))

def draw_board(board):
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, cell, (x * SIZE, y * SIZE, SIZE, SIZE), 0)
                glow_color = tuple(min(255, c + 100) for c in cell)
                glow_surface = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, glow_color + (50,), (0, 0, SIZE, SIZE))
                screen.blit(glow_surface, (x * SIZE, y * SIZE))

def draw_ui(score, level):
    score_text = FONT.render(f"Score: {score}", True, WHITE)
    level_text = FONT.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, SCREEN_HEIGHT - 90))
    screen.blit(level_text, (10, SCREEN_HEIGHT - 60))

def draw_background(offset):
    for y in range(0, SCREEN_HEIGHT, SIZE):
        for x in range(0, SCREEN_WIDTH, SIZE):
            rect = pygame.Rect(x, y, SIZE, SIZE)
            color = (offset + x + y) % 255
            pygame.draw.rect(screen, (color, color, color), rect)

def main():
    board = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
    piece = new_piece()
    next_piece = new_piece()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    score = 0
    level = 1
    offset = 0

    running = True
    while running:
        fall_time += clock.get_rawtime()
        offset += 1
        clock.tick()
        
        if fall_time / 1000 > fall_speed:
            fall_time = 0
            piece['y'] += 1
            if check_collision(board, piece):
                piece['y'] -= 1
                join_piece(board, piece)
                lines = clear_rows(board)
                if lines > 0:
                    score += lines * 100
                    level = score // 1000 + 1
                    fall_speed = max(0.1, 0.5 - (level - 1) * 0.05)
                piece = next_piece
                next_piece = new_piece()
                if check_collision(board, piece):
                    running = False  # Game Over
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    piece['x'] -= 1
                    if check_collision(board, piece):
                        piece['x'] += 1
                    else:
                        move_sound.play()
                elif event.key == K_RIGHT:
                    piece['x'] += 1
                    if check_collision(board, piece):
                        piece['x'] -= 1
                    else:
                        move_sound.play()
                elif event.key == K_DOWN:
                    piece['y'] += 1
                    if check_collision(board, piece):
                        piece['y'] -= 1
                    else:
                        move_sound.play()
                elif event.key == K_UP:
                    rotated_shape = rotate_piece(piece)
                    original_shape = piece['shape']
                    piece['shape'] = rotated_shape
                    if check_collision(board, piece):
                        piece['shape'] = original_shape
                    else:
                        rotate_sound.play()
        
        screen.fill(BLACK)
        draw_background(offset)
        draw_board(board)
        draw_piece(piece)
        draw_ui(score, level)
        pygame.display.update()

    screen.fill(BLACK)
    game_over_text = FONT.render("GAME OVER", True, RED)
    final_score_text = FONT.render(f"Final Score: {score}", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    pygame.display.update()
    pygame.time.delay(3000)

if __name__ == "__main__":
    main()
    pygame.quit()
