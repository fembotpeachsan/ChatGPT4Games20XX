import pygame
import sys
import random
from array import array

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Game settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60
GRAVITY = 1
JUMP_STRENGTH = -15
DASH_STRENGTH = 20
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
GROUND_HEIGHT = SCREEN_HEIGHT - 50
OBSTACLE_WIDTH = 30
OBSTACLE_HEIGHT = 60
SCROLL_SPEED = 5

# Function to generate beep sounds with varying frequencies
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

# Player class
class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, GROUND_HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.velocity_y = 0
        self.on_ground = True
        self.has_double_jump = True
        self.is_dashing = False
        self.gravity_flipped = False

    def update(self):
        # Apply gravity
        if not self.gravity_flipped:
            self.velocity_y += GRAVITY
        else:
            self.velocity_y -= GRAVITY

        # Move player
        self.rect.y += self.velocity_y

        # Prevent falling through the ground
        if not self.gravity_flipped and self.rect.bottom > GROUND_HEIGHT:
            self.rect.bottom = GROUND_HEIGHT
            self.velocity_y = 0
            self.on_ground = True
            self.has_double_jump = True
        elif self.gravity_flipped and self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0
            self.on_ground = True
            self.has_double_jump = True

    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_STRENGTH if not self.gravity_flipped else -JUMP_STRENGTH
            self.on_ground = False
            sounds[0][1].play()
        elif self.has_double_jump:
            self.velocity_y = JUMP_STRENGTH if not self.gravity_flipped else -JUMP_STRENGTH
            self.has_double_jump = False
            sounds[0][1].play()

    def dash(self):
        if not self.is_dashing:
            self.is_dashing = True
            self.velocity_y += DASH_STRENGTH if not self.gravity_flipped else -DASH_STRENGTH
            sounds[1][1].play()

    def flip_gravity(self):
        self.gravity_flipped = not self.gravity_flipped
        self.velocity_y = -self.velocity_y  # Reverse the direction of gravity
        self.on_ground = False  # Allow the player to float up or down after flipping gravity
        sounds[2][1].play()

# Obstacle class
class Obstacle:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH, GROUND_HEIGHT - OBSTACLE_HEIGHT, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)

    def update(self):
        self.rect.x -= SCROLL_SPEED

# Function to display the main menu
def main_menu():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Geometry Dash 2.2 Clone")
    font = pygame.font.Font(None, 74)
    clock = pygame.time.Clock()

    while True:
        screen.fill((0, 0, 0))
        title_text = font.render("Main Menu", True, (255, 255, 255))
        start_text = font.render("Press ENTER to Start", True, (255, 255, 255))
        quit_text = font.render("Press ESC to Quit", True, (255, 255, 255))

        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Press Enter to start the game
                    return
                if event.key == pygame.K_ESCAPE:  # Press Esc to quit
                    pygame.quit()
                    sys.exit()

        clock.tick(15)

# Main game loop
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Geometry Dash 2.2 Clone")
    clock = pygame.time.Clock()

    player = Player()
    obstacles = []
    spawn_timer = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_LSHIFT:
                    player.dash()
                if event.key == pygame.K_g:
                    player.flip_gravity()

        # Update player
        player.update()

        # Spawn obstacles
        spawn_timer += 1
        if spawn_timer > 60:  # spawn an obstacle every second
            spawn_timer = 0
            obstacles.append(Obstacle())

        # Update obstacles
        for obstacle in obstacles:
            obstacle.update()
            if obstacle.rect.right < 0:
                obstacles.remove(obstacle)

            # Check for collisions
            if player.rect.colliderect(obstacle.rect):
                sounds[1][1].play()  # Play collision sound
                pygame.time.delay(1000)  # Delay to allow sound to play
                pygame.quit()
                sys.exit()

        # Draw everything
        screen.fill((0, 0, 0))  # Clear screen with black
        pygame.draw.rect(screen, (255, 0, 0), player.rect)  # Draw player
        for obstacle in obstacles:
            pygame.draw.rect(screen, (0, 255, 0), obstacle.rect)  # Draw obstacles

        pygame.display.flip()  # Update the display
        clock.tick(FPS)  # Control the frame rate

if __name__ == "__main__":
    main_menu()  # Start with the main menu
    main()  # Start the game after the menu
