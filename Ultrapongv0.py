import pygame
from array import array

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Screen setup - fixed size window
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Game with Sound")

# Define a function to generate beep sounds with varying frequencies
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * ((i // (sample_rate // frequency)) % 2)) for i in range(samples)]
    sound = pygame.mixer.Sound(buffer=array('h', wave))
    sound.set_volume(0.1)
    return sound

# Create a list of sound objects
collision_sound = generate_beep_sound(440, 0.1)  # Ball collision sound

# Ball properties
ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
ball_radius = 10
ball_dx = 4
ball_dy = 4

# Paddles properties
paddle1_pos = [30, SCREEN_HEIGHT // 2 - 50, 20, 100]  # [x, y, width, height]
paddle2_pos = [SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 - 50, 20, 100]

# Scores
score1 = 0
score2 = 0

# Win score
win_score = 5

# Font setup for displaying score and menu
font = pygame.font.Font(None, 36)

# Function to move paddles
def move_paddle(paddle, dy):
    paddle[1] += dy
    paddle[1] = max(0, min(SCREEN_HEIGHT - paddle[3], paddle[1]))

# Function to display start menu
def display_start_menu():
    screen.fill((0, 0, 0))
    title_text = font.render("Pong Game", True, (255, 255, 255))
    start_text = font.render("Press ENTER to Start", True, (255, 255, 255))
    quit_text = font.render("Press ESC to Quit", True, (255, 255, 255))
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))
    pygame.display.flip()

# Function to display pause menu
def display_pause_menu():
    screen.fill((0, 0, 0))
    pause_text = font.render("Game Paused", True, (255, 255, 255))
    resume_text = font.render("Press SPACE to Resume", True, (255, 255, 255))
    quit_text = font.render("Press ESC to Quit", True, (255, 255, 255))
    screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
    screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))
    pygame.display.flip()

# Function to display credits screen
def display_credits():
    screen.fill((0, 0, 0))
    credits_text = font.render("Pong Game Credits", True, (255, 255, 255))
    dev_text = font.render("Developed by: Cat-san", True, (255, 255, 255))
    exit_text = font.render("Press ESC to Exit", True, (255, 255, 255))
    screen.blit(credits_text, (SCREEN_WIDTH // 2 - credits_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
    screen.blit(dev_text, (SCREEN_WIDTH // 2 - dev_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))
    pygame.display.flip()

# Function to display win/lose message
def display_message(message):
    screen.fill((0, 0, 0))
    message_text = font.render(message, True, (255, 255, 255))
    screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2, SCREEN_HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(3000)  # Display message for 3 seconds

# Function to move AI paddle
def move_ai_paddle(paddle, ball_pos):
    if paddle[1] + paddle[3] // 2 < ball_pos[1]:
        paddle[1] += 4
    elif paddle[1] + paddle[3] // 2 > ball_pos[1]:
        paddle[1] -= 4
    paddle[1] = max(0, min(SCREEN_HEIGHT - paddle[3], paddle[1]))

# Main loop for start menu
running = True
game_started = False
paused = False
show_credits = False

while running:
    while not game_started:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game_started = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_started = True
                elif event.key == pygame.K_ESCAPE:
                    running = False

        display_start_menu()

    while running and game_started and not paused and not show_credits:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    move_paddle(paddle1_pos, -20)
                elif event.key == pygame.K_s:
                    move_paddle(paddle1_pos, 20)
                elif event.key == pygame.K_SPACE:
                    paused = True
                elif event.key == pygame.K_c:
                    show_credits = True

        # Move ball
        ball_pos[0] += ball_dx
        ball_pos[1] += ball_dy

        # Ball collision with top and bottom walls
        if ball_pos[1] - ball_radius <= 0 or ball_pos[1] + ball_radius >= SCREEN_HEIGHT:
            ball_dy = -ball_dy
            collision_sound.play()

        # Ball collision with paddles
        if (ball_pos[0] - ball_radius <= paddle1_pos[0] + paddle1_pos[2] and
            paddle1_pos[1] <= ball_pos[1] <= paddle1_pos[1] + paddle1_pos[3]) or \
           (ball_pos[0] + ball_radius >= paddle2_pos[0] and
            paddle2_pos[1] <= ball_pos[1] <= paddle2_pos[1] + paddle2_pos[3]):
            ball_dx = -ball_dx
            collision_sound.play()

        # Ball out of bounds
        if ball_pos[0] - ball_radius <= 0:
            score2 += 1
            ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
            ball_dx = -ball_dx
        elif ball_pos[0] + ball_radius >= SCREEN_WIDTH:
            score1 += 1
            ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
            ball_dx = -ball_dx

        # Move AI paddle
        move_ai_paddle(paddle2_pos, ball_pos)

        # Check for win conditions
        if score1 >= win_score:
            display_message("WINNER!")
            score1 = 0
            score2 = 0
            game_started = False
        elif score2 >= win_score:
            display_message("FAILURE!")
            score1 = 0
            score2 = 0
            game_started = False

        # Clear screen and render the scores
        screen.fill((0, 0, 0))
        score_text = font.render(f"{score1} - {score2}", True, (255, 255, 255))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 20))

        # Draw ball
        pygame.draw.circle(screen, (255, 255, 255), ball_pos, ball_radius)

        # Draw paddles
        pygame.draw.rect(screen, (255, 255, 255), paddle1_pos)
        pygame.draw.rect(screen, (255, 255, 255), paddle2_pos)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                paused = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = False
                elif event.key == pygame.K_ESCAPE:
                    running = False

        display_pause_menu()

    while show_credits:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                show_credits = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    show_credits = False

        display_credits()

pygame.quit()
