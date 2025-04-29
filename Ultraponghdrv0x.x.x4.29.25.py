import pygame, sys, math, array, random

# === SETUP ===
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.set_num_channels(8)

# === SOUND ===
def make_sound(freq=440, duration_ms=90, volume=0.6):
    sample_rate = 44100
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = array.array("h")
    for i in range(n_samples):
        t = i / sample_rate
        buf.append(int(volume * 32767 * math.sin(2 * math.pi * freq * t)))
    return pygame.mixer.Sound(buffer=buf)

BOUNCE_SFX = make_sound(880)
SCORE_SFX = make_sound(440)
GAMEOVER_SFX = make_sound(220)

# === DISPLAY ===
GAME_W, GAME_H = 128, 96
SCALE = 5
WIN_W, WIN_H = GAME_W * SCALE, GAME_H * SCALE
FPS = 60

screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("ChatGPT Atari Pong v3.2")
playfield = pygame.Surface((GAME_W, GAME_H))
clock = pygame.time.Clock()

scanlines = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
for y in range(0, WIN_H, 4):
    pygame.draw.line(scanlines, (0, 0, 0, 30), (0, y), (WIN_W, y))

# === COLORS ===
BLACK, WHITE = (0,0,0), (255,255,255)

# === OBJECTS ===
BALL_SIZE, BALL_SPEED_INC = 3, 0.1
PADDLE_W, PADDLE_H, PADDLE_SPEED = 3, 18, 2

left_paddle = pygame.Rect(8, GAME_H//2 - PADDLE_H//2, PADDLE_W, PADDLE_H)
right_paddle = pygame.Rect(GAME_W-11, GAME_H//2 - PADDLE_H//2, PADDLE_W, PADDLE_H)
ball_pos, ball_vel = [GAME_W//2, GAME_H//2], [1,1]

score_font = pygame.font.SysFont("Courier", 36)
menu_font = pygame.font.SysFont("Courier", 28)

left_score, right_score, WIN_SCORE = 0, 0, 11

# === HELPERS ===
def reset_ball():
    global ball_pos, ball_vel
    ball_pos = [GAME_W//2, GAME_H//2]
    ball_vel = [random.choice([-1,1]), random.choice([-1,1])]
    SCORE_SFX.play()

def draw_playfield():
    playfield.fill(BLACK)
    pygame.draw.rect(playfield, WHITE, left_paddle)
    pygame.draw.rect(playfield, WHITE, right_paddle)
    pygame.draw.rect(playfield, WHITE, (*map(int, ball_pos), BALL_SIZE, BALL_SIZE))
    scaled = pygame.transform.scale(playfield, (WIN_W, WIN_H))
    screen.blit(scaled, (0,0))
    screen.blit(scanlines, (0,0))
    txt = score_font.render(f"{left_score}  {right_score}", True, WHITE)
    screen.blit(txt, (WIN_W//2 - txt.get_width()//2, 10))
    pygame.display.flip()

def game_over(winner):
    GAMEOVER_SFX.play()
    while True:
        screen.fill(BLACK)
        msg = score_font.render(f"PLAYER {winner} WINS!", True, WHITE)
        hint = menu_font.render("Y=Restart  N=Quit", True, WHITE)
        screen.blit(msg, (WIN_W//2-msg.get_width()//2, 200))
        screen.blit(hint,(WIN_W//2-hint.get_width()//2,260))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_y: return True
                if e.key==pygame.K_n: pygame.quit(); sys.exit()

def main_menu():
    while True:
        screen.fill(BLACK)
        title = score_font.render("Atari Pong", True, WHITE)
        prompt = menu_font.render("SPACE to Start", True, WHITE)
        screen.blit(title, (WIN_W//2-title.get_width()//2, 150))
        screen.blit(prompt,(WIN_W//2-prompt.get_width()//2,220))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: sys.exit()
            if e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE: return

# === MAIN LOOP ===
def main():
    global left_score, right_score, ball_pos, ball_vel
    while True:
        left_score = right_score = 0
        reset_ball()
        left_paddle.centery = right_paddle.centery = GAME_H//2
        main_menu()
        running = True
        while running:
            for e in pygame.event.get():
                if e.type==pygame.QUIT: sys.exit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] and left_paddle.top>0: left_paddle.y-=PADDLE_SPEED
            if keys[pygame.K_s] and left_paddle.bottom<GAME_H: left_paddle.y+=PADDLE_SPEED
            if keys[pygame.K_UP] and right_paddle.top>0: right_paddle.y-=PADDLE_SPEED
            if keys[pygame.K_DOWN] and right_paddle.bottom<GAME_H: right_paddle.y+=PADDLE_SPEED
            ball_pos[0]+=ball_vel[0]; ball_pos[1]+=ball_vel[1]
            if ball_pos[1]<=0 or ball_pos[1]>=GAME_H-BALL_SIZE:
                ball_vel[1]*=-1; BOUNCE_SFX.play()
            br=pygame.Rect(*ball_pos,BALL_SIZE,BALL_SIZE)
            if br.colliderect(left_paddle):
                ball_vel[0]=abs(ball_vel[0])+BALL_SPEED_INC
                ball_vel[1]=(br.centery-left_paddle.centery)/(PADDLE_H/2)*1.6; BOUNCE_SFX.play()
            if br.colliderect(right_paddle):
                ball_vel[0]=-abs(ball_vel[0])-BALL_SPEED_INC
                ball_vel[1]=(br.centery-right_paddle.centery)/(PADDLE_H/2)*1.6; BOUNCE_SFX.play()
            if ball_pos[0]<=0:right_score+=1;reset_ball()
            if ball_pos[0]>=GAME_W-BALL_SIZE:left_score+=1;reset_ball()
            if left_score==WIN_SCORE:running=game_over(1)
            if right_score==WIN_SCORE:running=game_over(2)
            draw_playfield(); clock.tick(FPS)

if __name__ == "__main__": main()
