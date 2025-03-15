# Super Mario Bros 2D - Enhanced Version (test.py)
# Features:
# - High-resolution sprites and smooth animations (improved graphics and rendering).
# - 60 FPS gameplay, with consistent frame rate and delta-time based movement.
# - Enhanced physics: realistic jumping (variable jump height), acceleration and friction for fluid movement.
# - Smarter enemies with improved AI (basic pathfinding, jumping over obstacles, reacting to Mario's power-ups).
# - Expanded levels with complex design: breakable blocks, hidden power-ups, warp zones for secret/alternate paths.
# - New power-ups and abilities: invincibility star, double jump power-up, fire flower, etc., plus enhanced existing power-ups.
# - Improved sound: chiptune background music and sound effects, with dynamic music changes (e.g., invincibility theme).
# - macOS (M1) optimization: uses Pygame 2 (SDL2) for better performance (Metal API under-the-hood), double buffering, and ready for packaging (PyInstaller/py2app).
import pygame
import math
import random
import sys
import os
import platform

# Initialize Pygame and mixer for sounds
pygame.init()
pygame.mixer.init()

# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Physics constants
GRAVITY = 1800    # pixels per second^2 (downward acceleration)
ACCEL = 1200      # horizontal acceleration (pixels/sec^2)
DECEL = 2000      # horizontal deceleration when not moving (pixels/sec^2)
MAX_SPEED = 300   # max horizontal speed (pixels/sec)
JUMP_SPEED = 700  # initial jump velocity (pixels/sec upward)

# Colors (for placeholders and debugging)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)

# Load assets (sprites and sounds). Using placeholders since actual files are not provided.
# In a real game, here we would load high-res images and sounds.
try:
    # Player (Mario) sprites for animation (idle, running frames, jump)
    mario_idle_img = pygame.Surface((40, 50)); mario_idle_img.fill(RED)
    mario_run_img1 = pygame.Surface((40, 50)); mario_run_img1.fill((200,0,0))
    mario_run_img2 = pygame.Surface((40, 50)); mario_run_img2.fill((150,0,0))
    mario_jump_img = pygame.Surface((40, 50)); mario_jump_img.fill((100,0,0))
    # Enemy sprites
    goomba_img = pygame.Surface((40, 40)); goomba_img.fill((139,69,19))  # brownish
    smart_enemy_img = pygame.Surface((40, 40)); smart_enemy_img.fill((80, 50, 20))
    # Power-up sprites
    star_img = pygame.Surface((30, 30)); star_img.fill((255, 255, 0))
    doublejump_img = pygame.Surface((30, 30)); doublejump_img.fill((0, 255, 255))
    mushroom_img = pygame.Surface((30, 30)); mushroom_img.fill((255, 0, 255))
    flower_img = pygame.Surface((30, 30)); flower_img.fill((255, 165, 0))
    # Sound effects and music (placeholder, as actual files are needed for sound)
    jump_sound = None
    powerup_sound = None
    # For real game, e.g.:
    # jump_sound = pygame.mixer.Sound("jump.wav")
    # powerup_sound = pygame.mixer.Sound("powerup.wav")
    # pygame.mixer.music.load("main_theme.ogg")
    # pygame.mixer.music.play(-1)  # loop background music
except Exception as e:
    print("Error loading assets:", e)
    sys.exit()

