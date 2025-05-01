# [ DELTA-BUSTER ] : Generating enhanced NSMB-DS style Pygame code...
# [ COPYRIGHT NOVA ] : Applying NSMB-DS aesthetic principles programmatically...

import pygame
import sys
import math
import asyncio
import platform

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_TITLE = "Purrfect Platformer Tech Demo (NSMB-DS Style)"

# Colors (DS-inspired palette, meow!)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (237, 28, 36)        # Mario's Hat/Shirt
BRIGHT_RED = (255, 0, 0)   # Brighter Red
BLUE = (0, 88, 248)        # Mario's Overalls
DARK_BLUE = (0, 56, 160)   # Darker Blue for contrast/shading
BROWN = (184, 112, 0)      # Mario's Shoes/Hair, Blocks
DARK_BROWN = (120, 72, 0)  # Darker Brown
YELLOW = (255, 216, 0)     # Coins, ?-Blocks
GOLD = (255, 184, 0)       # Coin Shine
SKY_BLUE = (92, 148, 252)  # Daytime Sky
GRASS_GREEN = (34, 177, 76) # Not used directly, but for reference
BRICK_RED = (200, 76, 12)  # Brick Blocks
PIPE_GREEN = (0, 168, 0)   # Pipes
DARK_PIPE_GREEN = (0, 104, 0)
FLESH = (252, 216, 168)    # Mario's Face/Hands
GOOMBA_BROWN = (144, 88, 0)
GOOMBA_FEET = (88, 48, 0)
FLAGPOLE_GRAY = (192, 192, 192)
FLAGPOLE_BALL = (218, 165, 32) # Gold-ish

# Player Constants
PLAYER_ACC = 0.6
PLAYER_FRICTION = -0.15
PLAYER_GRAVITY = 0.8
PLAYER_JUMP = -16
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
PLAYER_MAX_FALL_SPEED = 15

# Enemy Constants
GOOMBA_WIDTH = 32
GOOMBA_HEIGHT = 32
GOOMBA_SPEED = 1

# Item Constants
COIN_WIDTH = 20
COIN_HEIGHT = 26

# Block Constants
BLOCK_SIZE = 40

# Level Data Constants
LEVEL_END_PADDING = 200 # Extra space after the last element

# Game States
STATE_LEVEL_SELECT = 0
STATE_PLAYING = 1
STATE_LEVEL_COMPLETE = 2 # Nya~ a state for finishing!

# --- Helper Functions ---

