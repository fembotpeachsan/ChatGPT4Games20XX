import pygame
import math
import random
import numpy as np
import asyncio
import platform

# Initialize Pygame
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 320, 240
SCALE = 2  # Scales to 640x480
screen = pygame.display.set_mode((SCREEN_WIDTH * SCALE, SCREEN_HEIGHT * SCALE))
clock = pygame.time.Clock()
FPS = 60

# Virtual screen for pixel-perfect rendering
v_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

# ========== PLAYER CLASS ==========
class Player:
    def __init__(self):
        self.x, self.y = 100, 200
        self.vel_x, self.vel_y = 0, 0
        self.on_ground = False
        self.size = 8  # Small Mario (8px)
        self.jump_cooldown = 0

    def update(self, keys):
        # Horizontal Movement
        if keys[pygame.K_LEFT]:
            self.vel_x = max(-2, self.vel_x - 0.1)
        elif keys[pygame.K_RIGHT]:
            self.vel_x = min(2, self.vel_x + 0.1)
        else:
            self.vel_x *= 0.9  # Friction

        # Jumping
        if keys[pygame.K_SPACE] and self.on_ground and self.jump_cooldown == 0:
            self.vel_y = -5
            self.on_ground = False
            self.jump_cooldown = 15  # Prevent rapid jumps
            play_sound(440, 0.1)  # Jump SFX

        # Gravity
        self.vel_y += 0.3
        self.y += self.vel_y

        # Collision with ground/platforms
        self.on_ground = self.y >= 200
        if self.on_ground:
            self.y = 200
            self.vel_y = 0

        # Update position
        self.x += self.vel_x

        # Jump cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1

    def draw(self, surface):
        color = (255, 0, 0) if self.size == 8 else (0, 0, 255)  # Red (small) or Blue (big)
        pygame.draw.rect(surface, color, (int(self.x), int(self.y), self.size, self.size))

# ========== LEVEL TILEMAP ==========
TILE_SIZE = 8
level_data = [
    [1] * 40,  # Ground row
    [0] * 40,
    [0] * 40,
    [1 if i % 10 == 0 else 0 for i in range(40)]  # Platforms
]

def draw_level(surface):
    for y, row in enumerate(level_data):
        for x, tile in enumerate(row):
            if tile == 1:
                pygame.draw.rect(surface, (0, 255, 0), (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))

# ========== ENEMIES ==========
class Enemy:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vel_x = -1
        self.width, self.height = 8, 8

    def update(self):
        self.x += self.vel_x
        # Bounce off walls
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
            self.vel_x *= -1

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y, self.width, self.height))  # Red Goomba

enemies = [Enemy(200, 200), Enemy(300, 200)]

# ========== POWER-UPS ==========
class PowerUp:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.active = True

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, (255, 255, 0), (self.x, self.y, 8, 8))  # Yellow Mushroom

powerups = [PowerUp(150, 150)]

# ========== CAMERA SCROLLING ==========
def get_camera_offset(player_x):
    return max(0, min(player_x - SCREEN_WIDTH//4, len(level_data[0])*TILE_SIZE - SCREEN_WIDTH))

# ========== MODE 7 EFFECT (FAKE PERSPECTIVE SKY) ==========
def draw_mode7_effect(surface, scroll):
    for y in range(SCREEN_HEIGHT):
        scale = max(1, int((y - scroll) / 10))
        pygame.draw.line(surface, (0, 0, 255), (0, y), (SCREEN_WIDTH, y), scale)

# ========== SOUND SYNTHESIS (FIXED FOR STEREO OUTPUT) ==========
def play_sound(freq=440, duration=0.1):
    sample_rate = 44100
    # Generate mono waveform
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    waveform = np.sin(freq * t * 2 * np.pi)
    # Normalize to 16-bit range
    audio = waveform * 32767
    # Convert to 16-bit integer array
    audio = np.int16(audio)
    # Convert to stereo (duplicate mono channel)
    stereo_audio = np.column_stack((audio, audio))
    sound = pygame.sndarray.make_sound(stereo_audio)
    sound.play()

# ========== SETUP AND LOOP ==========
player = Player()
camera_x = 0

def setup():
    pygame.display.set_caption("Mario-like Game")

def update_loop():
    global camera_x
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return

    # Update player
    player.update(keys)

    # Update enemies
    for enemy in enemies:
        enemy.update()

    # Check collisions
    player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
    for powerup in powerups:
        if powerup.active and player_rect.colliderect(pygame.Rect(powerup.x, powerup.y, 8, 8)):
            powerup.active = False
            player.size = 16  # Grow Mario

    # Camera scroll
    camera_x = get_camera_offset(player.x)

    # Clear virtual screen
    v_screen.fill((0, 0, 0))  # Black background

    # Draw Mode 7 sky effect
    draw_mode7_effect(v_screen, camera_x // 10)

    # Draw level
    draw_level(v_screen)

    # Draw enemies
    for enemy in enemies:
        enemy.draw(v_screen)

    # Draw power-ups
    for powerup in powerups:
        powerup.draw(v_screen)

    # Draw player
    player.draw(v_screen)

    # Scale and blit to real screen
    scaled_screen = pygame.transform.scale(v_screen, (SCREEN_WIDTH*SCALE, SCREEN_HEIGHT*SCALE))
    screen.blit(scaled_screen, (0, 0))
    pygame.display.flip()
    clock.tick(FPS)  # Target 60 FPS

async def main():
    setup()
    while True:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
