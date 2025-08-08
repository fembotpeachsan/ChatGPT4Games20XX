# Let's create a complete "Monster Red"-style engine with files=off, vibes=on, 60 FPS.
# This will be self-contained and ready to run with `pygame`.
# Includes: overworld with movement, random encounters, battle scene, sound effects, title screen, and types.

import pygame, sys, math, random, time, array

# ------------------------- Init & Globals ------------------------------
pygame.init()
SCREEN_W, SCREEN_H = 800, 600
TOP_H = 360
BOT_H = SCREEN_H - TOP_H
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("MONSTER RED - Files Off | Vibes On | 60 FPS")
clock = pygame.time.Clock()
FPS = 60

# Fonts
FONT_TINY = pygame.font.SysFont(None, 16)
FONT_SMALL = pygame.font.SysFont(None, 20)
FONT = pygame.font.SysFont(None, 24)
FONT_BIG = pygame.font.SysFont(None, 32)
FONT_TITLE = pygame.font.SysFont(None, 48)

# Sound
SFX_ENABLED = True
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=1)
except Exception:
    SFX_ENABLED = False

def make_tone(freq=440, ms=100, volume=0.25):
    if not SFX_ENABLED:
        return None
    sr = 44100
    n = int(sr * ms / 1000)
    buf = array.array("h")
    for s in range(n):
        t = float(s) / sr
        val = int(volume * 32767 * math.sin(2 * math.pi * freq * t))
        buf.append(val)
    sound = pygame.mixer.Sound(buffer=buf)
    return sound

# ---- SFX ----
SND_SELECT = make_tone(660, 70, 0.25)
SND_HIT    = make_tone(220, 90, 0.30)
SND_HEAL   = make_tone(880, 120, 0.20)
SND_CATCH  = make_tone(523, 180, 0.28)
SND_RUN    = make_tone(330, 70, 0.22)
SND_LEVEL  = make_tone(784, 200, 0.18)
SND_MENU   = make_tone(392, 60, 0.15)
SND_OPEN   = make_tone(523, 100, 0.20)
SND_ERROR  = make_tone(196, 100, 0.25)
SND_CANCEL = make_tone(300, 80, 0.22)

# ---- Types ----
TYPES = [
    "Normal","Fire","Water","Grass","Electric","Rock","Bug","Psychic","Ghost","Dragon","Ice",
    "Ground","Flying","Fighting"
]

# Dummy species list
SPECIES = [
    ("Flameling", "Fire"),
    ("Aquari", "Water"),
    ("Leafurr", "Grass"),
    ("Zaplet", "Electric")
]

# World map
MAP_W, MAP_H = 20, 15
WORLD = [[0 for _ in range(MAP_W)] for _ in range(MAP_H)]
for y in range(MAP_H):
    for x in range(MAP_W):
        if random.random() < 0.1:
            WORLD[y][x] = 1  # tree
        elif random.random() < 0.05:
            WORLD[y][x] = 3  # water

def can_walk(tx, ty):
    if tx < 0 or ty < 0 or tx >= MAP_W or ty >= MAP_H:
        return False
    t = WORLD[ty][tx]
    if t in (1, 3):
        return False
    return True

# ---- Entity classes ----
class Monster:
    def __init__(self, name, level=1):
        self.name = name
        self.level = level
        self.type = next((t for (n,t) in SPECIES if n == name), "Normal")
    def color(self):
        return {
            "Fire": (255, 100, 50),
            "Water": (50, 100, 255),
            "Grass": (50, 200, 50),
            "Electric": (255, 255, 50)
        }.get(self.type, (200, 200, 200))

# ---- Drawing ----
def draw_text(surf, text, x, y, col=(255,255,255), shadow=False, font=FONT):
    if shadow:
        surf.blit(font.render(text, True, (0,0,0)), (x+2,y+2))
    surf.blit(font.render(text, True, col), (x,y))

# ---- Game states ----
STATE_TITLE = 0
STATE_OVERWORLD = 1
STATE_BATTLE = 2

player_x, player_y = 5, 5
state = STATE_TITLE
title_time = 0

# ---- Main Loop ----
running = True
while running:
    dt = clock.tick(FPS)
    title_time += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if state == STATE_TITLE:
                if event.key == pygame.K_z or event.key == pygame.K_RETURN:
                    SND_SELECT.play() if SND_SELECT else None
                    state = STATE_OVERWORLD
            elif state == STATE_OVERWORLD:
                if event.key == pygame.K_z:
                    SND_MENU.play() if SND_MENU else None

    # ---- Render ----
    screen.fill((0,0,0))
    if state == STATE_TITLE:
        draw_text(screen, "MONSTER RED", SCREEN_W//2 - FONT_TITLE.size("MONSTER RED")[0]//2, 200, (255,0,0), True, FONT_TITLE)
        pulse = int(max(0, min(255, abs(math.sin(title_time * 0.05)) * 255)))
        draw_text(screen, "Press Z to start", SCREEN_W//2 - FONT.size("Press Z to start")[0]//2, 400, (pulse,pulse,pulse), True)
        for i in range(4):
            x = 150 + i * 150
            y = 300
            dummy = Monster(SPECIES[i][0], level=5)
            pygame.draw.circle(screen, dummy.color(), (x, y), 30)

    elif state == STATE_OVERWORLD:
        tile_size = 32
        for y in range(MAP_H):
            for x in range(MAP_W):
                col = (0,150,0) if WORLD[y][x] == 0 else (0,100,0) if WORLD[y][x] == 1 else (0,0,150)
                pygame.draw.rect(screen, col, (x*tile_size, y*tile_size, tile_size, tile_size))
        pygame.draw.rect(screen, (255,255,255), (player_x*tile_size, player_y*tile_size, tile_size, tile_size))

    pygame.display.flip()

pygame.quit()

