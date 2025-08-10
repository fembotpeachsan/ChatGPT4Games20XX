# koopa_engine_full.py
# KOOPA ENGINE 1.1 — Full Single-File Build
# - Includes OverworldEditor + LevelEditor
# - Fix: HUD coin/time overlap; uses distinct positions
# - Fix: Scene transitions now "replace" instead of stacking endlessly
# - Minor: Thumbnail generation colors for blocks vs ground clarified
# - Keys: F11 toggle fullscreen, ENTER to advance, E to open Editor from Title

import sys, math, random, time, json, os, shutil, zipfile
from dataclasses import dataclass, field

import pygame
from pygame.locals import *

# --- Init first so font/surface creation is safe ---
pygame.init()

# Constants
SCALE = 2
TILE = 16
WIDTH = int(300 * SCALE)   # 600
HEIGHT = int(200 * SCALE)  # 400
FPS = 60

# NES Palette (44 entries)
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

# Helpers
def create_button(text, width, height, bg_color, text_color):
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surf, bg_color, (0, 0, width, height))
    pygame.draw.rect(surf, NES_PALETTE[0], (0, 0, width, height), 2)
    font = pygame.font.SysFont(None, 20)
    text_surf = font.render(text, True, text_color)
    surf.blit(text_surf, (width//2 - text_surf.get_width()//2,
                          height//2 - text_surf.get_height()//2))
    return surf

def create_tile_images():
    tile_images = {}
    # Ground tile 'G'
    surf = pygame.Surface((TILE, TILE))
    pygame.draw.rect(surf, NES_PALETTE[20], (0, 0, TILE, TILE))
    pygame.draw.rect(surf, NES_PALETTE[19], (0, 8, TILE, TILE-8))
    pygame.draw.rect(surf, NES_PALETTE[18], (4, 4, TILE-8, 4))
    tile_images['G'] = surf
    # Brick/Block 'B'
    surf = pygame.Surface((TILE, TILE))
    pygame.draw.rect(surf, NES_PALETTE[33], (0, 0, TILE, TILE))
    pygame.draw.rect(surf, NES_PALETTE[32], (2, 2, TILE-4, TILE-4))
    tile_images['B'] = surf
    # Platform 'P'
    surf = pygame.Surface((TILE, TILE))
    pygame.draw.rect(surf, NES_PALETTE[21], (0, 0, TILE, TILE))
    tile_images['P'] = surf
    # Pipe 'T'
    surf = pygame.Surface((TILE, TILE))
    pygame.draw.rect(surf, NES_PALETTE[14], (0, 0, TILE, TILE))
    pygame.draw.rect(surf, NES_PALETTE[13], (2, 2, TILE-4, TILE-4))
    tile_images['T'] = surf
    # Question block '?'
    surf = pygame.Surface((TILE, TILE))
    pygame.draw.rect(surf, NES_PALETTE[33], (0, 0, TILE, TILE))
    pygame.draw.rect(surf, NES_PALETTE[39], (4, 4, 8, 4))
    pygame.draw.rect(surf, NES_PALETTE[39], (4, 8, 2, 2))
    pygame.draw.rect(surf, NES_PALETTE[39], (10, 8, 2, 2))
    tile_images['?'] = surf
    # Player start 'S'
    surf = pygame.Surface((TILE, TILE))
    pygame.draw.rect(surf, NES_PALETTE[39], (0, 0, TILE, TILE))
    tile_images['S'] = surf
    # Flag 'F'
    surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    pygame.draw.rect(surf, NES_PALETTE[31], (6, 0, 4, TILE))
    pygame.draw.rect(surf, NES_PALETTE[33], (0, 0, 10, 6))
    tile_images['F'] = surf
    # Empty ' '
    surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    tile_images[' '] = surf
    # Enemies previews
    def enemy_box(col):
        s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        pygame.draw.rect(s, col, (2, 2, TILE-4, TILE-4))
        return s
    tile_images['g'] = enemy_box(NES_PALETTE[21])
    tile_images['k'] = enemy_box(NES_PALETTE[14])
    tile_images['f'] = enemy_box(NES_PALETTE[40])
    tile_images['s'] = enemy_box(NES_PALETTE[33])
    return tile_images

def create_overworld_tile_images():
    tile_images = {}
    def box(c):
        s = pygame.Surface((24,24), pygame.SRCALPHA)
        pygame.draw.rect(s, c, (0,0,24,24))
        pygame.draw.rect(s, NES_PALETTE[0], (0,0,24,24), 2)
        return s
    tile_images["empty"]  = box(NES_PALETTE[27])
    tile_images["grass"]  = box(NES_PALETTE[20])
    tile_images["desert"] = box(NES_PALETTE[21])
    tile_images["water"]  = box(NES_PALETTE[25])
    tile_images["level"]  = box(NES_PALETTE[33])
    tile_images["castle"] = box(NES_PALETTE[28])
    tile_images["pipe"]   = box(NES_PALETTE[14])
    tile_images["path"]   = box(NES_PALETTE[21])
    tile_images["start"]  = box(NES_PALETTE[39])
    return tile_images

# Game State
class GameState:
    def __init__(self):
        self.slot = 0
        self.progress = [{"world": 1}, {"world": 1}, {"world": 1}]
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.world = 1
        self.level = 1
        self.time = 300
        self.mario_size = "small"
        self.unlocked_worlds = [1]
        self.editor_mode = False
        self.editing_level = None
        self.editing_world = 1
        self.selected_tool = "ground"
        self.selected_tile = "G"
        self.show_grid = True
        self.overworld_map = self.create_default_overworld()
        self.tile_images = create_tile_images()
        self.overworld_tile_images = create_overworld_tile_images()
        self.buttons = self.create_buttons()

    def create_default_overworld(self):
        overworld = []
        for row in range(8):
            overworld_row = []
            for col in range(8):
                tile = {"type": "empty", "level": None, "enemies": []}
                if row == 3 and col in [1,2,3,4,5]:
                    tile["type"] = "path"
                elif row == 3 and col == 0:
                    tile["type"] = "start"
                elif row == 3 and col == 6:
                    tile["type"] = "castle"; tile["level"] = "castle"
                elif row == 2 and col == 2:
                    tile["type"] = "level"; tile["level"] = "1-1"
                elif row == 4 and col == 2:
                    tile["type"] = "level"; tile["level"] = "1-2"
                elif row == 2 and col == 4:
                    tile["type"] = "level"; tile["level"] = "1-3"
                elif row == 4 and col == 4:
                    tile["type"] = "level"; tile["level"] = "1-4"
                overworld_row.append(tile)
            overworld.append(overworld_row)
        return overworld

    def create_buttons(self):
        return {
            "menu":   create_button("Menu", 80, 30, NES_PALETTE[33], NES_PALETTE[39]),
            "save":   create_button("Save", 80, 30, NES_PALETTE[33], NES_PALETTE[39]),
            "load":   create_button("Load", 80, 30, NES_PALETTE[33], NES_PALETTE[39]),
            "export": create_button("Export",80, 30, NES_PALETTE[33], NES_PALETTE[39]),
            "editor": create_button("Editor",80, 30, NES_PALETTE[33], NES_PALETTE[39]),
            "play":   create_button("Play", 80, 30, NES_PALETTE[33], NES_PALETTE[39]),
            "back":   create_button("Back", 80, 30, NES_PALETTE[33], NES_PALETTE[39]),
        }

state = GameState()

# Scene stack
SCENES = []
def push(scene): SCENES.append(scene)
def pop(): 
    if SCENES: SCENES.pop()

def replace(scene):
    if SCENES:
        SCENES[-1] = scene
    else:
        push(scene)

class Scene:
    def handle(self, events, keys): ...
    def update(self, dt): ...
    def draw(self, surf): ...

# World themes — enemy_char now LOWERCASE
WORLD_THEMES = {
    1: {"sky":27,"ground":20,"pipe":14,"block":33,"water":None,"enemy_char":"g","name":"GRASS LAND"},
    2: {"sky":26,"ground":21,"pipe":15,"block":34,"water":None,"enemy_char":"k","name":"DESERT HILL"},
    3: {"sky":25,"ground":22,"pipe":16,"block":35,"water":41,  "enemy_char":"f","name":"AQUA SEA"},
    4: {"sky":24,"ground":23,"pipe":17,"block":36,"water":None,"enemy_char":"g","name":"GIANT FOREST"},
    5: {"sky":23,"ground":24,"pipe":18,"block":37,"water":None,"enemy_char":"k","name":"SKY HEIGHTS"},
    6: {"sky":22,"ground":25,"pipe":19,"block":38,"water":None,"enemy_char":"g","name":"ICE CAVERN"},
    7: {"sky":21,"ground":26,"pipe":20,"block":39,"water":None,"enemy_char":"s","name":"LAVA CASTLE"},
    8: {"sky":20,"ground":27,"pipe":21,"block":40,"water":None,"enemy_char":"s","name":"FINAL FORTRESS"},
}

# Level generation (8 worlds x 4 stages, each 20 rows x 100 cols)
def generate_level_data():
    levels = {}
    rng = random.Random(1337)
    for world in range(1,9):
        for level in range(1,5):
            level_id = f"{world}-{level}"
            theme = WORLD_THEMES[world]
            rows = []
            # Build empty sky rows
            for _ in range(15): rows.append(" " * 100)
            # Ground stripe at y>=15
            for i in range(15,20):
                rows.append(("G" if i==15 else "B") * 100)
            # Platforms
            for i in range(5 + level):
                py = rng.randint(8, 12)
                px = rng.randint(10 + i*20, 15 + i*20)
                ln = rng.randint(4, 8)
                row = list(rows[py])
                for j in range(ln):
                    if 0 <= px+j < 100: row[px+j] = "P"
                rows[py] = "".join(row)
            # Pipes
            for i in range(2 + level//2):
                px = rng.randint(20 + i*30, 25 + i*30)
                ph = rng.randint(2, 4)
                for j in range(ph):
                    for dx in (0,1):
                        y = 19 - j
                        row = list(rows[y])
                        if 0 <= px+dx < 100: row[px+dx] = "T"
                        rows[y] = "".join(row)
            # Bricks / Question
            for i in range(8 + level):
                by = rng.randint(5, 10)
                bx = rng.randint(5 + i*10, 8 + i*10)
                bt = "?" if rng.random() > 0.5 else "B"
                if 0 <= bx < 100:
                    row = list(rows[by]); row[bx] = bt; rows[by] = "".join(row)
            # Player start + flag
            row = list(rows[14]); row[5] = "S"; row[95] = "F"; rows[14] = "".join(row)
            # Enemies (lowercase)
            e = theme["enemy_char"]
            for i in range(5 + level):
                ex = rng.randint(20 + i*15, 25 + i*15)
                if 0 <= ex < 100:
                    row = list(rows[14])
                    row[ex] = e
                    rows[14] = "".join(row)
            levels[level_id] = rows
    return levels

LEVELS = generate_level_data()

# Thumbnail helpers
def build_thumbnail(level_id, level_data):
    world = int(level_id.split("-")[0])
    theme = WORLD_THEMES[world]
    thumb = pygame.Surface((32, 24))
    thumb.fill(NES_PALETTE[theme["sky"]])
    # Show top of terrain slice
    sample_rows = level_data[12:16]
    for y, row in enumerate(sample_rows):
        for x, ch in enumerate(row[::3]):
            if ch in ("G","P","T"):
                thumb.set_at((x, y+8), NES_PALETTE[theme["ground"]])
            elif ch in ("B","?"):
                thumb.set_at((x, y+8), NES_PALETTE[theme["block"]])
    return thumb

THUMBNAILS = {lid: build_thumbnail(lid, dat) for lid, dat in LEVELS.items()}

# Entities
class Entity:
    def __init__(self, x, y):
        self.x,self.y = x,y
        self.vx = 0
        self.vy = 0
        self.width = TILE
        self.height = TILE
        self.on_ground = False
        self.facing_right = True
        self.active = True
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def update_rect(self):
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def check_collision(self, other):
        return self.rect.colliderect(other.rect)

    def update(self, colliders, dt):
        if not self.on_ground:
            self.vy += 0.5 * dt * 60
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.update_rect()
        self.on_ground = False
        for rect in colliders:
            if self.rect.colliderect(rect):
                # vertical
                if self.vy > 0 and self.y + self.height > rect.top and self.y < rect.top:
                    self.y = rect.top - self.height; self.vy = 0; self.on_ground = True
                elif self.vy < 0 and self.y < rect.bottom and self.y + self.height > rect.bottom:
                    self.y = rect.bottom; self.vy = 0
                # horizontal
                if self.vx > 0 and self.x + self.width > rect.left and self.x < rect.left:
                    self.x = rect.left - self.width; self.vx = 0
                elif self.vx < 0 and self.x < rect.right and self.x + self.width > rect.right:
                    self.x = rect.right; self.vx = 0
        self.update_rect()

    def draw(self, surf, cam): ...

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.jump_power = -5
        self.move_speed = 2
        self.invincible = 0
        self.animation_frame = 0
        self.walk_timer = 0
        self.frames = self.pre_render_frames()

    def pre_render_frames(self):
        frames = {"small": [], "big": []}
        for _ in range(3):
            surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            pygame.draw.rect(surf, NES_PALETTE[33], (4, 8, 8, 8))
            pygame.draw.rect(surf, NES_PALETTE[39], (4, 0, 8, 8))
            pygame.draw.rect(surf, NES_PALETTE[33], (2, 0, 12, 2))
            frames["small"].append(surf)
        for _ in range(3):
            surf = pygame.Surface((TILE, int(TILE*1.5)), pygame.SRCALPHA)
            pygame.draw.rect(surf, NES_PALETTE[33], (4, 8, 8, 16))
            pygame.draw.rect(surf, NES_PALETTE[39], (4, 4, 8, 4))
            pygame.draw.rect(surf, NES_PALETTE[33], (2, 0, 12, 4))
            frames["big"].append(surf)
        return frames

    def update(self, colliders, dt, enemies):
        keys = pygame.key.get_pressed()
        self.vx = (-self.move_speed if keys[K_LEFT] else 0) + (self.move_speed if keys[K_RIGHT] else 0)
        if self.vx < 0: self.facing_right = False
        if self.vx > 0: self.facing_right = True
        if (keys[K_SPACE] or keys[K_z]) and self.on_ground:
            self.vy = self.jump_power; self.on_ground = False
        if self.vx != 0:
            self.walk_timer += dt
            if self.walk_timer > 0.1:
                self.walk_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 3
        else:
            self.animation_frame = 0
        if self.invincible > 0: self.invincible -= dt
        super().update(colliders, dt)
        for enemy in enemies:
            if enemy.active and self.check_collision(enemy):
                if self.vy > 0 and self.y + self.height - 5 < enemy.y:
                    enemy.active = False; self.vy = self.jump_power / 2; state.score += 100
                elif self.invincible <= 0:
                    if state.mario_size == "big":
                        state.mario_size = "small"; self.invincible = 2
                    else:
                        state.lives -= 1
                        if state.lives <= 0:
                            replace(GameOverScene())
                        else:
                            self.x, self.y, self.vx, self.vy = 50, 100, 0, 0

    def draw(self, surf, cam):
        if self.invincible > 0 and int(self.invincible * 10) % 2 == 0: return
        frame = self.frames[state.mario_size][self.animation_frame]
        if not self.facing_right: frame = pygame.transform.flip(frame, True, False)
        surf.blit(frame, (int(self.x - cam), int(self.y)))

class Goomba(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vx = -0.5
        self.animation_frame = 0
        self.walk_timer = 0
        self.frames = self.pre_render_frames()

    def pre_render_frames(self):
        frames = []
        for frame in range(2):
            surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, NES_PALETTE[21], (2, 4, 12, 12))
            foot_offset = 2 if frame == 0 else -2
            pygame.draw.rect(surf, NES_PALETTE[21], (2, 14, 4, 2))
            pygame.draw.rect(surf, NES_PALETTE[21], (10, 14+foot_offset, 4, 2))
            pygame.draw.rect(surf, NES_PALETTE[0], (6, 6, 2, 2))
            pygame.draw.rect(surf, NES_PALETTE[0], (10, 6, 2, 2))
            frames.append(surf)
        return frames

    def update(self, colliders, dt):
        if self.on_ground:
            edge_check = pygame.Rect(self.x + (self.width if self.vx > 0 else -1),
                                     self.y + self.height, 1, 1)
            if not any(edge_check.colliderect(r) for r in colliders):
                self.vx *= -1
        super().update(colliders, dt)
        self.walk_timer += dt
        if self.walk_timer > 0.2:
            self.walk_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 2

    def draw(self, surf, cam):
        if not self.active: return
        frame = self.frames[self.animation_frame]
        if self.vx > 0: frame = pygame.transform.flip(frame, True, False)
        surf.blit(frame, (int(self.x - cam), int(self.y)))

class Koopa(Goomba):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.shell_mode = False
        self.frames = self.pre_render_frames()

    def pre_render_frames(self):
        frames = []
        for _ in range(2):
            surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, NES_PALETTE[14], (2, 4, 12, 12))
            if not self.shell_mode:
                pygame.draw.rect(surf, NES_PALETTE[39], (4, 0, 8, 4))
                pygame.draw.rect(surf, NES_PALETTE[14], (2, 14, 4, 2))
                pygame.draw.rect(surf, NES_PALETTE[14], (10, 14, 4, 2))
            frames.append(surf)
        return frames

class Fish(Goomba): ...
class Spike(Goomba): ...

# Tiles we actually draw/collide with
TILE_CHARS = {"G","B","P","T","?","S","F"," "}
ENEMY_CHARS = {"g","k","f","s"}

class TileMap:
    def __init__(self, level_data, level_id):
        self.tiles = []
        self.colliders = []
        self.width = len(level_data[0]) * TILE
        self.height = len(level_data) * TILE
        self.level_id = level_id
        world = int(level_id.split("-")[0])
        self.theme = WORLD_THEMES[world]
        for y, row in enumerate(level_data):
            for x, ch in enumerate(row):
                if ch in TILE_CHARS:
                    rect = pygame.Rect(x*TILE, y*TILE, TILE, TILE)
                    self.tiles.append((x*TILE, y*TILE, ch))
                    if ch in ("G","B","P","T","?"):
                        self.colliders.append(rect)

    def draw(self, surf, cam):
        surf.fill(NES_PALETTE[self.theme["sky"]])
        # clouds
        for i in range(10):
            cx = (i * 80 + int(cam/3)) % (self.width + 200) - 100
            cy = 30 + (i % 3) * 20
            pygame.draw.ellipse(surf, NES_PALETTE[31], (cx, cy, 30, 15))
            pygame.draw.ellipse(surf, NES_PALETTE[31], (cx+15, cy-5, 25, 15))
        for x,y,ch in self.tiles:
            dx = x - cam
            if -TILE <= dx <= WIDTH:
                surf.blit(state.tile_images[ch], (dx, y))

# Scenes
class TitleScreen(Scene):
    def __init__(self):
        self.timer = 0
        self.logo_y = -50
        self.logo_target_y = HEIGHT // 2 - 60
        self.logo = self.pre_render_logo()

    def pre_render_logo(self):
        surf = pygame.Surface((240, 100), pygame.SRCALPHA)
        pygame.draw.rect(surf, NES_PALETTE[0], (0,0,240,100), 4)
        pygame.draw.rect(surf, NES_PALETTE[33], (4,4,232,92))
        title_font = pygame.font.SysFont(None, 32)
        title = title_font.render("KOOPA ENGINE 1.1", True, NES_PALETTE[39])
        surf.blit(title, (120 - title.get_width()//2, 15))
        subtitle_font = pygame.font.SysFont(None, 16)
        subtitle = subtitle_font.render("8 Worlds Edition", True, NES_PALETTE[21])
        surf.blit(subtitle, (120 - subtitle.get_width()//2, 50))
        return surf

    def handle(self, events, keys):
        for e in events:
            if e.type == KEYDOWN and e.key == K_RETURN: replace(FileSelect())
            elif e.type == KEYDOWN and e.key == K_e:
                state.editor_mode = True; replace(OverworldEditor())

    def update(self, dt):
        self.timer += dt
        if self.logo_y < self.logo_target_y: self.logo_y += 3

    def draw(self, surf):
        surf.fill(NES_PALETTE[27])
        surf.blit(self.logo, (WIDTH//2 - self.logo.get_width()//2, self.logo_y))
        copyright_font = pygame.font.SysFont(None, 14)
        cr = copyright_font.render("[C] Team Flames 20XX [1985] - Nintendo", True, NES_PALETTE[0])
        surf.blit(cr, (WIDTH//2 - cr.get_width()//2, self.logo_y + 120))
        if self.logo_y >= self.logo_target_y and int(self.timer * 10) % 2 == 0:
            font = pygame.font.SysFont(None, 24)
            text = font.render("PRESS ENTER", True, NES_PALETTE[39])
            surf.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 30))
            font = pygame.font.SysFont(None, 16)
            text = font.render("Press E for Editor", True, NES_PALETTE[21])
            surf.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 60))

class FileSelect(Scene):
    def __init__(self):
        self.offset = 0
        self.selected = 0

    def handle(self, evts, keys):
        for e in evts:
            if e.type == KEYDOWN:
                if e.key in (K_1, K_2, K_3): self.selected = e.key - K_1
                elif e.key == K_RETURN:
                    state.slot = self.selected
                    state.world = state.progress[state.slot]["world"]
                    replace(WorldMapScene())
                elif e.key == K_ESCAPE:
                    replace(TitleScreen())

    def update(self, dt): self.offset += dt

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
            world = state.progress[i]["world"]
            world_font = pygame.font.SysFont(None, 16)
            world_text = world_font.render(f"WORLD {world}", True, NES_PALETTE[39])
            s.blit(world_text, (x+20 - world_text.get_width()//2, y+50))
            thumb = THUMBNAILS.get(f"{world}-1", list(THUMBNAILS.values())[0])
            s.blit(thumb, (x+4, y+20))

class WorldMapScene(Scene):
    def __init__(self):
        self.selection = state.world
        self.offset = 0
        self.cursor_timer = 0

    def handle(self, evts, keys):
        for e in evts:
            if e.type == KEYDOWN:
                if e.key == K_LEFT and self.selection > 1: self.selection -= 1
                elif e.key == K_RIGHT and self.selection < 8: self.selection += 1
                elif e.key == K_UP and self.selection > 4: self.selection -= 4
                elif e.key == K_DOWN and self.selection < 5: self.selection += 4
                elif e.key == K_RETURN:
                    if self.selection <= max(state.unlocked_worlds):
                        state.world = self.selection
                        state.progress[state.slot]["world"] = self.selection
                        replace(LevelScene(f"{state.world}-1"))
                elif e.key == K_ESCAPE: replace(FileSelect())

    def update(self, dt):
        self.offset += dt
        self.cursor_timer += dt

    def draw(self, s):
        s.fill(NES_PALETTE[27])
        font = pygame.font.SysFont(None, 30)
        title = font.render("WORLD MAP", True, NES_PALETTE[33])
        s.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        world_size = 40
        for world in range(1,8+1):
            row = (world-1)//4
            col = (world-1)%4
            x = 30 + col*70
            y = 70 + row*70
            theme = WORLD_THEMES[world]
            if world in state.unlocked_worlds:
                pygame.draw.rect(s, NES_PALETTE[theme["ground"]], (x,y,world_size,world_size))
                pygame.draw.rect(s, NES_PALETTE[theme["block"]],  (x+5,y+5,world_size-10,world_size-10))
            else:
                pygame.draw.rect(s, NES_PALETTE[0], (x,y,world_size,world_size))
                pygame.draw.rect(s, NES_PALETTE[28],(x+5,y+5,world_size-10,world_size-10))
                pygame.draw.line(s, NES_PALETTE[33], (x,y), (x+world_size,y+world_size), 3)
                pygame.draw.line(s, NES_PALETTE[33], (x+world_size,y), (x,y+world_size), 3)
            world_font = pygame.font.SysFont(None, 20)
            world_text = world_font.render(f"{world}", True, NES_PALETTE[39])
            s.blit(world_text, (x + world_size//2 - world_text.get_width()//2,
                                y + world_size//2 - world_text.get_height()//2))
            if world == self.selection:
                name_font = pygame.font.SysFont(None, 14)
                name_text = name_font.render(theme["name"], True, NES_PALETTE[39])
                s.blit(name_text, (WIDTH//2 - name_text.get_width()//2, HEIGHT - 40))
        row = (self.selection-1)//4
        col = (self.selection-1)%4
        x = 30 + col*70
        y = 70 + row*70
        cursor_offset = math.sin(self.cursor_timer * 5) * 3
        pygame.draw.rect(s, NES_PALETTE[39], (x-5, y-5 + cursor_offset, world_size+10, 5))
        pygame.draw.rect(s, NES_PALETTE[39], (x-5, y+world_size + cursor_offset, world_size+10, 5))
        mario_x = x + world_size//2 - 8
        mario_y = y - 30 + cursor_offset
        pygame.draw.rect(s, NES_PALETTE[33], (mario_x+4, mario_y+8, 8, 8))
        pygame.draw.rect(s, NES_PALETTE[39], (mario_x+4, mario_y, 8, 8))
        font = pygame.font.SysFont(None, 14)
        text = font.render("Arrow keys: Move  Enter: Select  Esc: Back", True, NES_PALETTE[39])
        s.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 20))
        unlocked_text = font.render(f"Unlocked Worlds: {max(state.unlocked_worlds)}/8", True, NES_PALETTE[39])
        s.blit(unlocked_text, (10, HEIGHT - 20))

# ---------- EDITORS ----------
PALETTE_LEVEL = [' ', 'G', 'B', 'P', 'T', '?', 'S', 'F', 'g', 'k', 'f', 's']
PALETTE_LABELS = ['(empty)','Ground','Brick','Platform','Pipe','Question','Start','Flag','Goomba','Koopa','Fish','Spike']

class OverworldEditor(Scene):
    def __init__(self):
        self.grid = state.overworld_map
        self.cursor = [3, 3]  # row, col
        self.selection = "path"
        self.tile_keys = ["empty","path","grass","desert","water","pipe","level","castle","start"]
        self.msg = "Overworld Editor: Arrows move, 1-9 select, Click to paint, L: open LevelEditor, Esc: back"
        self.button_rects = {}

    def handle(self, events, keys):
        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE: replace(TitleScreen())
                elif e.key == K_LEFT:  self.cursor[1] = max(0, self.cursor[1]-1)
                elif e.key == K_RIGHT: self.cursor[1] = min(7, self.cursor[1]+1)
                elif e.key == K_UP:    self.cursor[0] = max(0, self.cursor[0]-1)
                elif e.key == K_DOWN:  self.cursor[0] = min(7, self.cursor[0]+1)
                elif K_1 <= e.key <= K_9:
                    idx = e.key - K_1
                    if idx < len(self.tile_keys):
                        self.selection = self.tile_keys[idx]
                elif e.key == K_l:
                    r, c = self.cursor
                    t = self.grid[r][c]
                    # if it's not a level, make it one
                    if t["type"] != "level":
                        t["type"] = "level"
                        # Auto assign a level id based on world 1
                        # Try to find an unused slot
                        world = state.editing_world
                        for i in range(1,5):
                            candidate = f"{world}-{i}"
                            if t.get("level") is None or t["level"] not in LEVELS:
                                t["level"] = candidate
                                break
                            if candidate not in LEVELS:
                                t["level"] = candidate
                                break
                        if t.get("level") is None:
                            t["level"] = f"{world}-1"
                    # open level editor
                    state.editing_level = t["level"]
                    replace(LevelEditor(state.editing_level))
            elif e.type == MOUSEBUTTONDOWN and e.button in (1,3):
                mx, my = e.pos
                # Grid at (40,60) cell size 40x40
                gx = (mx - 40) // 40
                gy = (my - 60) // 40
                if 0 <= gx < 8 and 0 <= gy < 8:
                    self.cursor = [gy, gx]
                    t = self.grid[gy][gx]
                    if e.button == 1:
                        t["type"] = self.selection
                        if self.selection == "level" and not t.get("level"):
                            t["level"] = f"{state.editing_world}-1"
                        if self.selection != "level":
                            t["level"] = None
                # Buttons
                for name, rect in self.button_rects.items():
                    if rect.collidepoint(mx, my):
                        if name == "back": replace(TitleScreen())
                        elif name == "save": self.save_overworld()
                        elif name == "load": self.load_overworld()
                        elif name == "export": self.export_project()
                        elif name == "play": replace(WorldMapScene())

    def save_overworld(self, path="overworld.json"):
        with open(path, "w") as f:
            json.dump(self.grid, f, indent=2)
        self.msg = f"Saved overworld to {path}"

    def load_overworld(self, path="overworld.json"):
        if os.path.exists(path):
            with open(path) as f:
                state.overworld_map = json.load(f)
            self.grid = state.overworld_map
            self.msg = f"Loaded overworld from {path}"
        else:
            self.msg = "No overworld.json found."

    def export_project(self, out_zip="koopa_project.zip"):
        # write overworld + levels json
        tmp_over = "_overworld.json"
        tmp_levels = "_levels.json"
        with open(tmp_over, "w") as f: json.dump(state.overworld_map, f, indent=2)
        with open(tmp_levels, "w") as f: json.dump(LEVELS, f, indent=2)
        with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(tmp_over, "overworld.json")
            z.write(tmp_levels, "levels.json")
        os.remove(tmp_over); os.remove(tmp_levels)
        self.msg = f"Exported project to {out_zip}"

    def update(self, dt): pass

    def draw(self, s):
        s.fill(NES_PALETTE[27])
        font = pygame.font.SysFont(None, 24)
        title = font.render("OVERWORLD EDITOR", True, NES_PALETTE[39])
        s.blit(title, (WIDTH//2 - title.get_width()//2, 10))
        # Draw grid
        ox, oy = 40, 60
        for r in range(8):
            for c in range(8):
                tile = self.grid[r][c]
                img = state.overworld_tile_images[tile["type"]]
                s.blit(img, (ox + c*40, oy + r*40))
                if tile["type"] == "level" and tile.get("level"):
                    fid = pygame.font.SysFont(None, 16).render(tile["level"], True, NES_PALETTE[39])
                    s.blit(fid, (ox + c*40 + 2, oy + r*40 + 10))
                pygame.draw.rect(s, NES_PALETTE[0], (ox + c*40, oy + r*40, 40, 40), 1)
        # Cursor
        r, c = self.cursor
        pygame.draw.rect(s, NES_PALETTE[39], (ox + c*40-2, oy + r*40-2, 44, 44), 2)
        # Palette (right side)
        pox, poy = WIDTH - 120, 60
        pfont = pygame.font.SysFont(None, 18)
        for i, key in enumerate(self.tile_keys):
            img = state.overworld_tile_images[key]
            x = pox; y = poy + i*34
            s.blit(img, (x, y))
            lab = pfont.render(key, True, NES_PALETTE[39])
            s.blit(lab, (x+30, y+4))
            if key == self.selection:
                pygame.draw.rect(s, NES_PALETTE[39], (x-2,y-2, 28, 28), 2)
        # Buttons
        bx = 40; by = HEIGHT - 40
        names = ["back","save","load","export","play"]
        self.button_rects = {}
        for i, name in enumerate(names):
            img = state.buttons[name]
            rect = pygame.Rect(bx + i*90, by, img.get_width(), img.get_height())
            s.blit(img, rect.topleft)
            self.button_rects[name] = rect
        # Message
        m = pygame.font.SysFont(None, 18).render(self.msg, True, NES_PALETTE[39])
        s.blit(m, (40, HEIGHT - 70))

class LevelEditor(Scene):
    def __init__(self, level_id):
        self.level_id = level_id
        self.rows = [list(r) for r in LEVELS[level_id]]
        self.camx = 0
        self.selection_idx = 1  # Start on 'G'
        self.cell_w = TILE
        self.cell_h = TILE
        self.msg = f"Level Editor {level_id}: Arrows scroll, LClick: paint, RClick: erase, 1-9/0: choose, S: save, P: play, Esc: back"
        self.button_rects = {}

    def handle(self, events, keys):
        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    replace(OverworldEditor())
                elif e.key == K_LEFT:  self.camx = max(0, self.camx - 80)
                elif e.key == K_RIGHT: self.camx = min(len(self.rows[0])*TILE - WIDTH, self.camx + 80)
                elif e.key in (K_1,K_2,K_3,K_4,K_5,K_6,K_7,K_8,K_9,K_0):
                    # map to palette index
                    keymap = {K_1:0, K_2:1, K_3:2, K_4:3, K_5:4, K_6:5, K_7:6, K_8:7, K_9:8, K_0:9}
                    self.selection_idx = keymap[e.key] if e.key != K_0 else 9
                elif e.key == K_s:
                    self.save_level()
                elif e.key == K_p:
                    # bake and test-play
                    self.apply_to_global()
                    replace(LevelScene(self.level_id))
            elif e.type == MOUSEBUTTONDOWN:
                mx, my = e.pos
                if my < HEIGHT - 64:  # canvas
                    tx = (mx + self.camx) // self.cell_w
                    ty = (my) // self.cell_h
                    if 0 <= ty < len(self.rows) and 0 <= tx < len(self.rows[0]):
                        if e.button == 1:
                            self.rows[ty][tx] = PALETTE_LEVEL[self.selection_idx]
                        elif e.button == 3:
                            self.rows[ty][tx] = ' '
                # buttons
                for name, rect in self.button_rects.items():
                    if rect.collidepoint(mx, my):
                        if name == "back": replace(OverworldEditor())
                        elif name == "save": self.save_level()
                        elif name == "play": self.apply_to_global(); replace(LevelScene(self.level_id))

    def apply_to_global(self):
        # push back to LEVELS and refresh thumbnail
        LEVELS[self.level_id] = ["".join(r) for r in self.rows]
        THUMBNAILS[self.level_id] = build_thumbnail(self.level_id, LEVELS[self.level_id])

    def save_level(self, path="levels.json"):
        # Bake changes then write all levels (simple route)
        self.apply_to_global()
        with open(path, "w") as f:
            json.dump(LEVELS, f, indent=2)
        self.msg = f"Saved all levels to {path}"

    def update(self, dt): pass

    def draw(self, s):
        s.fill(NES_PALETTE[27])
        # Backdrop
        pygame.draw.rect(s, NES_PALETTE[0], (0, 0, WIDTH, 20))
        f = pygame.font.SysFont(None, 16)
        hdr = f.render(self.msg, True, NES_PALETTE[39])
        s.blit(hdr, (8, 2))

        # Grid canvas
        ox = -self.camx
        for y, row in enumerate(self.rows):
            for x, ch in enumerate(row):
                dx = x*TILE + ox
                if -TILE <= dx <= WIDTH:
                    img = state.tile_images.get(ch, state.tile_images[' '])
                    s.blit(img, (dx, y*TILE))
                if state.show_grid and -TILE <= dx <= WIDTH:
                    pygame.draw.rect(s, NES_PALETTE[41], (dx, y*TILE, TILE, TILE), 1)

        # Palette bar (bottom)
        bar_y = HEIGHT - 64
        pygame.draw.rect(s, NES_PALETTE[0], (0, bar_y, WIDTH, 64))
        for i, ch in enumerate(PALETTE_LEVEL):
            x = 12 + i*44
            img = state.tile_images.get(ch, state.tile_images[' '])
            s.blit(img, (x, bar_y + 10))
            lbl = f"{i+1 if i<9 else 0}:{PALETTE_LABELS[i]}"
            txt = f.render(lbl, True, NES_PALETTE[39])
            s.blit(txt, (x-6, bar_y + 32))
            if i == self.selection_idx:
                pygame.draw.rect(s, NES_PALETTE[39], (x-2, bar_y + 8, TILE+4, TILE+4), 2)

        # Buttons
        names = ["back","save","play"]
        self.button_rects = {}
        bx = WIDTH - 280; by = HEIGHT - 56
        for i, name in enumerate(names):
            img = state.buttons[name]
            rect = pygame.Rect(bx + i*92, by, img.get_width(), img.get_height())
            s.blit(img, rect.topleft)
            self.button_rects[name] = rect

# ---------- GAMEPLAY ----------
class LevelScene(Scene):
    def __init__(self, level_id):
        self.map = TileMap(LEVELS[level_id], level_id)
        self.player = Player(50, 100)
        self.enemies = []
        self.cam = 0.0
        self.level_id = level_id
        self.time = 300
        self.coins = 0
        self.end_level = False
        self.end_timer = 0
        world = int(level_id.split("-")[0])
        self.theme = WORLD_THEMES[world]
        # Parse dynamic things (DO NOT add to tiles)
        for y, row in enumerate(LEVELS[level_id]):
            for x, ch in enumerate(row):
                if ch == "S":
                    self.player.x, self.player.y = x*TILE, y*TILE
                elif ch == "g":
                    self.enemies.append(Goomba(x*TILE, y*TILE))
                elif ch == "k":
                    self.enemies.append(Koopa(x*TILE, y*TILE))
                elif ch == "f":
                    self.enemies.append(Fish(x*TILE, y*TILE))
                elif ch == "s":
                    self.enemies.append(Spike(x*TILE, y*TILE))

    def handle(self, evts, keys):
        for e in evts:
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                replace(WorldMapScene())

    def update(self, dt):
        self.time = max(0, self.time - dt)
        self.player.update(self.map.colliders, dt, self.enemies)
        for enemy in self.enemies:
            if enemy.active: enemy.update(self.map.colliders, dt)
        target = self.player.x - WIDTH // 2
        self.cam += (target - self.cam) * 0.1
        self.cam = max(0, min(self.cam, self.map.width - WIDTH))
        if self.player.x > self.map.width - 100 and not self.end_level:
            self.end_level = True; self.end_timer = 1.5
        if self.end_level:
            self.end_timer -= dt
            if self.end_timer <= 0:
                w, l = map(int, self.level_id.split("-"))
                if l < 4:
                    replace(LevelScene(f"{w}-{l+1}"))
                else:
                    if w < 8 and (w+1) not in state.unlocked_worlds:
                        state.unlocked_worlds.append(w+1)
                    replace(WorldMapScene())

    def draw(self, s):
        self.map.draw(s, self.cam)
        for enemy in self.enemies: enemy.draw(s, self.cam)
        self.player.draw(s, self.cam)
        # HUD bar
        pygame.draw.rect(s, NES_PALETTE[0], (0, 0, WIDTH, 20))
        font = pygame.font.SysFont(None, 16)
        score_text = font.render(f"SCORE {state.score:06d}", True, NES_PALETTE[39])
        s.blit(score_text, (10, 4))
        coin_text = font.render(f"COINS {state.coins:02d}", True, NES_PALETTE[39])
        s.blit(coin_text, (180, 4))
        world_text = font.render(f"WORLD {self.level_id}", True, NES_PALETTE[39])
        s.blit(world_text, (WIDTH//2 - world_text.get_width()//2, 4))
        time_text = font.render(f"TIME {int(self.time):03d}", True, NES_PALETTE[39])
        s.blit(time_text, (WIDTH - 140, 4))
        lives_text = font.render(f"x{state.lives}", True, NES_PALETTE[39])
        s.blit(lives_text, (WIDTH - 60, 4))
        pygame.draw.rect(s, NES_PALETTE[33], (WIDTH - 80, 6, 8, 8))
        pygame.draw.rect(s, NES_PALETTE[39], (WIDTH - 80, 2, 8, 8))
        theme_text = font.render(self.theme["name"], True, NES_PALETTE[39])
        s.blit(theme_text, (WIDTH//2 - theme_text.get_width()//2, HEIGHT - 20))

# ---- Minimal Game Over scene ----
class GameOverScene(Scene):
    def __init__(self):
        self.t = 0
    def handle(self, events, keys):
        for e in events:
            if e.type == KEYDOWN and e.key in (K_RETURN, K_SPACE):
                state.lives = 3; state.score = 0; replace(TitleScreen())
    def update(self, dt): self.t += dt
    def draw(self, s):
        s.fill(NES_PALETTE[0])
        f = pygame.font.SysFont(None, 48)
        txt = f.render("GAME OVER", True, NES_PALETTE[39])
        s.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 30))
        f2 = pygame.font.SysFont(None, 20)
        tip = f2.render("Press Enter to continue", True, NES_PALETTE[33])
        s.blit(tip, (WIDTH//2 - tip.get_width()//2, HEIGHT//2 + 20))

# ---- Main ----
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("KOOPA ENGINE 1.1 - Full")
    clock = pygame.time.Clock()
    replace(TitleScreen())
    while SCENES:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        for e in events:
            if e.type == QUIT:
                pygame.quit(); sys.exit()
            elif e.type == KEYDOWN and e.key == K_F11:
                pygame.display.toggle_fullscreen()
        scene = SCENES[-1]
        scene.handle(events, keys)
        scene.update(dt)
        scene.draw(screen)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
