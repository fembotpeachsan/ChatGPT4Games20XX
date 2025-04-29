import pygame
import sys
import random

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 600, 400
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
ORANGE = (255, 165, 0)

# Game States
MAIN_MENU = 0
PLAYING = 1
GAME_OVER = 2
current_state = MAIN_MENU

# Physics
GRAVITY = 0.8
JUMP_STRENGTH = -12
TILE_SIZE = 20
PLATFORM_HEIGHT = 10

# Player Stats
PLAYER_SPEED = 3
MAX_LIVES = 3

# Fonts
FONT = pygame.font.SysFont("comicsansms", 20)

def draw_text(text, color, x, y):
    label = FONT.render(text, True, color)
    SCREEN.blit(label, (x, y))

class Button:
    def __init__(self, text, x, y):
        self.rect = pygame.Rect(x, y, 150, 40)
        self.text = text
        self.color = RED
    
    def draw(self):
        pygame.draw.rect(SCREEN, self.color, self.rect)
        draw_text(self.text, WHITE, self.rect.x + 20, self.rect.y + 10)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE * 2)
        self.velocity_y = 0
        self.on_ground = False
        self.lives = MAX_LIVES
        self.score = 0

    def update(self, keys, platforms, enemies, coins, pows):
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED

        # Screen wrapping
        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif self.rect.left > WIDTH:
            self.rect.right = 0

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = JUMP_STRENGTH
            self.on_ground = False

        # Gravity
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Platform collisions
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.velocity_y > 0 and self.rect.bottom <= plat.rect.bottom:
                    self.rect.bottom = plat.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0 and self.rect.top >= plat.rect.top:
                    self.rect.top = plat.rect.bottom
                    self.velocity_y = 0
                    # Flip enemies on this platform
                    for enemy in enemies:
                        if abs(enemy.rect.bottom - plat.rect.top) < 5:
                            enemy.flip()

        # POW block collision
        for pow in pows:
            if self.rect.colliderect(pow.rect) and self.velocity_y < 0:
                if self.rect.top < pow.rect.bottom:
                    pow.hit(enemies)
                    self.velocity_y = 0

        # Enemy collision
        for enemy in enemies[:]:
            if self.rect.colliderect(enemy.rect):
                if enemy.state == "flipped":
                    enemies.remove(enemy)
                    self.score += 100
                else:
                    self.lives -= 1
                    self.respawn(platforms)

        # Coin collision
        for coin in coins[:]:
            if self.rect.colliderect(coin.rect):
                coins.remove(coin)
                self.score += 10

    def respawn(self, platforms):
        self.rect.x = WIDTH // 2
        self.rect.y = HEIGHT - TILE_SIZE * 4
        self.velocity_y = 0
        self.on_ground = True

class Enemy:
    def __init__(self, x, y, direction=1):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.direction = direction
        self.speed = 2
        self.state = "normal"  # normal, flipped
        self.flip_timer = 0
        self.velocity_y = 0
        self.on_ground = False

    def update(self, platforms):
        if self.state == "normal":
            # Horizontal movement
            self.rect.x += self.direction * self.speed

            # Gravity
            self.velocity_y += GRAVITY
            self.rect.y += self.velocity_y

            # Platform collisions
            self.on_ground = False
            for plat in platforms:
                if self.rect.colliderect(plat.rect):
                    if self.velocity_y > 0 and self.rect.bottom <= plat.rect.bottom:
                        self.rect.bottom = plat.rect.top
                        self.velocity_y = 0
                        self.on_ground = True
                    elif self.velocity_y < 0 and self.rect.top >= plat.rect.top:
                        self.rect.top = plat.rect.bottom
                        self.velocity_y = 0

            # Screen wrapping
            if self.rect.right < 0:
                self.rect.left = WIDTH
            elif self.rect.left > WIDTH:
                self.rect.right = 0

            # Fall off bottom, reappear at top
            if self.rect.top > HEIGHT:
                self.rect.bottom = 50
                self.rect.x = random.choice([50, 520])  # Pipe positions

        elif self.state == "flipped":
            self.flip_timer += 1
            if self.flip_timer > 180:  # 3 seconds at 60 FPS
                self.state = "normal"
                self.flip_timer = 0

    def flip(self):
        if self.state == "normal":
            self.state = "flipped"
            self.flip_timer = 0

class POW:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.hits_left = 3

    def hit(self, enemies):
        if self.hits_left > 0:
            for enemy in enemies:
                enemy.flip()
            self.hits_left -= 1

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE // 2, TILE_SIZE // 2)

class Platform:
    def __init__(self, x, y, width, height=PLATFORM_HEIGHT):
        self.rect = pygame.Rect(x, y, width, height)

