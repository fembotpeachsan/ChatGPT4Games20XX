#!/usr/bin/env python3
"""
Zelda 1 – Pure Pygame Edition (No PNGs, Just Vibes) · 2025
Author : Cat‑sama + OpenAI o3

Controls
--------
W A S D : Move Link
Space/Z : Sword attack
Esc/Q   : Quit

Everything is generated in code – no external images or sound files.
"""
import sys, random, math, array
import pygame as pg

# ───────────────────────── Configuration ──────────────────────────
TILE          = 32                              # each NES tile → 32×32 px
ROOM_W,ROOM_H = 16, 11                          # classic Zelda grid
VIEW_W,VIEW_H = TILE*ROOM_W, TILE*ROOM_H
UI_H          = 64
WIDTH,HEIGHT  = VIEW_W, VIEW_H+UI_H

FPS           = 60
LINK_SPEED    = 2.4
SWORD_TIME    = 200                             # ms visible
SWORD_LEN     = 20
ENEMY_SPEED   = 1.2
OCTOROK_COOLDOWN = 40                           # frames between dir changes

PALETTE_BG    = (4, 60, 20)
PAL_LINK      = (40, 200, 40)
PAL_SWORD     = (240, 240, 200)
PAL_ENEMY     = (200, 40, 40)
PAL_WALL      = (60, 100, 120)
PAL_DOOR      = (180, 140, 60)
PAL_HEART     = (230, 30, 70)
PAL_RUPEE     = (40, 220, 220)
PAL_TEXT      = (255, 255, 255)
CRT_ALPHA     = 60

# ───────────────────────── Helpers ────────────────────────────────
def make_wave(freq=440, dur=0.08, vol=0.4, sr=44100, duty=0.5):
    n = int(sr*dur)
    buf = array.array("h")
    amp = int(vol*32767)
    step = sr/freq
    for i in range(n):
        buf.append(amp if (i%step)/step<duty else -amp)
    return pg.mixer.Sound(buffer=buf.tobytes())

def now(): return pg.time.get_ticks()

def rect_for_tile(tx, ty):
    return pg.Rect(tx*TILE, ty*TILE, TILE, TILE)

# ───────────────────────── Entities ───────────────────────────────
class Entity:
    def __init__(self, x, y, w, h):
        self.rect = pg.Rect(x, y, w, h)
        self.alive = True
    def update(self, game): pass
    def draw(self, surf): pass

class Link(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20)
        self.hp, self.max_hp = 3, 3
        self.dir = pg.Vector2(0, -1)
        self.attacking = False
        self.attack_end = 0
    def update(self, game):
        keys = pg.key.get_pressed()
        vel = pg.Vector2(
            (keys[pg.K_d]-keys[pg.K_a]),
            (keys[pg.K_s]-keys[pg.K_w]))
        if vel.length_squared(): vel.scale_to_length(LINK_SPEED)
        # collision
        next_rect = self.rect.move(vel)
        for wall in game.room.walls:
            if next_rect.colliderect(wall):
                if vel.x>0: next_rect.right = wall.left
                if vel.x<0: next_rect.left  = wall.right
                if vel.y>0: next_rect.bottom= wall.top
                if vel.y<0: next_rect.top   = wall.bottom
        self.rect = next_rect
        if vel.length_squared(): self.dir = vel.normalize()
        # sword attack
        if not self.attacking and (keys[pg.K_SPACE] or keys[pg.K_z]):
            self.attacking = True
            self.attack_end = now()+SWORD_TIME
            game.sfx_swing.play()
            # sword rect extends from link
            tip = self.rect.center + self.dir*SWORD_LEN
            self.sword_rect = pg.Rect(0,0,SWORD_LEN,4)
            if abs(self.dir.x)>abs(self.dir.y):
                # horizontal
                self.sword_rect.size = (SWORD_LEN,4)
                self.sword_rect.center = (tip.x, self.rect.centery)
                if self.dir.x<0: self.sword_rect.right = self.rect.left
                else: self.sword_rect.left = self.rect.right
            else:
                self.sword_rect.size = (4,SWORD_LEN)
                self.sword_rect.center = (self.rect.centerx, tip.y)
                if self.dir.y<0: self.sword_rect.bottom = self.rect.top
                else: self.sword_rect.top = self.rect.bottom
            # hit enemies
            for e in list(game.room.enemies):
                if self.sword_rect.colliderect(e.rect):
                    e.alive=False
                    game.spawn_pickup(e.rect.center)
                    game.sfx_enemy.play()
            if not game.room.enemies and game.room.locked:
                game.room.locked=False
                game.sfx_unlock.play()
        if self.attacking and now()>self.attack_end:
            self.attacking=False
    def draw(self, surf):
        pg.draw.rect(surf, PAL_LINK, self.rect)
        if self.attacking:
            pg.draw.rect(surf, PAL_SWORD, self.sword_rect)

