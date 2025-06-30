#!/usr/bin/env python3
"""
Deltarune – Hometown Night Stroll
Pure‑Pygame • No external assets • Vibes only                     (2025)

Controls
--------
W A S D        : Move Kris
E / Space      : Interact / advance dialog
Esc / Q        : Quit
"""
import sys, math, random, array
import pygame as pg

# ───────────────────────── Config ─────────────────────────
WIDTH, HEIGHT      = 640, 480
FPS                = 60
TILE               = 32
PLAYER_SPEED       = 2.8
NPC_SPEED          = 1.2
DIALOG_WIDTH       = WIDTH - 40
CRT_ALPHA          = 70

# Colours (night blues & DR palette mash)
C_NIGHT_BG   = (10, 12, 28)
C_STREET     = (20, 24, 50)
C_HOUSE      = (40, 44, 80)
C_DOOR       = (120, 100, 60)
C_WINDOW     = (240, 200, 60)
C_TEXT       = (220, 220, 240)
C_KRIS       = (30, 90, 230)
C_SUSIE      = (160, 60, 160)
C_NOELLE     = (220, 220, 60)
C_TORIEL     = (240, 240, 200)
PORTRAITS    = {"Kris":C_KRIS, "Susie":C_SUSIE, "Noelle":C_NOELLE, "Toriel":C_TORIEL}

# ───────────────────────── Util – audio ───────────────────
def make_wave(freq=440, dur=0.1, vol=0.4, sr=22050, duty=0.5):
    n = int(sr*dur)
    buf, amp, step = array.array("h"), int(vol*32767), sr/freq
    for i in range(n):
        buf.append(amp if (i%step)/step<duty else -amp)
    return pg.mixer.Sound(buffer=buf.tobytes())

