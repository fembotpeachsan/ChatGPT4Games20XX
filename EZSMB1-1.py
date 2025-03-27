# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Nintendo Ultra Simulator (UltraSim) - Pygame Simulation EXPANDED
# Version: X-NINT 1.0 SGI [P]ygame [Sim]ulation v1.2 (World 1-1 Layout Attempt)
# Team: (Simulated) Flames 20XX (User Request)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# WARNING: This attempts to recreate the static layout of SMB World 1-1
#          programmatically based on a visual reference image.
#          - It is extremely verbose and hardcoded.
#          - Visuals are approximations using pygame.draw.
#          - Advanced mechanics (Koopas, Piranhas, Flagpole) are NOT implemented.
#          - Creating full games this way is highly impractical.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import pygame
import sys
import random
import math

# --- Constants ---
SCREEN_WIDTH = 600 # The visible window size
SCREEN_HEIGHT = 400
TARGET_FPS = 60
TILE = 16 # Pixel size of a standard tile

# Colors (approximations from NES palette)
COLOR_SKY_BLUE = (92, 148, 252)
COLOR_BRICK = (200, 76, 12)
COLOR_BRICK_MORTAR = (0, 0, 0)
COLOR_GROUND_TOP = (228, 152, 56)
COLOR_GROUND_FILL = (180, 110, 40)
COLOR_PIPE_GREEN = (0, 168, 0)
COLOR_PIPE_SHADOW = (0, 104, 0)
COLOR_PIPE_HIGHLIGHT = (116, 252, 116)
COLOR_QUESTION_BLOCK = (252, 152, 56)
COLOR_QUESTION_MARK = (0, 0, 0)
COLOR_EMPTY_BLOCK = (140, 60, 10)
COLOR_MARIO_RED = (255, 0, 0)
COLOR_MARIO_BLUE = (0, 0, 255)
COLOR_MARIO_SKIN = (252, 192, 168)
COLOR_MARIO_BROWN = (128, 64, 0)
COLOR_GOOMBA_BROWN = (140, 60, 10)
COLOR_GOOMBA_FEET = (80, 40, 0)
COLOR_MUSHROOM_RED = (255, 0, 0)
COLOR_MUSHROOM_WHITE = (255, 255, 255)
COLOR_COIN = (252, 224, 56)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_HILL_GREEN = (0, 168, 0) # Same as pipe green for simplicity
COLOR_HILL_SHADOW = (0, 104, 0) # Same as pipe shadow
COLOR_CLOUD = (255, 255, 255)
COLOR_FLAGPOLE = (192, 192, 192) # Silver
COLOR_FLAG = COLOR_WHITE
COLOR_CASTLE_BRICK = COLOR_BRICK # Reuse brick color
COLOR_CASTLE_DOOR = COLOR_BLACK
COLOR_CASTLE_WINDOW = COLOR_BLACK
COLOR_CASTLE_TOP = (160, 160, 160) # Greyish

# Physics & Gameplay Settings
GRAVITY = 0.35
JUMP_STRENGTH = -9
PLAYER_ACC = 0.35
PLAYER_FRICTION = -0.12
PLAYER_MAX_SPEED_X = 4.5
GOOMBA_SPEED = -0.6
STOMP_BOUNCE = -4
MUSHROOM_SPEED = 1.0
COIN_SCORE = 200
MUSHROOM_SCORE = 1000
GOOMBA_SCORE = 100
GAME_START_TIME = 400
BRICK_BREAK_SCORE = 50
LEVEL_END_X = TILE * 210 # Approximate end coordinate for camera clamping

# --- Background Element Drawing Functions ---
# These draw static, non-interactive elements directly onto the screen surface

def draw_cloud(surface, x, y, size, offset_x):
    """Draws a simple cloud approximation."""
    draw_x = round(x - offset_x)
    # Basic culling
    if draw_x + size * TILE * 2 < 0 or draw_x > SCREEN_WIDTH:
        return

    base_y = y
    # Simple cloud shape using circles/ellipses
    pygame.draw.ellipse(surface, COLOR_CLOUD, (draw_x, base_y, TILE*2, TILE))
    pygame.draw.ellipse(surface, COLOR_CLOUD, (draw_x + TILE*0.8, base_y - TILE*0.5, TILE*1.5, TILE*0.8))
    if size > 1: # Medium cloud
        pygame.draw.ellipse(surface, COLOR_CLOUD, (draw_x + TILE*1.5, base_y, TILE*2, TILE))
    if size > 2: # Large cloud
         pygame.draw.ellipse(surface, COLOR_CLOUD, (draw_x + TILE*2.5, base_y - TILE*0.3, TILE*2, TILE*0.9))

def draw_hill(surface, x, y, size, offset_x):
    """Draws a simple hill approximation."""
    draw_x = round(x - offset_x)
    # Basic culling
    width = TILE * (3 if size == 1 else 5) # Small hill 3 tiles, large 5 tiles wide
    height = TILE * (1.5 if size == 1 else 2.5) # Small 1.5, large 2.5 tiles high
    if draw_x + width < 0 or draw_x > SCREEN_WIDTH:
        return

    base_y = y + TILE * 2 # Hills start from the ground line
    hill_rect = pygame.Rect(draw_x, base_y - height, width, height)

    # Draw main shape (ellipse top on a rect base)
    pygame.draw.ellipse(surface, COLOR_HILL_GREEN, hill_rect)
    pygame.draw.rect(surface, COLOR_HILL_GREEN, (hill_rect.left, hill_rect.centery, hill_rect.width, hill_rect.height / 2))
    # Simple shadow line
    pygame.draw.line(surface, COLOR_HILL_SHADOW, (hill_rect.left + 5, hill_rect.centery+2), (hill_rect.centerx, hill_rect.bottom - 3), 2)

