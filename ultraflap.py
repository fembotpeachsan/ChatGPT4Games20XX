 
import pygame
import random
from array import array

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Set up the game window
WIDTH, HEIGHT = 400, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Define game variables
bird_x = 50
bird_y = 200
bird_radius = 20
bird_vel_y = 0
bird_flap = -10
gravity = 0.8
pipe_width = 60
pipe_gap = 150
pipe_vel_x = 3
pipe_frequency = 1500  # Milliseconds
last_pipe_time = 0
pipes = []

clock = pygame.time.Clock()
FPS = 60
score = 0
font = pygame.font.Font(None, 36)

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
    ("Flap", generate_beep_sound(440, 0.1)),  # Flap sound
    ("Point", generate_beep_sound(523.25, 0.1)),  # Point scored sound
    ("Hit", generate_beep_sound(587.33, 0.1)),  # Collision sound
]

# Game loop
running = True
while running:
    clock.tick(FPS)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_vel_y = bird_flap
                sounds[0][1].play()  # Play flap sound
    
    # Update bird position
    bird_vel_y += gravity
    bird_y += bird_vel_y
    
    # Generate pipes
    current_time = pygame.time.get_ticks()
    if current_time - last_pipe_time > pipe_frequency:
        pipe_height = random.randint(100, 400)
        pipe_top = pygame.Rect(WIDTH, 0, pipe_width, pipe_height)
        pipe_bottom = pygame.Rect(WIDTH, pipe_height + pipe_gap, pipe_width, HEIGHT - pipe_height - pipe_gap)
        pipes.append((pipe_top, pipe_bottom))
        last_pipe_time = current_time
    
    # Move pipes
    pipes = [(pipe_top.move(-pipe_vel_x, 0), pipe_bottom.move(-pipe_vel_x, 0)) for pipe_top, pipe_bottom in pipes]
    
    # Remove pipes off-screen
    pipes = [pipe for pipe in pipes if pipe[0].right > 0]
    
    # Check for collision
    for pipe_top, pipe_bottom in pipes:
        if (
            bird_y - bird_radius < 0
            or bird_y + bird_radius > HEIGHT
            or pipe_top.collidepoint(bird_x, bird_y)
            or pipe_bottom.collidepoint(bird_x, bird_y)
        ):
            running = False
            sounds[2][1].play()  # Play collision sound
    
    # Update score
    for pipe_top, pipe_bottom in pipes:
        if pipe_top.right < bird_x and not pipe_top.right + pipe_vel_x < bird_x:
            score += 1
            pipe_frequency = max(1200, pipe_frequency - 50)  # Increase difficulty
            sounds[1][1].play()  # Play point scored sound
    
    # Draw game objects
    WIN.fill(BLACK)
    pygame.draw.circle(WIN, WHITE, (bird_x, bird_y), bird_radius)
    for pipe_top, pipe_bottom in pipes:
        pygame.draw.rect(WIN, GREEN, pipe_top)
        pygame.draw.rect(WIN, GREEN, pipe_bottom)
    score_text = font.render("Score: " + str(score), True, WHITE)
    WIN.blit(score_text, (10, 10))
    pygame.display.update()

# Game over screen
WIN.fill(BLACK)
game_over_text = font.render("Game Over!", True, RED)
score_text = font.render("Final Score: " + str(score), True, WHITE)
WIN.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
WIN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + game_over_text.get_height() // 2))
pygame.display.update()

# Wait for a while before quitting
pygame.time.wait(3000)
pygame.quit() 
