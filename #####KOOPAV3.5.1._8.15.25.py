import pygame
import sys
import math
import random
from pygame.locals import *

# ================================
# Constants
# ================================
SCALE = 2
TILE = 16
WIDTH = int(300 * SCALE)
HEIGHT = int(200 * SCALE)
FPS = 60

# ================================
# NES-like Palette
# ================================
NES_PALETTE = [
    (84, 84, 84), (0, 30, 116), (8, 16, 144), (48, 0, 136),
    (68, 0, 100), (92, 0, 48), (84, 4, 0), (60, 24, 0),
    (32, 42, 0), (8, 58, 0), (0, 64, 0), (0, 60, 0),
    (0, 50, 60), (0, 0, 0), (152, 150, 152), (8, 76, 196),
    (48, 50, 236), (92, 30, 228), (136, 20, 176), (160, 20, 100),
    (152, 34, 32), (120, 60, 0), (84, 90, 0), (40, 114, 0),
    (8, 124, 0), (0, 118, 40), (0, 102, 120), (0, 0, 0),
    (236, 238, 236), (76, 154, 236), (120, 124, 236), (176, 98, 236),
    (228, 84, 236), (236, 88, 180), (236, 106, 100), (212, 136, 32),
    (160, 170, 0), (116, 196, 0), (76, 208, 32), (56, 204, 108),
    (56, 180, 204), (60, 60, 60), (0, 0, 0), (0, 0, 0)
]

# ================================
# Tile/Entity symbol definitions
# ================================
# Terrain tiles (drawn by TileMap)
TERRAIN_TILES = set(['G','S','D','I','B','P','T','?','F','L','C','W','Q','/'])
# Tiles that block movement (colliders)
COLLIDABLE_TILES = set(['G','S','D','I','B','P','T','?','L','C','W','Q'])
# Entity markers embedded in level strings (parsed by LevelScene)
ENTITY_MARKERS = {
    'E': 'start',   # player Entry
    'g': 'goomba',
    'k': 'koopa',   # currently uses Goomba placeholder
    'p': 'piranha',
    'c': 'cheep',
    'X': 'boss',
}
# Item markers (embedded in level strings -> converted to Item objects)
ITEM_MARKERS = {
    'O': 'coin',
    'm': 'mushroom',
    'f': 'flower',
    'r': 'star',
}

# ================================
# Game State
# ================================
class GameState:
    def __init__(self):
        self.slot = 0
        self.progress = [
            {"world": "1-1", "completed": set(), "powerups": set(), "boss_defeated": False},
            {"world": "1-1", "completed": set(), "powerups": set(), "boss_defeated": False},
            {"world": "1-1", "completed": set(), "powerups": set(), "boss_defeated": False}
        ]
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.world = "1-1"
        self.time = 300
        self.mario_size = "small"  # "small", "big", "fire"
        self.powerup_active = False
        self.powerup_type = None
        self.paused = False

state = GameState()

# ================================
# Scene management
# ================================
SCENES = []
def push(scene):
    SCENES.append(scene)
    return scene

def pop():
    if SCENES:
        return SCENES.pop()
    return None

class Scene:
    def handle(self, events, keys): ...
    def update(self, dt): ...
    def draw(self, surf): ...

# ================================
# World themes
# ================================
WORLD_THEMES = {
    "1": {"name": "Mushroom Plains", "bg": 27, "ground": 20, "block": 21, "enemies": ["G", "K"]},
    "2": {"name": "Sandy Dunes", "bg": 26, "ground": 33, "block": 21, "enemies": ["G", "P"]},
    "3": {"name": "Coral Cove", "bg": 29, "ground": 24, "block": 25, "enemies": ["C", "G"]},
    "4": {"name": "Frozen Falls", "bg": 31, "ground": 39, "block": 38, "enemies": ["G", "C"]},
    "5": {"name": "Cloudy Heights", "bg": 27, "ground": 31, "block": 39, "enemies": ["G", "P"]},
    "6": {"name": "Rocky Mountains", "bg": 21, "ground": 33, "block": 21, "enemies": ["K", "P"]},
    "7": {"name": "Twisted Forest", "bg": 13, "ground": 14, "block": 15, "enemies": ["G", "K"]},
    "8": {"name": "Bowser's Domain", "bg": 1, "ground": 33, "block": 21, "enemies": ["K", "G"]}
}

