import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants for the game
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 90
BALL_SIZE = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Famicom Pong with ToonEngineV0")

# Paddle settings
paddle_speed = 7
player_paddle = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
opponent_paddle = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Ball settings
ball_speed_x, ball_speed_y = 5, 5
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# ToonEngineV0: Custom Sound System
class ToonEngineV0:
    def __init__(self):
        self.sounds = {}

    def create_sound(self, name, frequency, duration, wave_type='square'):
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        buffer = bytearray()
        for i in range(num_samples):
            t = float(i) / sample_rate
            if wave_type == 'square':
                value = 127 if math.sin(2 * math.pi * frequency * t) > 0 else -127
            elif wave_type == 'noise':
                value = random.randint(-127, 127)
            else:  # default to sine
                value = int(127.0 * math.sin(2 * math.pi * frequency * t))
            buffer.append(int(value + 127))
        sound = pygame.mixer.Sound(buffer=buffer)
        self.sounds[name] = sound

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()
        else:
            print(f"Sound '{name}' not found in ToonEngineV0")

# Initialize ToonEngineV0
toon_engine = ToonEngineV0()

# Create Famicom-like sounds
toon_engine.create_sound("paddle_hit", 440, 0.1, 'square')
toon_engine.create_sound("wall_hit", 220, 0.1, 'square')
toon_engine.create_sound("start_game", 660, 0.2, 'square')
toon_engine.create_sound("menu_select", 880, 0.05, 'square')

# Game states
MENU = 0
PLAYING = 1
game_state = MENU

# Font
font = pygame.font.Font(None, 36)

# Scores
player_score = 0
opponent_score = 0

def draw_menu():
    screen.fill(BLACK)
    title = font.render("FAMICOM PONG", True, WHITE)
    start_text = font.render("Press SPACE to Start", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))

def draw_scores():
    player_text = font.render(f"{player_score}", True, WHITE)
    opponent_text = font.render(f"{opponent_score}", True, WHITE)
    screen.blit(player_text, (WIDTH // 4 - player_text.get_width() // 2, 20))
    screen.blit(opponent_text, (3 * WIDTH // 4 - opponent_text.get_width() // 2, 20))

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state == MENU:
                game_state = PLAYING
                toon_engine.play_sound("start_game")

    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        # Ball movement
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Ball collision with top/bottom
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_speed_y *= -1
            toon_engine.play_sound("wall_hit")

        # Ball collision with paddles
        if ball.colliderect(player_paddle) or ball.colliderect(opponent_paddle):
            ball_speed_x *= -1
            toon_engine.play_sound("paddle_hit")

        # Ball goes out of bounds
        if ball.left <= 0:
            opponent_score += 1
            ball.center = (WIDTH // 2, HEIGHT // 2)
            ball_speed_x *= -1
        if ball.right >= WIDTH:
            player_score += 1
            ball.center = (WIDTH // 2, HEIGHT // 2)
            ball_speed_x *= -1

        # Paddle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player_paddle.top > 0:
            player_paddle.y -= paddle_speed
        if keys[pygame.K_s] and player_paddle.bottom < HEIGHT:
            player_paddle.y += paddle_speed

        if opponent_paddle.top > ball.y:
            opponent_paddle.y -= paddle_speed
        if opponent_paddle.bottom < ball.y:
            opponent_paddle.y += paddle_speed

        # Drawing
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, player_paddle)
        pygame.draw.rect(screen, WHITE, opponent_paddle)
        pygame.draw.ellipse(screen, WHITE, ball)
        pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
        draw_scores()

    pygame.display.flip()
    pygame.time.Clock().tick(FPS)
