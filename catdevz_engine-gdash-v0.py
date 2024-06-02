import pygame
import random
from array import array

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash Clone with SFX")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Game variables
player_size = 50
player_x = 100
player_y = HEIGHT - player_size
player_vel = 10

obstacle_width = 20
obstacle_height = 70
obstacle_color = RED
obstacle_speed = 7
obstacles = []

# Player jump variables
is_jump = False
jump_count = 10

# Clock
clock = pygame.time.Clock()
FPS = 30

# Font
font = pygame.font.SysFont("Arial", 30)

# Define a function to generate beep sounds with varying frequencies
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * ((i // (sample_rate // frequency)) % 2)) for i in range(samples)]
    sound = pygame.mixer.Sound(buffer=array('h', wave))
    sound.set_volume(0.1)
    return sound

# Create a list of sound tuples (name, sound object)
sounds = [
    ("SND_1", generate_beep_sound(440, 0.1)),  # A4
    ("SND_2", generate_beep_sound(523.25, 0.1)),  # C5
    ("SND_3", generate_beep_sound(587.33, 0.1)),  # D5
    ("SND_4", generate_beep_sound(659.25, 0.1)),  # E5
]

jump_sound = sounds[0][1]
collision_sound = sounds[1][1]

# HUD variables
score = 0
high_score = 0

def draw_window():
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, (player_x, player_y, player_size, player_size))

    for obstacle in obstacles:
        pygame.draw.rect(screen, obstacle_color, obstacle)

    # Draw the HUD
    score_text = font.render(f"Score: {score}", True, BLACK)
    high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 40))

    pygame.display.update()

def draw_main_menu():
    screen.fill(WHITE)
    title_text = font.render("Geometry Dash Clone", True, BLACK)
    start_text = font.render("Press ENTER to Start", True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - title_text.get_height() // 2 - 20))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 - start_text.get_height() // 2 + 20))
    pygame.display.update()

def main():
    global player_y, is_jump, jump_count, score, high_score

    run = True
    game_active = False
    score = 0

    while run:
        clock.tick(FPS)

        if not game_active:
            draw_main_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game_active = True
                        obstacles.clear()
                        player_y = HEIGHT - player_size
                        is_jump = False
                        jump_count = 10
                        score = 0
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            keys = pygame.key.get_pressed()

            if not is_jump:
                if keys[pygame.K_SPACE]:
                    is_jump = True
                    jump_sound.play()
            else:
                if jump_count >= -10:
                    neg = 1
                    if jump_count < 0:
                        neg = -1
                    player_y -= (jump_count ** 2) * 0.5 * neg
                    jump_count -= 1
                else:
                    is_jump = False
                    jump_count = 10

            # Move obstacles
            for obstacle in obstacles:
                obstacle.x -= obstacle_speed
                if obstacle.x < 0:
                    obstacles.remove(obstacle)
                    score += 1

            # Spawn new obstacles
            if len(obstacles) == 0 or obstacles[-1].x < WIDTH - 200:
                new_obstacle = pygame.Rect(WIDTH, HEIGHT - obstacle_height, obstacle_width, obstacle_height)
                obstacles.append(new_obstacle)

            # Check for collisions
            player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
            for obstacle in obstacles:
                if player_rect.colliderect(obstacle):
                    collision_sound.play()
                    game_active = False
                    if score > high_score:
                        high_score = score

            draw_window()

    pygame.quit()

if __name__ == "__main__":
    main()
