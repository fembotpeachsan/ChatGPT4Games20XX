import os
import sys
import math
import pygame

# Init Pygame
pygame.init()

# Constants for GBA style
SCREEN_WIDTH, SCREEN_HEIGHT = 480, 320  # 2x GBA res for visibility
GBA_SCALE = 2
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -12
PLAYER_SPEED = 4
BOSS_HEALTH_MAX = 100
PLAYER_HEALTH_MAX = 50

# Colors (limited palette for retro feel)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)  # Gardevoir's psychic hue

# Load assets (placeholders; replace with sprites)
# os.path for cross-platform
ASSET_DIR = os.path.dirname(__file__)
# PLAYER_SPRITE = pygame.image.load(os.path.join(ASSET_DIR, 'player.png'))
# BOSS_SPRITE = pygame.image.load(os.path.join(ASSET_DIR, 'gardevoir.png'))
# For now, use rects as placeholders

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
        self.vel_x = 0
        self.vel_y = 0
        self.health = PLAYER_HEALTH_MAX
        self.on_ground = False

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

        # Physics: Gravity + velocity
        self.vel_y += GRAVITY
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Collision with ground/platforms
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vel_y > 0:
                    self.rect.bottom = plat.top
                    self.vel_y = 0
                    self.on_ground = True

        # Boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0
            self.on_ground = True

    def attack(self):
        # Simple projectile attack
        proj = Projectile(self.rect.centerx, self.rect.centery, 5, BLUE)
        return proj

class GardevoirBoss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((64, 64))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT // 2)
        self.health = BOSS_HEALTH_MAX
        self.phase = 0  # 0: Idle, 1: Teleport, 2: Beam, 3: Barrier
        self.timer = 0
        self.vel_x = 0
        self.vel_y = 0
        self.barrier_active = False

    def update(self, player):
        self.timer += 1
        if self.phase == 0:  # Idle float
            self.vel_y = math.sin(self.timer / 10) * 2  # Sinusoidal hover
            self.rect.y += self.vel_y
            if self.timer > 120:
                self.phase = 1
                self.timer = 0

        elif self.phase == 1:  # Teleport dash (Meta Knight style)
            if self.timer == 1:
                target_x = player.rect.x + (100 if player.vel_x > 0 else -100)
                self.rect.x = target_x
                self.rect.y = player.rect.y - 50
            if self.timer > 30:
                self.phase = 2
                self.timer = 0

        elif self.phase == 2:  # Psychic beam sweep
            if self.timer % 20 == 0:
                beam = Projectile(self.rect.centerx, self.rect.centery, -8, RED)  # Towards player-ish
                return beam  # Yield to all_sprites
            if self.timer > 90:
                self.phase = 3
                self.timer = 0

        elif self.phase == 3:  # Barrier reflect
            self.barrier_active = True
            if self.timer > 60:
                self.barrier_active = False
                self.phase = 0
                self.timer = 0

        # Boss boundaries and health check
        if self.health <= 0:
            print("Boss defeated!")  # Win condition
            sys.exit()

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

# Main game loop
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Gardevoir Boss Fight - GBA Style 60FPS")
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    platforms = [pygame.Rect(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20)]  # Ground

    player = Player()
    boss = GardevoirBoss()
    all_sprites.add(player, boss)

    projectiles = pygame.sprite.Group()

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    proj = player.attack()
                    projectiles.add(proj)
                    all_sprites.add(proj)

        # Updates
        player.update(platforms)
        boss_update = boss.update(player)
        if boss_update:
            projectiles.add(boss_update)
            all_sprites.add(boss_update)

        projectiles.update()

        # Collisions: Player proj hits boss
        for proj in projectiles:
            if proj.speed > 0:  # Player proj
                if pygame.sprite.collide_rect(proj, boss):
                    if not boss.barrier_active:
                        boss.health -= 5
                    else:
                        # Reflect: Reverse speed
                        proj.speed = -proj.speed
                    proj.kill()
            else:  # Boss proj
                if pygame.sprite.collide_rect(proj, player):
                    player.health -= 10
                    proj.kill()
                    if player.health <= 0:
                        print("Player defeated!")
                        running = False

        # Draw everything
        screen.fill(BLACK)
        # Draw platforms
        for plat in platforms:
            pygame.draw.rect(screen, WHITE, plat)
        all_sprites.draw(screen)

        # Health bars
        pygame.draw.rect(screen, RED, (10, 10, PLAYER_HEALTH_MAX * 2, 10))
        pygame.draw.rect(screen, BLUE, (10, 10, player.health * 2, 10))
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH - BOSS_HEALTH_MAX * 2 - 10, 10, BOSS_HEALTH_MAX * 2, 10))
        pygame.draw.rect(screen, PURPLE, (SCREEN_WIDTH - BOSS_HEALTH_MAX * 2 - 10, 10, boss.health * 2, 10))

        # Retro filter: Scale down then up for pixelation
        retro_surf = pygame.transform.scale(screen, (SCREEN_WIDTH // GBA_SCALE, SCREEN_HEIGHT // GBA_SCALE))
        screen.blit(pygame.transform.scale(retro_surf, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
