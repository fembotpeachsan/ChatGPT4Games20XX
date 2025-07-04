###############################################################################
#  Pong Game – “Atari Beeps ’n’ Boops Edition”
#  Requirements implemented:
#    • Mouse‑controlled left paddle (vertical only)
#    • Simple‑AI right paddle
#    • Race‑to‑5 scoring; Game‑Over screen with “Play again? (Y/N)”
#    • Classic‑style sound effects: “beep” (paddle), “boop” (wall), “score”
#    • Score display during play and on Game‑Over screen
###############################################################################

import math
import sys
import random
import array
import pygame

# ---------------------------------------------------------------------------
#‑‑‑ Configurable constants --------------------------------------------------
WIDTH, HEIGHT        = 800, 600
FPS                  = 60
PADDLE_W, PADDLE_H   = 10, 100
PADDLE_MARGIN        = 30                     # left edge distance
BALL_SIZE            = 10
BALL_SPEED           = 5.0                    # pixels per frame (vector is normalized)
AI_MAX_SPEED         = 6.0                    # how fast the CPU paddle can move
WIN_SCORE            = 5
FONT_NAME            = "arial"
BG_COLOR             = (0, 0, 0)
FG_COLOR             = (255, 255, 255)

# ---------------------------------------------------------------------------
#‑‑‑ Helper: generate retro “pure tone” sounds on the fly --------------------
def make_tone(freq_hz: int, ms: int, volume: float = 0.5) -> pygame.mixer.Sound:
    """
    Create a square‑wave tone (mono, 16‑bit) and return it as a pygame Sound.
    • freq_hz : frequency of square wave
    • ms      : duration in milliseconds
    • volume  : 0.0‑1.0
    """
    sample_rate  = 44100
    n_samples    = int(sample_rate * ms / 1000)
    amplitude    = int(32767 * volume)
    buf          = array.array("h")

    period = sample_rate // freq_hz
    half   = period // 2
    for i in range(n_samples):
        buf.append(amplitude if (i % period) < half else -amplitude)

    sound = pygame.mixer.Sound(buffer=buf.tobytes())
    return sound

# ---------------------------------------------------------------------------
#‑‑‑ Game objects ------------------------------------------------------------
class Paddle:
    def __init__(self, x: int):
        self.rect = pygame.Rect(x, (HEIGHT - PADDLE_H)//2, PADDLE_W, PADDLE_H)

    def clamp(self):
        self.rect.top = max(0, min(self.rect.top, HEIGHT - PADDLE_H))

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.reset(direction=random.choice((-1, 1)))

    def reset(self, direction: int):
        self.rect.center = (WIDTH//2, HEIGHT//2)
        angle    = random.uniform(-0.4, 0.4)  # ~±23°
        self.vx  = direction * BALL_SPEED * math.cos(angle)
        self.vy  = BALL_SPEED * math.sin(angle)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

# ---------------------------------------------------------------------------
def main():
    pygame.init()
    pygame.display.set_caption("Pong – Atari Beeps 'n' Boops Edition")
    screen  = pygame.display.set_mode((WIDTH, HEIGHT))
    clock   = pygame.time.Clock()
    font    = pygame.font.SysFont(FONT_NAME, 32)

    # Sounds – pure 1970s square waves
    beep_sound   = make_tone(1000, 40)        # paddle
    boop_sound   = make_tone(500,  40)        # wall
    score_sound  = make_tone(250, 250, 0.7)   # score

    left_pad  = Paddle(PADDLE_MARGIN)
    right_pad = Paddle(WIDTH - PADDLE_MARGIN - PADDLE_W)
    ball      = Ball()

    score_left  = 0
    score_right = 0
    game_over   = False

    # -----------------------------------------------------------------------
    #‑‑‑ Main loop ----------------------------------------------------------
    running = True
    while running:
        dt = clock.tick(FPS)

        # ------------ Input ------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Game‑Over keys
            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    # reset everything
                    score_left = score_right = 0
                    game_over  = False
                    ball.reset(direction=random.choice((-1, 1)))
                elif event.key == pygame.K_n:
                    running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

        # ------------ Gameplay (only if not Game‑Over) ---------------------
        if not game_over:
            # Left paddle follows mouse Y
            mouse_y = pygame.mouse.get_pos()[1]
            left_pad.rect.centery = mouse_y
            left_pad.clamp()

            # Right paddle simple AI
            if ball.rect.centery < right_pad.rect.centery:
                right_pad.rect.centery -= AI_MAX_SPEED
            elif ball.rect.centery > right_pad.rect.centery:
                right_pad.rect.centery += AI_MAX_SPEED
            right_pad.clamp()

            # Move ball
            prev_center = ball.rect.center
            ball.update()

            # Wall collision
            if ball.rect.top <= 0 or ball.rect.bottom >= HEIGHT:
                ball.vy = -ball.vy
                boop_sound.play()

            # Paddle collision
            if ball.rect.colliderect(left_pad.rect) and ball.vx < 0:
                ball.rect.left = left_pad.rect.right
                ball.vx = -ball.vx
                beep_sound.play()
            if ball.rect.colliderect(right_pad.rect) and ball.vx > 0:
                ball.rect.right = right_pad.rect.left
                ball.vx = -ball.vx
                beep_sound.play()

            # Goal?
            if ball.rect.right < 0:       # right scores
                score_right += 1
                score_sound.play()
                ball.reset(direction=1)
            elif ball.rect.left > WIDTH:  # left scores
                score_left += 1
                score_sound.play()
                ball.reset(direction=-1)

            # Check win condition
            if score_left == WIN_SCORE or score_right == WIN_SCORE:
                game_over = True

        # ------------ Render ----------------------------------------------
        screen.fill(BG_COLOR)

        # Center line
        for y in range(0, HEIGHT, 30):
            pygame.draw.rect(screen, FG_COLOR, (WIDTH//2-1, y+5, 2, 20))

        # Draw paddles & ball
        pygame.draw.rect(screen, FG_COLOR, left_pad.rect)
        pygame.draw.rect(screen, FG_COLOR, right_pad.rect)
        pygame.draw.ellipse(screen, FG_COLOR, ball.rect)

        # Score
        score_text = font.render(f"{score_left}   {score_right}", True, FG_COLOR)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 10))

        # Game‑Over overlay
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))  # semi‑transparent darken
            screen.blit(overlay, (0, 0))

            go_txt = font.render("Game Over!", True, FG_COLOR)
            qa_txt = font.render("Play again? (Y/N)", True, FG_COLOR)
            screen.blit(go_txt, (WIDTH//2 - go_txt.get_width()//2,
                                 HEIGHT//2 - go_txt.get_height() - 10))
            screen.blit(qa_txt, (WIDTH//2 - qa_txt.get_width()//2,
                                 HEIGHT//2 + 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
