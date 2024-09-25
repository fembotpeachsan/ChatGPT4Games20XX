import pygame
import numpy as np
import sys
import random

# Initialize pygame
pygame.init()

# Set up the screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
CLOCK = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Load the font
FONT = pygame.font.SysFont('Arial', 32)
SMALL_FONT = pygame.font.SysFont('Arial', 24)

# Bird settings
BIRD_SIZE = 30
BIRD_X = SCREEN_WIDTH // 4
BIRD_Y = SCREEN_HEIGHT // 2
GRAVITY = 0.5
FLAP_STRENGTH = -10

# Pipe settings
PIPE_WIDTH = 70
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds

# NumPy based SFX generator with stereo sound
def generate_sound(frequency=440, duration=0.2, volume=0.5, sample_rate=44100):
    samples = np.arange(int(duration * sample_rate))
    wave = np.sin(2 * np.pi * frequency * samples / sample_rate)
    wave = volume * wave

    # Convert the wave to a 2D array for stereo sound (duplicate mono signal to both channels)
    stereo_wave = np.column_stack((wave, wave))
    stereo_wave = np.int16(stereo_wave * 32767)
    
    sound = pygame.sndarray.make_sound(stereo_wave)
    return sound

# SFX
flap_sfx = generate_sound(frequency=880)
score_sfx = generate_sound(frequency=660)
hit_sfx = generate_sound(frequency=220)

# Bird class
class Bird:
    def __init__(self):
        self.y = BIRD_Y
        self.velocity = 0

    def flap(self):
        self.velocity = FLAP_STRENGTH
        flap_sfx.play()

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        if self.y < 0:
            self.y = 0
        if self.y > SCREEN_HEIGHT - BIRD_SIZE:
            self.y = SCREEN_HEIGHT - BIRD_SIZE

    def draw(self):
        pygame.draw.rect(SCREEN, BLUE, (BIRD_X, self.y, BIRD_SIZE, BIRD_SIZE))

# Pipe class
class Pipe:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)

    def update(self):
        self.x -= 5

    def draw(self):
        pygame.draw.rect(SCREEN, GREEN, (self.x, 0, PIPE_WIDTH, self.height))
        pygame.draw.rect(SCREEN, GREEN, (self.x, self.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - self.height - PIPE_GAP))

    def off_screen(self):
        return self.x < -PIPE_WIDTH

    def collide(self, bird):
        if BIRD_X + BIRD_SIZE > self.x and BIRD_X < self.x + PIPE_WIDTH:
            if bird.y < self.height or bird.y + BIRD_SIZE > self.height + PIPE_GAP:
                return True
        return False

# Game functions
def main_game():
    bird = Bird()
    pipes = []
    score = 0
    last_pipe = pygame.time.get_ticks()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird.flap()

        # Add new pipes
        if pygame.time.get_ticks() - last_pipe > PIPE_FREQUENCY:
            pipes.append(Pipe())
            last_pipe = pygame.time.get_ticks()

        # Update bird
        bird.update()

        # Update pipes
        for pipe in pipes:
            pipe.update()

        # Check for collisions
        for pipe in pipes:
            if pipe.collide(bird):
                hit_sfx.play()
                return score

        # Remove off-screen pipes and increase score
        pipes = [pipe for pipe in pipes if not pipe.off_screen()]
        if len(pipes) > 0 and pipes[0].x + PIPE_WIDTH < BIRD_X:
            pipes.pop(0)
            score += 1
            score_sfx.play()

        # Drawing everything
        SCREEN.fill(WHITE)
        bird.draw()
        for pipe in pipes:
            pipe.draw()

        # Draw score
        score_text = FONT.render(f"Score: {score}", True, BLACK)
        SCREEN.blit(score_text, (10, 10))

        # Refresh screen
        pygame.display.flip()
        CLOCK.tick(60)

def main_menu():
    while True:
        SCREEN.fill(WHITE)
        title_text = FONT.render("Flappy Bird", True, BLACK)
        start_text = SMALL_FONT.render("Press SPACE to Start", True, BLACK)
        credits_text = SMALL_FONT.render("Press C for Credits", True, BLACK)

        SCREEN.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
        SCREEN.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 300))
        SCREEN.blit(credits_text, (SCREEN_WIDTH // 2 - credits_text.get_width() // 2, 350))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "game"
                if event.key == pygame.K_c:
                    return "credits"

def game_over(score):
    while True:
        SCREEN.fill(WHITE)
        game_over_text = FONT.render("Game Over", True, BLACK)
        score_text = SMALL_FONT.render(f"Score: {score}", True, BLACK)
        restart_text = SMALL_FONT.render("Press SPACE to Restart", True, BLACK)
        menu_text = SMALL_FONT.render("Press M for Main Menu", True, BLACK)

        SCREEN.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 150))
        SCREEN.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))
        SCREEN.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 350))
        SCREEN.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, 400))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "game"
                if event.key == pygame.K_m:
                    return "menu"

def credits_screen():
    while True:
        SCREEN.fill(WHITE)
        credits_text = FONT.render("Credits", True, BLACK)
        author_text = SMALL_FONT.render("Developer: @catdevzsh", True, BLACK)
        back_text = SMALL_FONT.render("Press M for Main Menu", True, BLACK)

        SCREEN.blit(credits_text, (SCREEN_WIDTH // 2 - credits_text.get_width() // 2, 150))
        SCREEN.blit(author_text, (SCREEN_WIDTH // 2 - author_text.get_width() // 2, 250))
        SCREEN.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 350))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    return "menu"

# Main game loop with state management
if __name__ == "__main__":
    state = "menu"
    while True:
        if state == "menu":
            state = main_menu()
        elif state == "game":
            score = main_game()
            state = game_over(score)
        elif state == "game_over":
            state = game_over(score)
        elif state == "credits":
            state = credits_screen()
