import pygame
import random
import math

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32  # Changed to 32 for a more classic feel

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BRICK_COLOR = (160, 32, 240)  # A more classic brick color
GROUND_COLOR = (139, 69, 19)  # Brown for ground
EMPTY_COLOR = (92, 148, 252) # Light blue for empty space

# Player properties
PLAYER_WIDTH = 24  # Slightly smaller player
PLAYER_HEIGHT = 24
PLAYER_SPEED = 3
JUMP_FORCE = -10
GRAVITY = 0.5

# Mode 7 Constants
BACKGROUND_ROTATION_SPEED = 0.05
BACKGROUND_MIN_SCALE = 0.5
BACKGROUND_MAX_SCALE = 1.2

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False

    def update(self, tiles):
        self.velocity_y += GRAVITY

        # Horizontal movement
        self.rect.x += self.velocity_x
        tile_collisions = pygame.sprite.spritecollide(self, tiles, False)
        for tile in tile_collisions:
            if self.velocity_x > 0:
                self.rect.right = tile.rect.left
            elif self.velocity_x < 0:
                self.rect.left = tile.rect.right

        # Vertical movement
        self.rect.y += self.velocity_y
        self.on_ground = False
        tile_collisions = pygame.sprite.spritecollide(self, tiles, False)
        for tile in tile_collisions:
            if self.velocity_y > 0:
                self.rect.bottom = tile.rect.top
                self.on_ground = True
                self.velocity_y = 0
            elif self.velocity_y < 0:
                self.rect.top = tile.rect.bottom
                self.velocity_y = 0

        # Keep within screen bounds (optional)
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0
            self.on_ground = True
        elif self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0

    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_FORCE
            self.on_ground = False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = random.choice([-1, 1]) * 1  # Slower enemy speed

    def update(self, tiles):
        self.rect.x += self.velocity_x
        tile_collisions = pygame.sprite.spritecollide(self, tiles, False)
        for tile in tile_collisions:
            if self.velocity_x > 0:
                self.velocity_x = -abs(self.velocity_x)
            elif self.velocity_x < 0:
                self.velocity_x = abs(self.velocity_x)

        self.rect.y += 1  # Simple gravity for enemies
        tile_collisions = pygame.sprite.spritecollide(self, tiles, False)
        if not tile_collisions:
            # If falling off an edge, reverse direction
            if self.velocity_x > 0:
                self.velocity_x = -abs(self.velocity_x)
            elif self.velocity_x < 0:
                self.velocity_x = abs(self.velocity_x)
        else:
            self.rect.bottom = tile_collisions[0].rect.top

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario FX")
        self.clock = pygame.time.Clock()
        self.running = True

        self.mario = Player(100, 0, RED)  # Start Mario higher
        self.luigi = Player(160, 0, GREEN) # Start Luigi higher

        self.enemies = pygame.sprite.Group()
        self.enemies.add(Enemy(400, 0))
        self.enemies.add(Enemy(600, 0))

        self.tiles = pygame.sprite.Group()
        self.load_level() # Load the level design

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.mario)
        self.all_sprites.add(self.luigi)
        self.all_sprites.add(self.enemies)
        self.all_sprites.add(self.tiles)

        self.background_angle = 0
        self.background_scale = 1.0
        self.background_scale_speed = 0.005  # Slower background scaling

    def load_level(self):
        # Example level design using a 2D list
        level_design = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]

        # Iterate through the level design and create tiles
        for row_index, row in enumerate(level_design):
            for col_index, tile_type in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if tile_type == 1:
                    self.tiles.add(Tile(x, y, GROUND_COLOR))
                elif tile_type == 2:
                    self.tiles.add(Tile(x, y, BRICK_COLOR))
                # 0 represents empty space, no tile needed

    def show_menu(self):
        menu_font = pygame.font.Font(None, 50)
        instructions_font = pygame.font.Font(None, 30)

        title_text = menu_font.render("Super Mario FX", True, WHITE)
        play_text = menu_font.render("Press ENTER to Play", True, WHITE)
        exit_text = menu_font.render("Press ESC to Quit", True, WHITE)
        controls_text = instructions_font.render("Controls: WASD for Luigi, Arrow Keys for Mario, Space to Jump", True, WHITE)

        while True:
            self.screen.fill(BLACK)
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
            self.screen.blit(play_text, (SCREEN_WIDTH // 2 - play_text.get_width() // 2, 200))
            self.screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, 300))
            self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, 400))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.mario.velocity_x = -PLAYER_SPEED
        elif keys[pygame.K_RIGHT]:
            self.mario.velocity_x = PLAYER_SPEED
        else:
            self.mario.velocity_x = 0

        if keys[pygame.K_a]:
            self.luigi.velocity_x = -PLAYER_SPEED
        elif keys[pygame.K_d]:
            self.luigi.velocity_x = PLAYER_SPEED
        else:
            self.luigi.velocity_x = 0

        if keys[pygame.K_SPACE]:
            self.mario.jump()
        if keys[pygame.K_w]:
            self.luigi.jump()

    def update(self):
        self.mario.update(self.tiles)
        self.luigi.update(self.tiles)
        self.enemies.update(self.tiles)

    def draw(self):
        # Apply Mode 7-like background effect (rotation + scaling)
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill(EMPTY_COLOR) # Set background to light blue

        # Rotate and scale the background
        self.background_angle += BACKGROUND_ROTATION_SPEED
        self.background_scale += self.background_scale_speed
        if self.background_scale > BACKGROUND_MAX_SCALE or self.background_scale < BACKGROUND_MIN_SCALE:
            self.background_scale_speed *= -1  # Reverse the scaling direction

        # Rotate and scale the background
        rotated_background = pygame.transform.rotate(background, self.background_angle)
        scaled_width = int(SCREEN_WIDTH * self.background_scale)
        scaled_height = int(SCREEN_HEIGHT * self.background_scale)
        scaled_background = pygame.transform.scale(rotated_background, (scaled_width, scaled_height))

        # Center the scaled background
        bg_x = (SCREEN_WIDTH - scaled_width) // 2
        bg_y = (SCREEN_HEIGHT - scaled_height) // 2

        # Draw background
        self.screen.fill(BLACK)
        self.screen.blit(scaled_background, (bg_x, bg_y))

        # Draw tiles
        self.tiles.draw(self.screen)

        # Draw sprites
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def run(self):
        self.show_menu()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
