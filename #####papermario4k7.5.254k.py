#!/usr/bin/env python3
# paper_mario_battle.py
"""
Paper Mario‑style battle ‑ Mario (with partners) vs. Goomboss
-------------------------------------------------------------
REQUIRES:  Python 3.x, Pygame 2.x          (pip install pygame)
WINDOW:    800 × 450
CONTROLS:  ←/→ to change menu choice • ↑/↓ in partner list • Enter/Space confirm • Esc quit
OBJECTS:   Real surfaces for sprites (no rect placeholders) – swap with PNGs easily.
SOUND:     Retro beeps/boops generated in code via pygame.sndarray – no external files.
GAMEFLOW:  1) Mario picks action (Jump, Hammer, Swap Partner)
           2) If Jump/Hammer → Mario attacks, then active partner auto‑attacks.
              If Swap Partner → choose new partner (uses turn; partner skips)
           3) Goomboss attacks
           4) Repeat until Mario HP ≤ 0 (Game Over) or Goomboss HP ≤ 0 (You Win!)
"""

import pygame, math, array, sys, random, os

# --------------------------------------------------------------------------------------
# GLOBAL CONSTANTS
# --------------------------------------------------------------------------------------
WW, WH          = 800, 450
FPS             = 60
WHITE           = (255, 255, 255)
BLACK           = (0,   0,   0)
UI_BG           = (26,  26,  26)
UI_BORDER       = (240, 240, 240)
HP_GREEN        = (64,  200, 64)
HP_RED          = (200, 64,  64)

# Stats
MARIO_MAX_HP    = 20
GOOMBOSS_MAX_HP = 25
PARTNER_DAMAGE  = {"Koopa": 3, "Goomba": 2, "Chain Chomp": 4}
MARIO_DAMAGE    = {"Jump": 2, "Hammer": 3}
GOOMBOSS_DMG    = 3

# --------------------------------------------------------------------------------------
# INIT
# --------------------------------------------------------------------------------------
pygame.init()
pygame.mixer.init(frequency=44_100, size=-16, channels=1)
screen = pygame.display.set_mode((WW, WH))
pygame.display.set_caption("Paper Mario Battle – Mario vs. Goomboss")
clock  = pygame.time.Clock()
font_big   = pygame.font.SysFont("comicsansms", 32, bold=True)
font_small = pygame.font.SysFont("consolas", 18)

# --------------------------------------------------------------------------------------
# MINI SOUND SYNTH (sine wave → pygame.Sound)
# --------------------------------------------------------------------------------------
def tone(freq=880, ms=100, vol=0.6):
    rate = 44_100
    n    = int(rate * ms / 1000)
    buf  = array.array("h")
    amp  = int(32_767 * vol)
    for i in range(n):
        s = int(amp * math.sin(2 * math.pi * freq * (i / rate)))
        buf.append(s)
    return pygame.mixer.Sound(buffer=buf)

SND_JUMP  = tone(880, 80)
SND_HAMR  = tone(660, 90)
SND_SWAP  = tone(550, 80)
SND_KOOPA = tone(770, 70)
SND_GOOM  = tone(640, 70)
SND_CHOMP = tone(420, 90)
SND_HURT  = tone(300, 120, 0.5)
SND_VICT  = tone(1200, 300)
SND_DEFE  = tone(200, 300)

