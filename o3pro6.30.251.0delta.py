#!/usr/bin/env python3
"""
Deltarune × Zelda 1  –  Pure‑Pygame Crossover Demo
No PNGs • No external sounds • Just shapes, text, and vibes      (2025)

Controls
--------
W A S D : Move Kris
Space / Z : Slash SOUL‑sword
Enter / Space : Advance dialog / Start game
Esc / Q : Quit
"""
import sys, random, math, array
import pygame as pg

# ─────────────────────────────────────────────
#  GLOBAL CONFIG
# ─────────────────────────────────────────────
TILE                = 32
ROOM_W, ROOM_H      = 16, 11                 # 512×352 play field
VIEW_W, VIEW_H      = TILE*ROOM_W, TILE*ROOM_H
UI_H                = 80
WIDTH, HEIGHT       = VIEW_W, VIEW_H+UI_H
FPS                 = 60

# Player / combat
KRIS_SPEED          = 2.8
SWORD_LEN           = 22
SWORD_TIME          = 200                    # ms
INVULN_TIME         = 800                    # ms after hit
MAX_HP              = 5

# Boss
SPAMTON_HP          = 12
SPAMTON_BULLET_SPD  = 3.2
SPAMTON_FIRE_CD     = 600                    # ms

# Colours (NES / Deltarune palette mash)
PAL_BG              = (8, 8, 16)
PAL_WALL            = (40, 40, 80)
PAL_FLOOR           = (14, 14, 40)
PAL_KRIS            = (30, 90, 230)
PAL_SUSIE           = (160, 60, 160)
PAL_RALSEI          = (40, 200, 80)
PAL_SWORD           = (250, 250, 230)
PAL_HEART           = (230, 50, 70)
PAL_RUPEE           = (40, 220, 220)
PAL_SPAMTON         = (250, 250, 0)
PAL_BULLET          = (255, 200, 200)
PAL_TEXT            = (255, 255, 255)

CRT_ALPHA           = 60                     # scan‐line strength

# ─────────────────────────────────────────────
#  UTILS
# ─────────────────────────────────────────────
def make_wave(freq=440, dur=0.08, vol=0.4, sr=44100, duty=0.5):
    n = int(sr*dur)
    buf, amp, step = array.array("h"), int(vol*32767), sr/freq
    for i in range(n):
        buf.append(amp if (i%step)/step < duty else -amp)
    return pg.mixer.Sound(buffer=buf.tobytes())

def now() -> int:
    return pg.time.get_ticks()

def clamp(n, lo, hi): return max(lo, min(hi, n))

# ─────────────────────────────────────────────
#  ENTITY BASE
# ─────────────────────────────────────────────
class Entity:
    def __init__(self, x, y, w, h):
        self.rect = pg.Rect(x, y, w, h)
        self.alive = True
    def update(self, game): pass
    def draw(self, surf): pass

