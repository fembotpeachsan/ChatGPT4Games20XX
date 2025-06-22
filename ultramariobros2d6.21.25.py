import pygame
import sys
import random

# -----------------------------------------------------------------------------#
# Constants
# -----------------------------------------------------------------------------#
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
ROWS, COLS_VIEW = SCREEN_HEIGHT // 40, SCREEN_WIDTH // 40   # 15×20 tiles on‑screen
TILE_SIZE = 40
GRAVITY = 0.5
PLAYER_SPEED = 5
JUMP_SPEED = -12
FPS = 60
LEVEL_COUNT = 32           # 8 worlds × 4 stages

# Colours (R,G,B)
SKY_BLUE     = (135, 206, 235)
GROUND_BROWN = (139, 69,  19)
PLAYER_RED   = (255, 0,   0)
BLOCK_GREEN  = (  0, 255, 0)
QUESTION_GOLD= (255, 220, 0)

# Map characters → visual style
TILE_TYPES = {
    'X': GROUND_BROWN,   # solid brick / ground
    '?': QUESTION_GOLD,  # question block (behaves like solid for now)
}

# -----------------------------------------------------------------------------#
# Sprite classes
# -----------------------------------------------------------------------------#
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, colour):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(colour)
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(PLAYER_RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.on_ground = False

    def update(self, blocks):
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PLAYER_SPEED

        # Gravity
        self.vel_y += GRAVITY
        dy = self.vel_y

        # Horizontal collision
        self.rect.x += dx
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if dx > 0:
                    self.rect.right = block.rect.left
                elif dx < 0:
                    self.rect.left = block.rect.right

        # Vertical collision
        self.rect.y += dy
        self.on_ground = False
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if dy > 0:   # Falling
                    self.rect.bottom = block.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif dy < 0: # Jumping
                    self.rect.top = block.rect.bottom
                    self.vel_y = 0

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_SPEED

class Camera:
    """Keeps the player roughly centred while staying inside level bounds"""
    def __init__(self, level_px_width):
        self.offset_x = 0
        self.level_px_width = level_px_width

    def apply(self, rect):
        return rect.move(-self.offset_x, 0)

    def update(self, target_rect):
        center = target_rect.centerx
        self.offset_x = max(0, min(center - SCREEN_WIDTH // 2, self.level_px_width - SCREEN_WIDTH))

# -----------------------------------------------------------------------------#
# Level generation
# -----------------------------------------------------------------------------#
def generate_level(level_no):
    """
    Simple deterministic generator: ground everywhere,
    plus a handful of pillars and floating blocks that vary with level_no.
    World length = 50 columns (can adjust).
    """
    random.seed(level_no)           # reproducible
    COLS_TOTAL = 50
    rows = ['.' * COLS_TOTAL for _ in range(ROWS)]

    # Convert to list of list for easy mutation
    rows = [list(r) for r in rows]

    # Full ground on last row
    for c in range(COLS_TOTAL):
        rows[ROWS-1][c] = 'X'

    # Add a few gaps
    for _ in range(4 + level_no % 3):
        start = random.randint(5, COLS_TOTAL-8)
        length = random.randint(2, 4)
        for c in range(start, start+length):
            rows[ROWS-1][c] = '.'

    # Add columns/pillars
    for _ in range(3 + level_no % 5):
        col = random.randint(3, COLS_TOTAL-4)
        height = random.randint(1, 3)
        for h in range(height):
            rows[ROWS-1-h][col] = 'X'

    # Floating bricks / question blocks
    for _ in range(6):
        col = random.randint(4, COLS_TOTAL-6)
        row = random.randint(6, ROWS-4)
        rows[row][col] = '?' if random.random() < 0.4 else 'X'

    # Convert back to list[str]
    return [''.join(r) for r in rows]

def load_level(level_no, all_sprites, block_group):
    all_sprites.empty()
    block_group.empty()

    layout = generate_level(level_no)
    for r, row in enumerate(layout):
        for c, ch in enumerate(row):
            if ch in TILE_TYPES:
                colour = TILE_TYPES[ch]
                block = Block(c*TILE_SIZE, r*TILE_SIZE, colour)
                block_group.add(block)
                all_sprites.add(block)

    player = Player(80, SCREEN_HEIGHT - 3*TILE_SIZE)
    all_sprites.add(player)
    return player, len(layout[0]) * TILE_SIZE   # player, level pixel width

# -----------------------------------------------------------------------------#
# Main loop
# -----------------------------------------------------------------------------#
def main():
    pygame.init()
    screen  = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Minimal SMB‑style 32‑Level Demo (No Assets)")
    clock   = pygame.time.Clock()

    # Groups
    all_sprites = pygame.sprite.Group()
    blocks      = pygame.sprite.Group()

    current_level = 0
    player, level_width = load_level(current_level, all_sprites, blocks)
    camera = Camera(level_width)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000   # not strictly needed but handy

        # ----------------- Events -----------------#
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ----------------- Update -----------------#
        player.update(blocks)
        camera.update(player.rect)

        # Check for level completion (player exits right side)
        if player.rect.right > level_width:
            current_level += 1
            if current_level >= LEVEL_COUNT:
                print("Congratulations! You completed all 32 levels.")
                running = False
            else:
                player, level_width = load_level(current_level, all_sprites, blocks)
                camera = Camera(level_width)

        # ----------------- Draw -----------------#
        screen.fill(SKY_BLUE)
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite.rect))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
