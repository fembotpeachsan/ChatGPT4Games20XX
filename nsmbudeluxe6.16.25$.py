import pygame
import asyncio
import platform
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
        self.selected_index = 0
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
            elif event.key == pygame.K_RIGHT:
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
            elif event.key == pygame.K_LEFT:
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                _, level_str = self.buttons[self.selected_index]
                self.app.switch_to(GameplayScene(self.app, level_str))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for i, (rect, level_str) in enumerate(self.buttons):
                if rect.collidepoint(pos):
                    self.selected_index = i
                    self.app.switch_to(GameplayScene(self.app, level_str))

    def draw(self):
        screen.fill(BLACK)
        font = pygame.font.Font(None, 36)
        for i, (rect, level_str) in enumerate(self.buttons):
            color = WHITE if i == self.selected_index else BLUE
            pygame.draw.rect(screen, color, rect)
            text = font.render(level_str, True, BLACK if i == self.selected_index else WHITE)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

# Gameplay Scene
class GameplayScene(Scene):
    TILE_SIZE = 32

    def __init__(self, app, level_key):
        super().__init__(app)
        self.level_key = level_key
        self.player_x = 50
        self.player_y = HEIGHT - 50
        self.player_width = 20
        self.player_height = 30
        self.player_vel_x = 0
        self.player_vel_y = 0
        self.gravity = 0.5
        self.jump_speed = -10
        self.speed = 5
        self.level_data = self._generate_level_data()

    def _generate_level_data(self):
        # Simple level data: ground and some blocks
        ground = [{"x": 0, "y": HEIGHT // self.TILE_SIZE - 1, "type": "ground", "width": 25}]
        blocks = [
            {"x": 5, "y": HEIGHT // self.TILE_SIZE - 3, "type": "block"},
            {"x": 10, "y": HEIGHT // self.TILE_SIZE - 3, "type": "block"},
            {"x": 15, "y": HEIGHT // self.TILE_SIZE - 3, "type": "block"},
        ]
        return ground + blocks  # For simplicity, all levels use the same data

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
            elif event.key == pygame.K_SPACE and self.is_on_ground():
                self.player_vel_y = self.jump_speed
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.player_vel_x = 0

    def update(self):
        # Apply gravity and update position
        self.player_vel_y += self.gravity
        self.player_x += self.player_vel_x
        self.player_y += self.player_vel_y

        # Collision with ground and blocks
        for obj in self.level_data:
            if obj["type"] == "ground":
                ground_y = obj["y"] * self.TILE_SIZE
                if self.player_y + self.player_height > ground_y:
                    self.player_y = ground_y - self.player_height
                    self.player_vel_y = 0
            elif obj["type"] == "block":
                block_rect = pygame.Rect(obj["x"] * self.TILE_SIZE, obj["y"] * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)
                player_rect = pygame.Rect(self.player_x, self.player_y, self.player_width, self.player_height)
                if player_rect.colliderect(block_rect):
                    # Simple collision resolution
                    if self.player_vel_y > 0:  # Falling
                        self.player_y = block_rect.top - self.player_height
                        self.player_vel_y = 0
                    elif self.player_vel_y < 0:  # Jumping
                        self.player_y = block_rect.bottom
                        self.player_vel_y = 0

        # Keep player within screen bounds
        if self.player_x < 0:
            self.player_x = 0
        elif self.player_x + self.player_width > WIDTH:
            self.player_x = WIDTH - self.player_width

        # Win condition
        if self.player_x > 700:
            self.app.switch_to(LevelSelectScene(self.app))

    def draw(self):
        screen.fill(BLACK)
        # Draw level objects
        for obj in self.level_data:
            if obj["type"] == "ground":
                pygame.draw.rect(screen, BROWN, (obj["x"] * self.TILE_SIZE, obj["y"] * self.TILE_SIZE, obj["width"] * self.TILE_SIZE, self.TILE_SIZE))
            elif obj["type"] == "block":
                pygame.draw.rect(screen, BROWN, (obj["x"] * self.TILE_SIZE, obj["y"] * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE))
        # Draw player
        pygame.draw.rect(screen, WHITE, (self.player_x, self.player_y, self.player_width, self.player_height))
        # Display level key
        font = pygame.font.Font(None, 36)
        text = font.render(f"Level: {self.level_key}", True, WHITE)
        screen.blit(text, (10, 10))

    def is_on_ground(self):
        for obj in self.level_data:
            if obj["type"] == "ground":
                ground_y = obj["y"] * self.TILE_SIZE
                if abs(self.player_y + self.player_height - ground_y) < 5:
                    return True
        return False

# Application class
class App:
    def __init__(self):
        self.current_scene = None
        self.switch_to(LevelSelectScene(self))

    def switch_to(self, scene):
        self.current_scene = scene

    def update_loop(self):
        for event in pygame.event.get():
            self.current_scene.handle_event(event)
        self.current_scene.update()
        self.current_scene.draw()
        pygame.display.flip()

    def setup(self):
        pass  # Initialization if needed

# Main game loop
async def main():
    app = App()
    app.setup()
    while True:
        app.update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
