import pygame, sys, math, time, random

# --- Config ---
WIDTH, HEIGHT = 480, 320
BG = (198, 217, 159)
BORDER = (110, 130, 80)
TEXT = (32, 44, 28)
ENEMY = (60, 210, 240)
CHARIZARD = (230, 90, 40)
WHITE = (245, 245, 230)
OUTLINE = (48, 80, 40)
YELLOW = (245, 240, 90)
TITLERED = (220, 40, 40)
TITLEYELLOW = (255, 230, 90)
TITLESHADOW = (120, 15, 15)
GREY = (80, 90, 90)
NIDORINO = (110, 60, 150)
GENGAR = (90, 40, 120)
PIKACHU = (250, 210, 50)
RED = (210, 45, 40)
GAMEFREAK = (30, 60, 130)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokémon Red Full Intro - CAT SAMA Edition")
clock = pygame.time.Clock()
font_big = pygame.font.SysFont("Courier New", 56, bold=True)
font = pygame.font.SysFont("Courier New", 32, bold=True)
font2 = pygame.font.SysFont("Courier New", 24, bold=True)
font3 = pygame.font.SysFont("Courier New", 20, bold=True)

# --- Helper Draw Functions ---
def draw_charizard(surface, x, y, scale=1.0):
    pygame.draw.ellipse(surface, CHARIZARD, (x-25*scale, y, 60*scale, 80*scale))
    pygame.draw.circle(surface, CHARIZARD, (int(x+15*scale), int(y-18*scale)), int(22*scale))
    pygame.draw.ellipse(surface, WHITE, (x-7*scale, y+20*scale, 32*scale, 48*scale))
    pygame.draw.polygon(surface, (100,200,140), [(x+15*scale,y-5*scale), (x+80*scale,y-55*scale), (x+45*scale,y+10*scale)])
    pygame.draw.line(surface, CHARIZARD, (x-20*scale,y+50*scale), (x-40*scale,y+85*scale), int(8*scale))
    pygame.draw.circle(surface, (255,180,70), (int(x-40*scale),int(y+85*scale)), int(10*scale))
    pygame.draw.circle(surface, OUTLINE, (int(x+24*scale), int(y-25*scale)), int(3*scale))
    pygame.draw.circle(surface, (255,240,90), (int(x-36*scale),int(y+88*scale)), int(5*scale))

def draw_nidorino(surface, x, y, scale=1.0, flip=False):
    pts = [(x-22*scale, y+38*scale), (x+20*scale, y+18*scale), (x+25*scale, y-2*scale), (x-15*scale, y-14*scale)]
    if flip: pts = [(WIDTH-(p[0]),p[1]) for p in pts]
    pygame.draw.polygon(surface, NIDORINO, pts)
    pygame.draw.circle(surface, NIDORINO, (int(x+12*scale), int(y-9*scale)), int(14*scale))
    pygame.draw.circle(surface, WHITE, (int(x+19*scale), int(y-13*scale)), int(3*scale))
    pygame.draw.line(surface, OUTLINE, (int(x+2*scale), int(y-12*scale)), (int(x-12*scale), int(y-28*scale)), int(4*scale))

def draw_gengar(surface, x, y, scale=1.0):
    pygame.draw.circle(surface, GENGAR, (int(x), int(y)), int(25*scale))
    pygame.draw.polygon(surface, GENGAR, [(x-18*scale,y-20*scale),(x-12*scale,y-36*scale),(x-6*scale,y-18*scale)])
    pygame.draw.polygon(surface, GENGAR, [(x+10*scale,y-21*scale),(x+20*scale,y-36*scale),(x+13*scale,y-12*scale)])
    pygame.draw.ellipse(surface, WHITE, (x-13*scale, y-3*scale, 11*scale, 6*scale))
    pygame.draw.ellipse(surface, WHITE, (x+2*scale, y-3*scale, 11*scale, 6*scale))
    pygame.draw.line(surface, OUTLINE, (int(x-10*scale), int(y+15*scale)), (int(x+10*scale), int(y+15*scale)), int(2*scale))

