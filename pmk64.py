
"""
KOOPA ENGINE 64 — single-file, no-asset, 60 FPS Paper‑Mario‑style engine
-----------------------------------------------------------------------------
This is an ORIGINAL homage engine (not affiliated with Nintendo) that recreates
the *feel* of timed hits, action commands, partner moves, and an overworld->
battle flow — using only shapes, text, and synthesized UI. No external files.

How to run (local):
  1) pip install pygame
  2) python koopa_engine_64.py

Controls:
  Overworld:  Arrows / WASD to move, ESC to quit
  Battle:     Arrow keys to pick a command, ENTER/Z to confirm, X to back
              Action Command key is Z (press with timing / mash when prompted)
              Guard during enemy attacks with Z when the "!" flashes
  Global:     F1 toggles "Vibes Mode" (simple ambient wobble/scanlines)

Notes:
  * 60 FPS fixed loop via pygame.time.Clock().
  * Single file. No images, no audio assets. Optional tone synthesis inline.
  * Small but complete vertical slice: Title -> Map -> Battle -> Victory -> Map.
  * Expandable data tables for enemies, moves, badges.
"""

import pygame, random, math, sys, time
from dataclasses import dataclass, field

# ---------- Config ----------
W, H = 960, 540
TILE = 48
FPS = 60
GAME_TITLE = "KOOPA ENGINE 64 — single-file 60 FPS"

# Colors
BLACK = (10, 12, 14)
WHITE = (240, 240, 245)
GRAY  = (60, 64, 70)
SILVER= (160, 168, 180)
RED   = (220, 60, 60)
GREEN = (60, 220, 130)
CYAN  = (64, 200, 240)
YELLOW= (240, 220, 80)
ORANGE= (252, 150, 80)
PINK  = (255, 120, 170)
VIOLET= (170, 120, 255)

# ---------- Init ----------
pygame.init()
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=256)
    AUDIO_OK = True
except Exception:
    AUDIO_OK = False

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption(GAME_TITLE)
clock  = pygame.time.Clock()
FONT   = pygame.font.Font(None, 28)
FONT_S = pygame.font.Font(None, 22)
FONT_B = pygame.font.Font(None, 56)

