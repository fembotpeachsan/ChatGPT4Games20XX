"""
Mario Worker‑Inspired Level Editor & Platformer
Single‑file Pygame implementation — ready to run.

References
- Tile collision mechanics in Pygame platformers :contentReference[oaicite:0]{index=0}
- Authentic NES/Mario color palette values :contentReference[oaicite:1]{index=1}
- Gravity & terminal velocity research from Mario titles :contentReference[oaicite:2]{index=2}
- Grid‑snapping techniques for editors :contentReference[oaicite:3]{index=3}
- Basic level‑editor snapping/video example :contentReference[oaicite:4]{index=4}
- Enemy (Goomba‑style) movement patterns :contentReference[oaicite:5]{index=5}
- Camera that follows the player smoothly :contentReference[oaicite:6]{index=6}
- Coin‑collection collision logic :contentReference[oaicite:7]{index=7}
- Single‑file Pygame game architecture ideas :contentReference[oaicite:8]{index=8}
- Robust tile collision discussion threads :contentReference[oaicite:9]{index=9}
"""

import pygame
import math
from enum import Enum

pygame.init()
pygame.mixer.quit()      # Disable mixer to prevent ALSA crashes on headless boxes

# -----------------------------------------------------------------------------#
# GLOBAL CONSTANTS
# -----------------------------------------------------------------------------#
WINDOW_WIDTH, WINDOW_HEIGHT = 640, 480
TILE_SIZE = 16

# Physics tuned using research on classic Mario titles
GRAVITY = 0.25
MAX_FALL_SPEED = 6
JUMP_VELOCITY = -4.5
RUN_SPEED = 2.8
WALK_SPEED = 1.4
FRICTION = 0.85

# NES‑style palette
MARIO_RED       = (172, 44,  52)
MARIO_BROWN     = (140, 84,  60)
SKY_BLUE        = ( 92,148, 252)
BRICK_BROWN     = (188,116,  68)
PIPE_GREEN      = (  0,168,  68)
QUESTION_YELLOW = (252,188,  60)
CLOUD_WHITE     = (236,238, 236)
BLACK           = (  0,  0,   0)
WHITE           = (252,252, 252)
GRAY            = (128,128, 128)

# Boot splash colors
BOOT_RED  = (220, 20, 60)
BOOT_GOLD = (255,215,  0)

# -----------------------------------------------------------------------------#
# TILE & ENEMY ENUM
# -----------------------------------------------------------------------------#
class TileType(Enum):
    GROUND   = 0
    BRICK    = 1
    QUESTION = 2
    PIPE_TOP_L      = 3
    PIPE_TOP_R      = 4
    PIPE_BODY_L     = 5
    PIPE_BODY_R     = 6
    COIN     = 7
    HARD_BLOCK = 8

class EnemyType(Enum):
    GOOMBA = 0

