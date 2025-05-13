import pygame as pg
import sys

# Constants
TILE_SIZE = 32
SCREEN_WIDTH = 800 # <- Corrected this line
SCREEN_HEIGHT = 600
FPS = 60
BACKGROUND_COLOR = (0, 0, 0)
PLAYER_JUMP_POWER = 10
ENEMY_MOVE_SPEED = 2

color_map = {
    'W': (255, 255, 255),  # White
    'K': (0, 0, 0),        # Black
    'R': (255, 0, 0),      # Red
    'G': (0, 255, 0),      # Green
    'Y': (255, 255, 0),    # Yellow
    'L': (135, 206, 250),  # Light blue (sky)
    'O': (139, 69, 19)     # Brown (path)
}

# Stub classes for sprites
class Debris(pg.sprite.Sprite):
    def __init__(self, game, x, y, idx):
        super().__init__()
        self.image = pg.Surface((8, 8))
        self.image.fill((255, 0, 0)) # Red color for debris
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel = pg.math.Vector2(0,0) # Initialize velocity for debris
    def update(self, dt):
        # Placeholder for debris physics (e.g., gravity, lifespan)
        self.rect.x += self.vel.x * dt * TILE_SIZE # Apply horizontal velocity
        self.rect.y += self.vel.y * dt * TILE_SIZE # Apply vertical velocity
        self.vel.y += 0.5 * dt * TILE_SIZE # Simple gravity
        if self.rect.top > SCREEN_HEIGHT: # Remove if it falls off screen
            self.kill()


class GroundBlock(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color_map['O']) # Brown color for ground
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))

class BrickBlock(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((255, 165, 0)) # Orange color for bricks
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))

class QuestionBlock(pg.sprite.Sprite):
    def __init__(self, game, x, y, item_type):
        super().__init__()
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color_map['Y']) # Yellow color for question blocks
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))
        self.item_type = item_type # Stores the type of item it contains (e.g., SuperMushroom)
        self.hit = False # To track if the block has been hit

class Goomba(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((165, 42, 42)) # Brownish-red for Goomba
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))
        self.state = "walk" # Possible states: "walk", "squished"
        self.vel = pg.math.Vector2(-ENEMY_MOVE_SPEED, 0) # Goombas usually move left initially
        self.animation_speed = 0 # Placeholder for animation speed
        self.current_frame_index = 0 # Placeholder for animation frame
        self.squish_timer = 0 # Timer for how long the squished state lasts
        self.on_ground = False # For gravity

    def update(self, dt, platforms):
        # Basic Goomba movement and squish logic
        if self.state == "walk":
            self.rect.x += self.vel.x * dt # Adjusted speed scaling
            # Basic collision with platforms to turn around (simplified)
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.vel.x < 0 and self.rect.left <= platform.rect.right: # Moving left, hit right side of platform
                        self.rect.left = platform.rect.right
                        self.vel.x *= -1
                    elif self.vel.x > 0 and self.rect.right >= platform.rect.left: # Moving right, hit left side of platform
                        self.rect.right = platform.rect.left
                        self.vel.x *= -1
                    break # Stop checking after one collision
        elif self.state == "squished":
            self.squish_timer -= dt * FPS # Decrease timer
            if self.squish_timer <= 0:
                self.kill() # Remove Goomba after timer expires

        # Apply gravity
        if not self.on_ground:
            self.vel.y += 0.8 * dt * TILE_SIZE # Gravity
        else:
            self.vel.y = 0

        self.rect.y += self.vel.y * dt # Apply vertical movement

        # Check for ground collision
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel.y > 0 and self.rect.bottom >= platform.rect.top and self.rect.top < platform.rect.top : # Landing on top
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.vel.y = 0
                # (No need to check for hitting underside for basic Goomba)


class KoopaTroopa(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((0, 128, 0)) # Green for Koopa
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))
        self.state = "walk" # Possible states: "walk", "shell", "sliding"
        self.vel = pg.math.Vector2(-ENEMY_MOVE_SPEED, 0) # Koopas also move left initially
        self.on_ground = False # For gravity

    def stomped(self):
        # Logic when Koopa is stomped
        if self.state == "walk":
            self.state = "shell"
            self.vel.x = 0
            # Potentially change image to shell form here
            self.image.fill((0,80,0)) # Darker green for shell
        elif self.state == "shell": # If already a shell and stomped again, it might start sliding
            # This part can be handled by player collision logic (kicking the shell)
            pass

    def update(self, dt, platforms):
        # Basic Koopa movement and shell logic
        if self.state == "walk" or self.state == "sliding":
            self.rect.x += self.vel.x * dt # Adjusted speed scaling
            # Basic collision with platforms to turn around (simplified)
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.vel.x < 0 and self.rect.left <= platform.rect.right:
                        self.rect.left = platform.rect.right
                        self.vel.x *= -1
                    elif self.vel.x > 0 and self.rect.right >= platform.rect.left:
                        self.rect.right = platform.rect.left
                        self.vel.x *= -1
                    # If sliding shell hits a wall, it should also kill other enemies
                    if self.state == "sliding":
                        # Add logic here to check collision with other enemies
                        pass
                    break
        
        # Apply gravity
        if not self.on_ground:
            self.vel.y += 0.8 * dt * TILE_SIZE # Gravity
        else:
            self.vel.y = 0
        
        self.rect.y += self.vel.y * dt # Apply vertical movement

        # Check for ground collision
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel.y > 0 and self.rect.bottom >= platform.rect.top and self.rect.top < platform.rect.top: # Landing on top
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.vel.y = 0


