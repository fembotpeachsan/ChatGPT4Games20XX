import pygame
import sys
import random
import math
import array

# --- Constants ------------------------------------------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 15
PADDLE_SPEED = 7  # used by AI paddle only
BALL_SPEED = 5
WIN_POINTS = 5  # when either side reaches this → game‑over prompt
SCORE_FONT_SIZE = 48
MSG_FONT_SIZE = 36

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# --- Optional sound helpers ----------------------------------------------

def _generate_tone(frequency: int, duration_ms: int, volume: float = 0.5):
    """Return a pygame.Sound with a sine‑wave tone. Pure Python; no numpy required."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = array.array("h")
    amplitude = int(volume * 32767)
    for i in range(n_samples):
        t = i / sample_rate
        sample = int(amplitude * math.sin(2 * math.pi * frequency * t))
        buf.append(sample)
    return pygame.mixer.Sound(buffer=buf.tobytes())


def _init_sounds():
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=1)
        beep = _generate_tone(880, 120)
        boop = _generate_tone(440, 200)
    except pygame.error:
        beep = boop = None  # sound unavailable
    return beep, boop


# --- Game Objects ---------------------------------------------------------
class Paddle:
    """Player (mouse‑controlled) or AI paddle."""
    def __init__(self, x: int):
        self.rect = pygame.Rect(x, HEIGHT // 2 - PADDLE_HEIGHT // 2,
                                PADDLE_WIDTH, PADDLE_HEIGHT)

    # Human mouse control ---------------------------------------------------
    def move_to(self, y: int):
        """Place paddle's center at given y (mouse)."""
        self.rect.centery = y
        self._clamp()

    # Simple AI -------------------------------------------------------------
    def move_ai(self, target_y: int):
        if self.rect.centery < target_y - 5:
            self.rect.y += PADDLE_SPEED
        elif self.rect.centery > target_y + 5:
            self.rect.y -= PADDLE_SPEED
        self._clamp()

    def _clamp(self):
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, WHITE, self.rect)


class Ball:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.reset()

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.vx = random.choice([-BALL_SPEED, BALL_SPEED])
        self.vy = random.choice([-BALL_SPEED, BALL_SPEED])

    def move(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        # Bounce top/bottom
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.vy *= -1

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, WHITE, self.rect)


# --- Main Game Loop -------------------------------------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong – Mouse vs AI, beeps ‘n’ boops 🏓")
    clock = pygame.time.Clock()
    score_font = pygame.font.SysFont(None, SCORE_FONT_SIZE)
    msg_font = pygame.font.SysFont(None, MSG_FONT_SIZE)

    left_paddle = Paddle(30)                         # Mouse‑controlled
    right_paddle = Paddle(WIDTH - 30 - PADDLE_WIDTH) # AI‑controlled
    ball = Ball()

    beep_sound, boop_sound = _init_sounds()

    score_left = 0
    score_right = 0
    state = "play"  # or "game_over"

    running = True
    while running:
        # --- Event Handling ------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Game‑over prompt handling -------------------------------------
            if state == "game_over" and event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_y, pygame.K_RETURN):  # restart
                    score_left = score_right = 0
                    ball.reset()
                    state = "play"
                elif event.key in (pygame.K_n, pygame.K_ESCAPE):  # quit
                    running = False

        # --- Update --------------------------------------------------------
        if state == "play":
            # Mouse controls left paddle
            mouse_y = pygame.mouse.get_pos()[1]
            left_paddle.move_to(mouse_y)

            # AI paddle tracks ball
            right_paddle.move_ai(ball.rect.centery)
            ball.move()

            # Paddle collision
            if ball.rect.colliderect(left_paddle.rect) and ball.vx < 0:
                ball.vx *= -1
                if beep_sound:
                    beep_sound.play()
            if ball.rect.colliderect(right_paddle.rect) and ball.vx > 0:
                ball.vx *= -1
                if beep_sound:
                    beep_sound.play()

            # Scoring
            scored = False
            if ball.rect.left <= 0:  # right wins point
                score_right += 1
                scored = True
            elif ball.rect.right >= WIDTH:  # left wins point
                score_left += 1
                scored = True
            if scored:
                if boop_sound:
                    boop_sound.play()
                ball.reset()

            # Check for win condition
            if score_left >= WIN_POINTS or score_right >= WIN_POINTS:
                state = "game_over"

        # --- Drawing -------------------------------------------------------
        screen.fill(BLACK)
        left_paddle.draw(screen)
        right_paddle.draw(screen)
        ball.draw(screen)

        # Center net
        pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

        # Scoreboard
        left_text = score_font.render(str(score_left), True, WHITE)
        right_text = score_font.render(str(score_right), True, WHITE)
        screen.blit(left_text, (WIDTH // 2 - 60, 20))
        screen.blit(right_text, (WIDTH // 2 + 35, 20))

        # Game‑over overlay --------------------------------------------------
        if state == "game_over":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # semi‑transparent darken
            screen.blit(overlay, (0, 0))

            winner = "Left" if score_left > score_right else "Right"
            msg_lines = [f"{winner} player wins!",
                         "Play again? (Y/N)"]
            for i, line in enumerate(msg_lines):
                txt = msg_font.render(line, True, WHITE)
                txt_rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 50))
                screen.blit(txt, txt_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
