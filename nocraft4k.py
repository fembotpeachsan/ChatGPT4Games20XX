import perlin_noise
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
import random
from math import sqrt

# --- Constants ---
GRID_SIZE = 32
MAP_SIZE = 16
PLAYER_SPEED = 5
PLAYER_COLOR = color.orange
ENEMY_COLOR = color.red
PROJECTILE_COLOR = color.yellow
TILE_COLORS = {
    'grass': color.rgb(34, 139, 34),
    'water': color.rgb(0, 105, 148),
    'mountain': color.rgb(139, 137, 137),
    'forest': color.rgb(0, 100, 0),
}

# --- Game Data ---
class GameData:
    def __init__(self):
        self.level = 1
        self.player_hp = 100
        self.player_max_hp = 100
        self.player_attack = 10
        self.enemies_killed = 0
        self.game_over = False
        self.score = 0
        self.high_score = 0

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score

game_data = GameData()

# --- Helper Functions ---
def distance_2d(pos1, pos2):
    return sqrt((pos1.x - pos2.x)**2 + (pos1.z - pos2.z)**2)

# --- Map Generation ---
def generate_map():
    noise = PerlinNoise(octaves=3)
    map_tiles = []
    for z in range(MAP_SIZE):
        row = []
        for x in range(MAP_SIZE):
            noise_val = (noise([x / 10, z / 10]) + 1) / 2
            if noise_val < 0.3:
                tile_type = 'water'
            elif noise_val < 0.6:
                tile_type = 'grass'
            elif noise_val < 0.8:
                tile_type = 'forest'
            else:
                tile_type = 'mountain'
            row.append(tile_type)
        map_tiles.append(row)
    return map_tiles

class GameTile(Entity):
    def __init__(self, position, tile_type):
        super().__init__(
            model='quad',
            color=TILE_COLORS[tile_type],
            position=position,
            scale=(GRID_SIZE, 1, GRID_SIZE),
            collider='box' if tile_type == 'mountain' else None
        )
        self.tile_type = tile_type
        self.is_tile = True

def create_tile_entities(map_tiles):
    [destroy(e) for e in scene.entities if hasattr(e, 'is_tile')]
    return [[GameTile(
        position=(x * GRID_SIZE, 0, z * GRID_SIZE),
        tile_type=map_tiles[z][x]
    ) for x in range(MAP_SIZE)] for z in range(MAP_SIZE)]

# --- Game Control Functions ---
def spawn_enemies():
    # Placeholder function to spawn enemies
    print("Spawning enemies...")

def restart_game():
    game_data.game_over = False
    game_data.level = 1
    game_data.player_hp = game_data.player_max_hp
    game_data.enemies_killed = 0
    game_data.score = 0
    
    player.position = (MAP_SIZE * GRID_SIZE // 2, 1, MAP_SIZE * GRID_SIZE // 2)
    player.rotation = (0, 0, 0)
    
    global map_tiles
    map_tiles = generate_map()
    create_tile_entities(map_tiles)
    spawn_enemies()

# --- Main Game Setup ---
app = Ursina()
window.title = 'Adventure Game'
window.borderless = False

# Create initial game state
map_tiles = generate_map()
tile_entities = create_tile_entities(map_tiles)

player = FirstPersonController(
    position=(MAP_SIZE * GRID_SIZE // 2, 1, MAP_SIZE * GRID_SIZE // 2),
    speed=PLAYER_SPEED
)

app.run()
