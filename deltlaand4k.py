import pygame
import sys

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)

# Player Constants
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAVITY = 0.8
PLAYER_JUMP = -15

# Platform Constants
PLATFORM_COLOR = BROWN
PLATFORM_THICKNESS = 20

# --- Helper Functions ---
def load_level_data(world_index, level_index):
    """
    Returns level data including platforms, enemies, coins, and goal.
    Format: {'platforms': [(x, y, w, h), ...], 'enemies': [(x, y), ...], 'coins': [(x, y), ...], 'goal': (x, y, w, h)}
    """
    print(f"Loading World {world_index+1}, Level {level_index+1}")
    if world_index == 0 and level_index == 0:
        platforms = [
            (0, SCREEN_HEIGHT - PLATFORM_THICKNESS, SCREEN_WIDTH * 2, PLATFORM_THICKNESS),  # Ground
            (200, SCREEN_HEIGHT - 100, 100, PLATFORM_THICKNESS),
            (400, SCREEN_HEIGHT - 200, 150, PLATFORM_THICKNESS),
            (600, SCREEN_HEIGHT - 300, 50, PLATFORM_THICKNESS),
            (50, SCREEN_HEIGHT - 400, 100, 80),
        ]
        enemies = [
            (300, SCREEN_HEIGHT - PLATFORM_THICKNESS),  # On ground
            (450, SCREEN_HEIGHT - 200),                 # On platform
        ]
        coins = [
            (100, SCREEN_HEIGHT - 50),   # Above ground
            (250, SCREEN_HEIGHT - 130),  # Above platform
        ]
        goal = (1550, SCREEN_HEIGHT - 200, 10, 200)  # Flagpole at level end
        return {'platforms': platforms, 'enemies': enemies, 'coins': coins, 'goal': goal}
    else:
        # Default level with ground only
        platforms = [(0, SCREEN_HEIGHT - PLATFORM_THICKNESS, SCREEN_WIDTH * 2, PLATFORM_THICKNESS)]
        return {'platforms': platforms, 'enemies': [], 'coins': [], 'goal': None}

