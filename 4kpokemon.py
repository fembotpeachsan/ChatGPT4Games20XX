# Monster Red — vibes-only clean-room vertical slice (files=off, 60 FPS)
# ---------------------------------------------------------------------
# This is an original, no-assets, single-file Pygame project that pays
# homage to classic monster-battler flow WITHOUT using any copyrighted
# sprites, names, maps, or data. Everything is generated procedurally or
# authored here in code. You are free to mod it for personal use.
#
# Controls
# --------
# Overworld:
#   Arrow keys / WASD : move
#   ENTER / Z         : open menu / confirm (also advance text)
#   X / BACKSPACE     : cancel
#   V                 : toggle vibes (on by default)
#   ESC               : quit
#
# Battle:
#   Arrow keys        : navigate
#   ENTER / Z         : confirm (also advance text)
#   X / BACKSPACE     : cancel
#   R                 : quick-run attempt
#
# Notes
# -----
# * "FILES = OFF": no external images, audio, or data required.
# * 60 FPS lock; lightweight so it should run on modest machines.
# * HeartGold-ish *vibes*: dual-panel layout & subtle palette cues.
# * This is a vertical slice, not a 1:1 re-creation of any existing game.
#
# Have fun! — built for vibes :3

import sys, math, random, time, array
import pygame

# ------------------------- Init & Globals ------------------------------

pygame.init()
SCREEN_W, SCREEN_H = 800, 600
TOP_H = 360
BOT_H = SCREEN_H - TOP_H
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Monster Red — vibes edition (files off, 60 FPS)")
clock = pygame.time.Clock()
FPS = 60

# Fonts (system fonts only, no external files)
FONT_SMALL = pygame.font.SysFont(None, 20)
FONT = pygame.font.SysFont(None, 24)
FONT_BIG = pygame.font.SysFont(None, 32)

# Try to init sound (pure tone synthesis); if fails, run silent.
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
    buf = array.array('h')
    amp = int(32767 * max(0.0, min(1.0, volume)))
    for i in range(n):
        t = i / sr
        val = int(amp * math.sin(2 * math.pi * freq * t))
        buf.append(val)
    return pygame.mixer.Sound(buffer=buf.tobytes())

SND_SELECT = make_tone(660, 70, 0.25)
SND_HIT    = make_tone(220, 90, 0.30)
SND_HEAL   = make_tone(880, 120, 0.20)
SND_CATCH  = make_tone(523, 180, 0.28)
SND_RUN    = make_tone(330, 70, 0.22)

def play(snd):
    if snd and SFX_ENABLED:
        snd.play()

# Vibes toggle
VIBES_ON = True

# Palette (HGDS-ish vibes, no direct copying)
PAL_BG_TOP = (214, 228, 247)
PAL_BG_BOT = (238, 243, 250)
PAL_PANEL  = (230, 225, 230)
PAL_ACCENT = (248, 200, 88)
PAL_GRASS  = (122, 200, 120)
PAL_TREE   = (40, 120, 60)
PAL_PATH   = (190, 170, 150)
PAL_WATER  = (88, 155, 218)
PAL_TGRASS = (80, 180, 100)
PAL_HOME   = (200, 155, 120)
PAL_TEXT   = (30, 40, 50)
PAL_SHADOW = (0, 0, 0)

# Screen shake
shake_time = 0
shake_mag = 0

def screenshake(frames=8, mag=4):
    global shake_time, shake_mag
    shake_time = frames
    shake_mag = mag

def get_shake_offset():
    global shake_time
    if shake_time > 0 and VIBES_ON:
        shake_time -= 1
        return (random.randint(-shake_mag, shake_mag), random.randint(-shake_mag, shake_mag))
    return (0, 0)

# Simple HSV hue cycling for vibes
def hsv_to_rgb(h, s, v):
    h = float(h) % 1.0
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = int(255 * v * (1.0 - s))
    q = int(255 * v * (1.0 - f * s))
    t = int(255 * v * (1.0 - (1.0 - f) * s))
    v = int(255 * v)
    i = i % 6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)

# --------------------------- Map & Overworld ---------------------------

