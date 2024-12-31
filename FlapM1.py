import pygame
import sys
import random
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 600
screen_height = 500
screen = pygame.display.set_mode((screen_width, screen_height))

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
yellow = (255, 255, 0)
green = (0, 255, 0)

# Clock to control the frame rate
clock = pygame.time.Clock()

# Bird properties
bird_size = 20
bird_color = yellow
bird_x = screen_width // 4
bird_y = screen_height // 2
bird_velocity = 0
gravity = 0.5
jump_power = -8

# Pipe properties
pipe_width = 50
pipe_color = green
pipe_gap = 200
pipe_velocity = -3
pipes = []

# Score
score = 0
font = pygame.font.Font(None, 36)

# Game state
game_state = "menu"  # Can be "menu", "playing", or "game_over"

# Create sine wave sound effect
def generate_sound(frequency, duration, volume=0.5):
    """Generates a sine wave sound."""
    sample_rate = 44100  # Hz
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = (32767 * volume * np.sin(2 * np.pi * frequency * t)).astype(np.int16)
    # Convert mono audio to stereo
    wave_stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(wave_stereo)

# Load sound effects
flap_sound = generate_sound(500, 0.1, 0.5)
collision_sound = generate_sound(200, 0.2, 0.7)

def create_pipe():
    """Creates a new pipe at the right edge of the screen."""
    top_pipe_height = random.randint(100, 300)
    bottom_pipe_y = top_pipe_height + pipe_gap
    top_pipe = pygame.Rect(screen_width, 0, pipe_width, top_pipe_height)
    bottom_pipe = pygame.Rect(screen_width, bottom_pipe_y, pipe_width, screen_height - bottom_pipe_y)
    return top_pipe, bottom_pipe

def draw_bird(x, y):
    """Draws the bird as a rectangle."""
    pygame.draw.rect(screen, bird_color, (x, y, bird_size, bird_size))

def draw_pipes(pipes):
    """Draws the pipes on the screen."""
    for top_pipe, bottom_pipe in pipes:
        pygame.draw.rect(screen, pipe_color, top_pipe)
        pygame.draw.rect(screen, pipe_color, bottom_pipe)

def draw_score(score):
    """Displays the score on the screen."""
    score_text = font.render("Score: " + str(score), True, white)
    screen.blit(score_text, (10, 10))

def draw_menu():
    """Draws the main menu."""
    title_text = font.render("Flappy Bird", True, white)
    title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 4))
    screen.blit(title_text, title_rect)

    start_text = font.render("Press Space to Start", True, white)
    start_rect = start_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(start_text, start_rect)

def draw_game_over():
    """Draws the game over screen."""
    game_over_text = font.render("Game Over", True, white)
    game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 3))
    screen.blit(game_over_text, game_over_rect)

    restart_text = font.render("Press Space to Restart", True, white)
    restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(restart_text, restart_rect)

def check_collision(pipes, bird_rect):
    """Checks for collisions between the bird and pipes or the ground."""
    if bird_rect.colliderect(ground_rect):
        return True
    for top_pipe, bottom_pipe in pipes:
        if bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe):
            return True
    return False

# Initialize pipes
for i in range(2):
    top_pipe, bottom_pipe = create_pipe()
    top_pipe.x = screen_width + i * (screen_width // 2 + pipe_width)
    bottom_pipe.x = screen_width + i * (screen_width // 2 + pipe_width)
    pipes.append((top_pipe, bottom_pipe))

# Ground Rect
ground_rect = pygame.Rect(0, screen_height - 20, screen_width, 20)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == "menu":
                    game_state = "playing"
                    score = 0
                    pipes = []
                    for i in range(2):
                        top_pipe, bottom_pipe = create_pipe()
                        top_pipe.x = screen_width + i * (screen_width // 2 + pipe_width)
                        bottom_pipe.x = screen_width + i * (screen_width // 2 + pipe_width)
                        pipes.append((top_pipe, bottom_pipe))
                    bird_y = screen_height // 2
                    bird_velocity = 0
                elif game_state == "playing":
                    bird_velocity = jump_power
                    flap_sound.play()
                elif game_state == "game_over":
                    game_state = "menu"

    # Clear the screen
    screen.fill(blue)

    # Draw ground
    pygame.draw.rect(screen, green, ground_rect)

    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        # Bird physics
        bird_velocity += gravity
        bird_y += bird_velocity

        # Move pipes and create new ones if needed
        for i in range(len(pipes)):
            pipes[i][0].x += pipe_velocity
            pipes[i][1].x += pipe_velocity

        if pipes[0][0].right < 0:
            pipes.pop(0)
            pipes.append(create_pipe())

        # Bird rect for collision detection
        bird_rect = pygame.Rect(bird_x, bird_y, bird_size, bird_size)

        # Check for collisions
        if check_collision(pipes, bird_rect):
            game_state = "game_over"
            collision_sound.play()

        # Draw elements
        draw_bird(bird_x, bird_y)
        draw_pipes(pipes)
        draw_score(score)

    elif game_state == "game_over":
        draw_game_over()
        draw_score(score)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