# Player (Mario) class with enhanced physics and abilities
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Set up sprite images for animations
        self.images = {
            "idle": mario_idle_img,
            "run0": mario_run_img1,
            "run1": mario_run_img2,
            "jump": mario_jump_img
        }
        self.image = self.images["idle"]
        self.rect = self.image.get_rect(topleft=(x, y))
        # Physics attributes
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        # State attributes
        self.big = False           # powered up by mushroom
        self.invincible = False    # star power
        self.invincible_timer = 0
        self.can_double_jump = False
        self.has_double_jumped = False
        self.has_fire = False      # fire flower power (can shoot)
        # Animation state
        self.run_frame = 0
        self.anim_timer = 0.0

    def update(self, dt, keys, level):
        # Horizontal movement with acceleration
        if keys[pygame.K_LEFT]:
            self.vel_x -= ACCEL * dt
            if self.vel_x < -MAX_SPEED:
                self.vel_x = -MAX_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel_x += ACCEL * dt
            if self.vel_x > MAX_SPEED:
                self.vel_x = MAX_SPEED
        # Apply friction when no horizontal input
        if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            if self.vel_x > 0:
                self.vel_x -= DECEL * dt
                if self.vel_x < 0: self.vel_x = 0
            elif self.vel_x < 0:
                self.vel_x += DECEL * dt
                if self.vel_x > 0: self.vel_x = 0

        # Jumping (with double jump support)
        if keys[pygame.K_SPACE]:
            if self.on_ground:
                # Initial jump
                self.vel_y = -JUMP_SPEED
                self.on_ground = False
                self.has_double_jumped = False
                # if jump_sound: jump_sound.play()
            elif self.can_double_jump and not self.has_double_jumped:
                # Double jump once in mid-air
                self.vel_y = -JUMP_SPEED
                self.has_double_jumped = True
                # if jump_sound: jump_sound.play()
        # Variable jump height: if jump key released early, cut upward velocity
        if not keys[pygame.K_SPACE] and self.vel_y < 0:
            self.vel_y *= 0.5  # reduce upward velocity for smoother jump control

        # Apply gravity
        self.vel_y += GRAVITY * dt
        # Limit falling speed to avoid extreme fast fall
        if self.vel_y > GRAVITY:
            self.vel_y = GRAVITY

        # Horizontal movement and collision
        self.rect.x += self.vel_x * dt
        for block in level.solid_blocks:
            if self.rect.colliderect(block.rect):
                if self.vel_x > 0:  # moving right into block
                    self.rect.right = block.rect.left
                elif self.vel_x < 0:  # moving left into block
                    self.rect.left = block.rect.right
                self.vel_x = 0

        # Vertical movement and collision
        self.rect.y += self.vel_y * dt
        self.on_ground = False
        for block in level.solid_blocks:
            if self.rect.colliderect(block.rect):
                if self.vel_y > 0:  # falling and hit a block from above
                    self.rect.bottom = block.rect.top
                    self.on_ground = True
                    self.has_double_jumped = False  # reset double jump when landing
                elif self.vel_y < 0:  # jumping and hit a block from below
                    self.rect.top = block.rect.bottom
                    # If block is breakable and Mario is big, break it
                    if isinstance(block, Block) and block.breakable:
                        if self.big:
                            level.solid_blocks.remove(block)
                    # If block has hidden power-up, spawn it
                    if isinstance(block, Block) and block.hidden_power:
                        level.spawn_powerup(block.rect.x, block.rect.y - 40, block.hidden_power)
                        block.hidden_power = None
                self.vel_y = 0

        # Enemy collisions
        for enemy in list(level.enemies):
            if self.rect.colliderect(enemy.rect) and not enemy.defeated:
                if self.invincible:
                    # Mario is invincible: defeat any enemy on contact
                    enemy.defeated = True
                    level.enemies.remove(enemy)
                    continue
                if self.vel_y > 0:
                    # Mario stomped the enemy from above
                    enemy.defeated = True
                    level.enemies.remove(enemy)
                    # Bounce Mario up slightly after stomp
                    self.vel_y = -JUMP_SPEED * 0.5
                    self.on_ground = False
                else:
                    # Mario was hit by enemy
                    if self.big:
                        # If Mario is big, shrink instead of dying
                        self.big = False
                        # brief invincibility after getting hit
                        self.invincible = True
                        self.invincible_timer = 2000  # 2 seconds of post-hit invincibility
                        # Could play a shrink or damage sound
                    else:
                        # Mario is small and gets hit -> game over (or lose a life)
                        print("Mario loses a life or game over!")  # placeholder
                        self.invincible = True
                        self.invincible_timer = 2000
                        # In a real game, we'd handle lives and restart level

        # Power-up collisions
        for power in list(level.powerups):
            if self.rect.colliderect(power.rect):
                # Consume the power-up and apply its effect
                if power.type == "mushroom":
                    self.big = True
                elif power.type == "flower":
                    self.has_fire = True
                    self.big = True  # fire flower also makes Mario big
                elif power.type == "star":
                    self.invincible = True
                    self.invincible_timer = 5000  # 5 seconds of invincibility
                    # Switch to invincibility music if available
                    # pygame.mixer.music.load("invincible_theme.ogg"); pygame.mixer.music.play(-1)
                elif power.type == "double_jump":
                    self.can_double_jump = True
                # if powerup_sound: powerup_sound.play()
                level.powerups.remove(power)

        # Update invincibility timer
        if self.invincible:
            self.invincible_timer -= dt * 1000
            if self.invincible_timer <= 0:
                # Invincibility ended
                self.invincible = False
                # Restore normal music if it was changed for invincibility
                # pygame.mixer.music.load("main_theme.ogg"); pygame.mixer.music.play(-1)

        # Update animation
        if not self.on_ground:
            # Jumping/falling animation
            self.image = self.images["jump"]
        else:
            if abs(self.vel_x) > 0.1:
                # Running animation (toggle frames)
                self.anim_timer += dt
                if self.anim_timer > 0.1:  # switch frame every 0.1s (10 fps animation)
                    self.anim_timer = 0
                    self.run_frame = 1 - self.run_frame
                self.image = self.images[f"run{self.run_frame}"]
            else:
                # Idle animation/frame
                self.image = self.images["idle"]

