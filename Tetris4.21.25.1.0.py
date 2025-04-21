import pygame
import random
import sys

# test.py - Tetris game in Pygame at 60 FPS, pure Python blocks, no PNGs

# Initialize Pygame
pygame.init()

# Window settings
CELL_SIZE = 20
COLS = 10
ROWS = 20
SIDE_PANEL = 400
WIDTH = CELL_SIZE * COLS + SIDE_PANEL  # 600
HEIGHT = CELL_SIZE * ROWS               # 400
FPS = 60

# Colors
GRID_COLOR = (128, 128, 128)
BG_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()

# Define shapes
SHAPES = [
    [[1, 1, 0],
     [0, 1, 1],
     [0, 0, 0]],  # S
    [[0, 1, 1],
     [1, 1, 0],
     [0, 0, 0]],  # Z
    [[1, 1, 1, 1],
     [0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0]],  # I
    [[1, 1],
     [1, 1]],  # O
    [[1, 0, 0],
     [1, 1, 1],
     [0, 0, 0]],  # J
    [[0, 0, 1],
     [1, 1, 1],
     [0, 0, 0]],  # L
    [[0, 1, 0],
     [1, 1, 1],
     [0, 0, 0]]   # T
]

SHAPE_COLORS = [
    (0, 255, 0),    # S - Green
    (255, 0, 0),    # Z - Red
    (0, 255, 255),  # I - Cyan
    (255, 255, 0),  # O - Yellow
    (0, 0, 255),    # J - Blue
    (255, 165, 0),  # L - Orange
    (128, 0, 128)   # T - Purple
]

def rotate(shape):
    """Rotate shape clockwise."""
    return [list(row) for row in zip(*shape[::-1])]

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0
        self.states = self._get_states()

    def _get_states(self):
        states = [self.shape]
        for _ in range(3):
            states.append(rotate(states[-1]))
        return states

    def get_cells(self):
        state = self.states[self.rotation % len(self.states)]
        return [(self.x + j, self.y + i)
                for i, row in enumerate(state)
                for j, val in enumerate(row) if val]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.states)

def create_grid(locked):
    grid = [[BG_COLOR for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked.items():
        if 0 <= y < ROWS:
            grid[y][x] = color
    return grid

def valid_move(piece, locked):
    accepted = [(x, y) for y in range(ROWS) for x in range(COLS) if locked.get((x, y), BG_COLOR) == BG_COLOR]
    for x, y in piece.get_cells():
        if x < 0 or x >= COLS or y >= ROWS or (y >= 0 and (x, y) not in accepted):
            return False
    return True

def clear_rows(grid, locked):
    full_rows = [y for y in range(ROWS) if all(grid[y][x] != BG_COLOR for x in range(COLS))]
    if not full_rows:
        return 0
    for y in full_rows:
        for x in range(COLS):
            locked.pop((x, y), None)
    # Move above rows down
    new_locked = {}
    for (x, y), color in locked.items():
        shift = sum(1 for row in full_rows if row < y)
        new_locked[(x, y + shift)] = color
    locked.clear()
    locked.update(new_locked)
    return len(full_rows)

def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(surface, grid[y][x],
                             (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)
    for i in range(ROWS+1):
        pygame.draw.line(surface, GRID_COLOR,
                         (0, i*CELL_SIZE), (COLS*CELL_SIZE, i*CELL_SIZE))
    for j in range(COLS+1):
        pygame.draw.line(surface, GRID_COLOR,
                         (j*CELL_SIZE, 0), (j*CELL_SIZE, ROWS*CELL_SIZE))

def draw_side_panel(surface, score, level, next_piece):
    font = pygame.font.SysFont('comicsans', 30)
    # Score
    score_lbl = font.render(f'Score: {score}', True, TEXT_COLOR)
    surface.blit(score_lbl, (COLS*CELL_SIZE + 20, 20))
    # Level
    level_lbl = font.render(f'Level: {level}', True, TEXT_COLOR)
    surface.blit(level_lbl, (COLS*CELL_SIZE + 20, 60))
    # Next piece
    next_lbl = font.render('Next:', True, TEXT_COLOR)
    surface.blit(next_lbl, (COLS*CELL_SIZE + 20, 100))
    sx = COLS*CELL_SIZE + 20
    sy = 140
    for x, y in next_piece.get_cells():
        pygame.draw.rect(surface, next_piece.color,
                         (sx + (x - next_piece.x)*CELL_SIZE,
                          sy + (y - next_piece.y)*CELL_SIZE,
                          CELL_SIZE, CELL_SIZE), 0)

def main():
    locked = {}
    current = Piece(3, 0, random.choice(SHAPES))
    next_p = Piece(3, 0, random.choice(SHAPES))
    fall_time = 0
    fall_speed = 0.5
    level_time = 0
    score = 0
    level = 1

    run = True
    while run:
        dt = clock.tick(FPS) / 1000
        fall_time += dt
        level_time += dt

        # Increase level every 60 seconds
        if level_time >= 60:
            level_time = 0
            level += 1
            fall_speed = max(0.1, fall_speed - 0.05)

        # Handle piece fall
        if fall_time >= fall_speed:
            fall_time = 0
            current.y += 1
            if not valid_move(current, locked):
                current.y -= 1
                for cell in current.get_cells():
                    locked[cell] = current.color
                cleared = clear_rows(create_grid(locked), locked)
                if cleared:
                    score += cleared * 10
                current = next_p
                next_p = Piece(3, 0, random.choice(SHAPES))
                if not valid_move(current, locked):
                    run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current.x -= 1
                    if not valid_move(current, locked):
                        current.x += 1
                elif event.key == pygame.K_RIGHT:
                    current.x += 1
                    if not valid_move(current, locked):
                        current.x -= 1
                elif event.key == pygame.K_DOWN:
                    current.y += 1
                    if not valid_move(current, locked):
                        current.y -= 1
                elif event.key == pygame.K_UP:
                    current.rotate()
                    if not valid_move(current, locked):
                        current.rotate()
                elif event.key == pygame.K_SPACE:
                    while valid_move(current, locked):
                        current.y += 1
                    current.y -= 1

        grid = create_grid(locked)
        for cell in current.get_cells():
            x, y = cell
            if y >= 0:
                grid[y][x] = current.color

        screen.fill(BG_COLOR)
        draw_grid(screen, grid)
        draw_side_panel(screen, score, level, next_p)
        pygame.display.update()

    # Game Over Screen
    font = pygame.font.SysFont('comicsans', 60)
    lbl = font.render('GAME OVER', True, TEXT_COLOR)
    screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2,
                      HEIGHT//2 - lbl.get_height()
                      //2))
    pygame.display.update()
    pygame.time.delay(2000)
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
