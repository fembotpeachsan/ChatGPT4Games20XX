import pygame
import random
import sys
import numpy as np

# --- Constants ---
WIDTH, HEIGHT = 800, 600
BALL_SIZE = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 80
PADDLE_SPEED = 8
BALL_SPEED_X = 6
BALL_SPEED_Y = 4
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60
WINNING_SCORE = 5

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

# --- Sound Generation Function ---
def generate_beep(frequency=440, duration=0.1, sample_rate=44100):
    try:
        num_samples = int(sample_rate * duration)
        time_array = np.linspace(0, duration, num_samples, False)
        note = np.sign(np.sin(frequency * time_array * 2 * np.pi)) * 0.5
        audio = note * (2**15 - 1)
        audio = audio.astype(np.int16)
        stereo_audio = np.zeros((num_samples, 2), dtype=np.int16)
        stereo_audio[:, 0] = audio
        stereo_audio[:, 1] = audio
        return pygame.mixer.Sound(buffer=stereo_audio)
    except Exception as e:
        print(f"Sound generation error: {e}")
        return pygame.mixer.Sound(buffer=np.zeros((100, 2), dtype=np.int16))

# --- Paddle Class ---
class Paddle:
    def __init__(self, x, y, is_ai=False):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED
        self.is_ai = is_ai
        self.ai_miss_chance = 0.1

    def move(self, direction):
        if direction == "UP":
            self.rect.y -= self.speed
        elif direction == "DOWN":
            self.rect.y += self.speed

        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))

    def ai_move(self, ball):
        if random.random() > self.ai_miss_chance:
            if self.rect.centery < ball.rect.centery - 10:  # Added buffer to prevent jitter
                self.move("DOWN")
            elif self.rect.centery > ball.rect.centery + 10:
                self.move("UP")

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

# --- Ball Class ---
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
        self.reset()
        self.last_reset_time = 0

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.vel_x = BALL_SPEED_X * random.choice([-1, 1])
        self.vel_y = random.uniform(-BALL_SPEED_Y, BALL_SPEED_Y)
        self.last_reset_time = pygame.time.get_ticks()

    def update(self, paddle1, paddle2, score, sounds):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_reset_time < 500:  # Delay after reset
            return PLAYING, 0

        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Wall collision
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.vel_y *= -1
            sounds["wall"].play()

        # Paddle collisions
        if self.rect.colliderect(paddle1.rect) and self.vel_x < 0:
            self.handle_paddle_collision(paddle1, sounds["paddle"], left=True)
            
        if self.rect.colliderect(paddle2.rect) and self.vel_x > 0:
            self.handle_paddle_collision(paddle2, sounds["paddle"], left=False)

        # Scoring
        if self.rect.left <= 0:
            score[1] += 1
            sounds["score"].play()
            if score[1] >= WINNING_SCORE:
                return GAME_OVER, 2
            self.reset()
        elif self.rect.right >= WIDTH:
            score[0] += 1
            sounds["score"].play()
            if score[0] >= WINNING_SCORE:
                return GAME_OVER, 1
            self.reset()
        
        return PLAYING, 0

    def handle_paddle_collision(self, paddle, sound, left):
        relative_intersect = (paddle.rect.centery - self.rect.centery) / (paddle.rect.height / 2)
        self.vel_x = BALL_SPEED_X * (1 if left else -1)
        self.vel_y = -relative_intersect * BALL_SPEED_Y * 1.5
        sound.play()

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

# --- Main Menu Function ---
def main_menu(screen, font):
    menu_font = pygame.font.Font(None, 74)
    title_font = pygame.font.Font(None, 100)
    clock = pygame.time.Clock()
    selected = 0
    options = ["Start Game", "Exit"]
    
    while True:
        screen.fill(BLACK)
        title_text = title_font.render("PONG", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

        for i, option in enumerate(options):
            color = (255, 255, 0) if i == selected else WHITE
            text = menu_font.render(option, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 250 + i * 100))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        return PLAYING
                    elif selected == 1:
                        pygame.quit()
                        sys.exit()

        clock.tick(FPS)

# --- Main Game Function ---
def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Classic Pong")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 74)

    sounds = {
        "paddle": generate_beep(440, 0.05),
        "wall": generate_beep(220, 0.05),
        "score": generate_beep(880, 0.2)
    }

    paddle1 = Paddle(30, HEIGHT//2 - PADDLE_HEIGHT//2)
    paddle2 = Paddle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, is_ai=True)
    ball = Ball()
    score = [0, 0]
    game_state = MENU

    while True:
        if game_state == MENU:
            game_state = main_menu(screen, font)
        elif game_state == PLAYING:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                paddle1.move("UP")
            if keys[pygame.K_s]:
                paddle1.move("DOWN")

            paddle2.ai_move(ball)
            game_state, winner = ball.update(paddle1, paddle2, score, sounds)

            screen.fill(BLACK)
            pygame.draw.line(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)
            score_text = font.render(f"{score[0]}   {score[1]}", True, WHITE)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))
            paddle1.draw(screen)
            paddle2.draw(screen)
            ball.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
        
        elif game_state == GAME_OVER:
            screen.fill(BLACK)
            game_over_text = font.render("YOU WIN!", True, WHITE)
            winner_text = font.render(f"Player {winner}", True, WHITE)
            restart_text = font.render("Press R to restart", True, WHITE)
            quit_text = font.render("Press Q to quit", True, WHITE)
            
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
            screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, HEIGHT//2 - 30))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
            screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 120))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        score = [0, 0]
                        ball.reset()
                        game_state = PLAYING
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

if __name__ == "__main__":
    main()