class Flagpole(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.image = pg.Surface((16, TILE_SIZE * 5)) # Made flagpole taller
        self.image.fill(color_map['G']) # Green for flagpole
        self.rect = self.image.get_rect(bottomleft=(x * TILE_SIZE, (y + 1) * TILE_SIZE)) # Align bottom

class PipeSection(pg.sprite.Sprite):
    def __init__(self, game, x, y, section_type):
        super().__init__()
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color_map['G']) # Green for pipes
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))
        self.section_type = section_type # e.g., "top_left", "top_right", "body_left", "body_right"
        # Could add specific drawing for different pipe sections if needed

class Block(pg.sprite.Sprite): # Generic block, can be used for Castle or Spikes
    def __init__(self, game, x, y, pattern, solid, block_type):
        super().__init__()
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        # Determine color based on block_type
        if block_type == "castle":
            self.image.fill(color_map['O']) # Brown for castle blocks
        elif block_type == "spike":
            self.image.fill(color_map['K']) # Black for spikes (or a grey)
            # Could draw a spike pattern here
        else:
            self.image.fill(color_map['W']) # Default to white
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))
        self.solid = solid
        self.block_type = block_type

class SuperMushroom(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color_map['R']) # Red for mushroom
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))
        self.vel = pg.math.Vector2(ENEMY_MOVE_SPEED / 2, 0) # Mushrooms often move slowly
        self.on_ground = False

    def update(self, dt, platforms):
        # Basic item movement (gravity, platform collision)
        if not self.on_ground:
            self.vel.y += 0.8 * dt * TILE_SIZE # Basic gravity, scaled by dt and TILE_SIZE for consistency
        else:
            self.vel.y = 0

        self.rect.x += self.vel.x * dt * TILE_SIZE # Scale horizontal movement
        self.rect.y += self.vel.y * dt # Vertical movement already scaled by TILE_SIZE in gravity

        self.on_ground = False # Reset before checking collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Horizontal collision
                if self.vel.x > 0 and self.rect.right >= platform.rect.left and self.rect.left < platform.rect.left: # Moving right
                    self.rect.right = platform.rect.left
                    self.vel.x *= -1
                elif self.vel.x < 0 and self.rect.left <= platform.rect.right and self.rect.right > platform.rect.right: # Moving left
                    self.rect.left = platform.rect.right
                    self.vel.x *= -1

                # Vertical collision
                if self.vel.y > 0 and self.rect.bottom >= platform.rect.top and self.rect.top < platform.rect.top : # Falling
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.vel.y = 0
                elif self.vel.y < 0 and self.rect.top <= platform.rect.bottom and self.rect.bottom > platform.rect.bottom: # Hitting underside
                    self.rect.top = platform.rect.bottom
                    self.vel.y = 0 # Stop upward movement