TILE = 32
# Fit entirely inside TOP_H (360 px): 11 tiles * 32 = 352 px
MAP_W, MAP_H = 25, 11  # 800x352 fits top screen perfectly
# Tiles: 0 grass, 1 tree, 2 path, 3 water, 4 tall grass, 5 home
def make_world():
    # Build a light "route 1" style strip with a town house and some water.
    m = [[0 for _ in range(MAP_W)] for __ in range(MAP_H)]
    # Scatter trees on edges
    for y in range(MAP_H):
        for x in range(MAP_W):
            if x == 0 or y == 0 or x == MAP_H-1 or y == MAP_H-1:
                pass
    # Correct edge walls:
    for x in range(MAP_W):
        m[0][x] = 1
        m[MAP_H-1][x] = 1
    for y in range(MAP_H):
        m[y][0] = 1
        m[y][MAP_W-1] = 1

    # Path
    mid = MAP_H//2
    for x in range(2, MAP_W-2):
        m[mid][x] = 2
        if random.random() < 0.1 and mid-1 > 0:
            m[mid-1][x] = 2
    # Water pond (clamped to map)
    for y in range(2, min(2+4, MAP_H-2)):
        for x in range(4, min(9, MAP_W-2)):
            m[y][x] = 3
    # Tall grass patches near path
    for y in range(max(1, mid-3), min(MAP_H-1, mid+3)):
        for x in range(12, min(22, MAP_W-1)):
            if random.random() < 0.35:
                m[y][x] = 4
    # Home tile
    hx, hy = 3, mid
    m[hy][hx] = 5
    return m, (hx+1, hy)  # start to the right of home tile

WORLD, PLAYER_START = make_world()

def draw_tile(surf, x, y, t):
    r = pygame.Rect(x*TILE, y*TILE, TILE, TILE)
    if t == 0:  # grass
        pygame.draw.rect(surf, PAL_GRASS, r)
        # subtle blades
        if VIBES_ON and (x+y) % 2 == 0:
            pygame.draw.line(surf, (150, 220, 150), (r.x+4, r.y+TILE-6), (r.x+8, r.y+TILE-2), 1)
    elif t == 1:  # tree
        pygame.draw.rect(surf, PAL_GRASS, r)
        pygame.draw.rect(surf, PAL_TREE, r.inflate(-6, -6), border_radius=8)
    elif t == 2:  # path
        pygame.draw.rect(surf, PAL_PATH, r)
    elif t == 3:  # water
        pygame.draw.rect(surf, PAL_WATER, r)
        if VIBES_ON:
            c = hsv_to_rgb((pygame.time.get_ticks()%5000)/5000.0, 0.4, 0.9)
            pygame.draw.circle(surf, c, (r.centerx, r.centery), 6, 2)
    elif t == 4:  # tall grass
        pygame.draw.rect(surf, PAL_TGRASS, r)
        # render taller blades
        for i in range(3):
            bx = r.x + 4 + i*8
            pygame.draw.line(surf, (60, 120, 70), (bx, r.bottom-5), (bx+4, r.y+6), 2)
    elif t == 5:  # home
        pygame.draw.rect(surf, PAL_PATH, r)
        pygame.draw.rect(surf, PAL_HOME, r.inflate(-8, -8))

def can_walk(tx, ty):
    if tx < 0 or ty < 0 or tx >= MAP_W or ty >= MAP_H:
        return False
    t = WORLD[ty][tx]
    if t in (1, 3):  # trees, water are solid
        return False
    return True

def encounter_chance(tx, ty):
    t = WORLD[ty][tx]
    if t == 4:  # tall grass
        return 0.1  # 10% per step
    return 0.0

# --------------------------- Monsters & Moves --------------------------

TYPES = ["Normal","Fire","Water","Grass","Electric","Rock","Bug","Psychic","Ghost"]

# Minimal type chart (sparse)
TYPE_CHART = {
    ("Fire","Grass"): 2.0, ("Fire","Water"): 0.5, ("Fire","Rock"): 0.5, ("Fire","Bug"): 2.0,
    ("Water","Fire"): 2.0, ("Water","Grass"): 0.5, ("Water","Rock"): 2.0,
    ("Grass","Water"): 2.0, ("Grass","Fire"): 0.5, ("Grass","Rock"): 2.0,
    ("Electric","Water"): 2.0, ("Electric","Grass"): 0.5, ("Electric","Rock"): 0.5,
    ("Rock","Fire"): 2.0, ("Rock","Bug"): 2.0,
    ("Bug","Psychic"): 2.0, ("Bug","Fire"): 0.5,
    ("Psychic","Ghost"): 0.5, ("Psychic","Bug"): 0.5,
    ("Ghost","Psychic"): 2.0,
}

