import asyncio
import platform
import pygame
import sys
import math

# ------------- GAME CONSTANTS -------------
WIDTH, HEIGHT = 600, 400
FPS = 60

# Colors
BLACK    = (  0,   0,   0)
WHITE    = (255, 255, 255)
BLUE     = (  0,   0, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 165,   0)
CYAN     = (  0, 255, 255)
MAGENTA  = (255,   0, 255)
PURPLE   = (128,   0, 128)
GRAY     = (128, 128, 128)

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

# SMB3-Inspired Physics
GRAVITY                       = 0.5
WALK_ACCELERATION             = 0.3
MAX_WALK_SPEED                = 3.0
RUN_ACCELERATION              = 0.5
MAX_RUN_SPEED                 = 5.0
FRICTION                      = 0.2
JUMP_INITIAL_POWER            = -10.0
JUMP_VARIABLE_GRAVITY_MULTIPLIER = 0.5
JUMP_CUTOFF_VELOCITY          = -3.0
TERMINAL_VELOCITY             = 10   # Limits maximum fall speed

# Enemy stomping
ENEMY_STOMP_BOUNCE     = -5.0
ENEMY_STOMP_TOLERANCE  = 5

# P-Meter for running (mimics SMB3 run buildup)
PMETER_MAX = 60   # how many “ticks” until we have a full P-meter

# ------------- GAME OBJECTS -------------

class Platform:
    """
    Regular flat platform.
    """
    def __init__(self, x, y, w, h, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def update(self):
        pass

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Slope:
    """
    A simple slope that goes up from left to right.
    slope_height: how tall the slope is
    slope_width: how wide the slope is
    slope ‘rect’ is effectively bounding box for quick collision check.
    """
    def __init__(self, x, y, slope_width, slope_height, color):
        self.x = x
        self.y = y
        self.slope_width = slope_width
        self.slope_height = slope_height
        self.color = color
        # bounding box for collision check
        self.rect = pygame.Rect(x, y - slope_height, slope_width, slope_height)

    def update(self):
        pass

    def draw(self, screen):
        # For demonstration, we just draw a triangle
        # bottom-left = (x, y)
        # bottom-right = (x + slope_width, y)
        # top-left = (x, y - slope_height)
        points = [(self.x, self.y),
                  (self.x + self.slope_width, self.y),
                  (self.x, self.y - self.slope_height)]
        pygame.draw.polygon(screen, self.color, points)

    def get_slope_y_at_x(self, x_pos):
        """
        Returns the “top” y-position on the slope at a given x_pos.
        If x_pos is outside the slope range, return None.
        """
        if x_pos < self.x or x_pos > (self.x + self.slope_width):
            return None
        # linear interpolation from left to right
        ratio = (x_pos - self.x) / float(self.slope_width)
        # y decreases from y to (y - slope_height) as x goes from x to x + slope_width
        top_y = self.y - (ratio * self.slope_height)
        return top_y

class MovingPlatform(Platform):
    """
    A horizontally moving platform.
    """
    def __init__(self, x, y, w, h, color, x_min, x_max, speed):
        super().__init__(x, y, w, h, color)
        self.x_min = x_min
        self.x_max = x_max
        self.speed = speed
        self.direction = 1

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.x < self.x_min or self.rect.x + self.rect.width > self.x_max:
            self.direction *= -1

class QuestionBlock(Platform):
    """
    Acts like a classic “question block”:
    - If the player hits from below, spawns an item and becomes used.
    """
    def __init__(self, x, y, w, h, color, item_spawn_class=None):
        super().__init__(x, y, w, h, color)
        self.used = False
        self.item_spawn_class = item_spawn_class

    def hit_from_below(self, player):
        if not self.used:
            self.used = True
            self.color = GRAY  # becomes a “used” block
            # spawn an item
            if self.item_spawn_class:
                return self.item_spawn_class(self.rect.centerx, self.rect.top - 16)
        return None

class Mushroom:
    """
    Example power-up item that moves horizontally after it spawns.
    """
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.speed_x = 1
        self.active = True

    def update(self, platforms):
        if not self.active:
            return
        # Move horizontally
        self.rect.x += self.speed_x
        # Simple ground detection
        self.rect.y += 2  # gravity for the mushroom
        for p in platforms:
            if self.rect.colliderect(p.rect):
                # land on top
                if self.speed_x > 0:  # moving right
                    if self.rect.right > p.rect.left and self.rect.bottom > p.rect.top:
                        self.rect.right = p.rect.left
                        self.speed_x *= -1
                else:  # moving left
                    if self.rect.left < p.rect.right and self.rect.bottom > p.rect.top:
                        self.rect.left = p.rect.right
                        self.speed_x *= -1
                # very naive collision just to reverse direction when hitting a platform’s sides
                if (self.rect.bottom > p.rect.top
                        and (self.rect.top < p.rect.top)):
                    self.rect.bottom = p.rect.top
        # keep it on screen
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speed_x *= -1

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, ORANGE, self.rect)

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.direction = 1
        self.speed = 1
        self.active = True

    def update(self):
        if not self.active:
            return
        self.rect.x += self.speed * self.direction
        if self.rect.x < 50 or self.rect.x > 550:
            self.direction *= -1

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, RED, self.rect)

    def stomp(self):
        self.active = False

