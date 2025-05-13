import pygame as pg
import asyncio
import platform
import random
import math # For SuperLeaf sine wave

# Game Configuration
SCREEN_WIDTH = 768
SCREEN_HEIGHT = 672
FPS = 60
TILE_SIZE = 48  # Each tile is 16 chars * PIXEL_SCALE = 16 * 3 = 48 pixels
PIXEL_SCALE = 3

# Physics Constants
GRAVITY = 0.8
PLAYER_ACCEL = 0.8
PLAYER_FRICTION = -0.15
PLAYER_MAX_SPEED_X = 6
PLAYER_JUMP_POWER = 17 # Might need tweaking for SMB3 feel
MAX_FALL_SPEED = 15
ENEMY_MOVE_SPEED = 1

# --- SMB3 Color Map (Hallucinated Palette Data) ---
TRANSPARENT_CHAR = 'T'
SMB3_COLOR_MAP = {
    'T': (0,0,0,0),      # Transparent
    'R': (220, 0, 0),    # Mario Red
    'B': (0, 80, 200),   # Mario Blue overalls
    'S': (255, 200, 150),# Mario Skin
    'Y': (255, 240, 30), # Question Block Yellow
    'O': (210, 120, 30), # Block Orange/Brown (Bricks, Used Q-Block)
    'o': (160, 80, 20),  # Block Darker Orange/Brown (Shading)
    'K': (10, 10, 10),   # Black (Outlines, Eyes, Mario Hair)
    'W': (250, 250, 250),# White (Eyes, '?' on Q-block)
    'G': (0, 180, 0),    # Leaf Green / Pipe Green / Flag Green
    'g': (140, 70, 20),  # Ground Brown / Leaf Stem accent
    'N': (130, 80, 50),  # Goomba Brown Body
    'n': (80, 50, 30),   # Goomba Dark Brown Feet / Mario Shoes
    'L': (90, 200, 255), # Sky Blue (Background)
    'F': (100, 200, 50), # Leaf Light Green part
    'X': (190, 190, 190),# Light Grey (Q-Block Rivets, Flagpole)
    'D': (60, 60, 60),   # Dark Grey (general shadow/detail)
    'U': (180, 100, 60)  # Used Block main color (slightly different from brick)
}
color_map = SMB3_COLOR_MAP # Use this globally
BACKGROUND_COLOR = color_map['L']


# --- SMB3 Asset Definitions (Hallucinated ROM Graphics Data) ---