# -----------------------------------------------------------------------------#
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------#
def snap(value, size=TILE_SIZE):
    # Grid‑snap utility :contentReference[oaicite:10]{index=10}
    return (value // size) * size

def draw_tile(surface, tile_type, x, y):
    r = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
    if tile_type == TileType.GROUND:
        surface.fill(BRICK_BROWN, r)
        pygame.draw.rect(surface, MARIO_BROWN, r, 1)
    elif tile_type == TileType.BRICK:
        surface.fill(BRICK_BROWN, r)
        pygame.draw.line(surface, MARIO_BROWN, (x, y+8), (x+16, y+8))
        pygame.draw.rect(surface, MARIO_BROWN, r, 1)
    elif tile_type == TileType.QUESTION:
        surface.fill(QUESTION_YELLOW, r)
        pygame.draw.rect(surface, MARIO_BROWN, r, 1)
        q = FONT.render("?", True, WHITE)
        surface.blit(q, q.get_rect(center=r.center))
    elif tile_type in (TileType.PIPE_TOP_L, TileType.PIPE_TOP_R,
                       TileType.PIPE_BODY_L, TileType.PIPE_BODY_R):
        surface.fill(PIPE_GREEN, r)
        pygame.draw.rect(surface, BLACK, r, 1)
    elif tile_type == TileType.COIN:
        pygame.draw.circle(surface, QUESTION_YELLOW, r.center, 6)
        pygame.draw.circle(surface, MARIO_BROWN, r.center, 6, 1)
    elif tile_type == TileType.HARD_BLOCK:
        surface.fill(GRAY, r)
        pygame.draw.rect(surface, BLACK, r, 1)

def draw_goomba(surface, x, y):
    pygame.draw.ellipse(surface, MARIO_BROWN, (x, y+4, 16, 12))
    pygame.draw.rect(surface, MARIO_BROWN, (x+3, y+12, 4, 4))
    pygame.draw.rect(surface, MARIO_BROWN, (x+9, y+12, 4, 4))

# -----------------------------------------------------------------------------#
# CLASSES
# -----------------------------------------------------------------------------#
class Mario:
    WIDTH, HEIGHT = 12, 16
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx = self.vy = 0
        self.on_ground = False
        self.facing_right = True

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.WIDTH, self.HEIGHT)

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.facing_right = False
            self.vx = -RUN_SPEED if (keys[pygame.K_LSHIFT] or keys[pygame.K_z]) else -WALK_SPEED
        elif keys[pygame.K_RIGHT]:
            self.facing_right = True
            self.vx = RUN_SPEED if (keys[pygame.K_LSHIFT] or keys[pygame.K_z]) else WALK_SPEED
        else:
            self.vx *= FRICTION
            if abs(self.vx) < 0.05: self.vx = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = JUMP_VELOCITY
            self.on_ground = False

    def physics(self):
        self.vy = min(self.vy + GRAVITY, MAX_FALL_SPEED)
        self.x += self.vx
        self.y += self.vy

    def collide(self, level):
        # Horizontal pass
        self.rect.clamp_ip(pygame.Rect(0, 0, level.pixel_width, level.pixel_height))
        for tx, ty, tt in level.tiles:
            if tt == TileType.COIN:
                continue
            tile_rect = pygame.Rect(tx, ty, TILE_SIZE, TILE_SIZE)
            if self.rect.colliderect(tile_rect):
                if self.vx > 0:
                    self.x = tile_rect.left - self.WIDTH
                elif self.vx < 0:
                    self.x = tile_rect.right
                self.vx = 0
        # Vertical
        self.rect.topleft = (int(self.x), int(self.y))
        for tile in level.tiles.copy():
            tx, ty, tt = tile
            tile_rect = pygame.Rect(tx, ty, TILE_SIZE, TILE_SIZE)
            if self.rect.colliderect(tile_rect):
                if tt == TileType.COIN:                      # pickup
                    level.tiles.remove(tile)
                    continue
                if self.vy > 0:
                    self.y = tile_rect.top - self.HEIGHT
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = tile_rect.bottom
                    self.vy = 0
        self.rect.topleft = (int(self.x), int(self.y))

    def update(self, level, keys):
        self.handle_input(keys)
        self.physics()
        self.collide(level)

    def draw(self, surface, camx, camy):
        x = int(self.x - camx)
        y = int(self.y - camy)
        pygame.draw.rect(surface, MARIO_RED, (x+2, y, 8, 6))     # hat
        pygame.draw.rect(surface, (0,0,252), (x+2, y+8, 8, 4))   # overalls
        pygame.draw.rect(surface, MARIO_RED, (x,   y+6, 12, 6))  # torso
        pygame.draw.rect(surface, QUESTION_YELLOW, (x+4, y+2, 4, 4))  # face

class Goomba:
    WIDTH = HEIGHT = 16
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx = -0.5
        self.vy = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.WIDTH, self.HEIGHT)

    def update(self, level):
        self.vy = min(self.vy + GRAVITY, MAX_FALL_SPEED)
        self.x += self.vx
        self.y += self.vy

        for tx, ty, tt in level.tiles:
            if tt == TileType.COIN:
                continue
            tile_rect = pygame.Rect(tx, ty, TILE_SIZE, TILE_SIZE)
            if self.rect.colliderect(tile_rect):
                if self.vy > 0:
                    self.y = tile_rect.top - self.HEIGHT
                    self.vy = 0
                else:
                    self.vx = -self.vx
        self.rect.clamp_ip(pygame.Rect(0,0, level.pixel_width, level.pixel_height))

    def draw(self, surface, camx, camy):
        draw_goomba(surface, int(self.x - camx), int(self.y - camy))

# -----------------------------------------------------------------------------#
# LEVEL
# -----------------------------------------------------------------------------#
class Level:
    def __init__(self):
        self.tiles = []
        self.enemies = []
        self.width, self.height = 160, 15   # in tiles
        self.start = (32, 200)
        self.theme = "overworld"
    @property
    def pixel_width(self):  return self.width  * TILE_SIZE
    @property
    def pixel_height(self): return self.height * TILE_SIZE

    # --- Tile helpers
    def add_tile(self, x, y, tt):
        gx, gy = snap(x), snap(y)
        self.tiles = [(tx,ty,tt2) for tx,ty,tt2 in self.tiles if (tx,ty)!=(gx,gy)]
        self.tiles.append((gx, gy, tt))
    def remove_tile(self, x, y):
        gx, gy = snap(x), snap(y)
        self.tiles = [(tx,ty,tt2) for tx,ty,tt2 in self.tiles if (tx,ty)!=(gx,gy)]

    # --- Enemy helpers
    def add_enemy(self, x, y, etype):
        gx, gy = snap(x), snap(y)
        self.enemies.append((gx, gy, etype))
    def remove_enemy(self, x, y):
        gx, gy = snap(x), snap(y)
        self.enemies = [(ex,ey,et) for ex,ey,et in self.enemies if (ex,ey)!=(gx,gy)]

