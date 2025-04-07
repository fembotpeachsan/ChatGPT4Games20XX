import pygame
import sys
import random
import numpy as np

# --- Initialize Pygame ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("ULTRA PONG 🚀")
clock = pygame.time.Clock()

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
GOLD = (255, 215, 0)

# --- Game Settings ---
FPS = 60
PADDLE_SPEED = 8
AI_SPEED = 6
BALL_SPEED_X = 6
BALL_SPEED_Y = 4
MAX_BOUNCE_ANGLE = 60  # Degrees

# --- Sound Effects ---
def play_sound(freq, duration=0.1, volume=0.5):
    sound = pygame.mixer.Sound(
        buffer=np.int16(
            32767 * volume * 
            np.sin(2 * np.pi * freq * 
            np.arange(44100 * duration) / 44100)
        )
    )
    sound.play()

# --- Power-Ups ---
class PowerUp:
    def __init__(self):
        self.reset()
        self.active = False
        self.type = None
    
    def reset(self):
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.rect.x = random.randint(100, 700)
        self.rect.y = random.randint(100, 500)
        self.type = random.choice(["speed_boost", "paddle_grow", "paddle_shrink"])
        self.active = True
    
    def draw(self):
        if not self.active: return
        color = GOLD if self.type == "speed_boost" else BLUE
        pygame.draw.rect(screen, color, self.rect, border_radius=5)

# --- Paddles & Ball ---
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 10, 100)
        self.speed = PADDLE_SPEED
    
    def move(self, up_key, down_key):
        keys = pygame.key.get_pressed()
        if keys[up_key] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[down_key] and self.rect.bottom < 600:
            self.rect.y += self.speed
    
    def ai_move(self, ball):
        if ball.rect.centery < self.rect.centery - 15:
            self.rect.y -= AI_SPEED
        elif ball.rect.centery > self.rect.centery + 15:
            self.rect.y += AI_SPEED
    
    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(390, 290, 10, 10)
        self.speed_x = BALL_SPEED_X * random.choice([-1, 1])
        self.speed_y = BALL_SPEED_Y * random.choice([-1, 1])
    
    def reset(self):
        self.rect.center = (400, 300)
        self.speed_x = BALL_SPEED_X * random.choice([-1, 1])
        self.speed_y = BALL_SPEED_Y * random.choice([-1, 1])
    
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Wall bounce
        if self.rect.top <= 0 or self.rect.bottom >= 600:
            self.speed_y *= -1
            play_sound(880)
        
        # Paddle bounce (with angle change)
        if self.rect.colliderect(player_paddle.rect) and self.speed_x < 0:
            self._handle_paddle_hit(player_paddle)
            play_sound(440)
        elif self.rect.colliderect(ai_paddle.rect) and self.speed_x > 0:
            self._handle_paddle_hit(ai_paddle)
            play_sound(440)
        
        # Scoring
        if self.rect.left <= 0:
            ai_score.increase()
            self.reset()
            play_sound(220, 0.3)
        elif self.rect.right >= 800:
            player_score.increase()
            self.reset()
            play_sound(220, 0.3)
    
    def _handle_paddle_hit(self, paddle):
        # Calculate bounce angle based on where ball hits paddle
        relative_y = (self.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)
        bounce_angle = relative_y * (MAX_BOUNCE_ANGLE * (3.14159 / 180))  # Convert to radians
        self.speed_x *= -1.1  # Speed up slightly
        self.speed_y = 10 * np.sin(bounce_angle)  # Adjust Y speed based on angle
    
    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

# --- Score System ---
class Score:
    def __init__(self, x):
        self.value = 0
        self.x = x
    
    def increase(self):
        self.value += 1
    
    def draw(self):
        font = pygame.font.Font(None, 74)
        text = font.render(str(self.value), True, WHITE)
        screen.blit(text, (self.x, 20))

# --- Game Setup ---
player_paddle = Paddle(30, 250)
ai_paddle = Paddle(760, 250)
ball = Ball()
player_score = Score(200)
ai_score = Score(600)
powerup = PowerUp()

# --- Main Menu ---
def show_menu():
    menu = True
    global game_mode
    
    while menu:
        screen.fill(BLACK)
        font = pygame.font.Font(None, 64)
        title = font.render("ULTRA PONG", True, WHITE)
        screen.blit(title, (250, 100))
        
        font = pygame.font.Font(None, 36)
        option1 = font.render("1. SINGLE PLAYER (vs AI)", True, WHITE)
        option2 = font.render("2. TWO PLAYERS", True, WHITE)
        screen.blit(option1, (300, 300))
        screen.blit(option2, (300, 350))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_mode = "1P"
                    menu = False
                elif event.key == pygame.K_2:
                    game_mode = "2P"
                    menu = False

# --- Main Game Loop ---
game_mode = None
show_menu()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # --- Controls ---
    player_paddle.move(pygame.K_w, pygame.K_s)
    if game_mode == "2P":
        ai_paddle.move(pygame.K_UP, pygame.K_DOWN)
    else:
        ai_paddle.ai_move(ball)
    
    # --- Update Ball & Check Power-Ups ---
    ball.update()
    if powerup.active and ball.rect.colliderect(powerup.rect):
        if powerup.type == "speed_boost":
            ball.speed_x *= 1.5
            ball.speed_y *= 1.5
        elif powerup.type == "paddle_grow":
            player_paddle.rect.height += 30
        elif powerup.type == "paddle_shrink":
            ai_paddle.rect.height = max(50, ai_paddle.rect.height - 30)
        powerup.active = False
        play_sound(660, 0.2)
    
    # Randomly spawn power-ups
    if random.random() < 0.002 and not powerup.active:
        powerup.reset()
    
    # --- Drawing ---
    screen.fill(BLACK)
    pygame.draw.aaline(screen, WHITE, (400, 0), (400, 600))
    player_paddle.draw()
    ai_paddle.draw()
    ball.draw()
    player_score.draw()
    ai_score.draw()
    powerup.draw()
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()