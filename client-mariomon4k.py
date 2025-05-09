import asyncio
import platform
import pygame
import random
import sys

# --- Initialization ---
pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mariomon by Alpharad")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

# --- Constants ---
TILE_SIZE = 16
FPS = 60
PLAYER_SPEED = 2

# --- Color Palette ---
palette = [
    (0, 0, 0, 0),      # 0: transparent
    (0, 255, 0, 255),  # 1: green (grass)
    (139, 69, 19, 255),# 2: brown (path)
    (0, 128, 0, 255),  # 3: dark green (trees)
    (255, 0, 0, 255),  # 4: red (building/player hat)
]

# --- Tile Definitions ---
def create_surface(data, palette, size):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    for y in range(len(data)):
        for x in range(len(data[0])):
            color_index = data[y][x]
            if color_index != 0:
                surf.set_at((x, y), palette[color_index][:3])
    return surf

tile_surfaces = [
    create_surface([[1 for _ in range(16)] for _ in range(16)], palette, (TILE_SIZE, TILE_SIZE)),  # 0: Grass
    create_surface([[2 for _ in range(16)] for _ in range(16)], palette, (TILE_SIZE, TILE_SIZE)),  # 1: Path
    create_surface([[3 for _ in range(16)] for _ in range(16)], palette, (TILE_SIZE, TILE_SIZE)),  # 2: Trees
    create_surface([[4 for _ in range(16)] for _ in range(16)], palette, (TILE_SIZE, TILE_SIZE)),  # 3: Building
]

# --- Player Sprite ---
player_data = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,4,4,4,4,4,4,4,4,4,0,0,0,0],
    [0,0,4,4,4,4,4,4,4,4,4,4,4,0,0,0],
    [0,0,4,4,4,4,4,4,4,4,4,4,4,0,0,0],
    [0,0,0,4,4,4,4,4,4,4,4,4,0,0,0,0],
    [0,0,0,0,2,2,2,2,2,2,2,0,0,0,0,0],
    [0,0,0,0,2,2,2,2,2,2,2,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
] + [[0]*16 for _ in range(8)]  # Padded to 16 rows
player_surf = create_surface(player_data, palette, (TILE_SIZE, TILE_SIZE))
walkable_tiles = [0, 1]  # Grass and path

# --- Mariomon Definitions ---
class Mariomon:
    def __init__(self, name, hp, attack, defense, moves):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.moves = moves

moves = {
    "Jump": {"power": 20},
    "Fireball": {"power": 25},
    "Stomp": {"power": 15},
    "Shell Toss": {"power": 20},
    "Bite": {"power": 18},
}

player_mariomon = Mariomon("Mario", 50, 10, 10, ["Jump", "Fireball"])
goomba_data = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,2,2,2,2,2,2,2,2,0,0,0,0,0],
    [0,0,2,2,2,2,2,2,2,2,2,2,0,0,0,0],
    [0,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0],
    [0,0,2,2,2,2,2,2,2,2,2,2,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
] + [[0]*16 for _ in range(10)]  # Padded to 16 rows
koopa_data = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,3,3,3,3,3,3,3,3,0,0,0,0,0],
    [0,0,3,3,3,3,3,3,3,3,3,3,0,0,0,0],
    [0,3,3,3,3,3,3,3,3,3,3,3,3,0,0,0],
    [0,0,3,3,3,3,3,3,3,3,3,3,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
] + [[0]*16 for _ in range(10)]  # Padded to 16 rows
piranha_data = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,4,4,4,4,4,4,4,4,0,0,0,0,0],
    [0,0,4,4,4,4,4,4,4,4,4,4,0,0,0,0],
    [0,4,4,4,4,4,4,4,4,4,4,4,4,0,0,0],
    [0,0,4,4,4,4,4,4,4,4,4,4,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
] + [[0]*16 for _ in range(10)]  # Padded to 16 rows
mariomon_data = {
    "Mario": player_data,
    "Goomba": goomba_data,
    "Koopa Troopa": koopa_data,
    "Piranha Plant": piranha_data,
}
mariomon_surfaces = {name: create_surface(data, palette, (TILE_SIZE, TILE_SIZE)) for name, data in mariomon_data.items()}
wild_mariomon_list = [
    Mariomon("Goomba", 30, 5, 5, ["Stomp"]),
    Mariomon("Koopa Troopa", 40, 8, 8, ["Shell Toss"]),
    Mariomon("Piranha Plant", 35, 7, 6, ["Bite"]),
]

# --- Map Data (Fixed) ---
map_data = {
    'mushroom_kingdom': [
        [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],  # 2: Trees (was 3)
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 2],  # 0: Grass
        [2, 0, 1, 1, 1, 1, 1, 1, 0, 2],  # 1: Path
        [2, 0, 1, 3, 3, 3, 3, 1, 0, 2],  # 3: Building (was 4)
        [2, 0, 1, 3, 3, 3, 3, 1, 0, 2],
        [2, 0, 1, 1, 1, 1, 1, 1, 0, 2],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 2],
        [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    ]
}

