import pygame
import sys
import random

pygame.init()
pygame.font.init() # Initialize font module

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 40 # Size of one tile in pixels

# Default Level Dimensions (can be overridden by individual level configs)
DEFAULT_LEVEL_WIDTH_TILES = 150
DEFAULT_LEVEL_HEIGHT_TILES = 15 # Consistent height for simplicity

# Colors (RGB tuples)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0) # Small Mario
BLUE = (0, 0, 255) # Super Mario
GREEN = (0, 255, 0) # Goomba color
BROWN = (139, 69, 19) # Ground/Brick/Hit Question block color
YELLOW = (255, 255, 0) # Coin/Question block color
LIGHT_BLUE = (135, 206, 235) # Sky color
DARK_GRAY_BG = (100, 100, 100) # Underground background
CASTLE_BG = (60, 60, 60) # Castle background

# Physics Constants
GRAVITY = 0.8
PLAYER_JUMP_STRENGTH = -15
PLAYER_MOVE_SPEED = 5
ENEMY_MOVE_SPEED = 2

# Tile Types (represented by integers)
AIR = 0
GROUND = 1
BRICK = 2
QUESTION_BLOCK = 3
# PIPE_TOP_LEFT = 4 (Example for more complex tiles, not used in this simplified version)
# PIPE_TOP_RIGHT = 5
# PIPE_BODY_LEFT = 6
# PIPE_BODY_RIGHT = 7

MAX_LEVELS = 32

# --- Level Generation Helper Functions ---
def generate_base_level_layout(width=DEFAULT_LEVEL_WIDTH_TILES, height=DEFAULT_LEVEL_HEIGHT_TILES, floor_type=GROUND):
    layout = [[AIR] * width for _ in range(height)]
    for r_idx in range(height - 2, height): # Ground - last two rows
        for c_idx in range(width):
            layout[r_idx][c_idx] = floor_type
    return layout

