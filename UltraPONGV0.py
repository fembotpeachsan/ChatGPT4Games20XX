import pygame
import numpy as np

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
FONT_SIZE = 30
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
PADDLE_SPEED = 10
BALL_RADIUS = 10
BALL_SPEED = 5
BRICK_WIDTH, BRICK_HEIGHT = 75, 30
BRICK_ROWS, BRICK_COLUMNS = 5, 10
BRICK_SPACING = 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Create a window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong with a Twist")

# Using system font
font = pygame.font.SysFont(None, FONT_SIZE)
clock = pygame.time.Clock()

# Functions for sound effects, brick creation, text rendering, and the main menu
def create_chiptune_beep_sound(frequency, duration):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(frequency * 2 * np.pi * t)
    sound = np.zeros((wave.size, 2), dtype=np.int16)
    sound[:, 0] = wave * 32767
    sound[:, 1] = wave * 32767
    sound_array = pygame.sndarray.make_sound(sound)
    return sound_array

bounce_beep = create_chiptune_beep_sound(440, 0.1)
brick_beep = create_chiptune_beep_sound(523.25, 0.1)

def create_bricks():
    bricks = []
    for i in range(BRICK_ROWS):
        for j in range(BRICK_COLUMNS):
            brick = pygame.Rect(
                j * (BRICK_WIDTH + BRICK_SPACING) + BRICK_SPACING,
                i * (BRICK_HEIGHT + BRICK_SPACING) + BRICK_SPACING + 50,
                BRICK_WIDTH,
                BRICK_HEIGHT)
            bricks.append(brick)
    return bricks

def draw_text_centered(message, font, color, surface, x, y):
    text_obj = font.render(message, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

def main_menu():
    menu = True
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_loop()  # Start the game
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

        screen.fill(BLACK)
        draw_text_centered("Pong with a Twist", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        draw_text_centered("Press ENTER to Start", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text_centered("Press ESC to Quit", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        pygame.display.update()
        clock.tick(FPS)

def game_over(score):
    over = True
    while over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    game_loop()  # Restart the game
                elif event.key == pygame.K_n:
                    main_menu()  # Return to main menu

        screen.fill(BLACK)
        draw_text_centered("Game Over", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        draw_text_centered(f"Score: {score}", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text_centered("Play Again? (Y/N)", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        pygame.display.update()
        clock.tick(FPS)

def game_loop():
    global bricks
    bricks = create_bricks()
    paddle = pygame.Rect(SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, SCREEN_HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_RADIUS, SCREEN_HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
    ball_dir = [BALL_SPEED, -BALL_SPEED]
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and paddle.left > 0:
            paddle.move_ip(-PADDLE_SPEED, 0)
        if key[pygame.K_RIGHT] and paddle.right < SCREEN_WIDTH:
            paddle.move_ip(PADDLE_SPEED, 0)

        ball.move_ip(ball_dir[0], ball_dir[1])
        if ball.left <= 0 or ball.right >= SCREEN_WIDTH:
            ball_dir[0] = -ball_dir[0]
            bounce_beep.play()
        if ball.top <= 0 or ball.colliderect(paddle):
            ball_dir[1] = -ball_dir[1]
            bounce_beep.play()
        if ball.bottom >= SCREEN_HEIGHT:
            game_over(score)  # Game over
            running = False

        for brick in bricks[:]:
            if ball.colliderect(brick):
                brick_beep.play()
                score += 1
                bricks.remove(brick)
                ball_dir[1] = -ball_dir[1]
                break

        screen.fill(BLACK)
        for brick in bricks:
            pygame.draw.rect(screen, GREEN, brick)
        pygame.draw.rect(screen, WHITE, paddle)
        pygame.draw.ellipse(screen, WHITE, ball)
        draw_text_centered(f"Score: {score}", font, WHITE, screen, 50, 30)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

# Start the game from the main menu
main_menu()
