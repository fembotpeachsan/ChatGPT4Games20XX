import pygame
import random
import math
import sys
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders on Steroids")

# Clock for controlling the frame rate
clock = pygame.time.Clock()
FPS = 60

# --- GAME PARAMETERS ---
DAY_LENGTH = 10_000   # How many frames in a full day-night cycle
COOLDOWN_TIME = 500   # Milliseconds between shots

# We can degrade the resolution for that "PS1" vibe. We'll render to a smaller surface, then scale up.
RENDER_SCALE = 0.5  # Adjust for pixelation effect
RENDER_WIDTH = int(SCREEN_WIDTH * RENDER_SCALE)
RENDER_HEIGHT = int(SCREEN_HEIGHT * RENDER_SCALE)
render_surface = pygame.Surface((RENDER_WIDTH, RENDER_HEIGHT))

# --- SOUND ENGINE ---
class SoundEngine:
    def __init__(self):
        self.sounds = {}
        self.generate_sounds()

    def generate_sounds(self):
        # Generate a beep for shooting
        self.sounds['shoot'] = self.create_beep(frequency=440, duration=100)  # A4 note
        # Generate a beep for enemy hit
        self.sounds['hit'] = self.create_beep(frequency=220, duration=100)    # A3 note

    def create_beep(self, frequency=440, duration=100, volume=0.5):
        """Generates a beep sound of a given frequency (Hz) and duration (ms)."""
        sample_rate = 44100
        n_samples = int(round(duration * sample_rate / 1000))
        buf = np.zeros((n_samples, 2), dtype=np.int16)
        max_sample = 2**15 - 1
        for s in range(n_samples):
            t = float(s) / sample_rate  # Time in seconds
            val = max_sample * volume * math.sin(2 * math.pi * frequency * t)
            buf[s][0] = int(val)  # Left channel
            buf[s][1] = int(val)  # Right channel
        sound = pygame.sndarray.make_sound(buf)
        return sound

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

# Initialize Sound Engine
sound_engine = SoundEngine()

# --- GRAPHICS ENGINE ---
class GraphicsEngine:
    def __init__(self, surface):
        self.surface = surface
        self.day_time = 0  # For day-night cycle

    def draw_lighting(self):
        # day_time goes from 0 to DAY_LENGTH in a loop
        self.day_time = (self.day_time + 1) % DAY_LENGTH

        # Convert day_time into a 0->2π range for sine
        cycle_pos = (self.day_time / DAY_LENGTH) * 2 * math.pi
        # Value from 0 (dark) to 1 (bright)
        light_factor = (math.sin(cycle_pos) + 1) / 2

        # Alpha increases as it gets darker
        max_alpha = 150
        alpha = int(max_alpha * (1 - light_factor))

        # Create a semi-transparent black surface
        shade = pygame.Surface((RENDER_WIDTH, RENDER_HEIGHT))
        shade.fill(BLACK)
        shade.set_alpha(alpha)
        self.surface.blit(shade, (0, 0))

    def draw_hud(self, player):
        # HP Bar
        hp_ratio = player.hp / player.max_hp
        pygame.draw.rect(self.surface, RED, (20, 20, 200, 20))
        pygame.draw.rect(self.surface, GREEN, (20, 20, int(200 * hp_ratio), 20))

        # Mana Bar
        mana_ratio = player.mana / player.max_mana
        pygame.draw.rect(self.surface, (0, 0, 100), (20, 50, 200, 20))
        pygame.draw.rect(self.surface, (0, 0, 255), (20, 50, int(200 * mana_ratio), 20))

        # Cooldown indicator
        now = pygame.time.get_ticks()
        time_since_shot = now - player.last_shot_time
        if time_since_shot < COOLDOWN_TIME:
            cooldown_ratio = time_since_shot / COOLDOWN_TIME
        else:
            cooldown_ratio = 1.0

        pygame.draw.rect(self.surface, (50, 50, 50), (20, 80, 200, 10))
        pygame.draw.rect(self.surface, (100, 100, 255), (20, 80, int(200 * cooldown_ratio), 10))

    def draw_minimap(self, player, enemies):
        # Define minimap area
        map_width = 150
        map_height = 100
        map_x = RENDER_WIDTH - map_width - 10
        map_y = 10

        # Draw background
        pygame.draw.rect(self.surface, GRAY, (map_x, map_y, map_width, map_height))

        # Scale positions
        scale_x = map_width / SCREEN_WIDTH
        scale_y = map_height / SCREEN_HEIGHT

        # Player is invisible on the main screen, but we can still show it on the minimap if desired:
        px = int(map_x + player.rect.centerx * scale_x)
        py = int(map_y + player.rect.centery * scale_y)
        pygame.draw.circle(self.surface, BLUE, (px, py), 3)

        # Draw enemies
        for enemy in enemies:
            ex = int(map_x + enemy.rect.centerx * scale_x)
            ey = int(map_y + enemy.rect.centery * scale_y)
            pygame.draw.circle(self.surface, RED, (ex, ey), 2)

    def render(self, all_sprites, player, enemies):
        # Clear screen
        self.surface.fill(BLACK)
        # Draw all sprites EXCEPT the player
        all_sprites.draw(self.surface)

        # Apply lighting
        self.draw_lighting()
        # Draw HUD
        self.draw_hud(player)
        # Draw Minimap
        self.draw_minimap(player, enemies)