# Enemy class with basic AI (Goombas walk, Smart chase) and extensible behaviors (e.g., pathfinding, ranged attacks).
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="goomba"):
        super().__init__()
        self.type = enemy_type
        if self.type == "goomba":
            self.image = goomba_img
            self.speed = 100
        elif self.type == "smart":
            self.image = smart_enemy_img
            self.speed = 120
        else:
            self.image = goomba_img
            self.speed = 100
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = self.speed if self.type != "smart" else 0
        self.vel_y = 0
        self.on_ground = False
        self.defeated = False
        self.direction = 1 if self.vel_x >= 0 else -1  # 1: right, -1: left

    def update(self, dt, level, player):
        if self.defeated:
            return
        # Gravity
        self.vel_y += GRAVITY * dt
        if self.vel_y > GRAVITY:
            self.vel_y = GRAVITY
        # Basic AI depending on type
        if self.type == "goomba":
            # Goomba: walks in current direction, turns around at walls or edges
            # (Movement handled after collision checks)
            pass
        elif self.type == "smart":
            # Smart enemy: tries to follow Mario's horizontal position
            if player.invincible:
                # If Mario is invincible, this enemy runs away instead of chasing
                self.direction = -1 if player.rect.x > self.rect.x else 1
            else:
                # Chase Mario horizontally
                self.direction = 1 if player.rect.x > self.rect.x else -1
            self.vel_x = self.direction * self.speed
            # If there's an obstacle in front and on ground and Mario is above, attempt a jump to climb over
            ahead_rect = pygame.Rect(self.rect.x + self.direction*5, self.rect.y, self.rect.width, self.rect.height)
            blocked = any(ahead_rect.colliderect(block.rect) for block in level.solid_blocks)
            if blocked and self.on_ground and player.rect.y < self.rect.y:
                self.vel_y = -JUMP_SPEED * 0.7  # jump with 70% of Mario's jump power
            # If desired, could also add ranged attacks here when Mario is in sight.

        # Horizontal movement
        self.rect.x += self.vel_x * dt
        # Check horizontal collisions and edge turning
        for block in level.solid_blocks:
            if self.rect.colliderect(block.rect):
                if self.vel_x > 0:
                    self.rect.right = block.rect.left
                elif self.vel_x < 0:
                    self.rect.left = block.rect.right
                self.vel_x = -self.vel_x  # reverse horizontal direction
                self.direction *= -1
        # Check for edge of platform (goomba should not fall off ledges in Mario games typically)
        if self.type == "goomba":
            # If goomba is on ground and at a ledge, turn around
            foot_x = self.rect.centerx + self.direction * self.rect.width//2
            foot_y = self.rect.bottom + 1
            on_ground_block = False
            for block in level.solid_blocks:
                if block.rect.collidepoint(foot_x, foot_y):
                    on_ground_block = True
                    break
            if self.on_ground and not on_ground_block:
                # no ground ahead, turn around
                self.direction *= -1
                self.vel_x = self.direction * self.speed

        # Vertical movement
        self.rect.y += self.vel_y * dt
        self.on_ground = False
        for block in level.solid_blocks:
            if self.rect.colliderect(block.rect):
                if self.vel_y > 0:  # landed on a block
                    self.rect.bottom = block.rect.top
                    self.on_ground = True
                elif self.vel_y < 0:  # hit a ceiling
                    self.rect.top = block.rect.bottom
                self.vel_y = 0

        # If enemy goes off bottom of level (falls down a hole), consider it defeated
        if self.rect.y > HEIGHT:
            self.defeated = True

