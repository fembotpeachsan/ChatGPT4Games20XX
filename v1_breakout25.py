import pygame
from array import array
import random

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Screen setup - fixed size window
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong with NX2 Sound")

# Define a function to generate beep sounds with varying frequencies
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * ((i // (sample_rate // frequency)) % 2)) for i in range(samples)]
    sound = pygame.mixer.Sound(buffer=array('h', wave))
    sound.set_volume(0.1)
    return sound

# Create sound effects for the game
sounds = {
    "paddle_hit": generate_beep_sound(523.25, 0.05),  # C5
    "wall_hit": generate_beep_sound(587.33, 0.05),   # D5
    "score": generate_beep_sound(659.25, 0.2),       # E5
}

# Paddle setup
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
paddle_speed = 5
paddle1 = pygame.Rect(30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = pygame.Rect(SCREEN_WIDTH - 30 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Ball setup
BALL_SIZE = 15
ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
ball_speed_x = 5 * random.choice((1, -1))
ball_speed_y = 5 * random.choice((1, -1))

# Score setup
score1, score2 = 0, 0
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Achievements
achievements = {
    "first_point": False,
    "five_points": False,
    "win_game": False,
}

# Game states
MAIN_MENU = 0
PLAYING = 1
CREDITS = 2
GAME_OVER = 3
game_state = MAIN_MENU

# AI for left paddle
def ai_move():
    if paddle1.centery < ball.centery:
        paddle1.y += paddle_speed
    elif paddle1.centery > ball.centery:
        paddle1.y -= paddle_speed

# Reset game
def reset_game():
    global score1, score2, ball_speed_x, ball_speed_y
    score1, score2 = 0, 0
    ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    ball_speed_x = 5 * random.choice((1, -1))
    ball_speed_y = 5 * random.choice((1, -1))
    paddle1.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
    paddle2.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2

# Main menu
def draw_main_menu():
    screen.fill((0, 0, 0))
    title_text = font.render("Pong with NX2 Sound", True, (255, 255, 255))
    start_text = small_font.render("Press SPACE to Start", True, (255, 255, 255))
    credits_text = small_font.render("Press C for Credits", True, (255, 255, 255))
    quit_text = small_font.render("Press Q to Quit", True, (255, 255, 255))
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 200))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 300))
    screen.blit(credits_text, (SCREEN_WIDTH // 2 - credits_text.get_width() // 2, 350))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 400))

# Credits screen
def draw_credits():
    screen.fill((0, 0, 0))
    credits_text = font.render("Credits", True, (255, 255, 255))
    developer_text = small_font.render("Developed by Your Name", True, (255, 255, 255))
    back_text = small_font.render("Press B to go back", True, (255, 255, 255))
    screen.blit(credits_text, (SCREEN_WIDTH // 2 - credits_text.get_width() // 2, 200))
    screen.blit(developer_text, (SCREEN_WIDTH // 2 - developer_text.get_width() // 2, 300))
    screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 400))

# Achievements screen
def draw_achievements():
    screen.fill((0, 0, 0))
    achievements_text = font.render("Achievements", True, (255, 255, 255))
    screen.blit(achievements_text, (SCREEN_WIDTH // 2 - achievements_text.get_width() // 2, 100))
    y_offset = 200
    for achievement, unlocked in achievements.items():
        status = "Unlocked" if unlocked else "Locked"
        achievement_text = small_font.render(f"{achievement}: {status}", True, (255, 255, 255))
        screen.blit(achievement_text, (SCREEN_WIDTH // 2 - achievement_text.get_width() // 2, y_offset))
        y_offset += 50
    back_text = small_font.render("Press B to go back", True, (255, 255, 255))
    screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, y_offset + 50))

# Game over screen
def draw_game_over(winner):
    screen.fill((0, 0, 0))
    game_over_text = font.render("Game Over", True, (255, 255, 255))
    winner_text = font.render(f"Player {winner} Wins!", True, (255, 255, 255))
    restart_text = small_font.render("Press SPACE to Restart", True, (255, 255, 255))
    menu_text = small_font.render("Press M for Main Menu", True, (255, 255, 255))
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 200))
    screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, 300))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 400))
    screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, 450))

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if game_state == MAIN_MENU:
        draw_main_menu()
        if keys[pygame.K_SPACE]:
            reset_game()
            game_state = PLAYING
        if keys[pygame.K_c]:
            game_state = CREDITS
        if keys[pygame.K_q]:
            running = False

    elif game_state == CREDITS:
        draw_credits()
        if keys[pygame.K_b]:
            game_state = MAIN_MENU

    elif game_state == PLAYING:
        # Paddle movement
        if keys[pygame.K_w] and paddle1.top > 0:
            paddle1.y -= paddle_speed
        if keys[pygame.K_s] and paddle1.bottom < SCREEN_HEIGHT:
            paddle1.y += paddle_speed
        if keys[pygame.K_UP] and paddle2.top > 0:
            paddle2.y -= paddle_speed
        if keys[pygame.K_DOWN] and paddle2.bottom < SCREEN_HEIGHT:
            paddle2.y += paddle_speed

        # AI for left paddle if no input
        if not (keys[pygame.K_w] or keys[pygame.K_s]):
            ai_move()

        # Ball movement
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Ball collision with top and bottom
        if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
            ball_speed_y *= -1
            sounds["wall_hit"].play()

        # Ball collision with paddles
        if ball.colliderect(paddle1) or ball.colliderect(paddle2):
            ball_speed_x *= -1
            sounds["paddle_hit"].play()

        # Ball out of bounds
        if ball.left <= 0:
            score2 += 1
            sounds["score"].play()
            ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            ball_speed_x *= random.choice((1, -1))
            ball_speed_y *= random.choice((1, -1))
        if ball.right >= SCREEN_WIDTH:
            score1 += 1
            sounds["score"].play()
            ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            ball_speed_x *= random.choice((1, -1))
            ball_speed_y *= random.choice((1, -1))

        # Check for game over
        if score1 >= 5 or score2 >= 5:
            winner = 1 if score1 >= 5 else 2
            game_state = GAME_OVER

        # Clear screen
        screen.fill((0, 0, 0))

        # Draw paddles and ball
        pygame.draw.rect(screen, (255, 255, 255), paddle1)
        pygame.draw.rect(screen, (255, 255, 255), paddle2)
        pygame.draw.ellipse(screen, (255, 255, 255), ball)
        pygame.draw.aaline(screen, (255, 255, 255), (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))

        # Draw scores
        score_text = font.render(f"{score1}  {score2}", True, (255, 255, 255))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 70, 10))

    elif game_state == GAME_OVER:
        winner = 1 if score1 >= 5 else 2
        draw_game_over(winner)
        if keys[pygame.K_SPACE]:
            reset_game()
            game_state = PLAYING
        if keys[pygame.K_m]:
            game_state = MAIN_MENU

    pygame.display.flip()
    pygame.time.wait(30)

pygame.quit()
