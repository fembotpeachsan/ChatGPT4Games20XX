import pygame
import sys
import math
import numpy as np

# Init Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
MAX_FALL_SPEED = 10
SKY_BLUE = (135, 206, 235)
GROUND_BROWN = (139, 69, 19)
YOSHI_GREEN = (0, 255, 0)
YOSHI_RED = (255, 0, 0)
YOSHI_WHITE = (255, 255, 255)
ENEMY_RED = (255, 0, 0)
EGG_YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Generate sounds in-code (simple sine waves, now stereo)
def generate_sound(freq, duration, volume=0.5):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [math.sin(2 * math.pi * freq * x / sample_rate) for x in range(samples)]
    mono = np.array([int(x * max_amplitude * volume) for x in wave], dtype=np.int16)
    stereo = np.column_stack([mono, mono])  # Duplicate for stereo
    return pygame.sndarray.make_sound(stereo)

jump_sound = generate_sound(440, 0.1)  # A4 note for jump
collect_sound = generate_sound(880, 0.1)  # Higher for collect

# Yoshi Player Class
class Yoshi:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 50
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = -15
        self.on_ground = False
        self.facing_right = True

    def update(self, keys, platforms):
        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
            self.facing_right = True

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
            jump_sound.play()

        # Gravity
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

        # Collisions with platforms
        self.on_ground = False
        for plat in platforms:
            if (self.x + self.width > plat.x and self.x < plat.x + plat.width and
                self.y + self.height > plat.y and self.y + self.height - self.vel_y <= plat.y):
                self.y = plat.y - self.height
                self.vel_y = 0
                self.on_ground = True

        # Screen bounds
        if self.x < 0:
            self.x = 0
        if self.x > level_width - self.width:
            self.x = level_width - self.width
        if self.y > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.height  # Respawn or something, simple

    def draw(self, screen, camera_x):
        # Draw Yoshi body (simple shapes)
        body_x = self.x - camera_x
        # Body
        pygame.draw.ellipse(screen, YOSHI_GREEN, (body_x + 5, self.y + 10, 30, 30))
        # Head
        pygame.draw.circle(screen, YOSHI_GREEN, (body_x + 20, self.y + 5), 15)
        # Eyes
        eye_offset = 5 if self.facing_right else -5
        pygame.draw.circle(screen, YOSHI_WHITE, (body_x + 20 + eye_offset, self.y), 5)
        pygame.draw.circle(screen, BLACK, (body_x + 20 + eye_offset, self.y), 2)
        # Shoes
        pygame.draw.ellipse(screen, YOSHI_RED, (body_x, self.y + 35, 15, 10))
        pygame.draw.ellipse(screen, YOSHI_RED, (body_x + 25, self.y + 35, 15, 10))

# Enemy Class (Shy Guy like)
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.vel_x = -2
        self.alive = True

    def update(self, platforms):
        self.x += self.vel_x
        # Simple patrol reverse on edge (NES style)
        on_platform = False
        for plat in platforms:
            if (self.x + self.width > plat.x and self.x < plat.x + plat.width and
                self.y + self.height == plat.y):
                on_platform = True
                if self.x < plat.x or self.x + self.width > plat.x + plat.width:
                    self.vel_x = -self.vel_x
        if not on_platform:
            self.y += GRAVITY  # Fall if no ground

    def draw(self, screen, camera_x):
        pygame.draw.rect(screen, ENEMY_RED, (self.x - camera_x, self.y, self.width, self.height))

# Egg Collectible
class Egg:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 30
        self.collected = False
        self.rotation = 0

    def update(self):
        self.rotation += 0.1

    def draw(self, screen, camera_x):
        scale = abs(math.sin(self.rotation)) * 5 + 15
        pygame.draw.ellipse(screen, EGG_YELLOW, (self.x - camera_x, self.y, self.width, scale))

# Platform Class
class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen, camera_x):
        pygame.draw.rect(screen, GROUND_BROWN, (self.x - camera_x, self.y, self.width, self.height))

# Simple level setup
level_width = 2000
platforms = [
    Platform(0, SCREEN_HEIGHT - 50, level_width, 50),  # Ground
    Platform(200, 400, 200, 20),
    Platform(500, 300, 150, 20),
    Platform(800, 200, 100, 20),
    Platform(1100, 400, 200, 20),
    Platform(1400, 300, 150, 20),
    Platform(1700, 200, 100, 20),
]
enemies = [
    Enemy(300, 350),
    Enemy(600, 250),
    Enemy(900, 150),
    Enemy(1200, 350),
]
eggs = [
    Egg(250, 350),
    Egg(550, 250),
    Egg(850, 150),
    Egg(1150, 350),
    Egg(1450, 250),
]

# Main game
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Yoshi's Island NES Vibes - Pygame Edition")
    clock = pygame.time.Clock()

    yoshi = Yoshi(100, SCREEN_HEIGHT - 100)
    camera_x = 0
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Updates
        yoshi.update(keys, platforms)
        for enemy in enemies:
            enemy.update(platforms)
        for egg in eggs:
            egg.update()

        # Collisions: Eggs
        yoshi_rect = pygame.Rect(yoshi.x, yoshi.y, yoshi.width, yoshi.height)
        for egg in eggs[:]:
            if not egg.collected and yoshi_rect.colliderect(pygame.Rect(egg.x, egg.y, egg.width, egg.height)):
                egg.collected = True
                score += 1
                collect_sound.play()
                eggs.remove(egg)

        # Collisions: Enemies (simple stomp or die)
        for enemy in enemies[:]:
            if yoshi_rect.colliderect(pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)):
                if yoshi.vel_y > 0 and yoshi.y + yoshi.height < enemy.y + 10:  # Stomp
                    enemy.alive = False
                    enemies.remove(enemy)
                    yoshi.vel_y = -10  # Bounce
                else:
                    # Die/restart simple
                    yoshi.x = 100
                    yoshi.y = SCREEN_HEIGHT - 100
                    yoshi.vel_y = 0

        # Camera follow
        camera_x = max(0, min(yoshi.x - SCREEN_WIDTH // 2, level_width - SCREEN_WIDTH))

        # Draw
        screen.fill(SKY_BLUE)
        # Draw platforms
        for plat in platforms:
            plat.draw(screen, camera_x)
        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen, camera_x)
        # Draw eggs
        for egg in eggs:
            egg.draw(screen, camera_x)
        # Draw Yoshi
        yoshi.draw(screen, camera_x)

        # UI: Score
        font = pygame.font.SysFont(None, 36)
        text = font.render(f"Eggs: {score}", True, BLACK)
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
