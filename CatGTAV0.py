import pygame
import sys
import numpy as np  # Required for sound generation

# Constants for screen, world, and minimap dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WORLD_WIDTH, WORLD_HEIGHT = 1600, 1200
MINIMAP_WIDTH, MINIMAP_HEIGHT = 200, 150

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, size, color, speed):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed

    def update(self, keys):
        # Basic movement with WASD keys
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed

        # Keep the player within world boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WORLD_WIDTH:
            self.rect.right = WORLD_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > WORLD_HEIGHT:
            self.rect.bottom = WORLD_HEIGHT

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos, size, color=(0, 128, 0)):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)

class Camera:
    def __init__(self, world_width, world_height, screen_width, screen_height):
        self.world_width = world_width
        self.world_height = world_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Start with a camera covering the whole world (will be updated)
        self.camera = pygame.Rect(0, 0, world_width, world_height)
        # Smoothing factor (0.0: no movement, 1.0: instant snapping)
        self.smoothing = 0.1

    def apply(self, entity):
        # Adjust sprite positions based on camera offset
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        # Desired camera position to center on the target (player)
        desired_x = -target.rect.centerx + self.screen_width // 2
        desired_y = -target.rect.centery + self.screen_height // 2

        # Clamp desired values to the world bounds
        desired_x = min(0, desired_x)
        desired_y = min(0, desired_y)
        desired_x = max(-(self.world_width - self.screen_width), desired_x)
        desired_y = max(-(self.world_height - self.screen_height), desired_y)

        # Smoothly interpolate the camera's current position toward the desired position
        new_x = self.camera.x + (desired_x - self.camera.x) * self.smoothing
        new_y = self.camera.y + (desired_y - self.camera.y) * self.smoothing
        self.camera = pygame.Rect(new_x, new_y, self.world_width, self.world_height)

