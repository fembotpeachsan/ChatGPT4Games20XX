import asyncio
import platform
import pygame
import sys
import math # Needed for sign function

# Constants
WIDTH, HEIGHT = 600, 400
FPS = 60

# Colors (remain the same)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)

# World colors (remain the same)
world_colors = {
    1: (BLUE, GREEN),
    2: (YELLOW, ORANGE),
    3: (CYAN, BLUE),
    4: (MAGENTA, PURPLE),
    5: (ORANGE, RED),
    6: (GRAY, WHITE),
    7: ((0, 128, 0), GREEN),
    8: (BLACK, RED),
}

# --- SMB3-Inspired Physics Constants ---
# Gravity
GRAVITY = 0.5
# Walking
WALK_ACCELERATION = 0.3
MAX_WALK_SPEED = 3.0
# Running (Hold Z)
RUN_ACCELERATION = 0.5
MAX_RUN_SPEED = 5.0
# Friction/Deceleration
FRICTION = 0.2 # Lower value = more slide
# Jumping
JUMP_INITIAL_POWER = -10.0 # Initial upward velocity on jump press
JUMP_VARIABLE_GRAVITY_MULTIPLIER = 0.5 # Gravity is weaker while holding jump & moving up
JUMP_CUTOFF_VELOCITY = -3.0 # If jump released early, set vertical speed to this if faster
# Enemy Interaction
ENEMY_STOMP_BOUNCE = -5.0 # Small bounce after stomping an enemy
ENEMY_STOMP_TOLERANCE = 5 # How many pixels below player bottom is still a stomp

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_x = 0.0 # Use floats for velocity
        self.vel_y = 0.0
        self.on_ground = False
        self.is_running = False
        self.is_jumping = False # Track if jump key is currently held

    def update(self, keys, platforms):
        # --- Determine Movement Parameters ---
        self.is_running = keys[pygame.K_z]
        current_acceleration = RUN_ACCELERATION if self.is_running else WALK_ACCELERATION
        max_speed = MAX_RUN_SPEED if self.is_running else MAX_WALK_SPEED

        # --- Horizontal Movement (Acceleration/Deceleration) ---
        target_vel_x = 0
        if keys[pygame.K_a]: # Moving Left
            target_vel_x = -max_speed
            # Apply acceleration, respecting max speed
            self.vel_x = max(self.vel_x - current_acceleration, -max_speed)
        elif keys[pygame.K_d]: # Moving Right
            target_vel_x = max_speed
            # Apply acceleration, respecting max speed
            self.vel_x = min(self.vel_x + current_acceleration, max_speed)
        else: # No horizontal input - apply friction
            if abs(self.vel_x) > FRICTION:
                self.vel_x -= math.copysign(FRICTION, self.vel_x)
            else:
                self.vel_x = 0

        # --- Jumping ---
        # Check for jump initiation (key press)
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = JUMP_INITIAL_POWER
            self.on_ground = False
            self.is_jumping = True # Mark that jump key is held initially

        # Check if jump key is *still* held
        if not (keys[pygame.K_SPACE] or keys[pygame.K_w]):
            self.is_jumping = False # Key released

        # --- Apply Gravity ---
        # Variable jump height: Apply less gravity if jump key held & moving up
        if self.is_jumping and self.vel_y < 0:
            self.vel_y += GRAVITY * JUMP_VARIABLE_GRAVITY_MULTIPLIER
        else:
            # Cut jump short if key released while moving up fast
            if not self.is_jumping and self.vel_y < JUMP_CUTOFF_VELOCITY:
                 self.vel_y = JUMP_CUTOFF_VELOCITY
            self.vel_y += GRAVITY

        # Limit fall speed (optional, but common)
        # self.vel_y = min(self.vel_y, 10) # Example max fall speed

        # --- Collision Detection ---
        # Move horizontally, then check for collisions
        self.rect.x += round(self.vel_x) # Round velocity for pixel movement

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0: # Moving right
                    self.rect.right = platform.rect.left
                    self.vel_x = 0 # Stop horizontal movement on collision
                elif self.vel_x < 0: # Moving left
                    self.rect.left = platform.rect.right
                    self.vel_x = 0 # Stop horizontal movement on collision

        # Move vertically, then check for collisions
        self.rect.y += round(self.vel_y)
        self.on_ground = False # Assume not on ground until collision check

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0: # Moving down
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.is_jumping = False # Can't be holding jump if just landed
                elif self.vel_y < 0: # Moving up
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0 # Stop upward movement

        # --- Screen Bounds ---
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.vel_x = 0

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

    def reset(self, x, y):
        """Resets player position and velocity."""
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.is_jumping = False


