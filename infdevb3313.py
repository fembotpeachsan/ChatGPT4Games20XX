import pygame
import sys
import math
from enum import Enum
from ursina import Ursina, Entity, camera, held_keys, window, color, application, time


# ------------------------ CORE ENGINE COMPONENTS ------------------------

class FTRender:
    """Placeholder for an advanced renderer."""
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def render(self, surface):
        """Render method without drawing the triangle."""
        pass  # Removed drawing code


class MenuState(Enum):
    """Enumeration for menu states."""
    MAIN = "main"
    CREDITS = "credits"
    PLAYING = "playing"


class MenuItem:
    """Represents a menu item."""
    def __init__(self, text, position, action, font_size=36):
        self.text = text
        self.position = position
        self.action = action
        self.font = pygame.font.Font(None, font_size)
        self.is_selected = False
        self.hover_offset = 0

    def draw(self, surface):
        """Draw the menu item."""
        color = (255, 255, 0) if self.is_selected else (255, 255, 255)
        text_surface = self.font.render(self.text, True, color)
        pos = (self.position[0], self.position[1] + self.hover_offset)
        surface.blit(text_surface, pos)

    def update(self):
        """Animate the menu item when selected."""
        self.hover_offset = -5 * abs(math.sin(pygame.time.get_ticks() * 0.003)) if self.is_selected else 0


class MenuSystem:
    """Handles the menu system."""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = MenuState.MAIN
        self.selected_index = 0

        # Menu items
        self.menu_items = [
            MenuItem("Start Game", (screen_width // 2 - 80, screen_height // 2 - 60),
                     lambda: setattr(self, 'state', MenuState.PLAYING)),
            MenuItem("Credits", (screen_width // 2 - 60, screen_height // 2),
                     lambda: setattr(self, 'state', MenuState.CREDITS)),
            MenuItem("Exit", (screen_width // 2 - 40, screen_height // 2 + 60),
                     lambda: sys.exit())
        ]

        # Title font
        self.title_font = pygame.font.Font(None, 72)

    def update(self):
        """Update the menu state based on user input."""
        keys = pygame.key.get_pressed()
        for item in self.menu_items:
            item.is_selected = False
        self.menu_items[self.selected_index].is_selected = True

        # Handle navigation
        if keys[pygame.K_UP]:
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
        elif keys[pygame.K_DOWN]:
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
        elif keys[pygame.K_RETURN]:
            self.menu_items[self.selected_index].action()

    def draw(self, screen):
        """Draw the menu on the screen."""
        screen.fill((0, 0, 40))
        title_text = self.title_font.render("Super Mario FX Beta", True, (255, 255, 255))
        screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 100))

        for item in self.menu_items:
            item.draw(screen)


# ------------------------ GAMEPLAY AND URSINA ------------------------

def run_ursina_game():
    """Run the 3D Ursina gameplay."""
    print("Starting game engine Ninnt 1.0")
    app = Ursina(borderless=False)
    window.title = "Super Mario FX Beta - 3D Gameplay"
    window.fullscreen = False
    window.size = (800, 600)

    ground = Entity(model='plane', scale=32, color=color.gray)
    player = Entity(model='cube', color=color.orange, scale=1, position=(0, 0.5, 0))

    # Add some 3D objects to the environment
    box1 = Entity(model='cube', color=color.red, scale=1, position=(2, 0.5, 2))
    box2 = Entity(model='cube', color=color.blue, scale=1, position=(-2, 0.5, -2))
    box3 = Entity(model='cube', color=color.green, scale=1, position=(2, 0.5, -2))
    box4 = Entity(model='cube', color=color.yellow, scale=1, position=(-2, 0.5, 2))

    camera.position = (0, 10, -15)
    camera.look_at(player.position)

    def update():
        speed = 5 * time.dt
        if held_keys['w']:
            player.z += speed
        if held_keys['s']:
            player.z -= speed
        if held_keys['a']:
            player.x -= speed
        if held_keys['d']:
            player.x += speed

        if held_keys['escape']:
            application.quit()

    app.run()


# ------------------------ MAIN GAME CLASS ------------------------

class Game:
    """Main game class."""
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Super Mario FX Beta")
        self.clock = pygame.time.Clock()
        self.running = True

        # Components
        self.menu = MenuSystem(self.screen_width, self.screen_height)
        self.renderer = FTRender(self.screen_width, self.screen_height)

    def run(self):
        """Main game loop."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.menu.state == MenuState.PLAYING:
                pygame.display.quit()  # Quit the Pygame window
                pygame.quit()
                run_ursina_game()  # Run the 3D game
                pygame.init()  # Reinitialize Pygame after Ursina ends
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
                pygame.display.set_caption("Super Mario FX Beta")
                self.menu.state = MenuState.MAIN  # Reset to main menu after the game ends

            if self.menu.state == MenuState.MAIN:
                self.menu.update()
                self.menu.draw(self.screen)
                self.renderer.render(self.screen)

            elif self.menu.state == MenuState.CREDITS:
                # Show credits (can expand later)
                self.screen.fill((0, 0, 0))
                credits_font = pygame.font.Font(None, 48)
                credits_text = credits_font.render("Credits: Made by Gemini", True, (255, 255, 255))
                self.screen.blit(credits_text, (self.screen_width // 2 - credits_text.get_width() // 2,
                                                self.screen_height // 2 - 20))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


# ------------------------ ENTRY POINT ------------------------

if __name__ == "__main__":
    game = Game()
    game.run()
