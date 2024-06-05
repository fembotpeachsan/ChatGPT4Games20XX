import pygame
import random
from array import array

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# --- Sound Generation ---
def generate_beep_sound(frequency=440, duration=0.1):
    """Generates a beep sound at a given frequency and duration."""
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2**(abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * ((i // (sample_rate // frequency)) % 2)) for i in range(samples)]
    sound = pygame.mixer.Sound(buffer=array('h', wave))
    return sound

# Create sound effects
PADDLE_HIT_SOUND = generate_beep_sound(220, 0.05)
BRICK_HIT_SOUND = generate_beep_sound(880, 0.02)
GAME_OVER_SOUND = generate_beep_sound(110, 0.5)
POWERUP_SOUND = generate_beep_sound(440, 0.1) 

# --- Game Settings ---
WIDTH = 800
HEIGHT = 600
FPS = 60  # NES-like frame rate

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BRICK_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

BRICK_WIDTH = 80
BRICK_HEIGHT = 20
BRICKS_PER_ROW = WIDTH // BRICK_WIDTH
BRICK_ROWS = 5
BRICK_GAP = 5

PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
PADDLE_SPEED = 10

BALL_RADIUS = 10
BALL_SPEED = 8

POWERUP_SIZE = 20
POWERUP_SPEED = 5
POWERUP_TYPES = ["expand", "multi_ball"] 

MENU = 0
GAME = 1
GAME_OVER = 2

# --- Game Initialization ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout - Flameslabs [C] 20XX-25")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- Game Objects ---
def create_brick(x, y, color):
    return pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT), color

def create_powerup(x, y):
    powerup_type = random.choice(POWERUP_TYPES)
    return pygame.Rect(x, y, POWERUP_SIZE, POWERUP_SIZE), powerup_type

bricks = []
powerups = []
paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 50, PADDLE_WIDTH, PADDLE_HEIGHT)
balls = [pygame.Rect(WIDTH // 2 - BALL_RADIUS, HEIGHT // 2, BALL_RADIUS * 2, BALL_RADIUS * 2)]
ball_dx = BALL_SPEED
ball_dy = BALL_SPEED
score = 0

# --- Helper Functions ---
def draw_text(text, x, y, color=WHITE):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def reset_game():
    """Resets the game to its initial state."""
    global bricks, powerups, balls, ball_dx, ball_dy, paddle, score
    balls = [pygame.Rect(WIDTH // 2 - BALL_RADIUS, HEIGHT // 2, BALL_RADIUS * 2, BALL_RADIUS * 2)]
    ball_dx = BALL_SPEED
    ball_dy = BALL_SPEED
    paddle.x = WIDTH // 2 - PADDLE_WIDTH // 2
    score = 0
    bricks = []
    powerups = [] 
    for row in range(BRICK_ROWS):
        for col in range(BRICKS_PER_ROW):
            brick_x = col * (BRICK_WIDTH + BRICK_GAP)
            brick_y = row * (BRICK_HEIGHT + BRICK_GAP) + 50
            brick_color = random.choice(BRICK_COLORS)
            bricks.append(create_brick(brick_x, brick_y, brick_color))

def apply_powerup(powerup_type):
    """Applies the effect of a power-up."""
    global paddle, balls
    if powerup_type == "expand":
        paddle.width = min(paddle.width + 20, PADDLE_WIDTH * 2) 
    elif powerup_type == "multi_ball":
        if len(balls) < 3:  
            new_ball = pygame.Rect(balls[0].centerx, balls[0].centery, BALL_RADIUS * 2, BALL_RADIUS * 2)
            balls.append(new_ball)

# --- Game Loop ---
game_state = MENU
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Game State Management ---
    if game_state == MENU:
        screen.fill(BLACK)
        draw_text("BREAKOUT", WIDTH // 2, HEIGHT // 3)
        draw_text("Press any key to start", WIDTH // 2, HEIGHT // 2)
        if any(pygame.key.get_pressed()):
            game_state = GAME
            reset_game()

    elif game_state == GAME:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
            paddle.x += PADDLE_SPEED

        for ball in balls[:]: 
            ball.x += ball_dx
            ball.y += ball_dy

            if ball.left <= 0 or ball.right >= WIDTH:
                ball_dx *= -1
            if ball.top <= 0:
                ball_dy *= -1

            if ball.colliderect(paddle):
                PADDLE_HIT_SOUND.play()
                ball_dy *= -1

            for brick in bricks[:]:
                if ball.colliderect(brick[0]):
                    BRICK_HIT_SOUND.play()
                    bricks.remove(brick)
                    ball_dy *= -1
                    score += 10
                    if random.random() < 0.1:  
                        powerups.append(create_powerup(brick[0].centerx, brick[0].centery))

            if ball.top > HEIGHT:
                balls.remove(ball) 

        if not balls:  
            GAME_OVER_SOUND.play()
            game_state = GAME_OVER

        # Update power-ups
        for powerup in powerups[:]:
            powerup[0].y += POWERUP_SPEED
            if powerup[0].colliderect(paddle):
                POWERUP_SOUND.play()
                apply_powerup(powerup[1])
                powerups.remove(powerup)
            elif powerup[0].top > HEIGHT:
                powerups.remove(powerup)

        # Draw everything
        screen.fill(BLACK)
        for brick, color in bricks:
            pygame.draw.rect(screen, color, brick)
        for powerup in powerups:
            pygame.draw.rect(screen, GREEN, powerup[0]) 
        pygame.draw.rect(screen, WHITE, paddle)
        for ball in balls:
            pygame.draw.circle(screen, RED, ball.center, BALL_RADIUS)

        draw_text(f"Score: {score}", 50, 20) 

    elif game_state == GAME_OVER:
        screen.fill(BLACK)
        draw_text("GAME OVER", WIDTH // 2, HEIGHT // 3)
        draw_text(f"Final Score: {score}", WIDTH // 2, HEIGHT // 2)
        draw_text("Press any key to restart", WIDTH // 2, HEIGHT // 2 + 50)
        if any(pygame.key.get_pressed()):
            game_state = GAME
            reset_game()

    pygame.display.flip()
    clock.tick(FPS) 

pygame.quit()