class Enemy:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.type = type
        self.direction = 1
        self.speed = 1 # Slightly slower default speed
        self.active = True # To handle removal after stomp

    def update(self):
        if not self.active:
            return
        # Basic patrol movement (could be improved with platform awareness)
        self.rect.x += self.speed * self.direction
        # Simple boundary patrol - replace with platform edge detection for better AI
        if self.rect.x > 500 or self.rect.x < 100:
            self.direction *= -1

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, RED, self.rect)

    def stomp(self):
        """Called when the player successfully stomps this enemy."""
        self.active = False
        # Optional: Add score, sound effect trigger, or animation state here

class Platform:
    def __init__(self, x, y, w, h, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Goal:
    def __init__(self, x, y, w, h, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

def get_level_data(world):
    bg_color, platform_color = world_colors.get(world, (BLACK, WHITE))
    platforms = [
        Platform(0, 350, 600, 50, platform_color),  # Ground
        Platform(150, 270, 120, 20, platform_color), # Adjusted platforms
        Platform(350, 200, 100, 20, platform_color),
        Platform(50, 150, 80, 20, platform_color), # Added platform
    ]
    enemies = [
        Enemy(200, 318, 'goomba'), # On ground
        Enemy(400, 168, 'goomba'), # On platform
    ]
    goal = Goal(550, 318, 20, 32, YELLOW)
    return bg_color, platforms, enemies, goal

def setup():
    try:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SMB3 Inspired Engine Demo")
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 36) or pygame.font.SysFont('arial', 36)
        return screen, clock, font
    except Exception as e:
        print(f"Pygame setup failed: {e}")
        sys.exit(1)

async def main():
    screen, clock, font = setup()

    world_buttons = [
        {'rect': pygame.Rect(50, 50, 100, 50), 'world': 1},
        {'rect': pygame.Rect(200, 50, 100, 50), 'world': 2},
        {'rect': pygame.Rect(350, 50, 100, 50), 'world': 3},
        {'rect': pygame.Rect(500, 50, 100, 50), 'world': 4},
        {'rect': pygame.Rect(50, 150, 100, 50), 'world': 5},
        {'rect': pygame.Rect(200, 150, 100, 50), 'world': 6},
        {'rect': pygame.Rect(350, 150, 100, 50), 'world': 7},
        {'rect': pygame.Rect(500, 150, 100, 50), 'world': 8},
    ]

    current_state = 'overworld'
    current_world = None
    player = None
    platforms = []
    enemies = []
    goal = None
    bg_color = BLACK
    message = ""
    message_timer = 0
    player_start_pos = (50, 300) # Define start position

    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_state == 'level':
                        current_state = 'overworld' # Go back to overworld
                        message = "Exited Level"
                        message_timer = FPS * 2
                    else:
                        running = False # Exit game from overworld
            # Removed keydown jump - handled by get_pressed now
            elif event.type == pygame.MOUSEBUTTONDOWN and current_state == 'overworld':
                for button in world_buttons:
                    if button['rect'].collidepoint(event.pos):
                        current_world = button['world']
                        bg_color, platforms, enemies, goal = get_level_data(current_world)
                        # Ensure enemies are active when level starts
                        for enemy in enemies:
                            enemy.active = True
                        player = Player(player_start_pos[0], player_start_pos[1])
                        current_state = 'level'
                        message = f"World {current_world} Start!"
                        message_timer = FPS * 2
                        break

        # --- Game State Logic ---
        if current_state == 'overworld':
            screen.fill(BLACK)
            for button in world_buttons:
                pygame.draw.rect(screen, WHITE, button['rect'])
                text = font.render(f"World {button['world']}", True, BLACK)
                screen.blit(text, (button['rect'].x + 10, button['rect'].y + 10))
            if message_timer > 0:
                text = font.render(message, True, WHITE)
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
                message_timer -= 1

        elif current_state == 'level':
            keys = pygame.key.get_pressed()
            player.update(keys, platforms)

            # Update active enemies
            active_enemies = [e for e in enemies if e.active]
            for enemy in active_enemies:
                enemy.update()

            # --- Player-Enemy Collision ---
            player_died = False
            for enemy in active_enemies:
                if player.rect.colliderect(enemy.rect):
                    # Check for stomp: Player moving down, player bottom near enemy top
                    is_stomp = (player.vel_y > 0 and
                                player.rect.bottom <= enemy.rect.top + ENEMY_STOMP_TOLERANCE)

                    if is_stomp:
                        enemy.stomp() # Deactivate enemy
                        player.vel_y = ENEMY_STOMP_BOUNCE # Bounce player
                        player.on_ground = False # Ensure bounce happens
                        # Optional: Add score, sound effect
                    else:
                        # Collision from side or bottom - player dies
                        player_died = True
                        break # No need to check other enemies

            # Check for falling out of bounds
            if player.rect.top > HEIGHT: # Use top instead of y for clarity
                 player_died = True

            if player_died:
                player.reset(player_start_pos[0], player_start_pos[1])
                # Reset enemies (optional, could keep them defeated)
                # for enemy in enemies: enemy.active = True
                message = "Ouch! Try Again!"
                message_timer = FPS * 2

            # --- Check for Goal ---
            if player.rect.colliderect(goal.rect):
                current_state = 'overworld'
                message = f"World {current_world} Cleared!"
                message_timer = FPS * 2

            # --- Rendering ---
            screen.fill(bg_color)
            for platform in platforms:
                platform.draw(screen)
            for enemy in enemies: # Draw all enemies (even inactive ones, if they had a 'defeated' sprite)
                enemy.draw(screen) # Currently just doesn't draw if inactive
            goal.draw(screen)
            player.draw(screen)
            if message_timer > 0:
                text = font.render(message, True, WHITE)
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
                message_timer -= 1

        # --- Update Display ---
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0) # Yield control for asyncio