def draw_mario(surface, width, height, facing_right=True):
    """Draw a more detailed Mario-like character using shapes, purr!"""
    surface.fill((0, 0, 0, 0)) # Transparent background, meow!

    # Proportions
    head_h = height * 0.35
    body_h = height * 0.35
    legs_h = height * 0.30
    head_w = width * 0.7
    body_w = width * 0.8
    shoe_h = legs_h * 0.5
    shoe_w = width * 0.45

    center_x = width / 2
    head_y = 0
    body_y = head_h
    legs_y = head_h + body_h
    shoe_y = height - shoe_h

    # --- Head ---
    head_x = center_x - head_w / 2
    # Hair (Brown) - Draw first to be behind cap/face
    hair_h = head_h * 0.5
    hair_w = head_w * 0.9
    hair_x = center_x - hair_w / 2
    pygame.draw.rect(surface, BROWN, (hair_x, head_y + head_h * 0.2, hair_w, hair_h))

    # Face (Flesh)
    face_h = head_h * 0.8
    face_w = head_w * 0.8
    face_x = center_x - face_w / 2
    face_y = head_y + head_h * 0.2
    pygame.draw.rect(surface, FLESH, (face_x, face_y, face_w, face_h))

    # Cap (Red)
    cap_h = head_h * 0.6
    cap_w = head_w
    cap_x = head_x
    cap_y = head_y
    # Main Cap
    pygame.draw.ellipse(surface, RED, (cap_x, cap_y, cap_w, cap_h * 1.5))
    # Brim
    brim_h = cap_h * 0.3
    brim_w = cap_w * 1.1
    brim_x = center_x - brim_w / 2
    brim_y = cap_y + cap_h * 0.6
    pygame.draw.rect(surface, RED, (brim_x, brim_y, brim_w, brim_h))

    # Eyes (White circle, black pupil)
    eye_r = width * 0.08
    eye_y = face_y + face_h * 0.3
    eye_dist = head_w * 0.2
    eye_x1 = center_x - eye_dist
    eye_x2 = center_x + eye_dist
    pygame.draw.circle(surface, WHITE, (eye_x1, eye_y), eye_r)
    pygame.draw.circle(surface, WHITE, (eye_x2, eye_y), eye_r)
    pygame.draw.circle(surface, BLACK, (eye_x1 + (eye_r * 0.2 if facing_right else -eye_r * 0.2), eye_y), eye_r * 0.5)
    pygame.draw.circle(surface, BLACK, (eye_x2 + (eye_r * 0.2 if facing_right else -eye_r * 0.2), eye_y), eye_r * 0.5)

    # Nose (Flesh - slightly larger)
    nose_r = width * 0.12
    nose_y = face_y + face_h * 0.55
    nose_x = center_x
    pygame.draw.circle(surface, FLESH, (nose_x, nose_y), nose_r)
    pygame.draw.circle(surface, DARK_BROWN, (nose_x, nose_y), nose_r, 1) # Outline

    # Mustache (Brown)
    mustache_h = head_h * 0.25
    mustache_w = head_w * 0.7
    mustache_x = center_x - mustache_w / 2
    mustache_y = nose_y + nose_r * 0.5
    pygame.draw.rect(surface, BROWN, (mustache_x, mustache_y, mustache_w, mustache_h))

    # --- Body ---
    body_x = center_x - body_w / 2
    # Shirt (Red)
    shirt_h = body_h * 0.8
    pygame.draw.rect(surface, RED, (body_x, body_y, body_w, shirt_h))

    # Overalls (Blue)
    overalls_h = body_h + legs_h * 0.7 # Extend down over legs
    overalls_w = body_w * 0.8
    overalls_x = center_x - overalls_w / 2
    overalls_y = body_y + body_h * 0.1
    pygame.draw.rect(surface, BLUE, (overalls_x, overalls_y, overalls_w, overalls_h))

    # Straps (Blue)
    strap_w = body_w * 0.15
    strap_h = body_h
    strap_y = body_y
    strap_x1 = overalls_x
    strap_x2 = overalls_x + overalls_w - strap_w
    pygame.draw.rect(surface, BLUE, (strap_x1, strap_y, strap_w, strap_h))
    pygame.draw.rect(surface, BLUE, (strap_x2, strap_y, strap_w, strap_h))

    # Buttons (Yellow)
    button_r = width * 0.07
    button_y = overalls_y + button_r
    button_x1 = strap_x1 + strap_w / 2
    button_x2 = strap_x2 + strap_w / 2
    pygame.draw.circle(surface, YELLOW, (button_x1, button_y), button_r)
    pygame.draw.circle(surface, YELLOW, (button_x2, button_y), button_r)

    # --- Legs & Shoes ---
    leg_w = overalls_w / 2
    leg_x1 = overalls_x
    leg_x2 = overalls_x + leg_w

    # Shoes (Brown)
    shoe_x1 = leg_x1 - (shoe_w - leg_w) / 2 + (5 if facing_right else -5) # Offset shoes slightly
    shoe_x2 = leg_x2 - (shoe_w - leg_w) / 2 + (5 if facing_right else -5)
    pygame.draw.ellipse(surface, BROWN, (shoe_x1, shoe_y, shoe_w, shoe_h))
    pygame.draw.ellipse(surface, BROWN, (shoe_x2, shoe_y, shoe_w, shoe_h))

def draw_brick_block(surface, width, height):
    """Draw a brown brick block, meow!"""
    surface.fill(BRICK_RED)
    brick_h = height / 4
    brick_w = width / 2
    line_color = DARK_BROWN
    line_thick = 2

    # Horizontal lines
    for i in range(1, 4):
        pygame.draw.line(surface, line_color, (0, i * brick_h), (width, i * brick_h), line_thick)

    # Vertical lines (alternating pattern)
    for r in range(4):
        offset = brick_w / 2 if r % 2 == 1 else 0
        start_x = offset
        while start_x < width:
            pygame.draw.line(surface, line_color, (start_x, r * brick_h), (start_x, (r + 1) * brick_h), line_thick)
            if start_x == offset and offset > 0: # Draw half brick line at start if offset
                 pygame.draw.line(surface, line_color, (0, r * brick_h), (0, (r + 1) * brick_h), line_thick)
            start_x += brick_w
        # Draw line at the end if needed (mostly for odd rows starting at 0)
        if offset == 0:
             pygame.draw.line(surface, line_color, (width, r * brick_h), (width, (r + 1) * brick_h), line_thick)

    # Border
    pygame.draw.rect(surface, BLACK, (0, 0, width, height), line_thick)