def main_menu():
    global current_state
    play_button = Button("Start Game", WIDTH // 2 - 75, HEIGHT // 2 - 50)
    quit_button = Button("Quit", WIDTH // 2 - 75, HEIGHT // 2 + 20)
    while current_state == MAIN_MENU:
        SCREEN.fill(BLACK)
        draw_text("MARIO BROS ARCADE", WHITE, 180, 100)
        play_button.draw()
        quit_button.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if play_button.is_clicked(pos):
                    current_state = PLAYING
                if quit_button.is_clicked(pos):
                    pygame.quit()
                    sys.exit()
        pygame.display.update()
        CLOCK.tick(FPS)

def game_over_screen(player):
    global current_state
    restart_button = Button("Restart", WIDTH // 2 - 75, HEIGHT // 2 - 50)
    menu_button = Button("Main Menu", WIDTH // 2 - 75, HEIGHT // 2 + 20)
    while current_state == GAME_OVER:
        SCREEN.fill(BLACK)
        draw_text("GAME OVER", RED, WIDTH // 2 - 80, HEIGHT // 2 - 100)
        draw_text(f"Score: {player.score}", WHITE, WIDTH // 2 - 60, HEIGHT // 2 - 70)
        restart_button.draw()
        menu_button.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if restart_button.is_clicked(pos):
                    run_game()
                if menu_button.is_clicked(pos):
                    current_state = MAIN_MENU
        pygame.display.update()
        CLOCK.tick(FPS)

def run_game():
    global current_state
    # Updated level layout with two levels of platforms
    platforms = [
        Platform(0, 360, 600, 40),      # Bottom floor
        Platform(50, 280, 200, 10),     # First level left
        Platform(350, 280, 200, 10),    # First level right
        Platform(50, 180, 200, 10),     # Second level left
        Platform(350, 180, 200, 10),    # Second level right
    ]
    coins = [
        Coin(100, 270),  # On first level left
        Coin(500, 270),  # On first level right
        Coin(100, 170),  # On second level left
        Coin(500, 170),  # On second level right
    ]
    enemies = []
    pows = [POW(285, 200)]  # Center of screen
    player = Player(WIDTH // 2, HEIGHT - TILE_SIZE * 4)
    spawn_timer = 0
    max_enemies = 5

    while current_state == PLAYING:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Spawn enemies from pipes
        spawn_timer += 1
        if spawn_timer >= 300 and len(enemies) < max_enemies:  # Every 5 seconds
            spawn_timer = 0
            pipe_x = random.choice([50, 520])
            enemies.append(Enemy(pipe_x, 50))

        # Update
        player.update(keys, platforms, enemies, coins, pows)
        for enemy in enemies:
            enemy.update(platforms)

        # Check game over
        if player.lives <= 0:
            current_state = GAME_OVER

        # Draw
        SCREEN.fill(BLACK)
        draw_pipes()
        for plat in platforms:
            pygame.draw.rect(SCREEN, GRAY, plat.rect)
        for coin in coins:
            draw_coin(coin)
        for enemy in enemies:
            draw_enemy(enemy)
        for pow in pows:
            draw_pow(pow)
        draw_player(player)
        draw_text(f"Lives: {player.lives}", WHITE, 10, 10)
        draw_text(f"Score: {player.score}", WHITE, 10, 40)
        pygame.display.update()
        CLOCK.tick(FPS)

def draw_pipes():
    pygame.draw.rect(SCREEN, GREEN, (50, 50, 30, 50))   # Left pipe
    pygame.draw.rect(SCREEN, GREEN, (520, 50, 30, 50))  # Right pipe

def draw_player(player):
    pygame.draw.rect(SCREEN, RED, player.rect)  # Body
    hat_rect = pygame.Rect(player.rect.x + 5, player.rect.y - 10, 10, 10)
    pygame.draw.rect(SCREEN, BLUE, hat_rect)    # Hat

def draw_enemy(enemy):
    color = YELLOW if enemy.state == "flipped" else GREEN
    pygame.draw.rect(SCREEN, color, enemy.rect)

def draw_coin(coin):
    pygame.draw.circle(SCREEN, YELLOW, coin.rect.center, 5)

def draw_pow(pow):
    pygame.draw.rect(SCREEN, BLUE, pow.rect)
    draw_text("POW", WHITE, pow.rect.x + 5, pow.rect.y + 5)

if __name__ == "__main__":
    while True:
        if current_state == MAIN_MENU:
            main_menu()
        elif current_state == PLAYING:
            run_game()
        elif current_state == GAME_OVER:
            game_over_screen(None)