# --- Main Execution ---
if platform.system() == "Emscripten":
    # This block is for running in a web browser using Pygbag/Emscripten
    asyncio.ensure_future(main())
else:
    # This block is for running as a standard Python script
    if __name__ == "__main__":
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("Game terminated by user.")
        finally:
            pygame.quit()
            sys.exit(0)

import asyncio
import platform
import pygame
import sys
import math # Needed for sign function

# Constants
WIDTH, HEIGHT = 600, 400
FPS = 60

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)

# World colors
world_colors = {
    1: (BLUE, GREEN),
    2: (YELLOW, ORANGE),
    3: (CYAN, BLUE),
    4: (MAGENTA, PURPLE),
    5: (ORANGE, RED),
    6: (GRAY, WHITE),
    7: ((0, 128, 0), GREEN),
    8: (BLACK, RED),
}

# --- SMB3-Inspired Physics Constants ---
GRAVITY = 0.5
WALK_ACCELERATION = 0.3
MAX_WALK_SPEED = 3.0
RUN_ACCELERATION = 0.5
MAX_RUN_SPEED = 5.0
FRICTION = 0.2
JUMP_INITIAL_POWER = -10.0
JUMP_VARIABLE_GRAVITY_MULTIPLIER = 0.5
JUMP_CUTOFF_VELOCITY = -3.0
ENEMY_STOMP_BOUNCE = -5.0
ENEMY_STOMP_TOLERANCE = 5

