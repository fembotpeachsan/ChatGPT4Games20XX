import pygame
import random
import numpy as np

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Diablo-like Game with Inventory and Loot')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Player settings
PLAYER_SIZE = 40
PLAYER_SPEED = 5
PLAYER_COLOR = GREEN
START_HEALTH = 100
START_MANA = 50
EXP_PER_LEVEL = 100

# Item settings
ITEM_SIZE = 20
ITEM_COLOR_WEAPON = YELLOW
ITEM_COLOR_BANDAGE = BLUE
ITEM_COLOR_AMMO = RED

# Inventory settings
INVENTORY_SLOT_SIZE = 50
INVENTORY_COLUMNS = 5
INVENTORY_ROWS = 2

# Goblin settings
GOBLIN_SIZE = 40
GOBLIN_COLOR = RED
GOBLIN_SPEED = 2
GOBLIN_HEALTH = 30

# Inventory Class
class Inventory:
    def __init__(self, columns=INVENTORY_COLUMNS, rows=INVENTORY_ROWS):
        self.columns = columns
        self.rows = rows
        self.slots = [[None for _ in range(self.columns)] for _ in range(self.rows)]
        self.visible = False  # Initially not visible

    def draw(self, surface):
        if self.visible:
            for row in range(self.rows):
                for col in range(self.columns):
                    pygame.draw.rect(surface, WHITE, [100 + col * INVENTORY_SLOT_SIZE, 100 + row * INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE], 2)
                    item = self.slots[row][col]
                    if item:
                        pygame.draw.rect(surface, item.color, [110 + col * INVENTORY_SLOT_SIZE, 110 + row * INVENTORY_SLOT_SIZE, ITEM_SIZE, ITEM_SIZE])

    def add_item(self, item):
        for row in range(self.rows):
            for col in range(self.columns):
                if self.slots[row][col] is None:
                    self.slots[row][col] = item
                    print(f"Added {item.item_type} to inventory at slot {row}, {col}")
                    return
        print("Inventory full!")

    def toggle_visibility(self):
        self.visible = not self.visible

# Item class
class Item(pygame.sprite.Sprite):
    def __init__(self, item_type, color, rect):
        super().__init__()
        self.item_type = item_type
        self.image = pygame.Surface((ITEM_SIZE, ITEM_SIZE))
        self.image.fill(color)
        self.rect = rect
        self.color = color

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, inventory):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.health = START_HEALTH
        self.inventory = inventory  # Link inventory to player

    def update(self, keys):
        if keys[pygame.K_w]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_s]:
            self.rect.y += PLAYER_SPEED
        if keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED

        # Boundaries check
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

# Enemy class (Goblin)
class Goblin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((GOBLIN_SIZE, GOBLIN_SIZE))
        self.image.fill(GOBLIN_COLOR)
        self.rect = self.image.get_rect(center=(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)))
        self.health = GOBLIN_HEALTH

    def update(self, player_pos):
        direction = pygame.math.Vector2(player_pos[0] - self.rect.x, player_pos[1] - self.rect.y)
        if direction.length() != 0:
            direction.scale_to_length(GOBLIN_SPEED)
        self.rect.move_ip(direction)

# Game setup
inventory = Inventory()  # Create inventory for player
player = Player(inventory)
player_group = pygame.sprite.Group(player)
goblins = pygame.sprite.Group()
items = pygame.sprite.Group()

# Spawn some goblins
for _ in range(5):
    goblins.add(Goblin())

# Function to spawn random items
def spawn_item():
    item_type = random.choice(['weapon', 'bandage', 'ammo'])
    color = ITEM_COLOR_WEAPON if item_type == 'weapon' else ITEM_COLOR_BANDAGE if item_type == 'bandage' else ITEM_COLOR_AMMO
    rect = pygame.Rect(random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50), ITEM_SIZE, ITEM_SIZE)
    item = Item(item_type, color, rect)
    items.add(item)

# Spawn random items
for _ in range(10):
    spawn_item()

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)
    keys = pygame.key.get_pressed()

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:  # Toggle inventory visibility when E is pressed
                inventory.toggle_visibility()

    # Player updates
    player_group.update(keys)

    # Update goblins and items
    goblins.update(player.rect.center)

    # Check for collisions between player and items (picking up items)
    for item in pygame.sprite.spritecollide(player, items, True):
        player.inventory.add_item(item)

    # Check for goblins colliding with player
    for goblin in pygame.sprite.spritecollide(player, goblins, False):
        player.health -= 1
        if player.health <= 0:
            running = False

    # Draw everything
    player_group.draw(screen)
    goblins.draw(screen)
    items.draw(screen)

    # Draw inventory if visible
    inventory.draw(screen)

    # Draw health bar
    pygame.draw.rect(screen, RED, [20, 20, 200, 20])
    pygame.draw.rect(screen, GREEN, [20, 20, 2 * player.health, 20])

    # Update screen
    pygame.display.flip()

    # Frame rate
    clock.tick(60)

# Exit Pygame
pygame.quit()
