import pygame as pg
# import asyncio # Removed, Pygame's loop is synchronous
import platform # platform module is imported but not used. Consider removing if not needed.
import random
import math # For SuperLeaf sine wave

# Game Configuration
SCREEN_WIDTH = 768
SCREEN_HEIGHT = 672
FPS = 60
TILE_SIZE = 48  # Each tile is 16 chars * PIXEL_SCALE = 16 * 3 = 48 pixels
PIXEL_SCALE = 3

# Physics Constants (These are key for the "SMB3 feel" and will require tuning)
GRAVITY = 0.8
PLAYER_ACCEL = 0.8
PLAYER_FRICTION = -0.15
PLAYER_MAX_SPEED_X = 6
PLAYER_JUMP_POWER = 17 # User noted: "Might need tweaking for SMB3 feel" - this is very true!
MAX_FALL_SPEED = 15
ENEMY_MOVE_SPEED = 1

# --- SMB3 Color Map (Hallucinated Palette Data) ---
TRANSPARENT_CHAR = 'T'
SMB3_COLOR_MAP = {
    'T': (0,0,0,0),     # Transparent
    'R': (220, 0, 0),     # Mario Red
    'B': (0, 80, 200),    # Mario Blue overalls
    'S': (255, 200, 150), # Mario Skin
    'Y': (255, 240, 30),  # Question Block Yellow
    'O': (210, 120, 30),  # Block Orange/Brown (Bricks, Used Q-Block)
    'o': (160, 80, 20),   # Block Darker Orange/Brown (Shading)
    'K': (10, 10, 10),    # Black (Outlines, Eyes, Mario Hair)
    'W': (250, 250, 250), # White (Eyes, '?' on Q-block)
    'G': (0, 180, 0),     # Leaf Green / Pipe Green / Flag Green
    'g': (140, 70, 20),   # Ground Brown / Leaf Stem accent
    'N': (130, 80, 50),   # Goomba Brown Body
    'n': (80, 50, 30),    # Goomba Dark Brown Feet / Mario Shoes
    'L': (90, 200, 255),  # Sky Blue (Background)
    'F': (100, 200, 50),  # Leaf Light Green part
    'X': (190, 190, 190), # Light Grey (Q-Block Rivets, Flagpole)
    'D': (60, 60, 60),    # Dark Grey (general shadow/detail)
    'U': (180, 100, 60)   # Used Block main color (slightly different from brick)
}
color_map = SMB3_COLOR_MAP # Use this globally
BACKGROUND_COLOR = color_map['L']


