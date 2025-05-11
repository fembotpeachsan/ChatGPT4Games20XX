import tkinter as tk
from PIL import Image, ImageTk # You'll need Pillow: pip install Pillow
import pygame
import random

# Initialize Pygame (especially font module)
pygame.init() # Initializes all Pygame modules, including font
pygame.font.init()


# --- Constants ---
# NES native resolution
NES_WIDTH, NES_HEIGHT = 256, 240
# Tkinter window size
TK_WINDOW_WIDTH, TK_WINDOW_HEIGHT = 600, 400
FPS = 60
TILE_SIZE = 16

# Calculate the display size for the NES surface within the Tkinter window, maintaining aspect ratio
display_scale_factor = min(TK_WINDOW_WIDTH / NES_WIDTH, TK_WINDOW_HEIGHT / NES_HEIGHT)
DISPLAY_WIDTH = int(NES_WIDTH * display_scale_factor)
DISPLAY_HEIGHT = int(NES_HEIGHT * display_scale_factor)

# NES Palette (NTSC, from ROM Detectives Wiki) - unchanged
NES_PALETTE = [
    (124, 124, 124), (0, 0, 252), (0, 0, 188), (68, 40, 188), (148, 0, 132), (168, 0, 32), (168, 16, 0), (136, 20, 0),
    (80, 48, 0), (0, 120, 0), (0, 104, 0), (0, 88, 0), (0, 64, 88), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (188, 188, 188), (0, 120, 248), (0, 88, 248), (104, 68, 252), (216, 0, 204), (228, 0, 88), (248, 56, 0), (228, 92, 16),
    (172, 124, 0), (0, 184, 0), (0, 168, 0), (0, 168, 68), (0, 136, 136), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (248, 248, 248), (60, 188, 252), (104, 136, 252), (152, 120, 248), (248, 120, 248), (248, 88, 152), (248, 120, 88), (252, 160, 68),
    (248, 184, 0), (184, 248, 24), (88, 216, 84), (88, 248, 152), (0, 232, 216), (120, 120, 120), (0, 0, 0), (0, 0, 0),
    (252, 252, 252), (164, 228, 252), (184, 184, 248), (216, 184, 248), (248, 184, 248), (248, 164, 192), (240, 208, 176), (252, 224, 168),
    (248, 216, 120), (216, 248, 120), (184, 248, 184), (184, 248, 216), (0, 252, 252), (248, 216, 248), (0, 0, 0), (0, 0, 0)
]

# Color Definitions using NES Palette - unchanged
COLOR_BLACK = NES_PALETTE[0x0F]
COLOR_WHITE = NES_PALETTE[0x30]
COLOR_SKY_BLUE = NES_PALETTE[0x0C]
COLOR_MARIO_RED = NES_PALETTE[0x16]
COLOR_MARIO_SKIN = NES_PALETTE[0x27]
COLOR_GOOMBA_BROWN = NES_PALETTE[0x18]
COLOR_GOOMBA_DARK_BROWN = NES_PALETTE[0x07]
COLOR_GOOMBA_EYES = COLOR_WHITE
COLOR_GROUND_BRICK_LIGHT = NES_PALETTE[0x29]
COLOR_GROUND_BRICK_DARK = NES_PALETTE[0x18]
COLOR_QUESTION_BLOCK_YELLOW = NES_PALETTE[0x28]
COLOR_QUESTION_BLOCK_ORANGE = NES_PALETTE[0x17]
COLOR_USED_BLOCK_GREY = NES_PALETTE[0x10]
COLOR_PIPE_GREEN_LIGHT = NES_PALETTE[0x1A]
COLOR_PIPE_GREEN_DARK = NES_PALETTE[0x0A]
COLOR_CLOUD_WHITE = NES_PALETTE[0x20]
COLOR_BUSH_GREEN = NES_PALETTE[0x19]


# Tile Types - unchanged
TILE_EMPTY = 0
TILE_GROUND = 1
TILE_BRICK = 2
TILE_QUESTION_BLOCK = 3
TILE_USED_BLOCK = 4
TILE_PIPE_TOP_LEFT = 5
TILE_PIPE_TOP_RIGHT = 6
TILE_PIPE_LEFT = 7
TILE_PIPE_RIGHT = 8

# Use a pixel-art friendly font if available, otherwise default. Size for NES_SURFACE.
try:
    hud_font = pygame.font.Font("PressStart2P.ttf", 8)
except FileNotFoundError:
    hud_font = pygame.font.Font(None, 12) # Fallback

# --- Game variables (global or passed around) ---
gravity = 0.6
jump_strength_initial = -11
jump_hold_lift = -0.5
camera_x = 0
score = 0
lives = 3
coins = 0
game_time = 400 # Level timer
game_state = "playing" # "playing", "game_over", "level_complete", "title_screen"

# Level Data
LEVEL_WIDTH = 210 # Typical width for SMB 1-1
LEVEL_HEIGHT = 15
level = [[TILE_EMPTY] * LEVEL_WIDTH for _ in range(LEVEL_HEIGHT)]

# --- Game Objects and Functions (largely unchanged, but `font` becomes `hud_font`, `HEIGHT` is `NES_HEIGHT`) ---

