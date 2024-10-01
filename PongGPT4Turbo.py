import pygame
from pygame.locals import *
import numpy as np

# Initialize PyGame
pygame.init()
pygame.mixer.init()

# Set up the game window
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()

# Function to generate a beep sound
def generate_beep(frequency, duration, volume=1.0):
    sample_rate = 44100
    n_samples = int(round(duration * sample_rate))
    buf = np.zeros((n_samples, 2), dtype=np.int16)
    max_sample = 2**15 - 1
    for s in range(n_samples):
        t = float(s) / sample_rate
        buf[s][0] = int(round(max_sample * volume * np.sin(2 * np.pi * frequency * t)))  # Left channel
        buf[s][1] = buf[s][0]  # Right channel
    return pygame.sndarray.make_sound(buf)

# Generate beep and boop sounds
beep_sound = generate_beep(440, 0.1)  # A4 note
boop_sound = generate_beep(330, 0.1)  # E4 note

# Function to display the main menu
def main_menu():
    menu = True
    while menu:
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont("Arial", 50)
        title_text = font.render("PONG", True, (255, 255, 255))
        screen.blit(title_text, (150, 100))
        
        font = pygame.font.SysFont("Arial", 30)
        start_text = font.render("Press ENTER to Start", True, (255, 255, 255))
        screen.blit(start_text, (80, 200))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    menu = False

# Function to handle game over and prompt for restart
def game_over_screen(winner):
    game_over = True
    while game_over:
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont("Arial", 50)
        game_over_text = font.render(f"{winner} Wins!", True, (255, 255, 255))
        screen.blit(game_over_text, (100, 100))
        
        font = pygame.font.SysFont("Arial", 30)
        restart_text = font.render("Restart? [Y/N]", True, (255, 255, 255))
        screen.blit(restart_text, (120, 200))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_y:
                    return True
                elif event.key == K_n:
                    pygame.quit()
                    exit()

# Function to reset the game variables
def reset_game():
    global ball_pos, ball_vel, paddle1_pos, paddle2_pos, score1, score2
    ball_pos = np.array([200, 150], dtype=float)
    ball_vel = np.array([3, -3], dtype=float)
    paddle1_pos = np.array([10, 150], dtype=float)
    paddle2_pos = np.array([380, 150], dtype=float)
    score1 = 0
    score2 = 0

# Game variables
reset_game()

# Display the main menu
main_menu()

# Main game loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    keys = pygame.key.get_pressed()
    if keys[K_UP] and paddle1_pos[1] > 0:
        paddle1_pos[1] -= paddle1_vel
    if keys[K_DOWN] and paddle1_pos[1] < 220:
        paddle1_pos[1] += paddle1_vel

    # AI for right paddle
    if paddle2_pos[1] + 40 < ball_pos[1] and paddle2_pos[1] < 220:
        paddle2_pos[1] += paddle2_vel
    if paddle2_pos[1] + 40 > ball_pos[1] and paddle2_pos[1] > 0:
        paddle2_pos[1] -= paddle2_vel

    # Update ball position
    ball_pos += ball_vel

    # Bounce ball off walls
    if ball_pos[1] <= 0 or ball_pos[1] >= 290:
        ball_vel[1] *= -1
        beep_sound.play()

    # Check for collisions with paddles
    if paddle1_pos[0] < ball_pos[0] < paddle1_pos[0] + 10 and paddle1_pos[1] < ball_pos[1] < paddle1_pos[1] + 80:
        ball_vel[0] *= -1
        boop_sound.play()
    if paddle2_pos[0] < ball_pos[0] < paddle2_pos[0] + 10 and paddle2_pos[1] < ball_pos[1] < paddle2_pos[1] + 80:
        ball_vel[0] *= -1
        boop_sound.play()

    # Update scores
    if ball_pos[0] <= 0:
        score2 += 1
        ball_pos = np.array([200, 150], dtype=float)
        ball_vel[1] *= -1
    elif ball_pos[0] >= 400:
        score1 += 1
        ball_pos = np.array([200, 150], dtype=float)
        ball_vel[0] *= -1

    # Check for game over
    if score1 >= 5:
        if game_over_screen("Player 1"):
            reset_game()
        else:
            break
    elif score2 >= 5:
        if game_over_screen("Player 2"):
            reset_game()
        else:
            break

    # Draw everything on the screen
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 255, 255), [paddle1_pos[0], paddle1_pos[1], 10, 80])
    pygame.draw.rect(screen, (255, 255, 255), [paddle2_pos[0], paddle2_pos[1], 10, 80])
    pygame.draw.circle(screen, (255, 255, 255), ball_pos.astype(int), 10)
    font = pygame.font.SysFont("Arial", 30)
    score_text1 = font.render("Player 1: " + str(score1), True, (255, 255, 255))
    score_text2 = font.render("Player 2: " + str(score2), True, (255, 255, 255))
    screen.blit(score_text1, (10, 10))
    screen.blit(score_text2, (250, 10))

    # Update the display
    pygame.display.update()

    # Limit frame rate to 60 FPS
    clock.tick(60)

# Clean up PyGame resources
pygame.quit()