def generate_level_type_1(width=DEFAULT_LEVEL_WIDTH_TILES, height=DEFAULT_LEVEL_HEIGHT_TILES, seed=0): # Overworld
    layout = generate_base_level_layout(width, height)
    random.seed(seed) # For deterministic randomness based on level

    # Q-Blocks and Bricks line
    if width > 30:
        for i in range(15 + seed % 5, min(width - 10, 25 + seed % 5), 2):
            layout[height - 5][i] = QUESTION_BLOCK if random.random() < 0.6 else BRICK
            if i+1 < width: layout[height - 5][i+1] = BRICK if random.random() < 0.7 else AIR

    # Floating platforms/blocks
    for _ in range(width // 30): # Number of platform clusters
        px = random.randint(10, width - 15)
        py_offset = random.randint(3,6)
        plat_len = random.randint(1,3)
        for i in range(plat_len):
            if px + i < width:
                 layout[height - py_offset][px + i] = BRICK if random.random() < 0.5 else QUESTION_BLOCK

    # Gaps
    for _ in range(width // 50):
        gap_x = random.randint(10, width - 10)
        gap_len = random.randint(2,4)
        for i in range(gap_len):
            if gap_x + i < width:
                layout[height - 1][gap_x + i] = AIR
                layout[height - 2][gap_x + i] = AIR
    
    # "Pipe" like structures (simple blocks)
    if width > 40 and random.random() < 0.7:
        pipe_x = random.randint(30, width - 10)
        pipe_h = random.randint(2,4)
        for r_off in range(pipe_h):
            if height - 3 - r_off >=0:
                layout[height - 3 - r_off][pipe_x] = GROUND
                if pipe_x + 1 < width: layout[height - 3 - r_off][pipe_x+1] = GROUND
    return layout

def generate_level_type_2(width=DEFAULT_LEVEL_WIDTH_TILES, height=DEFAULT_LEVEL_HEIGHT_TILES, seed=0): # Underground
    layout = [[AIR] * width for _ in range(height)]
    random.seed(seed)
    # Ceiling and Floor
    for c in range(width):
        layout[0][c] = BRICK
        layout[1][c] = BRICK
        layout[height-1][c] = GROUND
        layout[height-2][c] = GROUND

    # Internal structure
    for r in range(2, height - 3):
        for c in range(1, width - 1):
            if random.random() < 0.4: # Fill with some bricks
                layout[r][c] = BRICK
    # Carve out a path
    path_y = height - 4
    for c in range(width):
        layout[path_y][c] = AIR
        layout[path_y-1][c] = AIR # Make path 2 tiles high
        if random.random() < 0.1 and c > 5 and c < width -5: # occasional obstacle
            layout[path_y][c] = BRICK
        if random.random() < 0.05 and c > 5 and c < width -5: # occasional q-block
             layout[path_y-2][c] = QUESTION_BLOCK


    # Add some Q-blocks in ceiling or brick areas
    for _ in range(width // 15):
        qb_x = random.randint(1, width - 2)
        qb_y = random.randint(2, height - 5)
        if layout[qb_y][qb_x] == BRICK:
            layout[qb_y][qb_x] = QUESTION_BLOCK if random.random() < 0.3 else BRICK # Sometimes hide QBs

    return layout

def generate_level_type_3(width=DEFAULT_LEVEL_WIDTH_TILES, height=DEFAULT_LEVEL_HEIGHT_TILES, seed=0): # Athletic/Sky
    layout = [[AIR] * width for _ in range(height)]
    random.seed(seed)
    # Start platform
    for c in range(min(width, 5)): layout[height-1][c] = GROUND

    current_x = 0
    last_y = height -1

    while current_x < width - 10:
        plat_len = random.randint(3, 7)
        # Determine next platform y (relative to last_y, within bounds)
        dy = random.randint(-2, 2) # Jump height difference
        next_y = max(height//3, min(height - 1, last_y + dy))

        # Determine next platform x (gap distance)
        gap = random.randint(2,4) if next_y == last_y else random.randint(1,3) # Shorter gaps for height changes
        current_x += gap

        for i in range(plat_len):
            if current_x + i < width:
                layout[next_y][current_x + i] = GROUND if random.random() < 0.8 else BRICK
                if i == plat_len // 2 and random.random() < 0.3 and next_y > 0: # Q-Block above platform center
                    layout[next_y-1][current_x+i] = QUESTION_BLOCK

        current_x += plat_len
        last_y = next_y
    
    # Ensure an end platform
    for c in range(max(0, width-5), width): layout[height-1][c] = GROUND
    return layout

def generate_level_type_0(width=DEFAULT_LEVEL_WIDTH_TILES, height=DEFAULT_LEVEL_HEIGHT_TILES, seed=0): # Castle
    layout = [[AIR] * width for _ in range(height)]
    random.seed(seed)
    # Floor & Ceiling
    for c in range(width):
        layout[0][c] = BRICK; layout[1][c] = BRICK
        layout[height-1][c] = BRICK; layout[height-2][c] = BRICK

    # Some pillars / walls
    for _ in range(width // 10):
        wall_x = random.randint(5, width - 6)
        wall_h = random.randint(height // 3, height - 3)
        for r_off in range(wall_h):
            if 2 + r_off < height -2:
                layout[2+r_off][wall_x] = BRICK

    # Create a path, potentially with lava pits (represented by AIR at bottom)
    path_y = height - 3
    for c in range(width):
        layout[path_y][c] = AIR
        layout[path_y -1][c] = AIR # Path height

        if c > 10 and c < width - 10:
            if random.random() < 0.15: # Lava pit
                layout[path_y+1][c] = AIR # Remove floor for pit
                layout[path_y][c] = AIR # Ensure pit is open
            elif random.random() < 0.05: # Small obstacle
                layout[path_y][c] = BRICK
            elif random.random() < 0.03: # Qblock over path
                layout[path_y-2][c] = QUESTION_BLOCK
    
    # Bridge at the end (visual only, still BRICK type)
    bridge_start_x = max(10, width - 20)
    for c in range(bridge_start_x, width -2):
        layout[height - 4][c] = BRICK # Bridge
        layout[height - 1][c] = AIR # "Lava" under bridge end
        layout[height - 2][c] = AIR

    return layout

# --- Global Game Variables ---
ALL_LEVELS_CONFIG = []
current_level_index = 0
score = 0
score_font = pygame.font.Font(None, 36)
current_background_color = LIGHT_BLUE


# --- Populate ALL_LEVELS_CONFIG ---
PLAYER_START_COL_TILE = 2
PLAYER_START_Y_PIXEL = (DEFAULT_LEVEL_HEIGHT_TILES - 2) * TILE_SIZE # For player's bottomleft

for i in range(MAX_LEVELS):
    world_num = (i // 4) + 1
    stage_num = (i % 4) + 1
    level_seed = i * 12345 # Unique seed for each level

    level_layout_func = generate_level_type_1
    level_bg_color = LIGHT_BLUE
    level_width = DEFAULT_LEVEL_WIDTH_TILES

    if stage_num == 1: # X-1 (Overworld)
        level_layout_func = generate_level_type_1
        level_bg_color = LIGHT_BLUE
        level_width = random.randint(130,180)
    elif stage_num == 2: # X-2 (Underground)
        level_layout_func = generate_level_type_2
        level_bg_color = DARK_GRAY_BG
        level_width = random.randint(100,150)
    elif stage_num == 3: # X-3 (Athletic/Sky)
        level_layout_func = generate_level_type_3
        level_bg_color = LIGHT_BLUE
        level_width = random.randint(180,250)
    elif stage_num == 4: # X-4 (Castle)
        level_layout_func = generate_level_type_0
        level_bg_color = CASTLE_BG
        level_width = random.randint(80,120)

    layout = level_layout_func(width=level_width, height=DEFAULT_LEVEL_HEIGHT_TILES, seed=level_seed)

    enemy_positions_tiles = []
    num_enemies = 1 + world_num + (stage_num % 2) # More enemies in later levels
    for _ in range(num_enemies):
        # Find valid ground for enemy, not too close to start
        for attempt in range(10): # Try to find a spot
            ex = random.randint(PLAYER_START_COL_TILE + 15, level_width - 5)
            ey_tile_bottom = -1
            for r_scan in range(DEFAULT_LEVEL_HEIGHT_TILES - 1, 1, -1):
                if layout[r_scan][ex] != AIR and layout[r_scan-1][ex] == AIR: # Standing on r_scan, head in r_scan-1
                    ey_tile_bottom = r_scan
                    break
            if ey_tile_bottom != -1:
                enemy_positions_tiles.append((ex, ey_tile_bottom))
                break
    
    player_start_x_pixel = PLAYER_START_COL_TILE * TILE_SIZE
    # Ensure player starts on solid ground for sky levels too
    start_y_tile_for_feet = DEFAULT_LEVEL_HEIGHT_TILES - 2
    if stage_num == 3: # Sky levels, may need to adjust player start
        found_start_ground = False
        for r_check in range(DEFAULT_LEVEL_HEIGHT_TILES -1, DEFAULT_LEVEL_HEIGHT_TILES //2, -1):
            if layout[r_check][PLAYER_START_COL_TILE] != AIR:
                 start_y_tile_for_feet = r_check -1 # Feet are on r_check, so rect.bottom is (r_check+1)*TILE_SIZE. Player y is (r_check)*TILE_SIZE for constructor
                 player_y_constructor = (start_y_tile_for_feet) * TILE_SIZE
                 found_start_ground = True
                 break
        if not found_start_ground: # Default if no immediate ground found at start col
            player_y_constructor = PLAYER_START_Y_PIXEL
        else:
             player_y_constructor = (start_y_tile_for_feet) * TILE_SIZE # This is for bottomleft, so player is on tile start_y_tile_for_feet
    else:
        player_y_constructor = PLAYER_START_Y_PIXEL


    ALL_LEVELS_CONFIG.append({
        'layout': layout,
        'enemy_positions_tiles': enemy_positions_tiles,
        'player_start_pixel': (player_start_x_pixel, player_y_constructor),
        'level_width_tiles': level_width,
        'level_height_tiles': DEFAULT_LEVEL_HEIGHT_TILES,
        'bg_color': level_bg_color
    })

# --- Game Classes ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.base_width = TILE_SIZE * 0.9
        self.base_height = TILE_SIZE * 0.9
        self.super_height = TILE_SIZE * 1.8
        self.width = self.base_width
        self.height = self.base_height
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(RED)
        self.rect = self.image.get_rect(bottomleft=(x, y))
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.state = "small" # "small", "super"
        self.facing_right = True

    def update_size_and_rect(self):
        old_bottomleft = self.rect.bottomleft
        self.width = self.base_width # Width could change for super mario too if desired
        self.height = self.base_height if self.state == "small" else self.super_height
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(RED if self.state == "small" else BLUE)
        self.rect = self.image.get_rect(bottomleft=old_bottomleft)

    def apply_gravity(self):
        self.vy += GRAVITY
        if self.vy > 15: self.vy = 15

    def jump(self):
        if self.on_ground:
            self.vy = PLAYER_JUMP_STRENGTH
            self.on_ground = False

    def move_x(self, blocks):
        self.rect.x += self.vx
        hit_blocks = pygame.sprite.spritecollide(self, blocks, False)
        for block in hit_blocks:
            if self.vx > 0: self.rect.right = block.rect.left
            elif self.vx < 0: self.rect.left = block.rect.right
            self.vx = 0

    def move_y(self, blocks): # Removed enemies from args, handle separately
        self.rect.y += self.vy
        hit_blocks = pygame.sprite.spritecollide(self, blocks, False)
        self.on_ground = False
        for block in hit_blocks:
            if self.vy > 0: # Falling
                self.rect.bottom = block.rect.top
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0: # Jumping up
                self.rect.top = block.rect.bottom
                self.vy = 0
                if isinstance(block, Block) and block.type == QUESTION_BLOCK and block.state == "active":
                    # Pass relevant groups to block.hit_from_below
                    block.hit_from_below(all_sprites_group=all_sprites, powerups_group=powerups)


    def update(self, blocks): # Removed enemies from args
        self.move_x(blocks)
        self.apply_gravity()
        self.move_y(blocks) # Collision with blocks handled here

    def get_rect(self):
        return self.rect

    def take_damage(self):
        global running # Allow modification of global running state for game over
        if self.state == "super":
            self.state = "small"
            self.update_size_and_rect()
            # Add brief invincibility/flashing here if desired
        elif self.state == "small":
            print("Mario is Small and took damage! Game Over (simplified)")
            running = False # End game

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = TILE_SIZE * 0.8
        self.height = TILE_SIZE * 0.8
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(bottomleft=(x, y))
        self.vx = -ENEMY_MOVE_SPEED
        self.vy = 0
        self.on_ground = False
        self.state = "walking" # "walking", "squashed", "dead"
        self.squash_timer = 0
        self.squash_duration = 30 # Frames

    def apply_gravity(self):
        self.vy += GRAVITY
        if self.vy > 15: self.vy = 15

    def move_x(self, blocks):
        self.rect.x += self.vx
        hit_blocks = pygame.sprite.spritecollide(self, blocks, False)
        for block in hit_blocks:
            if self.state == "walking":
                if self.vx > 0:
                    self.rect.right = block.rect.left
                    self.vx = -ENEMY_MOVE_SPEED
                elif self.vx < 0:
                    self.rect.left = block.rect.right
                    self.vx = ENEMY_MOVE_SPEED
    
    def move_y(self, blocks):
        self.rect.y += self.vy
        hit_blocks = pygame.sprite.spritecollide(self, blocks, False)
        self.on_ground = False
        for block in hit_blocks:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
                self.on_ground = True
            # Enemies don't typically hit their heads on blocks to stop upward vy

    def update(self, blocks):
        if self.state == "walking":
            self.apply_gravity()
            self.move_x(blocks)
            self.move_y(blocks)
        elif self.state == "squashed":
            self.squash_timer += 1
            if self.squash_timer >= self.squash_duration:
                self.state = "dead"
                self.kill()

    def get_rect(self): return self.rect

    def squash(self):
        if self.state == "walking":
            self.state = "squashed"
            self.vx = 0 # Stop moving when squashed
            self.vy = 0
            # Adjust rect for squash visual
            old_bottomleft = self.rect.bottomleft
            self.image = pygame.Surface([self.width, self.height / 2])
            self.image.fill(BROWN) # Squashed color
            self.rect = self.image.get_rect(bottomleft=old_bottomleft)

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y): # x,y is topleft for spawning from block
        super().__init__()
        self.width = TILE_SIZE * 0.8
        self.height = TILE_SIZE * 0.8
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(WHITE) # Mushroom color for now
        self.rect = self.image.get_rect(topleft=(x,y)) # Spawned from block top

        self.vx = ENEMY_MOVE_SPEED # Moves like an enemy
        self.vy = 0
        self.on_ground = False
        self.state = "emerging"
        self.emerge_target_y = self.rect.y - TILE_SIZE # Emerge one tile up
        self.emerged_fully = False


    def apply_gravity(self):
        self.vy += GRAVITY
        if self.vy > 15: self.vy = 15

    def move_x(self, blocks):
        self.rect.x += self.vx
        hit_blocks = pygame.sprite.spritecollide(self, blocks, False)
        for block in hit_blocks:
            if self.vx > 0:
                self.rect.right = block.rect.left; self.vx *= -1
            elif self.vx < 0:
                self.rect.left = block.rect.right; self.vx *= -1

    def move_y(self, blocks):
        self.rect.y += self.vy
        hit_blocks = pygame.sprite.spritecollide(self, blocks, False)
        self.on_ground = False
        for block in hit_blocks:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0: # If it hits something while emerging upwards (not standard behavior)
                self.rect.top = block.rect.bottom
                self.vy = 0


    def update(self, blocks):
        if self.state == "emerging" and not self.emerged_fully:
            self.rect.y -= 1 # Move up slowly
            if self.rect.bottom <= self.emerge_target_y + self.height : # Check if bottom has passed target spawn height
                self.rect.bottom = self.emerge_target_y + self.height
                self.emerged_fully = True
                self.vy = 0 # Start falling after emerging or wait for ground
                self.state = "moving"
        elif self.state == "moving":
            self.apply_gravity()
            self.move_x(blocks)
            self.move_y(blocks)

    def get_rect(self): return self.rect


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.image = pygame.Surface([self.width, self.height])
        self.type = type
        self.state = "active" # For question blocks: "active", "hit"
        self.contents = "mushroom" # Default for QUESTION_BLOCK

        if type == GROUND: self.image.fill(BROWN)
        elif type == BRICK: self.image.fill(BROWN)
        elif type == QUESTION_BLOCK: self.image.fill(YELLOW)
        else: self.image.fill(BLACK) # Fallback

        self.rect = self.image.get_rect(topleft=(x, y))

    def hit_from_below(self, all_sprites_group, powerups_group): # Needs sprite groups passed
        if self.type == QUESTION_BLOCK and self.state == "active":
            self.state = "hit"
            self.image.fill(BROWN) # Change color to indicate hit
            print(f"Question block at ({self.rect.x//TILE_SIZE}, {self.rect.y//TILE_SIZE}) hit!")

            if self.contents == "mushroom":
                # Spawn mushroom just above the block. Powerup init takes topleft.
                new_mushroom = Powerup(self.rect.x + (TILE_SIZE - TILE_SIZE *0.8)/2 , self.rect.y - TILE_SIZE*0.8) # Centered spawn
                all_sprites_group.add(new_mushroom)
                powerups_group.add(new_mushroom)
                print("Mushroom spawned!")
            # Add other contents like "coin" later

    def update(self): pass # Static blocks don't do much on update
    def get_rect(self): return self.rect

# --- Game Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(f"Simplified SMB - Level {current_level_index + 1}")
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
solid_blocks = pygame.sprite.Group()
enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()

camera_x = 0.0
mario_player = Player(0,0) # Initialized once, repositioned by load_level

def load_level(level_idx):
    global current_background_color, camera_x, level_data_for_collision # level_data_for_collision might not be needed if all logic uses sprite groups

    if level_idx >= MAX_LEVELS:
        print("CONGRATULATIONS! You've beaten all levels!")
        # Implement a win screen or loop eventually
        pygame.quit()
        sys.exit()

    config = ALL_LEVELS_CONFIG[level_idx]
    current_level_layout = config['layout']
    current_background_color = config['bg_color']
    pygame.display.set_caption(f"Simplified SMB - Level {level_idx + 1}/{MAX_LEVELS}")


    # Clear old sprites (except player who is handled separately)
    all_sprites.empty()
    solid_blocks.empty()
    enemies.empty()
    powerups.empty() # Spawned dynamically

    # Player repositioning and re-adding
    mario_player.rect.bottomleft = config['player_start_pixel']
    mario_player.vx = 0
    mario_player.vy = 0
    mario_player.on_ground = False # Will be re-evaluated by physics
    all_sprites.add(mario_player) # Add persistent player to new set of all_sprites

    # Create blocks
    for r, row_data in enumerate(current_level_layout):
        for c, tile_type in enumerate(row_data):
            if tile_type != AIR:
                block = Block(c * TILE_SIZE, r * TILE_SIZE, tile_type)
                all_sprites.add(block)
                solid_blocks.add(block)

    # Create enemies
    for ex_tile, ey_tile_bottom in config['enemy_positions_tiles']:
        enemy_px_x = ex_tile * TILE_SIZE
        enemy_px_y = (ey_tile_bottom + 1) * TILE_SIZE # bottomleft y for Enemy constructor
        goomba = Enemy(enemy_px_x, enemy_px_y)
        all_sprites.add(goomba)
        enemies.add(goomba)

    camera_x = 0
    print(f"Loaded Level {level_idx + 1}. Player State: {mario_player.state}")


# --- Initial Load ---
load_level(current_level_index)

# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: mario_player.jump()
            if event.key == pygame.K_ESCAPE: running = False
            #DEBUG: if event.key == pygame.K_n: current_level_index = (current_level_index + 1) % MAX_LEVELS; load_level(current_level_index)


    keys = pygame.key.get_pressed()
    mario_player.vx = 0
    if keys[pygame.K_LEFT]: mario_player.vx = -PLAYER_MOVE_SPEED; mario_player.facing_right = False
    if keys[pygame.K_RIGHT]: mario_player.vx = PLAYER_MOVE_SPEED; mario_player.facing_right = True

    # --- Update ---
    mario_player.update(solid_blocks)
    enemies.update(solid_blocks)
    powerups.update(solid_blocks) # Powerups also need block collision

    # --- Inter-sprite Collisions ---
    # Player vs. Enemies
    enemy_collisions = pygame.sprite.spritecollide(mario_player, enemies, False)
    for enemy in enemy_collisions:
        if enemy.state == "walking":
            # Stomp check: Player falling and player's bottom is near enemy's top
            if mario_player.vy > 0 and mario_player.rect.bottom < enemy.rect.centery + mario_player.vy : #vy added for pre-emptive check
                enemy.squash()
                mario_player.vy = PLAYER_JUMP_STRENGTH * 0.6 # Small bounce
                score += 100
            else: # Player hit by enemy from side/below
                mario_player.take_damage() # Mario takes damage or game over


    # Player vs. Powerups
    powerup_collisions = pygame.sprite.spritecollide(mario_player, powerups, True) # True to kill powerup
    for p_up in powerup_collisions:
        if mario_player.state == "small":
            mario_player.state = "super"
            mario_player.update_size_and_rect()
            score += 1000
        else: # Already super, or other powerup type
            score += 200 # Extra points if already super

    # --- Level Completion Check ---
    current_level_pixel_width = ALL_LEVELS_CONFIG[current_level_index]['level_width_tiles'] * TILE_SIZE
    if mario_player.rect.right > current_level_pixel_width - TILE_SIZE: # Reached far right
        current_level_index += 1
        if current_level_index >= MAX_LEVELS:
            print("Game Completed! You are a Super Player!")
            # You could show a win screen here then set running = False
            running = False # End after beating all levels
        else:
            load_level(current_level_index)


    # --- Camera Update ---
    # Target camera position to center player, but don't go out of bounds
    target_camera_x = mario_player.rect.centerx - SCREEN_WIDTH / 2
    level_width_px = ALL_LEVELS_CONFIG[current_level_index]['level_width_tiles'] * TILE_SIZE

    if target_camera_x < 0: camera_x = 0
    elif target_camera_x > level_width_px - SCREEN_WIDTH:
        camera_x = max(0, level_width_px - SCREEN_WIDTH) # Ensure camera_x isn't negative if level is narrower than screen
    else: camera_x = target_camera_x


    # --- Draw ---
    screen.fill(current_background_color)

    # Draw all sprites (offset by camera)
    # Blocks are part of all_sprites, so they'll be drawn.
    # Consider drawing order if needed (e.g., player on top of items)
    # Pygame's Group rendering order is usually addition order. Player added after blocks.
    for sprite in all_sprites:
        # Basic culling for sprites off-screen
        if sprite.rect.right - camera_x > 0 and sprite.rect.left - camera_x < SCREEN_WIDTH:
             screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))

    # Score and Level Display
    score_surf = score_font.render(f"Score: {score}", True, WHITE if current_background_color != LIGHT_BLUE else BLACK)
    level_surf = score_font.render(f"Level: {current_level_index + 1}/{MAX_LEVELS}", True, WHITE if current_background_color != LIGHT_BLUE else BLACK)
    screen.blit(score_surf, (10, 10))
    screen.blit(level_surf, (SCREEN_WIDTH - level_surf.get_width() - 10, 10))

    pygame.display.flip()
    clock.tick(FPS)

# --- Game Over/Quit ---
final_message_font = pygame.font.Font(None, 72)
if not running and current_level_index < MAX_LEVELS : # Game Over, not win
    msg_text = "GAME OVER"
elif not running and current_level_index >= MAX_LEVELS: # Win
     msg_text = "YOU WIN!"

if not pygame.display.get_init(): # If display was already closed by quit
    pass
else:
    if 'msg_text' in locals(): # only show if msg_text was defined
        msg_surf = final_message_font.render(msg_text, True, RED)
        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.fill(BLACK)
        screen.blit(msg_surf, msg_rect)
        pygame.display.flip()
        pygame.time.wait(3000) # Show for 3 seconds

pygame.quit()
sys.exit()