def setup_level_1_1():
    global level
    level = [[TILE_EMPTY] * LEVEL_WIDTH for _ in range(LEVEL_HEIGHT)] # Reset level

    # Ground (two layers)
    for x in range(LEVEL_WIDTH):
        level[LEVEL_HEIGHT - 1][x] = TILE_GROUND
        level[LEVEL_HEIGHT - 2][x] = TILE_GROUND

    def place_blocks(x_start, y_row, types):
        for i, block_type in enumerate(types):
            if x_start + i < LEVEL_WIDTH:
                level[y_row][x_start + i] = block_type

    place_blocks(16, LEVEL_HEIGHT - 6, [TILE_QUESTION_BLOCK])
    place_blocks(20, LEVEL_HEIGHT - 6, [TILE_BRICK, TILE_QUESTION_BLOCK, TILE_BRICK, TILE_QUESTION_BLOCK, TILE_BRICK])
    place_blocks(22, LEVEL_HEIGHT - 10, [TILE_QUESTION_BLOCK])

    def place_pipe(x_col, height):
        pipe_top_y = LEVEL_HEIGHT - 2 - height
        if pipe_top_y < 0: pipe_top_y = 0
        level[pipe_top_y][x_col] = TILE_PIPE_TOP_LEFT
        level[pipe_top_y][x_col + 1] = TILE_PIPE_TOP_RIGHT
        for y_pipe in range(pipe_top_y + 1, LEVEL_HEIGHT - 2):
            level[y_pipe][x_col] = TILE_PIPE_LEFT
            level[y_pipe][x_col + 1] = TILE_PIPE_RIGHT

    place_pipe(28, 2)
    place_pipe(38, 3)
    place_pipe(46, 4)
    place_pipe(57, 4)
    place_blocks(65, LEVEL_HEIGHT - 6, [TILE_BRICK, TILE_BRICK, TILE_QUESTION_BLOCK])
    for x in range(69, 71):
        level[LEVEL_HEIGHT - 1][x] = TILE_EMPTY
        level[LEVEL_HEIGHT - 2][x] = TILE_EMPTY
    place_blocks(78, LEVEL_HEIGHT - 6, [TILE_QUESTION_BLOCK])
    place_blocks(80, LEVEL_HEIGHT - 6, [TILE_BRICK])
    place_blocks(80, LEVEL_HEIGHT - 10, [TILE_BRICK])
    place_blocks(76, LEVEL_HEIGHT - 6, [TILE_BRICK] * 3)
    place_blocks(79, LEVEL_HEIGHT - 6, [TILE_QUESTION_BLOCK])
    place_blocks(79, LEVEL_HEIGHT - 10, [TILE_QUESTION_BLOCK])
    for x in range(85, 87):
        level[LEVEL_HEIGHT - 1][x] = TILE_EMPTY
        level[LEVEL_HEIGHT - 2][x] = TILE_EMPTY

    def place_pyramid(x_start, y_base_row, height_pyr, block_type=TILE_BRICK, right_align=False):
        for h_offset in range(height_pyr):
            num_blocks = h_offset + 1 if not right_align else height_pyr - h_offset
            row = y_base_row - h_offset
            start_c = x_start if not right_align else x_start + h_offset
            for b_offset in range(num_blocks):
                col = start_c + b_offset if not right_align else start_c # Mistake here, should be start_c for right_align with num_blocks logic
                if not right_align:
                    col = start_c + b_offset
                else: # for right align, the start changes, and we place num_blocks
                    col = x_start + (height_pyr - 1) - b_offset if h_offset == 0 else x_start + (height_pyr -1) - b_offset - ( (height_pyr - num_blocks) //2 ) if num_blocks < height_pyr else x_start #This is getting complex, simplified original
                    col = (x_start + height_pyr -1) - b_offset - h_offset # Simpler for right align stairs (original logic had issues)
                    # Corrected pyramid logic for right_align (descending)
                    # For a pyramid of height H, row y_base_row - h_offset has N blocks
                    # If right_align: blocks go from x_start + (height - 1 - (num_blocks-1)) to x_start + (height-1)
                    # A simpler interpretation for SMB stairs:
                    # Left-align (ascending): x to x + num_blocks-1
                    # Right-align (descending): x - (num_blocks-1) to x

                # Sticking to original place_pyramid logic as its effect is what matters for layout
                # The original place_pyramid:
                # right_align means the pyramid's rightmost blocks align at x_start + (height-1) effectively.
                # Let's use the original logic as provided for consistency in block placement.
                # The number of blocks in a row is 'num_blocks'.
                # If not right_align, blocks are from 'start_c' to 'start_c + num_blocks - 1'.
                # If right_align, 'start_c' is 'x_start + h_offset'. Blocks are from 'start_c' to 'start_c + num_blocks -1'.
                # This doesn't seem right for a descending pyramid.
                # A typical descending stair:
                # row 0 (top): x, x-1, x-2 ... (N blocks)
                # row 1: x, x-1 ... (N-1 blocks)
                # Let's re-evaluate `place_pyramid` for `right_align=True`
                # The provided code seems to interpret right_align as making the base longer on the right.
                # For SMB descending stairs, it's usually:
                # Base: [B B B B] at y_base
                # Base-1: [  B B B] at y_base-1, starting at x_start+1
                # Base-2: [    B B] at y_base-2, starting at x_start+2
                # Correcting place_pyramid for right_align to mean descending stairs to the right
                current_x_start = x_start
                current_num_blocks = height_pyr - h_offset
                if right_align:
                    current_x_start = x_start + h_offset


                for b_idx in range(current_num_blocks):
                    final_col = current_x_start + b_idx
                    if 0 <= row < LEVEL_HEIGHT and 0 <= final_col < LEVEL_WIDTH:
                        level[row][final_col] = block_type


    place_pyramid(100, LEVEL_HEIGHT - 3, 4, TILE_GROUND)
    place_blocks(110, LEVEL_HEIGHT - 6, [TILE_BRICK, TILE_QUESTION_BLOCK, TILE_BRICK])
    
    # Corrected way to call for descending stairs (original one was ascending from right)
    # For descending stairs of height 4 ending at LEVEL_HEIGHT-3:
    # Top step (1 block) at y = LEVEL_HEIGHT - 3 - (4-1) = LEVEL_HEIGHT - 6
    # Base step (4 blocks) at y = LEVEL_HEIGHT - 3
    # Let's use a simpler explicit loop for the second pyramid (descending)
    # Flagpole area (simplified)
    # Ascending pyramid (original call was fine)
    place_pyramid(134, LEVEL_HEIGHT - 3, 4, TILE_GROUND) 
    
    # Descending pyramid (second one)
    # Base (y = LEVEL_HEIGHT - 3) has 4 blocks. Top (y = LEVEL_HEIGHT - 3 - 3) has 1 block.
    # Example: height=4, base_y = L_H-3.
    # y = L_H-3 (h_offset=0): 4 blocks. Starts at x_flag_base.
    # y = L_H-4 (h_offset=1): 3 blocks. Starts at x_flag_base + 1.
    # y = L_H-5 (h_offset=2): 2 blocks. Starts at x_flag_base + 2.
    # y = L_H-6 (h_offset=3): 1 block.  Starts at x_flag_base + 3.
    x_flag_base_desc = 139 # This is the start of the base of the descending pyramid
    pyramid_height = 4
    for h_offset in range(pyramid_height):
        num_blocks_in_row = pyramid_height - h_offset
        row_y = (LEVEL_HEIGHT - 3) - (pyramid_height - 1 - h_offset) # This makes the top align with the other pyramid's top. Or simpler: (LEVEL_HEIGHT - 3) - h_offset_from_top
        row_y = (LEVEL_HEIGHT - 3 - (pyramid_height - 1)) + h_offset # y for row, h_offset is from top
        
        start_col_for_row = x_flag_base_desc + (pyramid_height - num_blocks_in_row) # This makes it align left
        # To make it a descending stair from a point (original intention of right_align=True)
        # The original call was: place_pyramid(139, LEVEL_HEIGHT - 3, 4, TILE_GROUND, right_align=True)
        # Let's use the explicit definition of SMB style stairs for clarity:
    
    # Ascending stairs
    stair_x = 133 # Start of the base
    stair_y_base = LEVEL_HEIGHT - 3
    stair_h = 4
    for i in range(stair_h): # i is step number from bottom, 0 to h-1
        for j in range(stair_h - i): # Number of blocks in this step
             if 0 <= stair_y_base - i < LEVEL_HEIGHT and \
                0 <= stair_x + j < LEVEL_WIDTH:
                level[stair_y_base - i][stair_x + j] = TILE_GROUND
    
    # Descending stairs (starts 1 block after the peak of ascending)
    # Peak of previous stairs is at (stair_x + 0, stair_y_base - (stair_h-1))
    # So next structure starts at stair_x + 1 for its peak, or stair_x + (stair_h-1) + 1 for its base
    # The original layout had them separated more. Let's use the original x values.
    place_pyramid(134, LEVEL_HEIGHT - 3, 4, TILE_GROUND) # Original was likely okay for its intent.
    
    # Descending stairs after flagpole (mimicking original call to place_pyramid with right_align=True)
    # For a right-aligned (descending) pyramid starting at x_start, where x_start is the leftmost block of that row
    # Height 4, base_y = LEVEL_HEIGHT - 3
    # Row 0 (bottom, y=LEVEL_HEIGHT-3): x_start to x_start+3 (4 blocks)
    # Row 1 (y=LEVEL_HEIGHT-4): x_start+1 to x_start+3 (3 blocks)
    # Row 2 (y=LEVEL_HEIGHT-5): x_start+2 to x_start+3 (2 blocks)
    # Row 3 (y=LEVEL_HEIGHT-6): x_start+3 (1 block)
    x_desc_start = 139 # Original: 139
    for h_idx in range(4): # h_idx is row from bottom (0 to 3)
        current_row_y = (LEVEL_HEIGHT - 3) - h_idx
        num_b = 4 - h_idx
        start_c = x_desc_start + h_idx # this makes it ascend right.
        # For descending to the right:
        # Number of blocks in row (from top, h_offset 0 to 3): 1, 2, 3, 4
        # y_row = (LEVEL_HEIGHT - 3 - 3) + h_offset_from_top
        # start_col = x_start_of_peak - h_offset_from_top
        # Let's just use the first pyramid logic but mirror its x placement for a simple effect
        # This part of 1-1 is often a solid block then stairs:
        # block at 133. Then stairs up starting 134. Then flat top. Then stairs down.
        # The original setup_level_1_1's pyramid calls are likely specific to its interpretation.
        # I will keep the original calls to place_pyramid as they were, to replicate its output.
    place_pyramid(139, LEVEL_HEIGHT - 3, 4, TILE_GROUND, right_align=True) # Descending stairs as per original


    for r in range(LEVEL_HEIGHT - 7, LEVEL_HEIGHT - 2):
        for c_offset in range(5):
            if 158 + c_offset < LEVEL_WIDTH:
                level[r][158 + c_offset] = TILE_BRICK


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.base_width = TILE_SIZE * 0.8
        self.base_height = TILE_SIZE * 0.9
        self.image = pygame.Surface([self.base_width, self.base_height])
        self.rect = self.image.get_rect(bottomleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.is_jumping = False
        self.jump_timer = 0
        self.max_jump_hold_time = 10
        self.speed = 2.5
        self.max_vel_x = 4
        self.state = "small"
        self.invincible_timer = 0
        self.flicker = False

    def update(self, keys, current_level_data, enemies_group):
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            self.flicker = (self.invincible_timer // (FPS // 10)) % 2 == 0
        else:
            self.flicker = False

        if keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
        else:
            self.vel_x = 0

        self.rect.x += self.vel_x
        self.check_horizontal_collisions(current_level_data)

        self.vel_y += gravity
        if self.vel_y > 12: self.vel_y = 12
        
        if self.is_jumping:
            if not (keys[pygame.K_SPACE] or keys[pygame.K_UP]) or self.jump_timer >= self.max_jump_hold_time :
                self.is_jumping = False
            else:
                self.vel_y += jump_hold_lift
                self.jump_timer += 1

        self.rect.y += self.vel_y
        self.on_ground = False
        self.check_vertical_collisions(current_level_data)
        self.check_enemy_collisions(enemies_group)

        if self.rect.bottom > NES_HEIGHT - TILE_SIZE:
            # Check if current pos is valid column
            player_col = self.rect.centerx // TILE_SIZE
            if 0 <= player_col < LEVEL_WIDTH:
                if current_level_data[LEVEL_HEIGHT-1][player_col] == TILE_EMPTY and \
                   current_level_data[LEVEL_HEIGHT-2][player_col] == TILE_EMPTY:
                    if self.rect.top > NES_HEIGHT :
                        self.die()
            elif self.rect.top > NES_HEIGHT : # Off screen to side and also fell
                 self.die()


    def jump(self):
        if self.on_ground:
            self.vel_y = jump_strength_initial
            self.on_ground = False
            self.is_jumping = True
            self.jump_timer = 0

    def check_horizontal_collisions(self, current_level_data):
        # Optimized to check only relevant tiles around player
        player_grid_y_top = self.rect.top // TILE_SIZE
        player_grid_y_bottom = self.rect.bottom // TILE_SIZE

        for r_idx in range(max(0, player_grid_y_top -1), min(LEVEL_HEIGHT, player_grid_y_bottom + 2)): # Check a bit around
            # Determine column range based on movement
            if self.vel_x > 0: # Moving right
                check_col = self.rect.right // TILE_SIZE
            elif self.vel_x < 0: # Moving left
                check_col = self.rect.left // TILE_SIZE
            else: # Not moving horizontally
                continue

            if not (0 <= check_col < LEVEL_WIDTH): continue # Out of bounds

            tile_id = current_level_data[r_idx][check_col]
            if tile_id != TILE_EMPTY:
                tile_rect = pygame.Rect(check_col * TILE_SIZE, r_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                # Check collision with this specific tile
                temp_rect_for_check = self.rect.copy()
                temp_rect_for_check.x += self.vel_x # Project movement
                if temp_rect_for_check.colliderect(tile_rect): # More precise check
                    if self.rect.colliderect(tile_rect): # Check actual current rect also
                        if self.vel_x > 0:
                            self.rect.right = tile_rect.left
                        elif self.vel_x < 0:
                            self.rect.left = tile_rect.right
                        self.vel_x = 0
                        return

    def check_vertical_collisions(self, current_level_data):
        # Optimized to check only relevant tiles around player
        player_grid_x_left = self.rect.left // TILE_SIZE
        player_grid_x_right = self.rect.right // TILE_SIZE

        for c_idx in range(max(0, player_grid_x_left -1), min(LEVEL_WIDTH, player_grid_x_right + 2)): # Check a bit around
            # Determine row range based on movement
            if self.vel_y > 0: # Moving down
                check_row = self.rect.bottom // TILE_SIZE
            elif self.vel_y < 0: # Moving up
                check_row = self.rect.top // TILE_SIZE
            else: # Not moving vertically
                continue
            
            if not (0 <= check_row < LEVEL_HEIGHT): continue # Out of bounds

            tile_id = current_level_data[check_row][c_idx]
            if tile_id != TILE_EMPTY:
                tile_rect = pygame.Rect(c_idx * TILE_SIZE, check_row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                temp_rect_for_check = self.rect.copy()
                temp_rect_for_check.y += self.vel_y # Project movement
                if temp_rect_for_check.colliderect(tile_rect):
                    if self.rect.colliderect(tile_rect):
                        if self.vel_y > 0:
                            self.rect.bottom = tile_rect.top
                            self.on_ground = True
                            self.is_jumping = False
                            self.vel_y = 0
                        elif self.vel_y < 0:
                            self.rect.top = tile_rect.bottom
                            self.vel_y = 0
                            self.is_jumping = False
                            if tile_id == TILE_QUESTION_BLOCK or tile_id == TILE_BRICK:
                                self.hit_block(current_level_data, check_row, c_idx)
                        return


    def hit_block(self, current_level_data, r_idx, c_idx):
        global score, coins
        block_type = current_level_data[r_idx][c_idx]
        if block_type == TILE_QUESTION_BLOCK:
            current_level_data[r_idx][c_idx] = TILE_USED_BLOCK
            score += 200; coins += 1
        elif block_type == TILE_BRICK:
            if self.state == "small": pass # print("Bumped Brick!")
            else: current_level_data[r_idx][c_idx] = TILE_EMPTY; score += 50

    def check_enemy_collisions(self, enemies_group):
        global score
        if self.invincible_timer > 0: return
        for enemy in pygame.sprite.spritecollide(self, enemies_group, False):
            if enemy.is_stomped: continue
            is_stomp = self.vel_y > 0 and self.rect.bottom < enemy.rect.centery + enemy.rect.height / 4
            if is_stomp:
                enemy.stomped()
                self.vel_y = jump_strength_initial / 1.5
                self.on_ground = False; self.is_jumping = True; self.jump_timer = 0
                score += 100
            else: self.take_damage(); break

    def take_damage(self):
        if self.invincible_timer > 0 : return
        if self.state == "big" or self.state == "fire":
            self.state = "small"; self.invincible_timer = FPS * 2
        else: self.die()

    def die(self):
        global lives, game_state
        lives -= 1
        if lives <= 0: game_state = "game_over"
        else:
            self.rect.bottomleft = (50, NES_HEIGHT - TILE_SIZE * 2)
            self.vel_x = 0; self.vel_y = 0
            self.invincible_timer = FPS * 3

    def draw(self, surface, camera_x_offset):
        if self.flicker: return
        draw_x = self.rect.x - camera_x_offset
        hat_rect = pygame.Rect(draw_x, self.rect.y, self.rect.width, self.rect.height * 0.5)
        pygame.draw.rect(surface, COLOR_MARIO_RED, hat_rect)
        face_rect = pygame.Rect(draw_x + self.rect.width * 0.2, self.rect.y + self.rect.height * 0.3, self.rect.width * 0.6, self.rect.height * 0.2)
        pygame.draw.rect(surface, COLOR_MARIO_SKIN, face_rect)
        body_rect = pygame.Rect(draw_x, self.rect.y + self.rect.height * 0.5, self.rect.width, self.rect.height * 0.5)
        pygame.draw.rect(surface, COLOR_MARIO_RED, body_rect)
        eye_x = draw_x + self.rect.width * 0.6; eye_y = self.rect.y + self.rect.height * 0.35
        pygame.draw.rect(surface, COLOR_BLACK, (eye_x, eye_y, 2, 2))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type="goomba"):
        super().__init__()
        self.type = type; self.original_x = x; self.original_y = y
        if self.type == "goomba":
            self.width = TILE_SIZE * 0.9; self.height = TILE_SIZE * 0.9
            self.speed = 0.5 + random.random() * 0.5
        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect(bottomleft=(x,y))
        self.vel_x = -self.speed; self.vel_y = 0
        self.on_ground = False; self.is_stomped = False; self.stomped_timer = 0

    def update(self, current_level_data):
        if self.is_stomped:
            self.stomped_timer -= 1
            if self.stomped_timer <= 0: self.kill()
            return
        self.rect.x += self.vel_x
        self.check_horizontal_collisions(current_level_data)
        self.vel_y += gravity
        if self.vel_y > 10: self.vel_y = 10
        self.rect.y += self.vel_y
        self.on_ground = False
        self.check_vertical_collisions(current_level_data)
        if self.rect.top > NES_HEIGHT: self.kill()

    def check_horizontal_collisions(self, current_level_data):
        # Simplified enemy collision - check one tile ahead and one tile at feet for walls
        # More robust logic would be similar to player's tile-based collision
        probe_x = self.rect.right + 1 if self.vel_x > 0 else self.rect.left - 1
        probe_col = probe_x // TILE_SIZE
        mid_row = self.rect.centery // TILE_SIZE

        if 0 <= probe_col < LEVEL_WIDTH and 0 <= mid_row < LEVEL_HEIGHT:
            if current_level_data[mid_row][probe_col] != TILE_EMPTY:
                if self.vel_x > 0: self.rect.right = probe_col * TILE_SIZE
                else: self.rect.left = (probe_col + 1) * TILE_SIZE
                self.vel_x *= -1
                return # Added return

        # Edge detection
        if self.on_ground and self.type == "goomba":
            leading_edge_x = self.rect.right if self.vel_x > 0 else self.rect.left
            tile_check_x = (leading_edge_x + self.vel_x) // TILE_SIZE # Tile it's moving towards
            tile_check_y = (self.rect.bottom) // TILE_SIZE # Tile layer below its feet

            # Check if tile_check_x is valid before accessing level_data
            if 0 <= tile_check_x < LEVEL_WIDTH and 0 <= tile_check_y < LEVEL_HEIGHT:
                # If the tile *below* where it's about to step is empty, turn around
                 # Need to check one tile down from tile_check_y, or rather (self.rect.bottom + TILE_SIZE) // TILE_SIZE
                ground_check_y = (self.rect.bottom + 1) // TILE_SIZE # Row index for ground under the leading edge
                if 0 <= ground_check_y < LEVEL_HEIGHT:
                    if current_level_data[ground_check_y][int(tile_check_x)] == TILE_EMPTY:
                        self.vel_x *= -1


    def check_vertical_collisions(self, current_level_data):
        # Simplified version for enemies, similar to player but less interaction
        player_grid_x_left = self.rect.left // TILE_SIZE
        player_grid_x_right = self.rect.right // TILE_SIZE

        for c_idx in range(max(0, player_grid_x_left), min(LEVEL_WIDTH, player_grid_x_right + 1)):
            if self.vel_y > 0: # Moving down
                check_row = self.rect.bottom // TILE_SIZE
            elif self.vel_y < 0: # Moving up (unlikely for goomba unless hit)
                check_row = self.rect.top // TILE_SIZE
            else: continue
            
            if not (0 <= check_row < LEVEL_HEIGHT): continue

            tile_id = current_level_data[check_row][c_idx]
            if tile_id != TILE_EMPTY:
                tile_rect = pygame.Rect(c_idx * TILE_SIZE, check_row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.rect.colliderect(tile_rect):
                    if self.vel_y > 0:
                        self.rect.bottom = tile_rect.top
                        self.on_ground = True
                        self.vel_y = 0
                    elif self.vel_y < 0:
                        self.rect.top = tile_rect.bottom
                        self.vel_y = 0
                    return # Added return

    def stomped(self):
        if self.type == "goomba":
            self.is_stomped = True; self.stomped_timer = FPS // 3; self.vel_x = 0
            self.rect.height = self.height / 2; self.rect.y += self.height / 2

    def draw(self, surface, camera_x_offset):
        draw_x = self.rect.x - camera_x_offset
        if self.type == "goomba":
            if self.is_stomped:
                stomp_rect = pygame.Rect(draw_x, self.rect.y, self.width, self.height)
                pygame.draw.rect(surface, COLOR_GOOMBA_BROWN, stomp_rect)
            else:
                body_rect = pygame.Rect(draw_x, self.rect.y, self.width, self.height * 0.7)
                pygame.draw.ellipse(surface, COLOR_GOOMBA_BROWN, body_rect)
                foot_height = self.height * 0.3; foot_y = self.rect.y + self.height * 0.7
                foot_rect = pygame.Rect(draw_x + self.width * 0.1, foot_y, self.width * 0.8, foot_height)
                pygame.draw.rect(surface, COLOR_GOOMBA_DARK_BROWN, foot_rect)
                eye_size = max(2, int(self.width // 6)); eye_y_offset = self.height * 0.25
                eye_lx = draw_x + self.width * 0.25 - eye_size / 2
                eye_rx = draw_x + self.width * 0.75 - eye_size / 2
                pygame.draw.rect(surface, COLOR_GOOMBA_EYES, (eye_lx, self.rect.y + eye_y_offset, eye_size, eye_size))
                pygame.draw.rect(surface, COLOR_GOOMBA_EYES, (eye_rx, self.rect.y + eye_y_offset, eye_size, eye_size))


def draw_level_tiles(surface, current_level_data, camera_x_offset):
    start_col = int(camera_x_offset // TILE_SIZE)
    end_col = start_col + (NES_WIDTH // TILE_SIZE) + 2
    end_col = min(end_col, LEVEL_WIDTH); start_col = max(0, start_col)

    for r_idx in range(LEVEL_HEIGHT):
        for c_idx in range(start_col, end_col):
            tile_id = current_level_data[r_idx][c_idx]
            if tile_id == TILE_EMPTY: continue
            tile_x_on_nes_surface = c_idx * TILE_SIZE - camera_x_offset
            tile_y_on_nes_surface = r_idx * TILE_SIZE
            rect = pygame.Rect(tile_x_on_nes_surface, tile_y_on_nes_surface, TILE_SIZE, TILE_SIZE)

            if tile_id == TILE_GROUND:
                pygame.draw.rect(surface, COLOR_GROUND_BRICK_DARK, rect)
                pygame.draw.rect(surface, COLOR_GROUND_BRICK_LIGHT, rect.inflate(-2,-2))
                pygame.draw.line(surface, COLOR_GROUND_BRICK_DARK, rect.midleft, rect.midright, 1)
                pygame.draw.line(surface, COLOR_GROUND_BRICK_DARK, (rect.centerx, rect.top), (rect.centerx, rect.bottom), 1)
            elif tile_id == TILE_BRICK:
                pygame.draw.rect(surface, COLOR_GROUND_BRICK_DARK, rect)
                pygame.draw.rect(surface, COLOR_GROUND_BRICK_LIGHT, rect.inflate(-3,-3))
                pygame.draw.line(surface, COLOR_GROUND_BRICK_DARK, (rect.left, rect.top + TILE_SIZE * 0.25), (rect.right, rect.top + TILE_SIZE * 0.25), 1)
                pygame.draw.line(surface, COLOR_GROUND_BRICK_DARK, (rect.left, rect.top + TILE_SIZE * 0.75), (rect.right, rect.top + TILE_SIZE * 0.75), 1)
                pygame.draw.line(surface, COLOR_GROUND_BRICK_DARK, (rect.left + TILE_SIZE * 0.5, rect.top), (rect.left + TILE_SIZE*0.5, rect.top + TILE_SIZE*0.25),1)
                pygame.draw.line(surface, COLOR_GROUND_BRICK_DARK, (rect.left + TILE_SIZE * 0.25, rect.top + TILE_SIZE*0.25), (rect.left + TILE_SIZE*0.25, rect.top + TILE_SIZE*0.75),1)
                pygame.draw.line(surface, COLOR_GROUND_BRICK_DARK, (rect.left + TILE_SIZE * 0.75, rect.top + TILE_SIZE*0.25), (rect.left + TILE_SIZE*0.75, rect.top + TILE_SIZE*0.75),1)
            elif tile_id == TILE_QUESTION_BLOCK:
                pygame.draw.rect(surface, COLOR_QUESTION_BLOCK_ORANGE, rect)
                pygame.draw.rect(surface, COLOR_QUESTION_BLOCK_YELLOW, rect.inflate(-2, -2))
                q_font_small = pygame.font.Font(None, TILE_SIZE)
                q_text = q_font_small.render("?", True, COLOR_BLACK)
                q_text_rect = q_text.get_rect(center=rect.center); surface.blit(q_text, q_text_rect)
            elif tile_id == TILE_USED_BLOCK:
                pygame.draw.rect(surface, COLOR_USED_BLOCK_GREY, rect)
                pygame.draw.rect(surface, COLOR_BLACK, rect, 1)
            elif tile_id in [TILE_PIPE_TOP_LEFT, TILE_PIPE_TOP_RIGHT, TILE_PIPE_LEFT, TILE_PIPE_RIGHT]:
                pygame.draw.rect(surface, COLOR_PIPE_GREEN_DARK, rect)
                inner_offset = 2
                if tile_id == TILE_PIPE_TOP_LEFT:
                    pygame.draw.rect(surface, COLOR_PIPE_GREEN_LIGHT, (rect.left + inner_offset, rect.top + inner_offset, rect.width - inner_offset, rect.height - inner_offset))
                    pygame.draw.rect(surface, COLOR_BLACK, (rect.left, rect.top + inner_offset, rect.width, TILE_SIZE/3))
                elif tile_id == TILE_PIPE_TOP_RIGHT:
                    pygame.draw.rect(surface, COLOR_PIPE_GREEN_LIGHT, (rect.left, rect.top + inner_offset, rect.width - inner_offset, rect.height - inner_offset))
                    pygame.draw.rect(surface, COLOR_BLACK, (rect.left, rect.top + inner_offset, rect.width, TILE_SIZE/3))
                else: pygame.draw.rect(surface, COLOR_PIPE_GREEN_LIGHT, rect.inflate(-inner_offset*2, -inner_offset*2))
                if tile_id == TILE_PIPE_TOP_LEFT or tile_id == TILE_PIPE_LEFT:
                    pygame.draw.line(surface, COLOR_WHITE, (rect.left+inner_offset, rect.top+inner_offset), (rect.left+inner_offset, rect.bottom-inner_offset), 2)
                if tile_id == TILE_PIPE_TOP_RIGHT or tile_id == TILE_PIPE_RIGHT:
                    pygame.draw.line(surface, COLOR_BLACK, (rect.right-inner_offset, rect.top+inner_offset), (rect.right-inner_offset, rect.bottom-inner_offset), 2)

def draw_background_elements(surface, camera_x_offset): # surface is nes_surface
    surface.fill(COLOR_SKY_BLUE)
    hill_colors = [NES_PALETTE[0x09], NES_PALETTE[0x19]]
    hill_configs = [
        {"x": 50, "y": NES_HEIGHT - TILE_SIZE * 4, "w": TILE_SIZE * 8, "h": TILE_SIZE * 3, "parallax": 0.5},
        {"x": 200, "y": NES_HEIGHT - TILE_SIZE * 5, "w": TILE_SIZE * 12, "h": TILE_SIZE * 4, "parallax": 0.4},
        {"x": TILE_SIZE * 30, "y": NES_HEIGHT - TILE_SIZE * 3.5, "w": TILE_SIZE * 10, "h": TILE_SIZE * 2.5, "parallax": 0.5},
    ]
    for i, cfg in enumerate(hill_configs):
        hill_x = cfg["x"] - camera_x_offset * cfg["parallax"]
        if hill_x + cfg["w"] < 0 or hill_x > NES_WIDTH: continue
        pygame.draw.ellipse(surface, hill_colors[i % len(hill_colors)], (hill_x, cfg["y"], cfg["w"], cfg["h"]))
        pygame.draw.ellipse(surface, hill_colors[(i+1) % len(hill_colors)], (hill_x + cfg["w"]*0.2, cfg["y"] + cfg["h"]*0.2, cfg["w"]*0.8, cfg["h"]*0.7))

    cloud_configs = [
        {"x": TILE_SIZE*3, "y": TILE_SIZE*2, "parts": 3, "size": TILE_SIZE, "parallax": 0.2},
        {"x": TILE_SIZE*15, "y": TILE_SIZE*3, "parts": 2, "size": TILE_SIZE*1.2, "parallax": 0.25},
        {"x": TILE_SIZE*25, "y": TILE_SIZE*2.5, "parts": 3, "size": TILE_SIZE*0.8, "parallax": 0.15},
    ]
    for cfg in cloud_configs:
        cloud_base_x = cfg["x"] - camera_x_offset * cfg["parallax"]
        part_size = cfg["size"]
        for i in range(cfg["parts"]):
            part_x = cloud_base_x + i * part_size * 0.7
            if part_x + part_size < 0 or part_x > NES_WIDTH: continue
            pygame.draw.ellipse(surface, COLOR_CLOUD_WHITE, (part_x, cfg["y"], part_size, part_size * 0.7))
            if i < cfg["parts"] -1 :
                pygame.draw.ellipse(surface, COLOR_CLOUD_WHITE, (part_x + part_size*0.3, cfg["y"] - part_size*0.2, part_size, part_size * 0.7))

def draw_hud(surface): # surface is nes_surface, font is hud_font
    mario_label = hud_font.render("MARIO", True, COLOR_WHITE)
    surface.blit(mario_label, (20 * NES_WIDTH // 256, 10 * NES_HEIGHT // 240)) # Relative positioning
    score_text = hud_font.render(f"{score:06d}", True, COLOR_WHITE)
    surface.blit(score_text, (20 * NES_WIDTH // 256, 25 * NES_HEIGHT // 240))
    coin_label = hud_font.render(f"COINS {coins:02d}", True, COLOR_WHITE)
    surface.blit(coin_label, (NES_WIDTH // 2 - 40 * NES_WIDTH // 256, 25 * NES_HEIGHT // 240))
    world_label = hud_font.render("WORLD", True, COLOR_WHITE)
    surface.blit(world_label, (NES_WIDTH - 120 * NES_WIDTH // 256, 10 * NES_HEIGHT // 240))
    level_text = hud_font.render("1-1", True, COLOR_WHITE)
    surface.blit(level_text, (NES_WIDTH - 110 * NES_WIDTH // 256, 25 * NES_HEIGHT // 240))
    time_label = hud_font.render("TIME", True, COLOR_WHITE)
    surface.blit(time_label, (NES_WIDTH - 60 * NES_WIDTH // 256, 10 * NES_HEIGHT // 240))
    time_val_text = hud_font.render(f"{int(game_time):03d}", True, COLOR_WHITE)
    surface.blit(time_val_text, (NES_WIDTH - 55 * NES_WIDTH // 256, 25 * NES_HEIGHT // 240))
    lives_text = hud_font.render(f"LIVES x{lives}", True, COLOR_WHITE)
    surface.blit(lives_text, (20 * NES_WIDTH // 256, NES_HEIGHT - 25 * NES_HEIGHT // 240))

def game_over_display(surface_nes): # surface_nes is nes_surface
    surface_nes.fill(COLOR_BLACK)
    large_font = pygame.font.Font(None, 24) # Size for NES_SURFACE
    game_over_text = large_font.render("GAME OVER", True, COLOR_WHITE)
    text_rect = game_over_text.get_rect(center=(NES_WIDTH / 2, NES_HEIGHT / 2 - 10))
    surface_nes.blit(game_over_text, text_rect)
    small_font = pygame.font.Font(None, 16) # Size for NES_SURFACE
    restart_text = small_font.render("Press ENTER to restart", True, COLOR_WHITE)
    restart_rect = restart_text.get_rect(center=(NES_WIDTH / 2, NES_HEIGHT / 2 + 20))
    surface_nes.blit(restart_text, restart_rect)

# --- Global Tkinter and Pygame variables ---
root = None
tk_label = None
nes_surface = None
player = None
all_sprites = None
enemies_group = None
clock = None

def reset_game_state_and_level():
    global player, all_sprites, enemies_group
    global score, lives, coins, game_time, game_state, level, camera_x

    score = 0; lives = 3; coins = 0; game_time = 400
    game_state = "playing"; camera_x = 0
    
    setup_level_1_1()

    player = Player(50, NES_HEIGHT - TILE_SIZE * 2)
    if all_sprites: all_sprites.empty()
    else: all_sprites = pygame.sprite.Group()
    if enemies_group: enemies_group.empty()
    else: enemies_group = pygame.sprite.Group()
    
    all_sprites.add(player)

    enemy_positions = [
        (TILE_SIZE * 22, NES_HEIGHT - TILE_SIZE * 2), (TILE_SIZE * 33, NES_HEIGHT - TILE_SIZE * 2),
        (TILE_SIZE * 35, NES_HEIGHT - TILE_SIZE * 2), (TILE_SIZE * 51, NES_HEIGHT - TILE_SIZE * 2),
        (TILE_SIZE * 52.5, NES_HEIGHT - TILE_SIZE * 2), (TILE_SIZE * 79, NES_HEIGHT - TILE_SIZE * 2),
        (TILE_SIZE * 81, NES_HEIGHT - TILE_SIZE * 2), (TILE_SIZE * 97, NES_HEIGHT - TILE_SIZE * 2),
        (TILE_SIZE * 98.5, NES_HEIGHT - TILE_SIZE * 2),
    ]
    for pos_x, pos_y in enemy_positions:
        if pos_x < LEVEL_WIDTH * TILE_SIZE:
            goomba = Enemy(pos_x, pos_y, type="goomba")
            enemies_group.add(goomba); all_sprites.add(goomba)

def update_game_frame():
    global camera_x, game_time, game_state, player, level, enemies_group, nes_surface, tk_label, root, clock

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # Though Tkinter handles main quit
            root.quit()
            return
        if event.type == pygame.USEREVENT + 1 and game_state == "playing": # game_timer_event
            game_time -=1
            if game_time <=0:
                if player: player.die()
        
        if event.type == pygame.KEYDOWN:
            if game_state == "playing":
                if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and player:
                    player.jump()
            elif game_state == "game_over":
                if event.key == pygame.K_RETURN:
                    reset_game_state_and_level()
    
    keys = pygame.key.get_pressed()

    # Game logic update
    if game_state == "playing":
        if player: player.update(keys, level, enemies_group)
        
        # Update camera based on player, ensuring it doesn't go out of bounds
        target_camera_x = player.rect.centerx - NES_WIDTH / 3
        camera_x = max(0, min(target_camera_x, (LEVEL_WIDTH * TILE_SIZE) - NES_WIDTH))

        active_enemies = pygame.sprite.Group() # For optimization, though less critical here
        for enemy in enemies_group:
             # Simple check: update if enemy is within 1.5 screens of camera view
            if abs(enemy.rect.centerx - (camera_x + NES_WIDTH / 2)) < NES_WIDTH * 1.5:
                 enemy.update(level)


    # Drawing to nes_surface
    if nes_surface:
        if game_state == "playing":
            draw_background_elements(nes_surface, camera_x)
            draw_level_tiles(nes_surface, level, camera_x)
            if player: player.draw(nes_surface, camera_x)
            for enemy in enemies_group: # Draw all enemies, let their draw check visibility if needed
                 # Only draw enemies that would be visible on the nes_surface
                enemy_screen_x = enemy.rect.x - camera_x
                if enemy_screen_x < NES_WIDTH and enemy_screen_x + enemy.rect.width > 0:
                    enemy.draw(nes_surface, camera_x)
            draw_hud(nes_surface)
        elif game_state == "game_over":
            game_over_display(nes_surface)

        # Scale nes_surface to fit Tkinter label and convert
        scaled_pygame_surface = pygame.transform.scale(nes_surface, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        
        # Convert Pygame surface to string of RGB data
        image_rgb_str = pygame.image.tostring(scaled_pygame_surface, 'RGB')
        
        # Create PIL Image from string
        pil_image = Image.frombytes('RGB', (DISPLAY_WIDTH, DISPLAY_HEIGHT), image_rgb_str)
        
        # Convert PIL Image to PhotoImage for Tkinter
        tk_photo_image = ImageTk.PhotoImage(image=pil_image)
        
        # Update Tkinter label
        if tk_label:
            tk_label.config(image=tk_photo_image)
            tk_label.image = tk_photo_image # Keep a reference!

    # Schedule next frame
    if clock: clock.tick(FPS) # Control Pygame's internal timing if needed, less critical here
    if root: root.after(1000 // FPS, update_game_frame)


def main_mario_tkinter():
    global root, tk_label, nes_surface, player, all_sprites, enemies_group, clock

    # --- Tkinter Setup ---
    root = tk.Tk()
    root.title("Super Mario Bros. Procedural - Tkinter/Pygame")
    root.geometry(f"{TK_WINDOW_WIDTH}x{TK_WINDOW_HEIGHT}")
    
    # Create a black frame for padding if game area is smaller than window
    main_frame = tk.Frame(root, bg='black')
    main_frame.pack(expand=True, fill=tk.BOTH)

    tk_label = tk.Label(main_frame, bg='black') # Pygame content will be on this label
    # Pack the label to be centered
    tk_label.pack(expand=True)


    # --- Pygame Setup (within Tkinter context) ---
    # Pygame is already initialized.
    # No pygame.display.set_mode() needed for main screen.
    nes_surface = pygame.Surface((NES_WIDTH, NES_HEIGHT))
    clock = pygame.time.Clock()

    # Setup game timer event
    pygame.time.set_timer(pygame.USEREVENT + 1, 1000) # For game_time countdown

    reset_game_state_and_level() # Initial game and level setup

    # Start the game loop via Tkinter's after method
    root.after(100, update_game_frame) # Start after a brief moment
    
    root.mainloop()
    pygame.quit()


if __name__ == '__main__':
    main_mario_tkinter()