def type_mult(att_type, def_type):
    return TYPE_CHART.get((att_type, def_type), 1.0)

class Move:
    def __init__(self, name, mtype, power, accuracy=100, kind="physical"):
        self.name = name
        self.type = mtype
        self.power = power
        self.acc = accuracy
        self.kind = kind  # "physical" or "special"

BASIC_MOVES = [
    Move("Tackle", "Normal", 40, 100),
    Move("Ember", "Fire", 40, 100),
    Move("WaterJet", "Water", 40, 100),
    Move("LeafDart", "Grass", 45, 95),
    Move("Spark", "Electric", 45, 100),
    Move("Pebble", "Rock", 40, 100),
    Move("Nibble", "Bug", 35, 100),
    Move("MindTap", "Psychic", 45, 100, kind="special"),
    Move("Shade", "Ghost", 40, 100),
]

# Base species data (original; keep small)
SPECIES = [
    # name, type, base stats (hp, atk, df, spd), learnset (levels->move)
    ("Flameling", "Fire",    (39, 52, 43, 65), {1:"Tackle", 3:"Ember", 7:"Spark"}),
    ("Aquadrop",  "Water",   (44, 48, 65, 43), {1:"Tackle", 3:"WaterJet", 7:"Pebble"}),
    ("Leaflit",   "Grass",   (45, 49, 49, 45), {1:"Tackle", 3:"LeafDart", 7:"Nibble"}),
    ("Voltkit",   "Electric",(35, 55, 40, 90), {1:"Tackle", 3:"Spark", 7:"MindTap"}),
    ("Rocko",     "Rock",    (50, 70, 65, 30), {1:"Pebble", 5:"Tackle"}),
    ("Buzzy",     "Bug",     (40, 35, 30, 70), {1:"Nibble", 4:"LeafDart"}),
    ("Psyba",     "Psychic", (35, 30, 30, 70), {1:"MindTap", 5:"Tackle"}),
    ("Shadepup",  "Ghost",   (30, 45, 35, 80), {1:"Shade", 4:"Tackle"}),
]

MOVE_LOOKUP = {m.name: m for m in BASIC_MOVES}
SPECIES_LOOKUP = {name: (typ, stats, learn) for (name, typ, stats, learn) in SPECIES}

def level_to_stat(base, level):
    # Very rough stat scaling
    return int(base + level * (base / 25.0)) + 5

class Monster:
    def __init__(self, species, level=3):
        self.species = species
        self.level = level
        stype, (b_hp, b_atk, b_df, b_spd), learn = SPECIES_LOOKUP[species]
        self.type = stype
        self.max_hp = level_to_stat(b_hp, level)
        self.atk    = level_to_stat(b_atk, level)
        self.df     = level_to_stat(b_df, level)
        self.spd    = level_to_stat(b_spd, level)
        self.hp     = self.max_hp
        self.moves  = []
        for lv in sorted(learn.keys()):
            if lv <= level:
                mname = learn[lv]
                if mname in MOVE_LOOKUP and MOVE_LOOKUP[mname] not in self.moves:
                    self.moves.append(MOVE_LOOKUP[mname])
        if not self.moves:
            self.moves = [MOVE_LOOKUP["Tackle"]]
        self.xp = 0
        self.next_xp = 20 + level * 10

    def alive(self):
        return self.hp > 0

    def gain_xp(self, amt):
        self.xp += amt
        leveled = False
        while self.xp >= self.next_xp:
            self.xp -= self.next_xp
            self.level += 1
            self.max_hp += random.randint(2, 4)
            self.atk    += random.randint(1, 3)
            self.df     += random.randint(1, 3)
            self.spd    += random.randint(1, 3)
            self.hp = self.max_hp
            self.next_xp += 10 + self.level * 2
            leveled = True
        return leveled

    def color(self):
        # Color by type
        t = self.type
        if t == "Fire": return (255, 110, 60)
        if t == "Water": return (80, 160, 255)
        if t == "Grass": return (90, 200, 100)
        if t == "Electric": return (255, 225, 90)
        if t == "Rock": return (150, 130, 110)
        if t == "Bug": return (170, 200, 60)
        if t == "Psychic": return (230, 100, 230)
        if t == "Ghost": return (130, 90, 180)
        return (200, 200, 200)