def draw_question_block(surface, width, height):
    """Draw a yellow ?-Block, nya!"""
    surface.fill(YELLOW)
    border_thick = 4
    pygame.draw.rect(surface, DARK_BROWN, (0, 0, width, height), border_thick) # Border

    # Rivets (simple circles)
    rivet_r = border_thick // 2
    rivet_color = DARK_BROWN
    pygame.draw.circle(surface, rivet_color, (border_thick, border_thick), rivet_r)
    pygame.draw.circle(surface, rivet_color, (width - border_thick, border_thick), rivet_r)
    pygame.draw.circle(surface, rivet_color, (border_thick, height - border_thick), rivet_r)
    pygame.draw.circle(surface, rivet_color, (width - border_thick, height - border_thick), rivet_r)

    # Question Mark (simple rects for '?' shape)
    q_color = WHITE
    q_thick = width // 6
    q_h1 = height * 0.5
    q_w1 = width * 0.4
    q_x1 = width / 2 - q_w1 / 2
    q_y1 = height * 0.15
    # Top curve part
    pygame.draw.rect(surface, q_color, (q_x1, q_y1, q_w1, q_thick)) # Top horizontal
    pygame.draw.rect(surface, q_color, (q_x1 + q_w1 - q_thick, q_y1, q_thick, q_h1 * 0.6)) # Right vertical
    pygame.draw.rect(surface, q_color, (q_x1, q_y1 + q_h1*0.6 - q_thick, q_w1*0.6, q_thick)) # Middle horizontal leftwards
    # Stem part
    stem_h = height * 0.3
    stem_y = q_y1 + q_h1 * 0.6
    stem_x = width/2 - q_thick/2
    pygame.draw.rect(surface, q_color, (stem_x, stem_y, q_thick, stem_h))
    # Dot part
    dot_y = stem_y + stem_h + height * 0.05
    pygame.draw.rect(surface, q_color, (stem_x, dot_y, q_thick, q_thick))


def draw_ground_block(surface, width, height):
    """Draw a simple ground block, meow."""
    surface.fill(BROWN)
    pygame.draw.rect(surface, DARK_BROWN, (0, 0, width, height * 0.3)) # Darker top bit
    pygame.draw.rect(surface, BLACK, (0, 0, width, height), 1) # Outline


def draw_goomba(surface, width, height):
    """Draw a Goomba-like enemy, rawr!"""
    surface.fill((0,0,0,0)) # Transparent bg
    body_h = height * 0.7
    body_y = height - body_h
    feet_h = height * 0.3
    feet_y = height - feet_h

    # Body (Brown oval)
    pygame.draw.ellipse(surface, GOOMBA_BROWN, (0, body_y, width, body_h))

    # Feet (Darker ovals)
    foot_w = width * 0.45
    foot_space = width * 0.1
    foot_x1 = 0
    foot_x2 = width - foot_w
    pygame.draw.ellipse(surface, GOOMBA_FEET, (foot_x1, feet_y, foot_w, feet_h))
    pygame.draw.ellipse(surface, GOOMBA_FEET, (foot_x2, feet_y, foot_w, feet_h))

    # Eyes (simple white ovals with black pupil lines) - Angry look!
    eye_h = body_h * 0.3
    eye_w = width * 0.2
    eye_y = body_y + body_h * 0.2
    eye_x1 = width * 0.25 - eye_w / 2
    eye_x2 = width * 0.75 - eye_w / 2
    pygame.draw.ellipse(surface, WHITE, (eye_x1, eye_y, eye_w, eye_h))
    pygame.draw.ellipse(surface, WHITE, (eye_x2, eye_y, eye_w, eye_h))
    # Pupils (lines for angry look)
    pupil_y1 = eye_y + eye_h * 0.1
    pupil_y2 = eye_y + eye_h * 0.9
    pupil_x_off = eye_w * 0.5 # Center of eye
    pygame.draw.line(surface, BLACK, (eye_x1 + pupil_x_off, pupil_y1), (eye_x1 + pupil_x_off, pupil_y2), 2)
    pygame.draw.line(surface, BLACK, (eye_x2 + pupil_x_off, pupil_y1), (eye_x2 + pupil_x_off, pupil_y2), 2)

    # Eyebrows (thick black lines slanted down)
    brow_y = eye_y - eye_h * 0.1
    brow_l = eye_w * 1.2
    brow_x1_start = eye_x1 - brow_l * 0.1
    brow_x1_end = eye_x1 + brow_l * 0.9
    brow_x2_start = eye_x2 + brow_l * 0.1
    brow_x2_end = eye_x2 + brow_l * 1.1
    pygame.draw.line(surface, BLACK, (brow_x1_start, brow_y + 3), (brow_x1_end, brow_y), 4)
    pygame.draw.line(surface, BLACK, (brow_x2_start, brow_y), (brow_x2_end, brow_y + 3), 4)


def draw_coin(surface, width, height):
    """Draw a shiny coin, meow!"""
    surface.fill((0,0,0,0)) # Transparent bg
    # Main coin body (oval)
    pygame.draw.ellipse(surface, YELLOW, (0, 0, width, height))
    # Inner shine/detail (slightly smaller, brighter oval)
    shine_w = width * 0.7
    shine_h = height * 0.7
    shine_x = width / 2 - shine_w / 2
    shine_y = height / 2 - shine_h / 2
    pygame.draw.ellipse(surface, GOLD, (shine_x, shine_y, shine_w, shine_h))
    # Tiny glint
    glint_r = width * 0.1
    pygame.draw.circle(surface, WHITE, (width * 0.3, height * 0.3), glint_r)

