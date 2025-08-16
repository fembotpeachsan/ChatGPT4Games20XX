#!/usr/bin/env python3
# Pong PSX Vibes — mouse vs AI, first-to-5, Y/N restart
# Files=off | 60 FPS | PS1-ish dithering/jitter | Procedural beeps
# BUG FIXED VERSION

import math, random, sys
import pygame
from array import array

# -----------------------------
# Config
# -----------------------------
BASE_W, BASE_H = 320, 240
SCALE          = 3
SCREEN_W, SCREEN_H = BASE_W*SCALE, BASE_H*SCALE
FPS = 60

PADDLE_W, PADDLE_H = 5, 38
BALL_SIZE          = 5

PADDLE_SPEED = 3.2      # (unused for mouse)
CPU_SPEED    = 2.6
BALL_SPEED   = 2.8
BALL_MAX_VY  = 3.6
SPEED_UP     = 1.06
WIN_SCORE    = 5

BG_COL   = (18,18,22)
FG_COL   = (220,220,220)
NET_COL  = (160,160,160)
OVERLAY  = (0,0,0,140)

# -----------------------------
# Tiny PS1-ish audio (procedural)
# -----------------------------
class Bleeps:
    def __init__(self):
        self.enabled = True
        self.hit = None
        self.wall = None
        self.point = None
        self.boot = None
        self.sr = 22050
        
        try:
            pygame.mixer.pre_init(self.sr, -16, 1, 512)
            pygame.mixer.init()
            self.hit   = self._tone(440, 45, 0.45, wave='square')
            self.wall  = self._tone(330, 35, 0.36, wave='square')
            self.point = self._chirp(900, 220, ms=220, vol=0.5)
            self.boot  = self._tone(640, 80, 0.35, wave='triangle')
        except Exception:
            self.enabled = False

    def _tone(self, hz, ms, vol, wave='square'):
        try:
            n = int(self.sr * ms / 1000)
            amp = int(30000 * max(0.0, min(1.0, vol)))
            buf = array('h', [0]*n)
            phase = 0.0
            inc = (2*math.pi*hz)/self.sr
            for i in range(n):
                if wave == 'square':
                    s = amp if math.sin(phase) >= 0 else -amp
                elif wave == 'triangle':
                    s = int(amp * (2/math.pi) * math.asin(math.sin(phase)))
                else:
                    s = int(amp * math.sin(phase))
                buf[i] = s
                phase += inc
            return pygame.mixer.Sound(buffer=buf.tobytes())
        except Exception:
            return None

    def _chirp(self, f0, f1, ms=240, vol=0.5):
        try:
            n = int(self.sr * ms / 1000)
            amp = int(30000 * max(0.0, min(1.0, vol)))
            buf = array('h', [0]*n)
            phase = 0.0
            for i in range(n):
                t = i / max(1, n-1)
                hz = f0 * (f1/f0)**t
                phase += (2*math.pi*hz)/self.sr
                s = int(amp * (2/math.pi) * math.asin(math.sin(phase)))
                buf[i] = s
            return pygame.mixer.Sound(buffer=buf.tobytes())
        except Exception:
            return None

    def play(self, s):
        if self.enabled and s:
            try:
                s.play()
            except Exception:
                pass

# -----------------------------
# Helpers
# -----------------------------
def clamp(v, lo, hi): 
    return max(lo, min(hi, v))

def reset_ball(to_left=False):
    angle = random.uniform(-0.35*math.pi, 0.35*math.pi)
    # Ensure minimum horizontal velocity to prevent stuck ball
    vx = max(abs(BALL_SPEED * math.cos(angle)), BALL_SPEED * 0.7)
    vx *= -1 if to_left else 1
    vy = BALL_SPEED * math.sin(angle)
    return BASE_W//2 - BALL_SIZE//2, BASE_H//2 - BALL_SIZE//2, vx, vy

def make_scanlines():
    s = pygame.Surface((BASE_W, BASE_H), pygame.SRCALPHA)
    for y in range(0, BASE_H, 2):
        pygame.draw.line(s, (0,0,0,40), (0,y), (BASE_W,y))
    return s

def make_dither():
    bayer4 = [
        [ 0,  8,  2, 10],
        [12,  4, 14,  6],
        [ 3, 11,  1,  9],
        [15,  7, 13,  5]
    ]
    s = pygame.Surface((BASE_W, BASE_H), pygame.SRCALPHA)
    for y in range(BASE_H):
        for x in range(BASE_W):
            a = 18 if bayer4[y&3][x&3] < 8 else 0
            if a: 
                s.set_at((x,y), (0,0,0,a))
    return s

