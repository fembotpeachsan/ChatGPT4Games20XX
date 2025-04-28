import asyncio
import pygame
import sys
import math

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
        self.start_x = x
        self.start_y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.is_running = False
        self.is_jumping = False
        self.left_key = left_key
        self.right_key = right_key
        self.run_key = run_key
        self.jump_keys = jump_keys or []
        self.color = color

    def update(self, keys, platforms):
        # Determine if running key is held
        self.is_running = keys[self.run_key] if self.run_key else False
        accel = RUN_ACCELERATION if self.is_running else WALK_ACCELERATION
        max_speed = MAX_RUN_SPEED if self.is_running else MAX_WALK_SPEED

        # Horizontal movement
        if keys[self.left_key]:
            self.vel_x = max(self.vel_x - accel, -max_speed)
        elif keys[self.right_key]:
            self.vel_x = min(self.vel_x + accel, max_speed)
        else:
            # Apply friction if no horizontal input
            if abs(self.vel_x) > FRICTION:
                self.vel_x -= math.copysign(FRICTION, self.vel_x)
            else:
                self.vel_x = 0

        # Jump logic
        if any(keys[k] for k in self.jump_keys) and self.on_ground:
            self.vel_y = JUMP_INITIAL_POWER
            self.on_ground = False
            self.is_jumping = True
        if not any(keys[k] for k in self.jump_keys):
            self.is_jumping = False

        # Gravity handling
        if self.is_jumping and self.vel_y < 0:
            # Variable jump height
            self.vel_y += GRAVITY * JUMP_VARIABLE_GRAVITY_MULTIPLIER
        else:
            # Normal gravity
            if not self.is_jumping and self.vel_y < JUMP_CUTOFF_VELOCITY:
                self.vel_y = JUMP_CUTOFF_VELOCITY
            self.vel_y += GRAVITY

        # Horizontal collision
        self.rect.x += round(self.vel_x)
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_x > 0:
                    self.rect.right = plat.rect.left
                elif self.vel_x < 0:
                    self.rect.left = plat.rect.right
                self.vel_x = 0

        # Vertical collision
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

        # Screen boundary collision
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.vel_x = 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
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
    platforms = [
        Platform(0, 350, 600, 50, plat_color),
        Platform(150, 270, 120, 20, plat_color),
        Platform(50, 150, 80, 20, plat_color),
        MovingPlatform(250, 220, 100, 20, plat_color, x_min=200, x_max=400, speed=2)
    ]
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
                        
                        # ----------------------------------
                        #  Change the controls to arrow keys
                        #    ←: move left, →: move right
                        #    Right Shift: run
                        #    ↑ or Space: jump
                        # ----------------------------------
                        players = [
                            Player(
                                player_start[0], player_start[1],
                                left_key=pygame.K_LEFT,
                                right_key=pygame.K_RIGHT,
                                run_key=pygame.K_RSHIFT,
                                jump_keys=[pygame.K_UP, pygame.K_SPACE],
                                color=MAGENTA  # A more visible color
                            )
                        ]
                        
                        # Reset enemies
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
                screen.blit(txt, (btn['rect'].x + 10, btn['rect'].y + 10))

            if message_timer > 0:
                txt = font.render(message, True, WHITE)
                screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2))
                message_timer -= 1

        elif current_state == 'level':
            for plat in platforms:
                if hasattr(plat, 'update'):
                    plat.update()

            keys = pygame.key.get_pressed()
            for p in players:
                p.update(keys, platforms)

            active_enemies = [e for e in enemies if e.active]
            for e in active_enemies:
                e.update()

            # Check collisions & death
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
                # If player falls off-screen
                if p.rect.top > HEIGHT:
                    died = True
                if died:
                    p.reset()
                    message = "Ouch! Try Again!"
                    message_timer = FPS * 2

            # Check if goal reached
            if any(p.rect.colliderect(goal.rect) for p in players):
                current_state = 'overworld'
                message = f"World {current_world} Cleared!"
                message_timer = FPS * 2

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
                screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2))
                message_timer -= 1

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Game terminated by user.")
    finally:
        pygame.quit()
        sys.exit(0)