def draw_flagpole(surface, x, y, offset_x):
    """Draws a simplified flagpole."""
    draw_x = round(x - offset_x)
    pole_height = TILE * 9
    base_y = y + TILE * 2 # Starts from ground line

    # Basic culling
    if draw_x + TILE < 0 or draw_x > SCREEN_WIDTH:
        return

    # Pole
    pygame.draw.rect(surface, COLOR_FLAGPOLE, (draw_x, base_y - pole_height, 4, pole_height))
    # Ball on top
    pygame.draw.circle(surface, COLOR_FLAGPOLE, (draw_x + 2, base_y - pole_height), 5)
    # Flag (Placeholder position)
    # In a real game, flag position depends on player progress
    flag_y = base_y - pole_height + TILE
    pygame.draw.polygon(surface, COLOR_FLAG, [(draw_x+4, flag_y), (draw_x+4+TILE, flag_y + TILE//2), (draw_x+4, flag_y+TILE)])

def draw_castle(surface, x, y, offset_x):
    """Draws a simplified end-level castle."""
    draw_x = round(x - offset_x)
    base_y = y + TILE * 2 # Starts from ground line
    width = TILE * 5
    height = TILE * 5

    # Basic culling
    if draw_x + width < 0 or draw_x > SCREEN_WIDTH:
        return

    # Main structure
    pygame.draw.rect(surface, COLOR_CASTLE_BRICK, (draw_x, base_y - height, width, height))
    # Door
    door_width = TILE * 1.5
    door_height = TILE * 2
    pygame.draw.rect(surface, COLOR_CASTLE_DOOR, (draw_x + width/2 - door_width/2, base_y - door_height, door_width, door_height))
    # Top battlements (simplified)
    battlement_h = TILE * 0.5
    battlement_y = base_y - height - battlement_h
    for i in range(4):
        pygame.draw.rect(surface, COLOR_CASTLE_BRICK, (draw_x + i * width/4, battlement_y, width/4 - 2, battlement_h))
    # Central tower bit (simplified)
    tower_w = TILE
    tower_h = TILE * 1.5
    pygame.draw.rect(surface, COLOR_CASTLE_BRICK, (draw_x + width/2 - tower_w/2, base_y - height - tower_h, tower_w, tower_h))
    pygame.draw.rect(surface, COLOR_CASTLE_TOP, (draw_x + width/2 - tower_w/2, base_y - height - tower_h - 2, tower_w, 2)) # Top line


# --- Game Object Classes (Copied from previous version, minor adjustments possible) ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.state = "small" # small, big, fire (not implemented)
        self.invincible_timer = 0
        self.invincible_duration = 1000 # 1 second invincibility after getting hit
        # Initialize rect with default size *before* calling set_size
        self.rect = pygame.Rect(0, 0, TILE, TILE)
        self.pos = pygame.Vector2(SCREEN_WIDTH // 5, SCREEN_HEIGHT - TILE*2 - 1)  # Initialize pos before set_size
        self.set_size() # Now set_size can safely use self.rect
        self.image = pygame.Surface(self.size, pygame.SRCALPHA) # Use SRCALPHA for potential transparency
        # self.rect is set within set_size now
        self.pos = pygame.Vector2(self.rect.centerx, self.rect.bottom) # Position based on bottom center
        self.vel = pygame.Vector2(0, 0)
        self.acc = pygame.Vector2(0, 0)
        self.on_ground = False
        self.last_jump_time = 0
        self.last_on_ground_time = 0
        self.facing_right = True # For drawing direction
        self.is_dead = False # Flag for death animation state
        self.death_timer = 0
        # Mario 35 specific movement variables
        self.run_speed = 1.5  # Multiplier for running
        self.is_running = False
        self.skid_timer = 0
        self.max_walk_speed = 3.0
        self.max_run_speed = 5.5
        self.jump_cut_magnitude = 0.4  # How much to cut jump when button released

    def set_size(self):
        if self.state == "big":
            self.size = (TILE, TILE * 2)
        else: # small or fire (uses small collision for now)
            self.size = (TILE, TILE)
        # Adjust rect position when size changes to keep feet roughly in place
        old_bottom = self.rect.bottom if hasattr(self, 'rect') and self.rect else SCREEN_HEIGHT - TILE*2 - 1
        old_centerx = self.rect.centerx if hasattr(self, 'rect') and self.rect else SCREEN_WIDTH // 5 + TILE // 2
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.bottom = old_bottom
        self.rect.centerx = old_centerx
        # Make sure pos is updated after rect is finalized
        if not hasattr(self, 'pos') or self.pos is None: # Initial setup case
             self.pos = pygame.Vector2(self.rect.centerx, self.rect.bottom)
        else: # Size change case
             self.pos.y = self.rect.bottom
             self.pos.x = self.rect.centerx

    def jump(self):
        if self.is_dead: return
        now = pygame.time.get_ticks()
        # Allow jumping shortly after falling off a ledge (coyote time - basic)
        if (self.on_ground or now - self.last_on_ground_time < 100) and now - self.last_jump_time > 100: # Small debounce
            jump_power = JUMP_STRENGTH
            # Boost jump if running at high speed
            if abs(self.vel.x) > self.max_walk_speed:
                jump_power *= 1.2
            self.vel.y = jump_power
            self.on_ground = False
            self.last_jump_time = now

    def jump_cut(self):
        """Cut jump height when button is released"""
        if self.vel.y < 0:  # Only if moving upward
            self.vel.y *= self.jump_cut_magnitude

    def grow(self):
        if self.is_dead: return
        if self.state == "small":
            self.state = "big"
            current_bottom = self.rect.bottom
            self.set_size()
            self.rect.bottom = current_bottom # Keep feet on ground
            self.pos.y = self.rect.bottom
            # TODO: Add growing animation/sound effect

    def shrink(self):
         if self.is_dead: return
         if self.state == "big" and self.invincible_timer == 0:
            self.state = "small"
            current_bottom = self.rect.bottom
            self.set_size()
            self.rect.bottom = current_bottom # Keep feet on ground
            self.pos.y = self.rect.bottom
            self.invincible_timer = pygame.time.get_ticks() # Start invincibility
            # TODO: Add shrinking animation/sound effect

    def die(self):
        if not self.is_dead:
            print("Player Died")
            self.is_dead = True
            self.state = "small" # Visuals for death anim often use small Mario
            self.set_size() # Use small size for anim
            self.vel.x = 0
            self.vel.y = -8 # Initial bounce up for death anim
            self.acc.x = 0
            self.death_timer = pygame.time.get_ticks()
            # No more input, gravity takes over after initial bounce

    def hit(self):
        """Called when Mario gets hit. Returns True if player should die, False otherwise."""
        if self.is_dead or self.invincible_timer > 0: # Already dead or invincible
            return False

        if self.state == "big":
            self.shrink()
            return False # Indicate damage taken but not death
        else:
            # self.die() # Trigger death sequence
            return True # Indicate death should happen

    def update(self, platforms, delta_time):
        now = pygame.time.get_ticks()

        # --- Death Animation ---
        if self.is_dead:
            # Simple death: bounce up, fall down through everything
            self.vel.y += GRAVITY * 1.5 # Fall faster
            self.pos.y += self.vel.y
            self.rect.bottom = round(self.pos.y)
            # Check if fallen off screen
            if self.pos.y > SCREEN_HEIGHT + TILE*2 and now - self.death_timer > 1000:
                # TODO: Trigger game over sequence / life decrement
                pygame.event.post(pygame.event.Event(pygame.QUIT)) # Simple quit for now
            return # Skip normal updates during death anim

        # --- Invincibility Timer ---
        if self.invincible_timer > 0 and now - self.invincible_timer > self.invincible_duration:
            self.invincible_timer = 0

        # --- Input and Acceleration ---
        keys = pygame.key.get_pressed()
        
        # Reset acceleration each frame
        self.acc = pygame.Vector2(0, GRAVITY)
        
        # Running flag - Mario 35 style
        self.is_running = keys[pygame.K_z] or keys[pygame.K_s]
        speed_multiplier = self.run_speed if self.is_running else 1.0
        
        # Direction input
        moving_left = keys[pygame.K_LEFT]
        moving_right = keys[pygame.K_RIGHT]
        
        # Mario 35 style acceleration based on direction
        if moving_left:
            self.acc.x = -PLAYER_ACC * speed_multiplier
            self.facing_right = False
        if moving_right:
            self.acc.x = PLAYER_ACC * speed_multiplier
            self.facing_right = True
            
        # Skidding - when changing direction at speed
        is_skidding = False
        if (moving_right and self.vel.x < -1.0) or (moving_left and self.vel.x > 1.0):
            # Higher friction when changing direction at speed
            self.acc.x += self.vel.x * PLAYER_FRICTION * 2.5
            is_skidding = True
            self.skid_timer = now
        # Skid effect lasts briefly for animation
        elif now - self.skid_timer < 100:
            is_skidding = True

        # Normal friction when not accelerating or skidding
        if (not moving_left and not moving_right) or abs(self.vel.x) > 0.1:
            self.acc.x += self.vel.x * PLAYER_FRICTION

        # --- Equations of Motion ---
        # Apply acceleration scaled by delta time
        self.vel.x += self.acc.x * (delta_time * 60)
        self.vel.y += self.acc.y * (delta_time * 60)
        
        # Speed limits - different for walking vs running
        max_speed = self.max_run_speed if self.is_running else self.max_walk_speed
        if abs(self.vel.x) > max_speed:
            self.vel.x = math.copysign(max_speed, self.vel.x)
            
        # Stop if very slow and no acceleration
        if abs(self.vel.x) < 0.1 and abs(self.acc.x) < PLAYER_ACC * 0.5:
            self.vel.x = 0

        # --- Collision Detection ---
        # Store time if on ground for coyote time
        if self.on_ground:
            self.last_on_ground_time = now

        # Move X first, check collision, correct
        self.pos.x += self.vel.x * (delta_time * 60) # Scale velocity by delta time
        self.rect.centerx = round(self.pos.x)
        collided_platforms_x = pygame.sprite.spritecollide(self, platforms, False)
        for plat in collided_platforms_x:
            # Ensure sprite doesn't collide with itself (shouldn't happen but safe)
            if plat == self: continue
            # Only collide with solid types horizontally (add more types if needed)
            if plat.type in ["ground", "brick", "question", "pipe", "stair_block", "empty_block"]:
                if self.vel.x > 0: # Moving right
                    self.rect.right = plat.rect.left
                elif self.vel.x < 0: # Moving left
                    self.rect.left = plat.rect.right
                self.pos.x = self.rect.centerx
                self.vel.x = 0

        # Move Y second, check collision, correct
        self.pos.y += self.vel.y * (delta_time * 60) # Scale velocity by delta time
        self.rect.bottom = round(self.pos.y)
        self.on_ground = False # Assume not on ground until vertical collision check
        collided_platforms_y = pygame.sprite.spritecollide(self, platforms, False)
        for plat in collided_platforms_y:
            if plat == self: continue
            # Only collide with solid types vertically
            if plat.type in ["ground", "brick", "question", "pipe", "stair_block", "empty_block"]:
                # Player's feet were roughly above the platform's top before this frame's vertical movement
                player_feet_prev_y = self.pos.y - self.vel.y * (delta_time * 60)
                # Player's head was roughly below the platform's bottom before this frame's vertical movement
                player_head_prev_y = player_feet_prev_y - self.size[1]

                if self.vel.y > 0: # Moving Down / Landing
                    # Land only if feet were above or very close to the top
                    if player_feet_prev_y <= plat.rect.top + 1:
                        self.rect.bottom = plat.rect.top + 1
                        self.pos.y = self.rect.bottom
                        self.vel.y = 0
                        self.on_ground = True
                        # Don't break here, landing might resolve multiple overlaps if needed
                elif self.vel.y < 0: # Moving Up / Hitting Underside
                     # Hit underside only if head was below or very close to the bottom
                     if player_head_prev_y >= plat.rect.bottom - 1:
                        self.rect.top = plat.rect.bottom
                        self.pos.y = self.rect.bottom
                        self.vel.y = 0
                        # Trigger block hit action if the platform is hittable
                        if hasattr(plat, 'hit'):
                             plat.hit(self) # Pass player
                        # Break after hitting something from below
                        break


        # --- Screen Boundary (Left) ---
        if self.rect.left < camera_x:
            self.rect.left = camera_x
            self.pos.x = self.rect.centerx
            self.vel.x = max(0, self.vel.x) # Prevent moving further left

    def draw_programmatic(self, surface, offset_x):
        # ... (Drawing code remains the same as v1.1, just uses TILE constant) ...
        # Blinking effect when invincible
        if self.invincible_timer > 0:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                return # Skip drawing every other frame to make it blink

        # Special draw for death animation (simple flashing/fading maybe)
        if self.is_dead:
             # Example: Flicker during death anim
             if (pygame.time.get_ticks() // 80) % 2 == 0:
                 return

        draw_x = round(self.rect.x - offset_x)
        draw_y = round(self.rect.y)
        width, height = self.size

        body_color = COLOR_MARIO_RED
        overalls_color = COLOR_MARIO_BLUE
        skin_color = COLOR_MARIO_SKIN
        shoe_color = COLOR_MARIO_BROWN

        if height == TILE: # Small Mario
            pygame.draw.rect(surface, body_color, (draw_x, draw_y, width, int(height * 0.6)))
            pygame.draw.rect(surface, skin_color, (draw_x + int(width * 0.25), draw_y + int(height * 0.2), int(width * 0.5), int(height * 0.3)))
            pygame.draw.rect(surface, overalls_color, (draw_x + int(width * 0.1), draw_y + int(height * 0.5), int(width * 0.8), int(height * 0.3)))
            foot_width = int(width * 0.4)
            foot_height = int(height * 0.3)
            feet_y = draw_y + int(height * 0.7)
            pygame.draw.rect(surface, shoe_color, (draw_x + int(width * 0.1), feet_y, foot_width, foot_height))
            pygame.draw.rect(surface, shoe_color, (draw_x + int(width * 0.5), feet_y, foot_width, foot_height))

        elif height == TILE * 2: # Big Mario
            pygame.draw.rect(surface, body_color, (draw_x + 2, draw_y, 12, 4)) # Hat top
            pygame.draw.rect(surface, body_color, (draw_x + 0, draw_y + 4, TILE, 4)) # Hat brim
            pygame.draw.rect(surface, skin_color, (draw_x + 4, draw_y + 4, 8, 4)) # Face upper
            pygame.draw.rect(surface, shoe_color, (draw_x + 2, draw_y + 8, 12, 4)) # Hair/Sideburns
            pygame.draw.rect(surface, body_color, (draw_x, draw_y + 12, TILE, 8)) # Shirt torso
            pygame.draw.rect(surface, overalls_color, (draw_x + 2, draw_y + 12, 12, 12)) # Overalls main
            pygame.draw.rect(surface, overalls_color, (draw_x + 0, draw_y + 14, 4, 6)) # Strap L
            pygame.draw.rect(surface, overalls_color, (draw_x + 12, draw_y + 14, 4, 6)) # Strap R
            arm_y = draw_y + 14; arm_w = 4; arm_h = 6
            if self.facing_right:
                pygame.draw.rect(surface, skin_color, (draw_x + TILE - arm_w + 2, arm_y, arm_w, arm_h)) # R arm
                pygame.draw.rect(surface, body_color, (draw_x - 2, arm_y, arm_w, arm_h)) # L arm behind
            else:
                 pygame.draw.rect(surface, skin_color, (draw_x - 2, arm_y, arm_w, arm_h)) # L arm
                 pygame.draw.rect(surface, body_color, (draw_x + TILE - arm_w + 2, arm_y, arm_w, arm_h))# R arm behind
            legs_y = draw_y + 24; leg_w = 6; leg_h = 8
            pygame.draw.rect(surface, shoe_color, (draw_x + 0, legs_y, leg_w, leg_h)) # L leg/foot
            pygame.draw.rect(surface, shoe_color, (draw_x + TILE - leg_w, legs_y, leg_w, leg_h)) # R leg/foot

    def input(self, key):
        """Handle key input events"""
        if key == pygame.K_SPACE or key == pygame.K_UP:
            self.jump()
        elif key == pygame.K_SPACE or key == pygame.K_UP:
            if self.vel.y < 0:  # Only if still moving upward
                self.jump_cut()  # Cut jump height when button is released


class Platform(pygame.sprite.Sprite):
    # ... (Platform class code largely the same, but draw_programmatic handles more types) ...
    def __init__(self, x, y, width, height, type="ground", text=None, breakable=False):
        super().__init__()
        self.type = type
        # Ensure width and height are at least 1
        width = max(1, width)
        height = max(1, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.original_y = y
        self.text = text
        self.breakable = breakable
        self.hit_state = 0 # 0: normal, 1: bumping, 2: empty/used
        self.hit_timer = 0
        self.item_spawn_info = None

        # Store type for drawing after becoming empty
        self.original_type = type
        if type == "question":
             self.empty_type = "empty_block"
        else:
             self.empty_type = type # Bricks, ground etc keep their look when 'empty' unless broken

    def hit(self, player_hitting):
        global score, coins
        if self.hit_state != 0: return

        is_bumping = False
        spawn_item = None
        award_score = 0
        award_coins = 0
        break_block = False

        if self.type == "question":
            if self.text:
                spawn_item = self.text
                if self.text == "coin":
                     award_score = COIN_SCORE
                     award_coins = 1
                # Mushrooms etc score awarded on collection
                self.text = None # Mark item as used
            is_bumping = True
            self.type = self.empty_type # Change type immediately for collision logic
            self.hit_state = 1 # Start bumping visual

        elif self.type == "brick":
            if player_hitting.state == "big" and self.breakable:
                award_score = BRICK_BREAK_SCORE
                break_block = True # Schedule block removal
            else: # Small Mario hit, or Big hit non-breakable
                if self.text == "coin": # Secret coin
                     spawn_item = "coin"
                     award_score = COIN_SCORE
                     award_coins = 1
                     self.text = None # Only one coin
                # TODO: Play bump sound if no coin
                is_bumping = True # Always bump bricks unless broken

        # Process Actions
        if spawn_item:
            self.item_spawn_info = (spawn_item, (self.rect.centerx, self.rect.top))
        if award_score > 0:
            score += award_score
        if award_coins > 0:
            coins += award_coins
        if is_bumping and not break_block:
            self.hit_state = 1
            self.hit_timer = pygame.time.get_ticks()
            self.rect.y -= 4 # Visual bump up
        if break_block:
             # TODO: Spawn particle effect
             self.kill() # Remove block immediately

    def update(self, *args):
        if self.hit_state == 1: # During bump animation
            now = pygame.time.get_ticks()
            bump_duration = 100
            if now - self.hit_timer > bump_duration:
                self.rect.y = self.original_y # Move back down
                # Question blocks stay visually empty, others revert state
                if self.original_type == "question":
                    self.hit_state = 2 # Visually empty
                else:
                    self.hit_state = 0 # Brick bump finishes
                self.hit_timer = 0

    def draw_programmatic(self, surface, offset_x):
        draw_x = round(self.rect.x - offset_x)
        draw_y = round(self.rect.y)
        width = self.rect.width
        height = self.rect.height
        # Basic Culling
        if draw_x + width < 0 or draw_x > SCREEN_WIDTH or draw_y + height < 0 or draw_y > SCREEN_HEIGHT:
            return

        draw_rect = pygame.Rect(draw_x, draw_y, width, height)

        current_draw_type = self.type
        if self.hit_state == 2 and self.original_type == "question":
             current_draw_type = "empty_block" # Draw visually empty

        # Colors
        block_color = COLOR_EMPTY_BLOCK
        outline_color = COLOR_BLACK

        if current_draw_type == "ground":
            pygame.draw.rect(surface, COLOR_GROUND_FILL, draw_rect)
            for tile_x_rel in range(0, width, TILE):
                 for tile_y_rel in range(0, height, TILE):
                     # Draw only the top layer differently
                     is_top_layer = (tile_y_rel == 0)
                     brick_rect = pygame.Rect(draw_x + tile_x_rel, draw_y + tile_y_rel, TILE, TILE)
                     pygame.draw.rect(surface, COLOR_GROUND_TOP if is_top_layer else COLOR_GROUND_FILL, brick_rect)
                     pygame.draw.rect(surface, COLOR_BRICK_MORTAR, brick_rect, 1)

        elif current_draw_type in ["brick", "stair_block"]: # Stair blocks look like bricks
            block_color = COLOR_BRICK
            outline_color = COLOR_BRICK_MORTAR
            pygame.draw.rect(surface, block_color, draw_rect)
            pygame.draw.rect(surface, outline_color, draw_rect, 1)
            # Mortar lines
            for row in range(1, height // (TILE // 2)): # Horizontal lines every half tile
                 hline_y = draw_y + row * (TILE // 2)
                 pygame.draw.line(surface, outline_color, (draw_x, hline_y), (draw_x + width - 1, hline_y))
            for col in range(1, width // TILE): # Vertical lines every full tile
                 vline_x = draw_x + col * TILE
                 stagger = TILE//2 if (col % 2 != 0) else 0 # Simple stagger TBD
                 pygame.draw.line(surface, outline_color, (vline_x, draw_y), (vline_x, draw_y + height - 1))


        elif current_draw_type == "question":
            block_color = COLOR_QUESTION_BLOCK
            pygame.draw.rect(surface, block_color, draw_rect)
            pygame.draw.rect(surface, outline_color, draw_rect, 1)
            # Flashing '?'
            if (pygame.time.get_ticks() // 200) % 3 != 0:
                q_center_x = draw_rect.centerx; q_center_y = draw_rect.centery
                pygame.draw.line(surface, COLOR_QUESTION_MARK, (q_center_x - 3, q_center_y - 4), (q_center_x + 3, q_center_y - 4), 2)
                pygame.draw.line(surface, COLOR_QUESTION_MARK, (q_center_x + 3, q_center_y - 4), (q_center_x + 3, q_center_y - 1), 2)
                pygame.draw.line(surface, COLOR_QUESTION_MARK, (q_center_x + 3, q_center_y - 1), (q_center_x - 1, q_center_y + 1), 2)
                pygame.draw.line(surface, COLOR_QUESTION_MARK, (q_center_x, q_center_y + 4), (q_center_x, q_center_y + 6), 2) # Dot

        elif current_draw_type == "empty_block":
            block_color = COLOR_EMPTY_BLOCK
            pygame.draw.rect(surface, block_color, draw_rect)
            pygame.draw.rect(surface, outline_color, draw_rect, 1)

        elif current_draw_type == "pipe":
             pygame.draw.rect(surface, COLOR_PIPE_GREEN, draw_rect)
             rim_height = 8
             rim_rect = pygame.Rect(draw_x - 2, draw_y, width + 4, rim_height)
             pygame.draw.rect(surface, COLOR_PIPE_GREEN, rim_rect)
             body_draw_y = draw_y + rim_height
             body_height = height - rim_height
             if body_height > 0:
                 pygame.draw.line(surface, COLOR_PIPE_SHADOW, (draw_x + 3, body_draw_y), (draw_x + 3, body_draw_y + body_height), 4)
                 pygame.draw.line(surface, COLOR_PIPE_HIGHLIGHT, (draw_x + width - 5, body_draw_y), (draw_x + width - 5, body_draw_y + body_height), 3)
             pygame.draw.rect(surface, COLOR_BLACK, rim_rect, 1)
             pygame.draw.rect(surface, COLOR_BLACK, draw_rect, 1)


class Goomba(pygame.sprite.Sprite):
    # ... (Goomba class code remains largely the same as v1.1) ...
    def __init__(self, x, y):
        super().__init__()
        self.size = (TILE, TILE)
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        # Position based on bottom-left corner on the ground level (y = ground_top_y)
        self.rect.bottomleft = (x, y + 1) # y is the ground top line
        self.pos = pygame.Vector2(self.rect.centerx, self.rect.bottom)
        self.vel = pygame.Vector2(GOOMBA_SPEED, 0)
        self.on_ground = False
        self.state = "walk" # walk, squished
        self.kill_timer = 0

    def update(self, platforms, delta_time):
        global GOOMBA_REMOVE_DELAY
        
        if self.state == "walk":
            # Vertical Movement & Gravity
            self.vel.y += GRAVITY * (delta_time * 60)
            self.pos.y += self.vel.y * (delta_time * 60)
            self.rect.bottom = round(self.pos.y)

            # Vertical Collision (Landing)
            self.on_ground = False
            hits_y = pygame.sprite.spritecollide(self, platforms, False)
            for plat in hits_y:
                 if plat.type in ["ground", "brick", "question", "pipe", "stair_block", "empty_block"]:
                     if self.vel.y > 0 and self.pos.y - self.vel.y * (delta_time*60) <= plat.rect.top + 1:
                         self.rect.bottom = plat.rect.top + 1
                         self.pos.y = self.rect.bottom
                         self.vel.y = 0
                         self.on_ground = True
                         break

            # Horizontal Movement
            self.pos.x += self.vel.x * (delta_time * 60)
            self.rect.centerx = round(self.pos.x)

            # Horizontal Collision (Walls & Turnaround)
            hits_x = pygame.sprite.spritecollide(self, platforms, False)
            wall_hit = False
            for plat in hits_x:
                 if plat.type in ["ground", "brick", "question", "pipe", "stair_block", "empty_block"]:
                      if (self.vel.x > 0 and self.rect.right > plat.rect.left and self.rect.left < plat.rect.left) or \
                         (self.vel.x < 0 and self.rect.left < plat.rect.right and self.rect.right > plat.rect.right):
                           self.vel.x *= -1
                           if self.vel.x < 0: self.rect.right = plat.rect.left
                           else: self.rect.left = plat.rect.right
                           self.pos.x = self.rect.centerx
                           wall_hit = True
                           break

            # Edge Turnaround (Basic)
            if self.on_ground and not wall_hit and abs(self.vel.x) > 0:
                probe_offset_x = math.copysign(self.size[0] // 2 + 2, self.vel.x)
                probe_y = self.rect.bottom + 5
                probe_x = self.rect.centerx + probe_offset_x
                ground_ahead = False
                # Check against all platforms efficiently? Maybe spatial hash later.
                probe_rect = pygame.Rect(probe_x-1, probe_y-1, 2, 2)
                possible_ground = [p for p in platforms if p.rect.colliderect(probe_rect.inflate(TILE*2, 0))] # Optimisation TBD
                for plat in possible_ground: # Use full platforms group for now
                    if plat.rect.collidepoint(probe_x, probe_y) and plat.type in ["ground", "brick", "question", "pipe", "stair_block", "empty_block"]:
                        ground_ahead = True
                        break
                if not ground_ahead:
                     self.vel.x *= -1

        elif self.state == "squished":
            if pygame.time.get_ticks() - self.kill_timer > GOOMBA_REMOVE_DELAY:
                self.kill()

    def stomp(self):
        if self.state == "walk":
            global score
            self.state = "squished"
            self.vel.x = 0; self.vel.y = 0
            squish_height = TILE // 3
            original_bottom = self.rect.bottom
            self.rect.height = squish_height
            self.rect.bottom = original_bottom
            self.kill_timer = pygame.time.get_ticks()
            score += GOOMBA_SCORE
            # TODO: Play stomp sound

    def draw_programmatic(self, surface, offset_x):
        # ... (Drawing code remains the same as v1.1, using TILE) ...
        draw_x = round(self.rect.x - offset_x)
        draw_y = round(self.rect.y)
        # Culling
        if draw_x + TILE < 0 or draw_x > SCREEN_WIDTH: return

        if self.state == "walk":
            pygame.draw.ellipse(surface, COLOR_GOOMBA_BROWN, (draw_x, draw_y, TILE, TILE * 0.75))
            pygame.draw.rect(surface, COLOR_GOOMBA_BROWN, (draw_x, draw_y + TILE * 0.375, TILE, TILE * 0.375))
            feet_y = draw_y + TILE
            pygame.draw.polygon(surface, COLOR_GOOMBA_FEET, [(draw_x, feet_y), (draw_x+5, feet_y), (draw_x+2, feet_y-4)])
            pygame.draw.polygon(surface, COLOR_GOOMBA_FEET, [(draw_x+TILE, feet_y), (draw_x+TILE-5, feet_y), (draw_x+TILE-3, feet_y-4)])
            eye_y = draw_y + TILE * 0.25
            pygame.draw.ellipse(surface, COLOR_WHITE, (draw_x + 2, eye_y, 5, 5))
            pygame.draw.ellipse(surface, COLOR_WHITE, (draw_x + TILE - 7, eye_y, 5, 5))
            pygame.draw.circle(surface, COLOR_BLACK, (draw_x + 4, eye_y + 2), 1)
            pygame.draw.circle(surface, COLOR_BLACK, (draw_x + TILE - 5, eye_y + 2), 1)
        elif self.state == "squished":
             pygame.draw.rect(surface, COLOR_GOOMBA_BROWN, (draw_x, draw_y, TILE, self.rect.height))


class Item(pygame.sprite.Sprite):
    # ... (Item class code remains largely the same as v1.1, using TILE) ...
    def __init__(self, item_type, spawn_pos):
        super().__init__()
        self.type = item_type
        # Adjust size based on type
        if self.type == "coin":
            self.size = (int(TILE * 0.6), int(TILE * 0.9)) # Coin slightly smaller, taller
        else: # Mushroom, Star etc.
            self.size = (TILE, TILE)
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.bottom = spawn_pos[1] # Set bottom at the block's top
        self.rect.centerx = spawn_pos[0] # Set horizontal center
        self.pos = pygame.Vector2(self.rect.centerx, self.rect.bottom)
        self.vel = pygame.Vector2(0, -4) if self.type == "coin" else pygame.Vector2(0, -1.5)
        self.spawn_time = pygame.time.get_ticks()
        self.state = "spawning" # spawning, active, collected
        self.on_ground = False
        self.emerge_target_y = spawn_pos[1] - TILE # Target Y for mushroom emerge

    def update(self, platforms, delta_time):
        now = pygame.time.get_ticks()

        if self.state == "spawning":
            self.pos.y += self.vel.y * (delta_time * 60)
            self.rect.bottom = round(self.pos.y)
            if self.type == "coin":
                if now - self.spawn_time > 80:
                     self.vel.y = 1.5; self.state = "active"
            elif self.type == "mushroom":
                 if self.rect.top <= self.emerge_target_y:
                      self.rect.top = self.emerge_target_y; self.pos.y = self.rect.bottom
                      self.vel.x = MUSHROOM_SPEED; self.vel.y = 0; self.state = "active"

        elif self.state == "active":
            if self.type == "coin":
                self.pos.y += self.vel.y * (delta_time * 60)
                self.vel.y += GRAVITY * 0.3 * (delta_time * 60)
                self.rect.bottom = round(self.pos.y)
                if now - self.spawn_time > 600: self.kill()
            elif self.type == "mushroom":
                # Gravity
                self.vel.y += GRAVITY * (delta_time * 60)
                self.pos.y += self.vel.y * (delta_time * 60)
                self.rect.bottom = round(self.pos.y)
                # Vertical Collision
                self.on_ground = False
                hits_y = pygame.sprite.spritecollide(self, platforms, False)
                for plat in hits_y:
                     if plat.type in ["ground", "brick", "question", "pipe", "stair_block", "empty_block"]:
                         if self.vel.y > 0 and self.pos.y - self.vel.y*(delta_time*60) <= plat.rect.top + 1:
                             self.rect.bottom = plat.rect.top + 1; self.pos.y = self.rect.bottom
                             self.vel.y = 0; self.on_ground = True; break
                # Horizontal Movement
                self.pos.x += self.vel.x * (delta_time * 60)
                self.rect.centerx = round(self.pos.x)
                # Horizontal Collision
                hits_x = pygame.sprite.spritecollide(self, platforms, False)
                for plat in hits_x:
                     if plat.type in ["ground", "brick", "question", "pipe", "stair_block", "empty_block"]:
                          self.vel.x *= -1
                          if self.vel.x < 0: self.rect.right = plat.rect.left
                          else: self.rect.left = plat.rect.right
                          self.pos.x = self.rect.centerx; break

    def draw_programmatic(self, surface, offset_x):
        # ... (Drawing code remains the same as v1.1, using TILE) ...
        draw_x = round(self.rect.x - offset_x)
        draw_y = round(self.rect.y)
        # Culling
        if draw_x + self.size[0] < 0 or draw_x > SCREEN_WIDTH: return

        draw_rect = pygame.Rect(draw_x, draw_y, self.size[0], self.size[1])

        if self.type == "coin":
             anim_phase = ((pygame.time.get_ticks() - self.spawn_time) // 80) % 4
             coin_color = COLOR_COIN; outline_color = COLOR_BLACK
             if anim_phase == 0: # Full ellipse
                 pygame.draw.ellipse(surface, coin_color, draw_rect)
                 pygame.draw.ellipse(surface, outline_color, draw_rect, 1)
             elif anim_phase == 1 or anim_phase == 3: # Thinner
                 thin_rect = draw_rect.inflate(-draw_rect.width * 0.6, 0); thin_rect.center = draw_rect.center
                 pygame.draw.ellipse(surface, coin_color, thin_rect)
             else: # Line
                 line_rect = draw_rect.inflate(-draw_rect.width * 0.85, 0); line_rect.center = draw_rect.center
                 pygame.draw.ellipse(surface, coin_color, line_rect)
        elif self.type == "mushroom":
             cap_rect = pygame.Rect(draw_rect.left, draw_rect.top, TILE, TILE * 0.625)
             pygame.draw.ellipse(surface, COLOR_MUSHROOM_RED, cap_rect)
             pygame.draw.rect(surface, COLOR_MUSHROOM_RED, (draw_rect.left, draw_rect.top + TILE*0.3125, TILE, TILE*0.3125))
             stem_rect = pygame.Rect(draw_rect.left + 3, draw_rect.top + TILE*0.5, TILE - 6, TILE*0.5)
             pygame.draw.rect(surface, COLOR_MUSHROOM_WHITE, stem_rect)
             pygame.draw.rect(surface, COLOR_BLACK, stem_rect, 1)
             eye_size = 3; eye_y = draw_rect.bottom - 6
             pygame.draw.rect(surface, COLOR_BLACK, (draw_rect.centerx - 4, eye_y, eye_size, eye_size))
             pygame.draw.rect(surface, COLOR_BLACK, (draw_rect.centerx + 1, eye_y, eye_size, eye_size))
             spot_color = COLOR_MUSHROOM_WHITE
             pygame.draw.circle(surface, spot_color, (draw_rect.centerx, draw_rect.top + 4), 3)
             pygame.draw.circle(surface, spot_color, (draw_rect.left + 4, draw_rect.top + 7), 2)
             pygame.draw.circle(surface, spot_color, (draw_rect.right - 4, draw_rect.top + 7), 2)
             pygame.draw.ellipse(surface, COLOR_BLACK, cap_rect, 1)


# --- Helper Function - THE MASSIVE LEVEL LAYOUT ---
def create_level():
    """Creates sprite groups based on VISUAL LAYOUT of SMB 1-1 image."""
    all_sprites_group = pygame.sprite.Group()
    platforms_group = pygame.sprite.Group()
    enemies_group = pygame.sprite.Group()
    items_group = pygame.sprite.Group() # Items added dynamically

    # Define ground level Y coordinate (top of the ground blocks)
    GROUND_Y = SCREEN_HEIGHT - TILE * 2

    # --- Create Ground Segments ---
    # Segment 1 (Start to first gap)
    platforms_group.add(Platform(0, GROUND_Y, TILE * 69, TILE * 2, type="ground"))
    # Segment 2 (After first gap)
    platforms_group.add(Platform(TILE * 71, GROUND_Y, TILE * 15, TILE * 2, type="ground"))
    # Segment 3 (After second gap)
    platforms_group.add(Platform(TILE * 89, GROUND_Y, TILE * 63, TILE * 2, type="ground")) # Extended ground
    # Segment 4 (Final stretch) - Needs exact length to castle
    platforms_group.add(Platform(TILE * 155, GROUND_Y, TILE * 50, TILE * 2, type="ground")) # Approx

    # --- Create Blocks (Bricks, Question Blocks) ---
    # Coordinates are (TileX * TILE, GROUND_Y - TileAboveGround * TILE)

    # Block Group 1
    platforms_group.add(Platform(TILE * 16, GROUND_Y - TILE * 4, TILE, TILE, type="question", text="coin"))
    platforms_group.add(Platform(TILE * 20, GROUND_Y - TILE * 4, TILE, TILE, type="brick", breakable=True))
    platforms_group.add(Platform(TILE * 21, GROUND_Y - TILE * 4, TILE, TILE, type="question", text="mushroom")) # Powerup
    platforms_group.add(Platform(TILE * 22, GROUND_Y - TILE * 4, TILE, TILE, type="brick", breakable=True))
    platforms_group.add(Platform(TILE * 23, GROUND_Y - TILE * 4, TILE, TILE, type="question", text="coin"))
    platforms_group.add(Platform(TILE * 22, GROUND_Y - TILE * 8, TILE, TILE, type="question", text="coin")) # High block

    # Block Group 2 (After first pipe)
    platforms_group.add(Platform(TILE * 37, GROUND_Y - TILE * 4, TILE*3, TILE, type="brick", breakable=True)) # 3 Bricks row

    # Block Group 3 (Near second pipe)
    platforms_group.add(Platform(TILE * 45, GROUND_Y - TILE * 4, TILE, TILE, type="brick", breakable=True))
    platforms_group.add(Platform(TILE * 46, GROUND_Y - TILE * 4, TILE, TILE, type="brick", text="coin", breakable=False)) # Hidden coin brick

    # Block Group 4 (Between pipes 2 and 3)
    platforms_group.add(Platform(TILE * 55, GROUND_Y - TILE * 4, TILE, TILE, type="brick", breakable=True))
    platforms_group.add(Platform(TILE * 56, GROUND_Y - TILE * 8, TILE, TILE, type="brick", breakable=True)) # High brick

    # Block Group 5 (Before first gap)
    platforms_group.add(Platform(TILE * 64, GROUND_Y - TILE * 4, TILE, TILE, type="question", text="coin"))
    platforms_group.add(Platform(TILE * 65, GROUND_Y - TILE * 4, TILE, TILE, type="question", text="coin"))

    # Block Group 6 (After first gap)
    platforms_group.add(Platform(TILE * 77, GROUND_Y - TILE * 4, TILE, TILE, type="question", text="mushroom")) # Powerup (or 1-UP?) Check image - it's a powerup
    platforms_group.add(Platform(TILE * 80, GROUND_Y - TILE * 4, TILE, TILE, type="brick", breakable=True))
    platforms_group.add(Platform(TILE * 81, GROUND_Y - TILE * 4, TILE, TILE, type="brick", breakable=True))
    platforms_group.add(Platform(TILE * 82, GROUND_Y - TILE * 4, TILE, TILE, type="brick", breakable=True))
    platforms_group.add(Platform(TILE * 80, GROUND_Y - TILE * 8, TILE, TILE, type="brick", breakable=True)) # High single brick

    # Block Group 7 (After second gap)
    platforms_group.add(Platform(TILE * 94, GROUND_Y - TILE * 4, TILE, TILE, type="brick", breakable=True))
    platforms_group.add(Platform(TILE * 95, GROUND_Y - TILE * 4, TILE, TILE, type="brick", breakable=True))
    platforms_group.add(Platform(TILE * 97, GROUND_Y - TILE * 4, TILE, TILE, type="brick", text="coin", breakable=False)) # Hidden coin brick? Check image - looks normal
    platforms_group.add(Platform(TILE * 97, GROUND_Y - TILE * 4, TILE, TILE, type="brick", breakable=True))

    # Block Group 8 (Before stairs)
    platforms_group.add(Platform(TILE * 109, GROUND_Y - TILE * 4, TILE, TILE, type="question", text="coin"))
    platforms_group.add(Platform(TILE * 112, GROUND_Y - TILE * 4, TILE, TILE, type="question", text="coin"))
    platforms_group.add(Platform(TILE * 115, GROUND_Y - TILE * 4, TILE, TILE, type="question", text="coin"))
    platforms_group.add(Platform(TILE * 112, GROUND_Y - TILE * 8, TILE, TILE, type="question", text="mushroom")) # High powerup

    # Block Group 9 (After small stairs, near end)
    platforms_group.add(Platform(TILE * 128, GROUND_Y - TILE * 4, TILE, TILE, type="brick", breakable=True))
    platforms_group.add(Platform(TILE * 129, GROUND_Y - TILE * 4, TILE, TILE, type="brick", breakable=True))
    platforms_group.add(Platform(TILE * 130, GROUND_Y - TILE * 4, TILE, TILE, type="question", text="coin"))
    platforms_group.add(Platform(TILE * 131, GROUND_Y - TILE * 4, TILE, TILE, type="brick", breakable=True))


    # --- Create Pipes ---
    # Coords: (TileX * TILE, GROUND_Y - PipeHeight * TILE, Width=TILE*2, Height=PipeHeight*TILE)
    platforms_group.add(Platform(TILE * 28, GROUND_Y - TILE * 2, TILE * 2, TILE * 2, type="pipe"))
    platforms_group.add(Platform(TILE * 38, GROUND_Y - TILE * 3, TILE * 2, TILE * 3, type="pipe"))
    platforms_group.add(Platform(TILE * 46, GROUND_Y - TILE * 4, TILE * 2, TILE * 4, type="pipe")) # Maybe hidden coin here? Let's skip warp for now
    platforms_group.add(Platform(TILE * 57, GROUND_Y - TILE * 4, TILE * 2, TILE * 4, type="pipe"))


    # --- Create Stairs ---
    # Small stair block near end
    for i in range(4):
        platforms_group.add(Platform(TILE * (134 + i), GROUND_Y - TILE * (i + 1), TILE, TILE * (i + 1), type="stair_block"))

    # Large final stairs
    for i in range(8): # 8 blocks high on the left side
        platforms_group.add(Platform(TILE * (140 + i), GROUND_Y - TILE * (i + 1), TILE, TILE * (i + 1), type="stair_block"))
    # Solid block at the top right of stairs
    platforms_group.add(Platform(TILE * 148, GROUND_Y - TILE * 8, TILE, TILE, type="stair_block"))


    # --- Create Enemies ---
    # Coords: (TileX * TILE, GROUND_Y)
    enemies_group.add(Goomba(TILE * 22, GROUND_Y))
    enemies_group.add(Goomba(TILE * 40, GROUND_Y))
    enemies_group.add(Goomba(TILE * 51, GROUND_Y))
    enemies_group.add(Goomba(TILE * 53, GROUND_Y))
    enemies_group.add(Goomba(TILE * 80, GROUND_Y)) # Pair Goombas after gap 1
    enemies_group.add(Goomba(TILE * 81 + 8, GROUND_Y))
    enemies_group.add(Goomba(TILE * 97, GROUND_Y)) # Pair Goombas after gap 2
    enemies_group.add(Goomba(TILE * 98 + 8, GROUND_Y))
    enemies_group.add(Goomba(TILE * 105, GROUND_Y))
    enemies_group.add(Goomba(TILE * 108, GROUND_Y))
    enemies_group.add(Goomba(TILE * 128, GROUND_Y)) # Pair near end stairs
    enemies_group.add(Goomba(TILE * 129 + 8, GROUND_Y))


    # --- Add platforms and enemies to the main drawing group ---
    all_sprites_group.add(platforms_group)
    all_sprites_group.add(enemies_group)

    # Store background elements separately for drawing order
    # List of tuples: (type, x, y, size) or (type, x, y)
    background_elements = []

    # --- Clouds --- (Approximate positions based on image)
    background_elements.append(('cloud', TILE * 8, GROUND_Y - TILE * 10, 1))
    background_elements.append(('cloud', TILE * 19, GROUND_Y - TILE * 11, 3))
    background_elements.append(('cloud', TILE * 35, GROUND_Y - TILE * 10, 2))
    background_elements.append(('cloud', TILE * 52, GROUND_Y - TILE * 11, 1))
    background_elements.append(('cloud', TILE * 67, GROUND_Y - TILE * 10, 3))
    background_elements.append(('cloud', TILE * 83, GROUND_Y - TILE * 11, 2))
    background_elements.append(('cloud', TILE * 100, GROUND_Y - TILE * 10, 1))
    background_elements.append(('cloud', TILE * 115, GROUND_Y - TILE * 11, 3))
    background_elements.append(('cloud', TILE * 131, GROUND_Y - TILE * 10, 2))
    background_elements.append(('cloud', TILE * 148, GROUND_Y - TILE * 11, 1))
    background_elements.append(('cloud', TILE * 163, GROUND_Y - TILE * 10, 3))
    background_elements.append(('cloud', TILE * 190, GROUND_Y - TILE * 11, 2)) # Extra clouds off screen right

    # --- Hills --- (Approximate positions)
    background_elements.append(('hill', 0, GROUND_Y, 2)) # Large hill start
    background_elements.append(('hill', TILE * 16, GROUND_Y, 1)) # Small hill
    background_elements.append(('hill', TILE * 32, GROUND_Y, 2)) # Large hill
    background_elements.append(('hill', TILE * 48, GROUND_Y, 1)) # Small hill
    background_elements.append(('hill', TILE * 64, GROUND_Y, 2)) # Large hill
    background_elements.append(('hill', TILE * 80, GROUND_Y, 1)) # Small hill
    background_elements.append(('hill', TILE * 96, GROUND_Y, 2)) # Large hill
    background_elements.append(('hill', TILE * 112, GROUND_Y, 1)) # Small hill
    background_elements.append(('hill', TILE * 128, GROUND_Y, 2)) # Large hill
    background_elements.append(('hill', TILE * 144, GROUND_Y, 1)) # Small hill
    background_elements.append(('hill', TILE * 160, GROUND_Y, 2)) # Large hill near end
    background_elements.append(('hill', TILE * 176, GROUND_Y, 1)) # Small hill near castle

    # --- Flagpole & Castle ---
    background_elements.append(('flagpole', TILE * 152, GROUND_Y))
    background_elements.append(('castle', TILE * 160, GROUND_Y))


    return all_sprites_group, platforms_group, enemies_group, items_group, background_elements


# --- Game Initialization ---
pygame.init()
# pygame.mixer.quit() # No sound needed / implemented
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("UltraSim Pygame Simulation - World 1-1 Layout Attempt")
clock = pygame.time.Clock()
try:
    font = pygame.font.Font(None, 24) # Use default font
except Exception as e:
    print(f"Warning: Could not load default font: {e}. HUD text may not display.")
    font = None

# --- Game Variables ---
running = True
camera_x = 0
score = 0
coins = 0
lives = 3
world_str = "1-1"
time_left = GAME_START_TIME
time_last_tick = pygame.time.get_ticks()

# --- Create Sprites and Level ---
all_sprites, platforms, enemies, items, background_data = create_level()

# Create player and position on top of a block for testing
player = Player()
player_start_x = TILE * 14  # Position on a question block
player_start_y = SCREEN_HEIGHT - TILE*4 - TILE*2 - 1  # On top of a question block (4 tiles up from ground)
player.rect.bottomleft = (player_start_x, player_start_y)
player.pos = pygame.Vector2(player.rect.centerx, player.rect.bottom)
all_sprites.add(player) # Add player to the main sprite group


# --- Main Game Loop ---
while running:
    # Delta Time for physics scaling
    delta_time = clock.tick(TARGET_FPS) / 1000.0
    # Avoid huge jumps in delta_time if debugging/lagging
    delta_time = min(delta_time, 0.05)

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                player.jump()
            if event.key == pygame.K_ESCAPE:
                 running = False
            # Debug keys
            if event.key == pygame.K_g: player.grow()
            if event.key == pygame.K_s: player.shrink()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                player.jump_cut()  # Cut jump height when button released

    # --- Updates ---
    # Update sprites with appropriate arguments for each type
    if not player.is_dead:
        player.update(platforms, delta_time)
    else:
        player.update(platforms, delta_time)  # Still call update for death animation
        
    # Update enemies and items with delta time
    for enemy in enemies:
        enemy.update(platforms, delta_time)
    
    for item in items:
        item.update(platforms, delta_time)
        
    # Update platforms without extra arguments
    platforms.update()

    # --- Camera Scrolling Logic ---
    # Target camera X to keep player roughly in the center-left
    target_camera_x = player.pos.x - SCREEN_WIDTH / 3
    # Clamp camera: cannot scroll left past 0, cannot scroll right past level end
    camera_x = max(0, min(target_camera_x, LEVEL_END_X - SCREEN_WIDTH))


    # --- Item Spawning from Hit Blocks ---
    spawned_items_this_frame = []
    for plat in platforms:
        if hasattr(plat, 'item_spawn_info') and plat.item_spawn_info:
            item_type, spawn_pos = plat.item_spawn_info
            new_item = Item(item_type, spawn_pos)
            spawned_items_this_frame.append(new_item)
            plat.item_spawn_info = None
    if spawned_items_this_frame:
         items.add(spawned_items_this_frame)
         all_sprites.add(spawned_items_this_frame)


    # --- Interactions ---
    # Item Collection
    item_hits = pygame.sprite.spritecollide(player, items, True)
    for item in item_hits:
        if item.type == "mushroom":
            if player.state == "small": player.grow()
            score += MUSHROOM_SCORE
            # TODO: Sound effect
        elif item.type == "coin":
             # Score already handled
             # TODO: Sound effect
             pass

    # Enemy Collision
    if not player.is_dead and player.invincible_timer == 0:
        enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
        for enemy in enemy_hits:
            # Check for stomp: Player falling, feet near/above enemy top
            is_stomp = player.vel.y > 0 and player.rect.bottom <= enemy.rect.centery + 5 # Generous stomp check

            if is_stomp and enemy.state == "walk":
                enemy.stomp()
                player.vel.y = STOMP_BOUNCE # Bounce
            elif enemy.state == "walk": # Player running into enemy
                if player.hit(): # Check if hit causes death
                     player.die() # Start death sequence
                     break # Stop checking enemies

    # --- Game State Checks ---
    # Player falling off screen
    if not player.is_dead and player.rect.top > SCREEN_HEIGHT:
         player.die()

    # Timer Decrement
    now = pygame.time.get_ticks()
    if not player.is_dead: # Stop timer ticking if player is dead
        time_tick_interval = 400 # ms per game 'second'
        while now - time_last_tick >= time_tick_interval:
            time_left -= 1
            time_last_tick += time_tick_interval
            if time_left < 0:
                time_left = 0
                player.die() # Time up
                break


    # --- Drawing ---
    # Fill background
    screen.fill(COLOR_SKY_BLUE)

    # Draw static background elements (relative to camera)
    ground_y_coord = SCREEN_HEIGHT - TILE * 2 # Reference for placing hills etc.
    for elem in background_data:
        elem_type = elem[0]
        x = elem[1]
        y = elem[2] # This is ground Y for hills/castle/flagpole
        if elem_type == 'cloud':
            size = elem[3]
            draw_cloud(screen, x, y, size, camera_x) # Y is absolute cloud level
        elif elem_type == 'hill':
            size = elem[3]
            draw_hill(screen, x, ground_y_coord, size, camera_x) # Y needs to be ground level
        elif elem_type == 'flagpole':
            draw_flagpole(screen, x, ground_y_coord, camera_x)
        elif elem_type == 'castle':
            draw_castle(screen, x, ground_y_coord, camera_x)


    # Draw all sprites (platforms, enemies, items, player)
    for entity in all_sprites:
         if hasattr(entity, 'draw_programmatic'):
             entity.draw_programmatic(screen, camera_x)


    # Draw HUD
    if font:
        score_surf = font.render(f"MARIO {score:06d}", True, COLOR_WHITE)
        coins_surf = font.render(f" C x{coins:02d}", True, COLOR_WHITE)
        world_surf = font.render(f"WORLD {world_str}", True, COLOR_WHITE)
        time_surf = font.render(f"TIME {max(0, time_left):03d}", True, COLOR_WHITE)
        hud_y = 10
        screen.blit(score_surf, (20, hud_y))
        screen.blit(coins_surf, (SCREEN_WIDTH * 0.35, hud_y))
        screen.blit(world_surf, (SCREEN_WIDTH * 0.60, hud_y))
        screen.blit(time_surf, (SCREEN_WIDTH * 0.85, hud_y))


    # --- Update Display ---
    pygame.display.flip()

# --- Quit Pygame ---
pygame.quit()
sys.exit()