# --- Game State ---
current_map = 'mushroom_kingdom'
player_x, player_y = 5 * TILE_SIZE, 5 * TILE_SIZE
game_state = 'overworld'
battle_state = None
enemy_mariomon = None
last_tx, last_ty = int(player_x // TILE_SIZE), int(player_y // TILE_SIZE)  # For step-based encounters
enemy_attack_timer = 0

# --- Helper Functions ---
def check_collision(x, y):
    map_width = len(map_data[current_map][0])
    map_height = len(map_data[current_map])
    tx = int(x // TILE_SIZE)
    ty = int(y // TILE_SIZE)
    if 0 <= tx < map_width and 0 <= ty < map_height:
        return map_data[current_map][ty][tx] not in walkable_tiles
    return True

def calculate_damage(attacker, defender, move):
    move_power = moves[move]["power"]
    damage = move_power * (attacker.attack / defender.defense)
    return int(damage)

def enemy_turn():
    global battle_state, game_state, enemy_attack_timer
    move = random.choice(enemy_mariomon.moves)
    damage = calculate_damage(enemy_mariomon, player_mariomon, move)
    player_mariomon.hp -= damage
    if player_mariomon.hp <= 0:
        game_state = 'overworld'
        player_mariomon.hp = player_mariomon.max_hp
    else:
        battle_state = 'main_menu'

# --- Main Game Loop ---
async def update_loop():
    global current_map, player_x, player_y, game_state, battle_state, enemy_mariomon, last_tx, last_ty, enemy_attack_timer

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        if game_state == 'battle' and event.type == pygame.KEYDOWN:
            if battle_state == 'main_menu':
                if event.key == pygame.K_1:
                    battle_state = 'move_selection'
                elif event.key == pygame.K_2:
                    game_state = 'overworld'
                    player_mariomon.hp = player_mariomon.max_hp
            elif battle_state == 'move_selection':
                number = event.key - pygame.K_0
                if 1 <= number <= len(player_mariomon.moves):
                    move = player_mariomon.moves[number - 1]
                    damage = calculate_damage(player_mariomon, enemy_mariomon, move)
                    enemy_mariomon.hp -= damage
                    if enemy_mariomon.hp <= 0:
                        game_state = 'overworld'
                        player_mariomon.hp = player_mariomon.max_hp
                    else:
                        battle_state = 'enemy_attacking'
                        enemy_attack_timer = 30  # Frames to display enemy attack

    if game_state == 'overworld':
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]: dx = -PLAYER_SPEED
        elif keys[pygame.K_RIGHT]: dx = PLAYER_SPEED
        if keys[pygame.K_UP]: dy = -PLAYER_SPEED
        elif keys[pygame.K_DOWN]: dy = PLAYER_SPEED

        if dx != 0:
            new_x = player_x + dx
            if not check_collision(new_x, player_y):
                player_x = new_x
        if dy != 0:
            new_y = player_y + dy
            if not check_collision(player_x, new_y):
                player_y = new_y

        tx = int(player_x // TILE_SIZE)
        ty = int(player_y // TILE_SIZE)
        if (tx != last_tx or ty != last_ty) and (0 <= ty < len(map_data[current_map]) and 
            0 <= tx < len(map_data[current_map][0]) and 
            map_data[current_map][ty][tx] == 0 and 
            random.random() < 0.1):
            game_state = 'battle'
            enemy_mariomon = random.choice(wild_mariomon_list)
            enemy_mariomon.hp = enemy_mariomon.max_hp
            battle_state = 'main_menu'
        last_tx, last_ty = tx, ty

        map_width = len(map_data[current_map][0])
        map_height = len(map_data[current_map])
        cam_x = max(0, min(player_x - WIDTH // 2, map_width * TILE_SIZE - WIDTH))
        cam_y = max(0, min(player_y - HEIGHT // 2, map_height * TILE_SIZE - HEIGHT))

        screen.fill((0, 0, 0))
        for ty in range(map_height):
            for tx in range(map_width):
                tile_index = map_data[current_map][ty][tx]
                screen.blit(tile_surfaces[tile_index], (tx * TILE_SIZE - cam_x, ty * TILE_SIZE - cam_y))
        screen.blit(player_surf, (player_x - cam_x, player_y - cam_y))

    elif game_state == 'battle':
        if battle_state == 'enemy_attacking':
            enemy_attack_timer -= 1
            if enemy_attack_timer <= 0:
                battle_state = 'enemy_turn'
        elif battle_state == 'enemy_turn':
            enemy_turn()

        screen.fill((0, 0, 0))
        screen.blit(mariomon_surfaces[player_mariomon.name], (100, 100))
        screen.blit(mariomon_surfaces[enemy_mariomon.name], (400, 100))
        player_hp = font.render(f"{player_mariomon.name} HP: {max(0, player_mariomon.hp)}/{player_mariomon.max_hp}", True, (255, 255, 255))
        enemy_hp = font.render(f"{enemy_mariomon.name} HP: {max(0, enemy_mariomon.hp)}/{enemy_mariomon.max_hp}", True, (255, 255, 255))
        screen.blit(player_hp, (50, 50))
        screen.blit(enemy_hp, (350, 50))
        if battle_state == 'main_menu':
            menu_text = font.render("1. Fight 2. Run", True, (255, 255, 255))
            screen.blit(menu_text, (100, 300))
        elif battle_state == 'move_selection':
            moves_text = " ".join([f"{i+1}. {move}" for i, move in enumerate(player_mariomon.moves)])
            screen.blit(font.render(moves_text, True, (255, 255, 255)), (100, 300))
        elif battle_state == 'enemy_attacking':
            attack_text = font.render(f"{enemy_mariomon.name} is attacking...", True, (255, 255, 255))
            screen.blit(attack_text, (100, 300))

    pygame.display.flip()

async def main():
    while True:
        await update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
