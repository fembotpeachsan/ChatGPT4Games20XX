import pygame
import sys
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 15
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
WHITE = (255, 255, 255)
FPS = 60
FONT_COLOR = (0, 0, 0)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PONG FRENZY")

# Load sound effects
def create_sound(frequency, duration):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)  # Sine wave
    sound_array = (wave * 32767).astype(np.int16)  # Convert to 16-bit PCM
    sound_array_stereo = np.column_stack((sound_array, sound_array))  # Make it stereo
    sound = pygame.sndarray.make_sound(sound_array_stereo)  # Create sound from the stereo array
    return sound

# Create sound effects
bounce_sound = create_sound(440, 0.1)  # A4 note for bounce
score_sound = create_sound(523.25, 0.1)  # C5 note for score

# Ball class
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - BALL_RADIUS, HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
        self.dx = 5 * (-1 if WIDTH % 2 else 1)
        self.dy = 5 * (-1 if HEIGHT % 2 else 1)

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Bounce off the top and bottom
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy = -self.dy

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.dx = 5 * (-1 if self.dx > 0 else 1)

# Paddle class
class Paddle:
    def __init__(self, x):
        self.rect = pygame.Rect(x, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

    def move(self, dy):
        self.rect.y += dy
        # Keep the paddle on the screen
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

# AI Paddle class
class AIPaddle(Paddle):
    def move_ai(self, ball):
        if ball.rect.centery < self.rect.centery:
            self.move(-5)
        elif ball.rect.centery > self.rect.centery:
            self.move(5)

# Game functions
def game_loop():
    clock = pygame.time.Clock()
    ball = Ball()
    paddle1 = Paddle(30)  # Player paddle
    paddle2 = AIPaddle(WIDTH - 30 - PADDLE_WIDTH)  # AI paddle

    player_score = 0
    ai_score = 0
    font = pygame.font.SysFont("Arial", 40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Paddle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            paddle1.move(-10)
        if keys[pygame.K_s]:
            paddle1.move(10)

        # Move the ball
        ball.move()

        # AI movement
        paddle2.move_ai(ball)

        # Collision with paddles
        if ball.rect.colliderect(paddle1.rect) or ball.rect.colliderect(paddle2.rect):
            ball.dx = -ball.dx
            bounce_sound.play()  # Play bounce sound

        # Reset ball if it goes out of bounds
        if ball.rect.left <= 0:
            ai_score += 1
            ball.reset()
            score_sound.play()  # Play score sound
        elif ball.rect.right >= WIDTH:
            player_score += 1
            ball.reset()
            score_sound.play()  # Play score sound

        # Clear screen
        screen.fill(WHITE)

        # Draw everything
        pygame.draw.ellipse(screen, (0, 0, 0), ball.rect)
        pygame.draw.rect(screen, (0, 0, 0), paddle1.rect)
        pygame.draw.rect(screen, (0, 0, 0), paddle2.rect)

        # Display scores
        score_text = font.render(f"{player_score} : {ai_score}", True, FONT_COLOR)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

        # Check for game over
        if player_score == 5 or ai_score == 5:
            game_over(player_score, ai_score)
            return  # Exit the loop to return to the main menu

        pygame.display.flip()
        clock.tick(FPS)

def game_over(player_score, ai_score):
    font = pygame.font.SysFont("Arial", 60)
    while True:
        screen.fill(WHITE)
        game_over_text = font.render("GAME OVER", True, (255, 0, 0))
        score_text = font.render(f"Final Score: {player_score} : {ai_score}", True, FONT_COLOR)
        restart_text = font.render("Press R to Restart or Q to Quit", True, FONT_COLOR)

        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 3))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return  # Restart the game
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def main_menu():
    while True:
        screen.fill(WHITE)
        font = pygame.font.SysFont("Arial", 60)
        title_text = font.render("PONG FRENZY", True, FONT_COLOR)
        start_text = font.render("Press Enter to Start", True, FONT_COLOR)
        credits_text = font.render("Press C for Credits", True, FONT_COLOR)

        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))
        screen.blit(credits_text, (WIDTH // 2 - credits_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_loop()
                if event.key == pygame.K_c:
                    credits_screen()

def credits_screen():
    while True:
        screen.fill(WHITE)
        font = pygame.font.SysFont("Arial", 40)
        credits_text = font.render("Created by Your Name", True, FONT_COLOR)
        back_text = font.render("Press Backspace to Return", True, FONT_COLOR)

        screen.blit(credits_text, (WIDTH // 2 - credits_text.get_width() // 2, HEIGHT // 3))
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    return  # Go back to the main menu

if __name__ == "__main__":
    main_menu()