class SuperLeaf(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((255, 165, 0)) # Orange/Brown for leaf
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))
        self.vel = pg.math.Vector2(0, 0.5) # Leaf might float down slowly
        self.amplitude = TILE_SIZE / 4
        self.frequency = 0.005 # Adjusted frequency for smoother sway
        self.initial_x_pixels = x * TILE_SIZE
        self.time_offset = pg.time.get_ticks() # Offset time for unique sway per leaf

    def update(self, dt, platforms):
        # Leaf floating behavior
        self.rect.y += self.vel.y * dt * TILE_SIZE # Scale vertical movement
        # Swaying motion
        self.rect.x = self.initial_x_pixels + self.amplitude * pg.math.sin(self.frequency * (pg.time.get_ticks() - self.time_offset))

        # Basic collision with platforms (stop falling)
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel.y > 0:
                if self.rect.bottom >= platform.rect.top and self.rect.top < platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.vel.y = 0 # Stop falling
                    break


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game # Reference to the game instance
        self.image_small_orig = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image_small_orig.fill(color_map['R']) # Red for small Mario
        self.image_super_orig = pg.Surface((TILE_SIZE, TILE_SIZE * 2)) # Super Mario is taller
        self.image_super_orig.fill(color_map['R'])
        pg.draw.rect(self.image_super_orig, (0,0,255), (0,0,TILE_SIZE, TILE_SIZE)) # Blue overalls for Super
        self.image_raccoon_orig = pg.Surface((TILE_SIZE, TILE_SIZE * 2)) # Raccoon Mario
        self.image_raccoon_orig.fill((160, 82, 45)) # Brown for Raccoon
        # Add ears/tail to raccoon image if desired

        self.image = self.image_small_orig.copy() # Initial image
        self.rect = self.image.get_rect(bottomleft=(x * TILE_SIZE, (y + 1) * TILE_SIZE))
        self.vel = pg.math.Vector2(0, 0)
        self.lives = 3
        self.score = 0
        self.form = "small" # "small", "super", "raccoon"
        self.facing_left = False
        self.on_ground = False
        self.invincible_timer = 0 # In frames
        self.is_raccoon_form = False # Redundant with self.form, but kept for compatibility
        self.p_meter = 0 # For raccoon flight, 0-7
        self.jump_power = PLAYER_JUMP_POWER
        self.gravity = 0.8
        self.max_fall_speed = 15
        self.walk_speed = 5
        self.run_speed = 8
        self.current_speed = self.walk_speed
        self.is_jumping = False
        self.is_flying = False
        self.flight_timer = 0
        self.max_flight_time = 2 * FPS # 2 seconds of flight

    def set_form(self, form_type): # Renamed parameter to avoid conflict
        old_bottom = self.rect.bottom
        old_centerx = self.rect.centerx # Keep player centered when changing form

        if form_type == "super" and self.form == "small":
            self.form = "super"
            self.image = self.image_super_orig.copy()
            self.is_raccoon_form = False
        elif form_type == "raccoon" and (self.form == "small" or self.form == "super"):
            self.form = "raccoon"
            self.image = self.image_raccoon_orig.copy()
            self.is_raccoon_form = True # Keep this for logic if needed
        elif form_type == "small": # Downgrade
            self.form = "small"
            self.image = self.image_small_orig.copy()
            self.is_raccoon_form = False
        else: # No change if current form is already the target or invalid transition
            return

        self.rect = self.image.get_rect()
        self.rect.bottom = old_bottom
        self.rect.centerx = old_centerx # Re-center
        self.game.player.invincible_timer = (1 if form_type != "small" else 2) * FPS # Brief invincibility

    def die(self):
        if self.invincible_timer > 0:
            return # Can't die if invincible

        if self.form == "raccoon" or self.form == "super":
            self.set_form("small")
            # Add sound/animation for losing power-up
        else:
            self.lives -= 1
            # Add sound/animation for dying
            if self.lives > 0:
                self.game.reset_level_soft()
            else:
                self.game.game_state = "game_over_screen" # Changed from self.game.game_over = True
                # Add sound/animation for game over

    def update(self, dt, platforms):
        keys = pg.key.get_pressed()
        self.current_speed = self.run_speed if keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT] else self.walk_speed

        # Horizontal movement
        if keys[pg.K_LEFT]:
            self.vel.x = -self.current_speed
            self.facing_left = True
        elif keys[pg.K_RIGHT]:
            self.vel.x = self.current_speed
            self.facing_left = False
        else:
            self.vel.x = 0

        # P-Meter for Raccoon
        if self.form == "raccoon": # Check form directly
            if abs(self.vel.x) > 0 and self.on_ground:
                self.p_meter = min(7, self.p_meter + dt * 5) # Fill P-meter faster
            elif self.on_ground:
                self.p_meter = max(0, self.p_meter - dt * 2) # Decrease slowly on ground if not moving
            if self.is_flying:
                self.p_meter = max(0, self.p_meter - dt * 3) # Decrease while flying
                if self.p_meter == 0:
                    self.is_flying = False


        # Jumping and Flying
        if keys[pg.K_SPACE] or keys[pg.K_UP]:
            if self.on_ground:
                self.is_jumping = True
                self.on_ground = False
                self.vel.y = -self.jump_power
                if self.form == "raccoon" and self.p_meter >= 7: # Full P-Meter allows flight takeoff
                    self.is_flying = True
                    self.flight_timer = self.max_flight_time
            elif self.form == "raccoon" and not self.is_flying and self.vel.y > 0: # Tail whip for slow descent
                self.vel.y = min(self.vel.y, 2) # Slow fall speed
            elif self.form == "raccoon" and self.is_flying and self.flight_timer > 0: # Continue flying
                self.vel.y = -self.jump_power / 3 # Reduced upward thrust while flying (less than jump)
                self.flight_timer -= 1 # Decrement by 1 per frame if dt is not used here
        else: # Jump key not pressed
            if self.is_jumping and self.vel.y < -self.jump_power / 3:
                # Short hop if jump key released early
                self.vel.y = -self.jump_power / 3
            if self.is_flying and self.form == "raccoon": # If flying and space released, stop ascending but can still glide
                 self.vel.y = min(self.vel.y + self.gravity * dt, 1) # Gentle descent or slow fall

        if not self.on_ground:
            if not (self.is_flying and (keys[pg.K_SPACE] or keys[pg.K_UP])): # Apply gravity if not actively flying up
                 self.vel.y += self.gravity * dt # Apply gravity scaled by dt
            self.vel.y = min(self.vel.y, self.max_fall_speed) # Terminal velocity
            if self.is_flying and self.flight_timer <=0: # Stop flying if timer runs out
                self.is_flying = False

        # Apply movement (scaled by dt for frame rate independence)
        # Note: TILE_SIZE scaling for velocity is unusual. Velocities are usually pixels/second or pixels/frame.
        # If vel.x/y are speeds in "tiles per second", then multiply by dt.
        # If vel.x/y are speeds in "pixels per second", then multiply by dt.
        # If vel.x/y are speeds in "pixels per frame", then DON'T multiply by dt (dt is already 1/FPS).
        # Assuming speeds are pixels/second for player, and dt is fraction of a second.
        self.rect.x += self.vel.x * dt * TILE_SIZE # Corrected: Player speed is often in abstract units, scaled to pixels
        self.check_collisions_x(platforms)
        self.rect.y += self.vel.y * dt * TILE_SIZE # Corrected: Player speed is often in abstract units, scaled to pixels
        self.on_ground = False # Assume not on ground until collision check
        self.check_collisions_y(platforms)

        # Invincibility timer
        if self.invincible_timer > 0:
            self.invincible_timer -= 1 # Assuming called 60 times per second (FPS)
            # Blinking animation for invincibility
            if self.invincible_timer % 10 < 5 : # Blink every 10 frames
                self.image.set_alpha(100) # Semi-Transparent
            else:
                self.image.set_alpha(255) # Opaque
        else:
            self.image.set_alpha(255)


    def check_collisions_x(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel.x > 0: # Moving right
                    self.rect.right = platform.rect.left
                elif self.vel.x < 0: # Moving left
                    self.rect.left = platform.rect.right
                self.vel.x = 0 # Stop horizontal movement on collision

    def check_collisions_y(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel.y > 0: # Moving down
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.is_jumping = False
                    self.is_flying = False # Land if flying and hit ground
                    self.vel.y = 0
                elif self.vel.y < 0: # Moving up (hitting head)
                    self.rect.top = platform.rect.bottom
                    self.vel.y = 0
                    # Check if hit a question block or brick block
                    if isinstance(platform, QuestionBlock) and not platform.hit:
                        self.game.spawn_item(platform)
                        platform.hit = True # Mark as hit, change appearance
                        platform.image.fill((100,100,100)) # Example: Greyed out
                    elif isinstance(platform, BrickBlock):
                        if self.form == "small":
                            # Brick doesn't break, maybe a bump sound
                            pass
                        else: # Super or Raccoon Mario can break bricks
                            self.game.add_debris(platform.rect.x, platform.rect.top)
                            platform.kill() # Remove the brick
                            self.game.player.score += 50


class Camera:
    def __init__(self, world_width_tiles, world_height_tiles): # Changed to tiles
        self.world_width_pixels = world_width_tiles * TILE_SIZE
        self.world_height_pixels = world_height_tiles * TILE_SIZE
        self.offset = pg.math.Vector2(0, 0)
        self.rect = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

    def update(self, player):
        # Camera follows player, centered, but doesn't go beyond world edges
        target_x = player.rect.centerx - SCREEN_WIDTH // 2
        target_y = player.rect.centery - SCREEN_HEIGHT // 2 # Basic vertical follow

        self.offset.x = max(0, min(target_x, self.world_width_pixels - SCREEN_WIDTH))
        # For now, keep Y offset fixed or simple. Real SMB3 has more complex Y scrolling.
        # self.offset.y = max(0, min(target_y, self.world_height_pixels - SCREEN_HEIGHT))
        # A common approach for Y is to only scroll up if player is above a certain threshold,
        # and always scroll down if player is below screen.
        # For simplicity, let's keep Y fixed unless level is smaller than screen.
        if self.world_height_pixels > SCREEN_HEIGHT:
             # Adjust y offset to keep player roughly in the lower half of the screen, but don't go below world_start (0)
             # or above world_end - screen_height
            player_y_target_on_screen = SCREEN_HEIGHT * 0.6
            desired_offset_y = player.rect.centery - player_y_target_on_screen
            self.offset.y = max(0, min(desired_offset_y, self.world_height_pixels - SCREEN_HEIGHT))
        else:
            self.offset.y = 0 # Level is smaller than screen height, so no vertical scroll.


        self.rect.topleft = self.offset

    def get_world_view_rect(self): # Renamed for clarity
        return self.rect

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Platformer Engine") # Window title
        self.clock = pg.time.Clock()
        try:
            self.font = pg.font.Font(None, 36) # Default font
            self.hud_font = pg.font.Font(None, 48) # Larger font for HUD
        except pg.error as e:
            print(f"Font loading error: {e}. Using default system font.")
            self.font = pg.font.SysFont(None, 36)
            self.hud_font = pg.font.SysFont(None, 48)

        self.debug_mode = False
        self.game_state = "overworld" # "overworld", "level", "game_over_screen", "level_complete_screen"
        self.player = Player(self, 0, 0) # Initialize player early for overworld HUD
        self.current_level_char = '1' # Start at level '1' node
        self.mario_overworld_pos = (2, 0) # Default starting (col, row) on overworld for node '1'
        self.level_complete = False # Tracks if current level is complete

        self.overworld_cell_size = 64 # Pixels for each cell in overworld grid
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group() # Solid blocks, pipes
        self.enemies = pg.sprite.Group()
        self.items = pg.sprite.Group() # Mushrooms, leaves
        self.flagpoles = pg.sprite.Group()
        self.debris = pg.sprite.Group() # Broken brick pieces

        # Sample level data (expanded)
        self.levels = {
            '1': [
                "L                                                               F ",
                "L                                                               F ",
                "L                                                               F ",
                "L                                                               F ",
                "L           QQQ                                                 F ",
                "L                                                               F ",
                "L                                                               F ",
                "L       B                                                       F ",
                "L     BBB                                                       F ",
                "L   BBBBB                                                       F ",
                "L               E   K                                           F ",
                "L   P        BBBBBBBBBBBBBBBB                                   F ",
                "L   p                                                           F ",
                "L   p                                                           F ",
                "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
                "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
            ],
            '2': [
                "L                                           F",
                "L                                           F",
                "L                                           F",
                "L   BBBB                                    F",
                "L  B    B     Q                             F",
                "L B      B        K                         F",
                "L B        B   BBBBBBBB                     F",
                "L                                           F",
                "L     E E E                                 F",
                "L   BBBBBBBBBB                              F",
                "L                 P                         F",
                "L                 p                         F",
                "L                 p                         F",
                "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
                "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
            ]
        }
        # Sample overworld data
        self.overworld_data = [ # (col, row)
            "  1--C", # C for Castle (end node, not a level)
            "  |   ",
            "  2   "
        ]
        self.overworld_nodes = {'1': (2, 0), '2': (2, 2), 'C':(5,0)} # (col, row) in overworld_data
        self.overworld_paths = { # Allowed movements between nodes
            '1': ['2', 'C'],
            '2': ['1']
            # 'C' is an endpoint, no paths from it in this simple setup
        }
        self.camera = None # Will be initialized in load_level
        self.reset_game_hard() # Initialize player stats and load first level for overworld

    def spawn_item(self, question_block):
        """Spawns an item from a question block."""
        item_class_to_spawn = question_block.item_type
        if item_class_to_spawn:
            # Spawn slightly above the block
            item = item_class_to_spawn(self, question_block.rect.x / TILE_SIZE, (question_block.rect.y / TILE_SIZE) -1)
            self.all_sprites.add(item)
            self.items.add(item)
            # Item might have an initial emerging animation/movement
            if hasattr(item, 'vel'): # Give it a little pop-up
                item.vel.y = -2 # Adjust as needed

    def add_debris(self, x_px, y_px):
        """Add debris particles when a brick is broken. x_px, y_px are top-left of the broken brick."""
        for i in range(4):  # 4 corner pieces
            debris_piece = Debris(self, x_px + (i % 2) * (TILE_SIZE // 2),
                                  y_px + (i // 2) * (TILE_SIZE // 2) - (TILE_SIZE //2), i) # Start above
            # Give debris some velocity (e.g., upward and outward)
            debris_piece.vel = pg.math.Vector2( (i % 2 - 0.5) * 3, -4 - (i // 2) * 1.5) # Example velocity
            self.all_sprites.add(debris_piece)
            self.debris.add(debris_piece)


    def load_level(self, level_data_str_array):
        # Clear previous level sprites
        self.all_sprites.empty()
        self.platforms.empty()
        self.enemies.empty()
        self.items.empty()
        self.flagpoles.empty()
        self.debris.empty()

        player_start_pos_tiles = (2, len(level_data_str_array) - 3) # Default player start (col, row from top)

        # Parse level data
        for row_idx, row_str in enumerate(level_data_str_array):
            for col_idx, char_code in enumerate(row_str):
                x_tile, y_tile = col_idx, row_idx
                if char_code == 'G':  # Ground
                    block = GroundBlock(self, x_tile, y_tile)
                    self.all_sprites.add(block)
                    self.platforms.add(block)
                elif char_code == 'B':  # Brick
                    block = BrickBlock(self, x_tile, y_tile)
                    self.all_sprites.add(block)
                    self.platforms.add(block) # Bricks are platforms
                elif char_code == 'Q':  # Question Block with Mushroom (default)
                    # Determine item based on player state (e.g., if small, mushroom, if super, leaf)
                    item_to_spawn = SuperMushroom
                    if self.player and self.player.form == "super":
                         item_to_spawn = SuperLeaf
                    block = QuestionBlock(self, x_tile, y_tile, item_to_spawn)
                    self.all_sprites.add(block)
                    self.platforms.add(block)
                # 'L' in the original level data was for Light Blue Sky, not a Question Block with Leaf.
                # If 'L' is intended to be a Leaf block, it should be distinct from sky.
                # Assuming 'L' in level data is sky and should be ignored for object placement.
                # If you want a specific leaf block, use a different char e.g. 'X'
                # For now, 'L' in level data does nothing here.
                elif char_code == 'E':  # Goomba
                    enemy = Goomba(self, x_tile, y_tile)
                    self.all_sprites.add(enemy)
                    self.enemies.add(enemy)
                elif char_code == 'K':  # Koopa Troopa
                    enemy = KoopaTroopa(self, x_tile, y_tile)
                    self.all_sprites.add(enemy)
                    self.enemies.add(enemy)
                elif char_code == 'F':  # Flagpole
                    flagpole = Flagpole(self, x_tile, y_tile)
                    self.all_sprites.add(flagpole)
                    self.flagpoles.add(flagpole) # Add to specific group for collision
                    # Flagpole base can be a platform, but its rect is thin.
                    # Consider adding a small invisible block at its base if needed for solid standing.
                    # For now, the Flagpole sprite itself is added to platforms.
                    self.platforms.add(flagpole)
                elif char_code == 'P':  # Pipe Top Left
                    # Create the top-left and top-right parts of the pipe head
                    pipe_tl = PipeSection(self, x_tile, y_tile, "top_left")
                    pipe_tr = PipeSection(self, x_tile + 1, y_tile, "top_right")
                    self.all_sprites.add(pipe_tl, pipe_tr)
                    self.platforms.add(pipe_tl, pipe_tr)

                    # Add body sections below if 'p' is present
                    current_pipe_y = y_tile + 1
                    while (current_pipe_y < len(level_data_str_array) and
                           col_idx < len(level_data_str_array[current_pipe_y]) and
                           level_data_str_array[current_pipe_y][col_idx].lower() == 'p'): # Check for 'p'
                        pipe_bl = PipeSection(self, x_tile, current_pipe_y, "body_left")
                        pipe_br = PipeSection(self, x_tile + 1, current_pipe_y, "body_right")
                        self.all_sprites.add(pipe_bl, pipe_br)
                        self.platforms.add(pipe_bl, pipe_br)
                        current_pipe_y +=1
                # 'p' (lowercase) is handled by the 'P' block implicitly, skip explicit 'p' processing
                elif char_code == 'p':
                    pass # Already handled by 'P'
                elif char_code == 'C':  # Castle block (as per level data, not overworld 'C')
                    castle_block = Block(self, x_tile, y_tile, None, True, "castle")
                    self.all_sprites.add(castle_block)
                    self.platforms.add(castle_block)
                elif char_code == '^':  # Spikes
                    spike = Block(self, x_tile, y_tile, None, False, "spike") # Spikes are not solid for movement over
                    self.all_sprites.add(spike)
                    # Add to a separate group for damage collision if needed, not platforms.
                    # self.damaging_terrain.add(spike)

        # Preserve player stats if player exists (e.g., from overworld to level)
        prev_lives = self.player.lives if self.player else 3
        prev_score = self.player.score if self.player else 0
        prev_form = self.player.form if self.player else "small"

        # Create and add player
        self.player = Player(self, player_start_pos_tiles[0], player_start_pos_tiles[1])
        self.player.lives = prev_lives
        self.player.score = prev_score
        if prev_form != "small":
            self.player.set_form(prev_form) # This will set image and rect correctly

        self.all_sprites.add(self.player)

        # Initialize camera for the loaded level
        level_width_tiles = len(level_data_str_array[0])
        level_height_tiles = len(level_data_str_array)
        self.camera = Camera(level_width_tiles, level_height_tiles)


    def enter_level(self, level_char_id):
        """Enter a specific level by ID from the overworld."""
        if level_char_id in self.levels:
            self.current_level_char = level_char_id

            current_score = self.player.score
            current_lives = self.player.lives
            current_form = self.player.form

            self.load_level(self.levels[level_char_id]) # This creates a new player instance

            self.player.score = current_score
            self.player.lives = current_lives
            if current_form != "small":
                self.player.set_form(current_form)

            self.game_state = "level"
            self.level_complete = False # Ensure this is reset
        else:
            print(f"Warning: Level '{level_char_id}' not found in self.levels.")
            self.game_state = "overworld" # Go back to overworld if level doesn't exist


    def complete_level(self):
        """Handle level completion logic."""
        if not self.level_complete: # Ensure this runs only once
            self.level_complete = True
            self.player.score += 1000 # Bonus for completing level
            print(f"Level {self.current_level_char} Complete! Score: {self.player.score}")
            pg.time.set_timer(pg.USEREVENT + 1, 3000) # Timer to switch to overworld (3 seconds)
            self.game_state = "level_complete_screen" # Show a completion message

    def reset_level_soft(self):
        """Called when player dies but has lives remaining. Resets current level."""
        print(f"Player died. Lives remaining: {self.player.lives}. Resetting level {self.current_level_char}.")
        current_score = self.player.score
        current_lives = self.player.lives # Already decremented by player.die()

        self.load_level(self.levels[self.current_level_char]) # Reload the current level

        self.player.score = current_score
        self.player.lives = current_lives
        self.player.set_form("small") # Player always starts small after dying in a level

        if self.player.lives <= 0: # Should be handled by player.die() setting game_state
            self.game_state = "game_over_screen"
        else:
            self.game_state = "level" # Back to playing the level


    def reset_game_hard(self):
        """Called on Game Over and choosing to restart, or initial game start."""
        print("Hard reset: Resetting game to initial state.")
        level_to_start_char = '1'

        if not hasattr(self, 'player') or self.player is None: # Ensure player exists
            self.player = Player(self, 0, 0) # Temp position

        self.player.score = 0
        self.player.lives = 3
        self.player.set_form("small")

        if level_to_start_char in self.overworld_nodes:
            self.mario_overworld_pos = self.overworld_nodes[level_to_start_char]
            self.current_level_char = level_to_start_char # Set current level focus for overworld
        else:
            self.mario_overworld_pos = (0,0)
            print(f"Warning: Default start node '{level_to_start_char}' not in overworld_nodes.")

        self.game_state = "overworld"
        self.level_complete = False


    def draw_overworld(self):
        """Draw the overworld map with paths and level nodes."""
        self.screen.fill(color_map['L'])  # Light blue sky background
        ow_tile_size = self.overworld_cell_size

        if self.debug_mode:
            for r_idx in range(len(self.overworld_data)):
                for c_idx in range(len(self.overworld_data[0])):
                    rect = pg.Rect(c_idx * ow_tile_size, r_idx * ow_tile_size, ow_tile_size, ow_tile_size)
                    pg.draw.rect(self.screen, (200, 200, 200), rect, 1) # Light grey grid lines

        for row_idx, row_str in enumerate(self.overworld_data):
            for col_idx, char_code in enumerate(row_str):
                x_center = col_idx * ow_tile_size + ow_tile_size // 2
                y_center = row_idx * ow_tile_size + ow_tile_size // 2

                if char_code == '-': # Horizontal path
                    pg.draw.line(self.screen, color_map['O'],
                                 (col_idx * ow_tile_size, y_center),
                                 ((col_idx + 1) * ow_tile_size, y_center), 4)
                elif char_code == '|': # Vertical path
                    pg.draw.line(self.screen, color_map['O'],
                                 (x_center, row_idx * ow_tile_size),
                                 (x_center, (row_idx + 1) * ow_tile_size), 4)
                elif char_code.isalnum(): # Node
                    is_completed = False # Add logic for completed levels if needed
                    node_color = color_map['G'] if is_completed else color_map['Y']
                    if char_code == 'C': node_color = (128,128,128) # Grey for castle

                    pg.draw.circle(self.screen, node_color, (x_center, y_center), ow_tile_size // 3)
                    text_surf = self.font.render(char_code, True, color_map['K'])
                    text_rect = text_surf.get_rect(center=(x_center, y_center))
                    self.screen.blit(text_surf, text_rect)

        mario_marker_col, mario_marker_row = self.mario_overworld_pos
        marker_x_px = mario_marker_col * ow_tile_size + ow_tile_size // 2
        marker_y_px = mario_marker_row * ow_tile_size + ow_tile_size // 2
        pg.draw.circle(self.screen, color_map['R'], (marker_x_px, marker_y_px), ow_tile_size // 4)

        if self.player:
            self.draw_text_hud(f"MARIO x{self.player.lives}", 20, 20)
            self.draw_text_hud(f"SCORE: {self.player.score}", SCREEN_WIDTH - 250, 20)


    def draw_text(self, text_str, x, y, color_char_code='W', font_to_use=None):
        """Draw general game text on the screen with the specified color and font."""
        if font_to_use is None:
            font_to_use = self.font # Default to the smaller game font
        try:
            # Corrected line:
            text_surface = font_to_use.render(text_str, True, color_map.get(color_char_code, color_map['W']))
            text_rect = text_surface.get_rect(topleft=(x,y))
            self.screen.blit(text_surface, text_rect)
        except pg.error as e:
            print(f"Error rendering text '{text_str}': {e}")
        except Exception as e: # Catch other potential errors
            print(f"An unexpected error occurred in draw_text: {e}")

    def draw_text_hud(self, text_str, x, y, color_char_code='W'):
        """Draw HUD text using the dedicated HUD font."""
        self.draw_text(text_str, x, y, color_char_code, self.hud_font)


    def draw_game_over_screen(self):
        self.screen.fill(color_map['K']) # Black background
        self.draw_text_hud("GAME OVER", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 3, 'R')
        self.draw_text("Press R to Restart", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 'W')
        self.draw_text("Press Q to Quit", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 'W')

    def draw_level_complete_screen(self):
        self.screen.fill(color_map['L']) # Sky blue background
        self.draw_text_hud(f"LEVEL {self.current_level_char} COMPLETE!", SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 3, 'G')
        if self.player:
             self.draw_text_hud(f"SCORE: {self.player.score}", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 'W')
        # Message about returning to overworld is implicit due to timer

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0 # Delta time in seconds

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_d: # Toggle debug mode
                        self.debug_mode = not self.debug_mode
                        print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")

                    if self.game_state == "overworld":
                        new_pos = list(self.mario_overworld_pos)
                        current_node_char = None
                        # Find which node Mario is on
                        for char, pos in self.overworld_nodes.items():
                            if pos == tuple(self.mario_overworld_pos):
                                current_node_char = char
                                break

                        if current_node_char:
                            if event.key == pg.K_UP:
                                # Try to find a node directly above
                                target_pos = (new_pos[0], new_pos[1]-1)
                                for node_char, node_pos_tuple in self.overworld_nodes.items():
                                    if node_pos_tuple == target_pos and node_char in self.overworld_paths.get(current_node_char, []):
                                        self.mario_overworld_pos = target_pos
                                        self.current_level_char = node_char # Update focus
                                        break
                            elif event.key == pg.K_DOWN:
                                target_pos = (new_pos[0], new_pos[1]+1)
                                for node_char, node_pos_tuple in self.overworld_nodes.items():
                                    if node_pos_tuple == target_pos and node_char in self.overworld_paths.get(current_node_char, []):
                                        self.mario_overworld_pos = target_pos
                                        self.current_level_char = node_char
                                        break
                            elif event.key == pg.K_LEFT:
                                target_pos = (new_pos[0]-1, new_pos[1])
                                for node_char, node_pos_tuple in self.overworld_nodes.items():
                                    if node_pos_tuple == target_pos and node_char in self.overworld_paths.get(current_node_char, []):
                                        self.mario_overworld_pos = target_pos
                                        self.current_level_char = node_char
                                        break
                            elif event.key == pg.K_RIGHT:
                                target_pos = (new_pos[0]+1, new_pos[1])
                                for node_char, node_pos_tuple in self.overworld_nodes.items():
                                    if node_pos_tuple == target_pos and node_char in self.overworld_paths.get(current_node_char, []):
                                        self.mario_overworld_pos = target_pos
                                        self.current_level_char = node_char
                                        break
                            elif event.key == pg.K_RETURN or event.key == pg.K_SPACE:
                                if current_node_char and current_node_char != 'C': # 'C' is castle, not a playable level
                                    self.enter_level(current_node_char)
                                elif current_node_char == 'C':
                                    print("Reached the Castle! Game End (not implemented).")
                                    # Potentially trigger a win screen or end sequence
                                    self.game_state = "game_over_screen" # Placeholder for win
                                    self.draw_text_hud("YOU REACHED THE CASTLE!", SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 4, 'Y')


                    elif self.game_state == "game_over_screen":
                        if event.key == pg.K_r:
                            self.reset_game_hard() # This will set game_state to "overworld"
                        elif event.key == pg.K_q:
                            running = False
                
                if event.type == pg.USEREVENT + 1: # Timer for level complete
                    if self.game_state == "level_complete_screen":
                        self.game_state = "overworld"
                        # Potentially mark level as completed on overworld here
                        pg.time.set_timer(pg.USEREVENT + 1, 0) # Disable timer

            # Update logic based on game state
            if self.game_state == "level":
                if self.player:
                    self.player.update(dt, self.platforms)
                self.enemies.update(dt, self.platforms)
                self.items.update(dt, self.platforms)
                self.debris.update(dt) # Debris has its own simple physics
                if self.camera and self.player:
                    self.camera.update(self.player)

                # Player-enemy collisions
                if self.player and self.player.invincible_timer <= 0:
                    enemy_hit_list = pg.sprite.spritecollide(self.player, self.enemies, False)
                    for enemy in enemy_hit_list:
                        if self.player.vel.y > 0 and self.player.rect.bottom < enemy.rect.centery: # Stomping
                            if isinstance(enemy, Goomba):
                                enemy.state = "squished"
                                enemy.image.fill((100,20,20)) # Darker, squished color
                                enemy.squish_timer = 0.5 * FPS # Squished for 0.5 seconds
                                enemy.vel.x = 0
                                self.player.vel.y = -self.player.jump_power / 2 # Small bounce
                                self.player.score += 100
                            elif isinstance(enemy, KoopaTroopa):
                                if enemy.state == "walk":
                                    enemy.stomped()
                                    self.player.vel.y = -self.player.jump_power / 2
                                    self.player.score += 100
                                elif enemy.state == "shell": # Kick shell
                                    enemy.state = "sliding"
                                    enemy.vel.x = ENEMY_MOVE_SPEED * 2 * (-1 if self.player.rect.centerx < enemy.rect.centerx else 1)
                                    self.player.vel.y = -self.player.jump_power / 3 # slight bounce
                                    self.player.score += 200
                        elif enemy.state != "squished" and enemy.state != "shell": # Player gets hit
                            self.player.die()
                            break # Only process one hit

                # Player-item collisions
                if self.player:
                    item_collected_list = pg.sprite.spritecollide(self.player, self.items, True) # True to remove item
                    for item in item_collected_list:
                        if isinstance(item, SuperMushroom):
                            if self.player.form == "small":
                                self.player.set_form("super")
                            self.player.score += 1000
                        elif isinstance(item, SuperLeaf):
                            self.player.set_form("raccoon")
                            self.player.score += 1000
                
                # Sliding Koopa shell collisions with other enemies
                for koopa in self.enemies:
                    if isinstance(koopa, KoopaTroopa) and koopa.state == "sliding":
                        # Check collision between this sliding koopa and other enemies (excluding itself)
                        other_enemies = pg.sprite.Group([e for e in self.enemies if e != koopa])
                        shell_hits = pg.sprite.spritecollide(koopa, other_enemies, True) # True to kill other enemies
                        for hit_enemy in shell_hits:
                            self.player.score += 200 # Score for shell kill
                            # Could add a "poof" animation for the killed enemy

                # Check for flagpole collision (level complete)
                if self.player and not self.level_complete:
                    flag_collision = pg.sprite.spritecollide(self.player, self.flagpoles, False)
                    if flag_collision:
                        self.complete_level()
                
                # Check if player fell off screen
                if self.player and self.player.rect.top > SCREEN_HEIGHT:
                    self.player.die()


            # Drawing logic based on game state
            if self.game_state == "overworld":
                self.draw_overworld()
            elif self.game_state == "level":
                self.screen.fill(color_map['L']) # Sky blue background
                if self.camera:
                    for sprite in self.all_sprites:
                        # Adjust sprite's position by camera offset for drawing
                        self.screen.blit(sprite.image, sprite.rect.move(-self.camera.offset.x, -self.camera.offset.y))
                    
                    # Draw HUD (Score, Lives, P-Meter if Raccoon)
                    if self.player:
                        self.draw_text_hud(f"MARIO x{self.player.lives}", 20, 20)
                        self.draw_text_hud(f"SCORE: {self.player.score}", SCREEN_WIDTH - 300, 20)
                        if self.player.form == "raccoon":
                            # Draw P-Meter
                            p_meter_bar_width = 20
                            p_meter_bar_height_unit = 10
                            p_meter_x = SCREEN_WIDTH - 100
                            p_meter_y = SCREEN_HEIGHT - 50
                            for i in range(7):
                                color = color_map['Y'] if i < self.player.p_meter else color_map['K']
                                pg.draw.rect(self.screen, color, (p_meter_x + i * (p_meter_bar_width + 2), p_meter_y, p_meter_bar_width, p_meter_bar_height_unit))
                            if self.player.p_meter >=7:
                                p_text = self.font.render("P!", True, color_map['R'])
                                self.screen.blit(p_text, (p_meter_x + 7 * (p_meter_bar_width + 2) + 5, p_meter_y -5))


                if self.debug_mode and self.player:
                    self.draw_text(f"Player Pos: ({self.player.rect.x:.1f}, {self.player.rect.y:.1f})", 10, SCREEN_HEIGHT - 90)
                    self.draw_text(f"Player Vel: ({self.player.vel.x:.1f}, {self.player.vel.y:.1f})", 10, SCREEN_HEIGHT - 60)
                    self.draw_text(f"OnGround: {self.player.on_ground} Fly: {self.player.is_flying} P: {self.player.p_meter:.1f}", 10, SCREEN_HEIGHT - 30)

            elif self.game_state == "game_over_screen":
                self.draw_game_over_screen()
            elif self.game_state == "level_complete_screen":
                self.draw_level_complete_screen()


            pg.display.flip() # Update the full screen

        pg.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()