def calc_damage(attacker, defender, move):
    # accuracy check
    if random.randint(1,100) > move.acc:
        return 0, 1.0, False, False  # miss
    stab = 1.5 if attacker.type == move.type else 1.0
    mult = type_mult(move.type, defender.type)
    crit = (random.random() < 0.1)
    rand = random.uniform(0.85, 1.0)
    base = move.power * (attacker.atk / max(1, defender.df))
    dmg = int(max(1, base * stab * mult * (1.5 if crit else 1.0) * rand))
    return dmg, mult, crit, True

# ----------------------------- UI Helpers ------------------------------

def draw_panel(surf, rect, title=None):
    pygame.draw.rect(surf, PAL_PANEL, rect, border_radius=8)
    pygame.draw.rect(surf, (200, 200, 200), rect, 2, border_radius=8)
    if title:
        txt = FONT.render(title, True, PAL_TEXT)
        surf.blit(txt, (rect.x + 10, rect.y + 8))

def draw_text(surf, text, x, y, col=PAL_TEXT, shadow=True, font=FONT):
    if shadow:
        sh = font.render(text, True, PAL_SHADOW)
        surf.blit(sh, (x+2, y+2))
    s = font.render(text, True, col)
    surf.blit(s, (x, y))

class TextBox:
    def __init__(self, rect):
        self.rect = rect
        self.queue = []
        self.current = ""
        self.show_len = 0
        self.speed = 2  # chars per frame
        self.done = True

    def push(self, msg):
        self.queue.append(msg)
        if self.done:
            self.next_msg()

    def next_msg(self):
        if self.queue:
            self.current = self.queue.pop(0)
            self.show_len = 0
            self.done = False
        else:
            self.current = ""
            self.show_len = 0
            self.done = True

    def update(self):
        if not self.done:
            self.show_len += self.speed
            if self.show_len >= len(self.current):
                self.show_len = len(self.current)

    def draw(self, surf):
        draw_panel(surf, self.rect, None)
        # render wrapped
        txt = self.current[:self.show_len]
        lines = wrap_text(txt, FONT, self.rect.w - 20)
        y = self.rect.y + 10
        for line in lines[:5]:
            draw_text(surf, line, self.rect.x+10, y, font=FONT)
            y += 26
        if self.done or self.show_len >= len(self.current):
            draw_text(surf, "Z/Enter: next", self.rect.right-130, self.rect.bottom-28, (80,80,90), font=FONT_SMALL)

    def advance(self):
        # Returns True if it moved to the next (or finished), False if it just fast-forwarded
        if self.done:
            return False
        if self.show_len < len(self.current):
            self.show_len = len(self.current)
            return False
        else:
            self.next_msg()
            return True

def wrap_text(text, font, width):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = cur + (" " if cur else "") + w
        if font.size(test)[0] <= width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

class Menu:
    def __init__(self, options, rect, cols=1):
        self.options = options
        self.rect = rect
        self.idx = 0
        self.cols = max(1, cols)

    def draw(self, surf, title=None):
        draw_panel(surf, self.rect, title)
        w = self.rect.w
        h = self.rect.h
        rows = math.ceil(len(self.options) / self.cols)
        cell_w = (w - 20) // self.cols
        cell_h = (h - 40) // max(1, rows)
        for i, opt in enumerate(self.options):
            r = i // self.cols
            c = i % self.cols
            x = self.rect.x + 10 + c * cell_w
            y = self.rect.y + 30 + r * cell_h
            if i == self.idx:
                pygame.draw.rect(surf, PAL_ACCENT, (x-6, y-4, cell_w-8, 28), border_radius=6)
                draw_text(surf, opt, x, y, (30,30,30))
            else:
                draw_text(surf, opt, x, y, PAL_TEXT)

    def move(self, dx, dy):
        rows = math.ceil(len(self.options) / self.cols)
        r = self.idx // self.cols
        c = self.idx % self.cols
        r = max(0, min(rows-1, r + dy))
        c = max(0, min(self.cols-1, c + dx))
        new = r * self.cols + c
        if new < len(self.options):
            if new != self.idx:
                play(SND_SELECT)
            self.idx = new

    def current(self):
        return self.options[self.idx]