def draw_flagpole(surface, width, height):
    """Draw the end-level flagpole, nya!"""
    surface.fill((0,0,0,0)) # Transparent bg
    pole_width = width * 0.2
    pole_x = width / 2 - pole_width / 2
    ball_radius = width / 2

    # Pole
    pygame.draw.rect(surface, FLAGPOLE_GRAY, (pole_x, ball_radius / 2 , pole_width, height - ball_radius / 2))
    # Ball on top
    pygame.draw.circle(surface, FLAGPOLE_BALL, (width / 2, ball_radius), ball_radius)


def load_level_data(world_index, level_index):
    """
    Returns level data including blocks, enemies, coins, and goal. Nya~ more levels!
    Block format: (x, y, type) where type is 'brick', 'question', 'ground' etc.
    Other formats: (x, y)
    Goal format: (x, y, w, h)
    """
    print(f"Loading World {world_index+1}, Level {level_index+1}, meow!")
    blocks = []
    enemies = []
    coins = []
    goal = None
    level_width = 0 # Keep track of how wide the level is

    # Helper to add ground strip
    def add_ground(start_x, end_x, y_pos):
        nonlocal level_width
        for x in range(start_x, end_x, BLOCK_SIZE):
            blocks.append((x, y_pos, 'ground'))
        level_width = max(level_width, end_x)

    if world_index == 0: # World 1
        ground_y = SCREEN_HEIGHT - BLOCK_SIZE * 2

        if level_index == 0: # Level 1-1
            add_ground(0, SCREEN_WIDTH * 3, ground_y + BLOCK_SIZE) # Lower ground
            add_ground(0, BLOCK_SIZE * 15, ground_y) # Main ground path

            # Some blocks
            blocks.append((BLOCK_SIZE * 6, ground_y - BLOCK_SIZE * 3, 'question'))
            blocks.append((BLOCK_SIZE * 7, ground_y - BLOCK_SIZE * 3, 'brick'))
            blocks.append((BLOCK_SIZE * 8, ground_y - BLOCK_SIZE * 3, 'question'))
            blocks.append((BLOCK_SIZE * 9, ground_y - BLOCK_SIZE * 3, 'brick'))
            blocks.append((BLOCK_SIZE * 8, ground_y - BLOCK_SIZE * 7, 'question')) # High one

            # Some platforms
            for i in range(5):
                 blocks.append((BLOCK_SIZE * (18 + i), ground_y - BLOCK_SIZE * 3, 'brick'))

            # Enemies
            enemies.append((BLOCK_SIZE * 10, ground_y))
            enemies.append((BLOCK_SIZE * 12, ground_y))
            enemies.append((BLOCK_SIZE * 20, ground_y - BLOCK_SIZE * 3)) # On platform

            # Coins
            coins.append((BLOCK_SIZE * 6, ground_y - BLOCK_SIZE * 4))
            coins.append((BLOCK_SIZE * 8, ground_y - BLOCK_SIZE * 4))
            coins.append((BLOCK_SIZE * 8, ground_y - BLOCK_SIZE * 8))

            # Goal
            goal_x = BLOCK_SIZE * 25
            goal_y = ground_y - BLOCK_SIZE * 5 # Flagpole base height
            goal_h = BLOCK_SIZE * 6
            blocks.append((goal_x, ground_y, 'ground')) # Block for flagpole base
            goal = (goal_x, goal_y, BLOCK_SIZE, goal_h)
            level_width = max(level_width, goal_x + BLOCK_SIZE)

        elif level_index == 1: # Level 1-2 (A bit different!)
            add_ground(0, SCREEN_WIDTH * 2, ground_y + BLOCK_SIZE) # Lower ground
            add_ground(0, BLOCK_SIZE * 10, ground_y) # Start path
            add_ground(BLOCK_SIZE * 18, BLOCK_SIZE * 30, ground_y) # End path

            # Floating blocks
            for i in range(3): blocks.append((BLOCK_SIZE * (4+i), ground_y - BLOCK_SIZE*4, 'brick'))
            blocks.append((BLOCK_SIZE * 5, ground_y - BLOCK_SIZE*4, 'question'))

            # Gap with coins
            for i in range(4): coins.append((BLOCK_SIZE * (12 + i*1.5), ground_y - BLOCK_SIZE))

            # Higher platform
            for i in range(4): blocks.append((BLOCK_SIZE * (20+i), ground_y - BLOCK_SIZE*5, 'ground'))

            # Enemies
            enemies.append((BLOCK_SIZE * 7, ground_y))
            enemies.append((BLOCK_SIZE * 22, ground_y - BLOCK_SIZE*5)) # On high platform

            # Goal
            goal_x = BLOCK_SIZE * 28
            goal_y = ground_y - BLOCK_SIZE * 5
            goal_h = BLOCK_SIZE * 6
            blocks.append((goal_x, ground_y, 'ground'))
            goal = (goal_x, goal_y, BLOCK_SIZE, goal_h)
            level_width = max(level_width, goal_x + BLOCK_SIZE)


        elif level_index == 2: # Level 1-3 (More vertical maybe?)
            add_ground(0, BLOCK_SIZE * 8, ground_y)
            add_ground(BLOCK_SIZE * 20, BLOCK_SIZE * 28, ground_y) # Second ground part

            # Stacks of blocks
            for y_off in range(5): blocks.append((BLOCK_SIZE * 10, ground_y - BLOCK_SIZE*y_off, 'brick'))
            for y_off in range(3): blocks.append((BLOCK_SIZE * 12, ground_y - BLOCK_SIZE*y_off, 'brick'))
            blocks.append((BLOCK_SIZE * 12, ground_y - BLOCK_SIZE*3, 'question'))

            # Pyramid
            for level in range(4):
                for i in range(level + 1):
                    blocks.append((BLOCK_SIZE * (15 + i), ground_y - BLOCK_SIZE * level, 'brick'))

            # Enemies
            enemies.append((BLOCK_SIZE * 5, ground_y))
            enemies.append((BLOCK_SIZE * 23, ground_y))
            enemies.append((BLOCK_SIZE * 16, ground_y - BLOCK_SIZE * 4)) # Top of pyramid

             # Coins
            coins.append((BLOCK_SIZE * 12, ground_y - BLOCK_SIZE * 5)) # Above q block
            coins.append((BLOCK_SIZE * 10, ground_y - BLOCK_SIZE * 6)) # Top of stack

            # Goal
            goal_x = BLOCK_SIZE * 26
            goal_y = ground_y - BLOCK_SIZE * 5
            goal_h = BLOCK_SIZE * 6
            blocks.append((goal_x, ground_y, 'ground'))
            goal = (goal_x, goal_y, BLOCK_SIZE, goal_h)
            level_width = max(level_width, goal_x + BLOCK_SIZE)

    else: # Default empty level if world/level doesn't exist
        add_ground(0, SCREEN_WIDTH * 2, SCREEN_HEIGHT - BLOCK_SIZE)
        level_width = SCREEN_WIDTH * 2


    # Ensure level width includes padding at the end
    level_width += LEVEL_END_PADDING

    return {'blocks': blocks, 'enemies': enemies, 'coins': coins, 'goal': goal, 'width': level_width}