# ─────────────────────────────────────────────
#  PLAYER – KRIS
# ─────────────────────────────────────────────
class Kris(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 22, 26)
        self.hp = MAX_HP
        self.invuln_until = 0
        self.dir = pg.Vector2(0, -1)
        self.attacking = False
        self.attack_until = 0
        self.sword_rect = pg.Rect(0,0,0,0)
    # -----------------------------------------
    def update(self, game):
        keys = pg.key.get_pressed()
        vel = pg.Vector2(keys[pg.K_d]-keys[pg.K_a],
                         keys[pg.K_s]-keys[pg.K_w])
        if vel.length_squared():
            vel.scale_to_length(KRIS_SPEED)
            self.dir = vel.normalize()
        nxt = self.rect.move(vel)
        # collide with walls
        for wall in game.room.walls:
            if nxt.colliderect(wall): break
        else:
            self.rect = nxt
        # sword
        if not self.attacking and (keys[pg.K_SPACE] or keys[pg.K_z]):
            self.slash(game)
        if self.attacking and now() > self.attack_until:
            self.attacking = False
    # -----------------------------------------
    def slash(self, game):
        self.attacking = True
        self.attack_until = now() + SWORD_TIME
        game.sfx_swing.play()
        # build sword rect
        tip = pg.Vector2(self.rect.center) + self.dir * SWORD_LEN
        if abs(self.dir.x) > abs(self.dir.y):           # horiz slash
            self.sword_rect.size = (SWORD_LEN, 4)
            self.sword_rect.center = (tip.x, self.rect.centery)
            if self.dir.x < 0: self.sword_rect.right = self.rect.left
            else:              self.sword_rect.left  = self.rect.right
        else:                                          # vertical slash
            self.sword_rect.size = (4, SWORD_LEN)
            self.sword_rect.center = (self.rect.centerx, tip.y)
            if self.dir.y < 0: self.sword_rect.bottom = self.rect.top
            else:              self.sword_rect.top    = self.rect.bottom
        # damage enemies / boss
        for e in list(game.room.enemies):
            if self.sword_rect.colliderect(e.rect):
                e.hit(game)
        if game.room.boss and self.sword_rect.colliderect(game.room.boss.rect):
            game.room.boss.hit(game)
    # -----------------------------------------
    def hit(self, dmg, game):
        if now() < self.invuln_until: return
        self.hp -= dmg
        self.invuln_until = now()+INVULN_TIME
        game.sfx_hurt.play()
        if self.hp <= 0:
            game.state = "GAME_OVER"
            game.state_time = now()
    # -----------------------------------------
    def draw(self, surf):
        pg.draw.rect(surf, PAL_KRIS, self.rect)
        if self.attacking:
            pg.draw.rect(surf, PAL_SWORD, self.sword_rect)

# ─────────────────────────────────────────────
#  NPCs – SUSIE & RALSEI (Static Cameos)
# ─────────────────────────────────────────────
class NPC(Entity):
    def __init__(self, x, y, colour, label):
        super().__init__(x, y, 22, 26)
        self.colour, self.label = colour, label
    def draw(self, surf):
        pg.draw.rect(surf, self.colour, self.rect)

# ─────────────────────────────────────────────
#  ENEMY  – Simple Rudinn‑like baddie
# ─────────────────────────────────────────────
class Rudinn(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20)
        self.dir = pg.Vector2(random.choice((-1,1)), 0)
    def update(self, game):
        nxt = self.rect.move(self.dir)
        # bounce off walls
        hit=False
        for w in game.room.walls:
            if nxt.colliderect(w): hit=True; break
        if hit: self.dir.x *= -1
        else:   self.rect = nxt
    def hit(self, game):
        self.alive=False
        game.room.enemies.remove(self)
        game.spawn_pickup(self.rect.center)
        game.sfx_enemy.play()
        if not game.room.enemies and game.room.locked:
            game.unlock_doors()
    def draw(self, surf):
        pg.draw.rect(surf, (180,180,255), self.rect)

# ─────────────────────────────────────────────
#  BOSS  – SPAMTON
# ─────────────────────────────────────────────
class Spamton(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 36, 44)
        self.max_hp = SPAMTON_HP
        self.hp = SPAMTON_HP
        self.dir = 1
        self.last_fire = now()
    # -----------------------------------------
    def update(self, game):
        self.rect.x += self.dir*2
        if self.rect.right > VIEW_W-8:
            self.dir=-1
        elif self.rect.left < 8:
            self.dir=1
        if now()-self.last_fire > SPAMTON_FIRE_CD:
            self.last_fire = now()
            self.fire(game)
    # -----------------------------------------
    def fire(self, game):
        # shoot downward bullet towards Kris
        kx, ky = game.kris.rect.center
        dx, dy = kx - self.rect.centerx, ky - self.rect.bottom
        direction = pg.Vector2(dx, dy).normalize()
        vel = direction * SPAMTON_BULLET_SPD
        game.room.bullets.append(Bullet(self.rect.center, vel))
        game.sfx_blip.play()
    # -----------------------------------------
    def hit(self, game):
        self.hp -= 1
        game.sfx_hit.play()
        if self.hp <= 0:
            self.alive=False
            game.room.boss=None
            game.state="WIN"
            game.state_time=now()
    def draw(self, surf):
        pg.draw.rect(surf, PAL_SPAMTON, self.rect)
        # tiny face – smile
        eye_y = self.rect.y+10
        pg.draw.circle(surf, (0,0,0), (self.rect.x+10, eye_y), 2)
        pg.draw.circle(surf, (0,0,0), (self.rect.x+26, eye_y), 2)
        pg.draw.line   (surf, (0,0,0), (self.rect.x+8, eye_y+8),
                                          (self.rect.x+28, eye_y+8), 2)