class SoundEngine:
    """
    FLAMES's GTA Sound Engine:
    A simple sound engine that generates tones on the fly using NumPy.
    No external mp3 or wav files are needed.
    """
    def __init__(self):
        # Initialize the mixer with desired settings
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.sounds = {}

    def generate_tone(self, frequency, duration, volume=1.0):
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        # Generate a sine wave tone
        tone = np.sin(frequency * 2 * np.pi * t) * 32767
        tone = tone.astype(np.int16)
        # Create stereo by duplicating the mono tone
        stereo_tone = np.column_stack((tone, tone))
        sound = pygame.sndarray.make_sound(stereo_tone)
        sound.set_volume(volume)
        return sound

    def load_sound(self, name, frequency, duration, volume=1.0):
        self.sounds[name] = self.generate_tone(frequency, duration, volume)

    def play(self, name, loops=0):
        if name in self.sounds:
            self.sounds[name].play(loops=loops)

    def play_melody(self, notes):
        """
        Play a sequence of notes.
        'notes' should be a list of tuples in the form: (frequency, duration, volume)
        """
        sample_rate = 44100
        melody = np.array([], dtype=np.int16)
        for freq, duration, vol in notes:
            t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
            # Generate tone with volume scaling
            tone = np.sin(freq * 2 * np.pi * t) * (32767 * vol)
            tone = tone.astype(np.int16)
            melody = np.concatenate((melody, tone))
        # Convert to stereo by duplicating the mono channel
        stereo_melody = np.column_stack((melody, melody))
        sound = pygame.sndarray.make_sound(stereo_melody)
        sound.play()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Enhanced GTA 5 in Pygame - FLAMES's GTA")
        self.clock = pygame.time.Clock()

        # Sprite groups for managing game objects
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()

        # Create the player at the center of the world
        self.player = Player(pos=(WORLD_WIDTH // 2, WORLD_HEIGHT // 2), size=40, color=(255, 0, 0), speed=5)
        self.all_sprites.add(self.player)

        # Create obstacles (representing buildings or other structures)
        obs1 = Obstacle(pos=(300, 300), size=(200, 100))
        obs2 = Obstacle(pos=(1000, 800), size=(150, 150))
        self.obstacles.add(obs1, obs2)
        self.all_sprites.add(obs1, obs2)

        # Initialize the camera for scrolling the world
        self.camera = Camera(WORLD_WIDTH, WORLD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Set up a font for the debug overlay
        self.font = pygame.font.SysFont("Arial", 18)

        # Initialize our custom sound engine (FLAMES's GTA Sound Engine)
        self.sound_engine = SoundEngine()
        # Load a low-volume looping background ambience tone (e.g., 440 Hz)
        self.sound_engine.load_sound("background", frequency=440, duration=2, volume=0.2)
        # Load a short collision sound (e.g., 100 Hz for a thump)
        self.sound_engine.load_sound("collision", frequency=100, duration=0.2, volume=0.5)
        # Play the GTAS theme (a custom melody in beeps and boops) on load
        theme_notes = [
            (523, 0.3, 1.0),  # C5
            (587, 0.3, 1.0),  # D5
            (659, 0.3, 1.0),  # E5
            (698, 0.3, 1.0),  # F5
            (784, 0.3, 1.0),  # G5
            (698, 0.3, 1.0),  # F5
            (659, 0.3, 1.0),  # E5
            (587, 0.3, 1.0),  # D5
            (523, 0.3, 1.0)   # C5
        ]
        self.sound_engine.play_melody(theme_notes)
        # Start playing the background sound on loop
        self.sound_engine.play("background", loops=-1)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

    def handle_events(self):
        # Handle quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def update(self):
        keys = pygame.key.get_pressed()
        # Save player's current position for collision resolution
        old_rect = self.player.rect.copy()
        self.player.update(keys)

        # Check for collision with obstacles
        if pygame.sprite.spritecollideany(self.player, self.obstacles):
            self.player.rect = old_rect
            # Play collision sound on impact
            self.sound_engine.play("collision")

        # Update the camera to center smoothly on the player
        self.camera.update(self.player)

    def draw_debug_info(self):
        # Render debug info: FPS and player's coordinates
        fps = int(self.clock.get_fps())
        debug_text = f"FPS: {fps}  Player: ({self.player.rect.x}, {self.player.rect.y})"
        debug_surface = self.font.render(debug_text, True, (255, 255, 255))
        self.screen.blit(debug_surface, (10, 10))

    def draw_minimap(self):
        # Create a minimap surface to represent the world overview
        minimap_surface = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT))
        minimap_surface.fill((20, 20, 20))
        # Calculate scaling factors to convert world coordinates to minimap coordinates
        scale_x = MINIMAP_WIDTH / WORLD_WIDTH
        scale_y = MINIMAP_HEIGHT / WORLD_HEIGHT

        # Draw obstacles on the minimap
        for obstacle in self.obstacles:
            scaled_rect = pygame.Rect(
                obstacle.rect.x * scale_x,
                obstacle.rect.y * scale_y,
                obstacle.rect.width * scale_x,
                obstacle.rect.height * scale_y
            )
            pygame.draw.rect(minimap_surface, (0, 128, 0), scaled_rect)

        # Draw the player on the minimap
        scaled_player_rect = pygame.Rect(
            self.player.rect.x * scale_x,
            self.player.rect.y * scale_y,
            self.player.rect.width * scale_x,
            self.player.rect.height * scale_y
        )
        pygame.draw.rect(minimap_surface, (255, 0, 0), scaled_player_rect)

        # Draw the camera viewport on the minimap
        scaled_camera = pygame.Rect(
            -self.camera.camera.x * scale_x,
            -self.camera.camera.y * scale_y,
            SCREEN_WIDTH * scale_x,
            SCREEN_HEIGHT * scale_y
        )
        pygame.draw.rect(minimap_surface, (255, 255, 0), scaled_camera, 1)

        # Draw a border around the minimap
        pygame.draw.rect(minimap_surface, (255, 255, 255), minimap_surface.get_rect(), 2)
        # Position the minimap in the top-right corner with a 10-pixel margin
        self.screen.blit(minimap_surface, (SCREEN_WIDTH - MINIMAP_WIDTH - 10, 10))

    def draw(self):
        # Fill the background to represent the game world
        self.screen.fill((50, 50, 50))

        # Draw all sprites adjusted by the camera's offset
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        # Draw the debug overlay and minimap
        self.draw_debug_info()
        self.draw_minimap()

        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