# ------------------------------ Battle ---------------------------------

class Particle:
    def __init__(self, x, y, vx, vy, life, col):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = life
        self.col = col

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            pygame.draw.circle(surf, self.col, (int(self.x), int(self.y)), 3)

class Battle:
    def __init__(self, player_party, wild_mon, inventory):
        self.player_party = player_party
        self.enemy = wild_mon
        self.inventory = inventory
        self.state = "intro"
        self.menu = Menu(["Fight","Capsule","Swap","Run"], pygame.Rect(20, TOP_H+20, 360, 140), cols=2)
        self.move_menu = None
        self.text = TextBox(pygame.Rect(400, TOP_H+20, 380, 140))
        self.turn_timer = 0
        self.particles = []
        self.flash = 0
        self.choose_idx = 0
        self.result = None  # None, "win", "run", "caught", "lose"

        # choose first alive
        self.active = 0
        while self.active < len(self.player_party) and not self.player_party[self.active].alive():
            self.active += 1
        if self.active >= len(self.player_party):
            self.result = "lose"

        self.text.push(f"A wild {self.enemy.species} appeared!")

    def get_active(self):
        return self.player_party[self.active]

    def ai_choose_move(self):
        m = self.enemy.moves
        return random.choice(m)

    def update(self, keys, pressed_confirm, pressed_cancel, pressed_run):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        if self.flash > 0:
            self.flash -= 1
        self.text.update()

        # Let player advance queued text before any other interaction
        if pressed_confirm and not self.text.done:
            progressed = self.text.advance()
            # When the intro line is fully acknowledged, go to menu
            if self.state == "intro" and self.text.done:
                self.state = "menu"
            return False

        # If battle already has a result, allow exit when user confirms after finishing all text
        if self.result:
            if pressed_confirm:
                return True
            return False

        if self.state == "intro":
            # Wait until player advances the intro text (handled above)
            return False

        elif self.state == "menu":
            if pressed_confirm:
                choice = self.menu.current()
                if choice == "Fight":
                    pm = self.get_active().moves
                    opts = [m.name for m in pm]
                    self.move_menu = Menu(opts, pygame.Rect(20, TOP_H+20, 360, 140), cols=2)
                    self.state = "choose_move"
                elif choice == "Capsule":
                    # Use a capsule if available
                    if self.inventory.get("Capsule", 0) <= 0:
                        self.text.push("Out of capsules!")
                    else:
                        self.inventory["Capsule"] -= 1
                        success = self.try_capture()
                        if success:
                            self.text.push(f"Gotcha! {self.enemy.species} was captured!")
                            play(SND_CATCH)
                            self.result = "caught"
                        else:
                            self.text.push("It broke free!")
                            # wild turn
                            self.wild_turn()
                    self.state = "menu"
                elif choice == "Swap":
                    # choose next alive
                    alive = [(i, m) for i, m in enumerate(self.player_party) if m.alive() and i != self.active]
                    if not alive:
                        self.text.push("No other monsters can fight!")
                    else:
                        # simple rotate
                        ni = alive[0][0]
                        self.active = ni
                        self.text.push(f"Go! {self.get_active().species}!")
                        play(SND_SELECT)
                    self.state = "menu"
                elif choice == "Run":
                    if pressed_run or random.random() < 0.6:
                        self.text.push("Got away safely!")
                        play(SND_RUN)
                        self.result = "run"
                    else:
                        self.text.push("Couldn't escape!")
                        self.wild_turn()
                        self.state = "menu"

            # movement
            dx = dy = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += 1
            if dx or dy:
                self.menu.move(dx, dy)

        elif self.state == "choose_move":
            dx = dy = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += 1
            if dx or dy:
                self.move_menu.move(dx, dy)
            if pressed_confirm:
                mname = self.move_menu.current()
                move = MOVE_LOOKUP[mname]
                self.resolve_turn(move)
                self.state = "menu"
            if pressed_cancel:
                self.state = "menu"

        # check lose
        if not any(m.alive() for m in self.player_party):
            self.text.push("Your party fainted...")
            self.result = "lose"

        # check win
        if not self.enemy.alive() and not self.result:
            self.text.push("Wild monster fainted!")
            # XP to active
            leveled = self.get_active().gain_xp(12 + self.enemy.level * 3)
            if leveled:
                self.text.push(f"{self.get_active().species} grew to Lv.{self.get_active().level}!")
            self.result = "win"

        return False

    def try_capture(self):
        # Simplified capture rate
        hp_ratio = self.enemy.hp / self.enemy.max_hp
        base = 0.35  # base rate
        rate = base * (1.0 - hp_ratio) * (1.0 + 0.1 * (self.enemy.level/5.0))
        return random.random() < rate

    def wild_turn(self):
        if not self.enemy.alive(): return
        emove = self.ai_choose_move()
        self.perform_move(self.enemy, self.get_active(), emove, enemy=True)

    def perform_move(self, attacker, defender, move, enemy=False):
        dmg, mult, crit, hit = calc_damage(attacker, defender, move)
        if not hit:
            self.text.push(f"{attacker.species}'s {move.name} missed!")
            play(SND_SELECT)
            return
        defender.hp = max(0, defender.hp - dmg)
        # particles & shake
        for _ in range(10):
            ang = random.uniform(0, 2*math.pi)
            spd = random.uniform(1, 3)
            vx, vy = math.cos(ang)*spd, math.sin(ang)*spd
            cx = 580 if enemy else 220
            cy = 180
            self.particles.append(Particle(cx, cy, vx, vy, 20, (255,200,80)))
        screenshake(6, 4)
        self.flash = 6
        play(SND_HIT)
        # text
        tmsg = f"{attacker.species} used {move.name}!"
        if crit: tmsg += " Critical!"
        if mult > 1.0: tmsg += " It's super effective!"
        if mult < 1.0: tmsg += " It's not very effective..."
        self.text.push(tmsg)

    def resolve_turn(self, p_move):
        # Player chooses p_move; compare speeds.
        p = self.get_active()
        e = self.enemy
        e_move = self.ai_choose_move()
        # order
        first_player = p.spd >= e.spd
        seq = [("player", p_move), ("enemy", e_move)] if first_player else [("enemy", e_move), ("player", p_move)]
        for who, mv in seq:
            if who == "player" and p.alive():
                self.perform_move(p, e, mv, enemy=False)
            elif who == "enemy" and e.alive():
                self.perform_move(e, p, mv, enemy=True)

    def draw(self, surf):
        # top panel
        top = pygame.Surface((SCREEN_W, TOP_H))
        top.fill(PAL_BG_TOP)
        # battle "stage"
        pygame.draw.rect(top, (255,255,255), (20, 20, SCREEN_W-40, TOP_H-40), border_radius=16)
        pygame.draw.rect(top, (220,220,220), (20, 20, SCREEN_W-40, TOP_H-40), 4, border_radius=16)

        # vibe ribbon
        if VIBES_ON:
            t = (pygame.time.get_ticks() % 6000) / 6000.0
            c = hsv_to_rgb(t, 0.5, 0.95)
            pygame.draw.rect(top, c, (24, 24, SCREEN_W-48, 8), border_radius=4)

        # enemy on right, player on left
        # HP boxes
        def hp_bar(mon, x, y):
            draw_panel(top, pygame.Rect(x, y, 260, 80))
            draw_text(top, f"{mon.species}  Lv.{mon.level}", x+12, y+10, PAL_TEXT, True, FONT)
            # HP
            pct = max(0.0, min(1.0, mon.hp / max(1, mon.max_hp)))
            bw = 200
            pygame.draw.rect(top, (50,50,50), (x+12, y+40, bw, 16), 2)
            # green->red
            col = (int(255*(1-pct)), int(255*pct), 64)
            pygame.draw.rect(top, col, (x+12, y+40, int(bw*pct), 16))
            draw_text(top, f"{mon.hp}/{mon.max_hp}", x+12+bw+10, y+36, PAL_TEXT, False, FONT_SMALL)

        hp_bar(self.enemy, SCREEN_W-300, 40)
        if self.active < len(self.player_party):
            hp_bar(self.get_active(), 40, TOP_H-120)

        # sprites (circles)
        def mon_sprite(mon, cx, cy, enemy=False):
            base = mon.color()
            r = 38 if enemy else 45
            shade = (max(0, base[0]-30), max(0, base[1]-30), max(0, base[2]-30))
            pygame.draw.circle(top, shade, (cx+3, cy+3), r+2)
            pygame.draw.circle(top, base, (cx, cy), r)
            # eye
            pygame.draw.circle(top, (255,255,255), (cx+10, cy-6), 6)
            pygame.draw.circle(top, (0,0,0), (cx+10, cy-6), 2)
            # type ring
            pygame.draw.circle(top, (255,255,255), (cx, cy), r+6, 2)

        # flashing on hit
        if self.flash % 2 == 1:
            # skip draw for flicker
            pass
        else:
            mon_sprite(self.enemy, SCREEN_W-200, 190, enemy=True)
            if self.active < len(self.player_party):
                mon_sprite(self.get_active(), 200, 220, enemy=False)

        # particles
        for p in self.particles:
            p.draw(top)

        # bottom UI
        bot = pygame.Surface((SCREEN_W, BOT_H))
        bot.fill(PAL_BG_BOT)
        if self.state == "choose_move" and self.move_menu:
            self.move_menu.draw(bot, "Choose a move")
        else:
            self.menu.draw(bot, "Choose an action")
        self.text.draw(bot)

        # compose with shake
        ox, oy = get_shake_offset()
        surf.blit(top, (ox, oy))
        surf.blit(bot, (0, TOP_H))