# ─────────────────────────────────────────────
#  PROJECTILE
# ─────────────────────────────────────────────
class Bullet(Entity):
    def __init__(self, pos, vel):
        super().__init__(pos[0]-4, pos[1]-4, 8, 8)
        self.vel = vel
    def update(self, game):
        self.rect.x += int(self.vel.x)
        self.rect.y += int(self.vel.y)
        if not self.rect.colliderect(pg.Rect(0,0,VIEW_W,VIEW_H)):
            self.alive=False
        elif self.rect.colliderect(game.kris.rect):
            self.alive=False
            game.kris.hit(1, game)
    def draw(self,surf):
        pg.draw.rect(surf, PAL_BULLET, self.rect)

# ─────────────────────────────────────────────
#  PICKUP – HEARTS or RUPEES
# ─────────────────────────────────────────────
class Pickup(Entity):
    def __init__(self, x, y, kind):
        super().__init__(x, y, 14, 14)
        self.kind = kind
    def collect(self, game):
        if self.kind=="heart" and game.kris.hp < MAX_HP:
            game.kris.hp += 1
        elif self.kind=="rupee":
            game.rupees += 1
        game.sfx_pick.play()
        self.alive=False
    def draw(self, surf):
        col = PAL_HEART if self.kind=="heart" else PAL_RUPEE
        pg.draw.rect(surf, col, self.rect)

