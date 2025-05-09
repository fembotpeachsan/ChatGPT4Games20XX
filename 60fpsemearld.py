import asyncio
import platform
import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
TILE_SIZE = 32
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Game states
game_state = 'overworld'
battle_state = None

# Player properties
player_pos = [5 * TILE_SIZE, 4 * TILE_SIZE]
player_speed = 4

# Simple map (0 = grass, 1 = wall)
tile_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Pokémon-like entity (Mariomon)
class Mariomon:
    def __init__(self, name, hp, attack, defense, moves):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense
        self.moves = moves

# Moves
tackle = {"name": "Tackle", "power": 40, "type": "Normal"}
ember = {"name": "Ember", "power": 40, "type": "Fire"}

# Player's Mariomon
player_mariomon = Mariomon("Charimario", 50, 20, 15, [tackle, ember])
enemy_mariomon = None

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pokémon Emerald Engine Test")

# Font
font = pygame.font.Font(None, 36)

def setup():
    global clock
    clock = pygame.time.Clock()

def draw_tile_map():
    for y, row in enumerate(tile_map):
        for x, tile in enumerate(row):
            if tile == 0:
                pygame.draw.rect(screen, (0, 255, 0), (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif tile == 1:
                pygame.draw.rect(screen, (100, 100, 100), (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

def draw_player():
    pygame.draw.rect(screen, RED, (player_pos[0], player_pos[1], TILE_SIZE, TILE_SIZE))

def check_collision(new_pos):
    new_x, new_y = new_pos[0] // TILE_SIZE, new_pos[1] // TILE_SIZE
    if 0 <= new_x < len(tile_map[0]) and 0 <= new_y < len(tile_map):
        return tile_map[new_y][new_x] != 1
    return False

def start_battle():
    global game_state, battle_state, enemy_mariomon
    game_state = 'battle'
    battle_state = 'player_turn'
    enemy_mariomon = Mariomon("Bowserasaur", 45, 18, 12, [tackle])

def draw_battle():
    screen.fill(BLACK)
    # Draw player Mariomon
    pygame.draw.rect(screen, RED, (50, 150, 50, 50))
    player_hp_text = font.render(f"{player_mariomon.name} HP: {player_mariomon.hp}/{player_mariomon.max_hp}", True, WHITE)
    screen.blit(player_hp_text, (50, 100))
    # Draw enemy Mariomon
    pygame.draw.rect(screen, (0, 0, 255), (200, 50, 50, 50))
    enemy_hp_text = font.render(f"{enemy_mariomon.name} HP: {enemy_mariomon.hp}/{enemy_mariomon.max_hp}", True, WHITE)
    screen.blit(enemy_hp_text, (200, 10))
    # Battle options or message
    if battle_state == 'player_turn':
        text = font.render("Press 1 for Tackle, 2 for Ember", True, WHITE)
        screen.blit(text, (20, 200))
    elif battle_state == 'enemy_turn':
        text = font.render("Enemy's turn...", True, WHITE)
        screen.blit(text, (20, 200))
    elif battle_state == 'end_battle':
        text = font.render("Battle ended! Press SPACE to continue", True, WHITE)
        screen.blit(text, (20, 200))

def apply_damage(attacker, defender, move):
    damage = max(1, (attacker.attack * move["power"] // defender.defense) // 2)
    defender.hp = max(0, defender.hp - damage)
    return damage

async def update_loop():
    global player_pos, game_state, battle_state, enemy_mariomon

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return

    keys = pygame.key.get_pressed()

    if game_state == 'overworld':
        new_pos = player_pos.copy()
        if keys[pygame.K_LEFT]:
            new_pos[0] -= player_speed
        if keys[pygame.K_RIGHT]:
            new_pos[0] += player_speed
        if keys[pygame.K_UP]:
            new_pos[1] -= player_speed
        if keys[pygame.K_DOWN]:
            new_pos[1] += player_speed

        if check_collision(new_pos):
            player_pos = new_pos

        # Random encounter
        if random.random() < 0.01 and tile_map[player_pos[1] // TILE_SIZE][player_pos[0] // TILE_SIZE] == 0:
            start_battle()

        screen.fill((0, 0, 0))
        draw_tile_map()
        draw_player()

    elif game_state == 'battle':
        if battle_state == 'player_turn' and keys[pygame.K_1]:
            apply_damage(player_mariomon, enemy_mariomon, tackle)
            battle_state = 'enemy_turn'
        elif battle_state == 'player_turn' and keys[pygame.K_2]:
            apply_damage(player_mariomon, enemy_mariomon, ember)
            battle_state = 'enemy_turn'
        elif battle_state == 'enemy_turn':
            await asyncio.sleep(1)  # Simulate enemy thinking
            apply_damage(enemy_mariomon, player_mariomon, tackle)
            if player_mariomon.hp <= 0 or enemy_mariomon.hp <= 0:
                battle_state = 'end_battle'
            else:
                battle_state = 'player_turn'
        elif battle_state == 'end_battle' and keys[pygame.K_SPACE]:
            game_state = 'overworld'
            player_mariomon.hp = player_mariomon.max_hp  # Reset HP
            enemy_mariomon = None
            battle_state = None

        draw_battle()

    pygame.display.flip()

async def main():
    setup()
    while True:
        await update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
