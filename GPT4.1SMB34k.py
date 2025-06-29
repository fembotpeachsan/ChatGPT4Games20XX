#!/usr/bin/env python3
"""
Super Mario Bros. 3 – SNES PC Edition (Full Tech Demo)
All graphics, sound, and menus from code. No files. 60 FPS.
"""

import math, random, time, sys, pickle, threading
from array import array
import pygame as pg

### ----------- CONFIG
WIDTH, HEIGHT = 640, 448
FPS = 60
TILE = 16
GRAVITY = 0.32
WALK_SPEED, RUN_SPEED = 1.5, 3.2
JUMP_VY = -6.7
P_METER_MAX = 100
BLACK, WHITE = (0,0,0), (255,255,255)
WORLD_COUNT = 5

# ---- Pygame Init
pg.mixer.pre_init(44100, -16, 1, 256)
pg.init()
pg.font.init()
pg.mixer.set_num_channels(8)

# ---- SFX + Music
def square_wave(freq, dur, vol=0.4):
    sr = 44100
    length = int(dur * sr)
    buf = array('h')
    period = sr / freq if freq else 1
    for i in range(length):
        v = vol*32767 if (i % period) < period/2 else -vol*32767
        buf.append(int(v))
    return pg.mixer.Sound(buffer=buf.tobytes())

SFX = {
    'jump'  : square_wave(880, .12),
    'stomp' : square_wave(110, .09),
    'coin'  : square_wave(1560, .18),
    'power' : square_wave(660, .2),
    'bump'  : square_wave(140, .09),
    'death' : square_wave(220, .8 , vol=.6),
    'boom'  : square_wave(55,  .6 , vol=.7),
    'flag'  : square_wave(2200, .4),
}

NOTESEQ = [
    (659,0.5),(659,0.5),(0,0.5),(659,0.5),(0,0.5),(523,0.5),(659,1),(0,0.5),
    (784,1.5),(0,0.5),(392,1.5),(0,0.5),
    (523,0.5),(0,0.25),(392,0.5),(0,0.25),(330,0.5),(0,0.25),
    (440,0.5),(0,0.25),(494,0.5),(0,0.25),(466,0.25),(440,0.5),(0,0.25),
    (392,0.75),(659,0.25),(784,0.25),(880,0.5),(0,0.25),
    (698,0.5),(784,0.5),(0,0.25),(659,0.5),(0,0.25),
    (523,0.5),(587,0.25),(494,0.5),(0,0.5),
]
def play_world1_music(loop=True):
    ch = pg.mixer.Channel(7)
    beat = 60/180
    def music():
        while True:
            for f,d in NOTESEQ:
                if f: ch.play(square_wave(f, d*beat, vol=.18))
                time.sleep(d*beat*0.97)
            if not loop: break
    threading.Thread(target=music, daemon=True).start()

### ----------- LEVELS + MAP DATA
TILES = {
    '=': (180, 72, 12),      # Ground
    '#': (252,152,56),       # Highlight
    '?': (252,180,0),        # Question
    'B': (220,180,110),      # Brick
    'P': (0,200,0),          # Pipe
    'C': (255,220,0),        # Coin
    '-': (180,160,100),      # Platform
    'T': (0,168,0),          # Grass top
    'G': (0,200,64),         # Grass
    ' ': None,
    'F': (60, 60, 60),       # Fortress
    'X': (180, 0, 0),        # Flag
}

