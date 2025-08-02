import pygame as pg, random, sys, numpy as np

# --- Config ---
GRID, TILE = 20, 24
W, H = GRID * TILE, GRID * TILE
FPS = 10

pg.init()
pg.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
screen = pg.display.set_mode((W, H))
pg.display.set_caption("🐍 SNAKE 2600 – BEEP+BOOP mode")
clock = pg.time.Clock()

snake = [(10, 10)]
direction = (1, 0)
next_dir = direction
food = (random.randint(0, GRID - 1), random.randint(0, GRID - 1))

BG_COLOR   = (0, 0, 0)
SNAKE_BODY = (128, 255, 128)
SNAKE_HEAD = (255, 255, 255)
FOOD_COLOR = (255, 80, 80)
GRID_LINE  = (24, 24, 24)

def draw_tile(pos, color):
    pg.draw.rect(screen, color, (pos[0]*TILE, pos[1]*TILE, TILE-1, TILE-1))

def draw_grid():
    for x in range(0, W, TILE): pg.draw.line(screen, GRID_LINE, (x, 0), (x, H))
    for y in range(0, H, TILE): pg.draw.line(screen, GRID_LINE, (0, y), (W, y))

def beep(freq=440, ms=120, vol=0.4):
    rate, _, chans = pg.mixer.get_init()
    n = int(rate * ms / 1000)
    t = np.linspace(0, ms / 1000, n, False)
    wave = np.sin(2 * np.pi * freq * t) * vol
    buf = np.int16(wave * 32767)
    if chans == 2: buf = np.column_stack([buf, buf])
    pg.sndarray.make_sound(buf).play()

def reset_game():
    global snake, direction, next_dir, food
    snake = [(10, 10)]
    direction = (1, 0)
    next_dir = direction
    food = (random.randint(0, GRID - 1), random.randint(0, GRID - 1))
    beep(120, 300)

# --- Main Loop ---
while True:
    for e in pg.event.get():
        if e.type == pg.QUIT: sys.exit()
        elif e.type == pg.KEYDOWN:
            if e.key == pg.K_UP    and direction != (0, 1): next_dir = (0, -1)
            if e.key == pg.K_DOWN  and direction != (0, -1): next_dir = (0, 1)
            if e.key == pg.K_LEFT  and direction != (1, 0): next_dir = (-1, 0)
            if e.key == pg.K_RIGHT and direction != (-1, 0): next_dir = (1, 0)

    direction = next_dir
    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    if head in snake or not (0 <= head[0] < GRID and 0 <= head[1] < GRID):
        reset_game()
        continue

    snake.insert(0, head)
    if head == food:
        beep(880, 80)
        while True:
            food = (random.randint(0, GRID - 1), random.randint(0, GRID - 1))
            if food not in snake:
                break
    else:
        snake.pop()

    screen.fill(BG_COLOR)
    draw_grid()
    for i, s in enumerate(snake):
        draw_tile(s, SNAKE_HEAD if i == 0 else SNAKE_BODY)
    draw_tile(food, FOOD_COLOR)
    pg.display.flip()
    clock.tick(FPS)