# --- SMB3 Asset Definitions (Hallucinated ROM Graphics Data) ---
# Ensure all art strings are consistently 16 characters wide for proper rendering.

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
    "TTTTNNNNNNTTTTTT", # Squished body starts lower
    "TTTNNNNNNNNTTTTT",
    "TTNNWWKKWWNNTTTT",
    "TTNKKWWWWKKNNTTT",
    "TTNNNNNNNNNNTTTT",
    "TTNNNNNNNNNNNNTT", # This line might be too much for a squish
    "TTTNNNNNNNNTTTTT", # This line might be too much for a squish
    "TTTTNNNNNNTTTTTT", # This line might be too much for a squish
    "TTTTTnnnnTTTTTTT", # Feet remain
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
    "YTTTTWWWWTTTTTYY", # One W shifts in '?'
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
    "DDDDDDDDDDDDDDDD", # Dark line for depth/texture
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
    "TTGFFFFgFFFFFGTT", # 'g' for stem/darker part
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
SMB3_FLAGPOLE_ART = [ # Represents the pole itself, flag would be separate or part of animation
    "TTTTTTTTXTTTTTTT", # Top ball of flagpole
    "TTTTTTGGGXTTTTTT", # Example of a flag part (can be animated)
    "TTTTTGGGGGXTTTTT",
    "TTTTGGGGGGXTTTTT",
    "TTTGGGGGGGXTTTTT",
    "TTTTGGGGGXTTTTTT",
    "TTTTTTGGGXTTTTTT",
    "TTTTTTTTXTTTTTTT", # Pole segment
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
    """Builds a compact palette for a given sprite art."""
    palette = [(0,0,0,0)] # Index 0 is always transparent
    unique_colors_in_art = set()
    for row in pixel_art_rows:
        for char_code in row:
            if char_code != TRANSPARENT_CHAR and char_code in color_map:
                unique_colors_in_art.add(color_map[char_code])
    
    # Sort for consistent palette order, though not strictly necessary for functionality
    sorted_unique_colors = sorted(list(unique_colors_in_art), key=lambda c: (c[0], c[1], c[2]))
    palette.extend(sorted_unique_colors)
    return palette

def create_snes_tile_indices(pixel_art_rows, palette):
    """Converts character-based art into palette indices."""
    tile_indices = []
    for row_str in pixel_art_rows:
        indices_for_row = []
        for char_code in row_str:
            if char_code == TRANSPARENT_CHAR:
                indices_for_row.append(0) # Transparent index
            else:
                actual_color_tuple = color_map.get(char_code)
                if actual_color_tuple:
                    try:
                        indices_for_row.append(palette.index(actual_color_tuple))
                    except ValueError: # Color in art but not in this sprite's built palette (should not happen if build_sprite_palette is correct)
                        indices_for_row.append(0) # Default to transparent if error
                else: # Character not in global color_map
                    indices_for_row.append(0) # Default to transparent
        tile_indices.append(indices_for_row)
    return tile_indices

def draw_snes_tile_indexed(screen, tile_indices, palette, x, y, scale):
    """Draws a tile using indexed colors and a local palette."""
    for r_idx, row_of_indices in enumerate(tile_indices):
        for c_idx, palette_idx in enumerate(row_of_indices):
            if palette_idx != 0: # Skip transparent pixels (index 0)
                # Ensure palette_idx is within bounds
                if 0 < palette_idx < len(palette):
                    color_tuple = palette[palette_idx]
                    pg.draw.rect(screen, color_tuple, (x + c_idx * scale, y + r_idx * scale, scale, scale))
                # else: print(f"Warning: palette_idx {palette_idx} out of bounds for palette size {len(palette)}")


# Classes
class AnimatedSprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.animation_frames = {} # Stores {(indices, palette), ...} for each animation state
        self.current_frame_index = 0
        self.animation_speed = 0.1 # Time (in terms of 1/FPS ticks) per animation frame
        self.animation_timer = 0
        self.image_scale = PIXEL_SCALE
        self.state = "idle" # e.g., "idle", "walk", "jump"
        self.facing_left = False
        self.rect = pg.Rect(0,0,TILE_SIZE,TILE_SIZE) # Default rect, should be set by subclasses

    def load_animation_frames(self, action_name, frame_art_list_right):
        """Loads and processes animation frames from art strings for right-facing."""
        key_r = f"{action_name}_right"
        processed_frames_r = []
        for art_strings in frame_art_list_right:
            palette = build_sprite_palette(art_strings)
            indices = create_snes_tile_indices(art_strings, palette)
            processed_frames_r.append((indices, palette))
        self.animation_frames[key_r] = processed_frames_r

        # Create left-facing frames by flipping the right-facing ones
        key_l = f"{action_name}_left"
        processed_frames_l = []
        for art_strings in frame_art_list_right: # Use original right-facing art to flip
            flipped_art_strings = flip_pixel_art(art_strings)
            # Palette might be different for flipped art if colors are used asymmetrically,
            # but typically should be the same. Rebuilding is safer.
            palette = build_sprite_palette(flipped_art_strings)
            indices = create_snes_tile_indices(flipped_art_strings, palette)
            processed_frames_l.append((indices, palette))
        self.animation_frames[key_l] = processed_frames_l


    def get_current_animation_set(self):
        """Gets the current set of frames (indices, palette) based on state and direction."""
        direction = "left" if self.facing_left else "right"
        key = f"{self.state}_{direction}"
        # Provide a default fallback if a specific animation is missing
        # e.g., use idle_right if jump_left is not defined.
        default_fallback_key = "idle_right" 
        if default_fallback_key not in self.animation_frames and self.animation_frames:
            default_fallback_key = list(self.animation_frames.keys())[0] # any existing key

        return self.animation_frames.get(key, self.animation_frames.get(default_fallback_key, [([[]], [(0,0,0,0)])]))


    def update_animation(self, dt):
        """Updates the animation frame based on dt and animation_speed."""
        self.animation_timer += dt * FPS * self.animation_speed # dt is in seconds
        current_animation_set = self.get_current_animation_set()
        
        if not current_animation_set or not current_animation_set[0] or not current_animation_set[0][0]: # Check if valid frames exist
            return

        if self.animation_timer >= 1.0: # 1.0 because animation_speed is scaled by FPS
            self.animation_timer = 0 # Reset timer
            self.current_frame_index = (self.current_frame_index + 1) % len(current_animation_set)

    def draw(self, screen, camera_offset_x, camera_offset_y):
        """Draws the current animation frame."""
        current_animation_set = self.get_current_animation_set()
        if not current_animation_set or not current_animation_set[0] or not current_animation_set[0][0]: # Check for valid frames
            # print(f"Warning: No valid animation frames for state '{self.state}', direction {'left' if self.facing_left else 'right'}")
            return

        # Ensure current_frame_index is valid
        if self.current_frame_index >= len(current_animation_set):
            self.current_frame_index = 0 # Reset if out of bounds
        
        tile_indices, palette = current_animation_set[self.current_frame_index]
        if not tile_indices: # Further check if tile_indices themselves are empty
            return

        draw_snes_tile_indexed(screen, tile_indices, palette,
                               self.rect.x - camera_offset_x, 
                               self.rect.y - camera_offset_y, 
                               self.image_scale)

def flip_pixel_art(pixel_art_rows):
    """Flips pixel art horizontally."""
    return ["".join(reversed(row)) for row in pixel_art_rows]

class Player(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.vel = pg.math.Vector2(0, 0)
        self.acc = pg.math.Vector2(0, 0) # Acceleration vector

        # Player form state - crucial for SMB3 features
        self.is_super_form = False # TODO: Implement Super Mario form
        # self.is_raccoon_form = False # TODO: Implement Raccoon Mario
        # self.can_fly = False 
        
        self.set_form(small=True) # Initialize with small form
        
        self.on_ground = False
        self.can_jump = True # To prevent holding jump for multiple jumps
        self.score = 0
        self.lives = 3
        self.invincible_timer = 0 # Frames of invincibility after taking damage

    def set_form(self, small=True, super_form=False): # Add more forms as needed
        """Sets player art and properties based on form (e.g., small, super)."""
        self.animation_frames = {} # Clear previous frames
        self.is_super_form = super_form

        if small:
            self.is_super_form = False # Ensure consistency
            self.art_height_chars = 16 # Standard 16-char height for small Mario
            self.player_height_tiles = 1 # Small Mario is 1 tile high for collision
            
            self.load_animation_frames("idle", [SMB3_MARIO_SMALL_IDLE_R_ART])
            self.load_animation_frames("walk", [SMB3_MARIO_SMALL_WALK_R_ART_1, SMB3_MARIO_SMALL_WALK_R_ART_2])
            self.load_animation_frames("jump", [SMB3_MARIO_SMALL_JUMP_R_ART])
            # TODO: Add skid, die, etc. animations for small Mario
        elif super_form:
            self.is_super_form = True
            # self.art_height_chars = 32 # Example: Super Mario might be taller in art
            # self.player_height_tiles = 2 # Super Mario is 2 tiles high for collision
            # self.load_animation_frames("idle", [SMB3_MARIO_SUPER_IDLE_R_ART]) # Placeholder
            # self.load_animation_frames("walk", [SMB3_MARIO_SUPER_WALK_R_ART_1, ...]) # Placeholder
            # self.load_animation_frames("jump", [SMB3_MARIO_SUPER_JUMP_R_ART]) # Placeholder
            # For now, fallback to small mario if super art not defined
            print("Warning: Super Mario form selected, but art not implemented. Using Small Mario art.")
            self.set_form(small=True) # Fallback
        
        # Update rect based on new form
        current_x, current_y = self.pos.x, self.pos.y # Preserve position
        # Adjust y if height changes to keep feet at same level (approx)
        if hasattr(self, 'rect') and self.rect: # if rect already exists
            if self.player_height_tiles == 2 and self.rect.height == TILE_SIZE: # Grown
                current_y -= TILE_SIZE
            elif self.player_height_tiles == 1 and self.rect.height == TILE_SIZE * 2: # Shrunk
                current_y += TILE_SIZE
        
        self.rect = pg.Rect(current_x, current_y, TILE_SIZE, self.player_height_tiles * TILE_SIZE)
        self.pos.x = self.rect.x 
        self.pos.y = self.rect.y


    def jump(self):
        if self.on_ground:
            self.vel.y = -PLAYER_JUMP_POWER
            self.on_ground = False
            self.can_jump = False # Prevent re-jump until key release and ground touch

    def update(self, dt, platforms):
        self.acc = pg.math.Vector2(0, GRAVITY) # Reset acceleration, apply gravity
        keys = pg.key.get_pressed()

        if self.invincible_timer > 0:
            self.invincible_timer -= 1 # Simple frame countdown

        # Horizontal movement
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACCEL
            self.facing_left = True
        elif keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACCEL
            self.facing_left = False
        
        # Apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # Update velocity
        self.vel.x += self.acc.x * dt * FPS # Scale by dt for frame-rate independence (approx)
                                            # Or, if ACCEL is "per frame", then just self.vel.x += self.acc.x
                                            # The original was self.vel.x += self.acc.x, assuming acc is per-frame impulse
        # For this kind of physics, often:
        # self.vel.x += self.acc.x (if acc is impulse for the frame)
        # self.vel.x *= (1 - abs(PLAYER_FRICTION)) (if friction is damping factor)
        # Let's stick to original for now:
        self.vel.x += self.acc.x # Assuming acc values are balanced for this

        if abs(self.vel.x) < 0.1: self.vel.x = 0 # Stop if very slow

        # Cap horizontal speed
        self.vel.x = max(-PLAYER_MAX_SPEED_X, min(self.vel.x, PLAYER_MAX_SPEED_X))
        
        # Update horizontal position and collide
        self.pos.x += self.vel.x # * dt * FPS if vel is m/s, or just self.vel.x if vel is pixels/frame
                                 # Original was self.pos.x += self.vel.x
        self.rect.x = round(self.pos.x)
        self.collide_with_platforms_x(platforms)

        # Jumping
        if keys[pg.K_SPACE]:
            if self.can_jump and self.on_ground:
                self.jump()
        else: # Key released
            self.can_jump = True # Allow jump again once space is released and on ground

        # Vertical movement (apply gravity)
        self.vel.y += self.acc.y # acc.y is GRAVITY, applied per frame
        self.vel.y = min(self.vel.y, MAX_FALL_SPEED) # Cap fall speed
        
        # Update vertical position and collide
        self.pos.y += self.vel.y
        self.rect.y = round(self.pos.y)
        
        self.on_ground = False # Assume not on ground until collision check proves otherwise
        self.collide_with_platforms_y(platforms)

        # Update animation state
        if not self.on_ground:
            self.state = "jump"
        elif abs(self.vel.x) > 0.1: # Check if moving
            self.state = "walk"
        else:
            self.state = "idle"
        
        self.update_animation(dt)

        # Check for falling out of the world
        if self.rect.top > SCREEN_HEIGHT + TILE_SIZE * 2: # Give some leeway
            self.die()

    def collide_with_platforms_x(self, platforms):
        for plat in platforms:
            if plat.solid and self.rect.colliderect(plat.rect):
                if self.vel.x > 0: # Moving right
                    self.rect.right = plat.rect.left
                    self.vel.x = 0
                elif self.vel.x < 0: # Moving left
                    self.rect.left = plat.rect.right
                    self.vel.x = 0
                self.pos.x = self.rect.x # Sync pos with rect after collision

    def collide_with_platforms_y(self, platforms):
        for plat in platforms:
            if plat.solid and self.rect.colliderect(plat.rect):
                if self.vel.y > 0: # Moving down
                    self.rect.bottom = plat.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0: # Moving up (hit head)
                    self.rect.top = plat.rect.bottom
                    self.vel.y = 0 
                    if hasattr(plat, 'hit_from_bottom'):
                        plat.hit_from_bottom(self) # Notify block it was hit
                self.pos.y = self.rect.y # Sync pos with rect after collision
    
    def die(self):
        # TODO: Implement death animation, sound, short pause
        if self.invincible_timer > 0: return # Don't die if recently hit / invincible

        self.lives -= 1
        if self.lives > 0:
            # self.invincible_timer = FPS * 2 # e.g., 2 seconds of invincibility after respawn
            self.game.reset_level_soft() # Respawn at start of level
        else:
            self.game.game_over = True
            # TODO: Transition to game over screen or overworld

class Block(AnimatedSprite): 
    def __init__(self, game, x_tile, y_tile, art_frames_list, solid=True, block_type="generic"):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        self.load_animation_frames("idle", art_frames_list) 
        self.solid = solid
        self.block_type = block_type
        self.animation_speed = 0 # Most blocks don't animate by default

    def update(self, dt): 
        if self.animation_speed > 0:
            self.update_animation(dt)
    
    # Optional: hit_from_bottom method for blocks that react
    # def hit_from_bottom(self, player):
    #     pass

class BrickBlock(Block):
    def __init__(self, game, x_tile, y_tile):
        super().__init__(game, x_tile, y_tile, [SMB3_BRICK_BLOCK_ART], solid=True, block_type="brick")

    def hit_from_bottom(self, player):
        if player.is_super_form: 
            # TODO: Break animation, remove block, add score
            # self.kill() # Remove from all groups
            # self.game.player.score += 50
            print("Super Mario hits brick! (Not implemented: break)") # Placeholder
            pass 
        else:
            # TODO: Bump animation for the block
            print("Small Mario hits brick!") # Placeholder
            pass


class QuestionBlock(Block):
    def __init__(self, game, x_tile, y_tile):
        super().__init__(game, x_tile, y_tile, 
                         [SMB3_QUESTION_BLOCK_ART_FRAME1, SMB3_QUESTION_BLOCK_ART_FRAME2], 
                         solid=True, block_type="qblock")
        self.is_active = True 
        self.animation_speed = 0.05 # Slower animation for Q-block '?' shimmer
        self.item_to_spawn = SuperLeaf # Can be configured per block instance in level data

    def hit_from_bottom(self, player):
        if self.is_active:
            self.is_active = False
            self.animation_speed = 0 # Stop '?' shimmer
            self.load_animation_frames("idle", [SMB3_USED_BLOCK_ART]) # Change to used block art
            self.current_frame_index = 0 # Show the first (only) frame of used block

            # Spawn item
            if self.item_to_spawn:
                # Item spawns at the block's tile position, then moves out
                item_instance = self.item_to_spawn(self.game, self.pos.x / TILE_SIZE, self.pos.y / TILE_SIZE)
                self.game.all_sprites.add(item_instance)
                self.game.items.add(item_instance)
            
            # TODO: Play sound effect


class GroundBlock(Block):
    def __init__(self, game, x_tile, y_tile):
        super().__init__(game, x_tile, y_tile, [SMB3_GROUND_BLOCK_ART], solid=True, block_type="ground")

class Goomba(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        # Goombas are 1 tile high for collision
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        
        self.load_animation_frames("walk", [SMB3_GOOMBA_WALK1_ART, SMB3_GOOMBA_WALK2_ART])
        self.load_animation_frames("squished", [SMB3_GOOMBA_SQUISHED_ART]) 
        
        self.vel = pg.math.Vector2(-ENEMY_MOVE_SPEED, 0) # Start moving left
        self.facing_left = True # Matches initial velocity
        self.state = "walk"
        self.animation_speed = 0.08 
        self.squish_timer = 0 # Timer for how long squished state lasts before disappearing

    def update(self, dt, platforms):
        if self.state == "walk":
            self.pos.x += self.vel.x # * dt * FPS (if vel is m/s)
            self.rect.x = round(self.pos.x)
            
            # Horizontal collision with platforms
            collided_x = False
            for plat in platforms: 
                if plat.solid and self.rect.colliderect(plat.rect):
                    if self.vel.x > 0: # Moving right
                        self.rect.right = plat.rect.left
                        self.vel.x *= -1
                        self.facing_left = True
                    elif self.vel.x < 0: # Moving left
                        self.rect.left = plat.rect.right
                        self.vel.x *= -1
                        self.facing_left = False
                    self.pos.x = self.rect.x
                    collided_x = True
                    break
            
            # TODO: Add simple edge detection to turn around if about to fall off a platform
            # This requires checking the tile in front and below the Goomba.

            # Apply gravity to Goomba (optional, SMB1 Goombas didn't always respect gravity perfectly)
            # For simplicity, let's assume they stick to ground unless pushed off.
            # If you want them to fall:
            # self.vel.y += GRAVITY 
            # self.pos.y += self.vel.y
            # self.rect.y = round(self.pos.y)
            # self.collide_with_platforms_y(platforms) # Needs a collide_y method for enemies

            self.update_animation(dt)

        elif self.state == "squished":
            self.squish_timer -= 1 # Simple frame count timer
            if self.squish_timer <= 0:
                self.kill() # Remove from all sprite groups

    # Goomba's get_current_animation_set can be simplified if squished art is non-directional
    # Or, ensure "squished_right" / "squished_left" are properly loaded by load_animation_frames.
    # The base AnimatedSprite.get_current_animation_set should work if "squished_left" etc. exist.
    # The user's original override for Goomba was fine. Let's test if the base class handles it.
    # If SMB3_GOOMBA_SQUISHED_ART is symmetrical, flipping it for "_left" is fine.

class SuperLeaf(AnimatedSprite):
    def __init__(self, game, x_tile_spawn_base, y_tile_spawn_base): 
        super().__init__()
        self.game = game
        # Spawn slightly above the block it came from
        self.pos = pg.math.Vector2(x_tile_spawn_base * TILE_SIZE, (y_tile_spawn_base - 0.5) * TILE_SIZE) 
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        self.load_animation_frames("idle", [SMB3_SUPER_LEAF_ART]) # Leaf usually has one look
        self.state = "idle" # Or "drifting"
        
        self.vel = pg.math.Vector2(0,0) 
        
        self.spawn_state = "rising" # "rising", "drifting", "landed" (not fully implemented)
        # Target Y after rising out of the block (e.g., 1 tile above the block's top)
        self.rise_target_y = (y_tile_spawn_base - 1) * TILE_SIZE - (TILE_SIZE * 0.25) 
        self.rise_speed = -1.5 # Pixels per frame (negative is up)
        
        # Drifting behavior
        self.drift_amplitude_y = TILE_SIZE / 3.5 # How much it moves up/down
        self.drift_frequency_rad_per_tick = 0.03 # Speed of the sine wave
        self.drift_timer_rad = random.uniform(0, 2 * math.pi) # Start at random point in wave
        self.base_y_drift = 0 # The Y around which it drifts

    def update(self, dt, platforms):
        if self.spawn_state == "rising":
            self.pos.y += self.rise_speed # * dt * FPS if speed is m/s
            if self.pos.y <= self.rise_target_y:
                self.pos.y = self.rise_target_y
                self.spawn_state = "drifting"
                self.base_y_drift = self.pos.y 
                # Start drifting horizontally
                self.vel.x = random.choice([ENEMY_MOVE_SPEED * 0.6, -ENEMY_MOVE_SPEED * 0.6])
                self.facing_left = self.vel.x < 0

        elif self.spawn_state == "drifting":
            self.pos.x += self.vel.x # * dt * FPS
            
            # Sine wave vertical movement
            self.drift_timer_rad += self.drift_frequency_rad_per_tick # * dt * FPS (if freq is cycles/sec)
            offset_y = self.drift_amplitude_y * math.sin(self.drift_timer_rad)
            self.pos.y = self.base_y_drift + offset_y

            self.rect.x = round(self.pos.x)
            self.rect.y = round(self.pos.y)

            # Collision with platforms (simple horizontal bounce)
            for plat in platforms:
                if plat.solid and self.rect.colliderect(plat.rect):
                    # Check if primarily a horizontal collision
                    # A more robust check would involve previous position or separating axes
                    if abs(self.rect.centerx - plat.rect.centerx) > abs(self.rect.centery - plat.rect.centery):
                        if self.vel.x > 0 and self.rect.right > plat.rect.left:
                            self.rect.right = plat.rect.left
                            self.vel.x *= -1
                            self.facing_left = True
                        elif self.vel.x < 0 and self.rect.left < plat.rect.right:
                            self.rect.left = plat.rect.right
                            self.vel.x *= -1
                            self.facing_left = False
                        self.pos.x = self.rect.x
                    # Items usually don't "land" solidly while drifting, they might pass through
                    # or have a specific interaction. For now, just horizontal bounce.

        # elif self.spawn_state == "landed": # TODO: Implement landing logic if needed
        #     pass

        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        # SuperLeaf typically doesn't have multiple animation frames, but call if it might
        # self.update_animation(dt) 


class Flagpole(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        # Flagpole art might be taller than 1 tile. Adjust rect height accordingly.
        # SMB3_FLAGPOLE_ART is 16 rows, so 1 TILE_SIZE high.
        # If it's meant to be a tall pole, the art should reflect that, or use multiple tiles.
        # For a simple single-tile interactable point:
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE) # Assuming interaction point is 1 tile
        # If the art represents a taller structure, the rect for collision might be different
        # e.g. self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE * 4)
        self.load_animation_frames("idle", [SMB3_FLAGPOLE_ART])
        self.animation_speed = 0 
        self.solid = False # Player passes through it, but collision triggers level end

class Camera:
    def __init__(self, world_width_tiles, world_height_tiles): 
        self.camera_rect_on_screen = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT) # Viewport
        self.offset = pg.math.Vector2(0, 0) # How much the world is shifted
        self.world_width_pixels = world_width_tiles * TILE_SIZE
        self.world_height_pixels = world_height_tiles * TILE_SIZE

    def update(self, target_player):
        # Center camera on player, with clamping to world boundaries
        target_cam_x = -target_player.rect.centerx + SCREEN_WIDTH // 2
        
        # Clamp X
        # Max offset is 0 (left edge of world at left edge of screen)
        # Min offset is -(world_width - screen_width) (right edge of world at right edge of screen)
        clamped_cam_x = min(0, max(target_cam_x, -(self.world_width_pixels - SCREEN_WIDTH)))
        
        # Y clamping (SMB3 usually has fixed Y camera for a given section, or scrolls up/down at screen edges)
        # For a simple side-scroller, Y might be fixed or follow player within vertical limits.
        # Current implementation keeps Y fixed at 0 (top of the level).
        clamped_cam_y = 0 
        # Example for vertical follow (would need world_height_pixels to be accurate for level):
        # target_cam_y = -target_player.rect.centery + SCREEN_HEIGHT // 2
        # clamped_cam_y = min(0, max(target_cam_y, -(self.world_height_pixels - SCREEN_HEIGHT)))
        # However, SMB3 often has screen transitions rather than continuous vertical scroll.

        self.offset.x = clamped_cam_x
        self.offset.y = clamped_cam_y # For now, Y is fixed
        
    def get_world_view_rect(self): 
        """Returns a rect representing the portion of the world currently visible."""
        return pg.Rect(-self.offset.x, -self.offset.y, SCREEN_WIDTH, SCREEN_HEIGHT)


# Level and Overworld Data
LEVEL_1_1_DATA = [ 
    "..........................................................................................F.",
    "..........................................................................................F.", # F for Flagpole (interaction point)
    "..................BBQB....................................................................F.", # Q for QuestionBlock, B for Brick
    "..........................................................................................F.",
    ".........................BBBB.........QQQ.................................................F.",
    "..........................................................................................F.",
    "...................E................E.........E.E.........................................F.", # E for Enemy (Goomba)
    "GGGGGGGGGGGGGGGGGGGGGGGG...GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG...GGGGGGGGGGGGGGGGGGGGGGGGGGGGGG", # G for Ground
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
    "                  ", # Ensure consistent width for overworld data rows
    " . 1 . 2 . . . . .", 
    " . . . . . . . . .",
    " . . . . . . . . .",
    " . . . . . . . . .",
    " . . . . . . . . .",
    " . . . . . . . . .", 
    "                  "
]

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("SMB3 Style Game Engine - Hallucinated ROM")
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, TILE_SIZE // 2) # Scaled font for UI
        
        self.game_state = "overworld" # "overworld", "level", "game_over_screen"
        self.overworld_data = OVERWORLD_DATA
        self.mario_overworld_pos = (2,1) # Initial position on Overworld (col, row)
        
        # Find first level node for default mario_overworld_pos
        found_first_level_node = False
        for r, row in enumerate(self.overworld_data):
            for c, char_code in enumerate(row):
                # Check if char_code is a level identifier (digit or specific letter)
                if char_code.isdigit() or (char_code.isalpha() and char_code not in ['P', ' ', '.']): # Assuming 'P' is not a level ID
                    self.mario_overworld_pos = (c,r)
                    found_first_level_node = True
                    break
            if found_first_level_node:
                break
        
        self.overworld_cell_size = TILE_SIZE 

        self.levels = {'1': LEVEL_1_1_DATA, '2': LEVEL_1_2_DATA} 
        
        self.game_over = False # This flag is used within "level" state
        self.debug_mode = False 

        # Sprite groups
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group() 
        self.enemies = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.flagpoles = pg.sprite.Group() 

        self.player = None 
        self.camera = Camera(0,0) # Initialized properly in load_level

        self.current_level_char = '1' # Default starting level if directly entering
        self.enter_level(self.current_level_char) # Start in level 1 by default for testing, or switch to overworld first
        self.game_state = "overworld" # Override to start in overworld

    def load_level(self, level_data_str_array):
        self.all_sprites.empty()
        self.platforms.empty()
        self.enemies.empty()
        self.items.empty()
        self.flagpoles.empty()

        # Default player start position if 'P' not found in level data
        player_start_pos_tiles = (2, len(level_data_str_array) - 4) # Approx start

        for row_idx, row_str in enumerate(level_data_str_array):
            for col_idx, char_code in enumerate(row_str):
                # x_pos = col_idx * TILE_SIZE (not needed directly for tile-based init)
                # y_pos = row_idx * TILE_SIZE
                
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
                # TODO: Add 'P' for player start position in level_data
                # elif char_code == 'P':
                #    player_start_pos_tiles = (col_idx, row_idx)
        
        # Preserve player's existing lives and score if reloading mid-game
        prev_lives = self.player.lives if self.player else 3
        prev_score = self.player.score if self.player else 0

        self.player = Player(self, player_start_pos_tiles[0], player_start_pos_tiles[1])
        self.player.lives = prev_lives
        self.player.score = prev_score
        self.all_sprites.add(self.player)
        
        # Setup camera for the loaded level
        level_width_pixels = len(level_data_str_array[0]) * TILE_SIZE
        level_height_pixels = len(level_data_str_array) * TILE_SIZE
        self.camera = Camera(len(level_data_str_array[0]), len(level_data_str_array)) # Pass tiles
        self.camera.world_width_pixels = level_width_pixels
        self.camera.world_height_pixels = level_height_pixels


    def enter_level(self, level_char_id):
        if level_char_id in self.levels:
            self.current_level_char = level_char_id
            
            current_score = 0
            current_lives = 3 # Default for new game or if player didn't exist
            if self.player: # Preserve score and lives if transitioning between levels
                current_score = self.player.score
                current_lives = self.player.lives
            
            self.load_level(self.levels[level_char_id]) # This creates a new player instance
            
            # Restore score and lives to the new player instance
            self.player.score = current_score
            self.player.lives = current_lives

            self.game_state = "level"
            self.game_over = False 
        else:
            print(f"Warning: Level '{level_char_id}' not found in self.levels.")
            self.game_state = "overworld" # Fallback to overworld if level invalid

    def complete_level(self):
        # TODO: Add level complete sequence (flag slide, score tally, castle walk)
        print(f"Level {self.current_level_char} completed!")
        self.player.score += 1000 # Bonus for completing level
        self.game_state = "overworld" 
        # Player's mario_overworld_pos remains on the completed level node.
        # Could implement logic to auto-move to next node if path is linear.

    def reset_level_soft(self): 
        """Called when player dies but has lives remaining."""
        if self.player:
            # Score is kept, lives are already decremented by Player.die()
            current_score = self.player.score 
            current_lives = self.player.lives 
            self.load_level(self.levels[self.current_level_char]) # Reloads level, player re-created
            self.player.score = current_score
            self.player.lives = current_lives
            if self.player.lives <= 0: 
                self.game_over = True # Should be handled by Player.die leading to game_over
        else: 
            self.enter_level(self.current_level_char) 

    def reset_game_hard(self): 
        """Called on Game Over and restart."""
        self.game_over = False
        # Determine starting level from overworld position or default
        level_to_start_char = self.overworld_data[self.mario_overworld_pos[1]][self.mario_overworld_pos[0]]
        if level_to_start_char not in self.levels: # Fallback to first defined level
            level_to_start_char = list(self.levels.keys())[0] if self.levels else None
            if not level_to_start_char:
                print("Error: No levels defined to start game.")
                pg.quit()
                exit()
            # Try to find this fallback level on the map and set mario_overworld_pos
            found_node = False
            for r_idx, r_str in enumerate(self.overworld_data):
                if found_node: break
                for c_idx, char_val in enumerate(r_str):
                    if char_val == level_to_start_char:
                        self.mario_overworld_pos = (c_idx, r_idx)
                        found_node = True
                        break
        
        self.enter_level(level_to_start_char) 
        if self.player: # enter_level re-creates player
            self.player.score = 0
            self.player.lives = 3


    def draw_overworld(self):
        self.screen.fill(BACKGROUND_COLOR) 
        ow_tile_size = self.overworld_cell_size
        for r, row_str in enumerate(self.overworld_data):
            for c, char_code in enumerate(row_str):
                x, y = c * ow_tile_size, r * ow_tile_size
                rect = (x, y, ow_tile_size, ow_tile_size)
                if char_code == ' ': # Path tile (empty space)
                    pg.draw.rect(self.screen, color_map.get('B', (0,0,255)), rect, 1) # Blue border for path
                elif char_code == '.': # Decoration tile (e.g., grass)
                    pg.draw.rect(self.screen, color_map.get('G', (0,128,0)), rect) 
                elif char_code.isdigit() or (char_code.isalpha() and char_code not in 'P'): # Level node
                    pg.draw.rect(self.screen, color_map.get('Y', (255,255,0)), rect) 
                    self.draw_text(char_code, x + ow_tile_size // 3, y + ow_tile_size // 4, 'K')
        
        # Draw Mario marker on overworld
        mario_ow_x = self.mario_overworld_pos[0] * ow_tile_size
        mario_ow_y = self.mario_overworld_pos[1] * ow_tile_size
        pg.draw.rect(self.screen, color_map.get('R', (255,0,0)), 
                     (mario_ow_x + ow_tile_size//4, mario_ow_y + ow_tile_size//4, 
                      ow_tile_size//2, ow_tile_size//2))


    def draw_text(self, text_str, x, y, color_char_code='W', Sfont=None):
        if Sfont is None: Sfont = self.font
        try:
            text_surface = Sfont.render(text_str, True, color_map[color_char_code])
            self.screen.blit(text_surface, (x,y))
        except KeyError:
            print(f"Warning: Color character code '{color_char_code}' not in color_map. Using white.")
            text_surface = Sfont.render(text_str, True, color_map['W'])
            self.screen.blit(text_surface, (x,y))
        except Exception as e:
            print(f"Error rendering text: {e}")


    def run(self): # Renamed from main, removed async
        running = True
        # dt_accumulator = 0.0 # For fixed physics updates (more advanced)
        # fixed_dt = 1/FPS 

        while running:
            # Delta time in seconds (time since last frame)
            # Important for frame-rate independent movement and animations
            dt = self.clock.tick(FPS) / 1000.0 
            
            # --- Event Handling ---
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
                    if event.key == pg.K_F1: 
                        self.debug_mode = not self.debug_mode
                        print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
                    
                    if self.game_state == "level":
                        if self.game_over and event.key == pg.K_r:
                            self.reset_game_hard()
                        # Player jump is handled in Player.update via get_pressed for holding
                    
                    elif self.game_state == "overworld":
                        # Basic keyboard navigation for overworld (optional)
                        # Example:
                        # current_x, current_y = self.mario_overworld_pos
                        # if event.key == pg.K_UP and current_y > 0: self.mario_overworld_pos = (current_x, current_y - 1)
                        # if event.key == pg.K_DOWN and current_y < len(self.overworld_data)-1: self.mario_overworld_pos = (current_x, current_y + 1)
                        # ... add left/right, and check if new pos is valid path/node
                        # if event.key == pg.K_RETURN: # Enter level
                        #    char_at_pos = self.overworld_data[self.mario_overworld_pos[1]][self.mario_overworld_pos[0]]
                        #    if char_at_pos in self.levels:
                        #        self.enter_level(char_at_pos)
                        pass # Mouse interaction is primary for overworld as per original

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
                                    # Check if this node is "reachable" from current Mario pos (optional advanced pathfinding)
                                    self.mario_overworld_pos = (clicked_col, clicked_row) # Move Mario marker
                                    self.enter_level(char_at_click)
            
            # --- Update Logic ---
            if self.game_state == "level" and not self.game_over:
                self.player.update(dt, self.platforms)
                for enemy in list(self.enemies): # Iterate over a copy for safe removal
                    enemy.update(dt, self.platforms)
                for item in list(self.items):
                    item.update(dt, self.platforms)
                
                self.camera.update(self.player)

                # Player-Enemy collisions
                if self.player.invincible_timer <= 0: # Only check if not invincible
                    for enemy in list(self.enemies): 
                        if isinstance(enemy, Goomba) and enemy.state == "walk": # Only collidable if walking
                            if self.player.rect.colliderect(enemy.rect):
                                # Stomp Goomba
                                if (self.player.vel.y > 0 and # Player is falling
                                    self.player.rect.bottom < enemy.rect.centery + (TILE_SIZE / 3) and # Player's feet are above goomba's center-ish
                                    not self.player.on_ground): # Player is not on ground (mid-air stomp)
                                    
                                    enemy.state = "squished"
                                    enemy.animation_speed = 0 # Stop walk animation
                                    enemy.current_frame_index = 0 # Show first frame of squish
                                    enemy.vel.x = 0 # Stop moving
                                    enemy.squish_timer = FPS // 2 # Disappear after 0.5 sec
                                    self.player.vel.y = -PLAYER_JUMP_POWER / 2.0 # Small bounce after stomp
                                    self.player.score += 100
                                    # TODO: Play stomp sound
                                else: # Player hit Goomba from side or bottom
                                    self.player.die() 
                                    break # Stop checking other enemies if player died
                
                # Player-Item collisions
                for item in list(self.items):
                    if self.player.rect.colliderect(item.rect):
                        if isinstance(item, SuperLeaf):
                            self.player.score += 1000
                            # TODO: Transform player to Super/Raccoon Mario
                            # self.player.set_form(super_form=True) # Example
                            print("Collected Super Leaf! (Form change not implemented)")
                            item.kill() # Remove leaf
                            # TODO: Play power-up sound
                
                # Player-Flagpole collision
                for flagpole in self.flagpoles:
                    if self.player.rect.colliderect(flagpole.rect):
                        # Crude check, real SMB3 has specific grab/slide logic
                        if not flagpole.solid: # Make sure it's the interactable part
                            self.complete_level()
                            break 
            
            # --- Drawing Logic ---
            self.screen.fill(BACKGROUND_COLOR) 

            if self.game_state == "overworld":
                self.draw_overworld()
            elif self.game_state == "level":
                world_view = self.camera.get_world_view_rect()
                # Draw sprites that are within the camera's view
                for sprite in self.all_sprites:
                    # Basic culling: check if sprite's rect intersects with camera's world view
                    if sprite.rect.colliderect(world_view): 
                        sprite.draw(self.screen, self.camera.offset.x, self.camera.offset.y)
                
                # Draw HUD
                if self.player:
                    self.draw_text(f"SCORE: {self.player.score}", 20, 10, 'W')
                    self.draw_text(f"LIVES: {self.player.lives}", SCREEN_WIDTH - 150, 10, 'W')
                    # self.draw_text(f"FPS: {self.clock.get_fps():.2f}", SCREEN_WIDTH - 150, 40, 'W') # Optional FPS display

                if self.game_over:
                    # Simple Game Over overlay
                    overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA) # SRCALPHA for transparency
                    overlay.fill((50, 50, 50, 180)) # Semi-transparent dark overlay
                    self.screen.blit(overlay, (0,0))
                    
                    large_font = pg.font.Font(None, TILE_SIZE) 
                    self.draw_text("GAME OVER", SCREEN_WIDTH // 2 - TILE_SIZE * 3, SCREEN_HEIGHT // 2 - TILE_SIZE, 'R', large_font)
                    self.draw_text("Press R to Restart", SCREEN_WIDTH // 2 - TILE_SIZE * 3.5, SCREEN_HEIGHT // 2 + TILE_SIZE //2, 'W')
            
            pg.display.flip() # Update the full screen

        pg.quit()


if __name__ == "__main__":
    game_instance = Game()
    game_instance.run() # Call the synchronous run method
