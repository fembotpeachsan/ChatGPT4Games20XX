###############################################################################
#  🏓 60 FPS PS‑1‑style PONG – single‑file, no‑asset – by Koopa Engine (Cat)  #
###############################################################################
import pygame, sys, numpy as np, random

# ------------ configuration --------------------------------------------------
LOGICAL_W, LOGICAL_H = 320, 240        # internal PS1‑ish resolution
SCALE              = 2                 # window = 640×480
FPS                = 60
WIN_SCORE          = 5
PADDLE_W, PADDLE_H = 6, 40
BALL_SIZE          = 6
PADDLE_SPEED       = 3                 # px / frame (AI)
BALL_SPEED_START   = 2.5
BALL_SPEED_INC     = 0.25              # after each paddle hit
BEEP_FREQ_HIT      = 880               # Hz
BEEP_FREQ_SCORE    = 440               # Hz
BEEP_LEN_MS        = 80
VIBES_DEFAULT_ON   = True              # background colour cycling

# ------------ square‑wave synth ---------------------------------------------
def make_beep(freq=BEEP_FREQ_HIT, ms=BEEP_LEN_MS, vol=0.3, sr=44100):
    n = int(sr * ms / 1000)
    t = np.arange(n, dtype=np.float32) / sr
    wave = np.sign(np.sin(2 * np.pi * freq * t))      # square
    samples = (vol * 32767 * wave).astype(np.int16)
    stereo = np.repeat(samples[:, None], 2, axis=1)   # 2‑channel
    return pygame.sndarray.make_sound(stereo)

# ------------ entities -------------------------------------------------------
class Paddle(pygame.Rect):
    def __init__(self, x):
        super().__init__(x, LOGICAL_H//2 - PADDLE_H//2, PADDLE_W, PADDLE_H)

class Ball(pygame.Rect):
    def __init__(self):
        super().__init__(0,0,BALL_SIZE,BALL_SIZE)
        self.reset()

    def reset(self, direction=random.choice((-1,1))):
        self.center = (LOGICAL_W//2, LOGICAL_H//2)
        angle = random.uniform(-0.3, 0.3)
        self.dx = direction * BALL_SPEED_START * np.cos(angle)
        self.dy = BALL_SPEED_START * np.sin(angle)

# ------------ main -----------------------------------------------------------
def main():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 256)
    pygame.mixer.init()
    screen  = pygame.display.set_mode((LOGICAL_W*SCALE, LOGICAL_H*SCALE))
    surf    = pygame.Surface((LOGICAL_W, LOGICAL_H))  # render target
    clock   = pygame.time.Clock()
    font    = pygame.font.SysFont("arial", 16)

    left  = Paddle(12)
    right = Paddle(LOGICAL_W - 12 - PADDLE_W)
    ball  = Ball()
    score = [0,0]          # [player, AI]
    game_over = False
    vibes = VIBES_DEFAULT_ON
    hue = 0

    beep_hit   = make_beep(BEEP_FREQ_HIT)
    beep_score = make_beep(BEEP_FREQ_SCORE, vol=0.4)

    while True:
        # ---------- input ----------------------------------------------------
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if game_over and e.key in (pygame.K_y, pygame.K_n):
                    if e.key == pygame.K_y:
                        score = [0,0]; ball.reset(); game_over=False
                    else:
                        pygame.quit(); sys.exit()
                if e.key == pygame.K_v:
                    vibes = not vibes
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # ---------- update ---------------------------------------------------
        if not game_over:
            # player paddle follows mouse (clamped)
            mx, _ = pygame.mouse.get_pos()
            left.centery = int(mx / SCALE)
            left.clamp_ip(pygame.Rect(0,0,LOGICAL_W,LOGICAL_H))

            # simple AI: chase ball with capped speed
            if ball.centery > right.centery + 4:
                right.centery += PADDLE_SPEED
            elif ball.centery < right.centery - 4:
                right.centery -= PADDLE_SPEED
            right.clamp_ip(pygame.Rect(0,0,LOGICAL_W,LOGICAL_H))

            # move ball
            ball.x  += ball.dx
            ball.y  += ball.dy

            # collisions – top/bottom
            if ball.top <= 0 or ball.bottom >= LOGICAL_H:
                ball.dy *= -1; beep_hit.play()

            # collisions – paddles
            if ball.colliderect(left) and ball.dx < 0:
                ball.dx *= -1; ball.dx *= 1 + BALL_SPEED_INC
                offset = (ball.centery - left.centery) / (PADDLE_H/2)
                ball.dy = BALL_SPEED_START * offset
                beep_hit.play()

            if ball.colliderect(right) and ball.dx > 0:
                ball.dx *= -1; ball.dx *= 1 + BALL_SPEED_INC
                offset = (ball.centery - right.centery) / (PADDLE_H/2)
                ball.dy = BALL_SPEED_START * offset
                beep_hit.play()

            # scoring
            if ball.right < 0:
                score[1] += 1; beep_score.play(); ball.reset(direction=1)
            elif ball.left > LOGICAL_W:
                score[0] += 1; beep_score.play(); ball.reset(direction=-1)

            # game over?
            if score[0] >= WIN_SCORE or score[1] >= WIN_SCORE:
                game_over = True

        # ---------- draw -----------------------------------------------------
        # vibe background
        if vibes:
            hue = (hue + 0.5) % 360
            color = pygame.Color(0)
            color.hsva = (hue, 40, 20, 100)
            surf.fill(color)
        else:
            surf.fill((0,0,0))

        # net
        for y in range(0, LOGICAL_H, 8):
            surf.fill((200,200,200), (LOGICAL_W//2-1, y, 2, 4))

        # paddles & ball
        pygame.draw.rect(surf, (255,255,255), left)
        pygame.draw.rect(surf, (255,255,255), right)
        pygame.draw.rect(surf, (255,255,255), ball)

        # scores
        p_text = font.render(str(score[0]), True, (255,255,255))
        a_text = font.render(str(score[1]), True, (255,255,255))
        surf.blit(p_text, (LOGICAL_W//4 - p_text.get_width()//2, 10))
        surf.blit(a_text, (3*LOGICAL_W//4 - a_text.get_width()//2, 10))

        # game‑over banner
        if game_over:
            msg = f"{'You' if score[0]>score[1] else 'AI'} win!  Y = restart  N = quit"
            overlay = font.render(msg, True, (255,255,0))
            surf.blit(overlay, (LOGICAL_W//2 - overlay.get_width()//2,
                                LOGICAL_H//2 - overlay.get_height()//2))

        # scale to window & flip
        pygame.transform.scale(surf, screen.get_size(), screen)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
