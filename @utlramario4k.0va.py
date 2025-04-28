import asyncio
import platform
import pygame
import sys

# Constants
WIDTH, HEIGHT = 600, 400
FPS = 60

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)

# World colors (background, platform)
world_colors = {
    1: (BLUE, GREEN),
    2: (YELLOW, ORANGE),
    3: (CYAN, BLUE),
    4: (MAGENTA, PURPLE),
    5: (ORANGE, RED),
    6: (GRAY, WHITE),
    7: ((0, 128, 0), GREEN),
    8: (BLACK, RED),
}

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.jump_power = -10
        self.gravity = 0.5
        self.speed = 3

    def update(self, keys, platforms):
        if keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
        else:
            self.vel_x = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

        self.vel_y += self.gravity
        self.rect.x += self.vel_x

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right

        self.rect.y += self.vel_y
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

class Enemy:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.type = type
        self.direction = 1
        self.speed = 2

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.x > 500 or self.rect.x < 100:
            self.direction *= -1

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)

class Platform:
    def __init__(self, x, y, w, h, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Goal:
    def __init__(self, x, y, w, h, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

def get_level_data(world):
    bg_color, platform_color = world_colors.get(world, (BLACK, WHITE))
    platforms = [
        Platform(0, 350, 600, 50, platform_color),  # Ground
        Platform(200, 250, 100, 20, platform_color),
        Platform(400, 200, 100, 20, platform_color),
    ]
    enemies = [
        Enemy(300, 330, 'goomba'),
        Enemy(500, 180, 'goomba'),
    ]
    goal = Goal(550, 318, 20, 32, platform_color)  # On ground
    return bg_color, platforms, enemies, goal

def setup():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SMB3 Inspired Overworld and Levels")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    return screen, clock, font

async def main():
    screen, clock, font = setup()

    world_buttons = [
        {'rect': pygame.Rect(50, 50, 100, 50), 'world': 1},
        {'rect': pygame.Rect(200, 50, 100, 50), 'world': 2},
        {'rect': pygame.Rect(350, 50, 100, 50), 'world': 3},
        {'rect': pygame.Rect(500, 50, 100, 50), 'world': 4},
        {'rect': pygame.Rect(50, 150, 100, 50), 'world': 5},
        {'rect': pygame.Rect(200, 150, 100, 50), 'world': 6},
        {'rect': pygame.Rect(350, 150, 100, 50), 'world': 7},
        {'rect': pygame.Rect(500, 150, 100, 50), 'world': 8},
    ]

    current_state = 'overworld'
    current_world = None
    player = None
    platforms = []
    enemies = []
    goal = None
    bg_color = BLACK

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if current_state == 'overworld':
            screen.fill(BLACK)
            for button in world_buttons:
                pygame.draw.rect(screen, WHITE, button['rect'])
                text = font.render(f"World {button['world']}", True, BLACK)
                screen.blit(text, (button['rect'].x + 10, button['rect'].y + 10))
            pygame.display.flip()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in world_buttons:
                    if button['rect'].collidepoint(event.pos):
                        current_world = button['world']
                        bg_color, platforms, enemies, goal = get_level_data(current_world)
                        player = Player(50, 300)
                        current_state = 'level'
                        break

        elif current_state == 'level':
            keys = pygame.key.get_pressed()
            player.update(keys, platforms)
            for enemy in enemies:
                enemy.update()

            if any(player.rect.colliderect(enemy.rect) for enemy in enemies) or player.rect.y > HEIGHT:
                player.rect.x = 50
                player.rect.y = 300
                player.vel_x = 0
                player.vel_y = 0

            if player.rect.colliderect(goal.rect):
                current_state = 'overworld'

            screen.fill(bg_color)
            for platform in platforms:
                platform.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            goal.draw(screen)
            player.draw(screen)
            pygame.display.flip()

        clock.tick(FPS)
        await asyncio.sleep(0)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
