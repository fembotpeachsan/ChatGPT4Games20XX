import pygame
import sys
import math
import array

# Initialize audio
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

def make_sound(freq=440, dur_ms=100, vol=0.5):
    sr = 44100
    n = int(sr * dur_ms / 1000)
    buf = array.array('h', [0]*n)
    for i in range(n):
        t = i/sr
        buf[i] = int(vol*32767*math.sin(2*math.pi*freq*t))
    return pygame.mixer.Sound(buffer=buf)

# Settings
WIDTH, HEIGHT = 800, 600
FPS = 60
PADDLE_W, PADDLE_H = 10, 100
BALL_SIZE = 20
PADDLE_SPEED = 7
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
WIN_SCORE = 10

# Colors
WHITE = (255,255,255)
GRAY = (150,150,150)
BLACK = (0,0,0)

# Fonts
font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 50)

# Sounds
bounce_sound = make_sound(440, 100, 0.5)
score_sound = make_sound(220, 300, 0.7)
SOUND_ON = True

# Globals
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pygame Pong with Audio')

# Game state
left_paddle = right_paddle = ball = None
ball_vx = ball_vy = 0
left_score = right_score = 0

# Helpers
def init_game():
    global left_paddle, right_paddle, ball, ball_vx, ball_vy, left_score, right_score
    left_paddle = pygame.Rect(50, HEIGHT//2 - PADDLE_H//2, PADDLE_W, PADDLE_H)
    right_paddle = pygame.Rect(WIDTH-50-PADDLE_W, HEIGHT//2 - PADDLE_H//2, PADDLE_W, PADDLE_H)
    ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
    ball_vx = -BALL_SPEED_X
    ball_vy = BALL_SPEED_Y
    left_score = right_score = 0
    return True  # continue game


def draw():
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH//2,0),(WIDTH//2,HEIGHT))
    ls = font_large.render(str(left_score), True, WHITE)
    rs = font_large.render(str(right_score), True, WHITE)
    screen.blit(ls, (WIDTH//4 - ls.get_width()//2, 20))
    screen.blit(rs, (WIDTH*3//4 - rs.get_width()//2, 20))
    pygame.display.flip()


def show_end_screen(clock, winner):
    prompt = f"{winner} wins! Play again? Y/N"
    while True:
        screen.fill(BLACK)
        text = font_medium.render(prompt, True, WHITE)
        screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False  # quit entire
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_y:
                    return True   # restart
                if e.key == pygame.K_n:
                    return False  # quit
        clock.tick(FPS)


def game_loop(clock):
    init_game()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and left_paddle.top>0:
            left_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_s] and left_paddle.bottom<HEIGHT:
            left_paddle.y += PADDLE_SPEED
        # AI
        if ball.centery>right_paddle.centery and right_paddle.bottom<HEIGHT:
            right_paddle.y += PADDLE_SPEED
        if ball.centery<right_paddle.centery and right_paddle.top>0:
            right_paddle.y -= PADDLE_SPEED
        # Move ball
        global ball_vx, ball_vy, left_score, right_score
        ball.x += ball_vx; ball.y += ball_vy
        # Walls
        if ball.top<=0 or ball.bottom>=HEIGHT:
            ball_vy*=-1
            if SOUND_ON: bounce_sound.play()
        # Paddles
        if ball.colliderect(left_paddle) and ball_vx<0:
            ball_vx*=-1; SOUND_ON and bounce_sound.play()
        if ball.colliderect(right_paddle) and ball_vx>0:
            ball_vx*=-1; SOUND_ON and bounce_sound.play()
        # Score
        if ball.left<=0:
            right_score+=1; SOUND_ON and score_sound.play(); ball.center=(WIDTH//2,HEIGHT//2); ball_vx=BALL_SPEED_X
        if ball.right>=WIDTH:
            left_score+=1; SOUND_ON and score_sound.play(); ball.center=(WIDTH//2,HEIGHT//2); ball_vx=-BALL_SPEED_X
        draw()
        # End check
        if left_score>=WIN_SCORE or right_score>=WIN_SCORE:
            winner='Left Player' if left_score>=WIN_SCORE else 'Right AI'
            if not show_end_screen(clock, winner): return False
            init_game()
        clock.tick(FPS)
    return True


def show_menu(clock):
    global SOUND_ON
    options=['Play', f"Sound: {'On' if SOUND_ON else 'Off'}", 'Quit']
    sel=0; rects=[]
    while True:
        screen.fill(BLACK)
        title = font_large.render('Pygame Pong', True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH//2,HEIGHT//4)))
        rects.clear()
        for i,opt in enumerate(options):
            col=WHITE if i==sel else GRAY
            surf=font_medium.render(opt, True, col)
            r=surf.get_rect(center=(WIDTH//2,HEIGHT//2+i*60)); screen.blit(surf,r); rects.append(r)
        credit=font_medium.render('[@Team Flames 20XX[C] ]', True, WHITE)
        screen.blit(credit,credit.get_rect(center=(WIDTH//2,HEIGHT-50)))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: return False
            if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                x,y=e.pos
                for i,r in enumerate(rects):
                    if r.collidepoint(x,y): sel=i; break
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_UP: sel=(sel-1)%len(options)
                if e.key==pygame.K_DOWN: sel=(sel+1)%len(options)
                if e.key==pygame.K_RETURN:
                    pass
            if sel==0 and (e.type==pygame.KEYDOWN and e.key==pygame.K_RETURN or e.type==pygame.MOUSEBUTTONDOWN and e.button==1):
                return game_loop(clock)
            if sel==1 and (e.type==pygame.KEYDOWN and e.key==pygame.K_RETURN or e.type==pygame.MOUSEBUTTONDOWN and e.button==1):
                SOUND_ON=not SOUND_ON; options[1]=f"Sound: {'On' if SOUND_ON else 'Off'}"
            if sel==2 and (e.type==pygame.KEYDOWN and e.key==pygame.K_RETURN or e.type==pygame.MOUSEBUTTONDOWN and e.button==1):
                return False
        clock.tick(FPS)


def main():
    clock=pygame.time.Clock()
    while show_menu(clock): pass
    pygame.quit(); sys.exit()

if __name__=='__main__':
    main()
