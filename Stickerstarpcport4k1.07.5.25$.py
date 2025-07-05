#!/usr/bin/env python3
# paper_mario_battle.py  ⭐ Sticker‑Star patch – pure‑code assets ⭐
# Python 3.x, Pygame 2.x      (pip install pygame)
# Controls ────────────────────────────────────────────────────────
#  ← / →  cycle main commands      (Jump • Hammer • Swap Partner)
#  ↑ / ↓  scroll partner list
#  Space / Enter  confirm
#  During a Jump / Hammer animation press **Space** while the
#  attack “spark” is on‑screen to land a stylish ACTION COMMAND
#  Esc      quit          • Banner prompt appears on win / loss
# ──────────────────────────────────────────────────────────────────

import pygame, math, array, random, sys, os

# ─────────────────────────────────────────────────────────────────
# GLOBAL CONSTANTS / COLOUR PALETTE
# ─────────────────────────────────────────────────────────────────
WW, WH   = 800, 450
FPS      = 60
WHITE    = (255, 255, 255)
BLACK    = (0, 0, 0)

STICKER_YELLOW = (254, 246, 154)
STICKER_BLUE   = ( 95, 190, 255)
STICKER_GREEN  = ( 94, 218, 146)
STICKER_RED    = (255, 106, 106)

UI_BG     = STICKER_YELLOW
UI_BORDER = BLACK

HP_GREEN = ( 72, 220, 72)
HP_MID   = (235, 191,  90)
HP_RED   = (255,  80,  80)

MARIO_MAX_HP    = 20
GOOMBOSS_MAX_HP = 25
PARTNER_DAMAGE  = {"Koopa": 3, "Goomba": 2, "Chain Chomp": 4}
MARIO_DAMAGE    = {"Jump": 2, "Hammer": 3}
GOOMBOSS_DAMAGE = 3

# ─────────────────────────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=44_100, size=-16, channels=1)
screen = pygame.display.set_mode((WW, WH))
pygame.display.set_caption("Paper Mario – Sticker‑Star Battle!")
clock       = pygame.time.Clock()
font_big    = pygame.font.SysFont("comicsansms", 34, bold=True)
font_medium = pygame.font.SysFont("arialroundedmtbold", 22)
font_small  = pygame.font.SysFont("consolas", 16)

# ─────────────────────────────────────────────────────────────────
# SOUND HELPERS
# ─────────────────────────────────────────────────────────────────
def synth_tone(freq=440, ms=120, vol=0.5, kind="sine"):
    """Return a pygame.Sound containing a sine/square wave tone."""
    rate = 44_100
    n    = int(rate * ms / 1000)
    buf  = array.array("h")
    amp  = int(32_767 * vol)
    two_pi = 2 * math.pi
    for i in range(n):
        t = i / rate
        x = two_pi * freq * t
        sample = math.sin(x) if kind == "sine" else (1 if math.sin(x) >= 0 else -1)
        buf.append(int(amp * sample))
    return pygame.mixer.Sound(buffer=buf)

# Retro beeps & boops (unchanged)
SND_JUMP  = synth_tone(880,  90)
SND_HAMR  = synth_tone(660, 100)
SND_SWAP  = synth_tone(550,  90)
SND_KOOPA = synth_tone(760,  80)
SND_GOOM  = synth_tone(640,  80)
SND_CHOMP = synth_tone(420, 100)
SND_HURT  = synth_tone(300, 140, 0.5)
SND_VICT  = synth_tone(1200, 350)
SND_DEFE  = synth_tone(200,  350)

# ─── Chiptune music loop ────────────────────────────────────────
def build_music_loop():
    """Generate an 8‑second square‑wave melody and stream it as music."""
    bpm = 132
    quarter = 60_000 // bpm           # milliseconds per quarter note
    pattern = [440, 523, 659, 587, 659, 784, 659, 523,
               440, 523, 659, 880, 784, 659, 587, 523]  # simple hook
    notes = []
    for f in pattern:
        notes.append(synth_tone(f, quarter, 0.35, kind="square"))
    # stitch samples together into one long array
    raw = array.array("h")
    for snd in notes:
        raw.frombytes(snd.get_raw())
    music = pygame.mixer.Sound(buffer=raw)
    music.play(loops=-1)
build_music_loop()

# ─────────────────────────────────────────────────────────────────
# PAPER SPRITES & BACKGROUND
# ─────────────────────────────────────────────────────────────────
def outlined(func):
    """Decorator: draw shape twice – thick black outline then coloured fill."""
    def wrapper(surf, colour, *args, **kwargs):
        func(surf, BLACK, *args, **kwargs, width=0, inflate=6)
        func(surf, colour, *args, **kwargs, width=0, inflate=0)
    return wrapper

