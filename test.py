"""
Super Mario Bros. 3 – pure‑code, single‑file prototype
──────────────────────────────────────────────────────
This file provides a **playable skeleton** of SMB3 recreated
entirely with Pygame draw calls—NO external assets.  

⚠️  Disclaimer (inside code as requested):  
    – For brevity/size, only core systems, World‑1 map,
      and a sample Level 1‑1 are fully populated.  
    – All other worlds, bosses, power‑ups, enemies, cut‑scenes,
      and UI details are scaffolded with TODO notes so you can
      extend them.  
    – Everything lives in a single file and follows the requested
      controls & vibe. Enjoy hacking it further!
"""

import sys, math, random, pygame as pg
# ──────────── CONSTANTS ──────────── #
WIDTH, HEIGHT     = 640, 480   # window
TILE              = 16         # pixel size of one tile
COL_BG            = ( 92,148,252)   # SMB3 sky blue
COL_GROUND        = (  0,160, 72)   # grass
COL_BRICK         = (228,108, 40)   # brick
COL_PLAYER        = (252,188,176)   # mario skin
COL_PLAYER_F      = (252, 92,  0)   # mario fire suit (placeholder)
COL_TEXT          = (252,252,252)   # HUD
GRAVITY           = 0.35
JUMP_VEL          = -6.5
MOVE_ACC, MAX_X   = 0.25, 3.5
FPS               = 60

# Controls
K_LEFT, K_RIGHT, K_RUN, K_JUMP = pg.K_LEFT, pg.K_RIGHT, pg.K_s, pg.K_SPACE

# Scenes
MENU, MAP, LEVEL, GAMEOVER = range(4)

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("SMB3 – Code‑Only Edition")
clock  = pg.time.Clock()
font   = pg.font.SysFont("Courier New", 14, bold=True)

# ──────────── UTILS ──────────── #
def draw_text(txt, pos):
    screen.blit(font.render(txt, True, COL_TEXT), pos)

# ──────────── LEVEL DATA ──────────── #
# Tiles legend: '.' empty, '#' ground, '?' brick block, 'P' pipe top, '=' pipe body,
# 'E' goomba, 'F' flag/goal, 'S' player start.
LEVELS = {
    "1‑1": [
        "................................................................",
        "................................................................",
        "................................................................",
        "................................................................",
        "................................................................",
        "................................................................",
        "...............................................E................",
        "........................??......................................",
        "............................................................F...",
        "##############################..###############################.",
        "S...............................................................",
    ],
    # TODO: Add 1‑2 … 8‑? layouts here
}

# ──────────── MAP DATA ──────────── #
class MapNode:
    def __init__(self, x, y, label, level_id=None, locked=False):
        self.rect = pg.Rect(x, y, 12, 12)
        self.label = label
        self.level_id = level_id
        self.locked = locked
        self.neighbors = []  # linked nodes

def build_world1():
    nodes = []
    start = MapNode(80, 320, "START")
    n1    = MapNode(140,320,"1‑1","1‑1")
    castle= MapNode(200,320,"CASTLE", locked=True)
    nodes += [start,n1,castle]
    start.neighbors.append(n1)
    n1.neighbors.append(castle)
    return nodes, start

# ──────────── PLAYER ──────────── #
class Player:
    def __init__(self, x, y):
        self.rect = pg.Rect(x, y, 12, 16)
        self.vel   = pg.Vector2(0, 0)
        self.on_ground = False
        self.power = "small"   # TODO: mushroom, fire, leaf, etc.
        self.lives = 4

    def update(self, tiles, keys):
        # Movement
        if keys[K_LEFT]:  self.vel.x = max(self.vel.x - MOVE_ACC, -MAX_X)
        elif keys[K_RIGHT]: self.vel.x = min(self.vel.x + MOVE_ACC,  MAX_X)
        else: self.vel.x *= 0.85

        # Jump
        if keys[K_JUMP] and self.on_ground:
            self.vel.y = JUMP_VEL
            self.on_ground = False

        # Gravity
        self.vel.y += GRAVITY
        if self.vel.y > 10: self.vel.y = 10

        # Horizontal collide
        self.rect.x += int(self.vel.x)
        self._collide(tiles, axis=0)
        # Vertical collide
        self.rect.y += int(self.vel.y)
        self._collide(tiles, axis=1)

    def _collide(self, tiles, axis):
        hit = None
        for t in tiles:
            if self.rect.colliderect(t):
                hit = t; break
        if not hit: 
            if axis==1: self.on_ground=False
            return
        if axis==0:
            if self.vel.x > 0: self.rect.right = hit.left
            elif self.vel.x < 0: self.rect.left = hit.right
            self.vel.x = 0
        else:
            if self.vel.y > 0:
                self.rect.bottom = hit.top
                self.on_ground = True
            elif self.vel.y < 0:
                self.rect.top = hit.bottom
            self.vel.y = 0

    def draw(self, cam_x):
        pg.draw.rect(screen, COL_PLAYER, self.rect.move(-cam_x,0))

