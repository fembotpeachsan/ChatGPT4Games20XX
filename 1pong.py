#!/usr/bin/env python3
"""
O3 Alpha Pong: AI Left, You Right — Retro Atari SFX, Auto-Prompt Vibes
No files. Pure simulation. M1 Mac/Rosetta 2 ready.

Keys: UP/DOWN arrows (your paddle). Left is AI.
Beep/boop when ball hits. First to 5 points wins.

On Game Over: Terminal asks [Play Again? y/n]
"""

import pygame, sys, random, numpy as np

# ==== O3 LAUNCH PROMPT ====
print("""
🕹️  O3 Alpha Pong  ∙  Reality Test Chamber
Left = AI  |  Right = You  |  60 FPS  |  Maximum Blorb
""")

# ==== CONFIG ====
WIDTH, HEIGHT = 640, 400
PADDLE_W, PADDLE_H = 12, 60
BALL = 14
SCORE_WIN = 5
SPEED = 6
AI_SPEED = 4.5

# ==== SFX ENGINE: Pure Atari Boop ====
def beep(freq=420, dur=0.07, vol=0.42):
    rate = 22050
    n = int(rate * dur)
    arr = (np.sin(2 * np.pi * np.arange(n) * freq / rate) * (32767 * vol)).astype(np.int16)
    arr = np.repeat(arr.reshape(-1,1), 2, axis=1)
    try:
        pygame.sndarray.make_sound(arr).play()
    except Exception:  # Sound might fail on some configs, just skip
        pass

# ==== RESET FUNC ====
def reset():
    ball = pygame.Rect(WIDTH//2-BALL//2, HEIGHT//2-BALL//2, BALL, BALL)
    bdx = random.choice([-1,1]) * SPEED
    bdy = random.uniform(-1.5, 1.5) * SPEED
    lp = pygame.Rect(20, HEIGHT//2-PADDLE_H//2, PADDLE_W, PADDLE_H)
    rp = pygame.Rect(WIDTH-32, HEIGHT//2-PADDLE_H//2, PADDLE_W, PADDLE_H)
    return ball, bdx, bdy, lp, rp

def draw(screen, ball, lp, rp, lsc, rsc):
    screen.fill((16, 16, 16))
    pygame.draw.rect(screen, (230,230,230), lp)
    pygame.draw.rect(screen, (230,230,230), rp)
    pygame.draw.ellipse(screen, (200,255,180), ball)
    pygame.draw.aaline(screen, (60,60,60), (WIDTH//2,0), (WIDTH//2, HEIGHT))
    font = pygame.font.SysFont("Consolas", 36)
    t = font.render(f"{lsc}    {rsc}", 1, (255,255,160))
    screen.blit(t, (WIDTH//2-t.get_width()//2, 24))

def ai_move(ball, lp):
    if ball.centery < lp.centery - 8:
        lp.y -= int(AI_SPEED)
    elif ball.centery > lp.centery + 8:
        lp.y += int(AI_SPEED)
    lp.y = max(0, min(HEIGHT-PADDLE_H, lp.y))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("O3 Alpha Pong — AI Reality Chamber")
    clock = pygame.time.Clock()
    while True:
        lscore, rscore = 0, 0
        ball, bdx, bdy, lp, rp = reset()
        playing = True

        while playing:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:    rp.y -= SPEED
            if keys[pygame.K_DOWN]:  rp.y += SPEED
            rp.y = max(0, min(HEIGHT-PADDLE_H, rp.y))

            # AI moves left paddle
            ai_move(ball, lp)

            # Ball move
            ball.x += int(bdx)
            ball.y += int(bdy)

            # Wall bounce
            if ball.top <= 0 or ball.bottom >= HEIGHT:
                bdy = -bdy
                beep(800, 0.04)
            # Paddle bounce
            if ball.colliderect(lp) and bdx < 0:
                bdx = -bdx
                beep(440, 0.05)
            if ball.colliderect(rp) and bdx > 0:
                bdx = -bdx
                beep(600, 0.05)

            # Score check
            if ball.left <= 0:
                rscore += 1
                beep(1200, 0.18)
                ball, bdx, bdy, lp, rp = reset()
            if ball.right >= WIDTH:
                lscore += 1
                beep(220, 0.18)
                ball, bdx, bdy, lp, rp = reset()

            draw(screen, ball, lp, rp, lscore, rscore)
            pygame.display.flip()
            clock.tick(60)

            # Win condition
            if lscore == SCORE_WIN or rscore == SCORE_WIN:
                playing = False

        # Game Over Prompt (Terminal, O3 style)
        win_side = "AI" if lscore == SCORE_WIN else "YOU"
        print(f"\n🕹️  GAME OVER! {win_side} wins.")
        print("Play again? (y/n): ", end="", flush=True)
        ans = ""
        while ans not in ("y","n"):
            ans = input().lower()
        if ans == "n":
            print("Goodbye, blorbo.")
            pygame.quit(); sys.exit()
        print("Restarting reality...\n")

if __name__ == "__main__":
    main()
