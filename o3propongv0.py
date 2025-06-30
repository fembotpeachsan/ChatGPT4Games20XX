#!/usr/bin/env python3
"""
PONG – Mouse vs AI · Vibes‑Only Edition  (2025)
Author : Cat‑sama + OpenAI o3
Single‑file, no‑asset Pong remake.
Controls
--------
Mouse Y   : Move left paddle
Esc / Q   : Quit
"""
import sys, random, math, array
import pygame as pg

# ─────────────── CONFIGURABLE CONSTANTS ────────────────
WIDTH, HEIGHT      = 640, 480
FPS                = 60
PADDLE_W, PADDLE_H = 12, 80
BALL_SIZE          = 12
AI_SPEED           = 6                   # max px/frame for CPU paddle
BALL_INIT_SPD      = 4.0
BALL_SPEED_INC     = 0.35                # speed up after every hit
MAX_SCORE          = 11                  # first to …
PALETTE_BG         = (8, 8, 16)
PALETTE_L_PADDLE   = (64, 255, 64)
PALETTE_R_PADDLE   = (255, 64, 64)
PALETTE_BALL       = (255, 255, 255)
CRT_ALPHA          = 60                  # scan‑line opacity; 0 = off

# ─────────────── SIMPLE SQUARE‑WAVE SFX ────────────────
def make_wave(freq=440, dur=0.06, vol=0.4, sr=44100, duty=0.5):
    n = int(sr * dur)
    buf = array.array("h")
    amp = int(vol * 32767)
    step = sr / freq
    for i in range(n):
        phase = (i % step) / step
        buf.append(amp if phase < duty else -amp)
    return pg.mixer.Sound(buffer=buf.tobytes())

# ─────────────── CORE GAME OBJECT ────────────────
class Pong:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 1, 512)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("PONG – Mouse vs AI (Vibes Only)")
        self.clock = pg.time.Clock()
        self.font  = pg.font.SysFont("Courier", 32, bold=True)
        self._build_crt()
        self._load_sfx()
        self.reset()

    def reset(self):
        self.l_score = self.r_score = 0
        self.ball_speed = BALL_INIT_SPD
        self.ball_dir   = random.choice((1, -1))
        self._spawn_ball()

    # ─── entities
    def _spawn_ball(self):
        self.ball = pg.Rect(WIDTH//2 - BALL_SIZE//2,
                            HEIGHT//2 - BALL_SIZE//2,
                            BALL_SIZE, BALL_SIZE)
        angle = random.uniform(-0.4, 0.4)
        self.vel = [self.ball_dir * self.ball_speed,
                    self.ball_speed * math.sin(angle)]
        self.ball_speed = BALL_INIT_SPD

    # ─── visuals
    def _build_crt(self):
        self.crt = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        for y in range(0, HEIGHT, 2):
            pg.draw.line(self.crt, (0,0,0,CRT_ALPHA), (0,y), (WIDTH,y))

    def _load_sfx(self):
        self.sfx_paddle = make_wave(880, 0.05, 0.4)
        self.sfx_wall   = make_wave(440, 0.05, 0.4, duty=0.3)
        self.sfx_score  = make_wave(220, 0.25, 0.5)

    # ─── main loop
    def run(self):
        while True:
            self._events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

    # ─── input
    def _events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit(); sys.exit()
            if e.type == pg.KEYDOWN and e.key in (pg.K_ESCAPE, pg.K_q):
                pg.quit(); sys.exit()

    # ─── update world
    def _update(self):
        mx, my = pg.mouse.get_pos()

        # left paddle follows mouse
        l_paddle = pg.Rect(20, my - PADDLE_H//2, PADDLE_W, PADDLE_H)
        l_paddle.clamp_ip(pg.Rect(0,0,WIDTH,HEIGHT))

        # simple AI: move towards ball with capped speed
        target_y = self.ball.centery
        r_paddle = getattr(self, "r_paddle",
                           pg.Rect(WIDTH-20-PADDLE_W, HEIGHT//2-PADDLE_H//2,
                                   PADDLE_W, PADDLE_H))
        if target_y < r_paddle.centery - AI_SPEED:
            r_paddle.y -= AI_SPEED
        elif target_y > r_paddle.centery + AI_SPEED:
            r_paddle.y += AI_SPEED
        r_paddle.clamp_ip(pg.Rect(0,0,WIDTH,HEIGHT))
        self.r_paddle = r_paddle
        self.l_paddle = l_paddle

        # move ball
        self.ball.x += int(self.vel[0])
        self.ball.y += int(self.vel[1])

        # wall collision
        if self.ball.top <= 0 or self.ball.bottom >= HEIGHT:
            self.vel[1] *= -1
            self.sfx_wall.play()

        # paddle collision
        if self.ball.colliderect(l_paddle) and self.vel[0] < 0:
            self._bounce(l_paddle)
        elif self.ball.colliderect(r_paddle) and self.vel[0] > 0:
            self._bounce(r_paddle)

        # score
        if self.ball.right < 0:
            self.r_score += 1
            self._point_scored(-1)
        elif self.ball.left > WIDTH:
            self.l_score += 1
            self._point_scored(1)

    def _bounce(self, paddle):
        # invert X, add English based on hit position
        offset = (self.ball.centery - paddle.centery) / (PADDLE_H/2)
        angle  = 0.25 * math.pi * offset
        speed  = math.hypot(*self.vel) + BALL_SPEED_INC
        self.vel = [-self.vel[0]/abs(self.vel[0]) * speed * math.cos(angle),
                    speed * math.sin(angle)]
        self.sfx_paddle.play()

    def _point_scored(self, direction):
        self.sfx_score.play()
        if self.l_score >= MAX_SCORE or self.r_score >= MAX_SCORE:
            self.l_score = self.r_score = 0   # simple “new match”
        self.ball_dir = direction
        self._spawn_ball()

    # ─── draw
    def _draw(self):
        self.screen.fill(PALETTE_BG)
        pg.draw.rect(self.screen, PALETTE_L_PADDLE, self.l_paddle)
        pg.draw.rect(self.screen, PALETTE_R_PADDLE, self.r_paddle)
        pg.draw.ellipse(self.screen, PALETTE_BALL, self.ball)
        # center line
        for y in range(0, HEIGHT, 30):
            pg.draw.rect(self.screen, (40,40,60),
                         pg.Rect(WIDTH//2 - 2, y, 4, 20))

        # scores
        l_text = self.font.render(str(self.l_score), True, PALETTE_L_PADDLE)
        r_text = self.font.render(str(self.r_score), True, PALETTE_R_PADDLE)
        self.screen.blit(l_text, l_text.get_rect(center=(WIDTH*0.25,40)))
        self.screen.blit(r_text, r_text.get_rect(center=(WIDTH*0.75,40)))

        # CRT overlay
        if CRT_ALPHA:
            self.screen.blit(self.crt, (0,0))
        pg.display.flip()

# ─────────────── ENTRY POINT ────────────────
if __name__ == "__main__":
    Pong().run()