class Player:
    def __init__(self, x, y, left_key, right_key, run_key=None, jump_keys=None, color=BLUE):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.is_running = False
        self.is_jumping = False
        # control mapping
        self.left_key = left_key
        self.right_key = right_key
        self.run_key = run_key
        self.jump_keys = jump_keys or []
        self.color = color

    def update(self, keys, platforms):
        # Determine movement parameters
        self.is_running = keys[self.run_key] if self.run_key else False
        accel = RUN_ACCELERATION if self.is_running else WALK_ACCELERATION
        max_speed = MAX_RUN_SPEED if self.is_running else MAX_WALK_SPEED

        # Horizontal movement
        if keys[self.left_key]:
            self.vel_x = max(self.vel_x - accel, -max_speed)
        elif keys[self.right_key]:
            self.vel_x = min(self.vel_x + accel, max_speed)
        else:
            if abs(self.vel_x) > FRICTION:
                self.vel_x -= math.copysign(FRICTION, self.vel_x)
            else:
                self.vel_x = 0

        # Jumping
        if any(keys[k] for k in self.jump_keys) and self.on_ground:
            self.vel_y = JUMP_INITIAL_POWER
            self.on_ground = False
            self.is_jumping = True
            # Meow on jump for NPCs (red)
            if self.color == RED:
                print("Meow!")
        if not any(keys[k] for k in self.jump_keys):
            self.is_jumping = False

        # Apply gravity
        if self.is_jumping and self.vel_y < 0:
            self.vel_y += GRAVITY * JUMP_VARIABLE_GRAVITY_MULTIPLIER
        else:
            if not self.is_jumping and self.vel_y < JUMP_CUTOFF_VELOCITY:
                self.vel_y = JUMP_CUTOFF_VELOCITY
            self.vel_y += GRAVITY

        # Move and collide horizontally
        self.rect.x += round(self.vel_x)
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_x > 0:
                    self.rect.right = plat.rect.left
                elif self.vel_x < 0:
                    self.rect.left = plat.rect.right
                self.vel_x = 0

        # Move and collide vertically
        self.rect.y += round(self.vel_y)
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                elif self.vel_y < 0:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0

        # Screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.vel_x = 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def reset(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.is_jumping = False

class Enemy:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.type = type
        self.direction = 1
        self.speed = 1
        self.active = True

    def update(self):
        if not self.active:
            return
        self.rect.x += self.speed * self.direction
        if self.rect.x > 500 or self.rect.x < 100:
            self.direction *= -1

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, RED, self.rect)

    def stomp(self):
        self.active = False