# ----------------------------- Player ----------------------------------

class Player:
    def __init__(self, tx, ty):
        self.tx, self.ty = tx, ty
        self.step_cd = 0  # cooldown between steps

    def update(self, keys):
        if self.step_cd > 0:
            self.step_cd -= 1
            return None
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        if dx or dy:
            nx, ny = self.tx + (1 if dx>0 else -1 if dx<0 else 0), self.ty + (1 if dy>0 else -1 if dy<0 else 0)
            if can_walk(nx, ny):
                self.tx, self.ty = nx, ny
                self.step_cd = 8  # step delay
                return (self.tx, self.ty)
        return None

    def draw(self, surf):
        # simple oval on map
        r = pygame.Rect(self.tx*TILE, self.ty*TILE, TILE, TILE)
        pygame.draw.rect(surf, (255, 255, 255), r.inflate(-8, -8), border_radius=8)
        pygame.draw.rect(surf, (30, 30, 30), r.inflate(-8, -8), 2, border_radius=8)
        # tiny eyes
        pygame.draw.circle(surf, (0,0,0), (r.centerx+6, r.centery-6), 3)

# ----------------------------- Game State -------------------------------

class Game:
    def __init__(self):
        self.player = Player(*PLAYER_START)
        # starter
        starter = Monster(random.choice([s[0] for s in SPECIES][:4]), level=5)
        self.party = [starter]
        self.inventory = {"Capsule": 5}
        self.state = "overworld"  # or "battle", "menu"
        self.battle = None
        self.text = TextBox(pygame.Rect(20, TOP_H+20, SCREEN_W-40, 140))
        self.text.push("Welcome to Monster Red (vibes). Walk into tall grass for encounters.")
        self.menu = Menu(["Party","Inventory","Heal (Home)","Close"], pygame.Rect(200, TOP_H+20, 400, 160), cols=2)

    def heal_party(self):
        for m in self.party:
            m.hp = m.max_hp
        play(SND_HEAL)

    def update(self, keys, pressed_confirm, pressed_cancel, pressed_run, pressed_vibes):
        global VIBES_ON
        if pressed_vibes:
            VIBES_ON = not VIBES_ON

        if self.state == "overworld":
            # Let player advance overworld text before opening the menu
            if pressed_confirm and not self.text.done:
                self.text.advance()
                self.text.update()
                return

            step = self.player.update(keys)
            if step:
                tx, ty = step
                # encounter?
                if random.random() < encounter_chance(tx, ty):
                    # make a wild mon at level 3-6
                    sp = random.choice(SPECIES)[0]
                    lvl = random.randint(3, 6)
                    wild = Monster(sp, lvl)
                    self.battle = Battle(self.party, wild, self.inventory)
                    self.state = "battle"
                # home heal
                if WORLD[ty][tx] == 5:
                    self.heal_party()
                    self.text.push("Your party was fully healed at Home.")

            if pressed_confirm:
                # open menu
                self.state = "menu"

            self.text.update()

        elif self.state == "menu":
            dx = dy = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += 1
            if dx or dy: self.menu.move(dx, dy)
            if pressed_confirm:
                c = self.menu.current()
                if c == "Party":
                    # find next alive to front
                    for i, m in enumerate(self.party):
                        if m.alive():
                            self.party[0], self.party[i] = self.party[i], self.party[0]
                            self.text.push(f"{self.party[0].species} is at the front.")
                            break
                elif c == "Inventory":
                    self.text.push(f"Capsules: {self.inventory.get('Capsule',0)} — use in battle to capture.")
                elif c == "Heal (Home)":
                    # instant heal only on home tile
                    tx, ty = self.player.tx, self.player.ty
                    if WORLD[ty][tx] == 5:
                        self.heal_party()
                        self.text.push("Healed!")
                    else:
                        self.text.push("You need to be standing on Home to heal.")
                elif c == "Close":
                    self.state = "overworld"
            if pressed_cancel:
                self.state = "overworld"
            self.text.update()

        elif self.state == "battle" and self.battle:
            finished = self.battle.update(keys, pressed_confirm, pressed_cancel, pressed_run)
            if self.battle.result in ("win","run","caught","lose") and finished:
                # Handle caught
                if self.battle.result == "caught":
                    if len(self.party) < 6:
                        self.party.append(self.battle.enemy)
                        self.text.push(f"{self.battle.enemy.species} joined your party!")
                    else:
                        self.text.push("Party is full. Released to the wild (demo limit).")
                if self.battle.result == "lose":
                    # send home & heal
                    self.player.tx, self.player.ty = PLAYER_START
                    self.heal_party()
                    self.text.push("You blacked out... back home!")
                self.battle = None
                self.state = "overworld"

    def draw_overworld(self, surf):
        top = pygame.Surface((SCREEN_W, TOP_H))
        top.fill(PAL_BG_TOP)
        # draw map
        for y in range(MAP_H):
            for x in range(MAP_W):
                draw_tile(top, x, y, WORLD[y][x])
        self.player.draw(top)

        # vibe overlay
        if VIBES_ON:
            t = (pygame.time.get_ticks() % 10000) / 10000.0
            col = hsv_to_rgb(t, 0.25, 0.35)
            overlay = pygame.Surface((SCREEN_W, TOP_H), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (*col, 35), overlay.get_rect())
            top.blit(overlay, (0,0))

        # bottom UI
        bot = pygame.Surface((SCREEN_W, BOT_H))
        bot.fill(PAL_BG_BOT)
        if self.state == "menu":
            self.menu.draw(bot, "Menu")
        self.text.draw(bot)

        ox, oy = get_shake_offset()
        surf.blit(top, (ox, oy))
        surf.blit(bot, (0, TOP_H))

    def draw(self, surf):
        if self.state == "battle" and self.battle:
            self.battle.draw(surf)
        else:
            self.draw_overworld(surf)

# ------------------------------- Main ----------------------------------

def main():
    game = Game()
    running = True
    pressed_confirm = False
    pressed_cancel  = False
    pressed_run     = False
    pressed_vibes   = False

    while running:
        pressed_confirm = False
        pressed_cancel  = False
        pressed_run     = False
        pressed_vibes   = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_z):
                    pressed_confirm = True
                    play(SND_SELECT)
                if e.key in (pygame.K_x, pygame.K_BACKSPACE):
                    pressed_cancel = True
                if e.key == pygame.K_r:
                    pressed_run = True
                if e.key == pygame.K_v:
                    pressed_vibes = True
                if e.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        game.update(keys, pressed_confirm, pressed_cancel, pressed_run, pressed_vibes)
        screen.fill((255,255,255))
        game.draw(screen)

        # footer
        draw_text(screen, "MONSTER RED — vibes edition (files off) — 60 FPS", 12, 6, (60,60,70), False, FONT_SMALL)
        draw_text(screen, "V: toggle vibes • Z/Enter: select/advance • X/Backspace: cancel • ESC: quit", 12, 26, (60,60,70), False, FONT_SMALL)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