# -----------------------------------------------------------------------------#
# EDITOR
# -----------------------------------------------------------------------------#
class Editor:
    def __init__(self):
        self.camx = self.camy = 0
        self.mode = "tile"                 # 'tile' or 'enemy'
        self.sel_tile = TileType.GROUND
        self.sel_enemy = EnemyType.GOOMBA
        self.grid = True
        self.test_mode = False
        self.level = Level()
        # Auto‑seed ground
        for x in range(0, self.level.pixel_width, TILE_SIZE):
            self.level.add_tile(x, (self.level.height-2)*TILE_SIZE, TileType.GROUND)
            self.level.add_tile(x, (self.level.height-1)*TILE_SIZE, TileType.GROUND)

        self.mario = None
        self.runtime_enemies = []

    # ------------------------------------------------------------------#
    # PLAY/TEST
    # ------------------------------------------------------------------#
    def start_test(self):
        self.test_mode = True
        self.mario = Mario(*self.level.start)
        self.runtime_enemies = [Goomba(ex,ey) for ex,ey,et in self.level.enemies if et==EnemyType.GOOMBA]
    def stop_test(self):
        self.test_mode = False
        self.mario = None
        self.runtime_enemies.clear()
        self.camx = self.camy = 0

    # ------------------------------------------------------------------#
    # INPUT
    # ------------------------------------------------------------------#
    def handle_click(self, mx, my, button):
        if self.test_mode: return
        wx, wy = mx + self.camx, my + self.camy
        if self.mode == "tile":
            if button == 1:
                self.level.add_tile(wx, wy, self.sel_tile)
            elif button == 3:
                self.level.remove_tile(wx, wy)
        else:  # enemy
            if button == 1:
                self.level.add_enemy(wx, wy, self.sel_enemy)
            elif button == 3:
                self.level.remove_enemy(wx, wy)

    def handle_keydown(self, key):
        if key == pygame.K_g: self.grid = not self.grid
        if key == pygame.K_e: self.mode = "enemy" if self.mode=="tile" else "tile"
        if key == pygame.K_q and not self.test_mode: self.start_test()
        if key == pygame.K_ESCAPE and self.test_mode: self.stop_test()
        if key == pygame.K_r and self.test_mode:      # quick reset
            self.stop_test(); self.start_test()
        # Tile palette hotkeys
        if pygame.K_1 <= key <= pygame.K_9:
            idx = key - pygame.K_1
            if idx < len(TileType):
                self.sel_tile = list(TileType)[idx]

    # ------------------------------------------------------------------#
    # UPDATE
    # ------------------------------------------------------------------#
    def update(self, keys):
        if self.test_mode:
            self.mario.update(self.level, keys)
            for en in self.runtime_enemies:
                en.update(self.level)
            # basic enemy‑player stomp logic
            for en in self.runtime_enemies.copy():
                if self.mario.rect.colliderect(en.rect):
                    if self.mario.vy > 0:
                        self.runtime_enemies.remove(en)
                        self.mario.vy = JUMP_VELOCITY/2
                    else:
                        self.stop_test()   # player hit
                        return
            # camera follow
            self.camx = max(0, min(int(self.mario.x - WINDOW_WIDTH//2), self.level.pixel_width - WINDOW_WIDTH))
            self.camy = max(0, min(int(self.mario.y - WINDOW_HEIGHT//2), self.level.pixel_height - WINDOW_HEIGHT))
        else:
            # free camera in editor
            speed = 8
            if keys[pygame.K_LEFT]:  self.camx = max(0, self.camx - speed)
            if keys[pygame.K_RIGHT]: self.camx = min(self.level.pixel_width - WINDOW_WIDTH, self.camx + speed)
            if keys[pygame.K_UP]:    self.camy = max(0, self.camy - speed)
            if keys[pygame.K_DOWN]:  self.camy = min(self.level.pixel_height - WINDOW_HEIGHT, self.camy + speed)

    # ------------------------------------------------------------------#
    # DRAW
    # ------------------------------------------------------------------#
    def draw(self, surf):
        surf.fill(SKY_BLUE if self.level.theme=="overworld" else BLACK)

        # Tiles
        for tx,ty,tt in self.level.tiles:
            if -TILE_SIZE < tx - self.camx < WINDOW_WIDTH  and -TILE_SIZE < ty - self.camy < WINDOW_HEIGHT:
                draw_tile(surf, tt, tx - self.camx, ty - self.camy)

        # Enemies (editor overlay)
        if not self.test_mode:
            for ex,ey,et in self.level.enemies:
                if et==EnemyType.GOOMBA and -TILE_SIZE<ex-self.camx<WINDOW_WIDTH and -TILE_SIZE<ey-self.camy<WINDOW_HEIGHT:
                    draw_goomba(surf, ex-self.camx, ey-self.camy)

        # Runtime sprites
        if self.test_mode:
            for en in self.runtime_enemies: en.draw(surf, self.camx, self.camy)
            self.mario.draw(surf, self.camx, self.camy)

        # Grid
        if self.grid and not self.test_mode:
            for x in range(-self.camx % TILE_SIZE, WINDOW_WIDTH, TILE_SIZE):
                pygame.draw.line(surf, GRAY, (x,0),(x,WINDOW_HEIGHT))
            for y in range(-self.camy % TILE_SIZE, WINDOW_HEIGHT, TILE_SIZE):
                pygame.draw.line(surf, GRAY, (0,y),(WINDOW_WIDTH,y))

        # UI BAR
        pygame.draw.rect(surf, BLACK, (0,0,WINDOW_WIDTH,32))
        pygame.draw.line(surf, WHITE, (0,32), (WINDOW_WIDTH,32))
        x_off = 8
        # tile palette icons
        for i,tt in enumerate(TileType):
            if i>=9: break
            draw_tile(surf, tt, x_off, 8)
            if self.mode=="tile" and tt==self.sel_tile:
                pygame.draw.rect(surf, WHITE, (x_off,8,16,16), 2)
            x_off += 20
        # enemy palette
        draw_goomba(surf, x_off, 8)
        if self.mode=="enemy":
            pygame.draw.rect(surf, WHITE, (x_off,8,16,16), 2)
        # info text
        mode_text = "TEST" if self.test_mode else ("ENEMY" if self.mode=="enemy" else "TILE")
        txt = FONT.render(f"{mode_text} MODE  (E: toggle, Q: play, ESC: quit)", True, WHITE)
        surf.blit(txt, (WINDOW_WIDTH-txt.get_width()-8,8))

# -----------------------------------------------------------------------------#
# BOOT SPLASH
# -----------------------------------------------------------------------------#
def boot():
    splash = pygame.Surface((WINDOW_WIDTH,WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    for frame in range(180):
        for e in pygame.event.get():
            if e.type==pygame.QUIT: return False
        alpha = 255 if 60<=frame<=120 else (frame*4 if frame<60 else max(0,255-(frame-120)*4))
        splash.fill(BOOT_RED); splash.set_alpha(alpha)
        WIN.blit(splash,(0,0))
        if 30<frame<150:
            t1 = BIG_FONT.render("TEAM SPECIALEMU", True, BOOT_GOLD)
            t2 = FONT.render("AGI Division Presents", True, WHITE)
            WIN.blit(t1, t1.get_rect(center=(WINDOW_WIDTH//2,WINDOW_HEIGHT//2-20)))
            WIN.blit(t2, t2.get_rect(center=(WINDOW_WIDTH//2,WINDOW_HEIGHT//2+20)))
        pygame.display.flip(); clock.tick(60)
    return True

# -----------------------------------------------------------------------------#
# INITIALISE
# -----------------------------------------------------------------------------#
WIN   = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Mario Worker ‑ Special 64 Edition")
CLOCK = pygame.time.Clock()
FONT      = pygame.font.Font(None, 16)
BIG_FONT  = pygame.font.Font(None, 32)

# -----------------------------------------------------------------------------#
# MAIN LOOP
# -----------------------------------------------------------------------------#
def main():
    if not boot(): return
    editor = Editor(); running=True
    while running:
        keys = pygame.key.get_pressed()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            elif e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE and not editor.test_mode: running=False
                else: editor.handle_keydown(e.key)
            elif e.type==pygame.MOUSEBUTTONDOWN:
                editor.handle_click(*e.pos, e.button)
        editor.update(keys)
        editor.draw(WIN)
        fps = FONT.render(f"{int(CLOCK.get_fps())}", True, WHITE)
        WIN.blit(fps,(4,WINDOW_HEIGHT-18))
        pygame.display.flip(); CLOCK.tick(60)
    pygame.quit()

if __name__=="__main__":
    main()