class Platform:
    def __init__(self, x, y, w, h, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class MovingPlatform(Platform):
    def __init__(self, x, y, w, h, color, x_min, x_max, speed):
        super().__init__(x, y, w, h, color)
        self.x_min = x_min
        self.x_max = x_max
        self.speed = speed
        self.direction = 1
    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.x < self.x_min or self.rect.x > self.x_max:
            self.direction *= -1

class Goal:
    def __init__(self, x, y, w, h, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


def get_level_data(world):
    bg_color, plat_color = world_colors.get(world, (BLACK, WHITE))
    # Static platforms
    platforms = [
        Platform(0, 350, 600, 50, plat_color),
        Platform(150, 270, 120, 20, plat_color),
        Platform(50, 150, 80, 20, plat_color),
    ]
    # Moving platform
    platforms.append(
        MovingPlatform(250, 220, 100, 20, plat_color, x_min=200, x_max=400, speed=2)
    )
    enemies = [
        Enemy(200, 318, 'goomba'),
        Enemy(400, 168, 'goomba'),
    ]
    goal = Goal(550, 318, 20, 32, YELLOW)
    return bg_color, platforms, enemies, goal


def setup():
    try:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SMB3 Inspired Engine Demo")
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 36) or pygame.font.SysFont('arial', 36)
        return screen, clock, font
    except Exception as e:
        print(f"Pygame setup failed: {e}")
        sys.exit(1)

async def main():
    screen, clock, font = setup()
    world_buttons = [
        {'rect': pygame.Rect(50, 50, 100, 50), 'world': 1},
        {'rect': pygame.Rect(200, 50, 100, 50), 'world': 2},
        {'rect': pygame.Rect(350, 50, 100, 50), 'world': 3},
        {'rect': pygame.Rect(500, 50, 100, 50), 'world': 4},
        {'rect': pygame.Rect(50, 150, 100, 50), 'world': 5},
        {'rect': pygame.Rect(200, 150, 100, 50), 'world': 6},
        {'rect': pygame.Rect(350, 150, 100, 50), 'world': 7},
        {'rect': pygame.Rect(500, 150, 100, 50), 'world': 8},
    ]

    current_state = 'overworld'
    current_world = None
    players = []
    platforms = []
    enemies = []
    goal = None
    bg_color = BLACK
    message = ""
    message_timer = 0
    player_start = (50, 300)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_state == 'level':
                        current_state = 'overworld'
                        message = "Exited Level"
                        message_timer = FPS * 2
                    else:
                        running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and current_state == 'overworld':
                for btn in world_buttons:
                    if btn['rect'].collidepoint(event.pos):
                        current_world = btn['world']
                        bg_color, platforms, enemies, goal = get_level_data(current_world)
                        # initialize two players:
                        players = [
                            # Player 1: arrow controls, run with RSHIFT, jump with UP
                            Player(player_start[0], player_start[1], pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RSHIFT, [pygame.K_UP], color=BLUE),
                            # NPC / Player 2: WASD + space jump
                            Player(player_start[0] + 50, player_start[1], pygame.K_a, pygame.K_d, None, [pygame.K_SPACE], color=RED)
                        ]
                        # reset enemies
                        for e in enemies:
                            e.active = True
                        current_state = 'level'
                        message = f"World {current_world} Start!"
                        message_timer = FPS * 2
                        break

        if current_state == 'overworld':
            screen.fill(BLACK)
            for btn in world_buttons:
                pygame.draw.rect(screen, WHITE, btn['rect'])
                txt = font.render(f"World {btn['world']}", True, BLACK)
                screen.blit(txt, (btn['rect'].x+10, btn['rect'].y+10))
            if message_timer > 0:
                txt = font.render(message, True, WHITE)
                screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
                message_timer -= 1

        elif current_state == 'level':
            # Update moving platforms
            for plat in platforms:
                if hasattr(plat, 'update'):
                    plat.update()

            keys = pygame.key.get_pressed()
            # Update players
            for p in players:
                p.update(keys, platforms)

            # Update enemies
            active_enemies = [e for e in enemies if e.active]
            for e in active_enemies:
                e.update()

            # Handle collisions for each player
            for p in players:
                died = False
                for e in active_enemies:
                    if p.rect.colliderect(e.rect):
                        stomp = (p.vel_y > 0 and p.rect.bottom <= e.rect.top + ENEMY_STOMP_TOLERANCE)
                        if stomp:
                            e.stomp()
                            p.vel_y = ENEMY_STOMP_BOUNCE
                            p.on_ground = False
                        else:
                            died = True
                            break
                if p.rect.top > HEIGHT:
                    died = True
                if died:
                    # reset that player only
                    start_x = player_start[0] if p.color == BLUE else player_start[0]+50
                    p.reset(start_x, player_start[1])
                    message = "Ouch! Try Again!"
                    message_timer = FPS * 2

            # Check for goal by any player
            if any(p.rect.colliderect(goal.rect) for p in players):
                current_state = 'overworld'
                message = f"World {current_world} Cleared!"
                message_timer = FPS * 2

            # Rendering level
            screen.fill(bg_color)
            for plat in platforms:
                plat.draw(screen)
            for e in enemies:
                e.draw(screen)
            for p in players:
                p.draw(screen)
            goal.draw(screen)
            if message_timer > 0:
                txt = font.render(message, True, WHITE)
                screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
                message_timer -= 1

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("Game terminated by user.")
        finally:
            pygame.quit()
            sys.exit(0)
