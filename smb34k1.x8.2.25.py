#!/usr/bin/env python3
# mario3_vibes.py  –  zero‑dependency, 60 FPS Mario‑3‑style micro‑engine
import os, sys, math, pygame, itertools, random, time
os.environ.setdefault("SDL_VIDEO_CENTERED", "1")           # nice centring
pygame.init()
pygame.mixer.quit()                                        # silence for now

# ───────────────────────── Configuration ────────────────────────── #
WIDTH, HEIGHT, FPS       = 800, 480, 60
TILE                      = 32
GRAVITY, JUMP_VEL        = 0.55, -12
SCROLL_EDGE_X             = WIDTH // 3                     # camera dead‑zone
# ╌╌ Palette (NES‑ish) ╌╌ #
PAL = {
    "sky":  (110, 194, 255),
    "ground": (215, 160, 71),
    "brick": (185, 122, 77),
    "player": (252, 216, 168),
    "flag": (255, 255, 255),
}
# ────────────────────────── Level Layout ────────────────────────── #
LEVEL = [
"                                                                                              ",
"                                                                                              ",
"                                                                                              ",
"                                                                                              ",
"                                                                                              ",
"                                                                                              ",
"                                                                                              ",
"                                                                                              ",
"            ###                                                                               ",
"                                                                                              ",
"                                                                                              ",
"                                                                                              ",
"##############################       ##########################################################",
]
LEVEL_WIDTH  = len(LEVEL[0]) * TILE
LEVEL_HEIGHT = len(LEVEL)   * TILE

# pre‑compute solid tiles for collision
SOLIDS = { '#'}
solids_rects = []
for j,row in enumerate(LEVEL):
    for i,ch in enumerate(row):
        if ch in SOLIDS:
            solids_rects.append(pygame.Rect(i*TILE, j*TILE, TILE, TILE))

# flag pole (simple win condition)
FLAG_X = (len(LEVEL[0])-4)*TILE
FLAG_RECT = pygame.Rect(FLAG_X, (len(LEVEL)-8)*TILE, TILE, 7*TILE)

# ─────────────────────────── Engine Bits ────────────────────────── #
class Camera:
    def __init__(self): self.x = 0
    def apply(self, rect): return rect.move(-self.x, 0)
    def update(self, target_rect):
        if target_rect.centerx - self.x > WIDTH - SCROLL_EDGE_X:
            self.x = min(target_rect.centerx - (WIDTH-SCROLL_EDGE_X), LEVEL_WIDTH - WIDTH)
        elif target_rect.centerx - self.x < SCROLL_EDGE_X:
            self.x = max(target_rect.centerx - SCROLL_EDGE_X, 0)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x,y, TILE*0.8, TILE*1.6)
        self.vel  = pygame.Vector2(0,0)
        self.on_ground = False
        self.color = PAL["player"]
    def update(self, keys):
        # horiz
        self.vel.x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 5
        # jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel.y = JUMP_VEL; self.on_ground=False
        # gravity
        self.vel.y += GRAVITY; self.vel.y = min(self.vel.y, 12)

        # X movement & collisions
        self.rect.x += self.vel.x
        for s in solids_rects:
            if self.rect.colliderect(s):
                if self.vel.x > 0: self.rect.right = s.left
                elif self.vel.x < 0: self.rect.left  = s.right

        # Y movement & collisions
        self.rect.y += int(self.vel.y)
        self.on_ground=False
        for s in solids_rects:
            if self.rect.colliderect(s):
                if self.vel.y > 0:
                    self.rect.bottom = s.top; self.vel.y=0; self.on_ground=True
                elif self.vel.y < 0:
                    self.rect.top    = s.bottom; self.vel.y=0
    def draw(self, surf, cam):
        pygame.draw.rect(surf, self.color, cam.apply(self.rect))

# ─────────────────────────── Rendering ──────────────────────────── #
def draw_level(bg, cam, vibe_cycle):
    # sky
    bg.fill(PAL["sky"])
    # ground & bricks
    for s in solids_rects:
        colour = PAL["ground"] if (s.y//TILE) >= len(LEVEL)-2 else PAL["brick"]
        col = cycle_colour(colour, vibe_cycle) if vibe_mode else colour
        pygame.draw.rect(bg, col, cam.apply(s))
    # flag
    pole_rect = cam.apply(FLAG_RECT)
    pygame.draw.rect(bg, PAL["flag"], pole_rect)
    pygame.draw.polygon(bg, (0,200,0), [(pole_rect.centerx, pole_rect.y),
                                        (pole_rect.centerx+24, pole_rect.y+12),
                                        (pole_rect.centerx, pole_rect.y+24)])

def cycle_colour(col, t):
    # simple HSV rotation
    r,g,b = col
    h = (math.atan2(math.sqrt(3)*(g-b), 2*r-g-b) + t) % (2*math.pi)
    c = math.sqrt(r*r+g*g+b*b)/math.sqrt(3)
    return [int(max(0,min(255, c*(1+math.cos(h+angle))))) for angle in (0,2*math.pi/3,4*math.pi/3)]

# ─────────────────────────── Game States ────────────────────────── #
pygame.display.set_caption("Mario‑3‑ish | Vibes ON")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock  = pygame.time.Clock()
font   = pygame.font.SysFont("sans", 48)

def title_screen():
    blink = itertools.cycle([255]*30 + [0]*30)
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: sys.exit()
            if e.type==pygame.KEYDOWN: return
        screen.fill(PAL["sky"])
        title = font.render("SUPER MARIO 3‑ish", True, PAL["brick"])
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2-40)))
        if next(blink):
            prompt = font.render("PRESS ANY KEY", True, PAL["ground"])
            screen.blit(prompt, prompt.get_rect(center=(WIDTH//2, HEIGHT//2+40)))
        pygame.display.flip(); clock.tick(FPS)

def game_loop():
    global vibe_mode
    cam     = Camera()
    player  = Player(2*TILE, (len(LEVEL)-4)*TILE)
    vibe_cycle = 0.0
    while True:
        keys=pygame.key.get_pressed()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: sys.exit()
            if e.type==pygame.KEYDOWN and e.key==pygame.K_v: vibe_mode = not vibe_mode
        player.update(keys)
        cam.update(player.rect)
        vibe_cycle += 0.03
        draw_level(screen, cam, vibe_cycle)
        player.draw(screen, cam)
        # win check
        if player.rect.colliderect(FLAG_RECT):
            win_screen(); return
        pygame.display.flip(); clock.tick(FPS)

def win_screen():
    t0=time.time()
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: sys.exit()
            if e.type==pygame.KEYDOWN: return
        dt=time.time()-t0
        screen.fill(cycle_colour(PAL["sky"], dt) if vibe_mode else PAL["sky"])
        msg = font.render("YOU WIN!", True, PAL["flag"])
        screen.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2)))
        prompt = font.render("Press Any Key", True, PAL["ground"])
        screen.blit(prompt, prompt.get_rect(center=(WIDTH//2, HEIGHT//2+60)))
        pygame.display.flip(); clock.tick(FPS)

# ───────────────────────────── Main ─────────────────────────────── #
vibe_mode = True
title_screen()
while True:
    game_loop()
