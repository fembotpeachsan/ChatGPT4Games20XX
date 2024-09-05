import pygame
import numpy as np
import random

# Initialize Pygame and the mixer for sound
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gemtoray Dash")

# Colors
BACKGROUND_COLOR = (24, 24, 24)
PLAYER_COLOR = (0, 255, 255)  # Cyan
OBSTACLE_COLOR = (255, 0, 0)  # Red
TEXT_COLOR = (255, 255, 255)  # White

# Player properties
player_x = 100
player_y = SCREEN_HEIGHT // 2
player_size = 20
player_velocity = 0
gravity = 0.5
jump_strength = -8

# Obstacle properties
obstacle_width = 30
obstacle_speed = 6
obstacle_frequency = 1500  # Milliseconds between obstacles
obstacles = []
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, obstacle_frequency)

# Font setup
font = pygame.font.Font(None, 36)

# Sound generation
def generate_wave(frequency, duration, wave_type='sine'):
    sample_rate = 44100
    samples = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    if wave_type == 'sine':
        wave = np.sin(2 * np.pi * frequency * samples)
    elif wave_type == 'square':
        wave = np.sign(np.sin(2 * np.pi * frequency * samples))
    elif wave_type == 'triangle':
        wave = 2 * np.arcsin(np.sin(2 * np.pi * frequency * samples)) / np.pi
    elif wave_type == 'noise':
        wave = np.random.uniform(-1, 1, len(samples))

    # Normalize to 16-bit PCM format
    return (wave * 32767).astype(np.int16)

def create_synthwave_music():
    # Define a basic synthwave melody
    melody = [
        (261, 0.4), (293, 0.4), (329, 0.4), (293, 0.4),
        (349, 0.4), (329, 0.4), (293, 0.4), (261, 0.4),
        (293, 0.4), (329, 0.4), (293, 0.4), (349, 0.4),
        (329, 0.4), (293, 0.4), (261, 0.4)
    ]

    # Generate melody waves
    melody_wave = np.concatenate([
        generate_wave(frequency, duration, 'sine')  # Using sine wave for a more retro sound
        for frequency, duration in melody
    ])

    # Add some chord progressions to simulate synthwave style
    chords = [
        (261, 293, 329), (293, 329, 349), (329, 349, 393), (349, 393, 440)
    ]
    chord_duration = 0.8
    chord_wave = np.concatenate([
        np.sum([generate_wave(freq, chord_duration, 'square') for freq in chord], axis=0)
        for chord in chords
    ])

    # Combine melody and chord progression
    full_music_wave = np.concatenate([melody_wave, chord_wave])

    return pygame.mixer.Sound(buffer=full_music_wave.tobytes())

# Create sounds for the game
jump_sound = generate_wave(440, 0.2, 'sine')
jump_sound = pygame.mixer.Sound(buffer=jump_sound.tobytes())  # Create Sound object
hit_sound = generate_wave(300, 0.2, 'square')
hit_sound = pygame.mixer.Sound(buffer=hit_sound.tobytes())  # Create Sound object

# Create synthwave background music
background_music = create_synthwave_music()
background_music_playing = True
background_music.play(-1)  # Play the music in a loop

# Game Engine Class
class GemtorayDashEngine:
    def __init__(self):
        self.player_x = 100
        self.player_y = SCREEN_HEIGHT // 2
        self.player_size = 20
        self.player_velocity = 0
        self.gravity = 0.5
        self.jump_strength = -8
        self.obstacle_width = 30
        self.obstacle_speed = 6
        self.obstacles = []
        self.score = 0
        self.clock = pygame.time.Clock()
        self.running = True
    
    def handle_events(self):
        global background_music_playing
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player_velocity = self.jump_strength
                    jump_sound.play()
                elif event.key == pygame.K_m:  # Toggle music on/off
                    if background_music_playing:
                        background_music.stop()
                    else:
                        background_music.play(-1)
                    background_music_playing = not background_music_playing
                elif event.key == pygame.K_p:  # Start the game
                    self.start_game()
                elif event.key == pygame.K_e:  # Exit the game
                    self.running = False
            if event.type == obstacle_timer:
                obstacle_height = random.randint(100, 400)
                self.obstacles.append(pygame.Rect(SCREEN_WIDTH, SCREEN_HEIGHT - obstacle_height, self.obstacle_width, obstacle_height))
    
    def update_player(self):
        self.player_velocity += self.gravity
        self.player_y += self.player_velocity
        self.player_rect = pygame.Rect(self.player_x, self.player_y, self.player_size, self.player_size)
    
    def update_obstacles(self):
        for obstacle in list(self.obstacles):
            obstacle.x -= self.obstacle_speed
            if obstacle.x + self.obstacle_width < 0:
                self.obstacles.remove(obstacle)
                self.score += 1
            if self.player_rect.colliderect(obstacle):
                hit_sound.play()
                self.running = False
    
    def draw(self):
        screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(screen, PLAYER_COLOR, self.player_rect)
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, obstacle)
        score_text = font.render(f"Score: {self.score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))
        pygame.display.flip()

    def start_game(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.update_player()
            self.update_obstacles()
            self.draw()
            self.clock.tick(60)

# Display Menu
def display_menu():
    font = pygame.font.Font(None, 48)
    menu_options = ["Press P to Play", "Press M to Toggle Music", "Press E to Exit"]
    
    while True:
        screen.fill(BACKGROUND_COLOR)
        y_offset = 50
        for option in menu_options:
            text_surface = font.render(option, True, TEXT_COLOR)
            screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, y_offset))
            y_offset += 60
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return
                elif event.key == pygame.K_e:
                    pygame.quit()
                    exit()

# Start the menu and game
if __name__ == "__main__":
    display_menu()
    engine = GemtorayDashEngine()
    engine.start_game()
    pygame.quit()