# ─────────────────────────────────────────────
#  ROOM
# ─────────────────────────────────────────────
class Room:
    """
    Simple text layout:
      # = wall
      R = Rudinn
      S = Susie
      T = Ralsei (heh)
      B = Boss Spamton
      H = heart pickup
      U = rupee pickup
      D = locked door tile
      . = floor

    """
    def __init__(self, layout, palette=PAL_FLOOR, locked=False):
        self.layout = layout
        self.palette = palette
        self.locked = locked
        self.walls, self.enemies, self.npcs, self.pickups = [], [], [], []
        self.boss = None
        self.bullets=[]
        for y,row in enumerate(layout):
            for x,ch in enumerate(row):
                rx, ry = x*TILE, y*TILE
                if ch=="#": self.walls.append(pg.Rect(rx,ry,TILE,TILE))
                elif ch=="R": self.enemies.append(Rudinn(rx+6,ry+6))
                elif ch=="S": self.npcs.append(NPC(rx+4,ry+4, PAL_SUSIE,"Susie"))
                elif ch=="T": self.npcs.append(NPC(rx+4,ry+4, PAL_RALSEI,"Ralsei"))
                elif ch=="H": self.pickups.append(Pickup(rx+9,ry+9,"heart"))
                elif ch=="U": self.pickups.append(Pickup(rx+9,ry+9,"rupee"))
                elif ch=="B": self.boss = Spamton(rx+TILE//2, ry+TILE//2)
                elif ch=="D": self.lock_rect = pg.Rect(rx,ry,TILE,TILE); self.locked=True
    # -----------------------------------------
    def unlock(self): self.locked=False
    def draw(self, surf):
        surf.fill(self.palette)
        for w in self.walls: pg.draw.rect(surf, PAL_WALL, w)
        for p in self.pickups: p.draw(surf)
        for n in self.npcs: n.draw(surf)
        for e in self.enemies: e.draw(surf)
        if self.boss: self.boss.draw(surf)
        for b in self.bullets: b.draw(surf)
        if self.locked: pg.draw.rect(surf, (180,120,40), self.lock_rect)

# ─────────────────────────────────────────────
#  GAME – State machine & main loop
# ─────────────────────────────────────────────
class Game:
    def __init__(self):
        pg.mixer.pre_init(44100,-16,1,512)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH,HEIGHT))
        pg.display.set_caption("Deltarune × Zelda – Pure‑Pygame Crossover")
        self.clock = pg.time.Clock()
        self.font  = pg.font.SysFont("Courier", 22, bold=True)
        self._build_crt()
        self._load_sfx()
        self.reset_world()
        self.state = "MENU"
        self.state_time = now()
    # -----------------------------------------
    def _build_crt(self):
        self.crt = pg.Surface((WIDTH,HEIGHT), pg.SRCALPHA)
        for y in range(0,HEIGHT,2):
            pg.draw.line(self.crt, (0,0,0,CRT_ALPHA), (0,y), (WIDTH,y))
    # -----------------------------------------
    def _load_sfx(self):
        self.sfx_swing = make_wave(880,0.05,0.5)
        self.sfx_hit   = make_wave(200,0.12,0.6)
        self.sfx_enemy = make_wave(300,0.1,0.5)
        self.sfx_pick  = make_wave(660,0.08,0.5)
        self.sfx_blip  = make_wave(440,0.06,0.5)
        self.sfx_hurt  = make_wave(160,0.2,0.6)
        self.sfx_unlock= make_wave(520,0.4,0.5)
    # -----------------------------------------
    def reset_world(self):
        # -- Overworld room (0,0)
        ow = [
            "################",
            "#..............#",
            "#..R......R....#",
            "#..............#",
            "#......S....T..#",
            "#..............#",
            "#......H....U..#",
            "#..............#",
            "#..............#",
            "#..............#",
            "################",
        ]
        # -- Boss room (1,0)
        boss = [
            "################",
            "#..............#",
            "#......B.......#",
            "#..............#",
            "#......D.......#",
            "#..............#",
            "#..............#",
            "#..............#",
            "#..............#",
            "#..............#",
            "################",
        ]
        self.world = {(0,0): Room(ow, palette=(12,14,40), locked=False),
                      (1,0): Room(boss, palette=(6,6,24), locked=True)}
        self.room_pos = (0,0)
        self.room = self.world[self.room_pos]
        self.kris = Kris(VIEW_W//2, VIEW_H//2)
        self.rupees = 0
        self.dialog_queue = [
            "Kris woke up in a strange 8‑bit land…",
            "Ralsei  : \"Stay determined!\"",
            "Susie   : \"Let's clobber whatever boss lives here.\"",
            "— PRESS ENTER —"
        ]
        self.state="DIALOG"
    # ─────────────────────────────────────────
    #  WORLD HELPERS
    # ─────────────────────────────────────────
    def spawn_pickup(self, pos):
        kind = random.choice(("heart","rupee"))
        self.room.pickups.append(Pickup(pos[0]-7,pos[1]-7,kind))
    def unlock_doors(self):
        if self.room.locked:
            self.room.unlock()
            self.sfx_unlock.play()
    # ─────────────────────────────────────────
    #  MAIN LOOP
    # ─────────────────────────────────────────
    def run(self):
        while True:
            self._events()
            if self.state=="PLAY": self._update_play()
            elif self.state=="DIALOG": self._update_dialog()
            self._draw()
            self.clock.tick(FPS)
    # ─────────────────────────────────────────
    #  INPUT
    # ─────────────────────────────────────────
    def _events(self):
        for e in pg.event.get():
            if e.type==pg.QUIT: pg.quit(); sys.exit()
            if e.type==pg.KEYDOWN and e.key in (pg.K_ESCAPE, pg.K_q):
                pg.quit(); sys.exit()
            if self.state=="MENU" and e.type==pg.KEYDOWN:
                self.state="DIALOG"
            elif self.state=="DIALOG" and e.type==pg.KEYDOWN:
                if self.dialog_queue: self.dialog_queue.pop(0)
                if not self.dialog_queue:
                    self.state="PLAY"
            elif self.state in ("WIN","GAME_OVER") and e.type==pg.KEYDOWN:
                self.reset_world()
    # ─────────────────────────────────────────
    #  UPDATE – PLAY
    # ─────────────────────────────────────────
    def _update_play(self):
        self.kris.update(self)
        # enemies
        for e in list(self.room.enemies):
            e.update(self)
        # boss
        if self.room.boss:
            self.room.boss.update(self)
        # bullets
        for b in list(self.room.bullets):
            b.update(self)
        # cleanup
        self.room.enemies = [e for e in self.room.enemies if e.alive]
        self.room.bullets = [b for b in self.room.bullets if b.alive]
        self.room.pickups = [p for p in self.room.pickups if p.alive]
        # pickups collision
        for p in list(self.room.pickups):
            if self.kris.rect.colliderect(p.rect):
                p.collect(self)
        # door blocking
        if self.room.locked and self.kris.rect.colliderect(self.room.lock_rect):
            if self.kris.rect.centery < self.room.lock_rect.centery:
                self.kris.rect.bottom = self.room.lock_rect.top-1
            else:
                self.kris.rect.top = self.room.lock_rect.bottom+1
        # room transition (right only for demo)
        if self.kris.rect.right > VIEW_W:
            nxt = (self.room_pos[0]+1, self.room_pos[1])
            if nxt in self.world and not self.room.locked:
                self.room_pos = nxt
                self.room = self.world[nxt]
                self.kris.rect.left = 1
        elif self.kris.rect.left < 0:
            nxt = (self.room_pos[0]-1, self.room_pos[1])
            if nxt in self.world:
                self.room_pos = nxt
                self.room = self.world[nxt]
                self.kris.rect.right = VIEW_W-1
    # ─────────────────────────────────────────
    #  UPDATE – DIALOG
    # ─────────────────────────────────────────
    def _update_dialog(self):
        pass    # nothing to tick; waits for key press
    # ─────────────────────────────────────────
    #  DRAW
    # ─────────────────────────────────────────
    def _draw(self):
        if self.state=="MENU":
            self.screen.fill((0,0,0))
            txt = self.font.render("Press any key to Begin the Crossover",True,PAL_TEXT)
            self.screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2)))
            pg.display.flip(); return
        # main playfield
        self.room.draw(self.screen.subsurface((0,0,VIEW_W,VIEW_H)))
        self.kris.draw(self.screen)
        # UI bar
        ui = self.screen.subsurface((0,VIEW_H,WIDTH,UI_H))
        ui.fill((0,0,0))
        # hearts
        for i in range(MAX_HP):
            col = PAL_HEART if i < self.kris.hp else (60,60,60)
            pg.draw.rect(ui, col, pg.Rect(12+i*24, 18, 20, 20))
        # rupees
        rtxt = self.font.render(f"Rupees: {self.rupees}", True, PAL_RUPEE)
        ui.blit(rtxt, (WIDTH-180, 22))
        # state overlays
        if self.state=="DIALOG":
            self._draw_dialog_overlay()
        elif self.state=="WIN":
            self._draw_center_text("YOU WIN! Spamton became a [BIG LOSS].")
        elif self.state=="GAME_OVER":
            self._draw_center_text("GAME OVER – Kris was defeated.")
        # CRT
        self.screen.blit(self.crt, (0,0))
        pg.display.flip()
    # -----------------------------------------
    def _draw_center_text(self, text):
        overlay = pg.Surface((WIDTH,HEIGHT), pg.SRCALPHA)
        overlay.fill((0,0,0, 180))
        self.screen.blit(overlay,(0,0))
        t = self.font.render(text, True, PAL_TEXT)
        sub = self.font.render("Press any key to restart", True, PAL_TEXT)
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2-10)))
        self.screen.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//2+26)))
    # -----------------------------------------
    def _draw_dialog_overlay(self):
        if not self.dialog_queue: return
        box = pg.Surface((WIDTH-100, 120))
        box.fill((0,0,0))
        pg.draw.rect(box, PAL_TEXT, box.get_rect(), 2)
        lines = self.dialog_queue[0].split("\n")
        for i,l in enumerate(lines):
            txt = self.font.render(l, True, PAL_TEXT)
            box.blit(txt, (16, 12+i*26))
        self.screen.blit(box, box.get_rect(center=(WIDTH//2, HEIGHT-UI_H//2-40)))
# ─────────────────────────────────────────────
#  ENTRY
# ─────────────────────────────────────────────
if __name__ == "__main__":
    Game().run()
