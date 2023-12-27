import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the game window
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Pong')

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game States
MAIN_MENU, GAME, EXIT = 0, 1, 2
game_state = MAIN_MENU

# Font
font = pygame.font.Font(None, 36)

# Clock for controlling frame rate
clock = pygame.time.Clock()

def draw_main_menu():
    screen.fill(BLACK)
    title = font.render("Pong", True, WHITE)
    start_game = font.render("Start Game", True, WHITE)
    exit_game = font.render("Exit", True, WHITE)

    screen.blit(title, (width / 2 - title.get_width() / 2, 100))
    screen.blit(start_game, (width / 2 - start_game.get_width() / 2, 200))
    screen.blit(exit_game, (width / 2 - exit_game.get_width() / 2, 300))
    pygame.display.flip()

def pong_game():
    # Game variables
    paddle_width, paddle_height = 15, 90
    ball_size = 15
    player_score, opponent_score = 0, 0
    ball_speed_x, ball_speed_y = 3, 3
    opponent_speed = 3  # Speed of the opponent's paddle

    # Paddle positions and ball position
    player_paddle = pygame.Rect(width - paddle_width - 20, height / 2 - paddle_height / 2, paddle_width, paddle_height)
    opponent_paddle = pygame.Rect(20, height / 2 - paddle_height / 2, paddle_width, paddle_height)
    ball = pygame.Rect(width / 2 - ball_size / 2, height / 2 - ball_size / 2, ball_size, ball_size)

    while game_state == GAME:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MAIN_MENU

        # Player paddle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player_paddle.y -= 7
        if keys[pygame.K_DOWN]:
            player_paddle.y += 7

        # Opponent AI Movement
        if opponent_paddle.centery < ball.centery:
            opponent_paddle.y += opponent_speed
        elif opponent_paddle.centery > ball.centery:
            opponent_paddle.y -= opponent_speed

        # Keep paddles on screen
        if opponent_paddle.top < 0:
            opponent_paddle.top = 0
        if opponent_paddle.bottom > height:
            opponent_paddle.bottom = height
        if player_paddle.top < 0:
            player_paddle.top = 0
        if player_paddle.bottom > height:
            player_paddle.bottom = height

        # Ball movement and collision
        ball.x += ball_speed_x
        ball.y += ball_speed_y
        if ball.top <= 0 or ball.bottom >= height:
            ball_speed_y *= -1
        if ball.colliderect(player_paddle) or ball.colliderect(opponent_paddle):
            ball_speed_x *= -1

        # Score update and ball reset
        if ball.left <= 0:
            opponent_score += 1
            ball.center = (width / 2, height / 2)
            ball_speed_x, ball_speed_y = 3, 3
        if ball.right >= width:
            player_score += 1
            ball.center = (width / 2, height / 2)
            ball_speed_x, ball_speed_y = -3, 3

        # Drawing
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, player_paddle)
        pygame.draw.rect(screen, WHITE, opponent_paddle)
        pygame.draw.ellipse(screen, WHITE, ball)
        pygame.draw.aaline(screen, WHITE, (width / 2, 0), (width / 2, height))

        # Display scores
        player_text = font.render(str(player_score), True, WHITE)
        opponent_text = font.render(str(opponent_score), True, WHITE)
        screen.blit(player_text, (width / 2 + 30, 20))
        screen.blit(opponent_text, (width / 2 - 50, 20))

        pygame.display.flip()
        clock.tick(60)  # 60 frames per second

while True:
    if game_state == MAIN_MENU:
        draw_main_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state = EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = GAME
                elif event.key == pygame.K_ESCAPE:
                    game_state = EXIT

    elif game_state == GAME:
        game_state = pong_game()

    elif game_state == EXIT:
        pygame.quit()
        sys.exit()