# Small Mario (Right Facing - SMB3 Style)
SMB3_MARIO_SMALL_IDLE_R_ART = [ # Standing
    "TTTTTRRRRTTTTTTT",
    "TTTTRRRRRRTTTTTT",
    "TTTKKSSSKRTTTTTT", 
    "TTKSRSRSKRTTTTTT",
    "TTKSSSSSKRTTTTTT",
    "TTTKRKRRKTTTTTTT", 
    "TTBBBBBBBBTTTTTT", 
    "TTBBRBBBRBTTTTTT",
    "TTTRRnnRRTTTTTTT", 
    "TTTRnnnnRTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]
SMB3_MARIO_SMALL_WALK_R_ART_1 = [ # Walk frame 1
    "TTTTTRRRRTTTTTTT",
    "TTTTRRRRRRTTTTTT",
    "TTTKKSSSKRTTTTTT",
    "TTKSRSRSKRTTTTTT",
    "TTKSSSSSKRTTTTTT",
    "TTTKRKRRKTTTTTTT",
    "TTBBBBBBBBTTTTTT",
    "TTBBRBBBRBTTTTTT",
    "TTTRRTRnRTTTTTTT", 
    "TTTRnnnnRTTTTTTT",
    "TTTTTTnnTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]
SMB3_MARIO_SMALL_WALK_R_ART_2 = [ # Walk frame 2
    "TTTTTRRRRTTTTTTT",
    "TTTTRRRRRRTTTTTT",
    "TTTKKSSSKRTTTTTT",
    "TTKSRSRSKRTTTTTT",
    "TTKSSSSSKRTTTTTT",
    "TTTKRKRRKTTTTTTT",
    "TTBBBBBBBBTTTTTT",
    "TTBBRBBBRBTTTTTT",
    "TTTRRnnRRTTTTTTT", 
    "TTTRTRTRRTTTTTTT",
    "TTTTTTnnTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]
SMB3_MARIO_SMALL_JUMP_R_ART = [ # Jumping
    "TTTTTRRRRTTTTTTT",
    "TTTTRRRRRRTTTTTT",
    "TTTKKSSSKBBTTTTT", 
    "TTKSRSRSKBBTTTTT",
    "TTKSSSSSKRTTTTTT",
    "TTTKRKRRKTTTTTTT",
    "TTBBBBBBBBTTTTTT",
    "TTBBRBBBRBTTTTTT",
    "TTTTRnRTRTTTTTTT", 
    "TTTTRnRnRTTTTTTT",
    "TTTTnnTTnnTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]

# Goomba (SMB3 Style)
SMB3_GOOMBA_WALK1_ART = [
    "TTTTNNNNNNTTTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTNNWWKKWWNNTTTT", 
    "TTNKKWWWWKKNNTTT", 
    "TTNNNNNNNNNNTTTT",
    "TTNNNNNNNNNNNNTT",
    "TTTNNNNNNNNTTTTT",
    "TTTTNNNNNNTTTTTT",
    "TTTTTnnnnTTTTTTT", 
    "TTTTNnnnnNTTTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]
SMB3_GOOMBA_WALK2_ART = [ # Second walk frame for Goomba
    "TTTTNNNNNNTTTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTNNWWKKWWNNTTTT",
    "TTNKKWWWWKKNNTTT",
    "TTNNNNNNNNNNTTTT",
    "TTNNNNNNNNNNNNTT",
    "TTTNNNNNNNNTTTTT",
    "TTTTNNNNNNTTTTTT",
    "TTTTnnNNnnTTTTTT", 
    "TTTTNnnnnNTTTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]
SMB3_GOOMBA_SQUISHED_ART = [ # Goomba when squished
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTNNNNNNTTTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTNNWWKKWWNNTTTT",
    "TTNKKWWWWKKNNTTT",
    "TTNNNNNNNNNNTTTT",
    "TTNNNNNNNNNNNNTT",
    "TTTNNNNNNNNTTTTT",
    "TTTTNNNNNNTTTTTT",
    "TTTTTnnnnTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]


# Brick Block (SMB3 Style) - Orangey-brown
SMB3_BRICK_BLOCK_ART = [
    "OOOOOOOOOOOOOOOO", 
    "OKKOoKKOoKKOoKKO", 
    "OOOOOOOOOOOOOOOO",
    "OoKKOoKKOoKKOoKK",
    "OOOOOOOOOOOOOOOO",
    "OKKOoKKOoKKOoKKO",
    "OOOOOOOOOOOOOOOO",
    "OoKKOoKKOoKKOoKK",
    "OOOOOOOOOOOOOOOO",
    "OKKOoKKOoKKOoKKO",
    "OOOOOOOOOOOOOOOO",
    "OoKKOoKKOoKKOoKK",
    "OOOOOOOOOOOOOOOO",
    "OKKOoKKOoKKOoKKO",
    "OOOOOOOOOOOOOOOO",
    "oooooooooooooooo"
]

# Question Block (SMB3 Style)
SMB3_QUESTION_BLOCK_ART_FRAME1 = [
    "YYYYYYYYYYYYYYYY", 
    "YXWYYYYYYYWXYYYY", 
    "YWKKWYYYYYWKKYWY", 
    "YTWKKWYYYWKKWTYY", 
    "YTTWKKWWKKWTTTYY",
    "YTTTWKWWKWTTTTYY",
    "YTTTTWWWWTTTTTYY",
    "YTTTTWKKWTTTTTYY",
    "YTTTTWKKWTTTTTYY",
    "YTTTTWWWWTTTTTYY",
    "YXTTKWKKWKTTTXYY",
    "YWWWWKKKKWWWWWYW", 
    "YYYYYYYYYYYYYYYY",
    "YXXXXXXXXXXXXXXY", 
    "YooooooooooooooY", 
    "oooooooooooooooo"
]
SMB3_QUESTION_BLOCK_ART_FRAME2 = [ # Slight '?' animation (e.g. shimmer)
    "YYYYYYYYYYYYYYYY",
    "YXWYYYYYYYWXYYYY",
    "YWKKYYYYYYWKKYWY", 
    "YTWKKWYYYWKKWTYY",
    "YTTWKKWWKKWTTTYY",
    "YTTTWKWWKWTTTTYY",
    "YTTTTWKKWTTTTTYY", 
    "YTTTTWKKWTTTTTYY",
    "YTTTTWWWWTTTTTYY",
    "YTTTTWWWWTTTTTYY",
    "YXTTKWWWWKTTTXYY", 
    "YWWWWKKKKWWWWWYW",
    "YYYYYYYYYYYYYYYY",
    "YXXXXXXXXXXXXXXY",
    "YooooooooooooooY",
    "oooooooooooooooo"
]
SMB3_USED_BLOCK_ART = [ # After hit, becomes a plain darker block
    "UUUUUUUUUUUUUUUU", 
    "UooUooUooUooUooU", 
    "UooUooUooUooUooU",
    "UUUUUUUUUUUUUUUU",
    "UooUooUooUooUooU",
    "UooUooUooUooUooU",
    "UUUUUUUUUUUUUUUU",
    "UooUooUooUooUooU",
    "UooUooUooUooUooU",
    "UUUUUUUUUUUUUUUU",
    "UooUooUooUooUooU",
    "UooUooUooUooUooU",
    "UUUUUUUUUUUUUUUU",
    "UooUooUooUooUooU",
    "UooUooUooUooUooU",
    "oooooooooooooooo"
]

# Ground Block (SMB3 Style) - Brownish with some pattern
SMB3_GROUND_BLOCK_ART = [
    "gggggggggggggggg", 
    "gOgOgOgOgOgOgOgO", 
    "gOgOgOgOgOgOgOgO",
    "gggggggggggggggg",
    "gggggggggggggggg",
    "gggggggggggggggg",
    "DDDDDDDDDDDDDDDD", 
    "DDDDDDDDDDDDDDDD",
    "gggggggggggggggg",
    "gOgOgOgOgOgOgOgO",
    "gOgOgOgOgOgOgOgO",
    "gggggggggggggggg",
    "gggggggggggggggg",
    "gggggggggggggggg",
    "DDDDDDDDDDDDDDDD",
    "DDDDDDDDDDDDDDDD"
]

# Super Leaf (SMB3 Style)
SMB3_SUPER_LEAF_ART = [
    "TTTTTTGGTTTTTTTT", 
    "TTTTTGGGGTTTTTTT",
    "TTTTGGGGGGTTTTTT",
    "TTTGGFFFFFFGTTTT", 
    "TTGGFFFFFFFFGTTT",
    "TTGFFFFgFFFFFGTT", 
    "TTGFFFggFFFFFGTT",
    "TTGFFFggFFFFFGTT",
    "TTTGFFggggFFGTTT",
    "TTTTGFFggFFGTTTT",
    "TTTTTGFFGGTTTTTT",
    "TTTTTTGggGTTTTTT", 
    "TTTTTTTggTTTTTTT",
    "TTTTTTTggTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]

# Flagpole (SMB3 Style - simplified)
SMB3_FLAGPOLE_ART = [
    "TTTTTTTTXTTTTTTT", 
    "TTTTTTGGGXTTTTTT", 
    "TTTTTGGGGGXTTTTT",
    "TTTTGGGGGGXTTTTT",
    "TTTGGGGGGGXTTTTT",
    "TTTTGGGGGXTTTTTT",
    "TTTTTTGGGXTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT"
]

# SNES-like Graphics Functions
def build_sprite_palette(pixel_art_rows):
    palette = [(0,0,0,0)] 
    unique_colors_in_art = set()
    for row in pixel_art_rows:
        for char_code in row:
            if char_code != TRANSPARENT_CHAR and char_code in color_map:
                unique_colors_in_art.add(color_map[char_code])
    
    sorted_unique_colors = sorted(list(unique_colors_in_art), key=lambda c: (c[0], c[1], c[2]))
    palette.extend(sorted_unique_colors)
    return palette

def create_snes_tile_indices(pixel_art_rows, palette):
    tile_indices = []
    for row_str in pixel_art_rows:
        indices_for_row = []
        for char_code in row_str:
            if char_code == TRANSPARENT_CHAR:
                indices_for_row.append(0) 
            else:
                actual_color_tuple = color_map.get(char_code)
                if actual_color_tuple:
                    try:
                        indices_for_row.append(palette.index(actual_color_tuple))
                    except ValueError: 
                        indices_for_row.append(0) 
                else: 
                    indices_for_row.append(0) 
        tile_indices.append(indices_for_row)
    return tile_indices

def draw_snes_tile_indexed(screen, tile_indices, palette, x, y, scale):
    for r_idx, row_of_indices in enumerate(tile_indices):
        for c_idx, palette_idx in enumerate(row_of_indices):
            if palette_idx != 0: 
                color_tuple = palette[palette_idx]
                pg.draw.rect(screen, color_tuple, (x + c_idx * scale, y + r_idx * scale, scale, scale))

# Classes
class AnimatedSprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.animation_frames = {}
        self.current_frame_index = 0 # Renamed from current_frame_idx for clarity
        self.animation_speed = 0.1 
        self.animation_timer = 0
        self.image_scale = PIXEL_SCALE
        self.state = "idle"
        self.facing_left = False

    def load_animation_frames(self, action_name, frame_art_list_right):
        key_r = f"{action_name}_right"
        processed_frames_r = []
        for art_strings in frame_art_list_right:
            palette = build_sprite_palette(art_strings)
            indices = create_snes_tile_indices(art_strings, palette)
            processed_frames_r.append((indices, palette))
        self.animation_frames[key_r] = processed_frames_r

        key_l = f"{action_name}_left"
        processed_frames_l = []
        for art_strings in frame_art_list_right: 
            flipped_art_strings = flip_pixel_art(art_strings)
            palette = build_sprite_palette(flipped_art_strings) 
            indices = create_snes_tile_indices(flipped_art_strings, palette)
            processed_frames_l.append((indices, palette))
        self.animation_frames[key_l] = processed_frames_l


    def get_current_animation_set(self):
        direction = "left" if self.facing_left else "right"
        key = f"{self.state}_{direction}"
        return self.animation_frames.get(key, self.animation_frames.get("idle_right", [([[]], [(0,0,0,0)])]))


    def update_animation(self, dt):
        self.animation_timer += dt * FPS * self.animation_speed # Corrected timer update
        current_animation_set = self.get_current_animation_set()
        if not current_animation_set or not current_animation_set[0][0]: 
            return

        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(current_animation_set)

    def draw(self, screen, camera_offset_x, camera_offset_y):
        current_animation_set = self.get_current_animation_set()
        if not current_animation_set or not current_animation_set[0][0]: 
             return

        if self.current_frame_index >= len(current_animation_set): 
            self.current_frame_index = 0
        
        tile_indices, palette = current_animation_set[self.current_frame_index]
        if not tile_indices: 
            return

        draw_snes_tile_indexed(screen, tile_indices, palette, 
                               self.rect.x - camera_offset_x, 
                               self.rect.y - camera_offset_y, 
                               self.image_scale)

def flip_pixel_art(pixel_art_rows):
    return ["".join(reversed(row)) for row in pixel_art_rows]

class Player(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.vel = pg.math.Vector2(0, 0)
        self.acc = pg.math.Vector2(0, 0)
        self.is_super_form = False 
        self.set_form(small=True) 
        self.on_ground = False
        self.can_jump = True 
        self.score = 0
        self.lives = 3
        self.invincible_timer = 0 

    def set_form(self, small=False): 
        self.animation_frames = {} 
        self.is_super_form = False 
        self.art_height_chars = 16 
        self.player_height_tiles = 1 
        
        self.load_animation_frames("idle", [SMB3_MARIO_SMALL_IDLE_R_ART])
        self.load_animation_frames("walk", [SMB3_MARIO_SMALL_WALK_R_ART_1, SMB3_MARIO_SMALL_WALK_R_ART_2])
        self.load_animation_frames("jump", [SMB3_MARIO_SMALL_JUMP_R_ART])
        
        current_x, current_y = self.pos.x, self.pos.y
        self.rect = pg.Rect(current_x, current_y, TILE_SIZE, self.player_height_tiles * TILE_SIZE)
        self.pos.x = self.rect.x 
        self.pos.y = self.rect.y


    def jump(self):
        if self.on_ground:
            self.vel.y = -PLAYER_JUMP_POWER
            self.on_ground = False
            self.can_jump = False 

    def update(self, dt, platforms):
        self.acc = pg.math.Vector2(0, GRAVITY)
        keys = pg.key.get_pressed()

        if self.invincible_timer > 0:
            self.invincible_timer -= 1 

        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACCEL
            self.facing_left = True
        elif keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACCEL
            self.facing_left = False
        
        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel.x += self.acc.x # Simplified: acc is already per-frame
        if abs(self.vel.x) < 0.1: self.vel.x = 0 # Stop if very slow

        self.vel.x = max(-PLAYER_MAX_SPEED_X, min(self.vel.x, PLAYER_MAX_SPEED_X))
        
        self.pos.x += self.vel.x
        self.rect.x = round(self.pos.x)
        self.collide_with_platforms_x(platforms)

        if keys[pg.K_SPACE]:
            if self.can_jump and self.on_ground: # Ensure on_ground for jump as well
                 self.jump()
        else: 
            self.can_jump = True

        self.vel.y += self.acc.y 
        self.vel.y = min(self.vel.y, MAX_FALL_SPEED) 
        self.pos.y += self.vel.y
        self.rect.y = round(self.pos.y)
        
        self.on_ground = False 
        self.collide_with_platforms_y(platforms)

        if not self.on_ground:
            self.state = "jump"
        elif abs(self.vel.x) > 0.1: 
            self.state = "walk"
        else:
            self.state = "idle"
        
        self.update_animation(dt) # Pass dt here

        if self.rect.top > SCREEN_HEIGHT + TILE_SIZE * 2: 
            self.die()

    def collide_with_platforms_x(self, platforms):
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.x > 0: 
                    self.rect.right = plat.rect.left
                    self.vel.x = 0
                elif self.vel.x < 0: 
                    self.rect.left = plat.rect.right
                    self.vel.x = 0
                self.pos.x = self.rect.x

    def collide_with_platforms_y(self, platforms):
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.y > 0: 
                    self.rect.bottom = plat.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0: 
                    self.rect.top = plat.rect.bottom
                    self.vel.y = 0 
                    if hasattr(plat, 'hit_from_bottom'):
                        plat.hit_from_bottom(self) 
                self.pos.y = self.rect.y
    
    def die(self):
        self.lives -= 1
        if self.lives > 0:
            self.game.reset_level_soft() 
        else:
            self.game.game_over = True


class Block(AnimatedSprite): 
    def __init__(self, game, x_tile, y_tile, art_frames_list, solid=True, block_type="generic"):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        self.load_animation_frames("idle", art_frames_list) 
        self.solid = solid
        self.block_type = block_type
        self.animation_speed = 0 

    def update(self, dt): 
        if self.animation_speed > 0:
             self.update_animation(dt)

class BrickBlock(Block):
    def __init__(self, game, x_tile, y_tile):
        super().__init__(game, x_tile, y_tile, [SMB3_BRICK_BLOCK_ART], solid=True, block_type="brick")

    def hit_from_bottom(self, player):
        if player.is_super_form: 
             pass 
        else:
            pass


class QuestionBlock(Block):
    def __init__(self, game, x_tile, y_tile):
        super().__init__(game, x_tile, y_tile, 
                         [SMB3_QUESTION_BLOCK_ART_FRAME1, SMB3_QUESTION_BLOCK_ART_FRAME2], 
                         solid=True, block_type="qblock")
        self.is_active = True 
        self.animation_speed = 0.05 # Slower animation for Q-block '?'

    def hit_from_bottom(self, player):
        if self.is_active:
            self.is_active = False
            self.animation_speed = 0 
            self.load_animation_frames("idle", [SMB3_USED_BLOCK_ART]) 
            self.current_frame_index = 0 

            leaf = SuperLeaf(self.game, self.pos.x / TILE_SIZE, self.pos.y / TILE_SIZE) # Spawn at block's original tile
            self.game.all_sprites.add(leaf)
            self.game.items.add(leaf)


class GroundBlock(Block):
    def __init__(self, game, x_tile, y_tile):
        super().__init__(game, x_tile, y_tile, [SMB3_GROUND_BLOCK_ART], solid=True, block_type="ground")

class Goomba(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        self.load_animation_frames("walk", [SMB3_GOOMBA_WALK1_ART, SMB3_GOOMBA_WALK2_ART])
        self.load_animation_frames("squished", [SMB3_GOOMBA_SQUISHED_ART]) 
        self.vel = pg.math.Vector2(-ENEMY_MOVE_SPEED, 0) 
        self.state = "walk"
        self.animation_speed = 0.08 # Adjusted animation speed
        self.squish_timer = 0 

    def update(self, dt, platforms):
        if self.state == "walk":
            self.pos.x += self.vel.x 
            self.rect.x = round(self.pos.x)
            
            collided_x = False
            for plat in platforms: 
                if plat.solid and self.rect.colliderect(plat.rect):
                    if self.vel.x > 0: 
                        self.rect.right = plat.rect.left
                        self.vel.x *= -1
                        self.facing_left = True
                    elif self.vel.x < 0: 
                        self.rect.left = plat.rect.right
                        self.vel.x *= -1
                        self.facing_left = False
                    self.pos.x = self.rect.x
                    collided_x = True
                    break
            if not collided_x: # Check for edges if no direct collision
                # Simple edge detection: raycast down one step ahead
                # For now, they only turn at obstacles.
                pass

            self.update_animation(dt) # Pass dt

        elif self.state == "squished":
            self.squish_timer -= 1 # simple frame count timer
            if self.squish_timer <= 0:
                self.kill() 

    def get_current_animation_set(self): 
        if self.state == "squished":
            # Squished art isn't typically directional, provide a fallback
            return self.animation_frames.get("squished_right", self.animation_frames.get("squished_left", []))
        return super().get_current_animation_set()


class SuperLeaf(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile_spawn_base): 
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, (y_tile_spawn_base -1) * TILE_SIZE) # Start above block
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        self.load_animation_frames("idle", [SMB3_SUPER_LEAF_ART]) 
        
        self.vel = pg.math.Vector2(0,0) # Initial vel, set in rising
        self.on_ground = False
        
        self.spawn_state = "rising" 
        self.rise_target_y = (y_tile_spawn_base - 1) * TILE_SIZE - (TILE_SIZE * 0.5) # Target Y after rising
        self.rise_speed = -1 # Pixels per update step (negative is up)
        
        self.drift_amplitude_y = TILE_SIZE / 3 
        self.drift_frequency_y = 0.03 
        self.drift_timer_y = random.uniform(0, 2 * math.pi) 
        self.base_y_drift = 0 

    def update(self, dt, platforms):
        if self.spawn_state == "rising":
            self.pos.y += self.rise_speed 
            if self.pos.y <= self.rise_target_y:
                self.pos.y = self.rise_target_y
                self.spawn_state = "drifting"
                self.base_y_drift = self.pos.y 
                self.vel.x = random.choice([ENEMY_MOVE_SPEED * 0.5, -ENEMY_MOVE_SPEED * 0.5])


        elif self.spawn_state == "drifting":
            self.pos.x += self.vel.x 
            
            self.drift_timer_y += self.drift_frequency_y * FPS * dt # Use dt for frequency
            offset_y = self.drift_amplitude_y * math.sin(self.drift_timer_y)
            self.pos.y = self.base_y_drift + offset_y

            self.rect.x = round(self.pos.x)
            self.rect.y = round(self.pos.y)

            for plat in platforms:
                if plat.solid and self.rect.colliderect(plat.rect):
                    if self.vel.x > 0 and self.rect.right > plat.rect.left:
                        self.rect.right = plat.rect.left
                        self.vel.x *= -1
                    elif self.vel.x < 0 and self.rect.left < plat.rect.right:
                        self.rect.left = plat.rect.right
                        self.vel.x *= -1
                    self.pos.x = self.rect.x
                    
                    # Rudimentary landing, items usually don't land solidly on blocks while drifting
                    # We can let it pass through or stop if it hits a certain y_level relative to a block
                    # For now, it just reverses horizontal direction

        elif self.spawn_state == "landed":
            pass

        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.update_animation(dt) 


class Flagpole(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE * 4) 
        self.load_animation_frames("idle", [SMB3_FLAGPOLE_ART])
        self.animation_speed = 0 

class Camera:
    def __init__(self, width_tiles, height_tiles): 
        self.camera_rect_on_screen = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.offset = pg.math.Vector2(0, 0) 
        self.world_width_pixels = 0 
        self.world_height_pixels = 0 

    def update(self, target_player):
        target_cam_x = -target_player.rect.centerx + SCREEN_WIDTH // 2
        clamped_cam_x = min(0, max(target_cam_x, -(self.world_width_pixels - SCREEN_WIDTH)))
        clamped_cam_y = 0 

        self.offset.x = clamped_cam_x
        self.offset.y = clamped_cam_y
        
    def get_world_view_rect(self): 
        return pg.Rect(-self.offset.x, -self.offset.y, SCREEN_WIDTH, SCREEN_HEIGHT)


# Level and Overworld Data
LEVEL_1_1_DATA = [ 
    "..........................................................................................F.",
    "..........................................................................................F.",
    "..................BBQB....................................................................F.",
    "..........................................................................................F.",
    ".........................BBBB.........QQQ.................................................F.",
    "..........................................................................................F.",
    "...................E................E.........E.E.........................................F.",
    "GGGGGGGGGGGGGGGGGGGGGGGG...GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG...GGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGG...GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG...GGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG" 
]
LEVEL_1_2_DATA = [ # Example of a second level
    "..................................................F.",
    "..................................................F.",
    "............Q....B................................F.",
    "..................................................F.",
    ".......E............E.............................F.",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
]

OVERWORLD_DATA = [
    "                    ",
    " . 1 . 2 . . . . .  ", # Player starts implied near '1' or defined by mario_overworld_pos
    " . . . . . . . . .  ",
    " . . . . . . . . .  ",
    " . . . . . . . . .  ",
    " . . . . . . . . .  ",
    " . . . . . . . . .  ", 
    "                    "
]

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("SMB3 Style Game Engine - Hallucinated ROM")
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, TILE_SIZE // 2) # Scaled font
        
        self.game_state = "overworld" 
        self.overworld_data = OVERWORLD_DATA
        self.mario_overworld_pos = (2,1) # Initial position on Overworld (col, row)
        
        # Find first level node for default mario_overworld_pos if 'P' not used
        found_first_level_node = False
        for r, row in enumerate(self.overworld_data):
            for c, char_code in enumerate(row):
                if char_code.isdigit() or (char_code.isalpha() and char_code != 'P'):
                    self.mario_overworld_pos = (c,r)
                    found_first_level_node = True
                    break
            if found_first_level_node:
                break
        
        self.overworld_cell_size = TILE_SIZE 

        self.levels = {'1': LEVEL_1_1_DATA, '2': LEVEL_1_2_DATA} 
        
        self.game_over = False
        self.debug_mode = False 

        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group() 
        self.enemies = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.flagpoles = pg.sprite.Group() 

        self.player = None 
        self.camera = Camera(0,0) 

        self.current_level_char = '1' 

    def load_level(self, level_data_str_array):
        self.all_sprites.empty()
        self.platforms.empty()
        self.enemies.empty()
        self.items.empty()
        self.flagpoles.empty()

        player_start_pos_tiles = (2, len(level_data_str_array) - 4) # Adjusted default start y

        for row_idx, row_str in enumerate(level_data_str_array):
            for col_idx, char_code in enumerate(row_str):
                x_pos = col_idx * TILE_SIZE
                y_pos = row_idx * TILE_SIZE
                
                if char_code == 'G':
                    block = GroundBlock(self, col_idx, row_idx)
                    self.all_sprites.add(block)
                    self.platforms.add(block)
                elif char_code == 'B':
                    block = BrickBlock(self, col_idx, row_idx)
                    self.all_sprites.add(block)
                    self.platforms.add(block)
                elif char_code == 'Q':
                    block = QuestionBlock(self, col_idx, row_idx)
                    self.all_sprites.add(block)
                    self.platforms.add(block)
                elif char_code == 'E':
                    enemy = Goomba(self, col_idx, row_idx)
                    self.all_sprites.add(enemy)
                    self.enemies.add(enemy)
                elif char_code == 'F': 
                    flagpole = Flagpole(self, col_idx, row_idx)
                    self.all_sprites.add(flagpole)
                    self.flagpoles.add(flagpole)
        
        # Preserve player's existing lives and score if reloading mid-game (e.g., after death)
        prev_lives = self.player.lives if self.player else 3
        prev_score = self.player.score if self.player else 0

        self.player = Player(self, player_start_pos_tiles[0], player_start_pos_tiles[1])
        self.player.lives = prev_lives
        self.player.score = prev_score
        self.all_sprites.add(self.player)
        
        level_width_pixels = len(level_data_str_array[0]) * TILE_SIZE
        level_height_pixels = len(level_data_str_array) * TILE_SIZE
        self.camera = Camera(level_width_pixels // TILE_SIZE, level_height_pixels // TILE_SIZE)
        self.camera.world_width_pixels = level_width_pixels
        self.camera.world_height_pixels = level_height_pixels


    def enter_level(self, level_char_id):
        if level_char_id in self.levels:
            self.current_level_char = level_char_id
            # Reset player object (or re-init with persistent score/lives if needed)
            # For now, a fresh player instance for the level, lives/score reset
            if self.player: # Keep score and lives if player exists
                current_score = self.player.score
                current_lives = self.player.lives
                self.load_level(self.levels[level_char_id])
                self.player.score = current_score
                self.player.lives = current_lives
            else: # First time loading a level
                self.load_level(self.levels[level_char_id])
                self.player.score = 0
                self.player.lives = 3

            self.game_state = "level"
            self.game_over = False 

    def complete_level(self):
        self.game_state = "overworld" 
        # Player's mario_overworld_pos remains on the completed level node.

    def reset_level_soft(self): 
        if self.player:
            # Score is kept, lives are already decremented by Player.die()
            current_score = self.player.score 
            current_lives = self.player.lives 
            self.load_level(self.levels[self.current_level_char]) # Reloads level, player re-created
            self.player.score = current_score
            self.player.lives = current_lives
            if self.player.lives <= 0: 
                self.game_over = True
        else: # Should not happen if player died, but as a fallback
            self.enter_level(self.current_level_char) # Full reset for the level

    def reset_game_hard(self): 
        self.game_over = False
        # Reset score and lives, go to the current level the player was on in overworld
        level_to_start = self.overworld_data[self.mario_overworld_pos[1]][self.mario_overworld_pos[0]]
        if level_to_start not in self.levels: # Fallback to level '1'
            level_to_start = '1'
            # Try to find '1' on the map and set mario_overworld_pos
            found_level_1_node = False
            for r_idx, r_str in enumerate(self.overworld_data):
                if found_level_1_node: break
                for c_idx, char in enumerate(r_str):
                    if char == '1':
                        self.mario_overworld_pos = (c_idx, r_idx)
                        found_level_1_node = True
                        break

        self.enter_level(level_to_start) 
        if self.player: # enter_level re-creates player, so set score/lives after
            self.player.score = 0
            self.player.lives = 3


    def draw_overworld(self):
        self.screen.fill(BACKGROUND_COLOR) 
        ow_tile_size = self.overworld_cell_size
        for r, row_str in enumerate(self.overworld_data):
            for c, char_code in enumerate(row_str):
                x, y = c * ow_tile_size, r * ow_tile_size
                rect = (x, y, ow_tile_size, ow_tile_size)
                if char_code == ' ': 
                    pg.draw.rect(self.screen, color_map['B'], rect, 1) # Path border
                elif char_code == '.': 
                    pg.draw.rect(self.screen, color_map['G'], rect) 
                elif char_code.isdigit() or (char_code.isalpha() and char_code not in 'P'): 
                    pg.draw.rect(self.screen, color_map['Y'], rect) 
                    self.draw_text(char_code, x + ow_tile_size // 3, y + ow_tile_size // 3, 'K') # Center text a bit
        
        mario_ow_x = self.mario_overworld_pos[0] * ow_tile_size
        mario_ow_y = self.mario_overworld_pos[1] * ow_tile_size
        pg.draw.rect(self.screen, color_map['R'], 
                     (mario_ow_x + ow_tile_size//4, mario_ow_y + ow_tile_size//4, 
                      ow_tile_size//2, ow_tile_size//2)) # Smaller Mario marker


    def draw_text(self, text_str, x, y, color_char_code='W', Sfont=None):
        if Sfont is None: Sfont = self.font
        text_surface = Sfont.render(text_str, True, color_map[color_char_code])
        self.screen.blit(text_surface, (x,y))

    async def main(self):
        running = True
        dt_accumulator = 0.0 # For fixed physics updates if desired, not fully implemented here
        fixed_dt = 1/FPS # Target time per physics frame

        while running:
            raw_dt = self.clock.tick(FPS) / 1000.0 # Delta time in seconds
            
            # For a simple game loop, using raw_dt directly for updates is often fine.
            # If physics becomes unstable, a fixed timestep loop might be needed.
            # For now, player/enemy updates use a simplified notion of dt or assume per-frame logic.
            # Let's pass raw_dt to update methods for consistency.

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    return
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
                        return
                    if event.key == pg.K_F1: 
                        self.debug_mode = not self.debug_mode
                    
                    if self.game_state == "level":
                        if self.game_over and event.key == pg.K_r:
                            self.reset_game_hard()

                    elif self.game_state == "overworld":
                        # Keyboard navigation for overworld (optional if mouse is primary)
                        # ... (keep existing keyboard nav or remove if mouse-only)
                        pass 
                
                if self.game_state == "overworld":
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1: # Left mouse click
                            mouse_x, mouse_y = event.pos
                            clicked_col = mouse_x // self.overworld_cell_size
                            clicked_row = mouse_y // self.overworld_cell_size

                            if (0 <= clicked_row < len(self.overworld_data) and
                                0 <= clicked_col < len(self.overworld_data[0])):
                                char_at_click = self.overworld_data[clicked_row][clicked_col]
                                if char_at_click in self.levels:
                                    self.mario_overworld_pos = (clicked_col, clicked_row) # Move Mario marker
                                    self.enter_level(char_at_click)
            
            # --- Update Logic ---
            # Player and enemy updates now expect dt to scale their movements/timers
            # The current player/enemy updates are a mix of per-frame and dt-scaled.
            # For simplicity, we'll treat their internal logic as per-frame and pass raw_dt for animation.
            if self.game_state == "level" and not self.game_over:
                self.player.update(raw_dt, self.platforms) # Pass raw_dt
                for enemy in list(self.enemies): 
                    enemy.update(raw_dt, self.platforms) # Pass raw_dt
                for item in list(self.items):
                    item.update(raw_dt, self.platforms) # Pass raw_dt
                
                self.camera.update(self.player)

                if self.player.invincible_timer <= 0:
                    for enemy in list(self.enemies): 
                        if isinstance(enemy, Goomba) and enemy.state == "walk":
                            if self.player.rect.colliderect(enemy.rect):
                                if (self.player.vel.y > 0 and 
                                    self.player.rect.bottom < enemy.rect.centery + TILE_SIZE / 4 and 
                                    not self.player.on_ground): 
                                    
                                    enemy.state = "squished"
                                    enemy.animation_speed = 0 
                                    enemy.current_frame_index = 0 
                                    enemy.vel.x = 0
                                    enemy.squish_timer = FPS // 2 # Show for 0.5 sec approx
                                    self.player.vel.y = -PLAYER_JUMP_POWER / 2.5 # Smaller bounce
                                    self.player.score += 100
                                else: 
                                    self.player.die() 
                                    break 
                
                for item in list(self.items):
                    if self.player.rect.colliderect(item.rect):
                        if isinstance(item, SuperLeaf):
                            self.player.score += 1000
                        item.kill() 

                for flagpole in self.flagpoles:
                    if self.player.rect.colliderect(flagpole.rect):
                        self.complete_level()
                        break 
            
            # --- Drawing Logic ---
            self.screen.fill(BACKGROUND_COLOR) 

            if self.game_state == "overworld":
                self.draw_overworld()
            elif self.game_state == "level":
                world_view = self.camera.get_world_view_rect()
                for sprite in self.all_sprites:
                    if sprite.rect.colliderect(world_view): 
                         sprite.draw(self.screen, self.camera.offset.x, self.camera.offset.y)
                
                if self.player:
                    self.draw_text(f"SCORE: {self.player.score}", 20, 10, 'W')
                    self.draw_text(f"LIVES: {self.player.lives}", SCREEN_WIDTH - 150, 10, 'W')

                if self.game_over:
                    overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
                    overlay.fill((50, 50, 50, 180)) 
                    self.screen.blit(overlay, (0,0))
                    large_font = pg.font.Font(None, TILE_SIZE) # Larger font for Game Over
                    self.draw_text("GAME OVER", SCREEN_WIDTH // 2 - TILE_SIZE * 2.5, SCREEN_HEIGHT // 2 - TILE_SIZE, 'R', large_font)
                    self.draw_text("Press R to Restart", SCREEN_WIDTH // 2 - TILE_SIZE * 3, SCREEN_HEIGHT // 2 + TILE_SIZE //2, 'W')
            
            pg.display.flip()
            await asyncio.sleep(0) 

        pg.quit()


if __name__ == "__main__":
    game_instance = Game()
    asyncio.run(game_instance.main())