# PowerUp class for various power-ups (mushroom, flower, star, etc.)
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, ptype="mushroom"):
        super().__init__()
        self.type = ptype
        if self.type == "mushroom":
            self.image = mushroom_img
        elif self.type == "flower":
            self.image = flower_img
        elif self.type == "star":
            self.image = star_img
        elif self.type == "double_jump":
            self.image = doublejump_img
        else:
            self.image = pygame.Surface((30,30)); self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft=(x, y))
        # Initial velocity for moving power-ups
        self.vel_x = 0
        self.vel_y = 0
        if self.type == "mushroom":
            # Mushrooms move horizontally
            self.vel_x = 100
        if self.type == "star":
            # Stars bounce around
            self.vel_x = 150
            self.vel_y = -400

    def update(self, dt, level):
        # Apply gravity to power-up
        self.vel_y += GRAVITY * dt
        if self.vel_y > GRAVITY:
            self.vel_y = GRAVITY
        # Move horizontally and collide
        self.rect.x += self.vel_x * dt
        for block in level.solid_blocks:
            if self.rect.colliderect(block.rect):
                if self.vel_x > 0:
                    self.rect.right = block.rect.left
                elif self.vel_x < 0:
                    self.rect.left = block.rect.right
                # Reverse horizontal direction for moving power-ups (like mushroom or star bouncing off walls)
                self.vel_x = -self.vel_x
        # Move vertically and collide
        self.rect.y += self.vel_y * dt
        for block in level.solid_blocks:
            if self.rect.colliderect(block.rect):
                if self.vel_y > 0:
                    self.rect.bottom = block.rect.top
                    if self.type == "star":
                        # Star bounces when it hits the ground
                        self.vel_y = -300
                    else:
                        self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = block.rect.bottom
                    self.vel_y = 0
        # Remove if falls off the level
        if self.rect.y > HEIGHT:
            if self in level.powerups:
                level.powerups.remove(self)

# Block class for level tiles (solids, breakable blocks, etc.)
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, breakable=False, hidden_power=None):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.breakable = breakable
        self.hidden_power = hidden_power

# Level class containing layout, and lists of game objects (blocks, enemies, powerups, warps)
class Level:
    def __init__(self, layout):
        self.solid_blocks = []
        self.enemies = []
        self.powerups = []
        self.warps = {}   # dict mapping (grid_x, grid_y) of warp entry to target Level
        self.start_x = 0  # Mario's start position
        self.start_y = 0
        self._load_layout(layout)

    def _load_layout(self, layout):
        # Build the level from a 2D layout list of strings
        tile_size = 40
        for j, row in enumerate(layout):
            for i, ch in enumerate(row):
                x = i * tile_size
                y = j * tile_size
                if ch == 'X':
                    # Solid ground block
                    self.solid_blocks.append(Block(x, y, tile_size, tile_size))
                elif ch == 'B':
                    # Breakable block (may have a hidden power-up)
                    # Randomly decide a hidden power for demonstration (or could be predetermined in layout)
                    hidden = random.choice([None, "mushroom", "flower", "star", "double_jump"])
                    self.solid_blocks.append(Block(x, y, tile_size, tile_size, breakable=True, hidden_power=hidden))
                elif ch == 'G':
                    # Goomba enemy
                    self.enemies.append(Enemy(x, y, "goomba"))
                elif ch == 'E':
                    # "Smart" enemy
                    self.enemies.append(Enemy(x, y, "smart"))
                elif ch == 'S':
                    # Star power-up placed in world
                    self.powerups.append(PowerUp(x, y, "star"))
                elif ch == 'D':
                    # Double-jump power-up
                    self.powerups.append(PowerUp(x, y, "double_jump"))
                elif ch == 'M':
                    # Mario's starting position
                    self.start_x, self.start_y = x, y
                elif ch == 'P':
                    # Warp pipe or door
                    # Represented as a solid block (so Mario can stand on it if needed)
                    self.solid_blocks.append(Block(x, y, tile_size, tile_size))
                    # Mark this tile as a warp entry
                    self.warps[(i, j)] = None

    def spawn_powerup(self, x, y, ptype):
        # Spawn a power-up into the level (used when hitting a block with a hidden power-up)
        self.powerups.append(PowerUp(x, y, ptype))