# Initialize Graphics Engine
graphics_engine = GraphicsEngine(render_surface)

# --- PLAYER, BULLET, ENEMY CLASSES ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Even though we have an image, we won't add this sprite to all_sprites.
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10

        self.speed = 5

        # For the HUD
        self.max_hp = 100
        self.hp = 100
        self.max_mana = 50
        self.mana = 50

        # For shooting cooldown
        self.last_shot_time = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

        # Slow regen of mana
        self.mana = min(self.mana + 0.02, self.max_mana)

    def can_shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= COOLDOWN_TIME:
            self.last_shot_time = now
            return True
        return False

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -7

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2

    def update(self):
        self.rect.x += self.speed
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.speed = -self.speed
            self.rect.y += 20

# Initialize player, enemies, and sprite groups
player = Player()

all_sprites = pygame.sprite.Group()
# Notice: We do NOT do all_sprites.add(player) so the player won't be drawn!

bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

def create_enemies():
    for row in range(5):
        for col in range(10):
            enemy = Enemy(60 + col * 60, 50 + row * 40)
            all_sprites.add(enemy)
            enemies.add(enemy)

create_enemies()

# --- GAME LOOP ---
running = True
while running:
    dt = clock.tick(FPS)  # dt is time passed since last frame

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Shoot bullet if cooldown allows
                if player.can_shoot() and player.mana >= 5:
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                    player.mana -= 5  # Consume mana
                    sound_engine.play_sound('shoot')

    # Update
    player.update()       # We still update the player logic
    all_sprites.update()  # Update enemies and bullets

    # Check for bullet-enemy collisions
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    if hits:
        # If we kill an enemy, reward the player with some mana and play hit sound
        for _ in hits:
            player.mana = min(player.mana + 5, player.max_mana)
            sound_engine.play_sound('hit')

    # Check if all enemies are destroyed
    if not enemies:
        create_enemies()

    # Check for enemy-player collisions
    for enemy in enemies:
        if enemy.rect.colliderect(player.rect):
            player.hp -= 10
            enemy.kill()
            sound_engine.play_sound('hit')
            if player.hp <= 0:
                running = False

    # --- RENDER PHASE ---
    graphics_engine.render(all_sprites, player, enemies)

    # PS1-style scaling
    if RENDER_SCALE < 1:
        scaled_surface = pygame.transform.scale(render_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_surface, (0, 0))
    else:
        screen.blit(render_surface, (0, 0))

    pygame.display.flip()

# Game Over Screen (Optional)
def game_over_screen(surface):
    font = pygame.font.SysFont(None, 74)
    text = font.render('GAME OVER', True, RED)
    text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    surface.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(3000)

# Show Game Over screen
game_over_screen(screen)

pygame.quit()
sys.exit()