# --- Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image_right = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        draw_mario(self.image_right, PLAYER_WIDTH, PLAYER_HEIGHT, facing_right=True)
        self.image_left = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        draw_mario(self.image_left, PLAYER_WIDTH, PLAYER_HEIGHT, facing_right=False)
        self.image = self.image_right # Start facing right
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, PLAYER_GRAVITY)
        self.rect.midbottom = self.pos
        self.on_ground = False
        self.facing_right = True
        self.jump_power = PLAYER_JUMP
        self.score = 0 # Meow, let's count coins!

    def jump(self):
        # Only jump if on the ground, nya!
        if self.on_ground:
            self.vel.y = self.jump_power
            self.on_ground = False # Not on ground anymore after jumping

    def update(self):
        self.acc = pygame.math.Vector2(0, PLAYER_GRAVITY)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acc.x = -PLAYER_ACC
            if self.facing_right:
                self.facing_right = False
                self.image = self.image_left
        if keys[pygame.K_RIGHT]:
            self.acc.x = PLAYER_ACC
            if not self.facing_right:
                self.facing_right = True
                self.image = self.image_right

        # Apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # Equations of motion
        self.vel += self.acc
        # Limit fall speed
        if self.vel.y > PLAYER_MAX_FALL_SPEED:
             self.vel.y = PLAYER_MAX_FALL_SPEED

        self.pos.x += self.vel.x + 0.5 * self.acc.x
        self.pos.y += self.vel.y + 0.5 * self.acc.y

        self.rect.midbottom = self.pos # Keep rect updated

        # Collision detection happens in the Game class's update method after movement

    def collide_with_blocks(self, dx, dy):
         # Check collision based on predicted movement
        temp_rect = self.rect.copy()

        # Move horizontally first
        temp_rect.x += dx
        for block in self.game.blocks:
             if temp_rect.colliderect(block.rect):
                 if dx > 0: # Moving right
                     self.rect.right = block.rect.left
                 elif dx < 0: # Moving left
                     self.rect.left = block.rect.right
                 self.pos.x = self.rect.centerx # Update pos based on collision
                 self.vel.x = 0 # Stop horizontal movement
                 dx = 0 # Prevent further horizontal move check
                 break # Exit after first horizontal collision found


        # Move vertically
        self.on_ground = False # Assume not on ground until proven otherwise
        temp_rect = self.rect.copy() # Use the potentially corrected horizontal position
        temp_rect.y += dy
        for block in self.game.blocks:
             if temp_rect.colliderect(block.rect):
                 if dy > 0: # Moving down
                     self.rect.bottom = block.rect.top
                     self.on_ground = True
                     self.vel.y = 0 # Stop vertical movement
                 elif dy < 0: # Moving up (hitting head)
                     self.rect.top = block.rect.bottom
                     self.vel.y = 0 # Stop vertical movement
                      # Check if it's a special block we hit from below
                     if hasattr(block, 'hit'):
                         block.hit(self)

                 self.pos.y = self.rect.midbottom[1] # Update pos based on collision
                 dy = 0 # Prevent further vertical move check
                 break # Exit after first vertical collision found

         # If no vertical collision occurred, apply the original dy movement
        if dy != 0:
            self.rect.y += dy
            self.pos.y = self.rect.midbottom[1] # Update pos


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, block_type='brick'):
        super().__init__()
        self.block_type = block_type
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
        self.draw_block()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw_block(self):
        if self.block_type == 'brick':
            draw_brick_block(self.image, BLOCK_SIZE, BLOCK_SIZE)
        elif self.block_type == 'question':
            draw_question_block(self.image, BLOCK_SIZE, BLOCK_SIZE)
        elif self.block_type == 'ground':
            draw_ground_block(self.image, BLOCK_SIZE, BLOCK_SIZE)
        else: # Default fallback
            self.image.fill(BROWN)
            pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 1)

    def hit(self, player):
        # Specific hit behavior for block types, meow!
        if self.block_type == 'question':
            print("Nya! Hit a question block!")
            # Maybe spawn a coin or powerup here later?
            # Change to a 'used' block type?
            self.block_type = 'ground' # Change to plain block for now
            self.draw_block() # Redraw it
        elif self.block_type == 'brick':
             print("Bonk! Hit a brick block!")
             # Could break if player is 'big' later
             pass # Does nothing for now