# ──────────── LEVEL CLASS ──────────── #
class LevelScene:
    def __init__(self, level_id, world_state):
        self.data = LEVELS[level_id]
        self.tiles, self.enemies = [], []
        self.length_px = len(self.data[0])*TILE
        self.world_state = world_state
        # parse level
        y0=0
        for row in self.data:
            x0=0
            for ch in row:
                if ch == '#':
                    self.tiles.append(pg.Rect(x0,y0,TILE,TILE))
                elif ch == 'S':
                    self.player = Player(x0,y0-16)
                elif ch == 'E':
                    self.enemies.append(pg.Rect(x0,y0,TILE,14))  # simple goomba rectangle
                elif ch == 'F':
                    self.flag = pg.Rect(x0,y0,8,48)
                x0+=TILE
            y0+=TILE
        self.cam_x = 0
        self.complete=False

    def run(self):
        keys = pg.key.get_pressed()
        self.player.update(self.tiles, keys)

        # Camera follows player
        self.cam_x = max(0, min(self.player.rect.centerx - WIDTH//2, self.length_px-WIDTH))

        # simple enemy scroll
        for e in self.enemies:
            if e.colliderect(self.player.rect):
                self.player.lives -= 1
                return GAMEOVER if self.player.lives<0 else LEVEL

        # goal?
        if self.player.rect.colliderect(self.flag):
            self.complete=True
            return MAP

        # Render
        screen.fill(COL_BG)
        # draw tiles
        for t in self.tiles:
            pg.draw.rect(screen, COL_GROUND, t.move(-self.cam_x,0))
        pg.draw.rect(screen, (240,240,  0), self.flag.move(-self.cam_x,0))
        self.player.draw(self.cam_x)
        draw_text(f"World 1‑?  Lives:{self.player.lives}", (8,8))
        return LEVEL

# ──────────── MAP SCENE ──────────── #
class MapScene:
    def __init__(self, nodes, start_node, world_state):
        self.nodes = nodes
        self.cur   = start_node
        self.world_state = world_state

    def run(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            self._move(0,-1)
        elif keys[pg.K_DOWN]:
            self._move(0,1)
        elif keys[pg.K_LEFT]:
            self._move(-1,0)
        elif keys[pg.K_RIGHT]:
            self._move(1,0)
        elif keys[pg.K_RETURN] and self.cur.level_id and not self.cur.locked:
            return LEVEL, self.cur.level_id

        screen.fill((0,0,0))
        for n in self.nodes:
            col = (160,160,160) if n.locked else (240,240,240)
            pg.draw.rect(screen, col, n.rect, 1)
            draw_text(n.label, (n.rect.x-10, n.rect.y-14))
        pg.draw.rect(screen, (255, 80, 80), self.cur.rect.inflate(4,4), 2)
        draw_text("WORLD 1 MAP  – ENTER to play", (16,16))
        return MAP, None

    def _move(self, dx, dy):
        for n in self.cur.neighbors:
            if n.rect.x > self.cur.rect.x and dx>0: self.cur = n
            if n.rect.x < self.cur.rect.x and dx<0: self.cur = n
            if n.rect.y > self.cur.rect.y and dy>0: self.cur = n
            if n.rect.y < self.cur.rect.y and dy<0: self.cur = n

# ──────────── MENU SCENE ──────────── #
def menu_scene():
    while True:
        for e in pg.event.get():
            if e.type==pg.QUIT: pg.quit(); sys.exit()
            if e.type==pg.KEYDOWN:
                if e.key==pg.K_RETURN: return MAP
        screen.fill((0,0,0))
        draw_text("SUPER MARIO BROS. 3  (code‑only edition)", (100,200))
        draw_text("PRESS ENTER", (260,240))
        pg.display.flip()
        clock.tick(FPS)

# ──────────── GAME OVER ──────────── #
def gameover_scene():
    while True:
        for e in pg.event.get():
            if e.type==pg.QUIT: pg.quit(); sys.exit()
            if e.type==pg.KEYDOWN:
                if e.key==pg.K_RETURN: return MENU
        screen.fill((0,0,0))
        draw_text("GAME OVER – PRESS ENTER", (220,220))
        pg.display.flip()
        clock.tick(FPS)

# ──────────── MAIN LOOP ──────────── #
def main():
    state = MENU
    world_state = {}  # TODO: powerups, completed levels, etc.
    level_id = None

    # build world map
    nodes,start = build_world1()
    map_scene = MapScene(nodes,start,world_state)

    while True:
        for e in pg.event.get():
            if e.type==pg.QUIT: pg.quit(); sys.exit()

        if state == MENU:
            state = menu_scene()
        elif state == MAP:
            res, sel = map_scene.run()
            if res==LEVEL and sel:
                level_scene = LevelScene(sel, world_state)
                state, level_id = LEVEL, sel
            pg.display.flip(); clock.tick(FPS)
        elif state == LEVEL:
            state = level_scene.run()
            if state==MAP and level_scene.complete:
                # mark level completed, unlock next map node
                map_scene.cur.locked=False
                # TODO: unlock further nodes, handle item rewards, etc.
            pg.display.flip(); clock.tick(FPS)
        elif state == GAMEOVER:
            state = gameover_scene()

if __name__=="__main__":
    main()