def draw_circle(surf, colour, centre, radius, *, width=0, inflate=0):
    x,y = centre
    pygame.draw.circle(surf, colour, (x,y), radius+inflate, width)

def draw_ellipse(surf, colour, rect, *, width=0, inflate=0):
    r = pygame.Rect(rect).inflate(inflate, inflate)
    pygame.draw.ellipse(surf, colour, r, width)

def draw_polygon(surf, colour, points, *, width=0, inflate=0):
    if inflate:
        cx = sum(x for x,_ in points)/len(points)
        cy = sum(y for _,y in points)/len(points)
        pts = []
        for x,y in points:
            dx,dy = x-cx, y-cy
            d = math.hypot(dx,dy)
            if d: dx,dy = dx/d, dy/d
            pts.append((x+dx*inflate, y+dy*inflate))
    else:
        pts = points
    pygame.draw.polygon(surf, colour, pts, width)

draw_circle   = outlined(draw_circle)
draw_ellipse  = outlined(draw_ellipse)
draw_polygon  = outlined(draw_polygon)

def make_sprite(shape, colour, w=90, h=90):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    if shape == "mario":
        draw_circle(surf, colour, (w//2, h//2), w//2-6)
        draw_rect_hat = pygame.Rect(w*0.3, h*0.2, w*0.4, h*0.25)
        draw_ellipse(surf, WHITE, draw_rect_hat)
    elif shape == "goomba":
        draw_ellipse(surf, colour, (0, h*0.3, w, h*0.7))
        draw_rect = pygame.Rect(w*0.2, h*0.05, w*0.6, h*0.28)
        draw_ellipse(surf, (139,69,19), draw_rect)
    elif shape == "koopa":
        draw_circle(surf, colour, (w//2,h//2), w//2-6)
        draw_circle(surf, (20,180,20), (w//2,h//2), w//2-12)
    elif shape == "goomba_small":
        draw_ellipse(surf, colour, (0,h*0.25,w,h*0.75))
    elif shape == "chomp":
        draw_circle(surf, colour, (w//2,h//2), w//2-6)
        draw_polygon(surf, WHITE, [(w*0.2,h*0.5),(w*0.5,h*0.1),(w*0.8,h*0.5)])
    return surf

def drop_shadow(surf, offset=(5,5), alpha=90):
    s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    s.fill((0,0,0,alpha))
    return s, offset

# Pre‑built paper sprites
SPR_MARIO  = make_sprite("mario", STICKER_RED)
SPR_GOOMB  = make_sprite("goomba", (160, 82, 45))
SPR_KOOPA  = make_sprite("koopa", STICKER_GREEN)
SPR_GOOMPA = make_sprite("goomba_small", (210,105,30))
SPR_CHOMP  = make_sprite("chomp", (70,70,70))

# Layered background – three parallax stripes w/ outlines
def draw_background():
    BG = pygame.Surface((WW, WH))
    # sky
    BG.fill(STICKER_BLUE)
    # far hills
    draw_polygon(BG, (50,180,88),
                 [(0,WH*0.55),(WW*0.3,WH*0.45),(WW*0.6,WH*0.55),(WW,WH*0.48),(WW,WH),(0,WH)])
    # mid hills
    draw_polygon(BG, (34,139,34),
                 [(0,WH*0.63),(WW*0.25,WH*0.5),(WW*0.55,WH*0.63),(WW,WH*0.55),(WW,WH),(0,WH)])
    # grass foreground
    pygame.draw.rect(BG, (80,200,80), (0, WH*0.7, WW, WH*0.3))
    pygame.draw.rect(BG, BLACK, (0, WH*0.7, WW, WH*0.3), 4)
    return BG
SPR_BG = draw_background()

# ─────────────────────────────────────────────────────────────────
# GAME DATA CLASSES
# ─────────────────────────────────────────────────────────────────
class Fighter:
    def __init__(self, name, max_hp, sprite):
        self.name   = name
        self.max_hp = max_hp
        self.hp     = max_hp
        self.base   = sprite
        self.scale  = 1.0           # dynamic scale for squash‑and‑stretch
        self.flash  = 0.0           # white flash timer on hit
    def alive(self): return self.hp > 0
    def take(self, dmg):
        self.hp = max(0, self.hp - dmg)
        self.flash = 0.3
        SND_HURT.play()

mario    = Fighter("Mario", MARIO_MAX_HP, SPR_MARIO)
goomboss = Fighter("Goomboss", GOOMBOSS_MAX_HP, SPR_GOOMB)

PARTNERS = {
    "Koopa":  Fighter("Koopa", 15, SPR_KOOPA),
    "Goomba": Fighter("Goomba",15, SPR_GOOMPA),
    "Chain Chomp": Fighter("Chain Chomp", 15, SPR_CHOMP)
}
active_partner = "Koopa"

# ─────────────────────────────────────────────────────────────────
# PARTICLE NOTES
# ─────────────────────────────────────────────────────────────────
notes = []  # list of (x,y,vy,life)

def spawn_notes(cx, cy, count=3):
    for _ in range(count):
        x = cx + random.randint(-8,8)
        y = cy - random.randint(0,20)
        vy = random.uniform(-40,-20)
        notes.append([x,y,vy,1.0])

def update_notes(dt):
    for n in notes[:]:
        n[3] -= dt
        n[1] += n[2]*dt
        if n[3] <= 0: notes.remove(n)

def draw_notes():
    for x,y,_,life in notes:
        scale = 1.2*life
        h = 14*scale
        pygame.draw.circle(screen, STICKER_YELLOW, (int(x),int(y)), int(4*scale))
        pygame.draw.rect(screen, STICKER_YELLOW,
                         (x-2*scale, y, 4*scale, h), 0)

# ─────────────────────────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────────────────────────
def draw_hp_bar(ftr, x, y):
    w,h = 150, 18
    pct = ftr.hp / ftr.max_hp
    pygame.draw.rect(screen, BLACK, (x-3,y-3,w+6,h+6), 0, border_radius=6)
    fill_w = int(w * pct)
    colour = HP_GREEN if pct>0.5 else HP_MID if pct>0.25 else HP_RED
    pygame.draw.rect(screen, colour, (x,y,fill_w,h), 0, border_radius=4)
    pygame.draw.rect(screen, WHITE, (x,y,w,h), 2, border_radius=4)
    txt = font_small.render(f"{ftr.name} {ftr.hp}/{ftr.max_hp}", True, BLACK)
    screen.blit(txt, (x+4, y-h-4))

def sticker_panel(rect, bright=True):
    x,y,w,h = rect
    colour = STICKER_GREEN if bright else UI_BG
    pygame.draw.rect(screen, colour, rect, 0, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 4, border_radius=10)

def menu_box(opts, idx, rect):
    sticker_panel(rect)
    x,y,w,h = rect
    step = h//len(opts)
    for i,opt in enumerate(opts):
        col = STICKER_RED if i==idx else BLACK
        txt = font_medium.render(opt, True, col)
        screen.blit(txt, (x+14, y+i*step+8))

def center(surface, pos, scale=1, shadow=True):
    surf = surface
    if scale != 1:
        size = (int(surf.get_width()*scale), int(surf.get_height()*scale))
        surf = pygame.transform.smoothscale(surf, size)
    if shadow:
        sh,off = drop_shadow(surf, (6,6))
        screen.blit(sh, (pos[0]-sh.get_width()//2+off[0],
                         pos[1]-sh.get_height()//2+off[1]))
    screen.blit(surf, (pos[0]-surf.get_width()//2,
                       pos[1]-surf.get_height()//2))

# ─────────────────────────────────────────────────────────────────
# STATE MACHINE
# ─────────────────────────────────────────────────────────────────
state          = "PLAYER_MENU"  # or PARTNER_MENU / MARIO_ATTACK / PARTNER_ATTACK / ENEMY_ATTACK / WIN / LOSE
menu_idx       = 0
partner_idx    = 0
timer          = 0.0
action_window  = 0.0            # how long the player has to press Space for action command
damage_boost   = 0
anim_actor     = None

def reset_battle():
    global active_partner, state, menu_idx
    mario.hp = MARIO_MAX_HP
    goomboss.hp = GOOMBOSS_MAX_HP
    for p in PARTNERS.values(): p.hp = p.max_hp
    active_partner = "Koopa"
    state, menu_idx = "PLAYER_MENU", 0

reset_battle()

# ─────────────────────────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────────────────────────
running=True
while running:
    dt = clock.tick(FPS)/1000
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT: running=False
        elif ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE: running=False

        # ─── GAME INPUT ──────────────────────────────────────────
        if state=="PLAYER_MENU":
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_RIGHT: menu_idx=(menu_idx+1)%3
                if ev.key==pygame.K_LEFT:  menu_idx=(menu_idx-1)%3
                if ev.key in (pygame.K_RETURN,pygame.K_SPACE):
                    choice=("Jump","Hammer","Swap Partner")[menu_idx]
                    if choice=="Swap Partner":
                        state="PARTNER_MENU"; partner_idx=list(PARTNERS).index(active_partner)
                        SND_SWAP.play()
                    else:
                        dmg = MARIO_DAMAGE[choice]
                        damage_boost = 1       # base stylish bonus
                        goomboss.take(dmg)
                        SND_JUMP.play() if choice=="Jump" else SND_HAMR.play()
                        anim_actor = mario; mario.scale=1.2
                        timer, action_window = 0.6, 0.25
                        state="MARIO_ATTACK"
            # end keydown
        elif state=="PARTNER_MENU":
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_DOWN: partner_idx=(partner_idx+1)%len(PARTNERS)
                if ev.key==pygame.K_UP:   partner_idx=(partner_idx-1)%len(PARTNERS)
                if ev.key in (pygame.K_RETURN,pygame.K_SPACE):
                    active_partner=list(PARTNERS)[partner_idx]
                    state="ENEMY_ATTACK"
        elif state=="MARIO_ATTACK":
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_SPACE and action_window>0:
                damage_boost=2       # stylish success
                spawn_notes(WW*0.25, WH*0.45)
                action_window=0
        elif state in ("WIN","LOSE"):
            if ev.type==pygame.KEYDOWN and ev.key in (pygame.K_RETURN,pygame.K_SPACE):
                reset_battle()

    # ─── STATE UPDATES ───────────────────────────────────────────
    if state=="MARIO_ATTACK":
        timer-=dt; action_window-=dt
        if timer<=0:
            if goomboss.alive():
                # partner auto attack
                partner = PARTNERS[active_partner]
                goomboss.take(PARTNER_DAMAGE[partner.name]+(1 if damage_boost>1 else 0))
                {"Koopa":SND_KOOPA,"Goomba":SND_GOOM,"Chain Chomp":SND_CHOMP}[partner.name].play()
                anim_actor=partner; partner.scale=1.2
                timer, state = 0.6, "PARTNER_ATTACK"
            else:
                SND_VICT.play(); state="WIN"
    elif state=="PARTNER_ATTACK":
        timer-=dt
        if timer<=0:
            if goomboss.alive():
                state, timer = "ENEMY_ATTACK", 0.6
                anim_actor=goomboss; goomboss.scale=1.2
            else:
                SND_VICT.play(); state="WIN"
    elif state=="ENEMY_ATTACK":
        timer-=dt
        if timer<=0:
            mario.take(GOOMBOSS_DAMAGE)
            if mario.alive():
                state="PLAYER_MENU"
            else:
                SND_DEFE.play(); state="LOSE"
    # animate squash‑stretch & flashes
    for ftr in [mario,goomboss,*PARTNERS.values()]:
        if ftr.scale>1.0:
            ftr.scale = max(1.0, ftr.scale-3*dt)
        if ftr.flash>0:
            ftr.flash -= dt
    update_notes(dt)

    # ─── DRAW ────────────────────────────────────────────────────
    screen.blit(SPR_BG,(0,0))

    # Sprites + shadows (paper layers)
    center(goomboss.base,(WW*0.75,WH*0.48), goomboss.scale)
    center(mario.base,   (WW*0.25,WH*0.6 ), mario.scale)
    center(PARTNERS[active_partner].base,(WW*0.15,WH*0.48), PARTNERS[active_partner].scale)

    # flashes
    for ftr,pos in ((goomboss,(WW*0.75,WH*0.48)),
                    (mario,(WW*0.25,WH*0.6)),
                    (PARTNERS[active_partner],(WW*0.15,WH*0.48))):
        if ftr.flash>0:
            flash = pygame.Surface(ftr.base.get_size(),pygame.SRCALPHA)
            flash.fill((255,255,255,int(200*ftr.flash)))
            center(flash,pos, ftr.scale, shadow=False)

    draw_notes()

    # HP & UI
    draw_hp_bar(mario, 20, 30)
    draw_hp_bar(goomboss, WW-180, 30)

    if state=="PLAYER_MENU":
        menu_box(["Jump","Hammer","Swap"], menu_idx, (20, WH-130, 220, 100))
    elif state=="PARTNER_MENU":
        plist=list(PARTNERS)
        menu_box(plist, partner_idx, (20, WH-160, 220, 130))

    if state in ("WIN","LOSE"):
        msg="YOU WIN!" if state=="WIN" else "GAME OVER"
        txt=font_big.render(msg,True,WHITE)
        screen.blit(txt,(WW//2-txt.get_width()//2, WH//2-60))
        tip=font_small.render("Press Enter to play again",True,WHITE)
        screen.blit(tip,(WW//2-tip.get_width()//2, WH//2))

    pygame.display.flip()

pygame.quit(); sys.exit()
