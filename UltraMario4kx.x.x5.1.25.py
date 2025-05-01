import pygame
import sys
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_TITLE = "Mario-Style Platformer"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (237, 28, 36)
BLUE = (0, 88, 248)
YELLOW = (255, 216, 0)
SKY_BLUE = (92, 148, 252)
BRICK_RED = (200, 76, 12)
PIPE_GREEN = (0, 168, 0)

# Physics Constants
PLAYER_ACC = 36
PLAYER_FRICTION = -9
PLAYER_GRAVITY = 48
PLAYER_JUMP = -960

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 48), pygame.SRCALPHA)
        self._draw_mario()
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False

    def _draw_mario(self):
        # Body
        pygame.draw.rect(self.image, RED, (8, 8, 16, 32))
        # Head
        pygame.draw.circle(self.image, (252, 216, 168), (16, 16), 8)
        # Legs
        pygame.draw.rect(self.image, BLUE, (8, 40, 8, 8))
        pygame.draw.rect(self.image, BLUE, (16, 40, 8, 8))

    def jump(self):
        if self.on_ground:
            self.vel.y = PLAYER_JUMP
            self.on_ground = False

    def update(self, dt):
        keys = pygame.key.get_pressed()
        acc_x = PLAYER_ACC * (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT])
        
        self.vel.x += acc_x
        self.vel.x *= 0.9  # Simple friction
        self.vel.y += PLAYER_GRAVITY
        self.rect.y += self.vel.y * dt
        
        # Platform collision
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel.y > 0:
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.vel.y = 0
                elif self.vel.y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel.y = 0

        self.rect.x += self.vel.x * dt
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - 32))

class Goomba(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self._draw_goomba()
        self.rect = self.image.get_rect(bottomleft=(x, y))
        self.direction = -1

    def _draw_goomba(self):
        pygame.draw.ellipse(self.image, (144, 88, 0), (0, 8, 32, 24))
        pygame.draw.rect(self.image, (88, 48, 0), (0, 24, 32, 8))
        pygame.draw.line(self.image, BLACK, (8, 16), (24, 16), 4)

    def update(self, dt):
        self.rect.x += self.direction * 60 * dt
        if not any(p.rect.collidepoint(self.rect.midbottom) for p in platforms):
            self.direction *= -1

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(BRICK_RED)
        self.rect = self.image.get_rect(topleft=(x, y))

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 26), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (10, 13), 8)
        self.rect = self.image.get_rect(center=(x, y))

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Create level elements
platforms = pygame.sprite.Group(
    Block(0, SCREEN_HEIGHT-40, SCREEN_WIDTH, 40),
    Block(200, 400, 120, 20),
    Block(400, 350, 120, 20)
)

coins = pygame.sprite.Group(
    Coin(220, 380),
    Coin(420, 330),
    Coin(620, 280)
)

enemies = pygame.sprite.Group(
    Goomba(300, SCREEN_HEIGHT-40),
    Goomba(500, 400)
)

player = Player(100, SCREEN_HEIGHT-40)
all_sprites = pygame.sprite.Group(player, platforms, coins, enemies)

running = True
while running:
    dt = clock.tick(FPS) / 1000
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP):
                player.jump()

    # Update
    all_sprites.update(dt)
    
    # Coin collection
    for coin in pygame.sprite.spritecollide(player, coins, True):
        pass  # Add score logic here

    # Enemy collision
    for enemy in pygame.sprite.spritecollide(player, enemies, False):
        if player.vel.y > 0:
            enemy.kill()
            player.vel.y = -PLAYER_JUMP//2
        else:
            running = False

    # Draw
    screen.fill(SKY_BLUE)
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
