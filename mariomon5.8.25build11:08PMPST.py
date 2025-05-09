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

# --- Types and Effectiveness (Pokémon Emerald Feature) ---
types = ["Normal", "Fire", "Water", "Grass", "Dark", "Bug", "Rock", "Ground"]
type_to_index = {t: i for i, t in enumerate(types)}
effectiveness = [
    [1, 1, 1, 1, 1, 1, 1, 1],      # Normal
    [1, 0.5, 0.5, 2, 1, 1, 2, 1],  # Fire
    [1, 2, 0.5, 0.5, 1, 1, 1, 2],  # Water
    [1, 0.5, 2, 0.5, 1, 2, 1, 2],  # Grass
    [1, 1, 1, 1, 2, 1, 1, 1],      # Dark
    [1, 1, 1, 2, 1, 0.5, 1, 1],    # Bug
    [1, 2, 1, 1, 1, 2, 0.5, 1],    # Rock
    [1, 1, 2, 1, 1, 1, 2, 0.5],    # Ground
]

# --- Move Class (Pokémon Emerald Feature) ---
class Move:
    def __init__(self, name, type, category, power, accuracy):
        self.name = name
        self.type = type
        self.category = category  # "physical" or "special"
        self.power = power
        self.accuracy = accuracy

# --- Mariomon Class (Enhanced with Pokémon Emerald Stats) ---
class Mariomon:
    def __init__(self, name, type, hp, attack, defense, sp_attack, sp_defense, speed, moves):
        self.name = name
        self.type = type
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.sp_attack = sp_attack
        self.sp_defense = sp_defense
        self.speed = speed
        self.moves = moves  # List of move names

# --- Moves (Pokémon Emerald Style) ---
moves = {
    "Jump": Move("Jump", "Normal", "physical", 20, 100),
    "Fireball": Move("Fireball", "Fire", "special", 25, 100),
    "Stomp": Move("Stomp", "Ground", "physical", 15, 100),
    "Shell Toss": Move("Shell Toss", "Rock", "physical", 20, 90),
    "Bite": Move("Bite", "Dark", "physical", 18, 100),
}

# --- Player and Wild Mariomon ---
player_mariomon = Mariomon("Mario", "Normal", 50, 10, 10, 10, 10, 10, ["Jump", "Fireball"])
wild_mariomon_list = [
    Mariomon("Goomba", "Dark", 30, 5, 5, 5, 5, 5, ["Stomp"]),
    Mariomon("Koopa Troopa", "Bug", 40, 8, 8, 8, 8, 8, ["Shell Toss"]),
    Mariomon("Piranha Plant", "Grass", 35, 7, 6, 7, 6, 7, ["Bite"]),
]

# --- Mariomon Surfaces ---
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

