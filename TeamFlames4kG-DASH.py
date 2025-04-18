import pygame
import json
import os
import time
import base64
import math
# Initialize Pygame
pygame.init()

# Display setup
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash 2.4")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
BLUE = (65, 105, 225)
GREEN = (34, 139, 34)
GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)
CYAN = (0, 255, 255)
YELLOW = (255, 215, 0)

# Fonts
FONT = pygame.font.Font(None, 24)
TITLE_FONT = pygame.font.Font(None, 48)

# Player properties
PLAYER_SIZE = 40
PLAYER_X = 100
PLAYER_Y_START = HEIGHT - PLAYER_SIZE - 60
GRAVITY = 0.8
JUMP_HEIGHT = -15
DOUBLE_JUMP_HEIGHT = -12
JUMP_PAD_HEIGHT = -20

# Ground properties
GROUND_HEIGHT = 60

# Game state
default_level = []
level = []
scroll_speed = 5
player_jumps = 0
dash_speed_multiplier = 1
dash_duration = 0
dash_start_time = 0
score = 0

# Placeholder images
BLOCK_IMG = pygame.Surface((40, 40)); BLOCK_IMG.fill(WHITE)
SPIKE_IMG = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.polygon(SPIKE_IMG, RED, [(0, 40), (20, 0), (40, 40)])
MOVING_PLATFORM_IMG = pygame.Surface((80, 20)); MOVING_PLATFORM_IMG.fill(GREEN)
PORTAL_IMG = pygame.Surface((40, 40)); PORTAL_IMG.fill(YELLOW)
DASH_ORB_IMG = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.circle(DASH_ORB_IMG, CYAN, (15, 15), 15)
JUMP_PAD_IMG = pygame.Surface((40, 20), pygame.SRCALPHA)
pygame.draw.rect(JUMP_PAD_IMG, YELLOW, (0, 0, 40, 20))
pygame.draw.polygon(JUMP_PAD_IMG, RED, [(0, 20), (20, 0), (40, 20)])

# Sample Levels
LEVELS = {
    "1-1": [
        {"type": "block", "x": 200, "y": 400},
        {"type": "block", "x": 240, "y": 400},
        {"type": "moving_platform", "x": 280, "y": 350, "direction": "horizontal", "move_range": 100},
        {"type": "spike", "x": 320, "y": 460},
        {"type": "block", "x": 360, "y": 400},
        {"type": "block", "x": 400, "y": 400},
        {"type": "spike", "x": 440, "y": 460},
        {"type": "portal", "x": 500, "y": 400},
        {"type": "dash_orb", "x": 600, "y": 500},
        {"type": "jump_pad", "x": 700, "y": 500}
    ]
}

# Sharing Functions
def encode_level(data):
    return base64.urlsafe_b64encode(json.dumps(data).encode()).decode()

def decode_level(code):
    try:
        return json.loads(base64.urlsafe_b64decode(code.encode()).decode())
    except:
        return None

# Game Loops
def load_level(data):
    global level
    level = data.copy()


def draw_player(x, y):
    pygame.draw.rect(screen, BLUE, (x, y, PLAYER_SIZE, PLAYER_SIZE))


def draw_level(offset):
    for obj in level[:]:
        x = obj['x'] - offset
        y = obj['y']
        t = obj['type']
        if t == 'block':
            screen.blit(BLOCK_IMG, (x, y))
        elif t == 'spike':
            screen.blit(SPIKE_IMG, (x, y))
        elif t == 'moving_platform':
            dir = obj.get('direction', 'horizontal')
            rng = obj.get('move_range', 100)
            spd = obj.get('speed', 2)
            if 'start_time' not in obj:
                obj['start_time'] = time.time()
            elapsed = time.time() - obj['start_time']
            if dir == 'horizontal':
                x = obj['x'] + rng * math.sin(elapsed * spd)
            else:
                y = obj['y'] + rng * math.sin(elapsed * spd)
            screen.blit(MOVING_PLATFORM_IMG, (x - offset, y))
        elif t == 'portal':
            screen.blit(PORTAL_IMG, (x, y))
        elif t == 'dash_orb':
            screen.blit(DASH_ORB_IMG, (x, y))
        elif t == 'jump_pad':
            screen.blit(JUMP_PAD_IMG, (x, y))