class Octorok(Entity):
    sprites = None
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20)
        self.dir = pg.Vector2(random.choice((-1,1)), 0)
        self.frame=0
    def update(self, game):
        self.frame = (self.frame+1)%OCTOROK_COOLDOWN
        if self.frame==0:
            self.dir = pg.Vector2(random.choice((-1,0,1)),
                                  random.choice((-1,0,1)))
            if self.dir.length_squared()==0: self.dir.y=1
            self.dir.scale_to_length(ENEMY_SPEED)
        nxt = self.rect.move(self.dir)
        # bounce on walls
        hit=False
        for wall in game.room.walls:
            if nxt.colliderect(wall):
                hit=True; break
        if hit: self.dir*=-1
        else: self.rect = nxt
    def draw(self, surf): pg.draw.rect(surf, PAL_ENEMY, self.rect)

class Pickup(Entity):
    def __init__(self, x,y,kind):
        super().__init__(x,y,12,12)
        self.kind=kind
    def draw(self,surf):
        if self.kind=="heart":
            pg.draw.rect(surf, PAL_HEART, self.rect)
        else:
            pg.draw.rect(surf, PAL_RUPEE, self.rect)

# ───────────────────────── Room / Map ─────────────────────────────
class Room:
    """
    layout : list[str] using:
      # = wall
      E = enemy
      H = heart pickup
      R = rupee
      D = locked door (opened when enemies cleared)
      . = floor
    """
    def __init__(self, layout, locked=False, palette=PALETTE_BG):
        self.layout=layout
        self.palette=palette
        self.walls=[]
        self.enemies=[]
        self.pickups=[]
        self.locked=locked
        for y,row in enumerate(layout):
            for x,ch in enumerate(row):
                rx, ry = x*TILE, y*TILE
                if ch=="#":
                    self.walls.append(pg.Rect(rx,ry,TILE,TILE))
                elif ch=="E":
                    self.enemies.append(Octorok(rx+6,ry+6))
                elif ch=="H":
                    self.pickups.append(Pickup(rx+10, ry+10,"heart"))
                elif ch=="R":
                    self.pickups.append(Pickup(rx+10, ry+10,"rupee"))
                elif ch=="D":
                    self.lock_rect=pg.Rect(rx,ry,TILE,TILE)
                    self.locked=True
    def draw(self, surf):
        surf.fill(self.palette)
        for wall in self.walls:
            pg.draw.rect(surf, PAL_WALL, wall)
        if self.locked:
            pg.draw.rect(surf, PAL_DOOR, self.lock_rect)
        for p in self.pickups: p.draw(surf)
        for e in self.enemies: e.draw(surf)

