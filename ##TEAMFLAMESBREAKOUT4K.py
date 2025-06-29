#!/usr/bin/env python3
"""
🧱 BREAKOUT 60 FPS – Pygame
Pure‑Python, one file, no external images / sounds
"""

import sys, math, random, array
import pygame

# ─── Config ────────────────────────────────────────────────────────────────
WIN_W, WIN_H      = 600, 400
FPS               = 60
PADDLE_W, PADDLE_H = 80, 12
BALL_R            = 6
BALL_SPEED        = 260          # pixels / sec (vector length)
BRICK_COLS        = 10
BRICK_ROWS        = 5
BRICK_W           = WIN_W // BRICK_COLS
BRICK_H           = 20
BEEP_FREQ, BEEP_MS = 880, 80     # brick hit
BOOP_FREQ, BOOP_MS = 200, 350    # ball lost

# ─── Tone synthesis (no numpy) ─────────────────────────────────────────────
def make_tone(freq_hz: int, dur_ms: int, volume=0.6, sr=44100):
    n_samples = int(sr * dur_ms / 1000)
    buf = array.array("h")
    amp = int(volume * 32767)
    for i in range(n_samples):
        buf.append(int(amp * math.sin(2 * math.pi * freq_hz * i / sr)))
    return pygame.mixer.Sound(buffer=buf.tobytes())

# ─── Game objects ──────────────────────────────────────────────────────────
class Brick(pygame.Rect):
    def __init__(self, x, y, color):                 # inherit rect
        super().__init__(x, y, BRICK_W, BRICK_H)
        self.color = color

class Game:
    COLORS = [(255, 80, 80), (255, 160, 70), (255, 210, 50),
              (70, 200, 255), (140, 180, 255)]

    def __init__(self):
        self.reset()

    def reset(self):
        # Paddle centred at bottom
        self.paddle = pygame.Rect((WIN_W - PADDLE_W)//2,
                                  WIN_H - 40,
                                  PADDLE_W, PADDLE_H)
        # Ball in middle heading upward
        angle = random.uniform(30, 150) * (math.pi/180)
        self.ball_vel = [BALL_SPEED*math.cos(angle),
                         -BALL_SPEED*math.sin(angle)]
        self.ball_pos = [WIN_W/2, WIN_H/2]
        # Bricks
        self.bricks = []
        for r in range(BRICK_ROWS):
            color = Game.COLORS[r % len(Game.COLORS)]
            for c in range(BRICK_COLS):
                self.bricks.append(
                    Brick(c*BRICK_W, 60 + r*BRICK_H, color))
        self.score = 0
        self.running = True
        self.win = False

    # step the simulation dt seconds
    def update(self, dt, mouse_x):
        if not self.running: return
        # Paddle follows mouse X
        self.paddle.centerx = mouse_x
        self.paddle.clamp_ip(pygame.Rect(0,0,WIN_W,WIN_H))

        # Move ball
        self.ball_pos[0] += self.ball_vel[0]*dt
        self.ball_pos[1] += self.ball_vel[1]*dt
        bx, by = self.ball_pos

        # Wall collisions
        if bx - BALL_R <= 0 or bx + BALL_R >= WIN_W:
            self.ball_vel[0] *= -1; bx = max(BALL_R, min(bx, WIN_W-BALL_R))
        if by - BALL_R <= 0:
            self.ball_vel[1] *= -1; by = BALL_R

        # Paddle collision (only downward heading)
        ball_rect = pygame.Rect(int(bx-BALL_R), int(by-BALL_R),
                                BALL_R*2, BALL_R*2)
        if self.ball_vel[1] > 0 and ball_rect.colliderect(self.paddle):
            # reflect with angle based on hit position
            offset = (bx - self.paddle.centerx) / (PADDLE_W/2)
            angle = offset * 60               # max 60° from vertical
            angle = math.radians(angle)
            speed = BALL_SPEED
            self.ball_vel = [speed*math.sin(angle),
                             -speed*math.cos(angle)]
            by = self.paddle.top - BALL_R     # stick above paddle

        # Brick collisions
        hit_index = ball_rect.collidelist(self.bricks)
        if hit_index != -1:
            hit_brick = self.bricks.pop(hit_index)
            self.score += 1
            # reflect vertically for simplicity
            self.ball_vel[1] *= -1
            beep.play()
            if not self.bricks:
                self.running = False
                self.win = True

        # Bottom out?
        if by - BALL_R > WIN_H:
            self.running = False
            self.win = False
            boop.play()

        self.ball_pos = [bx, by]

# ─── Main ──────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("🧱 Breakout 60 FPS")
    clock = pygame.time.Clock()
    global beep, boop
    beep = make_tone(BEEP_FREQ, BEEP_MS)
    boop = make_tone(BOOP_FREQ, BOOP_MS)
    font = pygame.font.SysFont("Consolas", 18)

    game = Game()

    while True:
        dt = clock.tick(FPS) / 1000.0
        mouse_x = pygame.mouse.get_pos()[0]

        # ─ Event pump ─
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if ev.key == pygame.K_r:
                    game.reset()

        game.update(dt, mouse_x)

        # ─ Rendering ─
        screen.fill((0,0,0))
        # Bricks
        for br in game.bricks:
            pygame.draw.rect(screen, br.color, br)
            pygame.draw.rect(screen, (20,20,20), br, 1)
        # Paddle
        pygame.draw.rect(screen, (200, 200, 200), game.paddle)
        # Ball
        pygame.draw.circle(screen, (255,255,255),
                           (int(game.ball_pos[0]), int(game.ball_pos[1])),
                           BALL_R)
        # Score
        txt = f"Score {game.score}"
        if not game.running:
            txt += "  –  YOU WIN!" if game.win else "  –  YOU LOSE!"
            txt += "  (R to restart)"
        img = font.render(txt, True, (255,255,255))
        screen.blit(img, (10, 10))

        pygame.display.flip()

if __name__ == "__main__":
    main()