def game_loop():
    global score, player_jumps, dash_speed_multiplier, dash_duration, dash_start_time
    y = PLAYER_Y_START
    v = 0
    on_ground = True
    offset = 0
    score = 0
    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                if on_ground:
                    v = JUMP_HEIGHT
                    on_ground = False
                    player_jumps = 1
                elif player_jumps < 1:
                    v = DOUBLE_JUMP_HEIGHT
                    player_jumps += 1

        # Dash expiration
        if dash_speed_multiplier > 1 and time.time() - dash_start_time > dash_duration:
            dash_speed_multiplier = 1

        v += GRAVITY
        y += v

        # Ground clamp
        if y >= HEIGHT - PLAYER_SIZE - GROUND_HEIGHT:
            y = HEIGHT - PLAYER_SIZE - GROUND_HEIGHT
            v = 0
            on_ground = True
            player_jumps = 0

        player_rect = pygame.Rect(PLAYER_X, y, PLAYER_SIZE, PLAYER_SIZE)

        # Collisions
        for obj in level[:]:
            obj_rect = pygame.Rect(obj['x'] - offset, obj['y'], 40, 40)
            if player_rect.colliderect(obj_rect):
                if obj['type'] == 'spike':
                    print(f"Game Over! Score: {score}")
                    return True
                elif obj['type'] == 'portal':
                    print("Portal Activated!")
                elif obj['type'] == 'dash_orb':
                    dash_speed_multiplier = 2
                    dash_duration = 3
                    dash_start_time = time.time()
                    level.remove(obj)
                elif obj['type'] == 'jump_pad':
                    v = JUMP_PAD_HEIGHT
                    on_ground = False
                    player_jumps = 1
                    level.remove(obj)

        score += 1
        offset += scroll_speed * dash_speed_multiplier * dt

        screen.fill(BLACK)
        draw_level(offset)
        draw_player(PLAYER_X, y)
        screen.blit(FONT.render(f"Score: {int(score)}", True, WHITE), (10, 10))
        pygame.display.flip()

        if score >= 200:
            print("Level Complete!")
            return True


def main_menu():
    class Button:
        def __init__(self, text, pos):
            self.text_surf = FONT.render(text, True, WHITE)
            self.rect = pygame.Rect(pos[0], pos[1], 200, 50)
        def draw(self):
            pygame.draw.rect(screen, LIGHT_GRAY, self.rect)
            screen.blit(self.text_surf, (self.rect.x + 10, self.rect.y + 15))
        def clicked(self, mpos):
            return self.rect.collidepoint(mpos)

    buttons = [
        Button("Play", (540, 250)),
        Button("Load Code", (540, 320)),
        Button("Quit", (540, 390))
    ]

    while True:
        screen.fill(BLACK)
        screen.blit(TITLE_FONT.render("Geometry Dash 2.4", True, WHITE), (440, 100))
        for b in buttons:
            b.draw()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if buttons[0].clicked(e.pos):
                    load_level(LEVELS["1-1"]);
                    game_loop()
                elif buttons[1].clicked(e.pos):
                    code = input("Enter level code: ")
                    data = decode_level(code) or default_level
                    load_level(data)
                    game_loop()
                elif buttons[2].clicked(e.pos):
                    return False
        pygame.display.flip()


if __name__ == '__main__':
    if not os.path.exists('levels'):
        os.makedirs('levels')
    main_menu()
    pygame.quit()
## [C ] - Team Flames [20XX]
