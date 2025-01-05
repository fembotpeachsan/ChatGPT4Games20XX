import pygame
from array import array
import random

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong with Audio")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Game states
STATE_MENU = 0
STATE_PLAY = 1
STATE_CREDITS = 2
STATE_EXIT = 3
current_state = STATE_MENU

# Paddle and Ball settings
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 15
PADDLE_SPEED = 5
BALL_SPEED_X, BALL_SPEED_Y = 4, 4

# Initialize paddles and ball
player_paddle = pygame.Rect(30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
opponent_paddle = pygame.Rect(SCREEN_WIDTH - 30 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Ball direction
ball_dx, ball_dy = BALL_SPEED_X, BALL_SPEED_Y

# Function to generate beep sounds
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * ((i // (sample_rate // frequency)) % 2)) for i in range(samples)]
    sound = pygame.mixer.Sound(buffer=array('h', wave))
    sound.set_volume(0.1)
    return sound

# Create sounds for ball collisions
sounds = [
    generate_beep_sound(440, 0.1),  # A4
    generate_beep_sound(523.25, 0.1),  # C5
    generate_beep_sound(587.33, 0.1),  # D5
    generate_beep_sound(659.25, 0.1),  # E5
]

# Function to draw text on the screen
def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Main Menu
def main_menu():
    global current_state
    screen.fill(BLACK)
    draw_text("Pong with Audio", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    draw_text("Press P to Play", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text("Press C for Credits", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
    draw_text("Press Q to Quit", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
    draw_text("Copyright © 2023 Your Name", small_font, GRAY, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            current_state = STATE_EXIT
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                current_state = STATE_PLAY
            elif event.key == pygame.K_c:
                current_state = STATE_CREDITS
            elif event.key == pygame.K_q:
                current_state = STATE_EXIT

# Credits Screen
def credits():
    global current_state
    screen.fill(BLACK)
    draw_text("Credits", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    draw_text("Game Developed by Your Name", small_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text("Audio by Your Name", small_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
    draw_text("Press M to Return to Menu", small_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            current_state = STATE_EXIT
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                current_state = STATE_MENU

# Game Play
def play():
    global current_state, ball_dx, ball_dy

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            current_state = STATE_EXIT

    # Paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player_paddle.top > 0:
        player_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and player_paddle.bottom < SCREEN_HEIGHT:
        player_paddle.y += PADDLE_SPEED

    # Opponent AI (simple tracking)
    if opponent_paddle.centery < ball.centery:
        opponent_paddle.y += PADDLE_SPEED
    elif opponent_paddle.centery > ball.centery:
        opponent_paddle.y -= PADDLE_SPEED

    # Ball movement
    ball.x += ball_dx
    ball.y += ball_dy

    # Ball collision with top and bottom
    if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
        ball_dy *= -1
        random.choice(sounds).play()  # Play a random sound on collision

    # Ball collision with paddles
    if ball.colliderect(player_paddle) or ball.colliderect(opponent_paddle):
        ball_dx *= -1
        random.choice(sounds).play()  # Play a random sound on collision

    # Ball out of bounds (left or right)
    if ball.left <= 0 or ball.right >= SCREEN_WIDTH:
        ball.x, ball.y = SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2
        ball_dx, ball_dy = BALL_SPEED_X * random.choice([-1, 1]), BALL_SPEED_Y * random.choice([-1, 1])

    # Clear screen
    screen.fill(BLACK)

    # Draw paddles and ball
    pygame.draw.rect(screen, WHITE, player_paddle)
    pygame.draw.rect(screen, WHITE, opponent_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)

    # Draw center line
    pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))

    # Draw "Press M to Return to Menu"
    draw_text("Press M to Return to Menu", small_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)

    # Check for return to menu
    keys = pygame.key.get_pressed()
    if keys[pygame.K_m]:
        current_state = STATE_MENU

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    if current_state == STATE_MENU:
        main_menu()
    elif current_state == STATE_PLAY:
        play()
    elif current_state == STATE_CREDITS:
        credits()
    elif current_state == STATE_EXIT:
        running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
