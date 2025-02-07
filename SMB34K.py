import pygame
import numpy as np

# --- Constants ---
WIDTH, HEIGHT = 800, 600
GROUND_LEVEL = 550
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# --- Player Class ---
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.y_velocity = 0
        self.x_velocity = 0  # Add x_velocity for horizontal movement
        self.jump_strength = -20
        self.gravity = 1
        self.is_jumping = False
        self.speed = 5 # Movement speed
        self.color = BLUE
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def update(self):
        # --- Horizontal Movement ---
        keys = pygame.key.get_pressed()
        self.x_velocity = 0  # Reset velocity each frame
        if keys[pygame.K_a]:
            self.x_velocity = -self.speed
        if keys[pygame.K_d]:
            self.x_velocity = self.speed

        self.x += self.x_velocity

        # Keep player within screen bounds (horizontal)
        self.x = max(0, min(self.x, WIDTH - self.width))

        # --- Vertical Movement (Gravity and Jumping) ---
        self.y_velocity += self.gravity
        self.y += self.y_velocity

        # Ground collision
        if self.y + self.height > GROUND_LEVEL:
            self.y = GROUND_LEVEL - self.height
            self.y_velocity = 0
            self.is_jumping = False

        self.rect.topleft = (self.x, self.y)

    def jump(self, jump_sound):
        if not self.is_jumping:
            self.y_velocity = self.jump_strength
            self.is_jumping = True
            jump_sound.play()

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


# --- Enemy Class ---
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.x_speed = 2
        self.color = RED
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def update(self):
        self.x += self.x_speed
        if self.x < 0 or self.x + self.width > WIDTH:
            self.x_speed *= -1

        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

# --- Sound Generation ---
def generate_sine_wave(frequency, duration, volume=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = volume * np.sin(2 * np.pi * frequency * t)
    return (wave * 32767).astype(np.int16)

# --- Initialize Pygame ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario Bros. 3 (Simplified)")
clock = pygame.time.Clock()

# --- Pre-generate Sounds ---
jump_sound = pygame.mixer.Sound(generate_sine_wave(440, 0.1))
collision_sound = pygame.mixer.Sound(generate_sine_wave(220, 0.3))

# --- Game Objects ---
player = Player(50, GROUND_LEVEL - 40)
enemy = Enemy(200, GROUND_LEVEL - 30)
ground_rect = pygame.Rect(0, GROUND_LEVEL, WIDTH, HEIGHT - GROUND_LEVEL)

# --- Game Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # --- Key Presses (Jump only on keydown) ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w: # Use 'w' for jump
                player.jump(jump_sound)

    # --- Updates ---
    player.update() # Player update now handles horizontal movement
    enemy.update()

    # --- Collision Detection ---
    if player.rect.colliderect(enemy.rect):
        print("Collision! Game Over.")
        collision_sound.play()
        running = False

    # --- Drawing ---
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, ground_rect)
    player.draw(screen)
    enemy.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