class Goal:
    def __init__(self, x, y, w, h, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


# ------------- PLAYER CLASS -------------

class Player:
    def __init__(self, x, y, left_key, right_key, run_key=None, jump_keys=None, color=BLUE):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.is_running = False
        self.is_jumping = False
        self.color = color

        # Key bindings
        self.left_key = left_key
        self.right_key = right_key
        self.run_key = run_key
        self.jump_keys = jump_keys or []

        # P-Meter
        self.pmeter = 0
        self.pmeter_full = False

        # Power-up status (basic example)
        self.has_mushroom = False

    def update(self, keys, platforms_and_slopes):
        # Check run key
        self.is_running = (self.run_key is not None) and keys[self.run_key]
        accel = RUN_ACCELERATION if self.is_running else WALK_ACCELERATION
        max_speed = MAX_RUN_SPEED if self.is_running else MAX_WALK_SPEED

        # Horizontal input
        moving_left = keys[self.left_key]
        moving_right = keys[self.right_key]

        if moving_left and not moving_right:
            # accelerate left
            if self.vel_x > 0:
                # changing direction quickly
                self.vel_x -= accel * 2
            else:
                self.vel_x = max(self.vel_x - accel, -max_speed)
        elif moving_right and not moving_left:
            # accelerate right
            if self.vel_x < 0:
                # changing direction quickly
                self.vel_x += accel * 2
            else:
                self.vel_x = min(self.vel_x + accel, max_speed)
        else:
            # friction
            if abs(self.vel_x) > FRICTION:
                self.vel_x -= math.copysign(FRICTION, self.vel_x)
            else:
                self.vel_x = 0

        # Update P-Meter
        # If the player is running in a single direction (left or right), increment pmeter
        if self.is_running and (moving_left ^ moving_right):  # XOR = only one direction
            self.pmeter += 1
            if self.pmeter >= PMETER_MAX:
                self.pmeter = PMETER_MAX
                self.pmeter_full = True
        else:
            # decays if not running
            self.pmeter -= 1
            if self.pmeter < 0:
                self.pmeter = 0
            self.pmeter_full = False

        # Jump
        jump_pressed = any(keys[k] for k in self.jump_keys)
        if jump_pressed and self.on_ground:
            self.vel_y = JUMP_INITIAL_POWER
            self.on_ground = False
            self.is_jumping = True
            if self.color == RED:
                print("Meow!")

        # If jump is released
        if not jump_pressed:
            self.is_jumping = False

        # Apply gravity
        if self.is_jumping and self.vel_y < 0:
            # weaker gravity while rising
            self.vel_y += GRAVITY * JUMP_VARIABLE_GRAVITY_MULTIPLIER
        else:
            # if jump is released while going up quickly, cut it short
            if not self.is_jumping and self.vel_y < JUMP_CUTOFF_VELOCITY:
                self.vel_y = JUMP_CUTOFF_VELOCITY
            self.vel_y += GRAVITY

        # Cap fall speed
        if self.vel_y > TERMINAL_VELOCITY:
            self.vel_y = TERMINAL_VELOCITY

        # Horizontal collision
        self.rect.x += round(self.vel_x)
        self.handle_collisions_x(platforms_and_slopes)

        # Vertical collision
        self.rect.y += round(self.vel_y)
        self.on_ground = False
        self.handle_collisions_y(platforms_and_slopes)

        # Keep on screen
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.vel_x = 0

    def handle_collisions_x(self, platforms_and_slopes):
        for obj in platforms_and_slopes:
            if isinstance(obj, Slope):
                # Only check bounding box collision
                if self.rect.colliderect(obj.rect):
                    # We do a rough fix: if inside slope bounding box, do minimal horizontal push out
                    # We'll correct vertical in handle_collisions_y
                    pass
            else:
                if self.rect.colliderect(obj.rect):
                    if self.vel_x > 0:
                        self.rect.right = obj.rect.left
                        self.vel_x = 0
                    elif self.vel_x < 0:
                        self.rect.left = obj.rect.right
                        self.vel_x = 0

    def handle_collisions_y(self, platforms_and_slopes):
        for obj in platforms_and_slopes:
            if isinstance(obj, Slope):
                # If inside bounding box, check the slope surface
                if self.rect.colliderect(obj.rect):
                    # Get the slope top y at the player's center x
                    slope_top = obj.get_slope_y_at_x(self.rect.centerx)
                    if slope_top is not None:
                        # if the player's feet are below the slope's top
                        if self.rect.bottom >= slope_top:
                            # place them on slope
                            self.rect.bottom = slope_top
                            self.vel_y = 0
                            self.on_ground = True
                            self.is_jumping = False
            else:
                # typical platform
                if self.rect.colliderect(obj.rect):
                    if self.vel_y > 0:  # falling down
                        self.rect.bottom = obj.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                        self.is_jumping = False
                    elif self.vel_y < 0:  # moving up
                        self.rect.top = obj.rect.bottom
                        self.vel_y = 0

    def collect_powerup(self, item):
        """
        Example: if it’s a mushroom, set has_mushroom to True, which
        can let you do bigger jumps, etc.
        """
        if isinstance(item, Mushroom):
            item.active = False
            self.has_mushroom = True
            print("Player got a mushroom!")

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        # Show a simple P-meter bar above the player
        meter_ratio = self.pmeter / PMETER_MAX
        meter_width = 32
        pygame.draw.rect(screen, WHITE, (self.rect.x, self.rect.y - 10, meter_width, 5))
        pygame.draw.rect(screen, ORANGE, (self.rect.x, self.rect.y - 10, meter_width * meter_ratio, 5))

    def reset(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.is_jumping = False
        self.pmeter = 0
        self.pmeter_full = False

# ------------- SETUP & LEVEL DATA -------------

def get_level_data(world):
    bg_color, platform_color = world_colors.get(world, (BLACK, WHITE))

    # Example level with a slope, moving platform, question block, etc.
    objects = [
        Platform(0, 350, 600, 50, platform_color),   # ground
        Platform(150, 270, 80, 20, platform_color),  # standard block platform
        MovingPlatform(250, 220, 100, 20, platform_color, x_min=200, x_max=400, speed=2),
        Slope(400, 350, 100, 70, platform_color),    # a slope
        QuestionBlock(100, 250, 20, 20, YELLOW, item_spawn_class=Mushroom),
    ]

    enemies = [
        Enemy(320, 318),
        Enemy(500, 318),
    ]

    goal = Goal(550, 318, 20, 32, YELLOW)
    return bg_color, objects, enemies, goal

def setup():
    try:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SMB3-Inspired Engine")
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 36)
        return screen, clock, font
    except Exception as e:
        print(f"Pygame setup failed: {e}")
        sys.exit(1)

# ------------- MAIN LOOP (ASYNC) -------------

async def main():
    screen, clock, font = setup()

    world_buttons = [
        {'rect': pygame.Rect(50, 50, 100, 50),  'world': 1},
        {'rect': pygame.Rect(200, 50, 100, 50), 'world': 2},
        {'rect': pygame.Rect(350, 50, 100, 50), 'world': 3},
        {'rect': pygame.Rect(500, 50, 100, 50), 'world': 4},
        {'rect': pygame.Rect(50, 150, 100, 50), 'world': 5},
        {'rect': pygame.Rect(200, 150, 100, 50),'world': 6},
        {'rect': pygame.Rect(350, 150, 100, 50),'world': 7},
        {'rect': pygame.Rect(500, 150, 100, 50),'world': 8},
    ]

    current_state = 'overworld'
    current_world = None
    players = []
    objects = []
    enemies = []
    goal = None
    bg_color = BLACK
    message = ""
    message_timer = 0
    player_start_pos = (50, 300)

    # A list of items in the level (e.g., mushrooms after they spawn)
    items = []

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
                for button in world_buttons:
                    if button['rect'].collidepoint(event.pos):
                        current_world = button['world']
                        bg_color, objects, enemies, goal = get_level_data(current_world)
                        items = []
                        # Example: 2 players
                        players = [
                            Player(player_start_pos[0], player_start_pos[1],
                                   pygame.K_LEFT, pygame.K_RIGHT,
                                   run_key=pygame.K_RSHIFT,
                                   jump_keys=[pygame.K_UP], color=BLUE),
                            Player(player_start_pos[0]+50, player_start_pos[1],
                                   pygame.K_a, pygame.K_d,
                                   run_key=pygame.K_LSHIFT,
                                   jump_keys=[pygame.K_w], color=RED)
                        ]
                        # Reactivate enemies
                        for e in enemies:
                            e.active = True

                        current_state = 'level'
                        message = f"World {current_world} Start!"
                        message_timer = FPS * 2
                        break

        if current_state == 'overworld':
            screen.fill(BLACK)
            for button in world_buttons:
                pygame.draw.rect(screen, WHITE, button['rect'])
                text = font.render(f"World {button['world']}", True, BLACK)
                screen.blit(text, (button['rect'].x+10, button['rect'].y+10))

            if message_timer > 0:
                txt = font.render(message, True, WHITE)
                screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
                message_timer -= 1

        elif current_state == 'level':
            # Update platforms (moving ones)
            for obj in objects:
                obj.update()

            # Keyboard input
            keys = pygame.key.get_pressed()

            # Update players
            for p in players:
                p.update(keys, objects)

            # Update enemies
            for e in enemies:
                e.update()

            # Update items (like mushrooms)
            for itm in items:
                itm.update(objects)

            # Player-Enemy collisions
            for p in players:
                died = False
                for e in enemies:
                    if e.active and p.rect.colliderect(e.rect):
                        # Stomp check
                        stomp_condition = (p.vel_y > 0 and p.rect.bottom <= e.rect.top + ENEMY_STOMP_TOLERANCE)
                        if stomp_condition:
                            e.stomp()
                            p.vel_y = ENEMY_STOMP_BOUNCE
                            p.on_ground = False
                        else:
                            died = True
                            break
                # Fall off the bottom
                if p.rect.top > HEIGHT:
                    died = True

                if died:
                    # Reset only that player
                    p.reset(*player_start_pos)
                    message = "Ouch! Try Again!"
                    message_timer = FPS * 2

            # Player-Item collisions
            for p in players:
                for itm in items:
                    if itm.active and p.rect.colliderect(itm.rect):
                        p.collect_powerup(itm)

            # Player-QuestionBlock collisions from below
            # (Check each block if we came from below)
            for p in players:
                if p.vel_y < 0:  # moving up
                    for obj in objects:
                        if isinstance(obj, QuestionBlock) and not obj.used:
                            # We see if the player's head is inside the block
                            # A more accurate approach: check if player's top is near block bottom
                            if p.rect.colliderect(obj.rect):
                                # "hit" the block
                                spawned = obj.hit_from_below(p)
                                if spawned:
                                    items.append(spawned)
                                # adjust player's head so they don't get stuck
                                p.rect.top = obj.rect.bottom
                                p.vel_y = 0

            # Check goal
            if any(p.rect.colliderect(goal.rect) for p in players):
                current_state = 'overworld'
                message = f"World {current_world} Cleared!"
                message_timer = FPS * 2

            # --- RENDER LEVEL ---
            screen.fill(bg_color)
            for obj in objects:
                obj.draw(screen)
            for e in enemies:
                e.draw(screen)
            for itm in items:
                itm.draw(screen)
            goal.draw(screen)
            for p in players:
                p.draw(screen)

            # Show any message
            if message_timer > 0:
                txt = font.render(message, True, WHITE)
                screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
                message_timer -= 1

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

# ------------- EMSCRIPTEN / NORMAL EXEC -------------
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