def draw_pikachu(surface, x, y, scale=1.0):
    pygame.draw.ellipse(surface, PIKACHU, (x-18*scale, y, 36*scale, 32*scale))
    pygame.draw.circle(surface, PIKACHU, (int(x), int(y-12*scale)), int(15*scale))
    pygame.draw.ellipse(surface, YELLOW, (x+8*scale, y+20*scale, 11*scale, 7*scale))
    pygame.draw.line(surface, (110,80,35), (x+8*scale,y-15*scale),(x+28*scale,y-33*scale),3)
    pygame.draw.circle(surface, (255,0,0), (int(x-7*scale), int(y+10*scale)), int(4*scale))
    pygame.draw.circle(surface, (255,0,0), (int(x+9*scale), int(y+10*scale)), int(4*scale))
    pygame.draw.circle(surface, OUTLINE, (int(x-7*scale), int(y-20*scale)), int(2*scale))

def draw_chatgpt_logo(surface, x, y, r=33):
    for i in range(6):
        angle = math.radians(i*60 + 15)
        ox = x + int(math.cos(angle)*r*0.7)
        oy = y + int(math.sin(angle)*r*0.7)
        rect = pygame.Rect(0,0,r*1.1,r*0.45)
        rect.center = (ox, oy)
        pygame.draw.ellipse(surface, ENEMY, rect, 0)
    pygame.draw.circle(surface, BG, (x, y), int(r*0.65))
    pygame.draw.circle(surface, ENEMY, (x, y), int(r*0.45))

