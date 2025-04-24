import pygame

# Initialize Pygame
pygame.init()

# Set up the display (NES-like resolution: 256x240)
SCREEN_WIDTH = 256
SCREEN_HEIGHT = 240
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros. 1 Pygame Clone")

# Colors
SKY_BLUE = (135, 206, 235)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GROUND_COLOR = (139, 69, 19)
BLOCK_COLOR = (128, 128, 128)
QUESTION_COLOR = (255, 255, 0)
EMPTY_BLOCK_COLOR = (169, 169, 169)
COIN_COLOR = (255, 215, 0)
GOOMBA_COLOR = (165, 42, 42)
KOOPA_COLOR = (0, 128, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FLAGPOLE_COLOR = (0, 128, 0)
FLAG_COLOR = (255, 0, 0)
MUSHROOM_COLOR = (255, 165, 0)

# Game constants
TILE_SIZE = 16
PLAYER_WIDTH = 16
ENEMY_SIZE = 16
GRAVITY = 0.35
JUMP_VELOCITY = -6.5
MOVE_SPEED = 2
MAX_SPEED = 3
ACCELERATION = 0.2
FRICTION = 0.15
FPS = 60
LEVEL_TIME = 400  # Seconds

# Tilemap (0=empty, 1=ground, 2=question, 3=brick, 4=empty block)
tilemap = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Question blocks
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # Ground
]

# Game state
class GameState:
    def __init__(self):
        self.time_left = LEVEL_TIME * FPS
        self.lives = 3
        self.score = 0
        self.coins = 0
        self.level_complete = False

# Player class
class Player:
    def __init__(self, x, y):
        self.initial_x = x
        self.initial_y = y
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.width = PLAYER_WIDTH
        self.height = 16
        self.state = 'small'
        self.on_ground = False

    def set_state(self, new_state):
        self.state = new_state
        if new_state == 'big':
            self.height = 32
        else:
            self.height = 16
        if self.on_ground and new_state == 'big':
            self.y -= 16

    def update(self, keys, game_state):
        # Horizontal movement with inertia
        target_vx = 0
        if keys[pygame.K_LEFT]:
            target_vx = -MOVE_SPEED
        if keys[pygame.K_RIGHT]:
            target_vx = MOVE_SPEED

        # Apply acceleration and friction
        if target_vx != 0:
            self.vx += (target_vx - self.vx) * ACCELERATION
        else:
            self.vx *= (1 - FRICTION)
        if abs(self.vx) < 0.1:
            self.vx = 0
        self.vx = max(-MAX_SPEED, min(MAX_SPEED, self.vx))
        self.x += self.vx

        # Jumping
        if keys[pygame.K_UP] and self.on_ground:
            self.vy = JUMP_VELOCITY
            self.on_ground = False

        # Apply gravity
        self.vy += GRAVITY
        self.y += self.vy

        # Collision detection
        self.check_collisions(game_state)

        # Screen bounds
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

        # Death by falling
        if self.y > SCREEN_HEIGHT:
            self.die(game_state)

    def check_collisions(self, game_state):
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for y in range(len(tilemap)):
            for x in range(len(tilemap[y])):
                tile_type = tilemap[y][x]
                if tile_type in [1, 2, 3, 4]:  # Solid tiles
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if player_rect.colliderect(tile_rect):
                        if self.vy > 0 and player_rect.bottom > tile_rect.top:
                            self.y = tile_rect.top - self.height
                            self.vy = 0
                            self.on_ground = True
                        elif self.vy < 0 and player_rect.top < tile_rect.bottom:
                            if tile_type == 2:  # Question block
                                tilemap[y][x] = 4
                                item_x = x * TILE_SIZE
                                item_y = y * TILE_SIZE - TILE_SIZE
                                power_ups.append(PowerUp(item_x, item_y, 'mushroom'))
                                game_state.score += 1000
                            elif tile_type == 3 and self.state == 'big':
                                tilemap[y][x] = 0
                                game_state.score += 50
                            self.y = tile_rect.bottom
                            self.vy = 0
                        elif self.vx > 0 and player_rect.right > tile_rect.left:
                            self.x = tile_rect.left - self.width
                            self.vx = 0
                        elif self.vx < 0 and player_rect.left < tile_rect.right:
                            self.x = tile_rect.right
                            self.vx = 0

    def die(self, game_state):
        game_state.lives -= 1
        if game_state.lives <= 0:
            game_state.level_complete = True  # End game
        else:
            self.x = self.initial_x
            self.y = self.initial_y
            self.vx = 0
            self.vy = 0
            self.state = 'small'
            self.height = 16

    def draw(self):
        if self.state == 'small':
            pygame.draw.rect(screen, BLUE, (self.x, self.y + 8, self.width, 8))  # Overalls
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, 8))  # Shirt
            pygame.draw.rect(screen, RED, (self.x + 4, self.y - 4, 8, 4))  # Hat
        else:
            pygame.draw.rect(screen, BLUE, (self.x, self.y + 16, self.width, 16))  # Overalls
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, 16))  # Shirt
            pygame.draw.rect(screen, RED, (self.x + 4, self.y - 4, 8, 4))  # Hat