LEVELS = {
'1-1':[
"                                                                                                         ",
"                                                                                                         ",
"                                                                                                         ",
"                                                                                                         ",
"              ?                                                                                          ",
"                                     ?B?B?          P P                                                  ",
"                                                      P                                                  ",
"                      P P                          --     --           --     --                        ",
"             ?        P P        ?               -------               -------                           ",
"                      P P                                      ==                                     X ",
"                      P P                                     ===                                      ",
"                      P P                                    ====                                      ",
"TTTTTTTTTTTTTTTTTTTTTPPTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTPPTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT",
"GGGGGGGGGGGGGGGGGGGGGPPGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGPPGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
"=====================PP==============================PP=============================PP===================",
"=====================PP==============================PP=============================PP===================",
"=====================PP==============================PP=============================PP===================",
"=====================PP==============================PP=============================PP===================",
],
'1-2':[   # Underground
"                                                                                                         ",
"                                                                                                         ",
"                                                                                                         ",
"                                                                                                         ",
"                 ?B?B?                                                                                   ",
"                     ---                                                                                ",
"                  -------                ?                                                               ",
"         --  --  ---------            BBBB                                                               ",
"      --------  -------------                     ----                                                   ",
"   ------------         ?B?B?                 --------                    P P                             ",
"------------           -------              ------------                 P P                              ",
"--------         -------------------      ------------------             P P                              ",
"TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTPPTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT",
"GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGPPGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
"=====================PP==============================PP=============================PP===================",
"=====================PP==============================PP=============================PP===================",
"=====================PP==============================PP=============================PP===================",
"=====================PP==============================PP=============================PP===================",
],
'1-3':[   # Platforms
"                                                                                                         ",
"                                                                                                         ",
"                                                                                                         ",
"                                                                                                         ",
"                                                                                                         ",
"         ---         ---        ---                                                                      ",
"         CCC       CCCCC     CCCCCC   ?                                                                 ",
"     --    --       ---        ---                                                                       ",
"         ---         ---        ---    ?B?B?        X                                                    ",
"   =======     =======     =======   -------                                                            ",
"==========   ==========   ==========----------------                                                     ",
"=====================   ===============   ======                                                        ",
"TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT",
"GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
"=====================PP==============================PP=============================PP===================",
"=====================PP==============================PP=============================PP===================",
"=====================PP==============================PP=============================PP===================",
"=====================PP==============================PP=============================PP===================",
],
'1-F': [   # Fortress
"                                                                                                         ",
"                                                                                                         ",
"BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
"B                                                                                                     B",
"B                 BB   BB                    BBBBBBB                              BBBBBB               B",
"B              BBBBBBBBBBBB               BBBBBBBBBBBBB                        BBBBBBBBBBBB            B",
"B           BBBBBBBBBBBBBBBBBB         BBBBBBBBBBBBBBBBBBB                  BBBBBBBBBBBBBBBBBB         B",
"B        BBBBBBBBBBBBBBBBBBBBBBBB   BBBBBBBBBBBBBBBBBBBBBBBBB           BBBBBBBBBBBBBBBBBBBBBBBBB      B",
"B                                                                                                     B",
"B                                                                                                     B",
"B                                                                                      ==============B",
"BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
"BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
"BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
"BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
"BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
"BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
],
}

def tile_at(level,x,y):
    if y<0 or y>=len(level): return ' '
    row = level[y]
    if x<0 or x>=len(row): return ' '
    return row[x]

### ----------- SCENES
class Scene:  # Base class for menus/game
    def handle_event(self,e): pass
    def update(self,dt,keys): pass
    def draw(self,screen): pass