def draw_battle_bar(surface):
    pygame.draw.rect(surface, OUTLINE, (30, HEIGHT-88, WIDTH-60, 52), border_radius=12, width=3)
    txt = font2.render("CAT SAMA  VS.  CHATGPT", 1, TEXT)
    surface.blit(txt, ((WIDTH-txt.get_width())//2, HEIGHT-74))

def draw_title(surface, y, bounce=0):
    title = "POKéMON"
    surf_shadow = font_big.render(title, 1, TITLESHADOW)
    surface.blit(surf_shadow, ((WIDTH-surf_shadow.get_width())//2+5, y+5+bounce))
    surf = font_big.render(title, 1, TITLERED)
    surface.blit(surf, ((WIDTH-surf.get_width())//2, y+bounce))
    pygame.draw.circle(surface, TITLEYELLOW, (WIDTH//2-78, y+24+bounce), 7)
    sub = font.render("CAT SAMA VERSION", 1, TITLEYELLOW)
    surface.blit(sub, ((WIDTH-sub.get_width())//2, y+78+bounce))

def draw_press_start(surface, t):
    if int(t*2)%2==0:
        msg = font3.render("PRESS START", 1, TEXT)
        surface.blit(msg, ((WIDTH-msg.get_width())//2, HEIGHT-50))

def draw_gamefreak(surface, t):
    txt = font2.render("GAME FREAK", 1, GAMEFREAK)
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for i in range(2):
        pygame.draw.ellipse(surf, (255,255,255,160), (120+i*10,120,100,36), 0)
    surface.blit(surf, (0,0))
    surface.blit(txt, ((WIDTH-txt.get_width())//2, HEIGHT//2-10))

def draw_red(surface, x, y, scale=1.0):
    pygame.draw.rect(surface, RED, (x, y, 13*scale, 25*scale))
    pygame.draw.circle(surface, (180,180,180), (int(x+6*scale), int(y-5*scale)), int(7*scale))
    pygame.draw.rect(surface, (70,70,70), (x+3*scale, y-12*scale, 7*scale, 8*scale))
    pygame.draw.line(surface, (70,70,70), (x+6*scale, y-6*scale), (x+6*scale, y-12*scale), 3)

# --- Main Intro Sequence States ---
STATE_BOOT, STATE_GFREAK, STATE_NIDOGENG, STATE_TITLE, STATE_PIKACHU, STATE_REDWALK, STATE_BATTLE, STATE_START = range(8)

def run_intro():
    state = STATE_BOOT
    t0 = pygame.time.get_ticks()/1000
    running = True
    slide = 0

    while running:
        t = pygame.time.get_ticks()/1000 - t0
        dt = clock.tick(60)/1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if state == STATE_START and event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                running = False

        # --- BOOTUP FLASH ---
        if state == STATE_BOOT:
            screen.fill(WHITE if t<0.23 else BG)
            pygame.draw.rect(screen, BORDER, (22, 22, WIDTH-44, HEIGHT-44), border_radius=24, width=10)
            if t > 0.6:
                state = STATE_GFREAK
                t0 = pygame.time.get_ticks()/1000

        # --- GAME FREAK LOGO ---
        elif state == STATE_GFREAK:
            screen.fill(BG)
            draw_gamefreak(screen, t)
            if t > 1.6:
                state = STATE_NIDOGENG
                t0 = pygame.time.get_ticks()/1000

        # --- NIDORINO VS GENGAR SCENE ---
        elif state == STATE_NIDOGENG:
            screen.fill(BG)
            # Slide in Gengar + Nidorino (faux animation)
            gx = WIDTH//2 + int(60*math.sin(min(1,t)*2.2-0.7))
            gy = HEIGHT//2-22
            nx = WIDTH//2 - int(58*math.sin(min(1,t)*2.2-0.7))
            ny = HEIGHT//2+25
            draw_gengar(screen, gx, gy, 1.1)
            draw_nidorino(screen, nx, ny, 0.9)
            if t > 1.3:
                state = STATE_TITLE
                t0 = pygame.time.get_ticks()/1000

        # --- TITLE SCREEN ---
        elif state == STATE_TITLE:
            screen.fill(BG)
            pygame.draw.rect(screen, BORDER, (22, 22, WIDTH-44, HEIGHT-44), border_radius=24, width=10)
            bounce = -abs(math.sin(min(1.2, t)*2.5)*18)
            draw_title(screen, 62, bounce)
            draw_press_start(screen, t)
            if t > 1.4:
                state = STATE_PIKACHU
                t0 = pygame.time.get_ticks()/1000

        # --- PIKACHU JUMPS IN ---
        elif state == STATE_PIKACHU:
            screen.fill(BG)
            draw_title(screen, 62, 0)
            # Animate Pikachu jumping
            px = WIDTH//2 + int(math.sin(min(1.2,t)*3)*40)
            py = HEIGHT//2 + int(-abs(math.sin(t*3))*18)
            draw_pikachu(screen, px, py+20, 1.2)
            draw_press_start(screen, t)
            if t > 1.5:
                state = STATE_REDWALK
                t0 = pygame.time.get_ticks()/1000

        # --- RED WALKS IN ---
        elif state == STATE_REDWALK:
            screen.fill(BG)
            draw_title(screen, 62, 0)
            rx = int(40 + min(1.0, t)*320)
            draw_red(screen, rx, HEIGHT-95, 1.0)
            draw_pikachu(screen, rx+44, HEIGHT-85, 0.8)
            draw_press_start(screen, t)
            if t > 1.6:
                state = STATE_BATTLE
                t0 = pygame.time.get_ticks()/1000

        # --- BATTLE INTRO ANIMATION ---
        elif state == STATE_BATTLE:
            t_anim = t
            screen.fill(BG)
            pygame.draw.rect(screen, BORDER, (22, 22, WIDTH-44, HEIGHT-44), border_radius=24, width=10)
            slide_duration = 1.1
            slide_t = min(1, t_anim/slide_duration)
            enemy_x = int(WIDTH*0.70 - 160*(1-slide_t))
            enemy_y = 95
            char_x = int(WIDTH*0.30 + 160*(1-slide_t))
            char_y = 130

            draw_chatgpt_logo(screen, enemy_x, enemy_y, r=38)
            draw_charizard(screen, char_x, char_y)

            if t_anim > 1.0:
                draw_battle_bar(screen)

            # "Fight" flash stutter
            if 1.7 < t_anim % 2.5 < 2.0:
                pygame.draw.rect(screen, WHITE, (50,80,WIDTH-100,160), border_radius=24)

            if t_anim > 2.5:
                state = STATE_START
                t0 = pygame.time.get_ticks()/1000

        # --- PRESS START / REPLAY ---
        elif state == STATE_START:
            screen.fill(BG)
            pygame.draw.rect(screen, BORDER, (22, 22, WIDTH-44, HEIGHT-44), border_radius=24, width=10)
            draw_title(screen, 62)
            draw_press_start(screen, t)
            draw_charizard(screen, 90, HEIGHT-105, 0.7)
            draw_chatgpt_logo(screen, WIDTH-110, HEIGHT-90, r=24)

        pygame.display.flip()

while True:
    run_intro()
