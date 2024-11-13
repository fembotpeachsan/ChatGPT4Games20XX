import pygame
import sys
import random
import numpy as np

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60
WINNING_SCORE = 10

# Paddle and Ball Settings
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 10
PADDLE_SPEED = 7
BALL_SPEED = 5

# Set up the display
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Set up sounds
def generate_beep(frequency=440, duration=0.1, sample_rate=44100, volume=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    wave = (wave * 32767).astype(np.int16)  # Convert to 16-bit PCM format
    sound = pygame.mixer.Sound(buffer=wave)
    sound.set_volume(volume)
    return sound

beep_sound = generate_beep(frequency=700)  # Beep sound for collisions
boop_sound = generate_beep(frequency=300)  # Boop sound for scoring


class Paddle(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)

    def move(self, up_key, down_key, keys):
        if keys[up_key] and self.y > 0:
            self.y -= PADDLE_SPEED
        if keys[down_key] and self.y < HEIGHT - PADDLE_HEIGHT:
            self.y += PADDLE_SPEED


class Ball(pygame.Rect):
    def __init__(self):
        super().__init__(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
        self.speed_x = random.choice([-BALL_SPEED, BALL_SPEED])
        self.speed_y = random.choice([-BALL_SPEED, BALL_SPEED])

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        # Bounce off top and bottom walls
        if self.y <= 0 or self.y >= HEIGHT - BALL_SIZE:
            self.speed_y *= -1
            beep_sound.play()

    def reset_position(self):
        self.x = WIDTH // 2 - BALL_SIZE // 2
        self.y = HEIGHT // 2 - BALL_SIZE // 2
        self.speed_x *= random.choice([-1, 1])
        self.speed_y *= random.choice([-1, 1])


class Scoreboard:
    def __init__(self):
        self.score_a = 0
        self.score_b = 0

    def update_score(self, player):
        if player == 'a':
            self.score_a += 1
        elif player == 'b':
            self.score_b += 1

    def draw(self):
        draw_text(str(self.score_a), 64, WIDTH // 4, 10)
        draw_text(str(self.score_b), 64, WIDTH * 3 // 4, 10)

    def check_winner(self):
        if self.score_a >= WINNING_SCORE:
            return 'Player A'
        elif self.score_b >= WINNING_SCORE:
            return 'Player B'
        return None


def draw_text(text, size, x, y, center=False):
    font = pygame.font.SysFont("arial", size)
    text_surface = font.render(text, True, WHITE)
    if center:
        x -= text_surface.get_width() // 2
        y -= text_surface.get_height() // 2
    win.blit(text_surface, (x, y))


def game_over_prompt(winner):
    draw_text(f"{winner} Wins!", 64, WIDTH // 2, HEIGHT // 2 - 50, center=True)
    draw_text("Press Y to Play Again or N to Quit", 32, WIDTH // 2, HEIGHT // 2 + 50, center=True)
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_n:
                    return False


def main():
    clock = pygame.time.Clock()
    paddle_a = Paddle(10, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    paddle_b = Paddle(WIDTH - 20, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ball = Ball()
    scoreboard = Scoreboard()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        paddle_a.move(pygame.K_w, pygame.K_s, keys)
        paddle_b.move(pygame.K_UP, pygame.K_DOWN, keys)

        ball.move()

        # Ball collision with paddles
        if ball.colliderect(paddle_a) and ball.speed_x < 0:
            ball.speed_x *= -1
            beep_sound.play()
        if ball.colliderect(paddle_b) and ball.speed_x > 0:
            ball.speed_x *= -1
            beep_sound.play()

        # Ball out of bounds
        if ball.x <= 0:
            scoreboard.update_score('b')
            boop_sound.play()
            if scoreboard.check_winner():
                if not game_over_prompt(scoreboard.check_winner()):
                    running = False
                else:
                    scoreboard = Scoreboard()  # Reset scores
                    ball.reset_position()
            else:
                ball.reset_position()
        elif ball.x >= WIDTH - BALL_SIZE:
            scoreboard.update_score('a')
            boop_sound.play()
            if scoreboard.check_winner():
                if not game_over_prompt(scoreboard.check_winner()):
                    running = False
                else:
                    scoreboard = Scoreboard()  # Reset scores
                    ball.reset_position()
            else:
                ball.reset_position()

        # Drawing
        win.fill(BLACK)
        pygame.draw.rect(win, WHITE, paddle_a)
        pygame.draw.rect(win, WHITE, paddle_b)
        pygame.draw.ellipse(win, WHITE, ball)
        scoreboard.draw()

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
## [C] Flames Corp [20XX]