# ================================
# Level Generation
# ================================
def generate_level_data():
    """Generate 32 levels. Returns: dict[level_id] -> (level_rows, theme)"""
    levels = {}

    # Level types for each world
    level_types = {
        "1": ["plains", "plains", "plains", "castle"],
        "2": ["desert", "desert", "desert", "castle"],
        "3": ["beach", "underwater", "coral", "castle"],
        "4": ["ice", "ice_cave", "snow,ice", "castle"],
        "5": ["clouds", "sky", "airship", "castle"],
        "6": ["caves", "mountains", "mine", "castle"],
        "7": ["forest", "swamp", "haunted", "castle"],
        "8": ["volcano", "lava", "fortress", "castle"]
    }

    # Map theme enemy codes to our lower-case markers (ignore unknown -> goomba)
    enemy_map = {'G':'g','K':'k','P':'p','C':'c'}

    for world_num in range(1, 8+1):
        w = str(world_num)
        for level_num in range(1, 4+1):  # 4 levels per world
            level_id = f"{w}-{level_num}"
            ltype = level_types[w][level_num-1]

            # Build empty level grid
            level = []
            level_height = 20
            width_cols = 100
            for _ in range(level_height):
                level.append(" " * width_cols)

            theme = WORLD_THEMES[w]

            # ========== TERRAIN ==========
            if ltype in ("plains","beach","caves","mountains","mine","forest","swamp","haunted","clouds","sky","airship","volcano","lava","fortress","snow,ice","ice_cave"):
                # default ground-style layout
                for y in range(15, level_height):
                    if y == 15:
                        level[y] = "G" * width_cols
                    else:
                        level[y] = "B" * width_cols

            if ltype == "plains":
                # platforms
                for i in range(5):
                    py = random.randint(8, 12)
                    px = random.randint(10 + i*20, 15 + i*20)
                    ln = random.randint(4, 8)
                    row = list(level[py])
                    for j in range(min(ln, width_cols - (px))):
                        row[px+j] = 'P'
                    level[py] = "".join(row)

                # pipes
                for i in range(2):
                    px = random.randint(20 + i*30, 25 + i*30)
                    ph = random.randint(2, 4)
                    for j in range(ph):
                        for dx in (0,1):
                            y = 19 - j
                            if 0 <= px+dx < width_cols:
                                row = list(level[y])
                                row[px+dx] = 'T'
                                level[y] = "".join(row)

                # bricks / question
                for i in range(8):
                    by = random.randint(5, 10)
                    bx = random.randint(5 + i*10, 8 + i*10)
                    ch = '?' if random.random() > 0.5 else 'B'
                    row = list(level[by])
                    if 0 <= bx < width_cols:
                        row[bx] = ch
                        level[by] = "".join(row)

            elif ltype == "desert":
                for y in range(15, level_height):
                    level[y] = ("S" if y == 15 else "D") * width_cols

                # pyramids
                for px in (20, 60):
                    height = 5
                    width = 1
                    for y in range(15-height, 15):
                        row = list(level[y])
                        start = max(0, px - width)
                        end = min(width_cols, px + width + 1)
                        for x in range(start, end):
                            row[x] = 'P'
                        level[y] = "".join(row)
                        width += 1

                # quicksand pits
                for i in range(3):
                    qs_x = random.randint(30 + i*20, 40 + i*20)
                    qs_w = random.randint(3, 6)
                    row = list(level[15])
                    for x in range(qs_x, min(qs_x+qs_w, width_cols)):
                        row[x] = 'Q'
                    level[15] = "".join(row)

                # cacti
                for i in range(4):
                    cx = random.randint(10 + i*20, 15 + i*20)
                    ch = random.randint(3, 5)
                    for j in range(ch):
                        y = 15 - j
                        if 0 <= cx < width_cols:
                            row = list(level[y])
                            row[cx] = 'C'
                            level[y] = "".join(row)

            elif ltype == "underwater":
                # floor
                for y in range(15, level_height):
                    level[y] = ("G" if y == 15 else "B") * width_cols
                # seaweed
                for i in range(8):
                    wx = random.randint(5 + i*12, 10 + i*12)
                    wh = random.randint(3, 6)
                    for j in range(wh):
                        y = 15 - j
                        if 0 <= wx < width_cols:
                            row = list(level[y])
                            row[wx] = 'W'
                            level[y] = "".join(row)
                # coral
                for i in range(5):
                    cx = random.randint(15 + i*15, 20 + i*15)
                    cy = 14
                    if 0 <= cx < width_cols:
                        row = list(level[cy])
                        row[cx] = 'C'
                        level[cy] = "".join(row)

            elif ltype.startswith("ice"):
                for y in range(15, level_height):
                    level[y] = ("I" if y == 15 else "B") * width_cols
                # blocks
                for i in range(6):
                    by = random.randint(5, 10)
                    bx = random.randint(5 + i*15, 10 + i*15)
                    if 0 <= bx < width_cols:
                        row = list(level[by])
                        row[bx] = 'B'
                        level[by] = "".join(row)
                # slopes (visual only)
                for sx in (30, 70):
                    h = 3
                    for y in range(15-h, 15):
                        row = list(level[y])
                        span = min(15-y, width_cols - sx)
                        if span > 0:
                            for dx in range(span):
                                row[sx+dx] = '/'
                            level[y] = "".join(row)

            elif ltype == "castle":
                for y in range(15, level_height):
                    level[y] = ("G" if y == 15 else "B") * width_cols
                # lava pits
                for i in range(3):
                    pit_x = random.randint(20 + i*25, 30 + i*25)
                    pit_w = random.randint(4, 8)
                    for x in range(pit_x, min(pit_x+pit_w, width_cols)):
                        for py in (15, 16 if 16 < level_height else 15):
                            row = list(level[py])
                            row[x] = 'L'
                            level[py] = "".join(row)
                # brick structures
                for i in range(5):
                    sx = random.randint(10 + i*15, 15 + i*15)
                    sh = random.randint(4, 8)
                    sw = random.randint(2, 4)
                    for y in range(15 - sh, 15):
                        row = list(level[y])
                        for dx in range(sw):
                            x = sx + dx
                            if 0 <= x < width_cols:
                                row[x] = 'B'
                        level[y] = "".join(row)
                # platforms
                for i in range(3):
                    py = random.randint(8, 12)
                    px = random.randint(20 + i*25, 25 + i*25)
                    ln = random.randint(3, 5)
                    row = list(level[py])
                    for j in range(min(ln, width_cols - px)):
                        row[px+j] = 'P'
                    level[py] = "".join(row)
                # question blocks
                for i in range(4):
                    by = random.randint(5, 10)
                    bx = random.randint(10 + i*20, 15 + i*20)
                    if 0 <= bx < width_cols:
                        row = list(level[by])
                        row[bx] = '?'
                        level[by] = "".join(row)
                # boss marker
                row = list(level[10])
                row[min(width_cols-1, 90)] = 'X'
                level[10] = "".join(row)

            # ========== PLAYER START & FLAG ==========
            # Start marker 'E' (avoid 'S' which is also sand)
            row = list(level[14])
            row[5] = 'E'
            level[14] = "".join(row)

            # Flag 'F' near end
            row = list(level[14])
            row[min(width_cols-1, 95)] = 'F'
            level[14] = "".join(row)

            # ========== ENEMIES ==========
            # Place 5 enemies using recognized set
            allowed = [enemy_map.get(e, 'g') for e in theme['enemies']]
            if not allowed:
                allowed = ['g']
            for i in range(5):
                ex = random.randint(20 + i*15, 25 + i*15)
                ey = 14
                et = random.choice(allowed)
                if 0 <= ex < width_cols:
                    row = list(level[ey])
                    row[ex] = et
                    level[ey] = "".join(row)

            # ========== COINS ==========
            for i in range(10):
                cx = random.randint(10 + i*8, 15 + i*8)
                cy = random.randint(5, 12)
                if 0 <= cx < width_cols:
                    row = list(level[cy])
                    row[cx] = 'O'
                    level[cy] = "".join(row)

            levels[level_id] = (level, theme)

    return levels

LEVELS = generate_level_data()

# ================================
# Create thumbnails (tiny preview)
# ================================
THUMBNAILS = {}
def _build_thumbnails():
    for level_id, (level_rows, theme) in LEVELS.items():
        thumb = pygame.Surface((32, 24))
        thumb.fill(NES_PALETTE[theme["bg"]])
        # Draw a simple representation of mid rows
        base_rows = level_rows[10:14]
        for y, row in enumerate(base_rows):
            for x, ch in enumerate(row[::3]):  # sample every 3rd column
                if ch in ("G", "S", "D", "I", "B", "P", "T", "L"):
                    thumb.set_at((x, y+10), NES_PALETTE[theme["ground"]])
                elif ch in ("?",):
                    thumb.set_at((x, y+10), NES_PALETTE[theme["block"]])
        THUMBNAILS[level_id] = thumb

