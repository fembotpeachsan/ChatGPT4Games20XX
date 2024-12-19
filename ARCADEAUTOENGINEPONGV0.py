import pygame
import sys
from array import array
import math

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Paddle dimensions and speed
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 80
PADDLE_SPEED = 6

# Ball dimensions and speed
BALL_SIZE = 15
BALL_SPEED = 4

# Score limit
WINNING_SCORE = 5

# Sound configuration
sound_mode = "stereo"

# Initialize font
font = pygame.font.Font(None, 74)

# Function to draw a paddle
def draw_paddle(x, y):
    pygame.draw.rect(screen, WHITE, (x, y, PADDLE_WIDTH, PADDLE_HEIGHT))

# Function to draw the ball
def draw_ball(x, y):
    pygame.draw.rect(screen, WHITE, (x, y, BALL_SIZE, BALL_SIZE))

# Function to draw scores
def draw_scores(player1_score, player2_score):
    score1_text = font.render(str(player1_score), True, WHITE)
    score2_text = font.render(str(player2_score), True, WHITE)
    screen.blit(score1_text, (SCREEN_WIDTH // 4, 10))
    screen.blit(score2_text, (SCREEN_WIDTH * 3 // 4 - score2_text.get_width(), 10))

# Function to generate beep sound
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)) for i in range(samples)]
    sound = pygame.mixer.Sound(buffer=array('h', wave))
    sound.set_volume(0.2)
    return sound

# Generate sound for paddle hits
paddle_hit_sound = generate_beep_sound(440, 0.2)

# Function to toggle sound mode
def toggle_sound_mode():
    global sound_mode
    if sound_mode == "stereo":
        sound_mode = "mono"
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
    else:
        sound_mode = "stereo"
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Display the main menu
def main_menu():
    menu_font = pygame.font.Font(None, 36)
    selected_option = 0
    options = ["Start Game", f"Sound: {sound_mode}", "Exit"]

    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        return
                    elif selected_option == 1:
                        toggle_sound_mode()
                        options[1] = f"Sound: {sound_mode}"
                    elif selected_option == 2:
                        pygame.quit()
                        sys.exit()

        for i, option in enumerate(options):
            text = menu_font.render("> " + option if i == selected_option else option, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50 + i * 50))
        
        pygame.display.flip()

# Display "Game Over" screen
def game_over(winner):
    over_font = pygame.font.Font(None, 74)
    prompt_font = pygame.font.Font(None, 36)

    while True:
        screen.fill(BLACK)
        game_over_text = over_font.render(f"Player {winner} Wins!", True, WHITE)
        restart_text = prompt_font.render("Restart? Y/N", True, WHITE)

        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_n:
                    return False

        pygame.display.flip()

# Main game function
def main_game():
    player1_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
    player2_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
    ball_x = SCREEN_WIDTH // 2 - BALL_SIZE // 2
    ball_y = SCREEN_HEIGHT // 2 - BALL_SIZE // 2
    ball_x_speed = BALL_SPEED
    ball_y_speed = BALL_SPEED
    player1_score = 0
    player2_score = 0

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Paddle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player1_y > 0:
            player1_y -= PADDLE_SPEED
        if keys[pygame.K_s] and player1_y < SCREEN_HEIGHT - PADDLE_HEIGHT:
            player1_y += PADDLE_SPEED
        if keys[pygame.K_UP] and player2_y > 0:
            player2_y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and player2_y < SCREEN_HEIGHT - PADDLE_HEIGHT:
            player2_y += PADDLE_SPEED

        # Ball movement
        ball_x += ball_x_speed
        ball_y += ball_y_speed

        # Ball collision with walls
        if ball_y <= 0 or ball_y >= SCREEN_HEIGHT - BALL_SIZE:
            ball_y_speed = -ball_y_speed

        # Ball collision with paddles
        if (ball_x <= 50 + PADDLE_WIDTH and player1_y < ball_y + BALL_SIZE and player1_y + PADDLE_HEIGHT > ball_y) or \
           (ball_x >= SCREEN_WIDTH - 50 - PADDLE_WIDTH - BALL_SIZE and player2_y < ball_y + BALL_SIZE and player2_y + PADDLE_HEIGHT > ball_y):
            ball_x_speed = -ball_x_speed
            paddle_hit_sound.play()

        # Scoring
        if ball_x < 0:
            player2_score += 1
            ball_x, ball_y = SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2
            ball_x_speed = BALL_SPEED
        elif ball_x > SCREEN_WIDTH:
            player1_score += 1
            ball_x, ball_y = SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2
            ball_x_speed = -BALL_SPEED

        # Check for winner
        if player1_score >= WINNING_SCORE or player2_score >= WINNING_SCORE:
            winner = 1 if player1_score >= WINNING_SCORE else 2
            if game_over(winner):
                return True  # Restart game
            else:
                return False  # Quit game

        # Drawing
        screen.fill(BLACK)
        draw_paddle(50, player1_y)  # Left paddle
        draw_paddle(SCREEN_WIDTH - 50 - PADDLE_WIDTH, player2_y)  # Right paddle
        draw_ball(ball_x, ball_y)
        draw_scores(player1_score, player2_score)
        
        # Draw center line
        for y in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 2, y, 4, 10))
        
        pygame.display.flip()
        clock.tick(60)  # 60 FPS

# Main game loop
def main():
    while True:
        main_menu()
        restart = main_game()
        if not restart:
            break
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
