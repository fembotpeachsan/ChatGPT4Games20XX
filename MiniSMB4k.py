import pygame
import sys

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Player properties
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_COLOR = RED
PLAYER_SPEED = 5
JUMP_STRENGTH = 15
GRAVITY = 1

# Platform properties
PLATFORM_COLOR = GREEN

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    def jump(self):
        if self.on_ground:
            self.vel_y = -JUMP_STRENGTH
            self.on_ground = False

    def update(self, platforms):
        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10: # Terminal velocity
            self.vel_y = 10

        # Move horizontally
        self.rect.x += self.vel_x

        # Horizontal collision
        collided_platforms = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collided_platforms:
            if self.vel_x > 0: # Moving right
                self.rect.right = platform.rect.left
            elif self.vel_x < 0: # Moving left
                self.rect.left = platform.rect.right
            self.vel_x = 0 # Stop horizontal movement on collision

        # Move vertically
        self.rect.y += self.vel_y
        self.on_ground = False # Assume not on ground until collision check

        # Vertical collision
        collided_platforms = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collided_platforms:
            if self.vel_y > 0: # Moving down
                self.rect.bottom = platform.rect.top
                self.on_ground = True
                self.vel_y = 0
            elif self.vel_y < 0: # Moving up
                self.rect.top = platform.rect.bottom
                self.vel_y = 0
        
        # Prevent falling off screen bottom (simple boundary)
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.on_ground = True # Consider screen bottom as ground
            self.vel_y = 0

        # Prevent going off screen sides
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mini Mario-like Game")
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()

    player = Player(50, SCREEN_HEIGHT - PLAYER_HEIGHT - 50) # Start player on a virtual ground
    all_sprites.add(player)

    # Create some platforms
    platform_list = [
        (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40), # Ground platform
        (200, SCREEN_HEIGHT - 150, 150, 20),
        (400, SCREEN_HEIGHT - 250, 200, 20),
        (50, SCREEN_HEIGHT - 350, 100, 20)
    ]

    for plat_data in platform_list:
        platform = Platform(*plat_data)
        all_sprites.add(platform)
        platforms.add(platform)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    player.jump()
            # Continuous movement handling
            # Keydown sets velocity, keyup resets it if it's the same key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.vel_x = -PLAYER_SPEED
                if event.key == pygame.K_RIGHT:
                    player.vel_x = PLAYER_SPEED
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.vel_x < 0:
                    player.vel_x = 0
                if event.key == pygame.K_RIGHT and player.vel_x > 0:
                    player.vel_x = 0
        
        # Update
        player.update(platforms) # Pass platforms for collision detection

        # Draw / Render
        screen.fill(BLUE)  # Sky blue background
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