# --------------------------------------------------------------------------------------
# “SPRITE” FACTORY – tiny placeholder PNG‑like images made in‑memory
# --------------------------------------------------------------------------------------
def make_sprite(shape: str, rgb, w=80, h=80):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((0,0,0,0))
    if shape == "mario":
        pygame.draw.circle(surf, rgb, (w//2, h//2), w//2)
        pygame.draw.rect(surf, WHITE, (w//3, h//3, w//3, h//4))  # hat
    elif shape == "goomba":
        pygame.draw.ellipse(surf, rgb, (0, h*0.25, w, h*0.75))
        pygame.draw.rect(surf, (139,69,19), (w*0.2, h*0.1, w*0.6, h*0.25))
    elif shape == "koopa":
        pygame.draw.circle(surf, rgb, (w//2, h//2), w//2)
        pygame.draw.circle(surf, (0,150,0), (w//2, h//2), w//2, 6)
    elif shape == "chomp":
        pygame.draw.circle(surf, rgb, (w//2, h//2), w//2)
        pygame.draw.polygon(surf, WHITE, [(w*0.2,h*0.4),(w*0.5,h*0.2),(w*0.8,h*0.4)])
    elif shape == "bg":
        surf = pygame.Surface((WW, WH))
        surf.fill((135, 206, 235))
        pygame.draw.rect(surf, (80, 180, 80), (0, WH*0.6, WW, WH*0.4))
        # paper cut trees
        for x in range(0, WW, 120):
            pygame.draw.polygon(surf, (34,139,34),
                                [(x+60,WH*0.4),(x+80,WH*0.6),(x+40,WH*0.6)])
    return surf

# allow external PNG override via environment variables (optional)
def load_or_placeholder(env_key, shape, rgb, size=80):
    path = os.getenv(env_key)
    if path and os.path.isfile(path):
        return pygame.image.load(path).convert_alpha()
    return make_sprite(shape, rgb, size, size)

SPR_MARIO   = load_or_placeholder("PM_MARIO_PNG", "mario", (255, 50, 50))
SPR_GOOMB   = load_or_placeholder("PM_GOOMBOSS_PNG", "goomba", (160, 82, 45))
SPR_KOOPA   = load_or_placeholder("PM_KOOPA_PNG", "koopa", (255, 215, 0))
SPR_GOOMPA  = load_or_placeholder("PM_GOOM_PNG", "goomba", (210,105,30))
SPR_CHOMP   = load_or_placeholder("PM_CHOMP_PNG", "chomp", (70,70,70))
SPR_BG      = load_or_placeholder("PM_BG_PNG", "bg", (0,0,0), 10)

# --------------------------------------------------------------------------------------
# DATA STRUCTURES
# --------------------------------------------------------------------------------------
class Fighter:
    def __init__(self, name, hp, sprite):
        self.name   = name
        self.max_hp = hp
        self.hp     = hp
        self.sprite = sprite

    def take(self, dmg):
        self.hp = max(0, self.hp - dmg)
        SND_HURT.play()

    def alive(self):
        return self.hp > 0

# partners
PARTNERS = {
    "Koopa":  Fighter("Koopa", 15, SPR_KOOPA),
    "Goomba": Fighter("Goomba",15, SPR_GOOMPA),
    "Chain Chomp": Fighter("Chain Chomp", 15, SPR_CHOMP)
}

# game entities
mario    = Fighter("Mario", MARIO_MAX_HP, SPR_MARIO)
goomboss = Fighter("Goomboss", GOOMBOSS_MAX_HP, SPR_GOOMB)

active_partner = "Koopa"

# --------------------------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------------------------
def draw_hp_bar(entity, x, y):
    w,h = 140, 16
    pygame.draw.rect(screen, UI_BORDER, (x-2, y-2, w+4, h+4), 2)
    pct = entity.hp / entity.max_hp
    fill_w = int(w * pct)
    clr = HP_GREEN if pct > 0.5 else (200, 150, 50) if pct > 0.25 else HP_RED
    pygame.draw.rect(screen, clr, (x, y, fill_w, h))
    label = font_small.render(f"{entity.name}: {entity.hp}/{entity.max_hp}", True, WHITE)
    screen.blit(label, (x, y - 20))

def menu_box(options, sel_idx, rect):
    x,y,w,h = rect
    pygame.draw.rect(screen, UI_BG, rect)
    pygame.draw.rect(screen, UI_BORDER, rect, 2)
    step = h // len(options)
    for i, txt in enumerate(options):
        color = WHITE if i == sel_idx else (180,180,180)
        render = font_small.render(txt, True, color)
        screen.blit(render, (x+12, y+5 + i*step))

def center_pos(surf, base, offset=(0,0)):
    bx,by = base
    return (bx - surf.get_width()//2 + offset[0],
            by - surf.get_height()//2 + offset[1])

def reset_battle():
    mario.hp    = MARIO_MAX_HP
    goomboss.hp = GOOMBOSS_MAX_HP
    for p in PARTNERS.values():
        p.hp = p.max_hp
    return "Koopa"

# --------------------------------------------------------------------------------------
# MAIN LOOP STATE
# --------------------------------------------------------------------------------------
state            = "PLAYER_MENU"  # or "PARTNER_LIST" / "ANIMATING" / "GOOMBOSS_TURN" / "VICTORY" / "DEFEAT"
menu_idx         = 0
partner_idx      = 0
anim_timer       = 0
active_partner   = reset_battle()

# --------------------------------------------------------------------------------------
# LOOP
# --------------------------------------------------------------------------------------
running = True
while running:
    dt = clock.tick(FPS)/1000.0
    # -------------------------------- INPUT ---------------------------------
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE: running = False
            if state in ("VICTORY","DEFEAT"):
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    active_partner = reset_battle()
                    state, menu_idx = "PLAYER_MENU", 0
            elif state == "PLAYER_MENU":
                if ev.key in (pygame.K_RIGHT, pygame.K_LEFT):
                    menu_idx = (menu_idx + 1) % 3
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    choice = ("Jump","Hammer","Swap Partner")[menu_idx]
                    if choice == "Swap Partner":
                        state = "PARTNER_LIST"
                        partner_idx = list(PARTNERS).index(active_partner)
                        SND_SWAP.play()
                    else:
                        # Mario attack
                        dmg = MARIO_DAMAGE[choice]
                        goomboss.take(dmg)
                        (SND_JUMP if choice=="Jump" else SND_HAMR).play()
                        # queue partner auto attack if still alive
                        if goomboss.alive():
                            state = "ANIMATING"
                            anim_timer = 0.6
                        else:
                            SND_VICT.play()
                            state = "VICTORY"
            elif state == "PARTNER_LIST":
                if ev.key in (pygame.K_UP, pygame.K_DOWN):
                    partner_idx = (partner_idx + (1 if ev.key==pygame.K_DOWN else -1)) % len(PARTNERS)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    active_partner = list(PARTNERS)[partner_idx]
                    state, menu_idx = "GOOMBOSS_TURN", 0  # swapping uses turn; partner skips
            # no input during other states

    # ------------------------------ STATE TIMERS -----------------------------
    if state == "ANIMATING":
        anim_timer -= dt
        if anim_timer <= 0:
            # partner attacks
            partner = PARTNERS[active_partner]
            dmg = PARTNER_DAMAGE[partner.name]
            goomboss.take(dmg)
            {"Koopa":SND_KOOPA,"Goomba":SND_GOOM,"Chain Chomp":SND_CHOMP}[partner.name].play()
            if goomboss.alive():
                state = "GOOMBOSS_TURN"
            else:
                SND_VICT.play()
                state = "VICTORY"

    elif state == "GOOMBOSS_TURN":
        # simple wait then attack
        anim_timer += dt
        if anim_timer < 0.4:  # delay before attack
            pass
        else:
            mario.take(GOOMBOSS_DMG)
            SND_HURT.play()
            if mario.alive():
                state, menu_idx = "PLAYER_MENU", 0
                anim_timer = 0
            else:
                SND_DEFE.play()
                state = "DEFEAT"

    # ------------------------------ DRAW -------------------------------------
    screen.blit(SPR_BG, (0,0))

    # Sprites positions
    screen.blit(goomboss.sprite, center_pos(goomboss.sprite, (WW*0.75, WH*0.45)))
    screen.blit(mario.sprite,    center_pos(mario.sprite,    (WW*0.25, WH*0.55)))
    screen.blit(PARTNERS[active_partner].sprite,
                center_pos(PARTNERS[active_partner].sprite, (WW*0.15, WH*0.45), offset=(-30,-20)))

    # HP bars
    draw_hp_bar(mario,    30, 30)
    draw_hp_bar(goomboss, WW-190, 30)

    # Menus
    if state == "PLAYER_MENU":
        menu_box(["Jump","Hammer","Swap Partner"], menu_idx, (10, WH-110, 200, 90))
    elif state == "PARTNER_LIST":
        plist = list(PARTNERS)
        menu_box(plist, partner_idx, (10, WH-150, 200, 120))

    # Victory / defeat banners
    if state in ("VICTORY","DEFEAT"):
        txt = "YOU WIN!" if state=="VICTORY" else "GAME OVER"
        render = font_big.render(txt, True, WHITE)
        screen.blit(render, center_pos(render, (WW/2, WH/2)))
        tip = font_small.render("Press Enter to play again", True, WHITE)
        screen.blit(tip, center_pos(tip, (WW/2, WH/2+40)))

    pygame.display.flip()

pygame.quit()
sys.exit()
