import pygame
import random
from enum import Enum, auto

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60

# Enums for game states and types
class GameMode(Enum):
    TITLE_SCREEN = auto()
    WORLD_MAP = auto()
    LEVEL = auto()
    GAME_OVER = auto()

class PowerUp(Enum):
    NONE = auto()
    MUSHROOM = auto()
    FIRE_FLOWER = auto()

class EnemyType(Enum):
    GOOMBA = auto()
    KOOPA = auto()

# Enemy class
class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.width = 30
        self.height = 30
        self.alive = True
        self.direction = random.choice([-1, 1])

    def move(self):
        speed = 2 if self.type == EnemyType.GOOMBA else 1.5
        self.x += self.direction * speed
        if self.x < 50 or self.x > 550:
            self.direction *= -1

# Item (power-up) class
class Item:
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.type = powerup_type
        self.width = 20
        self.height = 20
        self.collected = False

# Main game class
class SMB3Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Bros. 3")
        self.clock = pygame.time.Clock()

        # Game state
        self.mode = GameMode.TITLE_SCREEN
        self.player_x = 300
        self.player_y = 300
        self.player_vy = 0
        self.on_ground = True
        self.scroll_x = 0
        self.level_length = 3000
        self.coins = 0
        self.lives = 3
        self.world = 1
        self.level = 1
        self.powerup = PowerUp.NONE
        self.invincible = False
        self.invincible_timer = 0

        # Level objects
        self.enemies = []
        self.items = []
        self.flag_x = 2800

        # Colors
        self.colors = {
            'sky': (135, 206, 235),
            'ground': (139, 69, 19),
            'brick': (160, 82, 45),
            'coin': (255, 215, 0),
            'pipe': (0, 128, 0),
            'mario': (255, 0, 0),
            'mario_big': (255, 165, 0),
            'fire': (255, 255, 255),
            'goomba': (165, 42, 42),
            'koopa': (0, 128, 0),
            'mushroom': (255, 0, 0),
            'flower': (255, 165, 0),
            'flag': (255, 255, 255),
            'black': (0, 0, 0),
            'white': (255, 255, 255)
        }

        # Fonts
        self.big_font = pygame.font.SysFont('Helvetica', 36, bold=True)
        self.small_font = pygame.font.SysFont('Helvetica', 20)

        # Start
        self.run()

    def start_level(self):
        self.player_x = 100
        self.player_y = 300
        self.player_vy = 0
        self.scroll_x = 0
        self.on_ground = True
        self.powerup = PowerUp.NONE
        self.invincible = False
        self.invincible_timer = 0
        self.enemies = [
            Enemy(400, 350, EnemyType.GOOMBA),
            Enemy(700, 350, EnemyType.KOOPA),
            Enemy(1200, 350, EnemyType.GOOMBA),
            Enemy(1800, 350, EnemyType.KOOPA)
        ]
        self.items = [
            Item(500, 250, PowerUp.MUSHROOM),
            Item(1500, 250, PowerUp.FIRE_FLOWER)
        ]
        self.flag_x = 2800

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.handle_input()
            self.update(dt)
            self.render()
            pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if self.mode == GameMode.GAME_OVER and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.lives = 3
                    self.coins = 0
                    self.level = 1
                    self.world = 1
                    self.mode = GameMode.TITLE_SCREEN
                elif self.mode == GameMode.TITLE_SCREEN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.mode = GameMode.WORLD_MAP
                elif self.mode == GameMode.WORLD_MAP and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.mode = GameMode.LEVEL
                    self.start_level()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if self.mode == GameMode.WORLD_MAP:
            if keys[pygame.K_RIGHT]: self.player_x = min(self.player_x + 3, 550)
            if keys[pygame.K_LEFT]: self.player_x = max(self.player_x - 3, 50)
            if keys[pygame.K_UP]: self.player_y = max(self.player_y - 3, 50)
            if keys[pygame.K_DOWN]: self.player_y = min(self.player_y + 3, 350)
        elif self.mode == GameMode.LEVEL:
            if keys[pygame.K_RIGHT]:
                self.player_x = min(self.player_x + 5, 550)
                self.scroll_x = min(self.scroll_x + 5, self.level_length - SCREEN_WIDTH)
            if keys[pygame.K_LEFT]:
                self.player_x = max(self.player_x - 5, 50)
                self.scroll_x = max(self.scroll_x - 5, 0)
            if keys[pygame.K_UP] and self.on_ground:
                self.player_vy = -12
                self.on_ground = False

    def update(self, dt):
        if self.mode == GameMode.LEVEL:
            # Gravity
            if not self.on_ground:
                self.player_vy += 0.7
                self.player_y += self.player_vy
                if self.player_y >= 350:
                    self.player_y = 350
                    self.player_vy = 0
                    self.on_ground = True

            # Move enemies
            for enemy in self.enemies:
                if enemy.alive:
                    enemy.move()

            # Invincibility
            if self.invincible:
                self.invincible_timer -= dt
                if self.invincible_timer <= 0:
                    self.invincible = False

            # Enemy collisions
            for enemy in self.enemies:
                if enemy.alive and self.collision(
                    self.player_x, self.player_y, 30, 45,
                    enemy.x - self.scroll_x, enemy.y, enemy.width, enemy.height):
                    if self.invincible:
                        enemy.alive = False
                    elif self.player_vy > 0 and self.player_y < enemy.y:
                        enemy.alive = False
                        self.player_vy = -8
                    else:
                        if self.powerup != PowerUp.NONE:
                            self.powerup = PowerUp.NONE
                            self.invincible = True
                            self.invincible_timer = 2
                        else:
                            self.lives -= 1
                            if self.lives <= 0:
                                self.mode = GameMode.GAME_OVER
                            else:
                                self.start_level()
                            return

            # Item collisions
            for item in self.items:
                if not item.collected and self.collision(
                    self.player_x, self.player_y, 30, 45,
                    item.x - self.scroll_x, item.y, item.width, item.height):
                    item.collected = True
                    if item.type == PowerUp.MUSHROOM:
                        self.powerup = PowerUp.MUSHROOM
                    elif item.type == PowerUp.FIRE_FLOWER:
                        self.powerup = PowerUp.FIRE_FLOWER

            # Coin collection simulation
            for i in range(5):
                coin_x = 120 + i * 200 - self.scroll_x % 200
                if 0 < coin_x < SCREEN_WIDTH and abs(self.player_x - coin_x) < 20 and abs(self.player_y - 220) < 20:
                    self.coins += 1

            # Level end
            if self.player_x + self.scroll_x > self.flag_x:
                self.level += 1
                self.world += (self.level // 4)
                self.level = (self.level - 1) % 4 + 1
                self.mode = GameMode.WORLD_MAP

    def collision(self, x1, y1, w1, h1, x2, y2, w2, h2):
        return (x1 < x2 + w2 and x1 + w1 > x2 and
                y1 < y2 + h2 and y1 + h1 > y2)

    def render(self):
        # Clear screen
        if self.mode in (GameMode.TITLE_SCREEN, GameMode.GAME_OVER):
            self.screen.fill(self.colors['black'])
        else:
            self.screen.fill(self.colors['sky'])

        if self.mode == GameMode.TITLE_SCREEN:
            self.render_title_screen()
        elif self.mode == GameMode.WORLD_MAP:
            self.render_world_map()
        elif self.mode == GameMode.LEVEL:
            self.render_level()
        elif self.mode == GameMode.GAME_OVER:
            self.render_game_over()

        self.render_hud()

    def render_title_screen(self):
        title_surf = self.big_font.render("SUPER MARIO BROS. 3", True, self.colors['white'])
        prompt_surf = self.small_font.render("Press START", True, self.colors['white'])
        self.screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 100))
        self.screen.blit(prompt_surf, (SCREEN_WIDTH//2 - prompt_surf.get_width()//2, 200))
        # Mario placeholder
        pygame.draw.rect(self.screen, self.colors['mario'], (280, 250, 40, 50))
        pygame.draw.circle(self.screen, self.colors['mario'], (300, 260), 30)

    def render_world_map(self):
        self.screen.fill((173, 216, 230))  # lightblue
        for i in range(1, 9):
            x = 50 + i * 60
            y = 100 + (i % 3) * 100
            pygame.draw.circle(self.screen, (0, 255, 0), (x, y), 20)
            text_surf = self.small_font.render(str(i), True, self.colors['black'])
            self.screen.blit(text_surf, (x - text_surf.get_width()//2, y - text_surf.get_height()//2))
        pygame.draw.circle(self.screen, self.colors['mario'], (self.player_x, self.player_y), 15)

    def render_level(self):
        # Background & ground
        self.screen.fill(self.colors['sky'])
        pygame.draw.rect(self.screen, self.colors['ground'], (0, 300, SCREEN_WIDTH, 100))

        # Platforms & coins
        for i in range(5):
            x = 100 + i * 200 - self.scroll_x % 200
            if -50 < x < SCREEN_WIDTH+50:
                pygame.draw.rect(self.screen, self.colors['brick'], (x, 250, 100, 10))
                pygame.draw.circle(self.screen, self.colors['coin'], (int(x+50), 230), 10)

        # Pipes
        for i in range(3):
            x = 300 + i * 300 - self.scroll_x % 300
            if -50 < x < SCREEN_WIDTH+50:
                pygame.draw.rect(self.screen, self.colors['pipe'], (x, 260, 60, 40))
                pygame.draw.rect(self.screen, self.colors['pipe'], (x-10, 240, 80, 20))

        # Flag
        flag_x = self.flag_x - self.scroll_x
        if 0 < flag_x < SCREEN_WIDTH:
            pygame.draw.rect(self.screen, self.colors['black'], (flag_x, 200, 10, 100))
            pygame.draw.rect(self.screen, self.colors['flag'], (flag_x+10, 200, 30, 30))

        # Items
        for item in self.items:
            if not item.collected:
                ix = item.x - self.scroll_x
                if 0 < ix < SCREEN_WIDTH:
                    color = self.colors['mushroom'] if item.type == PowerUp.MUSHROOM else self.colors['flower']
                    pygame.draw.ellipse(self.screen, color, (ix, item.y, item.width, item.height))

        # Enemies
        for enemy in self.enemies:
            if enemy.alive:
                ex = enemy.x - self.scroll_x
                if 0 < ex < SCREEN_WIDTH:
                    color = self.colors['goomba'] if enemy.type == EnemyType.GOOMBA else self.colors['koopa']
                    pygame.draw.ellipse(self.screen, color, (ex, enemy.y, enemy.width, enemy.height))

        # Player
        color = self.colors['mario']
        if self.powerup == PowerUp.MUSHROOM:
            color = self.colors['mario_big']
        elif self.powerup == PowerUp.FIRE_FLOWER:
            color = self.colors['fire']
        pygame.draw.rect(self.screen, color, (self.player_x-15, self.player_y-30 - (15 if self.powerup!=PowerUp.NONE else 0), 30, 45 + (15 if self.powerup!=PowerUp.NONE else 0)))
        pygame.draw.circle(self.screen, color, (self.player_x, self.player_y-30 - (25 if self.powerup!=PowerUp.NONE else 0)), 20)

        # Invincibility blink
        if self.invincible and (pygame.time.get_ticks()//100) % 2 == 0:
            pygame.draw.rect(self.screen, (255, 255, 0), (self.player_x-20, self.player_y-50, 40, 55), 3)

    def render_game_over(self):
        over_surf = self.big_font.render("GAME OVER", True, self.colors['white'])
        prompt_surf = self.small_font.render("Press START to continue", True, self.colors['white'])
        self.screen.blit(over_surf, (SCREEN_WIDTH//2 - over_surf.get_width()//2, 200))
        self.screen.blit(prompt_surf, (SCREEN_WIDTH//2 - prompt_surf.get_width()//2, 250))

    def render_hud(self):
        pygame.draw.rect(self.screen, self.colors['black'], (0, 0, SCREEN_WIDTH, 30))
        coin_surf = self.small_font.render(f"COINS: {self.coins}", True, self.colors['white'])
        world_surf = self.small_font.render(f"WORLD {self.world}-{self.level}", True, self.colors['white'])
        lives_surf = self.small_font.render(f"LIVES: {self.lives}", True, self.colors['white'])
        self.screen.blit(coin_surf, (10, 5))
        self.screen.blit(world_surf, (SCREEN_WIDTH//2 - world_surf.get_width()//2, 5))
        self.screen.blit(lives_surf, (SCREEN_WIDTH - lives_surf.get_width() - 10, 5))
        if self.powerup == PowerUp.MUSHROOM:
            pu_surf = self.small_font.render("MUSHROOM", True, self.colors['mario_big'])
            self.screen.blit(pu_surf, (110, 5))
        elif self.powerup == PowerUp.FIRE_FLOWER:
            pu_surf = self.small_font.render("FIRE FLOWER", True, self.colors['fire'])
            self.screen.blit(pu_surf, (110, 5))

if __name__ == '__main__':
    SMB3Game()
