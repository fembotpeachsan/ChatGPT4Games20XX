import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Plants vs. Zombies HD (No PNGs)")

# Colors
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
DARK_GREEN = (0, 100, 0)
DARK_RED = (139, 0, 0)
GREY = (169, 169, 169)

# Grid settings
ROWS, COLS = 5, 9
GRID_X_OFFSET, GRID_Y_OFFSET = 0, 200
CELL_WIDTH = SCREEN_WIDTH // COLS
CELL_HEIGHT = (SCREEN_HEIGHT - GRID_Y_OFFSET) // ROWS

# Font
FONT = pygame.font.SysFont(None, 36)
BUTTON_FONT = pygame.font.SysFont(None, 30)

# Game States
MAIN_MENU = 'main_menu'
SHOP = 'shop'
GAME = 'game'

# Frame rate
FPS = 60
CLOCK = pygame.time.Clock()

class Button:
    def __init__(self, text, x, y, width, height, callback, color=GREY, hover_color=WHITE):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.hovered = False
        self.text_surf = BUTTON_FONT.render(self.text, True, BLACK)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, surface):
        current_color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        surface.blit(self.text_surf, self.text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.callback()

class Plant(pygame.sprite.Sprite):
    def __init__(self, x, y, plant_type):
        super().__init__()
        self.plant_type = plant_type
        self.image = pygame.Surface((CELL_WIDTH - 10, CELL_HEIGHT - 10))
        if self.plant_type == "shooter":
            self.image.fill(GREEN)
        elif self.plant_type == "wall":
            self.image.fill(BROWN)
        self.rect = self.image.get_rect(topleft=(x + 5, y + 5))
        self.health = 100
        self.cooldown = 0
        if self.plant_type == "shooter":
            self.shot_cooldown = 50

    def update(self, peas):
        if self.plant_type == "shooter":
            self.shoot(peas)

    def shoot(self, peas):
        if self.plant_type == "shooter" and self.cooldown == 0:
            pea = Pea(self.rect.centerx, self.rect.centery)
            peas.add(pea)
            self.cooldown = self.shot_cooldown
        if self.cooldown > 0:
            self.cooldown -= 1

class Pea(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (5,5), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > SCREEN_WIDTH:
            self.kill()

class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y, slow=False):
        super().__init__()
        self.width, self.height = 40, CELL_HEIGHT - 20
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(DARK_RED)
        self.rect = self.image.get_rect(topleft=(x, y + 10))
        self.health = 100
        self.speed = 1 if slow else random.choice([1, 2])
        self.max_health = self.health

    def update(self):
        self.rect.x -= self.speed
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self, surface):
        bar_width = self.width
        bar_height = 5
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 10, fill, bar_height)
        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, BLACK, outline_rect, 1)

