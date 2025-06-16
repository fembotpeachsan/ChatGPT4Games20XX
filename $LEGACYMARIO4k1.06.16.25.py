import pygame
import sys

# Initialize Pygame
pygame.init()

# Configuration
FPS = 60
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SMB1-Inspired Pygame Game")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)

# Scene base class
class Scene:
    def __init__(self, app):
        self.app = app

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self):
        pass

# Level Select Scene
class LevelSelectScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.buttons = []
        self._create_level_buttons()

    def _create_level_buttons(self):
        levels = [(w, l) for w in range(1, 9) for l in range(1, 5)]  # 32 levels
        cols, rows = 8, 4
        btn_width, btn_height = 80, 40
        padding_x, padding_y = 20, 20

        for idx, (world, level) in enumerate(levels):
            col = idx % cols
            row = idx // cols
            x = padding_x + col * (btn_width + padding_x)
            y = padding_y + row * (btn_height + padding_y)
            rect = pygame.Rect(x, y, btn_width, btn_height)
            self.buttons.append((rect, f"{world}-{level}"))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for rect, level_str in self.buttons:
                if rect.collidepoint(pos):
                    self.app.switch_to(GameplayScene(self.app, level_str))

    def draw(self):
        screen.fill(BLACK)
        font = pygame.font.Font(None, 36)
        for rect, level_str in self.buttons:
            pygame.draw.rect(screen, BLUE, rect)
            text = font.render(level_str, True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

# Gameplay Scene
class GameplayScene(Scene):
    TILE_SIZE = 32

    def __init__(self, app, level_key):
        super().__init__(app)
        self.player_x = 100
        self.player_y = HEIGHT - 100
        self.player_width = 20
        self.player_height = 30
        self.player_vel_x = 0
        self.player_vel_y = 0
        self.gravity = 0.5
        self.jump_speed = -10
        self.speed = 5
        self.level_key = level_key
        # Simple hardcoded level data (replace with real SMB1 data if available)
        self.level_data = [
            {"x": 0, "y": HEIGHT // self.TILE_SIZE - 1, "type": 0, "val": 25},  # Ground
            {"x": 5, "y": HEIGHT // self.TILE_SIZE - 3, "type": 1, "val": 1},   # Block
            {"x": 10, "y": HEIGHT // self.TILE_SIZE - 3, "type": 1, "val": 1},  # Block
        ]

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.app.switch_to(LevelSelectScene(self.app))
            elif event.key == pygame.K_LEFT:
                self.player_vel_x = -self.speed
            elif event.key == pygame.K_RIGHT:
                self.player_vel_x = self.speed
            elif event.key == pygame.K_SPACE and self.player_y + self.player_height >= HEIGHT - self.TILE_SIZE:
                self.player_vel_y = self.jump_speed
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.player_vel_x = 0

    def update(self):
        # Update player position
        self.player_vel_y += self.gravity
        self.player_x += self.player_vel_x
        self.player_y += self.player_vel_y

        # Collision with ground
        ground_y = HEIGHT - self.TILE_SIZE
        if self.player_y + self.player_height > ground_y:
            self.player_y = ground_y - self.player_height
            self.player_vel_y = 0

        # Keep player within screen bounds
        if self.player_x < 0:
            self.player_x = 0
        elif self.player_x + self.player_width > WIDTH:
            self.player_x = WIDTH - self.player_width

    def draw(self):
        screen.fill(BLACK)
        # Draw level objects
        for obj in self.level_data:
            x, y = obj["x"] * self.TILE_SIZE, obj["y"] * self.TILE_SIZE
            if obj["type"] == 0:  # Ground
                pygame.draw.rect(screen, BROWN, (x, y, self.TILE_SIZE * obj["val"], self.TILE_SIZE))
            elif obj["type"] == 1:  # Block
                pygame.draw.rect(screen, BROWN, (x, y, self.TILE_SIZE, self.TILE_SIZE))
        # Draw player
        pygame.draw.rect(screen, WHITE, (self.player_x, self.player_y, self.player_width, self.player_height))
        # Display level key
        font = pygame.font.Font(None, 36)
        text = font.render(f"Level: {self.level_key}", True, WHITE)
        screen.blit(text, (10, 10))

# Application class
class App:
    def __init__(self):
        self.current_scene = None
        self.switch_to(LevelSelectScene(self))

    def switch_to(self, scene):
        self.current_scene = scene

    def run(self):
        while True:
            for event in pygame.event.get():
                self.current_scene.handle_event(event)

            self.current_scene.update()
            self.current_scene.draw()
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    app = App()
    app.run()
