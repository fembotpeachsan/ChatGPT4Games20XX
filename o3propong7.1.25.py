# o3pro_pong.py
# Classic Pong with Atari‑style "beep" and "boop" SFX (no external sound files)
import pygame, sys, random, math, array

# ----------------------------------------------------------------------
# CONFIGURABLE CONSTANTS
# ----------------------------------------------------------------------
WIDTH, HEIGHT       = 800, 600
PADDLE_W, PADDLE_H  = 10, 100
BALL_SIZE           = 10
WHITE, BLACK        = (255, 255, 255), (0, 0, 0)
FPS                 = 60
WIN_SCORE           = 5
AI_SPEED            = 6      # max pixels/frame the AI paddle can move
BALL_SPEED_X        = 6      # initial horizontal ball speed
BALL_SPEED_Y        = 4      # initial vertical ball speed range
SAMPLE_RATE         = 44100  # audio sample rate (Hz)

# ----------------------------------------------------------------------
# INITIALISE PYGAME + MIXER (pre_init ensures matching sample format)
# ----------------------------------------------------------------------
pygame.mixer.pre_init(SAMPLE_RATE, size=-16, channels=1)
pygame.init()
pygame.mixer.set_num_channels(8)  # generous but lightweight

screen  = pygame.display.set_mode((WIDTH, HEIGHT))
clock   = pygame.time.Clock()
f_big   = pygame.font.SysFont("arial", 48)
f_small = pygame.font.SysFont("arial", 24)
pygame.display.set_caption("o3 pro pong")

# ----------------------------------------------------------------------
# SIMPLE TONE SYNTHESIS (in‑memory, no files!)
# ----------------------------------------------------------------------

def tone(frequency: float, duration_ms: int, volume: float = 0.5):
    """Return a pygame.Sound containing a pure sine‑wave tone.

    Parameters
    ----------
    frequency : float
        Tone frequency in Hertz.
    duration_ms : int
        Duration in milliseconds.
    volume : float, optional
        Volume 0.0–1.0. Defaults to 0.5.
    """
    n_samples = int(SAMPLE_RATE * duration_ms / 1000)
    amplitude = int(32767 * max(0.0, min(volume, 1.0)))
    buf = array.array("h")  # signed 16‑bit
    for s in range(n_samples):
        sample = amplitude * math.sin(2 * math.pi * frequency * (s / SAMPLE_RATE))
        buf.append(int(sample))
    return pygame.mixer.Sound(buffer=buf.tobytes())

# Pre‑generate reusable effects
SFX_HIT   = tone(1200,  60, 0.35)  # short high‑pitched "beep"
SFX_SCORE = tone( 200, 150, 0.45)  # longer low "boop"

# ----------------------------------------------------------------------
class Paddle:
    def __init__(self, x, is_player=False):
        self.rect       = pygame.Rect(x, HEIGHT//2 - PADDLE_H//2, PADDLE_W, PADDLE_H)
        self.is_player  = is_player

    # Player paddle follows mouse Y position (clamped to screen)
    def move_player(self, y):
        self.rect.centery = max(PADDLE_H//2, min(HEIGHT - PADDLE_H//2, y))

    # Very simple AI: move toward ball Y at a fixed max speed
    def move_ai(self, target_y):
        if   self.rect.centery < target_y: self.rect.centery += AI_SPEED
        elif self.rect.centery > target_y: self.rect.centery -= AI_SPEED
        self.rect.centery = max(PADDLE_H//2, min(HEIGHT - PADDLE_H//2, self.rect.centery))

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=3)

# ----------------------------------------------------------------------
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2,
                                BALL_SIZE, BALL_SIZE)
        self.reset(direction=random.choice([-1, 1]))

    def reset(self, *, direction):
        self.rect.center = (WIDTH//2, HEIGHT//2)
        self.vx = BALL_SPEED_X * direction
        self.vy = random.choice([-BALL_SPEED_Y, BALL_SPEED_Y])

    def update(self, paddles, scores):
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Bounce off top/bottom
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.vy *= -1

        # Paddle collisions
        for paddle in paddles:
            if self.rect.colliderect(paddle.rect):
                self.vx *= -1
                SFX_HIT.play()
                # Add a bit of "spin": steer based on where the ball hit the paddle
                offset = (self.rect.centery - paddle.rect.centery) / (PADDLE_H / 2)
                self.vy = int(offset * BALL_SPEED_Y * 1.2)
                break

        # Scoring
        if self.rect.left <= 0:
            scores["ai"] += 1
            SFX_SCORE.play()
            self.reset(direction=1)
        elif self.rect.right >= WIDTH:
            scores["player"] += 1
            SFX_SCORE.play()
            self.reset(direction=-1)

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

# ----------------------------------------------------------------------

def center_text(msg, font, y_offset=0):
    surf = font.render(msg, True, WHITE)
    rect = surf.get_rect(center=(WIDTH//2, HEIGHT//2 + y_offset))
    screen.blit(surf, rect)

# ----------------------------------------------------------------------

def main():
    player = Paddle(20, is_player=True)
    ai     = Paddle(WIDTH - 20 - PADDLE_W)
    ball   = Ball()
    scores = {"player": 0, "ai": 0}
    state  = "menu"          # menu | credits | play | game_over
    winner = None

    while True:
        clock.tick(FPS)
        screen.fill(BLACK)

        # --------------
        # INPUT HANDLING
        # --------------
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if state == "menu":
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:  state = "play"
                    if e.key == pygame.K_c:       state = "credits"
            elif state == "credits":
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    state = "menu"
            elif state == "game_over":
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_y:       # restart
                        scores = {"player": 0, "ai": 0}
                        ball.reset(direction=random.choice([-1, 1]))
                        state = "menu"
                    if e.key == pygame.K_n:       # quit
                        pygame.quit(); sys.exit()

        # ------------------
        # STATE: MAIN MENU
        # ------------------
        if state == "menu":
            center_text("o3 pro pong", f_big, -60)
            center_text("Press ENTER to Start", f_small,  10)
            center_text("Press C for Credits",  f_small,  40)

        # ------------------
        # STATE: CREDITS
        # ------------------
        elif state == "credits":
            center_text("Credits", f_big, -120)
            y = -40
            for line in [
                "Programming: Cat-sama (wa wa 64)",
                "AI: o3 pro",
                "Special Thanks: The coding & AI community"]:
                center_text(line, f_small, y); y += 40
            center_text("Press ESC to return", f_small, 120)

        # ------------------
        # STATE: GAME PLAY
        # ------------------
        elif state == "play":
            # Player paddle follows mouse
            player.move_player(pygame.mouse.get_pos()[1])
            # AI paddle tracks ball
            ai.move_ai(ball.rect.centery)

            # Move & draw ball
            ball.update([player, ai], scores)
            ball.draw()

            # Draw paddles & center net
            player.draw(); ai.draw()
            pygame.draw.aaline(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

            # Draw scores
            screen.blit(f_big.render(str(scores["player"]), True, WHITE),
                        (WIDTH//4 - 10, 20))
            screen.blit(f_big.render(str(scores["ai"]), True, WHITE),
                        (3*WIDTH//4 - 10, 20))

            # Check win condition
            if scores["player"] >= WIN_SCORE or scores["ai"] >= WIN_SCORE:
                winner = "You" if scores["player"] > scores["ai"] else "AI"
                state  = "game_over"

        # ------------------
        # STATE: GAME OVER
        # ------------------
        elif state == "game_over":
            center_text(f"{winner} win!", f_big, -40)
            center_text("Press Y to Restart or N to Quit", f_small, 30)

        pygame.display.flip()

# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
