import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
PADDLE_SPEED = 7
BALL_SPEED_X, BALL_SPEED_Y = 5, 5

# Game States
STATE_MENU = 1
STATE_PONG = 2
STATE_FILE_SELECT = 3

# Setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong and File Select Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# Pong Game Variables
player_paddle = pygame.Rect(30, SCREEN_HEIGHT // 2 - 50, 10, 100)
opponent_paddle = pygame.Rect(SCREEN_WIDTH - 40, SCREEN_HEIGHT // 2 - 50, 10, 100)
ball = pygame.Rect(SCREEN_WIDTH // 2 - 7, SCREEN_HEIGHT // 2 - 7, 15, 15)
ball_speed = [BALL_SPEED_X, BALL_SPEED_Y]

# File Select Variables
selected_file = 0
file_options = ["File 1", "File 2", "File 3", "Delete File"]

# Game state
game_state = STATE_MENU

def reset_ball():
    ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    ball_speed[0] = BALL_SPEED_X * (-1 if ball_speed[0] > 0 else 1)
    ball_speed[1] = BALL_SPEED_Y * (-1 if ball_speed[1] > 0 else 1)

# Game loop
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # State logic
    if game_state == STATE_MENU:
        screen.fill(BLACK)
        title_text = font.render("Main Menu - Press 1 for Pong, 2 for File Select", True, WHITE)
        screen.blit(title_text, (50, 50))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            game_state = STATE_PONG
        elif keys[pygame.K_2]:
            game_state = STATE_FILE_SELECT

    elif game_state == STATE_PONG:
        # Pong game logic
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and player_paddle.top > 0:
            player_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and player_paddle.bottom < SCREEN_HEIGHT:
            player_paddle.y += PADDLE_SPEED

        # Move the ball
        ball.x += ball_speed[0]
        ball.y += ball_speed[1]

        # Ball collision with top and bottom
        if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
            ball_speed[1] = -ball_speed[1]

        # Ball collision with paddles
        if ball.colliderect(player_paddle) or ball.colliderect(opponent_paddle):
            ball_speed[0] = -ball_speed[0]

        # Ball out of bounds
        if ball.left <= 0 or ball.right >= SCREEN_WIDTH:
            reset_ball()

        # Opponent AI movement
        if opponent_paddle.centery < ball.centery:
            opponent_paddle.y += min(PADDLE_SPEED, ball.centery - opponent_paddle.centery)
        elif opponent_paddle.centery > ball.centery:
            opponent_paddle.y -= min(PADDLE_SPEED, opponent_paddle.centery - ball.centery)

        # Drawing the game
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, player_paddle)
        pygame.draw.rect(screen, WHITE, opponent_paddle)
        pygame.draw.ellipse(screen, WHITE, ball)

    elif game_state == STATE_FILE_SELECT:
        screen.fill(BLACK)
        for i, option in enumerate(file_options):
            color = WHITE if i == selected_file else (180, 180, 180)
            file_text = font.render(option, True, color)
            screen.blit(file_text, (100, 100 + 30 * i))

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_file = max(0, selected_file - 1)
                elif event.key == pygame.K_DOWN:
                    selected_file = min(len(file_options) - 1, selected_file + 1)
                elif event.key == pygame.K_RETURN:
                    print(f"Launching game with {file_options[selected_file]}")
                    game_state = STATE_PONG

    # Update screen
    pygame.display.flip()
    clock.tick(60)
