import pygame
import sys
import random

# -----------------------------------------------------------------------------#
# Constants
# -----------------------------------------------------------------------------#
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
ROWS, COLS_VIEW   = SCREEN_HEIGHT // 40, SCREEN_WIDTH // 40   # 15×20 tiles on‑screen
TILE_SIZE         = 40
GRAVITY           = 0.5
PLAYER_SPEED      = 5
JUMP_SPEED        = -12
FPS               = 60
LEVEL_COUNT       = 32           # 8 worlds × 4 stages

# Colours (R,G,B)
SKY_BLUE      = (135, 206, 235)
GROUND_BROWN  = (139,  69,  19)
PLAYER_RED    = (255,   0,   0)
BLOCK_GREEN   = (  0, 255,   0)
QUESTION_GOLD = (255, 220,   0)
POLE_GREY     = (180, 180, 180)
FLAG_WHITE    = (250, 250, 250)
FLAG_SELECT   = (255, 100, 100)

# Map characters → visual style
TILE_TYPES = {
    'X': GROUND_BROWN,   # solid brick / ground
    '?': QUESTION_GOLD,  # question block (behaves like solid for now)
}

# Main‑line titles, SMB → NSMB U
GAME_LIST = [
    "Super Mario Bros.",
    "The Lost Levels",
    "Super Mario Bros. 2 (USA)",
    "Super Mario Bros. 3",
    "Super Mario World",
    "Super Mario World 2: YI",
    "New Super Mario Bros.",
    "New SMB Wii",
    "New SMB 2 (3DS)",
    "New SMB U",
]

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
        self.offset_x = max(0, min(center - SCREEN_WIDTH // 2,
                                   self.level_px_width - SCREEN_WIDTH))

# -----------------------------------------------------------------------------#
# Level generation  (unchanged from previous version)
# -----------------------------------------------------------------------------#
def generate_level(level_no):
    """Very small deterministic generator."""
    random.seed(level_no)
    COLS_TOTAL = 50
    rows = ['.' * COLS_TOTAL for _ in range(ROWS)]
    rows = [list(r) for r in rows]

    # Ground
    for c in range(COLS_TOTAL):
        rows[ROWS-1][c] = 'X'

    # Gaps
    for _ in range(4 + level_no % 3):
        start = random.randint(5, COLS_TOTAL-8)
        length = random.randint(2, 4)
        for c in range(start, start+length):
            rows[ROWS-1][c] = '.'

    # Pillars
    for _ in range(3 + level_no % 5):
        col = random.randint(3, COLS_TOTAL-4)
        height = random.randint(1, 3)
        for h in range(height):
            rows[ROWS-1-h][col] = 'X'

    # Floating blocks / ?
    for _ in range(6):
        col = random.randint(4, COLS_TOTAL-6)
        row = random.randint(6, ROWS-4)
        rows[row][col] = '?' if random.random() < 0.4 else 'X'

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
# Menu rendering helpers
# -----------------------------------------------------------------------------#
def draw_menu(screen, font, selected):
    screen.fill(SKY_BLUE)

    # Draw flag‑pole
    pole_x = SCREEN_WIDTH // 3
    pole_top = 50
    pole_bottom = SCREEN_HEIGHT - 50
    pygame.draw.line(screen, POLE_GREY, (pole_x, pole_top), (pole_x, pole_bottom), 6)

    # Draw flags vertically spaced
    flag_h = 32
    gap = 10
    start_y = pole_top + 20
    for idx, title in enumerate(GAME_LIST):
        y = start_y + idx * (flag_h + gap)
        colour = FLAG_SELECT if idx == selected else FLAG_WHITE
        rect = pygame.Rect(pole_x + 6, y, 300, flag_h)
        pygame.draw.rect(screen, colour, rect)
        pygame.draw.rect(screen, (0,0,0), rect, 2)  # outline

        # Text
        txt = font.render(title, True, (0, 0, 0))
        screen.blit(txt, (rect.x + 8, rect.y + (flag_h - txt.get_height()) // 2))

    # Simple “Press Start” hint
    hint = font.render("↑↓ SELECT   ENTER START", True, (0,0,0))
    screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2,
                       pole_bottom + 10))

# -----------------------------------------------------------------------------#
# Main
# -----------------------------------------------------------------------------#
def main():
    pygame.init()
    screen  = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mario Flag‑Menu Demo (No Assets)")
    clock   = pygame.time.Clock()
    font    = pygame.font.SysFont(None, 24)  # default font, 24 pt

    # Sprite groups for gameplay
    all_sprites = pygame.sprite.Group()
    blocks      = pygame.sprite.Group()

    # State machine
    state = "MENU"
    selected_idx = 0
    current_game = None      # string name
    current_level = 0

    # Pre‑load first level (will actually be used after menu)
    player, level_width = load_level(current_level, all_sprites, blocks)
    camera = Camera(level_width)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        # ----------------- Events -----------------#
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        selected_idx = (selected_idx - 1) % len(GAME_LIST)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        selected_idx = (selected_idx + 1) % len(GAME_LIST)
                    elif event.key in (pygame.K_RETURN, pygame.K_z,
                                       pygame.K_x, pygame.K_SPACE):
                        # Begin game
                        current_game = GAME_LIST[selected_idx]
                        print(f"Starting: {current_game}")
                        state = "PLAY"
                        current_level = 0
                        player, level_width = load_level(
                            current_level, all_sprites, blocks)
                        camera = Camera(level_width)

            elif state == "PLAY":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Return to menu at any time
                    state = "MENU"

        # ----------------- Update & Draw -----------------#
        if state == "MENU":
            draw_menu(screen, font, selected_idx)

        elif state == "PLAY":
            player.update(blocks)
            camera.update(player.rect)

            # Level completion
            if player.rect.right > level_width:
                current_level += 1
                if current_level >= LEVEL_COUNT:
                    print(f"Finished all levels in {current_game}!")
                    state = "MENU"
                else:
                    player, level_width = load_level(
                        current_level, all_sprites, blocks)
                    camera = Camera(level_width)

            # Render
            screen.fill(SKY_BLUE)
            for sprite in all_sprites:
                screen.blit(sprite.image, camera.apply(sprite.rect))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