# ───────────────────────── Game ───────────────────────────────────
class Game:
    def __init__(self):
        pg.mixer.pre_init(44100,-16,1,512)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH,HEIGHT))
        pg.display.set_caption("Zelda 1 – Pure Pygame Edition")
        self.clock  = pg.time.Clock()
        self.font   = pg.font.SysFont("Courier", 20, bold=True)
        self._build_crt()
        self._load_sfx()
        self.state = "MENU"
        self.link  = Link(VIEW_W//2, VIEW_H//2)
        self.rupees=0
        self._build_world()
        self.room_pos=(0,0)
        self.room=self.world[self.room_pos]
    # Assets
    def _build_crt(self):
        self.crt = pg.Surface((WIDTH,HEIGHT),pg.SRCALPHA)
        for y in range(0,HEIGHT,2):
            pg.draw.line(self.crt,(0,0,0,CRT_ALPHA),(0,y),(WIDTH,y))
    def _load_sfx(self):
        self.sfx_swing  = make_wave(880,0.05,0.4)
        self.sfx_enemy  = make_wave(220,0.12,0.5)
        self.sfx_pick   = make_wave(660,0.08,0.45)
        self.sfx_unlock = make_wave(440,0.4,0.5)
    # World
    def _build_world(self):
        overworld = [
            "################",
            "#..............#",
            "#..E...........#",
            "#..............#",
            "#......H.......#",
            "#..............#",
            "#...........R..#",
            "#..............#",
            "#..............#",
            "#..............#",
            "################",
        ]
        dungeon = [
            "################",
            "#..............#",
            "#..E.......E...#",
            "#..............#",
            "#......D.......#",
            "#..............#",
            "#..E.......E...#",
            "#..............#",
            "#..............#",
            "#..............#",
            "################",
        ]
        self.world   = {(0,0):Room(overworld, palette=(10,80,20)),
                        (0,1):Room(dungeon, locked=True, palette=(10,10,40))}
    # Spawning
    def spawn_pickup(self,pos):
        kind = random.choice(("heart","rupee"))
        self.room.pickups.append(Pickup(pos[0]-6,pos[1]-6,kind))
    # Main loop
    def run(self):
        while True:
            self._events()
            if self.state=="PLAY": self._update()
            self._draw()
            self.clock.tick(FPS)
    # Input
    def _events(self):
        for e in pg.event.get():
            if e.type==pg.QUIT: pg.quit(); sys.exit()
            if e.type==pg.KEYDOWN and e.key in (pg.K_ESCAPE,pg.K_q):
                pg.quit(); sys.exit()
            if self.state=="MENU" and e.type==pg.KEYDOWN and e.key in (pg.K_RETURN,pg.K_SPACE):
                self.state="PLAY"
    # Update
    def _update(self):
        self.link.update(self)
        # Move enemies
        for e in list(self.room.enemies):
            e.update(self)
            if not e.alive: self.room.enemies.remove(e)
        # Pickups
        for p in list(self.room.pickups):
            if self.link.rect.colliderect(p.rect):
                if p.kind=="heart" and self.link.hp<self.link.max_hp:
                    self.link.hp+=1
                elif p.kind=="rupee":
                    self.rupees+=1
                self.room.pickups.remove(p)
                self.sfx_pick.play()
        # Door collision
        if self.room.locked and self.link.rect.colliderect(self.room.lock_rect):
            # prevent crossing locked door
            if abs(self.link.rect.centery-self.room.lock_rect.centery)<TILE//2:
                if self.link.rect.centerx<self.room.lock_rect.centerx:
                    self.link.rect.right=self.room.lock_rect.left
                else:
                    self.link.rect.left=self.room.lock_rect.right
        # Room transitions
        if self.link.rect.left<0:
            self._change_room(-1,0)
            self.link.rect.left=VIEW_W-1
        elif self.link.rect.right>VIEW_W:
            self._change_room(1,0)
            self.link.rect.right=1
        elif self.link.rect.top<0:
            self._change_room(0,-1)
            self.link.rect.top=VIEW_H-1
        elif self.link.rect.bottom>VIEW_H:
            self._change_room(0,1)
            self.link.rect.bottom=1
    def _change_room(self,dx,dy):
        nxt=(self.room_pos[0]+dx,self.room_pos[1]+dy)
        if nxt in self.world:
            self.room_pos=nxt
            self.room=self.world[nxt]
    # Draw
    def _draw(self):
        if self.state=="MENU":
            self.screen.fill((0,0,0))
            msg = self.font.render("Press Enter to start Zelda‑vibes",True,PAL_TEXT)
            self.screen.blit(msg,msg.get_rect(center=(WIDTH//2,HEIGHT//2)))
            pg.display.flip(); return
        self.room.draw(self.screen.subsurface((0,0,VIEW_W,VIEW_H)))
        self.link.draw(self.screen)
        # UI
        ui = self.screen.subsurface((0,VIEW_H,WIDTH,UI_H))
        ui.fill((0,0,0))
        # hearts
        for i in range(self.link.max_hp):
            col = PAL_HEART if i<self.link.hp else (50,50,50)
            pg.draw.rect(ui,col,pg.Rect(10+i*24,16,20,20))
        # rupees
        r_text = self.font.render(f"Rupees: {self.rupees}",True,PAL_RUPEE)
        ui.blit(r_text,(WIDTH-160,20))
        # CRT
        self.screen.blit(self.crt,(0,0))
        pg.display.flip()

# ───────────────────────── Entry Point ────────────────────────────
if __name__=="__main__":
    Game().run()
