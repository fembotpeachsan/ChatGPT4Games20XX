# Complete code with upgraded physics for platform interactions

# Initialize Pygame
import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Initialize screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Initialize fonts
font = pygame.font.Font(None, 74)

# Function to show title screen
def show_title_screen():
    screen.fill(BLACK)
    title = font.render("Donkey Kong", True, WHITE)
    screen.blit(title, (300, 250))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 50])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = HEIGHT - 60
        self.change_x = 0
        self.change_y = 0
        self.jump_power = 10  # Power of the jump
        self.gravity = 0.5  # Gravity pulling the player down

    def update(self):
        # Apply gravity
        self.change_y += self.gravity

        # Check for collision with platforms
        collision_list = pygame.sprite.spritecollide(self, platform_list, False)
        for platform in collision_list:
            if self.change_y > 0:  # Moving down; hit the top side of the platform
                self.rect.bottom = platform.rect.top
                self.change_y = 0  # Stop vertical movement

            elif self.change_y < 0:  # Moving up; hit the bottom side of the platform
                self.rect.top = platform.rect.bottom
                self.change_y = 0  # Stop vertical movement

        # Update position
        self.rect.x += self.change_x
        self.rect.y += self.change_y

        # Simple floor collision to stop falling
        if self.rect.y > HEIGHT - 50:
            self.rect.y = HEIGHT - 50
            self.change_y = 0

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(RED)
        self.rect = self.image.get_rect()

# Show the title screen first
show_title_screen()

# Initialize sprite groups
all_sprites = pygame.sprite.Group()
platform_list = pygame.sprite.Group()

# Create platforms
for i in range(5):
    platform = Platform(150, 10)
    platform.rect.x = i * 200
    platform.rect.y = HEIGHT - (i * 100) - 50
    platform_list.add(platform)
    all_sprites.add(platform)

# Create player
player = Player()
all_sprites.add(player)

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Player movement and jump
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.change_x = -5
            if event.key == pygame.K_RIGHT:
                player.change_x = 5
            if event.key == pygame.K_SPACE:  # Jump when the space bar is pressed
                player.change_y = -player.jump_power  # Negative because Pygame's y-axis is inverted

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player.change_x = 0

    # Update
    all_sprites.update()

    # Draw everything
    screen.fill(BLACK)
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