# ───────────────────────── Tile world ─────────────────────
class World:
    """
    Simple rectangular map built from rectangles, no tilesheet needed.
    Houses/fences are solid; doors have separate interact hit‑boxes.
    """
    def __init__(self):
        # scrollable area (px)
        self.w, self.h = 50*TILE, 25*TILE
        # static obstacles
        self.solids = []
        self.doors  = []     # (rect, id string)
        self._build()

    def _house(self, x, y, w, h, door_id=None):
        r = pg.Rect(x, y, w, h)
        self.solids.append(r)
        # windows
        for wy in (y+12, y+h-28):
            pg.draw.rect(self._dummy, C_WINDOW, (x+10, wy, 20,12))
            pg.draw.rect(self._dummy, C_WINDOW, (x+w-30, wy, 20,12))
        # door
        if door_id:
            dr = pg.Rect(x+w//2-12, y+h-28, 24, 28)
            self.doors.append((dr, door_id))
            self.solids.append(pg.Rect(x, y, w, h-28))  # main walls

    def _build(self):
        # dummy surface for windows pass
        self._dummy = pg.Surface((self.w, self.h))
        # street rectangle = non‑solid
        # big central street coords kept for drawing
        self.street = pg.Rect(0, 8*TILE, self.w, 9*TILE)
        # fences top & bottom
        self.solids.append(pg.Rect(0, 7*TILE, self.w, TILE//2))
        self.solids.append(pg.Rect(0, 17*TILE, self.w, TILE//2))
        # houses
        self._house(4*TILE, 9*TILE, 6*TILE, 6*TILE, "kris_home")
        self._house(13*TILE, 9*TILE, 6*TILE, 6*TILE, "noelle_home")
        self._house(22*TILE, 9*TILE, 6*TILE, 6*TILE, "sans_diner")
        # extra scenery (mailbox etc. could be drawn later)

    # drawing is handled by Game._draw_world

# ───────────────────────── Entities ───────────────────────
class Entity:
    def __init__(self, x, y, w, h):
        self.rect = pg.Rect(x, y, w, h)
        self.vel  = pg.Vector2(0,0)
    def update(self, world): pass
    def draw(self, surf, cam): pass

class Kris(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 26)
        self.facing = pg.Vector2(0,1)
    def update(self, world, keys):
        self.vel.xy = (keys[pg.K_d]-keys[pg.K_a],
                       keys[pg.K_s]-keys[pg.K_w])
        if self.vel.length_squared():
            self.vel.scale_to_length(PLAYER_SPEED)
            self.facing = self.vel.normalize()
        nxt = self.rect.move(self.vel)
        for s in world.solids:
            if nxt.colliderect(s):
                if self.vel.x>0: nxt.right = s.left
                if self.vel.x<0: nxt.left  = s.right
                if self.vel.y>0: nxt.bottom= s.top
                if self.vel.y<0: nxt.top   = s.bottom
        self.rect = nxt
        # keep inside world
        self.rect.clamp_ip(pg.Rect(0,0,world.w,world.h))

    def draw(self, surf, cam):
        pg.draw.rect(surf, C_KRIS, self.rect.move(-cam.x,-cam.y))

class WanderNPC(Entity):
    def __init__(self, x,y,w,h,col,name,dialog,path_x=None):
        super().__init__(x,y,w,h)
        self.col,self.name,self.dialog=col,name,dialog
        self.dir=1; self.path_x=path_x
    def update(self, world):
        if self.path_x:
            self.rect.x += self.dir*NPC_SPEED
            if self.rect.x<self.path_x[0] or self.rect.x>self.path_x[1]:
                self.dir*=-1
    def draw(self,surf,cam):
        pg.draw.rect(surf,self.col,self.rect.move(-cam.x,-cam.y))

# ───────────────────────── Dialog box ─────────────────────
class DialogBox:
    def __init__(self, font):
        self.font=font
        self.active=False
    def open(self, speaker, text):
        self.active=True
        self.speaker=speaker
        self.lines = self._wrap(text, 46)
        self.idx=0
    def _wrap(self,txt,width):
        words=txt.split(); lines=[]; cur=""
        for w in words:
            if len(cur)+len(w)+1>width:
                lines.append(cur); cur=w
            else: cur=cur+" "+w if cur else w
        if cur: lines.append(cur)
        return lines
    def advance(self):
        self.idx+=1
        if self.idx>=len(self.lines): self.active=False
    def draw(self,surf):
        if not self.active: return
        # box
        h=100; rect=pg.Rect((WIDTH-DIALOG_WIDTH)//2, HEIGHT-h-10,
                            DIALOG_WIDTH, h)
        pg.draw.rect(surf,(0,0,0),rect)
        pg.draw.rect(surf,C_TEXT,rect,2)
        # portrait bar
        pg.draw.rect(surf, PORTRAITS.get(self.speaker,C_TEXT),
                     (rect.x+4,rect.y+4,12,h-8))
        # text
        txt = self.font.render(f"{self.speaker}:",True,C_TEXT)
        surf.blit(txt,(rect.x+20,rect.y+8))
        dialog = self.font.render(self.lines[self.idx],True,C_TEXT)
        surf.blit(dialog,(rect.x+20,rect.y+40))

# ───────────────────────── Game ───────────────────────────
class Game:
    def __init__(self):
        pg.mixer.pre_init(22050,-16,1,256)
        pg.init()
        self.screen=pg.display.set_mode((WIDTH,HEIGHT))
        pg.display.set_caption("Hometown – Night Stroll")
        self.clock=pg.time.Clock()
        self.font=pg.font.SysFont("Courier",18,True)
        self.world=World()
        # Entities
        self.kris=Kris(6*TILE, 12*TILE)
        self.npcs=[
            WanderNPC(18*TILE, 12*TILE,20,28,C_SUSIE,"Susie",
                      "Yo Kris! Night stroll? Nice.", (15*TILE,21*TILE)),
            WanderNPC(14*TILE+10, 10*TILE,20,26,C_NOELLE,"Noelle",
                      "H‑hi Kris... Beautiful night, isn't it?", None)
        ]
        # dialog
        self.dialog=DialogBox(self.font)
        # synth SFX
        self.sfx_step = make_wave(440,0.05,0.3,duty=0.3)
        self.sfx_blip = make_wave(660,0.05,0.35)
        self.ambient  = make_wave(110,0.8,0.05,duty=0.1)
        self.ambient.play(-1)
        # CRT overlay
        self.crt=self._crt()
        # camera
        self.cam=pg.Vector2(0,0)

    def _crt(self):
        surf=pg.Surface((WIDTH,HEIGHT),pg.SRCALPHA)
        for y in range(0,HEIGHT,2):
            pg.draw.line(surf,(0,0,0,CRT_ALPHA),(0,y),(WIDTH,y))
        return surf

    # ───────────── main loop ─────────────
    def run(self):
        while True:
            self._events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

    # ───────────── input ─────────────
    def _events(self):
        for e in pg.event.get():
            if e.type==pg.QUIT: pg.quit(); sys.exit()
            if e.type==pg.KEYDOWN and e.key in (pg.K_ESCAPE,pg.K_q):
                pg.quit(); sys.exit()
            # dialog advance
            if self.dialog.active and e.type==pg.KEYDOWN and \
               e.key in (pg.K_e, pg.K_SPACE):
                self.dialog.advance()
            # try interact
            elif not self.dialog.active and e.type==pg.KEYDOWN and \
                 e.key in (pg.K_e, pg.K_SPACE):
                self._try_interact()

    # ───────────── game logic ─────────────
    def _update(self):
        keys=pg.key.get_pressed()
        if not self.dialog.active:
            prev=self.kris.rect.topleft
            self.kris.update(self.world, keys)
            if self.kris.rect.topleft!=prev and pg.time.get_ticks()%120==0:
                self.sfx_step.play()
        for n in self.npcs: n.update(self.world)
        # camera follow
        self.cam.x = clamp(self.kris.rect.centerx-WIDTH//2,0,self.world.w-WIDTH)
        self.cam.y = clamp(self.kris.rect.centery-HEIGHT//2,0,self.world.h-HEIGHT)

    def _try_interact(self):
        # NPCs
        for n in self.npcs:
            if n.rect.colliderect(self.kris.rect.inflate(20,20)):
                self.dialog.open(n.name, n.dialog)
                self.sfx_blip.play()
                return
        # doors
        for door, did in self.world.doors:
            if door.colliderect(self.kris.rect.inflate(10,10)):
                if did=="kris_home":
                    self.dialog.open("Toriel",
                        "Kris, you should be sleeping, not wandering!")
                elif did=="noelle_home":
                    self.dialog.open("Noelle",
                        "Oh! Kris, good evening... sorry the house is a mess.")
                elif did=="sans_diner":
                    self.dialog.open("??",
                        "the store is closed, kid. come back some other life.")
                self.sfx_blip.play()
                return

    # ───────────── render ─────────────
    def _draw_world(self, surface):
        surface.fill(C_NIGHT_BG)
        # street
        pg.draw.rect(surface, C_STREET,
                     self.world.street.move(-self.cam.x,-self.cam.y))
        # houses
        for s in self.world.solids:
            pg.draw.rect(surface, C_HOUSE,
                         s.move(-self.cam.x,-self.cam.y))
        # windows already mocked on dummy; we redraw quickly for vibe
        for door,_ in self.world.doors:
            d=door.move(-self.cam.x,-self.cam.y)
            pg.draw.rect(surface, C_DOOR, d)
        # fences top/bottom (thin)
        pg.draw.rect(surface, (60,60,100),
                     pg.Rect(0,7*TILE-self.cam.y, self.world.w,4))
        pg.draw.rect(surface, (60,60,100),
                     pg.Rect(0,17*TILE-self.cam.y, self.world.w,4))

    def _draw(self):
        self._draw_world(self.screen)
        # entities
        for n in self.npcs: n.draw(self.screen,self.cam)
        self.kris.draw(self.screen,self.cam)
        # dialog
        self.dialog.draw(self.screen)
        # CRT overlay
        self.screen.blit(self.crt,(0,0))
        pg.display.flip()

# ───────────────────────── entry ──────────────────────────
def clamp(n, lo, hi): return max(lo,min(n,hi))

if __name__=="__main__":
    Game().run()