class Game:
    def __init__(self):
        self.game_state = MAIN_MENU
        self.sun_points = 150
        self.selected_plant = "shooter"
        self.spawn_timer = 0
        self.zombies_spawned = 0

        self.plants_group = pygame.sprite.Group()
        self.peas_group = pygame.sprite.Group()
        self.zombies_group = pygame.sprite.Group()

        # Buttons
        self.main_menu_buttons = [
            Button("Start Game", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 60, 200, 50, self.start_game),
            Button("Shop", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 50, self.open_shop),
            Button("Exit", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 60, 200, 50, self.exit_game)
        ]

        self.shop_buttons = [
            Button("Shooter - 50 Sun", SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 60, 300, 50, self.select_shooter),
            Button("Wall - 75 Sun", SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2, 300, 50, self.select_wall),
            Button("Back to Menu", SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 60, 300, 50, self.back_to_menu)
        ]

    def start_game(self):
        self.game_state = GAME
        self.reset_game()

    def open_shop(self):
        self.game_state = SHOP

    def exit_game(self):
        pygame.quit()
        sys.exit()

    def back_to_menu(self):
        self.game_state = MAIN_MENU

    def select_shooter(self):
        self.selected_plant = "shooter"

    def select_wall(self):
        self.selected_plant = "wall"

    def reset_game(self):
        self.plants_group.empty()
        self.peas_group.empty()
        self.zombies_group.empty()
        self.sun_points = 150
        self.selected_plant = "shooter"
        self.spawn_timer = 0
        self.zombies_spawned = 0

    def run(self):
        running = True
        while running:
            CLOCK.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_events(event)

            self.update()
            self.draw()

        pygame.quit()

    def handle_events(self, event):
        if self.game_state == MAIN_MENU:
            for button in self.main_menu_buttons:
                button.handle_event(event)
        elif self.game_state == SHOP:
            for button in self.shop_buttons:
                button.handle_event(event)
        elif self.game_state == GAME:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                if mouse_y >= GRID_Y_OFFSET:
                    grid_x = mouse_x // CELL_WIDTH
                    grid_y = (mouse_y - GRID_Y_OFFSET) // CELL_HEIGHT
                    cell_x = grid_x * CELL_WIDTH
                    cell_y = grid_y * CELL_HEIGHT + GRID_Y_OFFSET

                    # Check if cell is free
                    if not any(p.rect.topleft == (cell_x + 5, cell_y + 5) for p in self.plants_group):
                        cost = 50 if self.selected_plant == "shooter" else 75
                        if self.sun_points >= cost:
                            self.plants_group.add(Plant(cell_x, cell_y, self.selected_plant))
                            self.sun_points -= cost

    def update(self):
        if self.game_state == GAME:
            self.plants_group.update(self.peas_group)
            self.peas_group.update()
            self.zombies_group.update()

            self.spawn_timer += 1
            if self.spawn_timer >= 100:
                spawn_y = random.randint(0, ROWS - 1) * CELL_HEIGHT + GRID_Y_OFFSET
                slow = True if self.zombies_spawned < 10 else False
                self.zombies_group.add(Zombie(SCREEN_WIDTH, spawn_y, slow=slow))
                self.zombies_spawned += 1
                self.spawn_timer = 0

            # Use groupcollide for efficient collision detection between peas and zombies
            hits = pygame.sprite.groupcollide(self.peas_group, self.zombies_group, True, False)
            for pea, hit_zombies in hits.items():
                for zombie in hit_zombies:
                    zombie.health -= 10

            # Check game over condition
            for zombie in self.zombies_group:
                if zombie.rect.left <= 0:
                    # Return to main menu and reset game
                    self.game_state = MAIN_MENU
                    self.reset_game()
                    break

    def draw(self):
        if self.game_state == MAIN_MENU:
            SCREEN.fill(SKY_BLUE)
            title_surf = FONT.render("Plants vs. Zombies HD", True, DARK_GREEN)
            title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 150))
            SCREEN.blit(title_surf, title_rect)
            for button in self.main_menu_buttons:
                button.draw(SCREEN)

        elif self.game_state == SHOP:
            SCREEN.fill(SKY_BLUE)
            shop_title = FONT.render("Shop", True, DARK_GREEN)
            shop_title_rect = shop_title.get_rect(center=(SCREEN_WIDTH//2, 100))
            SCREEN.blit(shop_title, shop_title_rect)
            for button in self.shop_buttons:
                button.draw(SCREEN)
            selected_text = FONT.render(f"Selected: {self.selected_plant.capitalize()}", True, BLACK)
            SCREEN.blit(selected_text, (SCREEN_WIDTH//2 - selected_text.get_width()//2, SCREEN_HEIGHT//2 + 130))

        elif self.game_state == GAME:
            SCREEN.fill(SKY_BLUE)
            pygame.draw.rect(SCREEN, GREEN, (0, GRID_Y_OFFSET, SCREEN_WIDTH, SCREEN_HEIGHT - GRID_Y_OFFSET))
            # Grid lines
            for row in range(ROWS + 1):
                pygame.draw.line(SCREEN, WHITE, (0, GRID_Y_OFFSET + row * CELL_HEIGHT), (SCREEN_WIDTH, GRID_Y_OFFSET + row * CELL_HEIGHT))
            for col in range(COLS + 1):
                pygame.draw.line(SCREEN, WHITE, (col * CELL_WIDTH, GRID_Y_OFFSET), (col * CELL_WIDTH, SCREEN_HEIGHT))

            sun_text = FONT.render(f"Sun: {self.sun_points}", True, BLACK)
            SCREEN.blit(sun_text, (10, 10))
            selected_text = FONT.render(f"Selected: {self.selected_plant.capitalize()}", True, BLACK)
            SCREEN.blit(selected_text, (200, 10))

            self.plants_group.draw(SCREEN)
            self.peas_group.draw(SCREEN)
            self.zombies_group.draw(SCREEN)

            # Draw zombie health bars
            for zombie in self.zombies_group:
                zombie.draw_health_bar(SCREEN)

        pygame.display.flip()

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()
