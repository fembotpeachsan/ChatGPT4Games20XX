# snake_ps1_hummer.py – Koopa Engine 3.1 x Team Hummer Vibes
import pygame as pg, sys, random, numpy as np

GRID   = 18
TILE   = 32
W, H   = GRID*TILE, GRID*TILE
FPS    = 60

# — PS1 Team Hummer Vibes Colors —
BG      = (32, 36, 54)
SNAKE_I = (238, 221, 130)
SNAKE_O = (80, 64, 32)
FOOD    = (244, 82, 66)
GRID_C  = (120, 120, 180)
TXT     = (255, 232, 155)

# --- Beep/Boop SFX (no files) ---
def sfx_beep(f=360, ms=80, v=0.6, sr=22050):
    t = np.linspace(0, ms/1000, int(sr*ms/1000), False)
    wave = (np.sign(np.sin(2*np.pi*f*t))*18000).astype(np.int16)
    snd = pg.mixer.Sound(wave)
    snd.set_volume(v)
    snd.play()

def sfx_boopsad(f=90, ms=320, v=0.4, sr=22050):
    t = np.linspace(0, ms/1000, int(sr*ms/1000), False)
    wave = ((np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*f*2*t))*9000).astype(np.int16)
    snd = pg.mixer.Sound(wave)
    snd.set_volume(v)
    snd.play()

# --- Init ---
pg.init()
pg.mixer.pre_init(22050, -16, 1, 256)
pg.mixer.init()
screen = pg.display.set_mode((W, H))
pg.display.set_caption("SNAKE – Team Hummer PS1 Vibe")
clock = pg.time.Clock()
font  = pg.font.SysFont("Consolas", 28, bold=1)

def draw_grid():
    for x in range(0, W, TILE):
        pg.draw.line(screen, GRID_C, (x, 0), (x, H), 3)
    for y in range(0, H, TILE):
        pg.draw.line(screen, GRID_C, (0, y), (W, y), 3)

def draw_snake(snake):
    for x, y in snake:
        # Outline
        pg.draw.rect(screen, SNAKE_O, (x*TILE+1, y*TILE+1, TILE-2, TILE-2), border_radius=6)
        # Fill
        pg.draw.rect(screen, SNAKE_I, (x*TILE+5, y*TILE+5, TILE-10, TILE-10), border_radius=8)

def draw_food(food, vibe_mode=False, frame=0):
    x, y = food
    color = FOOD
    if vibe_mode:
        # Trippy color cycling for "Vibes Mode"
        color = (244, 82 + int(120*np.sin(frame/8)), 66 + int(120*np.cos(frame/16)))
    pg.draw.ellipse(screen, color, (x*TILE+7, y*TILE+7, TILE-14, TILE-14))

def game_over_screen(score):
    sfx_boopsad()
    screen.fill(BG)
    msg = font.render("GAME OVER", True, TXT)
    scr = font.render(f"Score: {score}", True, TXT)
    yq  = font.render("Y = Restart   N = Quit", True, TXT)
    screen.blit(msg, ((W-msg.get_width())//2, H//2-60))
    screen.blit(scr, ((W-scr.get_width())//2, H//2))
    screen.blit(yq, ((W-yq.get_width())//2, H//2+50))
    pg.display.flip()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_y, pg.K_RETURN): return True
                if event.key in (pg.K_n, pg.K_ESCAPE): return False

def main():
    direction = (1, 0)
    snake = [(GRID//2, GRID//2)]
    food = (random.randint(0, GRID-1), random.randint(0, GRID-1))
    score, move_cool, vibe_mode = 0, 0, False
    frame = 0

    while True:
        clock.tick(FPS)
        frame += 1
        for event in pg.event.get():
            if event.type == pg.QUIT: sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_w, pg.K_UP)    and direction != (0, 1):  direction = (0, -1)
                if event.key in (pg.K_s, pg.K_DOWN)  and direction != (0, -1): direction = (0, 1)
                if event.key in (pg.K_a, pg.K_LEFT)  and direction != (1, 0):  direction = (-1, 0)
                if event.key in (pg.K_d, pg.K_RIGHT) and direction != (-1, 0): direction = (1, 0)
                if event.key == pg.K_v: vibe_mode = not vibe_mode

        move_cool += 1
        if move_cool >= 10:
            move_cool = 0
            nx, ny = (snake[0][0]+direction[0]) % GRID, (snake[0][1]+direction[1]) % GRID
            new_head = (nx, ny)
            if new_head in snake:
                if not game_over_screen(score): sys.exit()
                return
            snake.insert(0, new_head)
            if new_head == food:
                score += 1
                sfx_beep(370+score*10)
                food = snake[0]
                while food in snake:
                    food = (random.randint(0, GRID-1), random.randint(0, GRID-1))
            else:
                snake.pop()

        # --- Draw ---
        if vibe_mode:
            c = (BG[0]+frame%20, BG[1]+(frame*2)%30, BG[2]+(frame*3)%36)
            screen.fill(c)
        else:
            screen.fill(BG)
        draw_grid()
        draw_snake(snake)
        draw_food(food, vibe_mode, frame)
        score_surf = font.render(f"Score: {score}", True, TXT)
        screen.blit(score_surf, (8, 8))
        if vibe_mode:
            vtxt = font.render("VIBES MODE ON", True, (255, 180, 130))
            screen.blit(vtxt, (W-vtxt.get_width()-8, 8))
        pg.display.flip()

if __name__ == "__main__":
    while True:
        main()