# --- Title and File Select
class Title(Scene):
    def __init__(self, game):
        self.game = game
        self.blink = 0
        self.logo_y = 80
        self.frame = 0

    def handle_event(self, e):
        if e.type == pg.KEYDOWN and e.key in (pg.K_RETURN, pg.K_SPACE):
            self.game.change_scene(FileSelect(self.game))

    def update(self, dt, keys):
        self.blink = (self.blink + dt * 8) % 2
        self.logo_y = 80 + math.sin(time.time() * 2) * 10
        self.frame += 1

    def draw(self, sc):
        sc.fill((0, 0, 0))
        # BG pattern
        for i in range(0, HEIGHT, 32):
            pg.draw.rect(sc, (20, 20, 80), (0, i, WIDTH, 16))
        # Title
        title = "SUPER MARIO BROS. 3"
        font = self.game.font_big
        shadow = font.render(title, True, (128, 64, 0))
        text = font.render(title, True, (255, 200, 0))
        tx = WIDTH // 2 - text.get_width() // 2
        sc.blit(shadow, (tx + 3, int(self.logo_y + 3)))
        sc.blit(text, (tx, int(self.logo_y)))
        # Subtitle
        sub = self.game.font.render("PC EDITION", True, (255, 255, 255))
        sc.blit(sub, (WIDTH // 2 - sub.get_width() // 2, int(self.logo_y + 54)))
        # Blinking "PRESS ENTER"
        if self.blink < 1:
            msg = self.game.font.render("PRESS ENTER", True, (255, 255, 120))
            sc.blit(msg, (WIDTH // 2 - msg.get_width() // 2, int(self.logo_y + 100)))
        # Sparkles
        for i in range(6):
            t = (self.frame//7+i*12)%WIDTH
            if t > 0 and t < WIDTH-5:
                pg.draw.circle(sc, (255,255,180,128), (t, int(self.logo_y+30+10*math.sin(i+self.frame*0.06))), 1)

class FileSelect(Scene):
    def __init__(self, game):
        self.game = game
        self.sel = 0
        self.files = [
            {'name': 'FILE A', 'world': 1, 'level': '1-1', 'lives': 3, 'coins': 0},
            {'name': 'FILE B', 'world': 1, 'level': '1-1', 'lives': 3, 'coins': 0},
            {'name': 'FILE C', 'world': 1, 'level': '1-1', 'lives': 3, 'coins': 0}
        ]
        self.blink = 0

    def handle_event(self, e):
        if e.type == pg.KEYDOWN:
            if e.key in (pg.K_UP, pg.K_w):   self.sel = (self.sel - 1) % 3
            if e.key in (pg.K_DOWN, pg.K_s): self.sel = (self.sel + 1) % 3
            if e.key == pg.K_RETURN:
                self.game.save_slot = self.sel
                self.game.save = self.files[self.sel].copy()
                self.game.change_scene(Overworld(self.game))
            if e.key == pg.K_ESCAPE:
                self.game.change_scene(Title(self.game))

    def update(self, dt, keys):
        self.blink = (self.blink + dt * 8) % 2

    def draw(self, sc):
        sc.fill((16, 24, 64))
        label = self.game.font_big.render("FILE SELECT", True, (255, 255, 255))
        sc.blit(label, (WIDTH // 2 - label.get_width() // 2, 48))
        for i, f in enumerate(self.files):
            y = 140 + i * 80
            is_sel = (i == self.sel)
            slot_rect = pg.Rect(WIDTH // 2 - 150, y - 10, 300, 64)
            col = (64, 64, 160) if not is_sel else (255, 230, 90)
            pg.draw.rect(sc, col, slot_rect, 0 if is_sel else 2, border_radius=12)
            fname = self.game.font_big.render(f['name'], True, (0,0,0) if is_sel else (255,255,255))
            sc.blit(fname, (WIDTH // 2 - fname.get_width() // 2, y))
            meta = f"World {f['world']}  |  {f['lives']} Lives  |  {f['coins']} Coins"
            meta_r = self.game.font.render(meta, True, (50, 50, 50) if is_sel else (220,220,255))
            sc.blit(meta_r, (WIDTH // 2 - meta_r.get_width() // 2, y + 36))
        if self.blink < 1:
            arrow = self.game.font_big.render("➤", True, (255, 128, 32))
            sel_y = 140 + self.sel * 80
            sc.blit(arrow, (WIDTH // 2 - 190, sel_y))
        esc_tip = self.game.font.render("ESC = BACK", True, (120, 120, 160))
        sc.blit(esc_tip, (32, HEIGHT - 32))

class Overworld(Scene):
    NODES = [
        ('1-1', 80, 300), ('1-2', 160, 260), ('1-3', 250, 310), ('1-F', 340, 260),
        ('X', 480, 300) # placeholder for future worlds
    ]
    EDGES = [(0,1), (1,2), (2,3), (3,4)]
    def __init__(self, game):
        self.game = game
        self.pos = 0
        self.blink = 0
    def handle_event(self, e):
        if e.type == pg.KEYDOWN:
            if e.key in (pg.K_LEFT,pg.K_a): self.pos = max(0, self.pos-1)
            if e.key in (pg.K_RIGHT,pg.K_d):self.pos = min(len(self.NODES)-2, self.pos+1)
            if e.key == pg.K_RETURN:
                level = self.NODES[self.pos][0]
                if level != 'X': self.game.change_scene(Level(self.game, level))
            if e.key == pg.K_ESCAPE:
                self.game.change_scene(FileSelect(self.game))
    def update(self, dt, keys): self.blink = (self.blink + dt * 8) % 2
    def draw(self, sc):
        sc.fill((104,184,248))
        # World path
        for a,b in self.EDGES:
            xa,ya = self.NODES[a][1:]
            xb,yb = self.NODES[b][1:]
            pg.draw.line(sc, (0,0,0), (xa,ya), (xb,yb), 5)
        # Nodes
        for i,(name,x,y) in enumerate(self.NODES):
            col = (200,0,0) if i==self.pos else (0,0,0)
            pg.draw.circle(sc, col, (x,y), 18, 0 if i==self.pos else 2)
            label = self.game.font.render(name if name != 'X' else "WORLD 2", True, col)
            sc.blit(label, (x-25, y+22))
        # Mario icon
        mx,my = self.NODES[self.pos][1:]
        pg.draw.circle(sc, (255,224,128), (mx,my-25), 12)
        pg.draw.rect(sc, (236,88,0), (mx-8,my-39,16,8))
        # Blinking select
        if self.blink < 1:
            s = self.game.font.render("ENTER = PLAY", True, (255,255,255))
            sc.blit(s, (WIDTH//2 - s.get_width()//2, HEIGHT-48))

# --- Player, Enemies, Physics
def mario_palette(power):
    if power == 2:
        return ((252,252,252),(252,152,56),(255,200,150))
    elif power == 1:
        return ((236,88,0),(252,152,56),(255,200,150))
    else:
        return ((236,88,0),(252,152,56),(255,200,150))

def draw_mario(surf, x, y, flip, power, walkframe, jumping=False):
    px = lambda dx,dy,w,h,c: pg.draw.rect(surf,c,(x+dx,y+dy,w,h))
    colors = mario_palette(power)
    h = 24 if power > 0 else 16
    if power == 0:
        px(4,0,8,8,colors[2])
        px(3,1,10,6,colors[2])
        px(3,0,10,4,colors[0])
        px(4,0,8,5,colors[0])
        px(10,3,1,2,BLACK)
        px(4,8,8,4,colors[0])
        px(3,9,10,3,colors[0])
        px(2,9,2,3,colors[2]) if not flip else px(12,9,2,3,colors[2])
        if jumping:
            px(4,12,3,4,colors[1])
            px(9,12,3,4,colors[1])
        else:
            legx = [3,9] if (walkframe//4)%2 else [4,8]
            for lx in legx:
                px(lx,12,4,4,colors[1])
    else:
        px(4,4,8,8,colors[2])
        px(3,5,10,6,colors[2])
        px(3,0,10,6,colors[0])
        px(4,0,8,7,colors[0])
        px(10,7,1,2,BLACK)
        px(9,10,4,1,BLACK)
        px(4,12,8,6,colors[0])
        px(3,13,10,5,colors[0])
        px(1,13,3,4,colors[2]) if not flip else px(12,13,3,4,colors[2])
        if jumping:
            px(4,18,3,6,colors[1])
            px(9,18,3,6,colors[1])
        else:
            legx = [2,9] if (walkframe//4)%2 else [3,8]
            for lx in legx:
                px(lx,18,5,6,colors[1])
    if flip:
        surf.blit(pg.transform.flip(surf.subsurface(pg.Rect(x,y,16,h)),True,False),(x,y))

class Player:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx = self.vy = 0
        self.on_ground = False
        self.power = 0
        self.walkframe = 0
        self.facing_right = True
        self.jumping = False
        self.p_meter = 0
        self.coins = 0
        self.lives = 3
    def rect(self):
        h = 24 if self.power > 0 else 16
        return pg.Rect(int(self.x),int(self.y),16,h)
    def update(self, keys, level):
        run = keys[pg.K_x]
        ax = 0
        if keys[pg.K_LEFT] or keys[pg.K_a]:  ax = -RUN_SPEED if run else -WALK_SPEED; self.facing_right = False
        if keys[pg.K_RIGHT] or keys[pg.K_d]: ax = RUN_SPEED if run else WALK_SPEED; self.facing_right = True
        if not (keys[pg.K_LEFT]|keys[pg.K_a]|keys[pg.K_RIGHT]|keys[pg.K_d]):
            self.vx *= 0.89 if self.on_ground else 0.95
        else:
            self.vx = ax
        if run and abs(self.vx) > WALK_SPEED and self.on_ground:
            self.p_meter = min(P_METER_MAX, self.p_meter + 2)
        else:
            self.p_meter = max(0, self.p_meter - 1)
        if (keys[pg.K_z] or keys[pg.K_SPACE]):
            if self.on_ground and not self.jumping:
                self.vy = JUMP_VY * (1.2 if self.p_meter >= P_METER_MAX else 1)
                self.on_ground = False; self.jumping = True; SFX['jump'].play()
        else:
            self.jumping = False
            if self.vy < -2:
                self.vy = -2
        self.vy += GRAVITY; self.vy = min(self.vy, 10)
        self.x += self.vx; self._horizontal_collide(level)
        self.y += self.vy; self.on_ground = False; self._vertical_collide(level)
        if abs(self.vx)>0.5 and self.on_ground: self.walkframe += 1
        else: self.walkframe = 0
        tx, ty = int((self.x+8)/TILE), int((self.y+8)/TILE)
        if tile_at(level, tx, ty) == 'C':
            self.coins += 1; SFX['coin'].play()
            level[ty] = level[ty][:tx] + ' ' + level[ty][tx+1:]
    def _horizontal_collide(self, level):
        r = self.rect()
        for ty in range(r.top//TILE, (r.bottom-1)//TILE+1):
            if self.vx > 0: tx = r.right // TILE
            else: tx = r.left // TILE
            tile = tile_at(level, tx, ty)
            if tile in '=#PBT?-X':
                if self.vx > 0: self.x = tx * TILE - 16
                else: self.x = (tx + 1) * TILE
                self.vx = 0
    def _vertical_collide(self, level):
        r = self.rect()
        for tx in range(r.left//TILE, (r.right-1)//TILE+1):
            if self.vy > 0: ty = r.bottom // TILE
            else: ty = r.top // TILE
            tile = tile_at(level, tx, ty)
            if tile in '=#PBT?-X':
                if self.vy > 0:
                    self.y = ty * TILE - (24 if self.power > 0 else 16)
                    self.vy = 0; self.on_ground = True
                else:
                    self.y = (ty + 1) * TILE; self.vy = 0
                    if tile == '?':
                        SFX['coin'].play(); self.coins += 1
                        level[ty] = level[ty][:tx] + 'B' + level[ty][tx+1:]
                    elif tile == 'B' and self.power > 0:
                        SFX['bump'].play()
                        level[ty] = level[ty][:tx] + ' ' + level[ty][tx+1:]

class Goomba:
    def __init__(self,x,y):
        self.x=float(x); self.y=float(y)
        self.vx=-0.5; self.vy=0
        self.alive=True; self.squish_timer=0
    def rect(self): return pg.Rect(int(self.x),int(self.y),16,16)
    def update(self,level):
        if not self.alive: self.squish_timer -= 1; return
        self.vy += GRAVITY; self.x += self.vx; self.y += self.vy
        check_x = int((self.x + (16 if self.vx > 0 else 0)) / TILE)
        check_y = int((self.y + 16) / TILE)
        if tile_at(level, check_x, check_y) == ' ':
            self.vx = -self.vx
        if self.vy > 0:
            ty = int((self.y + 16) / TILE)
            tx = int((self.x + 8) / TILE)
            if tile_at(level, tx, ty) in '=#PTG':
                self.y = ty * TILE - 16; self.vy = 0
    def draw(self,surf,camx):
        if not self.alive:
            if self.squish_timer > 0:
                pg.draw.rect(surf,(152,72,8),(self.x-camx,self.y+8,16,8))
            return
        pg.draw.rect(surf,(152,72,8),(self.x-camx+2,self.y+4,12,12))
        pg.draw.ellipse(surf,(152,72,8),(self.x-camx,self.y,16,10))
        pg.draw.circle(surf,WHITE,(int(self.x-camx+5),int(self.y+4)),2)
        pg.draw.circle(surf,WHITE,(int(self.x-camx+11),int(self.y+4)),2)
        pg.draw.circle(surf,BLACK,(int(self.x-camx+5),int(self.y+4)),1)
        pg.draw.circle(surf,BLACK,(int(self.x-camx+11),int(self.y+4)),1)
        pg.draw.rect(surf,BLACK,(self.x-camx+2,self.y+14,5,2))
        pg.draw.rect(surf,BLACK,(self.x-camx+9,self.y+14,5,2))

### --- MAIN LEVEL SCENE
class Level(Scene):
    def __init__(self,game,code):
        self.game=game; self.code=code; self.level=[row[:] for row in LEVELS[code]]
        self.player=Player(32,HEIGHT-80)
        self.enemies=[Goomba(200,HEIGHT-32)]
        self.camx=0; self.done=False
        play_world1_music()
    def handle_event(self,e):
        if e.type==pg.KEYDOWN and e.key==pg.K_r: self.game.change_scene(Level(self.game,self.code))
        if e.type==pg.KEYDOWN and e.key==pg.K_ESCAPE: self.game.change_scene(Overworld(self.game))
    def update(self,dt,keys):
        self.player.update(keys,self.level)
        for g in self.enemies: g.update(self.level)
        # Camera
        self.camx = max(0, int(self.player.x - WIDTH//2))
        self.camx = min(self.camx, len(self.level[0])*TILE - WIDTH)
        # Win condition (reaches far right flag/pole)
        if self.player.x > len(self.level[0])*TILE-64:
            SFX['flag'].play()
            self.game.save['level'] = self.code
            self.game.change_scene(Overworld(self.game))
    def draw(self,sc):
        sc.fill((92,148,252))
        # Parallax BG
        for i in range(4):
            y=(i*40+((self.camx//4)%80)); col=(200-i*30,240-i*20,255)
            pg.draw.rect(sc,col,(0,y,WIDTH,40))
        # Tiles
        for y,row in enumerate(self.level):
            for x,ch in enumerate(row):
                if ch!=' ':
                    col = TILES.get(ch, (200,200,200))
                    pg.draw.rect(sc,col,(x*TILE-self.camx,y*TILE,TILE,TILE))
        draw_mario(sc, self.player.x-self.camx, self.player.y, not self.player.facing_right,
                   self.player.power, self.player.walkframe, not self.player.on_ground)
        for g in self.enemies:
            g.draw(sc,self.camx)

### --- GAME BOOT
class Game:
    def __init__(self):
        self.screen=pg.display.set_mode((WIDTH,HEIGHT)); pg.display.set_caption("SMB3 SNES PC Edition")
        self.clock=pg.time.Clock(); self.running=True
        self.font=pg.font.SysFont("Courier New",24)
        self.font_big=pg.font.SysFont("Courier New",32,bold=True)
        self.scene=Title(self); self.save_slot=0; self.save={}
    def change_scene(self,scene): self.scene=scene
    def loop(self):
        while self.running:
            dt=self.clock.tick(FPS)/1000
            keys=pg.key.get_pressed()
            for e in pg.event.get():
                if e.type==pg.QUIT: self.running=False
                if e.type==pg.KEYDOWN and e.key==pg.K_ESCAPE and isinstance(self.scene,Title): self.running=False
                self.scene.handle_event(e)
            self.scene.update(dt,keys)
            self.scene.draw(self.screen)
            pg.display.flip()
        pg.quit()

if __name__=="__main__":
    Game().loop()