# ================================
# Entity classes
# ================================
class Entity:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.width = TILE
        self.height = TILE
        self.on_ground = False
        self.facing_right = True
        self.active = True

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))

    def check_collision(self, other):
        return self.get_rect().colliderect(other.get_rect())

    def update(self, colliders, dt):
        """Axis-separated collision resolution to avoid tunneling & overlap bugs."""
        # Gravity
        if not self.on_ground:
            self.vy += 0.5 * dt * 60

        # --- Horizontal ---
        self.x += self.vx * dt * 60
        rect = self.get_rect()
        for solid in colliders:
            if rect.colliderect(solid):
                if self.vx > 0:  # moving right
                    self.x = solid.left - self.width
                elif self.vx < 0:  # moving left
                    self.x = solid.right
                self.vx = 0
                rect = self.get_rect()  # refresh

        # --- Vertical ---
        self.on_ground = False
        self.y += self.vy * dt * 60
        rect = self.get_rect()
        for solid in colliders:
            if rect.colliderect(solid):
                if self.vy > 0:  # falling
                    self.y = solid.top - self.height
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:  # moving up
                    self.y = solid.bottom
                    self.vy = 0
                rect = self.get_rect()

    def draw(self, surf, cam):
        pass

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.jump_power = -5
        self.move_speed = 2.0
        self.run_speed = 3.5
        self.invincible = 0.0
        self.animation_frame = 0
        self.walk_timer = 0.0
        self.fireballs = []
        self.fire_cooldown = 0.0
        self.star_timer = 0.0
        self.underwater = False

    def update(self, colliders, dt, enemies, items):
        keys = pygame.key.get_pressed()

        # Speed (run if shift)
        current_speed = self.run_speed if keys[K_LSHIFT] else self.move_speed

        # Horizontal input
        self.vx = 0.0
        if keys[K_LEFT]:
            self.vx = -current_speed
            self.facing_right = False
        if keys[K_RIGHT]:
            self.vx = current_speed
            self.facing_right = True

        # Jump
        if keys[K_SPACE] and self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False

        # Fireballs
        if keys[K_z] and state.mario_size == "fire" and self.fire_cooldown <= 0:
            self.fireballs.append(Fireball(self.x, self.y, self.facing_right))
            self.fire_cooldown = 0.5
        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt

        # Update fireballs
        for fb in self.fireballs[:]:
            fb.update(colliders, dt)
            if not fb.active:
                self.fireballs.remove(fb)

        # Star / invincibility timers
        if self.star_timer > 0:
            self.star_timer -= dt
            if self.star_timer <= 0:
                self.invincible = 0
        if self.invincible > 0:
            self.invincible -= dt

        # Walk animation
        if self.vx != 0:
            self.walk_timer += dt
            if self.walk_timer > 0.1:
                self.walk_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 3
        else:
            self.animation_frame = 0

        # Underwater damping
        if self.underwater:
            self.vy *= 0.95
            self.vx *= 0.9

        # Physics & collisions
        super().update(colliders, dt)

        # Interactions: enemies
        for enemy in enemies:
            if enemy.active and self.check_collision(enemy):
                if self.vy > 0 and self.y + self.height - 5 < enemy.y:
                    # stomp
                    enemy.active = False
                    self.vy = self.jump_power / 2
                    state.score += 100
                elif self.invincible <= 0 and self.star_timer <= 0:
                    # damage
                    if state.mario_size == "fire":
                        state.mario_size = "big"
                        self.invincible = 2
                    elif state.mario_size == "big":
                        state.mario_size = "small"
                        self.invincible = 2
                    else:
                        state.lives -= 1
                        if state.lives <= 0:
                            push(GameOverScene())
                        else:
                            self.x, self.y = 50, 100
                            self.vx = self.vy = 0

        # Interactions: items
        for item in items[:]:
            if pygame.Rect(item.x, item.y, TILE, TILE).colliderect(self.get_rect()):
                if item.type == "mushroom":
                    if state.mario_size == "small":
                        state.mario_size = "big"
                    state.progress[state.slot]["powerups"].add("mushroom")
                    state.score += 1000
                elif item.type == "flower":
                    state.mario_size = "fire"
                    state.progress[state.slot]["powerups"].add("flower")
                    state.score += 1000
                elif item.type == "star":
                    self.star_timer = 10
                    self.invincible = 10
                    state.progress[state.slot]["powerups"].add("star")
                    state.score += 1000
                elif item.type == "coin":
                    state.coins = min(99, state.coins + 1)
                    state.score += 100
                items.remove(item)

    def draw(self, surf, cam):
        if self.invincible > 0 and int(self.invincible * 10) % 2 == 0:
            return  # blink during invincibility

        x = int(self.x - cam)
        y = int(self.y)

        color = NES_PALETTE[33]  # red-ish
        skin = NES_PALETTE[39]

        if state.mario_size == "fire":
            color = NES_PALETTE[31]

        if state.mario_size in ("big", "fire"):
            pygame.draw.rect(surf, color, (x+4, y+8, 8, 16))   # body
            pygame.draw.rect(surf, skin, (x+4, y+4, 8, 4))     # head
            pygame.draw.rect(surf, color, (x+2, y, 12, 4))     # hat
            arm_offset = 2 if (self.animation_frame == 1 and self.vx != 0 and self.facing_right) else 0
            pygame.draw.rect(surf, skin, (x+arm_offset, y+10, 4, 6))        # left arm
            pygame.draw.rect(surf, skin, (x+12-arm_offset, y+10, 4, 6))     # right arm
            leg_offset = 2 if (self.animation_frame == 2 and self.vx != 0 and self.facing_right) else 0
            pygame.draw.rect(surf, NES_PALETTE[21], (x+2, y+24, 4, 8))      # left leg
            pygame.draw.rect(surf, NES_PALETTE[21], (x+10, y+24-leg_offset, 4, 8+leg_offset))  # right leg
            if state.mario_size == "fire":
                pygame.draw.rect(surf, NES_PALETTE[31], (x+4, y+8, 8, 2))
                pygame.draw.rect(surf, NES_PALETTE[31], (x+4, y+18, 8, 2))
        else:
            pygame.draw.rect(surf, color, (x+4, y+8, 8, 8))    # body
            pygame.draw.rect(surf, skin, (x+4, y, 8, 8))       # head
            pygame.draw.rect(surf, color, (x+2, y, 12, 2))     # hat

        for fb in self.fireballs:
            fb.draw(surf, cam)

class Fireball:
    def __init__(self, x, y, right):
        self.x = x
        self.y = y
        self.vx = 6 if right else -6
        self.vy = 0.0
        self.width = 8
        self.height = 8
        self.active = True
        self.timer = 1.0

    def update(self, colliders, dt):
        self.x += self.vx * dt * 60
        self.vy += 0.2 * dt * 60
        self.y += self.vy * dt * 60
        self.timer -= dt
        if self.timer <= 0:
            self.active = False
        r = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        for solid in colliders:
            if r.colliderect(solid):
                self.active = False
                break

    def draw(self, surf, cam):
        x = int(self.x - cam)
        y = int(self.y)
        pygame.draw.circle(surf, NES_PALETTE[33], (x+4, y+4), 4)
        pygame.draw.circle(surf, NES_PALETTE[39], (x+4, y+4), 2)