# --- Map Data ---
map_data = {
    'mushroom_kingdom': [
        [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],  # 2: Trees
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 2],  # 0: Grass
        [2, 0, 1, 1, 1, 1, 1, 1, 0, 2],  # 1: Path
        [2, 0, 1, 3, 3, 3, 3, 1, 0, 2],  # 3: Building
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
last_tx, last_ty = int(player_x // TILE_SIZE), int(player_y // TILE_SIZE)
message_timer = 0
current_message = ""
player_chosen_move = None
first = None
second = None

# --- Helper Functions ---
def check_collision(x, y):
    map_width = len(map_data[current_map][0])
    map_height = len(map_data[current_map])
    tx = int(x // TILE_SIZE)
    ty = int(y // TILE_SIZE)
    if 0 <= tx < map_width and 0 <= ty < map_height:
        return map_data[current_map][ty][tx] not in walkable_tiles
    return True

def calculate_damage(attacker, defender, move_name):
    move = moves[move_name]
    if random.random() > move.accuracy / 100:
        return 0  # Move misses
    attacking_type_index = type_to_index[move.type]
    defending_type_index = type_to_index[defender.type]
    eff = effectiveness[attacking_type_index][defending_type_index]
    if move.category == "physical":
        stat_ratio = attacker.attack / defender.defense
    else:
        stat_ratio = attacker.sp_attack / defender.sp_defense
    damage = int(move.power * stat_ratio * eff)
    return damage

# --- Main Game Loop ---
async def update_loop():
    global current_map, player_x, player_y, game_state, battle_state, enemy_mariomon, last_tx, last_ty, message_timer, current_message, player_chosen_move, first, second

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        if game_state == 'battle' and battle_state in ['player_choose_action', 'player_choose_move'] and event.type == pygame.KEYDOWN:
            if battle_state == 'player_choose_action':
                if event.key == pygame.K_1:
                    battle_state = 'player_choose_move'
                elif event.key == pygame.K_2:
                    game_state = 'overworld'
                    player_mariomon.hp = player_mariomon.max_hp
            elif battle_state == 'player_choose_move':
                number = event.key - pygame.K_0
                if 1 <= number <= len(player_mariomon.moves):
                    player_chosen_move = player_mariomon.moves[number - 1]
                    battle_state = 'ai_choose_move'

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
            battle_state = 'start'
            current_message = f"A wild {enemy_mariomon.name} appeared!"
            message_timer = 60
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
        if battle_state == 'start':
            if message_timer > 0:
                message_timer -= 1
            else:
                battle_state = 'player_choose_action'
        elif battle_state == 'player_choose_action':
            if message_timer > 0:
                message_timer -= 1
        elif battle_state == 'ai_choose_move':
            enemy_chosen_move = random.choice(enemy_mariomon.moves)
            if player_mariomon.speed > enemy_mariomon.speed:
                first = (player_mariomon, player_chosen_move, enemy_mariomon)
                second = (enemy_mariomon, enemy_chosen_move, player_mariomon)
            else:
                first = (enemy_mariomon, enemy_chosen_move, player_mariomon)
                second = (player_mariomon, player_chosen_move, enemy_mariomon)
            battle_state = 'execute_first_move'
            current_message = f"{first[0].name} will go first!"
            message_timer = 60
        elif battle_state == 'execute_first_move':
            if message_timer > 0:
                message_timer -= 1
            else:
                attacker, move, defender = first
                current_message = f"{attacker.name} used {move}!"
                message_timer = 60
                damage = calculate_damage(attacker, defender, move)
                if damage > 0:
                    defender.hp -= damage
                    eff = effectiveness[type_to_index[moves[move].type]][type_to_index[defender.type]]
                    if eff > 1:
                        current_message += " It's super effective!"
                    elif eff < 1:
                        current_message += " It's not very effective..."
                    current_message += f" {defender.name} took {damage} damage!"
                else:
                    current_message = "But it missed!"
                message_timer = 60
                if defender.hp <= 0:
                    battle_state = 'end_battle'
                else:
                    battle_state = 'execute_second_move'
        elif battle_state == 'execute_second_move':
            if message_timer > 0:
                message_timer -= 1
            else:
                attacker, move, defender = second
                current_message = f"{attacker.name} used {move}!"
                message_timer = 60
                damage = calculate_damage(attacker, defender, move)
                if damage > 0:
                    defender.hp -= damage
                    eff = effectiveness[type_to_index[moves[move].type]][type_to_index[defender.type]]
                    if eff > 1:
                        current_message += " It's super effective!"
                    elif eff < 1:
                        current_message += " It's not very effective..."
                    current_message += f" {defender.name} took {damage} damage!"
                else:
                    current_message = "But it missed!"
                message_timer = 60
                if defender.hp <= 0:
                    battle_state = 'end_battle'
                else:
                    battle_state = 'player_choose_action'
        elif battle_state == 'end_battle':
            if message_timer > 0:
                message_timer -= 1
            else:
                if enemy_mariomon.hp <= 0:
                    current_message = f"{enemy_mariomon.name} fainted!"
                else:
                    current_message = f"{player_mariomon.name} fainted!"
                message_timer = 60
                game_state = 'overworld'
                player_mariomon.hp = player_mariomon.max_hp

        screen.fill((0, 0, 0))
        screen.blit(mariomon_surfaces[player_mariomon.name], (100, 100))
        screen.blit(mariomon_surfaces[enemy_mariomon.name], (400, 100))
        player_hp = font.render(f"{player_mariomon.name} HP: {max(0, player_mariomon.hp)}/{player_mariomon.max_hp}", True, (255, 255, 255))
        enemy_hp = font.render(f"{enemy_mariomon.name} HP: {max(0, enemy_mariomon.hp)}/{enemy_mariomon.max_hp}", True, (255, 255, 255))
        screen.blit(player_hp, (50, 50))
        screen.blit(enemy_hp, (350, 50))
        if current_message and message_timer > 0:
            message_text = font.render(current_message, True, (255, 255, 255))
            screen.blit(message_text, (100, 300))
        elif battle_state == 'player_choose_action':
            menu_text = font.render("1. Fight 2. Run", True, (255, 255, 255))
            screen.blit(menu_text, (100, 300))
        elif battle_state == 'player_choose_move':
            moves_text = " ".join([f"{i+1}. {move}" for i, move in enumerate(player_mariomon.moves)])
            screen.blit(font.render(moves_text, True, (255, 255, 255)), (100, 300))

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