# --- Classes ---
class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((30, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.pos = pygame.math.Vector2(self.rect.midbottom)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.on_ground = False

    def jump(self):
        if self.on_ground:
            self.vel.y = PLAYER_JUMP
            self.on_ground = False

    def update(self):
        self.acc = pygame.math.Vector2(0, PLAYER_GRAVITY)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.acc.x = -PLAYER_ACC
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.acc.x = PLAYER_ACC
        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((20, 20))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)
        self.pos = pygame.math.Vector2(self.rect.midbottom)
        self.vel = pygame.math.Vector2(2, 0)  # Moves right initially
        self.acc = pygame.math.Vector2(0, PLAYER_GRAVITY)
        self.on_ground = False

    def update(self):
        self.vel += self.acc
        # Horizontal movement
        self.rect.x += self.vel.x
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        for hit in hits:
            if self.vel.x > 0:
                self.rect.right = hit.rect.left
                self.vel.x = -abs(self.vel.x)  # Reverse direction
            elif self.vel.x < 0:
                self.rect.left = hit.rect.right
                self.vel.x = abs(self.vel.x)
        # Vertical movement
        self.rect.y += self.vel.y
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        for hit in hits:
            if self.vel.y > 0:
                self.rect.bottom = hit.rect.top
                self.on_ground = True
                self.vel.y = 0
            elif self.vel.y < 0:
                self.rect.top = hit.rect.bottom
                self.vel.y = 0
        self.pos = pygame.math.Vector2(self.rect.centerx, self.rect.bottom)

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=PLATFORM_COLOR):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mario Forever CE 2025")
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_world = 0
        self.current_level = 0
        self.font = pygame.font.SysFont(None, 30)
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.goals = pygame.sprite.Group()
        self.player = None
        self.camera_offset_x = 0
        self.level_width = 0
        self.level_completed = False

    def new_level(self):
        self.all_sprites.empty()
        self.platforms.empty()
        self.enemies.empty()
        self.coins.empty()
        self.goals.empty()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        level_data = load_level_data(self.current_world, self.current_level)
        self.level_width = 0
        for plat_data in level_data['platforms']:
            p = Platform(*plat_data)
            self.all_sprites.add(p)
            self.platforms.add(p)
            right_edge = plat_data[0] + plat_data[2]
            if right_edge > self.level_width:
                self.level_width = right_edge
        for enemy_pos in level_data['enemies']:
            e = Enemy(self, *enemy_pos)
            self.all_sprites.add(e)
            self.enemies.add(e)
        for coin_pos in level_data['coins']:
            c = Coin(*coin_pos)
            self.all_sprites.add(c)
            self.coins.add(c)
        goal_data = level_data.get('goal')
        if goal_data:
            g = Goal(*goal_data)
            self.all_sprites.add(g)
            self.goals.add(g)
        self.camera_offset_x = 0
        print(f"Starting World {self.current_world + 1} - Level {self.current_level + 1}")

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    self.player.jump()
                if event.key == pygame.K_ESCAPE:
                    self.playing = False
                    self.running = False
                if event.key == pygame.K_n:  # Debug: next level
                    self.current_level += 1
                    if self.current_level >= 5:
                        self.current_level = 0
                        self.current_world += 1
                        if self.current_world >= 8:
                            self.current_world = 0
                            print("You beat the game structure!")
                    self.new_level()

    def update(self):
        self.all_sprites.update()
        # Player horizontal movement
        new_pos_x = self.player.pos.x + self.player.vel.x + 0.5 * self.player.acc.x
        self.player.rect.x = round(new_pos_x) - self.player.rect.width // 2
        hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
        for hit in hits:
            if self.player.vel.x > 0:
                self.player.rect.right = hit.rect.left
                self.player.vel.x = 0
            elif self.player.vel.x < 0:
                self.player.rect.left = hit.rect.right
                self.player.vel.x = 0
            new_pos_x = self.player.rect.centerx
        # Player vertical movement
        self.player.on_ground = False
        new_pos_y = self.player.pos.y + self.player.vel.y + 0.5 * self.player.acc.y
        self.player.rect.y = round(new_pos_y) - self.player.rect.height
        hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
        for hit in hits:
            if self.player.vel.y > 0:
                self.player.rect.bottom = hit.rect.top
                self.player.on_ground = True
                self.player.vel.y = 0
            elif self.player.vel.y < 0:
                self.player.rect.top = hit.rect.bottom
                self.player.vel.y = 0
            new_pos_y = self.player.rect.bottom
        self.player.pos = pygame.math.Vector2(new_pos_x, new_pos_y)
        # Camera
        target_camera_x = self.player.rect.centerx - SCREEN_WIDTH / 4
        self.camera_offset_x += (target_camera_x - self.camera_offset_x) * 0.1
        self.camera_offset_x = max(0, min(self.camera_offset_x, max(0, self.level_width - SCREEN_WIDTH)))
        # Fall off check
        if self.player.rect.top > SCREEN_HEIGHT:
            print("Fell off!")
            self.new_level()
            return
        # Enemy collisions
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemy_hits:
            if self.player.rect.bottom <= enemy.rect.top + 5:
                enemy.kill()
            else:
                print("Player hit by enemy!")
                self.new_level()
                return
        # Coin collisions
        coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
        for coin in coin_hits:
            print("Coin collected!")
        # Goal collision
        if pygame.sprite.spritecollide(self.player, self.goals, False):
            print("Level completed!")
            self.level_completed = True
            self.playing = False

    def draw(self):
        self.screen.fill(BLUE)
        for sprite in self.all_sprites:
            draw_rect = sprite.rect.copy()
            draw_rect.x -= self.camera_offset_x
            self.screen.blit(sprite.image, draw_rect)
        debug_text = f"Pos: ({int(self.player.pos.x)}, {int(self.player.pos.y)}) " \
                     f"Vel: ({self.player.vel.x:.2f}, {self.player.vel.y:.2f}) " \
                     f"Cam: {int(self.camera_offset_x)}"
        debug_surf = self.font.render(debug_text, True, WHITE)
        self.screen.blit(debug_surf, (10, 10))
        level_text = f"W {self.current_world + 1} - L {self.current_level + 1}"
        level_surf = self.font.render(level_text, True, WHITE)
        self.screen.blit(level_surf, (SCREEN_WIDTH - 150, 10))
        pygame.display.flip()

    def show_start_screen(self):
        self.screen.fill(BLACK)
        title_text = self.font.render("Mario Forever Community Edition", True, WHITE)
        instr_text = self.font.render("Press any key to start!", True, WHITE)
        self.screen.blit(title_text, (SCREEN_WIDTH / 2 - title_text.get_width() / 2, SCREEN_HEIGHT / 3))
        self.screen.blit(instr_text, (SCREEN_WIDTH / 2 - instr_text.get_width() / 2, SCREEN_HEIGHT / 2))
        pygame.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        if not self.running:
            return
        self.screen.fill(BLACK)
        go_text = self.font.render("Game Over!", True, RED)
        instr_text = self.font.render("Press any key to play again!", True, WHITE)
        self.screen.blit(go_text, (SCREEN_WIDTH / 2 - go_text.get_width() / 2, SCREEN_HEIGHT / 3))
        self.screen.blit(instr_text, (SCREEN_WIDTH / 2 - instr_text.get_width() / 2, SCREEN_HEIGHT / 2))
        pygame.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS / 2)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP:
                    waiting = False

# --- Main Execution ---
if __name__ == '__main__':
    g = Game()
    g.show_start_screen()
    while g.running:
        g.new_level()
        g.run()
        if g.level_completed:
            g.level_completed = False
            g.current_level += 1
            if g.current_level >= 5:
                g.current_level = 0
                g.current_world += 1
                if g.current_world >= 8:
                    print("You beat the game!")
                    g.running = False
        else:
            g.show_go_screen()
    print("Game closed!")
    pygame.quit()
    sys.exit()