class Goomba(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((GOOMBA_WIDTH, GOOMBA_HEIGHT), pygame.SRCALPHA)
        draw_goomba(self.image, GOOMBA_WIDTH, GOOMBA_HEIGHT)
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(-GOOMBA_SPEED, 0) # Start moving left
        self.rect.bottomleft = self.pos
        self.on_ground = False

    def update(self):
        # Basic AI: walk left/right, turn at edges or walls
        self.pos.x += self.vel.x
        self.rect.bottomleft = self.pos

        # Simple gravity simulation (doesn't need to be perfect for Goombas)
        if not self.on_ground:
            self.pos.y += 3 # Fall slowly if pushed off edge
            self.rect.bottomleft = self.pos


    def collide_with_world(self):
        self.rect.bottomleft = self.pos # Ensure rect is up-to-date before checks

        # Check horizontal collision with blocks
        hit_wall = False
        for block in self.game.blocks:
            if self.rect.colliderect(block.rect):
                 # Simple collision response: reverse direction
                 # More precise check needed to avoid sticking inside blocks briefly
                if self.vel.x > 0: # Moving right
                    self.rect.right = block.rect.left
                elif self.vel.x < 0: # Moving left
                    self.rect.left = block.rect.right
                self.vel.x *= -1 # Reverse direction
                self.pos.x = self.rect.bottomleft[0]
                hit_wall = True
                break # Only need one collision


        # Check if standing on ground
        self.rect.y += 1 # Move down slightly to check for ground
        self.on_ground = False
        for block in self.game.blocks:
            if self.rect.colliderect(block.rect):
                self.rect.bottom = block.rect.top # Snap to top of block
                self.pos.y = self.rect.bottomleft[1]
                self.on_ground = True
                break
        if not self.on_ground:
             self.rect.y -= 1 # Move back up if no ground found

        # Check if about to walk off an edge (if no wall was hit)
        if not hit_wall and self.on_ground:
            probe_dist = self.rect.width / 2 * (1 if self.vel.x > 0 else -1)
            probe_x = self.rect.centerx + probe_dist
            probe_y = self.rect.bottom + 5 # Check slightly below feet
            
            ground_ahead = False
            for block in self.game.blocks:
                 # Check if a block exists near where the Goomba is heading
                 if block.rect.collidepoint(probe_x, probe_y):
                     ground_ahead = True
                     break
            
            if not ground_ahead:
                 self.vel.x *= -1 # Turn around at the edge


    def stomp(self):
         print("Squish! Goomba stomped!")
         # Add score, play sound etc. later
         self.kill() # Remove goomba from all groups


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((COIN_WIDTH, COIN_HEIGHT), pygame.SRCALPHA)
        draw_coin(self.image, COIN_WIDTH, COIN_HEIGHT)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.value = 1

    def collect(self, player):
        print("Ding! Coin collected!")
        player.score += self.value
        # Could add animation/sound later
        self.kill()


class Goal(pygame.sprite.Sprite):
     def __init__(self, x, y, width, height):
         super().__init__()
         # The actual visual is the flagpole, the sprite is the collision area
         self.image = pygame.Surface((width, height), pygame.SRCALPHA)
         # Draw the flagpole onto the surface for visualization if needed
         # draw_flagpole(self.image, width, height) # Optional: visualize hit area
         # self.image.fill((0, 255, 0, 100)) # Semi-transparent green for debug
         self.rect = self.image.get_rect()
         self.rect.bottomleft = (x, y + height) # Goal position is usually top-left of flagpole base block

         # Store flagpole visual details separately
         self.pole_x = x + width / 2
         self.pole_bottom_y = y + height
         self.pole_top_y = y
         self.pole_width = width * 0.2


     def draw_visual(self, surface, camera_offset_x):
        """Draw the actual flagpole visual"""
        # Adjust position based on camera
        draw_x = self.pole_x - camera_offset_x
        # Draw Pole
        pygame.draw.line(surface, FLAGPOLE_GRAY, (draw_x, self.pole_bottom_y), (draw_x, self.pole_top_y), int(self.pole_width))
        # Draw Ball
        pygame.draw.circle(surface, FLAGPOLE_BALL, (draw_x, self.pole_top_y), self.pole_width * 1.5)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init() # Initialize font module, nya!
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36) # Default system font
        self.large_font = pygame.font.SysFont(None, 72)
        self.running = True
        self.game_state = STATE_LEVEL_SELECT
        self.current_world = 0
        self.current_level = 0
        self.level_width = SCREEN_WIDTH # Default before loading
        self.camera_offset_x = 0

        # Sprite Groups - initialize empty
        self.all_sprites = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.goal_group = pygame.sprite.GroupSingle() # Only one goal

        # Level select options
        self.level_options = [
            {"text": "World 1-1", "world": 0, "level": 0, "rect": None},
            {"text": "World 1-2", "world": 0, "level": 1, "rect": None},
            {"text": "World 1-3", "world": 0, "level": 2, "rect": None},
        ]
        self.selected_option = 0

    def start_level(self, world, level):
        print(f"Starting Level W{world+1}-{level+1}, meow!")
        self.current_world = world
        self.current_level = level

        # Clear existing sprites before loading new level
        self.all_sprites.empty()
        self.blocks.empty()
        self.enemies.empty()
        self.coins.empty()
        self.goal_group.empty()

        # Load level data
        level_data = load_level_data(world, level)
        self.level_width = level_data['width']

        # Create player instance at start position (e.g., bottom-left)
        player_start_x = BLOCK_SIZE * 2
        player_start_y = SCREEN_HEIGHT - BLOCK_SIZE * 3 # Adjust as needed
        self.player = Player(self, player_start_x, player_start_y)
        self.all_sprites.add(self.player)

        # Create blocks
        for bx, by, btype in level_data['blocks']:
            block = Block(bx, by, btype)
            self.all_sprites.add(block)
            self.blocks.add(block)

        # Create enemies
        for ex, ey in level_data['enemies']:
            goomba = Goomba(self, ex, ey - GOOMBA_HEIGHT) # Place bottom at ey
            self.all_sprites.add(goomba)
            self.enemies.add(goomba)

        # Create coins
        for cx, cy in level_data['coins']:
            coin = Coin(cx, cy)
            self.all_sprites.add(coin)
            self.coins.add(coin)

        # Create goal
        if level_data['goal']:
            gx, gy, gw, gh = level_data['goal']
            self.goal = Goal(gx, gy, gw, gh)
            # self.all_sprites.add(self.goal) # Don't add invisible rect to all_sprites
            self.goal_group.add(self.goal) # Add to its own group for collision

        self.camera_offset_x = 0 # Reset camera
        self.game_state = STATE_PLAYING

    def update_camera(self):
        # Simple camera follows player horizontally
        target_camera_x = self.player.rect.centerx - SCREEN_WIDTH / 3
        # Clamp camera to level boundaries
        self.camera_offset_x = max(0, min(target_camera_x, self.level_width - SCREEN_WIDTH))

    def run_level_select(self):
         # Event handling for level select
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.level_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.level_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    chosen = self.level_options[self.selected_option]
                    self.start_level(chosen["world"], chosen["level"])
                    return # Exit this loop once level starts
            if event.type == pygame.MOUSEBUTTONDOWN:
                 mouse_pos = pygame.mouse.get_pos()
                 for i, option in enumerate(self.level_options):
                     if option["rect"] and option["rect"].collidepoint(mouse_pos):
                         self.start_level(option["world"], option["level"])
                         return # Exit this loop

         # Drawing the level select screen
        self.screen.fill(SKY_BLUE)
        title_surf = self.large_font.render("Select a Level, Purr!", True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.2))
        self.screen.blit(title_surf, title_rect)

        option_y_start = SCREEN_HEIGHT * 0.4
        option_spacing = 60
        for i, option in enumerate(self.level_options):
            color = YELLOW if i == self.selected_option else WHITE
            text_surf = self.font.render(option["text"], True, color)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, option_y_start + i * option_spacing))
            self.level_options[i]["rect"] = text_rect # Store rect for mouse clicks
            self.screen.blit(text_surf, text_rect)

        pygame.display.flip()
        self.clock.tick(FPS) # Keep ticking even in menu


    def run_gameplay(self):
        # Event handling for gameplay
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                     self.player.jump()
                 if event.key == pygame.K_ESCAPE: # Go back to level select
                     self.game_state = STATE_LEVEL_SELECT

        # Update all sprites (like player movement intention)
        self.all_sprites.update()

        # --- Collision Detection and Response --- Nya! Important part!
        # Calculate intended movement
        dx = self.player.vel.x + 0.5 * self.player.acc.x
        dy = self.player.vel.y + 0.5 * self.player.acc.y

        # Player vs Blocks Collision
        self.player.collide_with_blocks(dx, dy)


        # Player vs Coins
        coin_hits = pygame.sprite.spritecollide(self.player, self.coins, False) # False = don't kill yet
        for coin in coin_hits:
            coin.collect(self.player)

        # Player vs Enemies
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemy_hits:
             # Check if player landed on top (stomp!)
             # A bit below player's feet, within enemy's width
            stomp_check_y = self.player.rect.bottom + 5
            stomp_check_x = self.player.rect.centerx
            is_stomp = (self.player.vel.y > 0 and # Player is falling
                         enemy.rect.collidepoint(stomp_check_x, stomp_check_y) and
                         self.player.rect.bottom <= enemy.rect.centery) # Make sure feet are above enemy center

            if is_stomp:
                 enemy.stomp()
                 self.player.vel.y = PLAYER_JUMP * 0.6 # Small bounce after stomp, meow!
            else:
                 # Player hit enemy from side/bottom - reset level for simplicity
                 print("Ouch! Player hit by enemy!")
                 self.start_level(self.current_world, self.current_level) # Restart
                 return # Exit update loop for this frame


        # Enemy vs Blocks/World (turn around, etc.)
        for enemy in self.enemies:
             if hasattr(enemy, 'collide_with_world'):
                 enemy.collide_with_world()

        # Player vs Goal
        if self.goal and pygame.sprite.spritecollide(self.player, self.goal_group, False):
            print("Level Complete! Nya!")
            self.game_state = STATE_LEVEL_COMPLETE # Go to completion state


        # Update Camera based on player position
        self.update_camera()

        # --- Drawing ---
        self.screen.fill(SKY_BLUE)

        # Draw everything offset by the camera
        for sprite in self.all_sprites:
            # Special draw for enemies/player if needed, or just use image
            self.screen.blit(sprite.image, (sprite.rect.x - self.camera_offset_x, sprite.rect.y))

        # Draw the goal flagpole separately
        if self.goal:
            self.goal.draw_visual(self.screen, self.camera_offset_x)

        # Draw HUD (Score) - fixed position
        score_surf = self.font.render(f"Score: {self.player.score}", True, WHITE)
        score_rect = score_surf.get_rect(topleft=(10, 10))
        self.screen.blit(score_surf, score_rect)

        pygame.display.flip()
        self.clock.tick(FPS)

    def run_level_complete(self):
        # Simple "Level Complete" screen
        for event in pygame.event.get():
             if event.type == pygame.QUIT:
                 self.running = False
             if event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                     self.game_state = STATE_LEVEL_SELECT # Go back to level select

        self.screen.fill(DARK_BLUE)
        win_surf = self.large_font.render("Level Clear! Meow!", True, YELLOW)
        win_rect = win_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.4))
        self.screen.blit(win_surf, win_rect)

        prompt_surf = self.font.render("Press Enter to Continue", True, WHITE)
        prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.6))
        self.screen.blit(prompt_surf, prompt_rect)

        pygame.display.flip()
        self.clock.tick(FPS) # Keep ticking


    def game_loop(self):
        """Main game loop that switches between states"""
        if self.game_state == STATE_LEVEL_SELECT:
            self.run_level_select()
        elif self.game_state == STATE_PLAYING:
            self.run_gameplay()
        elif self.game_state == STATE_LEVEL_COMPLETE:
            self.run_level_complete()

async def main():
    print("Starting game, meow!")
    game = Game()
    while game.running:
        game.game_loop()
        # Yield control for async environment (important for web/emscripten)
        await asyncio.sleep(0) # Yield control immediately

    print("Exiting game, bye nya!")
    pygame.quit()
    sys.exit()

# --- Main Execution ---
if __name__ == "__main__":
    # Check if running in standard Python or Emscripten (web)
    if platform.system() == "Emscripten":
        print("Running in Emscripten mode, meow!")
        asyncio.run(main()) # Use asyncio.run for Emscripten compatibility
    else:
        print("Running in standard Python mode, nya!")
        # For standard desktop Python, you can often just call the loop directly
        # if the async structure isn't strictly needed, but using run() is safer.
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\nGame interrupted by user, purr...")
            pygame.quit()
            sys.exit()
