import pygame
import sys
import time

# GameBoy-inspired color palette
GB_DARKEST = (15, 56, 15)
GB_DARK = (48, 98, 48)
GB_LIGHT = (139, 172, 15)
GB_LIGHTEST = (155, 188, 15)

class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Inventory:
    def __init__(self):
        self.items = []
        self.selected_index = 0

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None

    def get_selected_item(self):
        if self.items:
            return self.items[self.selected_index]
        return None

    def move_selection(self, direction):
        self.selected_index = (self.selected_index + direction) % len(self.items)

class GameObject:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen):
        pygame.draw.rect(screen, GB_DARKEST, self.rect)

class Mario(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 16, 24)
        self.velocity_y = 0
        self.is_jumping = False

    def draw(self, screen):
        pygame.draw.rect(screen, GB_DARK, self.rect)
        # Simple face
        pygame.draw.rect(screen, GB_DARKEST, (self.rect.x + 4, self.rect.y + 4, 3, 3))
        pygame.draw.rect(screen, GB_DARKEST, (self.rect.x + 10, self.rect.y + 4, 3, 3))
        pygame.draw.rect(screen, GB_DARKEST, (self.rect.x + 4, self.rect.y + 14, 9, 3))

class Platform(GameObject):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

    def draw(self, screen):
        pygame.draw.rect(screen, GB_DARK, self.rect)

class GameEngine:
    def __init__(self, width, height):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Legacy Delta Mario 1.0s")
        self.clock = pygame.time.Clock()
        self.mario = Mario(50, height - 40)
        self.platforms = [Platform(0, height - 16, width, 16)]
        self.start_time = time.time()
        self.coins = 0
        self.level = "1-1"
        self.inventory = Inventory()
        self.show_inventory = False
        self.font = pygame.font.Font(None, 20)

        # Add some items to the inventory
        self.inventory.add_item(Item("Mushroom", "Increases size"))
        self.inventory.add_item(Item("Star", "Temporary invincibility"))
        self.inventory.add_item(Item("Coin", "Collect 100 for extra life"))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.mario.is_jumping:
                    self.mario.velocity_y = -10
                    self.mario.is_jumping = True
                elif event.key == pygame.K_i:
                    self.show_inventory = not self.show_inventory
                elif event.key == pygame.K_UP and self.show_inventory:
                    self.inventory.move_selection(-1)
                elif event.key == pygame.K_DOWN and self.show_inventory:
                    self.inventory.move_selection(1)

    def update(self):
        if not self.show_inventory:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.mario.rect.x -= 3
            if keys[pygame.K_RIGHT]:
                self.mario.rect.x += 3

            # Apply gravity
            self.mario.velocity_y += 0.8
            self.mario.rect.y += self.mario.velocity_y

            # Check for collisions with platforms
            for platform in self.platforms:
                if self.mario.rect.colliderect(platform.rect):
                    if self.mario.velocity_y > 0:
                        self.mario.rect.bottom = platform.rect.top
                        self.mario.velocity_y = 0
                        self.mario.is_jumping = False

            # Keep Mario within screen bounds
            self.mario.rect.clamp_ip(self.screen.get_rect())

    def draw(self):
        self.screen.fill(GB_LIGHTEST)
        for platform in self.platforms:
            platform.draw(self.screen)
        self.mario.draw(self.screen)
        self.draw_hud()
        if self.show_inventory:
            self.draw_inventory()
        pygame.display.flip()

    def draw_hud(self):
        # Timer
        elapsed_time = int(time.time() - self.start_time)
        timer_text = self.font.render(f"TIME:{elapsed_time}", True, GB_DARKEST)
        self.screen.blit(timer_text, (10, 10))

        # Coin counter
        coin_text = self.font.render(f"COINS:{self.coins}", True, GB_DARKEST)
        self.screen.blit(coin_text, (100, 10))

        # Level info
        level_text = self.font.render(f"WORLD:{self.level}", True, GB_DARKEST)
        self.screen.blit(level_text, (200, 10))

    def draw_inventory(self):
        inventory_surface = pygame.Surface((200, 180))
        inventory_surface.fill(GB_LIGHT)
        pygame.draw.rect(inventory_surface, GB_DARK, inventory_surface.get_rect(), 3)

        title = self.font.render("INVENTORY", True, GB_DARKEST)
        inventory_surface.blit(title, (10, 10))

        for i, item in enumerate(self.inventory.items):
            color = GB_DARKEST if i == self.inventory.selected_index else GB_DARK
            item_text = self.font.render(item.name, True, color)
            inventory_surface.blit(item_text, (20, 40 + i * 30))

        if self.inventory.get_selected_item():
            desc = self.font.render(self.inventory.get_selected_item().description, True, GB_DARKEST)
            inventory_surface.blit(desc, (20, 150))

        self.screen.blit(inventory_surface, (28, 22))

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

# Run the game
if __name__ == "__main__":
    engine = GameEngine(256, 224)  # GameBoy resolution
    engine.run()