def draw_net(target):
    step = 8
    for y in range(0, BASE_H, step):
        pygame.draw.rect(target, NET_COL, (BASE_W//2-1, y, 2, step//2), 0)

# -----------------------------
# Game
# -----------------------------
def main():
    pygame.init()
    pygame.display.set_caption("Pong — PSX Vibes (mouse vs AI)")
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
    
    # Proper surface conversion
    surf = pygame.Surface((BASE_W, BASE_H))
    surf = surf.convert()
    
    clock = pygame.time.Clock()
    
    # Font initialization with fallback
    font = pygame.font.SysFont(None, 18)
    if not font:
        font = pygame.font.Font(None, 18)
    big = pygame.font.SysFont(None, 28)
    if not big:
        big = pygame.font.Font(None, 28)

    pygame.mouse.set_visible(False)

    scanlines = make_scanlines()
    dither    = make_dither()
    use_scan  = True
    use_dith  = True
    use_jitter= True
    muted     = False

    sounds = Bleeps()
    if sounds.enabled and sounds.boot: 
        sounds.play(sounds.boot)

    def beep(snd):
        if not muted and sounds.enabled: 
            sounds.play(snd)

    # Declare variables before use, so nonlocal works as intended
    p1 = p2 = ball = None
    s1 = s2 = 0
    bvx = bvy = 0

    def reset_match():
        nonlocal p1, p2, s1, s2, ball, bvx, bvy
        p1 = pygame.Rect(10, BASE_H//2-PADDLE_H//2, PADDLE_W, PADDLE_H)
        p2 = pygame.Rect(BASE_W-10-PADDLE_W, BASE_H//2-PADDLE_H//2, PADDLE_W, PADDLE_H)
        s1 = s2 = 0
        bx, by, vx, vy = reset_ball(to_left=random.choice([False,True]))
        ball = pygame.Rect(bx, by, BALL_SIZE, BALL_SIZE)
        bvx, bvy = vx, vy

    reset_match()
    paused = False
    game_over = False
    running = True

    while running:
        clock.tick(FPS)  # Removed unused dt variable

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: 
                    running = False
                elif e.key == pygame.K_SPACE and not game_over: 
                    paused = not paused
                elif e.key == pygame.K_F11: 
                    pygame.display.toggle_fullscreen()
                elif e.key == pygame.K_g: 
                    use_jitter = not use_jitter
                elif e.key == pygame.K_d: 
                    use_dith = not use_dith
                elif e.key == pygame.K_c: 
                    use_scan = not use_scan
                elif e.key == pygame.K_m: 
                    muted = not muted
                elif game_over and e.key == pygame.K_y:
                    reset_match()
                    game_over = False
                elif game_over and e.key == pygame.K_n:
                    running = False

        # ------------------ Update ------------------
        if not paused and not game_over:
            # Player paddle follows mouse Y (clamped to arena)
            mx, my = pygame.mouse.get_pos()
            # translate window coords to low-res surface coords with safe division
            w, h = screen.get_size()
            scale_x = max(1, w // BASE_W)
            scale_y = max(1, h // BASE_H)
            scale   = max(1, min(scale_x, scale_y))
            ox = (w - BASE_W*scale)//2
            oy = (h - BASE_H*scale)//2
            ly = ((my - oy) / max(1, scale))
            p1.centery = int(clamp(ly, PADDLE_H//2, BASE_H - PADDLE_H//2))
            p1.y = clamp(p1.y, 4, BASE_H - PADDLE_H - 4)

            # AI paddle (right) with improved tracking
            target = ball.centery
            diff = target - p2.centery
            if abs(diff) > 3:  # Dead zone to prevent jitter
                move = min(CPU_SPEED, abs(diff)) * (1 if diff > 0 else -1)
                p2.y += move
            p2.y = clamp(p2.y, 4, BASE_H - PADDLE_H - 4)

            # Ball move (quantized for PS1 wobble)
            q = 1.0 if not use_jitter else random.choice([1.0, 1.0, 0.75, 0.5])
            next_x = ball.x + int(round(bvx * q))
            next_y = ball.y + int(round(bvy * q))
            
            # Update ball position
            ball.x = next_x
            ball.y = next_y

            # Walls with better boundary checking
            if ball.top <= 2:
                ball.top = 2
                bvy = abs(bvy)
                beep(sounds.wall)
            elif ball.bottom >= BASE_H-2:
                ball.bottom = BASE_H-2
                bvy = -abs(bvy)
                beep(sounds.wall)

            # Improved paddle collision with anti-tunneling
            if ball.colliderect(p1) and bvx < 0:
                # Ensure ball is actually moving toward paddle
                if ball.centerx > p1.centerx:
                    rel = (ball.centery - p1.centery) / max(1, PADDLE_H/2)
                    rel = clamp(rel, -1, 1)
                    angle = rel * 0.4 * math.pi
                    speed = min((abs(bvx)**2 + abs(bvy)**2)**0.5 * SPEED_UP, BALL_SPEED * 3)
                    bvx = abs(speed * math.cos(angle))
                    bvy = clamp(speed * math.sin(angle), -BALL_MAX_VY, BALL_MAX_VY)
                    ball.left = p1.right + 1
                    beep(sounds.hit)

            if ball.colliderect(p2) and bvx > 0:
                # Ensure ball is actually moving toward paddle
                if ball.centerx < p2.centerx:
                    rel = (ball.centery - p2.centery) / max(1, PADDLE_H/2)
                    rel = clamp(rel, -1, 1)
                    angle = rel * 0.4 * math.pi
                    speed = min((abs(bvx)**2 + abs(bvy)**2)**0.5 * SPEED_UP, BALL_SPEED * 3)
                    bvx = -abs(speed * math.cos(angle))
                    bvy = clamp(speed * math.sin(angle), -BALL_MAX_VY, BALL_MAX_VY)
                    ball.right = p2.left - 1
                    beep(sounds.hit)

            # Score
            if ball.right < 0:
                s2 += 1
                beep(sounds.point)
                bx, by, bvx, bvy = reset_ball(to_left=False)
                ball.update(bx, by, BALL_SIZE, BALL_SIZE)
            elif ball.left > BASE_W:
                s1 += 1
                beep(sounds.point)
                bx, by, bvx, bvy = reset_ball(to_left=True)
                ball.update(bx, by, BALL_SIZE, BALL_SIZE)

            # Win condition
            if s1 >= WIN_SCORE or s2 >= WIN_SCORE:
                game_over = True
                paused = False

        # ------------------ Render ------------------
        surf.fill(BG_COL)
        draw_net(surf)

        jitter_x = random.choice([0, 0, 1]) if use_jitter else 0
        jitter_y = random.choice([0, 0, 1]) if use_jitter else 0

        pygame.draw.rect(surf, FG_COL, p1.move(jitter_x, -jitter_y))
        pygame.draw.rect(surf, FG_COL, p2.move(-jitter_x, jitter_y))
        pygame.draw.rect(surf, FG_COL, ball.move(jitter_x, jitter_y))

        # HUD text
        mute_status = "MUTED" if muted else "SOUND"
        hud = font.render(f"{s1}   AI:{s2}  [{'PAUSED' if paused else 'RUN'}]  G/D/C=FX  M={mute_status}", True, NET_COL)
        surf.blit(hud, (8, 6))

        if use_dith:  
            surf.blit(dither, (0,0))
        if use_scan:  
            surf.blit(scanlines, (0,0))

        # Game Over overlay
        if game_over:
            ov = pygame.Surface((BASE_W, BASE_H), pygame.SRCALPHA)
            ov.fill(OVERLAY)
            surf.blit(ov, (0,0))
            winner = "YOU" if s1 > s2 else "AI"
            t1 = big.render(f"GAME OVER — {winner} WINS", True, (240,240,240))
            t2 = font.render("Press Y to Restart, N to Quit", True, (220,220,220))
            surf.blit(t1, (BASE_W//2 - t1.get_width()//2, BASE_H//2 - 18))
            surf.blit(t2, (BASE_W//2 - t2.get_width()//2, BASE_H//2 + 6))

        # Scale to window, centered with safe division
        w, h = screen.get_size()
        scale_x = max(1, w // BASE_W)
        scale_y = max(1, h // BASE_H)
        scale = max(1, min(scale_x, scale_y))
        
        try:
            tgt = pygame.transform.scale(surf, (BASE_W*scale, BASE_H*scale))
            ox = (w - tgt.get_width()) // 2
            oy = (h - tgt.get_height()) // 2
            screen.fill((0,0,0))
            screen.blit(tgt, (ox, oy))
        except Exception:
            # Fallback if scaling fails
            screen.fill((0,0,0))
            screen.blit(surf, (0,0))
            
        pygame.display.flip()

    # Restore mouse visibility on exit
    pygame.mouse.set_visible(True)
    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Fatal error:", e)
        pygame.mouse.set_visible(True)  # Ensure mouse is visible on error
        pygame.quit()
        sys.exit(1)
