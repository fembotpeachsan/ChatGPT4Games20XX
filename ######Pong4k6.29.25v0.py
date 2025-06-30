import pygame
import sys
import math
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 15
PADDLE_SPEED = 7  # Still used by the AI paddle
BALL_SPEED = 5
SCORE_TO_WIN = 5  # <<< game‑over threshold >>>
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT_SIZE = 74
SMALL_FONT_SIZE = 36

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Clone – Mouse Control Left Paddle (Race to 5)")
clock = pygame.time.Clock()

# --- Sound synthesis functions ---

def create_beep(freq, duration=0.1):
    """Create an Atari‑style beep sound (mono or stereo for pygame)"""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    note = np.sin(freq * t * 2 * np.pi) * 0.5
    note = np.int16(note * 32767)

    if pygame.mixer.get_init():
        channels = pygame.mixer.get_init()[2]
    else:
        channels = 2

    # Make stereo if needed
    if channels == 2:
        stereo_note = np.zeros((n_samples, 2), dtype=np.int16)
        stereo_note[:, 0] = note
        stereo_note[:, 1] = note
        return pygame.sndarray.make_sound(stereo_note)
    else:
        return pygame.sndarray.make_sound(note)


def create_boop(freq, duration=0.15):
    """Create an Atari‑style boop sound"""
    return create_beep(freq, duration)

# Create sound effects
paddle_sound = create_beep(880)  # Higher frequency for paddle hit
wall_sound = create_boop(440)    # Lower frequency for wall hit

# --- Game objects ---

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.score = 0

    def move(self, dy: int):
        """Move paddle by dy pixels, clamped to screen"""
        self.rect.y += dy
        self._clamp_to_screen()

    def set_centery(self, y: int):
        """Set paddle center‑y directly (used for mouse control)"""
        self.rect.centery = y
        self._clamp_to_screen()

    def reset_position(self):
        self.rect.centery = SCREEN_HEIGHT // 2

    def _clamp_to_screen(self):
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)


class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2 - BALL_SIZE // 2,
            SCREEN_HEIGHT // 2 - BALL_SIZE // 2,
            BALL_SIZE,
            BALL_SIZE,
        )
        # Random initial direction (slight angle)
        angle = math.radians(45 + (pygame.time.get_ticks() % 60) * 3)
        self.dx = BALL_SPEED * math.cos(angle)
        self.dy = BALL_SPEED * math.sin(angle)

        # Randomly choose direction (left or right)
        if pygame.time.get_ticks() % 2 == 0:
            self.dx = -self.dx

    def update(self, player_paddle: "Paddle", ai_paddle: "Paddle"):
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Wall collision (top and bottom)
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.dy = -self.dy
            wall_sound.play()

        # Paddle collision
        if self.rect.colliderect(player_paddle.rect) or self.rect.colliderect(ai_paddle.rect):
            self.dx = -self.dx

            # Add slight angle based on where the ball hit
            if self.rect.colliderect(player_paddle.rect):
                relative_intersect_y = (player_paddle.rect.centery - self.rect.centery) / (PADDLE_HEIGHT / 2)
            else:
                relative_intersect_y = (ai_paddle.rect.centery - self.rect.centery) / (PADDLE_HEIGHT / 2)
            self.dy = relative_intersect_y * BALL_SPEED

            paddle_sound.play()

        # Score check
        if self.rect.left <= 0:
            ai_paddle.score += 1
            self.reset()
        elif self.rect.right >= SCREEN_WIDTH:
            player_paddle.score += 1
            self.reset()

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

# --- AI Logic ---

def ai_move(ai_paddle: Paddle, ball: Ball):
    """Simple AI that follows the ball's y position"""
    if ball.rect.centery < ai_paddle.rect.centery:
        ai_paddle.move(-PADDLE_SPEED)
    elif ball.rect.centery > ai_paddle.rect.centery:
        ai_paddle.move(PADDLE_SPEED)

# --- Helper ---

def draw_center_text(text: str, font: pygame.font.Font, y_offset: int = 0):
    surf = font.render(text, True, WHITE)
    rect = surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(surf, rect)

# --- Main Game Loop ---

def main():
    # Create game objects
    player_paddle = Paddle(20, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ai_paddle = Paddle(SCREEN_WIDTH - 20 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ball = Ball()

    # Fonts
    font = pygame.font.Font(None, FONT_SIZE)
    small_font = pygame.font.Font(None, SMALL_FONT_SIZE)

    running = True
    game_over = False
    winner = ""

    while running:
        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_y:  # restart
                    # reset everything
                    player_paddle.score = ai_paddle.score = 0
                    player_paddle.reset_position()
                    ai_paddle.reset_position()
                    ball.reset()
                    game_over = False
                elif event.key == pygame.K_n:
                    running = False

        if not game_over:
            # --- Player input (mouse control) ---
            mouse_y = pygame.mouse.get_pos()[1]
            player_paddle.set_centery(mouse_y)

            # --- AI movement ---
            ai_move(ai_paddle, ball)

            # --- Update ball position ---
            ball.update(player_paddle, ai_paddle)

            # --- Check win condition ---
            if player_paddle.score >= SCORE_TO_WIN or ai_paddle.score >= SCORE_TO_WIN:
                game_over = True
                winner = "Player" if player_paddle.score > ai_paddle.score else "AI"

        # --- Drawing ---
        screen.fill(BLACK)

        if game_over:
            draw_center_text(f"{winner} wins!", font)
            draw_center_text("Play again? Y/N", small_font, y_offset=FONT_SIZE)
        else:
            # Draw center line
            pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))

            # Draw game objects
            player_paddle.draw()
            ai_paddle.draw()
            ball.draw()

            # Draw scores
            player_score_text = font.render(str(player_paddle.score), True, WHITE)
            ai_score_text = font.render(str(ai_paddle.score), True, WHITE)
            screen.blit(player_score_text, (SCREEN_WIDTH // 4, 20))
            screen.blit(ai_score_text, (3 * SCREEN_WIDTH // 4 - ai_score_text.get_width(), 20))

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