# Power-up class
class PowerUp:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.vy = 0
        self.active = True

    def update(self):
        self.vy += GRAVITY
        self.y += self.vy
        self.check_collisions()

    def check_collisions(self):
        power_rect = pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)
        for y in range(len(tilemap)):
            for x in range(len(tilemap[y])):
                if tilemap[y][x] in [1, 4]:
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if power_rect.colliderect(tile_rect) and self.vy > 0:
                        self.y = tile_rect.top - TILE_SIZE
                        self.vy = 0

    def draw(self):
        if self.active:
            if self.type == 'mushroom':
                pygame.draw.rect(screen, MUSHROOM_COLOR, (self.x, self.y + 8, TILE_SIZE, 8))
                pygame.draw.rect(screen, WHITE, (self.x + 4, self.y, 8, 8))

# Coin class
class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 30

    def update(self):
        self.timer -= 1

    def draw(self):
        if self.timer > 0:
            pygame.draw.circle(screen, COIN_COLOR, (int(self.x), int(self.y)), 5)

# Enemy class (Goomba)
class Goomba:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = -1
        self.vy = 0
        self.alive = True

    def update(self):
        if self.alive:
            self.x += self.vx
            if self.x < 0 or self.x > SCREEN_WIDTH - ENEMY_SIZE:
                self.vx = -self.vx
            self.vy += GRAVITY
            self.y += self.vy
            self.check_collisions()

    def check_collisions(self):
        goomba_rect = pygame.Rect(self.x, self.y, ENEMY_SIZE, ENEMY_SIZE)
        for y in range(len(tilemap)):
            for x in range(len(tilemap[y])):
                if tilemap[y][x] in [1, 2, 3, 4]:
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if goomba_rect.colliderect(tile_rect):
                        if self.vy > 0:
                            self.y = tile_rect.top - ENEMY_SIZE
                            self.vy = 0

    def draw(self):
        if self.alive:
            pygame.draw.circle(screen, GOOMBA_COLOR, (int(self.x + ENEMY_SIZE / 2), int(self.y + ENEMY_SIZE / 2)), ENEMY_SIZE // 2)
            pygame.draw.circle(screen, WHITE, (int(self.x + ENEMY_SIZE / 4), int(self.y + ENEMY_SIZE / 3)), 3)
            pygame.draw.circle(screen, BLACK, (int(self.x + ENEMY_SIZE / 4), int(self.y + ENEMY_SIZE / 3)), 1)
            pygame.draw.circle(screen, WHITE, (int(self.x + 3 * ENEMY_SIZE / 4), int(self.y + ENEMY_SIZE / 3)), 3)
            pygame.draw.circle(screen, BLACK, (int(self.x + 3 * ENEMY_SIZE / 4), int(self.y + ENEMY_SIZE / 3)), 1)

# Draw tiles
def draw_tile(x, y, tile_type):
    if tile_type == 1:
        pygame.draw.rect(screen, GROUND_COLOR, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        grass_color = (0, 255, 0)
        for i in range(0, TILE_SIZE, 2):
            pygame.draw.line(screen, grass_color, (x * TILE_SIZE + i, y * TILE_SIZE), (x * TILE_SIZE + i, y * TILE_SIZE + 2))
    elif tile_type == 2:
        pygame.draw.rect(screen, QUESTION_COLOR, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.circle(screen, WHITE, (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 4)
    elif tile_type == 3:
        pygame.draw.rect(screen, BLOCK_COLOR, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    elif tile_type == 4:
        pygame.draw.rect(screen, EMPTY_BLOCK_COLOR, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

# Draw flagpole
def draw_flagpole():
    pole_width = 2
    pole_height = TILE_SIZE * 3
    pygame.draw.rect(screen, FLAGPOLE_COLOR, (flagpole_x, flagpole_y - pole_height, pole_width, pole_height))
    flag_size = TILE_SIZE
    pygame.draw.polygon(screen, FLAG_COLOR, [
        (flagpole_x + pole_width, flagpole_y - pole_height),
        (flagpole_x + pole_width + flag_size, flagpole_y - pole_height + flag_size / 2),
        (flagpole_x + pole_width, flagpole_y - pole_height + flag_size)
    ])

# Initialize game objects
game_state = GameState()
player = Player(50, 100)
power_ups = []
coins = []
enemies = [Goomba(150, 200)]
flagpole_x = SCREEN_WIDTH - TILE_SIZE * 2
flagpole_y = SCREEN_HEIGHT - TILE_SIZE
font = pygame.font.Font(None, 24)
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.update(keys, game_state)

    # Update game objects
    for enemy in enemies:
        enemy.update()
    for power_up in power_ups:
        if power_up.active:
            power_up.update()
    coins = [coin for coin in coins if coin.timer > 0]
    for coin in coins:
        coin.update()

    # Check collisions
    player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
    for enemy in enemies:
        if enemy.alive and player_rect.colliderect(pygame.Rect(enemy.x, enemy.y, ENEMY_SIZE, ENEMY_SIZE)):
            if player.vy > 0 and player_rect.bottom < enemy.y + ENEMY_SIZE:
                enemy.alive = False
                game_state.score += 100
                player.vy = -3
            else:
                player.die(game_state)
    for power_up in power_ups:
        if power_up.active and player_rect.colliderect(pygame.Rect(power_up.x, power_up.y, TILE_SIZE, TILE_SIZE)):
            if power_up.type == 'mushroom':
                player.set_state('big')
            power_up.active = False
            game_state.score += 1000
    flagpole_rect = pygame.Rect(flagpole_x, flagpole_y - TILE_SIZE * 3, 2, TILE_SIZE * 3)
    if player_rect.colliderect(flagpole_rect):
        game_state.level_complete = True

    # Update timer
    game_state.time_left -= 1
    if game_state.time_left <= 0:
        player.die(game_state)

    # Draw everything
    screen.fill(SKY_BLUE)
    for y in range(len(tilemap)):
        for x in range(len(tilemap[y])):
            if tilemap[y][x] != 0:
                draw_tile(x, y, tilemap[y][x])
    for coin in coins:
        coin.draw()
    for power_up in power_ups:
        power_up.draw()
    for enemy in enemies:
        enemy.draw()
    player.draw()
    draw_flagpole()

    # Draw HUD
    time_text = font.render(f"Time: {int(game_state.time_left / FPS)}", True, WHITE)
    score_text = font.render(f"Score: {game_state.score}", True, WHITE)
    coins_text = font.render(f"Coins: {game_state.coins}", True, WHITE)
    lives_text = font.render(f"Lives: {game_state.lives}", True, WHITE)
    screen.blit(time_text, (10, 10))
    screen.blit(score_text, (10, 30))
    screen.blit(coins_text, (10, 50))
    screen.blit(lives_text, (10, 70))

    if game_state.level_complete:
        end_text = font.render("Level Complete!" if game_state.lives > 0 else "Game Over", True, WHITE)
        screen.blit(end_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