import pygame
import sys
import random

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Game settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60
GRAVITY = 1
JUMP_STRENGTH = -15
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
GROUND_HEIGHT = SCREEN_HEIGHT - 50
SCROLL_SPEED = 8

# Load music and sound effects
pygame.mixer.music.load("background_music.mp3")  # Replace with your music file
pygame.mixer.music.set_volume(0.5)
jump_sound = pygame.mixer.Sound("jump.wav")  # Replace with your sound file
dash_sound = pygame.mixer.Sound("dash.wav")  # Replace with your sound file
flip_sound = pygame.mixer.Sound("flip.wav")  # Replace with your sound file
collision_sound = pygame.mixer.Sound("collision.wav")  # Replace with your sound file

# Player class
class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, GROUND_HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.velocity_y = 0
        self.on_ground = True
        self.gravity_flipped = False
        self.is_dashing = False

    def update(self):
        # Apply gravity
        if not self.gravity_flipped:
            self.velocity_y += GRAVITY
        else:
            self.velocity_y -= GRAVITY

        # Move player
        self.rect.y += self.velocity_y

        # Prevent falling through the ground or flying off the top
        if not self.gravity_flipped and self.rect.bottom > GROUND_HEIGHT:
            self.rect.bottom = GROUND_HEIGHT
            self.velocity_y = 0
            self.on_ground = True
        elif self.gravity_flipped and self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0
            self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_STRENGTH if not self.gravity_flipped else -JUMP_STRENGTH
            self.on_ground = False
            jump_sound.play()

    def dash(self):
        if not self.is_dashing:
            self.is_dashing = True
            dash_sound.play()

    def flip_gravity(self):
        self.gravity_flipped = not self.gravity_flipped
        self.velocity_y = -self.velocity_y  # Reverse the direction of gravity
        flip_sound.play()

# Obstacle class
class Obstacle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def update(self):
        self.rect.x -= SCROLL_SPEED

# Function to display the main menu
def main_menu():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Geometry Dash 2.2 Clone")
    font = pygame.font.Font(None, 74)
    clock = pygame.time.Clock()

    while True:
        screen.fill((0, 0, 0))
        title_text = font.render("Main Menu", True, (255, 255, 255))
        start_text = font.render("Press ENTER to Start", True, (255, 255, 255))
        quit_text = font.render("Press ESC to Quit", True, (255, 255, 255))

        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Press Enter to start the game
                    return
                if event.key == pygame.K_ESCAPE:  # Press Esc to quit
                    pygame.quit()
                    sys.exit()

        clock.tick(15)

# Main game loop
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Geometry Dash 2.2 Clone")
    clock = pygame.time.Clock()

    player = Player()
    obstacles = []
    spawn_timer = 0

    # Start background music
    pygame.mixer.music.play(-1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_LSHIFT:
                    player.dash()
                if event.key == pygame.K_g:
                    player.flip_gravity()

        # Update player
        player.update()

        # Spawn obstacles
        spawn_timer += 1
        if spawn_timer > 60:  # spawn an obstacle every second
            spawn_timer = 0
            obstacle_height = random.randint(20, 100)
            obstacle_y = GROUND_HEIGHT - obstacle_height if not player.gravity_flipped else 0
            obstacles.append(Obstacle(SCREEN_WIDTH, obstacle_y, 30, obstacle_height))

        # Update obstacles
        for obstacle in obstacles:
            obstacle.update()
            if obstacle.rect.right < 0:
                obstacles.remove(obstacle)

            # Check for collisions
            if player.rect.colliderect(obstacle.rect):
                collision_sound.play()  # Play collision sound
                pygame.time.delay(1000)  # Delay to allow sound to play
                pygame.quit()
                sys.exit()

        # Draw everything
        screen.fill((0, 0, 0))  # Clear screen with black
        pygame.draw.rect(screen, (255, 0, 0), player.rect)  # Draw player
        for obstacle in obstacles:
            pygame.draw.rect(screen, (0, 255, 0), obstacle.rect)  # Draw obstacles

        pygame.display.flip()  # Update the display
        clock.tick(FPS)  # Control the frame rate

if __name__ == "__main__":
    main_menu()  # Start with the main menu
    main()  # Start the game after the menu