# ---------- Tiny tone synth (square wave) ----------
def make_tone(freq=440, ms=120, vol=0.3):
    """Return a pygame Sound with a simple square wave. No numpy required."""
    if not AUDIO_OK:
        return None
    rate = 22050
    n = int(rate * (ms / 1000.0))
    amp = int(vol * 32767)
    buf = bytearray()
    period = int(rate / max(1, int(freq)))
    half = max(1, period // 2)
    s = amp
    cnt = 0
    for i in range(n):
        # simple square by flipping every half period
        if cnt >= half:
            s = -s
            cnt = 0
        cnt += 1
        buf += int(s).to_bytes(2, byteorder="little", signed=True)
    try:
        return pygame.mixer.Sound(buffer=bytes(buf))
    except Exception:
        return None

SFX_TICK   = make_tone(880, 60, 0.25)
SFX_HIT    = make_tone(220, 90, 0.35)
SFX_GOOD   = make_tone(1200, 100, 0.28)
SFX_GREAT  = make_tone(1600, 120, 0.3)
SFX_BLOCK  = make_tone(400, 80, 0.28)
SFX_HURT   = make_tone(180, 120, 0.35)
SFX_WIN    = make_tone(1000, 240, 0.25)

def play(snd):
    if AUDIO_OK and snd is not None:
        snd.play()

# ---------- Helpers ----------
def draw_text(surf, text, x, y, font=FONT, color=WHITE, center=False, shadow=True):
    if shadow:
        img = font.render(text, True, BLACK)
        r = img.get_rect()
        if center: r.center = (x+1, y+1)
        else: r.topleft = (x+1, y+1)
        surf.blit(img, r)
    img = font.render(text, True, color)
    r = img.get_rect()
    if center: r.center = (x, y)
    else: r.topleft = (x, y)
    surf.blit(img, r)

def clamp(v, lo, hi): return max(lo, min(hi, v))

def rect_for_cell(cx, cy, pad=0):
    return pygame.Rect(cx*TILE+pad, cy*TILE+pad, TILE-2*pad, TILE-2*pad)

# ---------- Data ----------
@dataclass
class Stats:
    name: str = "Shellby"
    max_hp: int = 10
    hp: int = 10
    max_fp: int = 5
    fp: int = 5
    atk: int = 1
    defense: int = 0
    level: int = 1
    xp: int = 0
    coins: int = 0

@dataclass
class Move:
    name: str
    fp_cost: int
    type: str  # "timed" or "mash"
    base: int  # base damage
    desc: str = ""
    press_window: float = 0.12   # for timed
    mash_time: float = 1.4       # for mash

# Define a small move set
JUMP = Move("Jump", fp_cost=0, type="timed", base=2, desc="Press Z when the marker hits center.")
SHELL_DASH = Move("Shell Dash", fp_cost=1, type="mash", base=1, desc="Mash Z to power up.")

# A tiny enemy bestiary
ENEMIES = [
    dict(kind="Goombean",  max_hp=8,  atk=2, defense=0, xp=3, coins=2, hue=ORANGE),
    dict(kind="Spikeling",  max_hp=10, atk=3, defense=1, xp=5, coins=3, hue=YELLOW),
    dict(kind="Shybyte",    max_hp=6,  atk=1, defense=0, xp=2, coins=1, hue=PINK),
]

# ---------- Scene system ----------
class Scene:
    def __init__(self, game): self.game = game
    def on_enter(self, **kwargs): pass
    def handle_event(self, e): pass
    def update(self, dt): pass
    def draw(self, s): pass

class Game:
    def __init__(self):
        self.vibes = False
        self.player = Stats()
        self.stack = []
        self.push(TitleScene(self))

    def push(self, scene, **kwargs):
        self.stack.append(scene)
        scene.on_enter(**kwargs)

    def pop(self):
        if self.stack: self.stack.pop()

    def switch(self, scene, **kwargs):
        self.pop()
        self.push(scene, **kwargs)

    def current(self):
        return self.stack[-1] if self.stack else None

    def run(self):
        dt = 0.0
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit(0)
                if e.type == pygame.KEYDOWN and e.key == pygame.K_F1:
                    self.vibes = not self.vibes
                cur = self.current()
                if cur: cur.handle_event(e)
            cur = self.current()
            if cur: cur.update(dt)
            # draw
            screen.fill(BLACK)
            if cur: cur.draw(screen)
            if self.vibes:
                # simple scanlines
                for y in range(0, H, 4):
                    pygame.draw.line(screen, (0,0,0), (0,y), (W,y), 1)
            pygame.display.flip()
            dt = clock.tick(FPS) / 1000.0

# ---------- Title ----------
class TitleScene(Scene):
    def on_enter(self, **kwargs):
        self.t = 0.0

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_z):
            play(SFX_TICK)
            self.game.switch(MapScene(self.game))

    def update(self, dt):
        self.t += dt

    def draw(self, s):
        s.fill((16,18,24))
        draw_text(s, "KOOPA ENGINE 64", W//2, H//2-40, FONT_B, CYAN, center=True)
        draw_text(s, "single-file • 60 FPS • action commands", W//2, H//2+6, FONT, SILVER, center=True)
        c = WHITE if int(self.t*2)%2==0 else SILVER
        draw_text(s, "Press ENTER or Z", W//2, H//2+60, FONT, c, center=True)
        draw_text(s, "F1: Vibes Mode | ESC: Quit", W//2, H-28, FONT_S, GRAY, center=True)

# ---------- Overworld Map ----------
class MapScene(Scene):
    def on_enter(self, **kwargs):
        self.cols = W//TILE
        self.rows = H//TILE
        self.grid = [[0]*self.cols for _ in range(self.rows)]
        # borders
        for y in range(self.rows):
            self.grid[y][0] = self.grid[y][-1] = 1
        for x in range(self.cols):
            self.grid[0][x] = self.grid[-1][x] = 1
        # sparse obstacles
        for _ in range(140):
            x = random.randint(1, self.cols-2)
            y = random.randint(1, self.rows-2)
            if random.random() < 0.14:
                self.grid[y][x] = 1

        # place player and enemies on empty tiles
        def empty_cell():
            while True:
                x = random.randint(1, self.cols-2)
                y = random.randint(1, self.rows-2)
                if self.grid[y][x] == 0:
                    return x, y

        self.px, self.py = empty_cell()
        self.px *= TILE; self.py *= TILE
        self.pvx = self.pvy = 0.0
        self.speed = 210.0

        self.enemies = []
        for _ in range(4):
            ex, ey = empty_cell()
            e = random.choice(ENEMIES).copy()
            e["x"] = ex*TILE + TILE//2
            e["y"] = ey*TILE + TILE//2
            e["dir"] = random.uniform(0, math.tau)
            e["spd"] = 65 + random.random()*40
            e["alive"] = True
            self.enemies.append(e)

        self.msg = "Bump an enemy to start a battle."

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit(0)

    def _move_and_collide(self, rect, dx, dy):
        # basic AABB collision with solid tiles
        rect.x += int(dx)
        # horizontal
        if dx != 0:
            cells = self._nearby_walls(rect)
            for c in cells:
                if rect.colliderect(c):
                    if dx > 0: rect.right = c.left
                    else: rect.left = c.right
        rect.y += int(dy)
        if dy != 0:
            cells = self._nearby_walls(rect)
            for c in cells:
                if rect.colliderect(c):
                    if dy > 0: rect.bottom = c.top
                    else: rect.top = c.bottom
        return rect

    def _nearby_walls(self, rect):
        res = []
        x0 = clamp(rect.left//TILE -1, 0, self.cols-1)
        y0 = clamp(rect.top//TILE -1, 0, self.rows-1)
        x1 = clamp(rect.right//TILE +1, 0, self.cols-1)
        y1 = clamp(rect.bottom//TILE+1, 0, self.rows-1)
        for y in range(y0, y1+1):
            for x in range(x0, x1+1):
                if self.grid[y][x] == 1:
                    res.append(rect_for_cell(x,y))
        return res

    def update(self, dt):
        keys = pygame.key.get_pressed()
        ax = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        ay = (keys[pygame.K_DOWN]  or keys[pygame.K_s]) - (keys[pygame.K_UP]   or keys[pygame.K_w])
        v = pygame.Vector2(ax, ay)
        if v.length_squared() > 0:
            v = v.normalize() * self.speed
        else:
            v.update(0,0)
        self.pvx, self.pvy = v.x, v.y

        prect = pygame.Rect(int(self.px), int(self.py), TILE-10, TILE-10)
        prect.centerx = int(self.px)+TILE//2
        prect.centery = int(self.py)+TILE//2
        prect = self._move_and_collide(prect, self.pvx*dt, self.pvy*dt)
        self.px, self.py = prect.left, prect.top

        # enemies wander
        for e in self.enemies:
            if not e["alive"]: continue
            # change dir sometimes
            if random.random() < 0.02:
                e["dir"] += random.uniform(-0.8, 0.8)
            ex = e["x"] + math.cos(e["dir"]) * e["spd"] * dt
            ey = e["y"] + math.sin(e["dir"]) * e["spd"] * dt
            # bounce off walls
            er = pygame.Rect(0,0,TILE-12,TILE-12); er.center = (ex,ey)
            solid_near = self._nearby_walls(er)
            blocked = False
            for c in solid_near:
                if er.colliderect(c):
                    e["dir"] += math.pi/2 + random.uniform(-0.5,0.5)
                    blocked = True
                    break
            if not blocked:
                e["x"], e["y"] = ex, ey

        # collision with player starts a battle
        for e in self.enemies:
            if not e["alive"]: continue
            er = pygame.Rect(0,0,TILE-16,TILE-16); er.center = (e["x"], e["y"])
            if prect.colliderect(er):
                play(SFX_TICK)
                e["alive"] = False
                # build enemy stats for the battle
                estats = dict(name=e["kind"], max_hp=e["max_hp"], hp=e["max_hp"], atk=e["atk"],
                              defense=e["defense"], xp=e["xp"], coins=e["coins"], hue=e["hue"])
                self.game.push(BattleScene(self.game), enemy=estats, return_to=self)

    def draw(self, s):
        # background grid
        s.fill((18,20,26))
        for y in range(self.rows):
            for x in range(self.cols):
                r = rect_for_cell(x,y)
                if self.grid[y][x] == 1:
                    pygame.draw.rect(s, (30,38,44), r)
                else:
                    pygame.draw.rect(s, (24,26,32), r, 1)
        # draw enemies
        for e in self.enemies:
            if not e["alive"]: continue
            cr = pygame.Rect(0,0,TILE-16,TILE-16); cr.center = (int(e["x"]), int(e["y"]))
            pygame.draw.rect(s, e["hue"], cr, border_radius=8)
            draw_text(s, e["kind"][:1], cr.centerx, cr.centery-1, FONT, BLACK, center=True, shadow=False)

        # draw player
        prect = pygame.Rect(0,0,TILE-10,TILE-10)
        prect.left, prect.top = int(self.px), int(self.py)
        pygame.draw.rect(s, CYAN, prect, border_radius=10)
        draw_text(s, self.game.player.name, 8, 8, FONT_S, SILVER)
        draw_text(s, f"HP {self.game.player.hp}/{self.game.player.max_hp}  FP {self.game.player.fp}/{self.game.player.max_fp}  LV {self.game.player.level}", 8, 28, FONT_S, SILVER)
        draw_text(s, self.msg, 8, H-28, FONT_S, GRAY)

# ---------- Battle ----------
class BattleScene(Scene):
    def on_enter(self, **kwargs):
        self.enemy = kwargs.get("enemy")
        self.return_to = kwargs.get("return_to", None)
        self.state = "intro"
        self.timer = 0.0
        self.menu_index = 0
        self.submenu_index = 0
        self.message = "A wild foe approaches!"
        self.flash = 0.0
        self.guard_window = 0.0
        self.guard_success = False
        self.pending_damage = 0
        self.last_grade = None
        self.cursor_blink = 0.0

        # menu layout
        self.commands = ["Attack", "Skill", "Item", "Run"]
        self.skills = [SHELL_DASH]
        self.selected_move = None

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if self.state in ("player_menu", "choose_skill"):
                if e.key in (pygame.K_RIGHT, pygame.K_d):
                    (self.submenu_right if self.state=="choose_skill" else self.menu_right)()
                elif e.key in (pygame.K_LEFT, pygame.K_a):
                    (self.submenu_left if self.state=="choose_skill" else self.menu_left)()
                elif e.key in (pygame.K_RETURN, pygame.K_z):
                    self.menu_confirm()
                elif e.key in (pygame.K_x, pygame.K_BACKSPACE, pygame.K_ESCAPE):
                    self.state = "player_menu"; self.selected_move=None
            elif self.state.startswith("ac_"):
                # action commands handle Z
                if e.key == pygame.K_z:
                    self.ac_press = True

    # menu helpers
    def menu_right(self): self.menu_index = (self.menu_index + 1) % len(self.commands)
    def menu_left(self):  self.menu_index = (self.menu_index - 1) % len(self.commands)

    def submenu_right(self):
        self.submenu_index = (self.submenu_index + 1) % max(1, len(self.skills))

    def submenu_left(self):
        self.submenu_index = (self.submenu_index - 1) % max(1, len(self.skills))

    def menu_confirm(self):
        c = self.commands[self.menu_index]
        if c == "Attack":
            self.selected_move = JUMP
            self.start_action_command(self.selected_move)
        elif c == "Skill":
            if not self.skills:
                self.message = "No skills yet."
                play(SFX_TICK); return
            move = self.skills[self.submenu_index]
            if self.game.player.fp < move.fp_cost:
                self.message = "Not enough FP!"
                play(SFX_HURT); return
            self.game.player.fp -= move.fp_cost
            self.selected_move = move
            self.start_action_command(move)
        elif c == "Item":
            # a single item type for demo
            if getattr(self.game.player, "_heart_leafs", 3) <= 0:
                self.message = "Out of Heart Leafs!"
                play(SFX_TICK)
            else:
                self.game.player._heart_leafs = getattr(self.game.player, "_heart_leafs", 3) - 1
                heal = 7
                self.game.player.hp = clamp(self.game.player.hp + heal, 0, self.game.player.max_hp)
                self.message = f"Used Heart Leaf! +{heal} HP"
                play(SFX_GOOD)
                self.state = "enemy_turn"; self.timer = 0.0
        elif c == "Run":
            if random.random() < 0.45:
                self.message = "You got away!"
                play(SFX_GOOD)
                # return to map
                self.finish_to_map(victory=False, fled=True)
            else:
                self.message = "Couldn't run!"
                play(SFX_HURT)
                self.state = "enemy_turn"; self.timer = 0.0

    def start_action_command(self, move: Move):
        self.ac_press = False
        self.last_grade = None
        if move.type == "timed":
            self.state = "ac_timed"
            self.timer = 0.0
            self.ac_pos = 0.0  # 0..1 marker position
            self.ac_speed = 1.3  # cycles per second
        elif move.type == "mash":
            self.state = "ac_mash"
            self.timer = 0.0
            self.mash_count = 0

    def update(self, dt):
        self.timer += dt
        self.cursor_blink += dt
        if self.state == "intro":
            if self.timer > 0.8:
                self.state = "player_menu"; self.timer = 0.0; self.message = "Choose a command."
        elif self.state == "player_menu":
            pass
        elif self.state == "choose_skill":
            pass
        elif self.state == "ac_timed":
            # marker sweeps left->right across a bar; press near center
            self.ac_pos = (self.ac_pos + self.ac_speed * dt) % 1.0
            if self.ac_press:
                self.ac_press = False
                diff = abs(self.ac_pos - 0.5)
                if diff < 0.035:
                    grade = "Great"; bonus = 2; play(SFX_GREAT)
                elif diff < 0.11:
                    grade = "Good"; bonus = 1; play(SFX_GOOD)
                else:
                    grade = "OK";   bonus = 0; play(SFX_TICK)
                self.resolve_player_attack(self.selected_move, bonus, grade)
        elif self.state == "ac_mash":
            # mash Z to build power for duration
            if self.ac_press:
                self.ac_press = False
                self.mash_count += 1
                play(SFX_TICK)
            if self.timer >= self.selected_move.mash_time:
                # Convert mash count to bonus
                rate = self.mash_count / self.selected_move.mash_time
                if rate >= 8: grade, bonus = ("Great", 3); play(SFX_GREAT)
                elif rate >= 4.5: grade, bonus = ("Good", 2); play(SFX_GOOD)
                else: grade, bonus = ("OK", 1); play(SFX_TICK)
                self.resolve_player_attack(self.selected_move, bonus, grade)
        elif self.state == "enemy_turn":
            # simple windup -> attack -> resolve; player can Guard with Z
            if self.guard_window > 0:
                self.guard_window -= dt
            if self.timer < 0.6:
                pass  # windup
            elif self.timer < 0.6 + 0.25:
                # strike window
                if self.guard_window <= 0:
                    self.guard_window = 0.18  # open window
                    self.guard_success = False
                # no explicit input here; key is read in handle_event via ac_press (reused)
            else:
                # apply damage once
                if self.pending_damage == 0:
                    dmg = max(0, self.enemy["atk"] - self.game.player.defense)
                    if self.guard_success:
                        dmg = max(0, dmg - 1)
                        play(SFX_BLOCK)
                    else:
                        play(SFX_HURT)
                    self.game.player.hp = clamp(self.game.player.hp - dmg, 0, self.game.player.max_hp)
                    self.message = ("BLOCK! " if self.guard_success else "") + f"Enemy hits for {dmg}."
                    self.pending_damage = dmg
                # advance state after a beat
                if self.timer >= 1.2:
                    self.pending_damage = 0
                    if self.game.player.hp <= 0:
                        self.state = "defeat"; self.timer = 0.0; self.message = "You fainted..."
                    else:
                        self.state = "player_menu"; self.timer = 0.0
        elif self.state == "victory":
            if self.timer > 1.5:
                self.finish_to_map(victory=True)
        elif self.state == "defeat":
            if self.timer > 1.8:
                # back to title
                self.game.player = Stats()  # reset
                self.game.switch(TitleScene(self.game))

        # read guard input in enemy turn
        if self.state == "enemy_turn" and self.guard_window > 0:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_z]:
                self.guard_success = True
                self.guard_window = 0

    def resolve_player_attack(self, move, bonus, grade):
        self.last_grade = grade
        atk = self.game.player.atk + move.base + bonus
        dmg = max(0, atk - self.enemy["defense"])
        self.enemy["hp"] = clamp(self.enemy["hp"] - dmg, 0, self.enemy["max_hp"])
        self.message = f"{move.name}! {grade}! {dmg} dmg."
        play(SFX_HIT if grade=="OK" else (SFX_GOOD if grade=="Good" else SFX_GREAT))
        self.timer = 0.0
        if self.enemy["hp"] <= 0:
            self.state = "victory"; self.timer = 0.0
            self.message = f"Victory! +{self.enemy['xp']} XP, +{self.enemy['coins']} coins"
            self.game.player.xp += self.enemy["xp"]
            self.game.player.coins += self.enemy["coins"]
            play(SFX_WIN)
            # Level up every 10 XP for the demo
            while self.game.player.xp >= 10:
                self.game.player.xp -= 10
                self.game.player.level += 1
                self.game.player.max_hp += 2
                self.game.player.hp = self.game.player.max_hp
                self.game.player.max_fp += 1
                self.game.player.fp = self.game.player.max_fp
                self.game.player.atk += 1 if self.game.player.level % 2 == 0 else 0
                self.message = f"Level Up! Now LV {self.game.player.level}"
        else:
            self.state = "enemy_turn"; self.timer = 0.0
            self.guard_window = 0.0
            self.guard_success = False
            self.pending_damage = 0

    def finish_to_map(self, victory=True, fled=False):
        # return to map scene on the stack
        if self.return_to:
            self.game.pop()  # remove battle, resume map
        else:
            # if launched standalone, go to map fresh
            self.game.switch(MapScene(self.game))

    def draw_hpbar(self, s, x, y, w, h, hp, maxhp, col):
        pygame.draw.rect(s, (40,48,56), (x,y,w,h), border_radius=4)
        if maxhp > 0:
            fw = int(w * (hp/maxhp))
            pygame.draw.rect(s, col, (x,y,fw,h), border_radius=4)
        pygame.draw.rect(s, BLACK, (x,y,w,h), 1, border_radius=4)

    def draw_menu(self, s):
        # command buttons
        bx, by, bw, bh = 40, H-96, 180, 40
        for i, name in enumerate(self.commands):
            r = pygame.Rect(bx + i*(bw+10), by, bw, bh)
            col = (34,40,48)
            pygame.draw.rect(s, col, r, border_radius=8)
            if i == self.menu_index and int(self.cursor_blink*4)%2==0:
                pygame.draw.rect(s, CYAN, r, 2, border_radius=8)
            else:
                pygame.draw.rect(s, SILVER, r, 1, border_radius=8)
            draw_text(s, name, r.centerx, r.centery, FONT, WHITE, center=True, shadow=False)

        # FP display
        draw_text(s, f"FP {self.game.player.fp}/{self.game.player.max_fp}", W-170, H-88, FONT_S, SILVER)

        # skill bar when Skill is focused
        if self.commands[self.menu_index] == "Skill":
            # show skill choices inline
            sx, sy = 40, H-140
            for i, mv in enumerate(self.skills):
                r = pygame.Rect(sx + i*(190), sy, 180, 34)
                pygame.draw.rect(s, (30,34,44), r, border_radius=6)
                pygame.draw.rect(s, SILVER if i!=self.submenu_index else CYAN, r, 1, border_radius=6)
                draw_text(s, f"{mv.name} ({mv.fp_cost} FP)", r.centerx, r.centery, FONT_S, WHITE, center=True, shadow=False)

    def draw(self, s):
        # stage
        s.fill((22, 22, 28))
        stage = pygame.Rect(0, H//2, W, H//2)
        pygame.draw.rect(s, (28,32,40), stage)
        pygame.draw.rect(s, (36,40,52), stage, 4)

        # enemy box
        er = pygame.Rect(W-320, 120, 220, 140)
        pygame.draw.rect(s, (34, 38, 46), er, border_radius=10)
        pygame.draw.rect(s, self.enemy["hue"], er, 3, border_radius=10)
        # enemy body
        ebody = pygame.Rect(0,0,120,80); ebody.center = er.center
        pygame.draw.rect(s, self.enemy["hue"], ebody, border_radius=20)
        draw_text(s, self.enemy["name"] if "name" in self.enemy else "??", er.centerx, er.top+16, FONT_S, WHITE, center=True, shadow=False)
        self.draw_hpbar(s, er.left+20, er.bottom-22, er.width-40, 10, self.enemy["hp"], self.enemy["max_hp"], ORANGE)

        # player box
        pr = pygame.Rect(80, 120, 220, 140)
        pygame.draw.rect(s, (34, 38, 46), pr, border_radius=10)
        pygame.draw.rect(s, CYAN, pr, 3, border_radius=10)
        pbody = pygame.Rect(0,0,120,80); pbody.center = pr.center
        pygame.draw.rect(s, CYAN, pbody, border_radius=20)
        draw_text(s, self.game.player.name, pr.centerx, pr.top+16, FONT_S, WHITE, center=True, shadow=False)
        self.draw_hpbar(s, pr.left+20, pr.bottom-22, pr.width-40, 10, self.game.player.hp, self.game.player.max_hp, GREEN)

        # menus or action UIs
        if self.state in ("player_menu","choose_skill"):
            self.draw_menu(s)
        elif self.state == "ac_timed":
            # draw the timing bar
            bar = pygame.Rect(80, H-110, 360, 16)
            pygame.draw.rect(s, (30,34,44), bar, border_radius=8)
            # center "sweet" zone
            sweet = bar.inflate(-bar.width*0.6, 0)
            pygame.draw.rect(s, (54,58,72), sweet, border_radius=8)
            # marker
            x = bar.left + int(bar.width * self.ac_pos)
            pygame.draw.rect(s, YELLOW, (x-3, bar.top-6, 6, bar.height+12))
            draw_text(s, "Press Z in the center!", bar.centerx, bar.top-14, FONT_S, SILVER, center=True, shadow=False)
        elif self.state == "ac_mash":
            # mash meter
            r = pygame.Rect(80, H-110, 360, 16)
            pygame.draw.rect(s, (30,34,44), r, border_radius=8)
            t = clamp(self.timer / self.selected_move.mash_time, 0, 1)
            fill = r.inflate(-4, -4)
            fw = int(fill.width * t)
            pygame.draw.rect(s, CYAN, (fill.left, fill.top, fw, fill.height), border_radius=6)
            draw_text(s, f"Mash Z! {self.mash_count}", r.centerx, r.top-14, FONT_S, SILVER, center=True, shadow=False)

        # enemy attack telegraph + guard
        if self.state == "enemy_turn":
            # flash exclamation near player
            ex = pr.right + 10; ey = pr.top + 10
            if int(self.timer*10)%2==0:
                draw_text(s, "!", ex, ey, FONT_B, YELLOW)
            if self.guard_window > 0:
                draw_text(s, "Z to Guard!", W//2, H-110, FONT_S, SILVER, center=True, shadow=False)

        # message box
        msgr = pygame.Rect(40, H-64, W-80, 36)
        pygame.draw.rect(s, (26,30,38), msgr, border_radius=6)
        pygame.draw.rect(s, SILVER, msgr, 1, border_radius=6)
        draw_text(s, self.message, msgr.left+12, msgr.centery, FONT_S, WHITE, center=False, shadow=False)

        # debug state
        # draw_text(s, f"STATE {self.state}", W-140, 8, FONT_S, GRAY)

# ---------- Main ----------
if __name__ == "__main__":
    g = Game()
    g.run()