class Goomba(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vx = -0.5
        self.animation_frame = 0
        self.walk_timer = 0.0

    def update(self, colliders, dt):
        # Edge turn-around: check one pixel ahead+below
        if self.on_ground:
            ahead_x = self.x + (self.width if self.vx > 0 else -1)
            edge_check = pygame.Rect(int(ahead_x), int(self.y + self.height), 1, 1)
            edge_found = False
            for rect in colliders:
                if edge_check.colliderect(rect):
                    edge_found = True
                    break
            if not edge_found:
                self.vx *= -1
        super().update(colliders, dt)
        self.walk_timer += dt
        if self.walk_timer > 0.2:
            self.walk_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 2

    def draw(self, surf, cam):
        if not self.active:
            return
        x = int(self.x - cam)
        y = int(self.y)
        pygame.draw.ellipse(surf, NES_PALETTE[21], (x+2, y+4, 12, 12))  # body
        foot_offset = 2 if self.animation_frame == 0 else -2
        pygame.draw.rect(surf, NES_PALETTE[21], (x+2, y+14, 4, 2))      # left foot
        pygame.draw.rect(surf, NES_PALETTE[21], (x+10, y+14+foot_offset, 4, 2))  # right foot
        eye_dir = 0 if self.vx > 0 else 2
        pygame.draw.rect(surf, NES_PALETTE[0], (x+4+eye_dir, y+6, 2, 2))  # eyes
        pygame.draw.rect(surf, NES_PALETTE[0], (x+10-eye_dir, y+6, 2, 2))

class PiranhaPlant(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vy = -0.5
        self.height = 16
        self.max_height = 32
        self.state = "rising"  # rising, up, lowering
        self.timer = 0.0

    def update(self, colliders, dt):
        self.timer += dt
        if self.state == "rising":
            self.y += self.vy * dt * 60
            self.height += abs(self.vy * dt * 60)
            if self.height >= self.max_height:
                self.state = "up"
                self.timer = 0
        elif self.state == "up":
            if self.timer > 2.0:
                self.state = "lowering"
        elif self.state == "lowering":
            self.y -= self.vy * dt * 60
            self.height -= abs(self.vy * dt * 60)
            if self.height <= 16:
                self.state = "rising"
                self.timer = 0

    def draw(self, surf, cam):
        x = int(self.x - cam)
        y = int(self.y)
        pygame.draw.rect(surf, NES_PALETTE[14], (x+6, y, 4, self.height))              # stem
        pygame.draw.ellipse(surf, NES_PALETTE[14], (x+2, y-4, 12, 12))                 # head
        pygame.draw.ellipse(surf, NES_PALETTE[33], (x+4, y-2, 8, 8))                   # mouth
        pygame.draw.rect(surf, NES_PALETTE[0], (x+4, y+2, 8, 4))                       # mouth line

class CheepCheep(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vx = random.choice([-1, 1])
        self.vy = 0.0
        self.amplitude = random.uniform(0.5, 1.5)
        self.offset = random.uniform(0, math.pi*2)

    def update(self, colliders, dt):
        self.x += self.vx * dt * 60
        self.vy = math.sin(pygame.time.get_ticks() / 500.0 + self.offset) * self.amplitude
        self.y += self.vy * dt * 60
        if self.x < 0:
            self.vx = abs(self.vx)
        elif self.x > 3000:
            self.vx = -abs(self.vx)

    def draw(self, surf, cam):
        x = int(self.x - cam)
        y = int(self.y)
        pygame.draw.ellipse(surf, NES_PALETTE[33], (x, y, 16, 8))
        pygame.draw.polygon(surf, NES_PALETTE[33], [(x+16, y+4), (x+24, y), (x+24, y+8)])
        pygame.draw.circle(surf, NES_PALETTE[0], (x+4, y+3), 2)
        pygame.draw.polygon(surf, NES_PALETTE[33], [(x+8, y), (x+12, y-4), (x+16, y)])

class Boss(Entity):
    def __init__(self, x, y, boss_type):
        super().__init__(x, y)
        self.boss_type = boss_type
        self.health = 3
        self.attack_timer = 0.0
        self.attack_cooldown = 2.0
        self.vx = 0.0
        self.vy = 0.0
        self.width = 32
        self.height = 32

    def update(self, colliders, dt, player):
        self.attack_timer += dt
        if self.attack_timer >= self.attack_cooldown:
            self.attack_timer = 0
            if self.boss_type == "boom_boom":
                self.vx = 2 if player.x > self.x else -2
            elif self.boss_type == "morton":
                self.vy = -5

        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60

        if not self.on_ground:
            self.vy += 0.2 * dt * 60

        self.on_ground = False
        rect = self.get_rect()
        for solid in colliders:
            if rect.colliderect(solid):
                if self.vy > 0 and self.y + self.height > solid.top and self.y < solid.top:
                    self.y = solid.top - self.height
                    self.vy = 0
                    self.on_ground = True
        # simple wall bounce
        rect = self.get_rect()
        for solid in colliders:
            if rect.colliderect(solid):
                if self.vx > 0:
                    self.x = solid.left - self.width
                elif self.vx < 0:
                    self.x = solid.right
                self.vx *= -1

    def draw(self, surf, cam):
        x = int(self.x - cam)
        y = int(self.y)
        if self.boss_type == "boom_boom":
            pygame.draw.ellipse(surf, NES_PALETTE[31], (x, y, 32, 32))  # body
            arm_angle = math.sin(pygame.time.get_ticks() / 200) * 0.5
            arm_length = 20
            pygame.draw.line(surf, NES_PALETTE[31], (x+16, y+16),
                             (x+16 + math.cos(arm_angle) * arm_length, y+16 + math.sin(arm_angle) * arm_length), 6)
            pygame.draw.line(surf, NES_PALETTE[31], (x+16, y+16),
                             (x+16 + math.cos(arm_angle+math.pi) * arm_length, y+16 + math.sin(arm_angle+math.pi) * arm_length), 6)
            pygame.draw.circle(surf, NES_PALETTE[0], (x+16, y+16), 6)
            pygame.draw.circle(surf, NES_PALETTE[39], (x+16, y+16), 4)
        elif self.boss_type == "morton":
            pygame.draw.ellipse(surf, NES_PALETTE[33], (x, y, 32, 24))  # shell
            pygame.draw.rect(surf, NES_PALETTE[39], (x+8, y-8, 16, 16)) # head
            pygame.draw.circle(surf, NES_PALETTE[0], (x+12, y), 3)
            pygame.draw.circle(surf, NES_PALETTE[0], (x+20, y), 3)
            pygame.draw.polygon(surf, NES_PALETTE[21], [(x+16, y-16), (x+12, y-8), (x+20, y-8)])

class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type
        self.bounce_timer = 0.0

    def update(self, colliders, dt):
        self.bounce_timer += dt
        self.y += math.sin(self.bounce_timer * 5) * 0.5 * dt * 60

    def draw(self, surf, cam):
        x = int(self.x - cam)
        y = int(self.y)
        if self.type == "mushroom":
            pygame.draw.rect(surf, NES_PALETTE[39], (x+6, y+8, 4, 8))           # stem
            pygame.draw.ellipse(surf, NES_PALETTE[33], (x+2, y, 12, 10))       # cap
            pygame.draw.circle(surf, NES_PALETTE[31], (x+5, y+3), 2)           # spots
            pygame.draw.circle(surf, NES_PALETTE[31], (x+11, y+3), 2)
        elif self.type == "flower":
            pygame.draw.rect(surf, NES_PALETTE[14], (x+7, y+8, 2, 8))          # stem
            pygame.draw.circle(surf, NES_PALETTE[33], (x+8, y+8), 6)           # petals
            pygame.draw.circle(surf, NES_PALETTE[39], (x+8, y+8), 4)           # center
            for i in range(4):
                angle = i * math.pi/2
                pygame.draw.ellipse(surf, NES_PALETTE[33],
                                    (x+8 + math.cos(angle)*4 - 4, y+8 + math.sin(angle)*4 - 2, 8, 4))
        elif self.type == "star":
            points = []
            for i in range(5):
                angle = math.pi/2 + i * 2*math.pi/5
                points.append((x+8 + math.cos(angle)*6, y+8 + math.sin(angle)*6))
                points.append((x+8 + math.cos(angle+math.pi/5)*3, y+8 + math.sin(angle+math.pi/5)*3))
            pygame.draw.polygon(surf, NES_PALETTE[31], points)
            pygame.draw.polygon(surf, NES_PALETTE[39], points, 1)
        elif self.type == "coin":
            # Simple spinning coin look
            t = (pygame.time.get_ticks() // 100) % 6
            w = 10 - abs(3 - t)  # oscillate width
            pygame.draw.ellipse(surf, NES_PALETTE[35], (x+8 - w//2, y+4, max(2, w), 10))

# ================================
# TileMap
# ================================
class TileMap:
    def __init__(self, level_rows, theme):
        self.tiles = []       # (x, y, ch) for known terrain tiles
        self.colliders = []   # solid rects
        self.items = []
        self.width = len(level_rows[0]) * TILE
        self.height = len(level_rows) * TILE
        self.theme = theme

        for y, row in enumerate(level_rows):
            for x, ch in enumerate(row):
                if ch in TERRAIN_TILES:
                    # Track known tiles only
                    rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                    self.tiles.append((x * TILE, y * TILE, ch))
                    if ch in COLLIDABLE_TILES:
                        self.colliders.append(rect)
                elif ch in ITEM_MARKERS:
                    t = ITEM_MARKERS[ch]
                    self.items.append(Item(x * TILE, y * TILE, t))
                # ignore entity markers here (handled in LevelScene)

    def draw(self, surf, cam):
        # Background
        surf.fill(NES_PALETTE[self.theme["bg"]])

        # Parallax clouds
        for i in range(10):
            x = (i * 80 + int(cam/3)) % (self.width + 200) - 100
            y = 30 + (i % 3) * 20
            pygame.draw.ellipse(surf, NES_PALETTE[31], (x, y, 30, 15))
            pygame.draw.ellipse(surf, NES_PALETTE[31], (x+15, y-5, 25, 15))

        # Tiles
        for x, y, ch in self.tiles:
            draw_x = x - cam
            if draw_x < -TILE or draw_x > WIDTH:
                continue
            if ch == "G":
                pygame.draw.rect(surf, NES_PALETTE[self.theme["ground"]], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[self.theme["block"]], (draw_x, y+8, TILE, TILE-8))
                pygame.draw.rect(surf, NES_PALETTE[21], (draw_x+4, y+4, TILE-8, 4))
            elif ch == "S":  # sand surface
                pygame.draw.rect(surf, NES_PALETTE[33], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[21], (draw_x+2, y+2, TILE-4, TILE-4))
            elif ch == "D":  # deep sand
                pygame.draw.rect(surf, NES_PALETTE[21], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[33], (draw_x+3, y+3, TILE-6, TILE-6))
            elif ch == "I":
                pygame.draw.rect(surf, NES_PALETTE[39], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[38], (draw_x+2, y+2, TILE-4, TILE-4))
            elif ch == "B":
                pygame.draw.rect(surf, NES_PALETTE[self.theme["block"]], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[33], (draw_x+2, y+2, TILE-4, TILE-4))
            elif ch == "P":
                pygame.draw.rect(surf, NES_PALETTE[self.theme["block"]], (draw_x, y, TILE, TILE))
            elif ch == "T":
                pygame.draw.rect(surf, NES_PALETTE[14], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[20], (draw_x+2, y+2, TILE-4, TILE-4))
            elif ch == "?":
                pygame.draw.rect(surf, NES_PALETTE[33], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[39], (draw_x+4, y+4, 8, 4))
                pygame.draw.rect(surf, NES_PALETTE[39], (draw_x+4, y+8, 2, 2))
                pygame.draw.rect(surf, NES_PALETTE[39], (draw_x+10, y+8, 2, 2))
            elif ch == "F":
                pygame.draw.rect(surf, NES_PALETTE[31], (draw_x+6, y, 4, TILE*4))  # pole
                pygame.draw.rect(surf, NES_PALETTE[33], (draw_x, y, 10, 6))       # flag
            elif ch == "L":
                pygame.draw.rect(surf, NES_PALETTE[33], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[21], (draw_x, y+4, TILE, TILE-4))
            elif ch == "C":
                pygame.draw.rect(surf, NES_PALETTE[25], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[33], (draw_x+2, y+2, TILE-4, TILE-4))
            elif ch == "W":
                pygame.draw.rect(surf, NES_PALETTE[14], (draw_x+6, y, 4, TILE))
                pygame.draw.rect(surf, NES_PALETTE[14], (draw_x+2, y+8, 12, 4))
            elif ch == "Q":
                pygame.draw.rect(surf, NES_PALETTE[33], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[21], (draw_x+2, y+2, TILE-4, TILE-4))
                for i in range(3):
                    pygame.draw.circle(surf, NES_PALETTE[21], (draw_x+4+i*4, y+8), 1)
            # '/' (slope visual) and any other tiles are skipped

        # Items
        for item in self.items:
            item.draw(surf, cam)

# ================================
# Scenes
# ================================
class TitleScreen(Scene):
    def __init__(self):
        self.timer = 0.0
        self.animation_frame = 0
        self.logo_y = -50
        self.logo_target_y = HEIGHT // 2 - 60

    def handle(self, events, keys):
        for e in events:
            if e.type == KEYDOWN and e.key == K_RETURN:
                push(SlotSelect())

    def update(self, dt):
        self.timer += dt
        if self.timer > 0.1:
            self.timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
        if self.logo_y < self.logo_target_y:
            self.logo_y += 3 * dt * 60

    def draw(self, surf):
        surf.fill(NES_PALETTE[27])
        box_width, box_height = 240, 100
        box_x = (WIDTH - box_width) // 2
        box_y = int(self.logo_y)
        pygame.draw.rect(surf, NES_PALETTE[0], (box_x-4, box_y-4, box_width+8, box_height+8))
        pygame.draw.rect(surf, NES_PALETTE[33], (box_x, box_y, box_width, box_height))
        title_font = pygame.font.SysFont(None, 32)
        title = title_font.render("KOOPA ENGINE 1.0A", True, NES_PALETTE[39])
        surf.blit(title, (box_x + (box_width - title.get_width()) // 2, box_y + 15))
        subtitle_font = pygame.font.SysFont(None, 16)
        subtitle = subtitle_font.render("Tech demo", True, NES_PALETTE[21])
        surf.blit(subtitle, (box_x + (box_width - subtitle.get_width()) // 2, box_y + 50))
        copyright_font = pygame.font.SysFont(None, 14)
        copyright = copyright_font.render("[C] Team Flames 20XX [1985] - Nintendo", True, NES_PALETTE[0])
        surf.blit(copyright, (WIDTH//2 - copyright.get_width()//2, box_y + box_height + 20))
        # Mini characters
        mario_x = WIDTH//2 - 100
        mario_y = box_y + box_height + 50
        pygame.draw.rect(surf, NES_PALETTE[33], (mario_x+4, mario_y+8, 8, 16))
        pygame.draw.rect(surf, NES_PALETTE[39], (mario_x+4, mario_y+4, 8, 4))
        pygame.draw.rect(surf, NES_PALETTE[33], (mario_x+2, mario_y, 12, 4))
        pygame.draw.rect(surf, NES_PALETTE[39], (mario_x, mario_y+10, 4, 6))
        pygame.draw.rect(surf, NES_PALETTE[39], (mario_x+16, mario_y+10, 4, 6))
        pygame.draw.rect(surf, NES_PALETTE[21], (mario_x+2, mario_y+24, 4, 8))
        pygame.draw.rect(surf, NES_PALETTE[21], (mario_x+10, mario_y+24, 4, 8))
        # Goomba
        goomba_x = WIDTH//2 + 30
        goomba_y = mario_y + 20
        pygame.draw.ellipse(surf, NES_PALETTE[21], (goomba_x+2, goomba_y+4, 12, 12))
        pygame.draw.rect(surf, NES_PALETTE[21], (goomba_x+2, goomba_y+14, 4, 2))
        pygame.draw.rect(surf, NES_PALETTE[21], (goomba_x+10, goomba_y+14, 4, 2))
        pygame.draw.rect(surf, NES_PALETTE[0], (goomba_x+4, goomba_y+6, 2, 2))
        pygame.draw.rect(surf, NES_PALETTE[0], (goomba_x+10, goomba_y+6, 2, 2))
        # Koopa
        koopa_x = WIDTH//2 + 70
        koopa_y = mario_y + 20
        pygame.draw.ellipse(surf, NES_PALETTE[14], (koopa_x+2, koopa_y+4, 12, 12))
        pygame.draw.rect(surf, NES_PALETTE[39], (koopa_x+4, koopa_y, 8, 4))
        pygame.draw.rect(surf, NES_PALETTE[14], (koopa_x+2, koopa_y+14, 4, 2))
        pygame.draw.rect(surf, NES_PALETTE[14], (koopa_x+10, koopa_y+14, 4, 2))
        # Prompt
        if self.logo_y >= self.logo_target_y and int(pygame.time.get_ticks() / 400) % 2 == 0:
            font = pygame.font.SysFont(None, 24)
            text = font.render("PRESS ENTER", True, NES_PALETTE[39])
            surf.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 30))

class SlotSelect(Scene):
    def __init__(self):
        self.offset = 0.0
        self.selected = 0

    def handle(self, evts, keys):
        for e in evts:
            if e.type == KEYDOWN:
                if e.key in (K_1, K_2, K_3):
                    self.selected = e.key - K_1
                elif e.key == K_RETURN:
                    state.slot = self.selected
                    push(WorldSelect())
                elif e.key == K_ESCAPE:
                    push(TitleScreen())

    def update(self, dt):
        self.offset += dt

    def draw(self, s):
        s.fill(NES_PALETTE[27])
        font = pygame.font.SysFont(None, 30)
        title = font.render("SELECT PLAYER", True, NES_PALETTE[33])
        s.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        for i in range(3):
            x = 50 + i * 100
            y = 90 + 5 * math.sin(self.offset * 3 + i)
            pygame.draw.rect(s, NES_PALETTE[21], (x-5, y-5, 50, 70))
            pygame.draw.rect(s, NES_PALETTE[33], (x, y, 40, 60))
            slot_font = pygame.font.SysFont(None, 20)
            slot_text = slot_font.render(f"{i+1}", True, NES_PALETTE[39])
            s.blit(slot_text, (x+18, y+5))
            if i == self.selected:
                pygame.draw.rect(s, NES_PALETTE[39], (x-2, y-2, 44, 64), 2)
            if state.progress[i]:
                world = state.progress[i]["world"]
                world_font = pygame.font.SysFont(None, 16)
                world_text = world_font.render(f"WORLD {world}", True, NES_PALETTE[39])
                s.blit(world_text, (x+20 - world_text.get_width()//2, y+50))
                completed = len(state.progress[i]["completed"])
                completed_text = world_font.render(f"{completed}/32", True, NES_PALETTE[31])
                s.blit(completed_text, (x+20 - completed_text.get_width()//2, y+35))

class WorldSelect(Scene):
    def __init__(self):
        self.selected_world = 1
        self.offset = 0.0
        self.scroll_y = 0.0
        self.max_scroll = (8 - 4) * 60  # 8 worlds, 4 visible at a time

    def handle(self, evts, keys):
        for e in evts:
            if e.type == KEYDOWN:
                if e.key == K_UP:
                    self.selected_world = max(1, self.selected_world - 1)
                    if self.selected_world * 60 - self.scroll_y < 100:
                        self.scroll_y = max(0, self.selected_world * 60 - 100)
                elif e.key == K_DOWN:
                    self.selected_world = min(8, self.selected_world + 1)
                    if self.selected_world * 60 - self.scroll_y > HEIGHT - 100:
                        self.scroll_y = min(self.max_scroll, self.selected_world * 60 - HEIGHT + 100)
                elif e.key == K_RETURN:
                    push(LevelSelect(self.selected_world))
                elif e.key == K_ESCAPE:
                    pop()

    def update(self, dt):
        self.offset += dt

    def draw(self, s):
        s.fill(NES_PALETTE[27])
        font = pygame.font.SysFont(None, 30)
        title = font.render(f"SELECT WORLD - SLOT {state.slot+1}", True, NES_PALETTE[33])
        s.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        for world in range(1, 9):
            y_pos = 80 + (world-1) * 60 - self.scroll_y
            if y_pos < 60 or y_pos > HEIGHT:
                continue
            theme = WORLD_THEMES[str(world)]
            pygame.draw.rect(s, NES_PALETTE[theme["block"]], (50, y_pos, WIDTH-100, 50))
            pygame.draw.rect(s, NES_PALETTE[theme["ground"]], (55, y_pos+5, WIDTH-110, 40))
            world_font = pygame.font.SysFont(None, 24)
            world_text = world_font.render(f"{theme['name']}", True, NES_PALETTE[39])
            s.blit(world_text, (WIDTH//2 - world_text.get_width()//2, y_pos+15))
            completed = sum(1 for lvl in range(1,5) if f"{world}-{lvl}" in state.progress[state.slot]["completed"])
            comp_font = pygame.font.SysFont(None, 18)
            comp_text = comp_font.render(f"{completed}/4 completed", True, NES_PALETTE[31])
            s.blit(comp_text, (WIDTH//2 - comp_text.get_width()//2, y_pos+35))
            if world == self.selected_world:
                pygame.draw.rect(s, NES_PALETTE[39], (50, y_pos, WIDTH-100, 50), 3)
        # Scroll indicator
        if self.max_scroll > 0:
            track_h = HEIGHT - 150
            scroll_h = track_h * track_h / (self.max_scroll + track_h)
            scroll_pos = 100 + (HEIGHT - 250) * self.scroll_y / self.max_scroll
            pygame.draw.rect(s, NES_PALETTE[21], (WIDTH-20, 100, 10, HEIGHT-150))
            pygame.draw.rect(s, NES_PALETTE[33], (WIDTH-18, scroll_pos, 6, scroll_h))
        # Instructions
        small = pygame.font.SysFont(None, 16)
        text = small.render("UP/DOWN: Select World  ENTER: Choose  ESC: Back", True, NES_PALETTE[0])
        s.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 20))

class LevelSelect(Scene):
    def __init__(self, world_num):
        self.world_num = world_num
        self.selected_level = 1
        self.offset = 0.0

    def handle(self, evts, keys):
        for e in evts:
            if e.type == KEYDOWN:
                if e.key == K_LEFT:
                    self.selected_level = max(1, self.selected_level - 1)
                elif e.key == K_RIGHT:
                    self.selected_level = min(4, self.selected_level + 1)
                elif e.key == K_RETURN:
                    level_id = f"{self.world_num}-{self.selected_level}"
                    state.world = level_id
                    push(LevelScene(level_id))
                elif e.key == K_ESCAPE:
                    pop()

    def update(self, dt):
        self.offset += dt

    def draw(self, s):
        s.fill(NES_PALETTE[27])
        theme = WORLD_THEMES[str(self.world_num)]
        font = pygame.font.SysFont(None, 30)
        title = font.render(f"{theme['name']} - SLOT {state.slot+1}", True, NES_PALETTE[33])
        s.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        for level in range(1, 5):
            x_pos = 50 + (level-1) * 70
            y_pos = 100
            pygame.draw.rect(s, NES_PALETTE[theme["block"]], (x_pos, y_pos, 60, 80))
            pygame.draw.rect(s, NES_PALETTE[theme["ground"]], (x_pos+5, y_pos+5, 50, 70))
            level_font = pygame.font.SysFont(None, 24)
            level_text = level_font.render(f"{level}", True, NES_PALETTE[39])
            s.blit(level_text, (x_pos+30 - level_text.get_width()//2, y_pos+15))
            level_id = f"{self.world_num}-{level}"
            thumb = THUMBNAILS.get(level_id)
            if not thumb:
                thumb = pygame.Surface((32,24))
                thumb.fill(NES_PALETTE[theme["bg"]])
            s.blit(thumb, (x_pos+15, y_pos+35))
            if level == 4:
                pygame.draw.rect(s, NES_PALETTE[33], (x_pos+20, y_pos+10, 20, 15))
                pygame.draw.rect(s, NES_PALETTE[21], (x_pos+25, y_pos+5, 10, 5))
                pygame.draw.rect(s, NES_PALETTE[0], (x_pos+28, y_pos+8, 4, 7))
            if level_id in state.progress[state.slot]["completed"]:
                pygame.draw.circle(s, NES_PALETTE[31], (x_pos+55, y_pos+15), 6)
            if level == self.selected_level:
                pygame.draw.rect(s, NES_PALETTE[39], (x_pos, y_pos, 60, 80), 3)
        small = pygame.font.SysFont(None, 16)
        text = small.render("LEFT/RIGHT: Select Level  ENTER: Play  ESC: Back", True, NES_PALETTE[0])
        s.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 20))

class LevelScene(Scene):
    def __init__(self, level_id):
        level_rows, theme = LEVELS[level_id]
        self.map = TileMap(level_rows, theme)
        self.player = Player(50, 100)
        self.enemies = []
        self.items = self.map.items
        self.cam = 0.0
        self.level_id = level_id
        self.time = 300.0
        self.end_level = False
        self.end_timer = 0.0
        self.flag_pos = 0
        self.boss = None
        self.world_num = level_id.split("-")[0]
        # world 3 -> underwater physics
        self.player.underwater = (self.world_num == "3")

        # Parse entities
        for y, row in enumerate(level_rows):
            for x, ch in enumerate(row):
                if ch == 'E':
                    self.player.x = x * TILE
                    self.player.y = y * TILE
                elif ch == 'g':
                    self.enemies.append(Goomba(x * TILE, y * TILE))
                elif ch == 'p':
                    self.enemies.append(PiranhaPlant(x * TILE, y * TILE))
                elif ch == 'c':
                    self.enemies.append(CheepCheep(x * TILE, y * TILE))
                elif ch == 'k':
                    self.enemies.append(Goomba(x * TILE, y * TILE))  # koopa placeholder
                elif ch == 'X':
                    if self.world_num == "1":
                        self.boss = Boss(x * TILE, y * TILE, "boom_boom")
                    elif self.world_num == "2":
                        self.boss = Boss(x * TILE, y * TILE, "morton")
                    else:
                        self.boss = Boss(x * TILE, y * TILE, "boom_boom")
                elif ch == 'F':
                    self.flag_pos = x * TILE

    def handle(self, evts, keys):
        for e in evts:
            if e.type == KEYDOWN:
                if e.key in (K_ESCAPE, K_p):
                    state.paused = not state.paused

    def update(self, dt):
        if state.paused:
            return
        # timer
        self.time = max(0, self.time - dt)

        # player & enemies
        self.player.update(self.map.colliders, dt, self.enemies, self.items)
        for enemy in self.enemies:
            if enemy.active:
                enemy.update(self.map.colliders, dt)

        # boss
        if self.boss and self.boss.active:
            self.boss.update(self.map.colliders, dt, self.player)
            for fb in self.player.fireballs[:]:
                fb_rect = pygame.Rect(int(fb.x), int(fb.y), fb.width, fb.height)
                if self.boss.get_rect().colliderect(fb_rect):
                    self.boss.health -= 1
                    fb.active = False
                    if self.boss.health <= 0:
                        self.boss.active = False
                        state.progress[state.slot]["boss_defeated"] = True
                        state.score += 5000

        # camera
        target = self.player.x - WIDTH // 2
        self.cam += (target - self.cam) * 0.1 * dt * 60
        self.cam = max(0, min(self.cam, self.map.width - WIDTH))

        # end of level logic
        if self.player.x > self.map.width - 120 and not self.end_level:
            self.end_level = True
            self.end_timer = 3.0
            state.progress[state.slot]["completed"].add(self.level_id)

        if self.end_level:
            if self.player.x < self.flag_pos - 10:
                self.player.vx = 2
            else:
                self.player.vx = 0
                if self.player.y < self.map.height - TILE * 5:
                    self.player.vy = 2
            self.end_timer -= dt
            if self.end_timer <= 0:
                pop()  # back to level select

    def draw(self, s):
        self.map.draw(s, self.cam)
        for enemy in self.enemies:
            if enemy.active:
                enemy.draw(s, self.cam)
        if self.boss and self.boss.active:
            self.boss.draw(s, self.cam)
        self.player.draw(s, self.cam)

        # HUD
        pygame.draw.rect(s, NES_PALETTE[0], (0, 0, WIDTH, 20))
        font = pygame.font.SysFont(None, 16)
        score_text = font.render(f"SCORE {state.score:06d}", True, NES_PALETTE[39])
        s.blit(score_text, (10, 4))
        # coins (left-center)
        coin_text = font.render(f"COINS {state.coins:02d}", True, NES_PALETTE[39])
        s.blit(coin_text, (WIDTH//2 - 120, 4))
        # time (right-center)
        time_text = font.render(f"TIME {int(self.time):03d}", True, NES_PALETTE[39])
        s.blit(time_text, (WIDTH//2 + 40, 4))
        # world (far right)
        world_text = font.render(f"WORLD {self.level_id}", True, NES_PALETTE[39])
        s.blit(world_text, (WIDTH - world_text.get_width() - 10, 4))
        # lives
        lives_text = font.render(f"x{state.lives}", True, NES_PALETTE[39])
        s.blit(lives_text, (WIDTH - 60, 4))
        pygame.draw.rect(s, NES_PALETTE[33], (WIDTH - 80, 6, 8, 8))
        pygame.draw.rect(s, NES_PALETTE[39], (WIDTH - 80, 2, 8, 8))

        # power-up indicator
        if state.mario_size == "big":
            pygame.draw.rect(s, NES_PALETTE[33], (10, HEIGHT-20, 12, 12))
        elif state.mario_size == "fire":
            pygame.draw.rect(s, NES_PALETTE[31], (10, HEIGHT-20, 12, 12))

        # pause overlay
        if state.paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            s.blit(overlay, (0, 0))
            big = pygame.font.SysFont(None, 30)
            text = big.render("PAUSED", True, NES_PALETTE[39])
            s.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 20))
            small = pygame.font.SysFont(None, 16)
            text2 = small.render("Press P or ESC to continue", True, NES_PALETTE[39])
            s.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2 + 20))

class GameOverScene(Scene):
    def __init__(self):
        self.timer = 3.0
        self.final_score = state.score

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            pop()
            state.lives = 3
            state.score = 0

    def draw(self, s):
        s.fill(NES_PALETTE[0])
        font = pygame.font.SysFont(None, 40)
        text = font.render("GAME OVER", True, NES_PALETTE[33])
        s.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 20))
        font2 = pygame.font.SysFont(None, 20)
        text2 = font2.render(f"FINAL SCORE: {self.final_score}", True, NES_PALETTE[39])
        s.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2 + 20))

class WinScreen(Scene):
    def __init__(self):
        self.timer = 5.0
        self.fireworks = []

    def update(self, dt):
        self.timer -= dt
        if random.random() < 0.2:
            self.fireworks.append({
                "x": random.randint(50, WIDTH-50),
                "y": HEIGHT,
                "size": random.randint(20, 40),
                "color": random.choice([NES_PALETTE[33], NES_PALETTE[39], NES_PALETTE[31]]),
                "particles": []
            })
        for fw in self.fireworks[:]:
            fw["y"] -= 3 * dt * 60
            if fw["y"] < HEIGHT//3:
                for _ in range(20):
                    angle = random.uniform(0, math.pi*2)
                    speed = random.uniform(2, 5)
                    fw["particles"].append({
                        "x": fw["x"],
                        "y": fw["y"],
                        "vx": math.cos(angle) * speed,
                        "vy": math.sin(angle) * speed,
                        "life": 1.0
                    })
                self.fireworks.remove(fw)
        for fw in self.fireworks:
            for p in fw["particles"][:]:
                p["x"] += p["vx"] * dt * 60
                p["y"] += p["vy"] * dt * 60
                p["vy"] += 0.1 * dt * 60
                p["life"] -= 0.02 * dt * 60
                if p["life"] <= 0:
                    fw["particles"].remove(p)
        if self.timer <= 0:
            push(TitleScreen())

    def draw(self, s):
        s.fill(NES_PALETTE[0])
        for fw in self.fireworks:
            pygame.draw.circle(s, NES_PALETTE[39], (int(fw["x"]), int(fw["y"])), 3)
            for p in fw["particles"]:
                pygame.draw.circle(s, (min(255, fw["color"][0]), min(255, fw["color"][1]), min(255, fw["color"][2])),
                                   (int(p["x"]), int(p["y"])), 2)
        font = pygame.font.SysFont(None, 40)
        text = font.render("CONGRATULATIONS!", True, NES_PALETTE[33])
        s.blit(text, (WIDTH//2 - text.get_width()//2, 50))
        font2 = pygame.font.SysFont(None, 30)
        text2 = font2.render("YOU SAVED THE PRINCESS!", True, NES_PALETTE[39])
        s.blit(text2, (WIDTH//2 - text2.get_width()//2, 100))
        font3 = pygame.font.SysFont(None, 24)
        text3 = font3.render(f"FINAL SCORE: {state.score}", True, NES_PALETTE[31])
        s.blit(text3, (WIDTH//2 - text3.get_width()//2, 150))

# ================================
# Main game
# ================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("KOOPA ENGINE 1.0A Tech Demo")
    clock = pygame.time.Clock()

    # Build thumbnails AFTER pygame is initialized
    _build_thumbnails()

    push(TitleScreen())

    running = True
    while running and SCENES:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        for e in events:
            if e.type == QUIT:
                running = False
        scene = SCENES[-1]
        scene.handle(events, keys)
        scene.update(dt)
        scene.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
