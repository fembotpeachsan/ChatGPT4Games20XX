import pygame
from pygame.locals import *
import sys

pygame.init()

# NES original resolution
NES_WIDTH, NES_HEIGHT = 256, 240
SCALE = 3
WINDOW_WIDTH, WINDOW_HEIGHT = NES_WIDTH * SCALE, NES_HEIGHT * SCALE
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Super Mario Bros. – Authentic NES Style')

# Authentic NES palette
WHITE = (252, 252, 252)
SKY_BLUE = (92, 148, 252)
GROUND_BROWN = (136, 112, 0)
RED = (200, 76, 12)
SKIN = (252, 188, 176)
BLUE = (0, 60, 236)
BROWN = (160, 88, 40)

# NES screen and tile setup
nes_surface = pygame.Surface((NES_WIDTH, NES_HEIGHT))
TILE = 8

# Mario sprite (NES accurate size 16x24 px)
mario_width, mario_height = 16, 24
ground_y = NES_HEIGHT - TILE * 2
mario = pygame.Rect(4 * TILE, ground_y - mario_height, mario_width, mario_height)

# Physics settings
mario_speed = 1
jump_speed = 5
gravity = 0.2
vertical_speed = 0
is_jumping = False

# Game tracking
current_world, current_level = 1, 1
max_world, max_level = 8, 4

# NES Mario sprite (accurate SMB1 look)
def draw_mario(surface: pygame.Surface, rect: pygame.Rect) -> None:
    x, y = rect.topleft
    pixels = [
        "    RR     ",
        "   RRRRR   ",
        "  SSBBBB   ",
        " SSSBBBBB  ",
        " SSSBBBBB  ",
        "SSSBBBBBB  ",
        "SSSBBBBBB  ",
        "  BBBBBBB  ",
        "  BBBBBBB  ",
        " BBB  BBB  ",
        "BBB   BBB  ",
        "BBB   BBB  "
    ]
    colors = {'R': RED, 'S': SKIN, 'B': BLUE, ' ': None}
    for row_idx, row in enumerate(pixels):
        for col_idx, pixel in enumerate(row):
            color = colors[pixel]
            if color:
                pygame.draw.rect(surface, color, (x + col_idx, y + row_idx, 1, 1))

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        mario.x -= mario_speed
    if keys[K_RIGHT]:
        mario.x += mario_speed

    if not is_jumping and keys[K_SPACE]:
        is_jumping = True
        vertical_speed = -jump_speed

    if is_jumping:
        mario.y += vertical_speed
        vertical_speed += gravity
        if mario.y >= ground_y - mario_height:
            mario.y = ground_y - mario_height
            is_jumping = False

    if mario.x > NES_WIDTH:
        mario.x = -mario_width
        current_level += 1
        if current_level > max_level:
            current_level = 1
            current_world += 1
            if current_world > max_world:
                current_world = 1

    nes_surface.fill(SKY_BLUE)
    pygame.draw.rect(nes_surface, GROUND_BROWN, (0, ground_y, NES_WIDTH, NES_HEIGHT - ground_y))
    draw_mario(nes_surface, mario)

    font = pygame.font.Font(pygame.font.get_default_font(), 8)
    hud_text = font.render(f'WORLD {current_world}-{current_level}', False, WHITE)
    nes_surface.blit(hud_text, (TILE, TILE))

    scaled = pygame.transform.scale(nes_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.blit(scaled, (0, 0))

    pygame.display.flip()
    clock.tick(60)