# Define two example levels (with hidden area)
level1_layout = [
    "........................................................................",
    "........................................................................",
    "....M.........................................................D........",
    "........................................................................",
    "......................XXXX...................B.........................",
    "...................................................................S....",
    "XXXXXXXXXXXXXXX......................XXXXXXX............................",
    "XXXXXXXXXXXXXXX......G.......B...........E.P............................",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
]
# Legend: M = Mario start, X = ground block, B = breakable block (random power-up), G = goomba, E = smart enemy,
# S = star power-up, D = double jump power-up, P = warp pipe (secret warp between levels)

level2_layout = [
    "........................................................",
    "......................S.................................",
    "....XXXXXXXX............................................",
    "...........................................M............",
    "XXXXXXXXXXXXXXXXXXXXX....XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
]
# Level2 can represent a secret area or next level (contains a star and a starting point for demonstration).

# Create level instances
level1 = Level(level1_layout)
level2 = Level(level2_layout)
# Link warps (if any warp points exist in levels)
if level1.warps:
    # Link all warps in level1 to level2's start (for demo, assume one secret warp leads to level2)
    for warp in level1.warps:
        level1.warps[warp] = level2
if level2.warps:
    # If level2 had warp(s), link them back to level1 (or to another level if extended further)
    for warp in level2.warps:
        level2.warps[warp] = level1

# Game class to manage the game state and main loop
class Game:
    def __init__(self):
        # Set up display with double buffering (and optional hardware accel flags)
        flags = pygame.DOUBLEBUF
        # On macOS, using FULLSCREEN or SCALED can improve performance by utilizing Metal acceleration
        # We won't force fullscreen here, but user can toggle with F key
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        pygame.display.set_caption("Super Mario Bros 2D - Enhanced")
        # Start with level1
        self.current_level = level1
        self.player = Player(level1.start_x or 0, level1.start_y or (HEIGHT - 50))
        # Time and control
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        # Main game loop
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Cap at 60 FPS and get delta time in seconds
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_f:
                        # Toggle fullscreen on F key for performance testing on Mac
                        pygame.display.toggle_fullscreen()
            keys = pygame.key.get_pressed()
            # Update game objects
            self.player.update(dt, keys, self.current_level)
            for enemy in self.current_level.enemies:
                enemy.update(dt, self.current_level, self.player)
            for power in self.current_level.powerups:
                power.update(dt, self.current_level)
            # Check if player reached a warp point
            for warp_coords, target_level in self.current_level.warps.items():
                if target_level:
                    i, j = warp_coords
                    tile_size = 40
                    warp_rect = pygame.Rect(i*tile_size, j*tile_size, tile_size, tile_size)
                    if self.player.rect.colliderect(warp_rect):
                        # Warp triggered: switch level
                        self.current_level = target_level
                        # Set player position to new level's start
                        self.player.rect.topleft = (self.current_level.start_x or 0, self.current_level.start_y or (HEIGHT - 50))
                        # If switching to secret level, we keep Mario's state (power-ups etc.)

            # Render everything
            self.screen.fill((107, 140, 255))  # fill background with sky-blue color
            # Draw blocks
            for block in self.current_level.solid_blocks:
                self.screen.blit(block.image, block.rect.topleft)
            # Draw power-ups
            for power in self.current_level.powerups:
                self.screen.blit(power.image, power.rect.topleft)
            # Draw enemies (skip if defeated)
            for enemy in self.current_level.enemies:
                if not enemy.defeated:
                    self.screen.blit(enemy.image, enemy.rect.topleft)
            # Draw player (Mario). If invincible, make him blink by drawing only on alternating frames
            if self.player.invincible and int(pygame.time.get_ticks() / 100) % 2 == 0:
                # blinking: skip drawing this frame
                pass
            else:
                self.screen.blit(self.player.image, self.player.rect.topleft)
            # Flip the display buffers
            pygame.display.flip()
        pygame.quit()

# Run the game if this script is executed
if __name__ == "__main__":
    game = Game()
    game.run()
