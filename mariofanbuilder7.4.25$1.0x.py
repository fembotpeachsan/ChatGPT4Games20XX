import pygame
import json
import math
import random
from enum import Enum

pygame.init()
pygame.mixer.init()

# Special 64 Boot Sequence
SPECIAL_64_RED = (220, 20, 60)
SPECIAL_64_GOLD = (255, 215, 0)

# Constants - Mario Worker exact specs
WINDOW_WIDTH, WINDOW_HEIGHT = 640, 480  # Mario Worker resolution
TILE_SIZE = 16  # Mario Worker uses 16x16 tiles
GRAVITY = 0.25  # Exact Mario Worker gravity
MAX_FALL_SPEED = 6
JUMP_VELOCITY = -4.5
RUN_SPEED = 2.8
WALK_SPEED = 1.4

# Mario Worker Color Palette (NES-accurate)
MARIO_RED = (172, 44, 52)
MARIO_BROWN = (140, 84, 60)
SKY_BLUE = (92, 148, 252)
BRICK_BROWN = (188, 116, 68)
PIPE_GREEN = (0, 168, 68)
QUESTION_YELLOW = (252, 188, 60)
GROUND_PATTERN = (0, 88, 248)
BLACK = (0, 0, 0)
WHITE = (252, 252, 252)

# Initialize
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Mario Worker - Special 64 Edition")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 16)
big_font = pygame.font.Font(None, 32)

# Boot sequence
def special_64_boot():
    fade_alpha = 0
    boot_timer = 0
    boot_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    while boot_timer < 180:  # 3 seconds at 60fps
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
        window.fill(BLACK)
        boot_surface.fill(SPECIAL_64_RED)
        
        if boot_timer < 60:
            fade_alpha = min(255, boot_timer * 4)
        elif boot_timer > 120:
            fade_alpha = max(0, 255 - (boot_timer - 120) * 4)
        else:
            fade_alpha = 255
            
        boot_surface.set_alpha(fade_alpha)
        window.blit(boot_surface, (0, 0))
        
        if 30 < boot_timer < 150:
            text1 = big_font.render("TEAM SPECIALEMU", True, SPECIAL_64_GOLD)
            text2 = font.render("AGI Division Presents", True, WHITE)
            text1_rect = text1.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 20))
            text2_rect = text2.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
            window.blit(text1, text1_rect)
            window.blit(text2, text2_rect)
            
        pygame.display.flip()
        clock.tick(60)
        boot_timer += 1
    
    return True

# Tile types enum
class TileType(Enum):
    GROUND = 1
    BRICK = 2
    QUESTION = 3
    PIPE_TOP_LEFT = 4
    PIPE_TOP_RIGHT = 5
    PIPE_BODY_LEFT = 6
    PIPE_BODY_RIGHT = 7
    CLOUD_LEFT = 8
    CLOUD_CENTER = 9
    CLOUD_RIGHT = 10
    BUSH_LEFT = 11
    BUSH_CENTER = 12
    BUSH_RIGHT = 13
    COIN = 14
    HARD_BLOCK = 15
    CASTLE_BRICK = 16

# Mario Worker tile renderer
def draw_tile(surface, tile_type, x, y):
    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
    
    if tile_type == TileType.GROUND:
        # Classic Mario ground pattern
        surface.fill(BRICK_BROWN, rect)
        for px in range(0, TILE_SIZE, 4):
            for py in range(0, TILE_SIZE, 4):
                if (px + py) % 8 == 0:
                    pygame.draw.rect(surface, MARIO_BROWN, (x+px, y+py, 2, 2))
                    
    elif tile_type == TileType.BRICK:
        surface.fill(BRICK_BROWN, rect)
        pygame.draw.line(surface, MARIO_BROWN, (x, y+TILE_SIZE//2), (x+TILE_SIZE, y+TILE_SIZE//2))
        pygame.draw.line(surface, MARIO_BROWN, (x+TILE_SIZE//2, y), (x+TILE_SIZE//2, y+TILE_SIZE//2))
        pygame.draw.line(surface, MARIO_BROWN, (x, y+TILE_SIZE), (x+TILE_SIZE, y+TILE_SIZE))
        
    elif tile_type == TileType.QUESTION:
        surface.fill(QUESTION_YELLOW, rect)
        pygame.draw.rect(surface, MARIO_BROWN, rect, 1)
        # Draw question mark
        qmark = font.render("?", True, WHITE)
        qrect = qmark.get_rect(center=(x+TILE_SIZE//2, y+TILE_SIZE//2))
        surface.blit(qmark, qrect)
        
    elif tile_type in [TileType.PIPE_TOP_LEFT, TileType.PIPE_TOP_RIGHT, 
                       TileType.PIPE_BODY_LEFT, TileType.PIPE_BODY_RIGHT]:
        surface.fill(PIPE_GREEN, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)
        
    elif tile_type == TileType.COIN:
        pygame.draw.circle(surface, QUESTION_YELLOW, (x+TILE_SIZE//2, y+TILE_SIZE//2), 6)
        pygame.draw.circle(surface, MARIO_BROWN, (x+TILE_SIZE//2, y+TILE_SIZE//2), 6, 1)
        
    elif tile_type == TileType.HARD_BLOCK:
        surface.fill((128, 128, 128), rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

# Mario sprite class
class Mario:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.width = 12
        self.height = 16
        self.on_ground = False
        self.facing_right = True
        self.running = False
        self.animation_timer = 0
        self.state = "small"  # small, big, fire
        
    def update(self, tiles, keys):
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.facing_right = False
            if keys[pygame.K_LSHIFT] or keys[pygame.K_z]:
                self.vx = -RUN_SPEED
                self.running = True
            else:
                self.vx = -WALK_SPEED
                self.running = False
        elif keys[pygame.K_RIGHT]:
            self.facing_right = True
            if keys[pygame.K_LSHIFT] or keys[pygame.K_z]:
                self.vx = RUN_SPEED
                self.running = True
            else:
                self.vx = WALK_SPEED
                self.running = False
        else:
            self.vx *= 0.85  # Friction
            self.running = False
            
        # Gravity
        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED
            
        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = JUMP_VELOCITY
            
        # Move and collide
        self.x += self.vx
        self.check_tile_collision(tiles, True)
        self.y += self.vy
        self.on_ground = False
        self.check_tile_collision(tiles, False)
        
        # Animation
        self.animation_timer += 1
        
    def check_tile_collision(self, tiles, horizontal):
        mario_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for tile_x, tile_y, tile_type in tiles:
            if tile_type == TileType.COIN:
                continue
                
            tile_rect = pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE)
            
            if mario_rect.colliderect(tile_rect):
                if horizontal:
                    if self.vx > 0:
                        self.x = tile_x - self.width
                    else:
                        self.x = tile_x + TILE_SIZE
                    self.vx = 0
                else:
                    if self.vy > 0:
                        self.y = tile_y - self.height
                        self.vy = 0
                        self.on_ground = True
                    else:
                        self.y = tile_y + TILE_SIZE
                        self.vy = 0
                        
    def draw(self, surface, camera_x, camera_y):
        # Simple Mario sprite
        x = int(self.x - camera_x)
        y = int(self.y - camera_y)
        
        if self.state == "small":
            # Head
            pygame.draw.rect(surface, MARIO_RED, (x+2, y, 8, 6))
            # Body
            pygame.draw.rect(surface, MARIO_RED, (x, y+6, 12, 6))
            # Overalls
            pygame.draw.rect(surface, (0, 0, 252), (x+2, y+8, 8, 4))
            # Face
            pygame.draw.rect(surface, (252, 188, 116), (x+4, y+2, 4, 4))

# Enemy classes
class Goomba:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = -0.5
        self.vy = 0
        self.width = 16
        self.height = 16
        self.animation_timer = 0
        
    def update(self, tiles):
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy
        
        # Simple collision
        for tile_x, tile_y, tile_type in tiles:
            if tile_type == TileType.COIN:
                continue
            tile_rect = pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE)
            enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if enemy_rect.colliderect(tile_rect):
                if self.vy > 0:
                    self.y = tile_y - self.height
                    self.vy = 0
                if abs(self.vx) > 0:
                    self.vx = -self.vx
                    
        self.animation_timer += 1
        
    def draw(self, surface, camera_x, camera_y):
        x = int(self.x - camera_x)
        y = int(self.y - camera_y)
        # Simple goomba
        pygame.draw.ellipse(surface, MARIO_BROWN, (x, y+4, 16, 12))
        pygame.draw.rect(surface, MARIO_BROWN, (x+4, y+12, 3, 4))
        pygame.draw.rect(surface, MARIO_BROWN, (x+9, y+12, 3, 4))

# Level data structure
class Level:
    def __init__(self):
        self.tiles = []
        self.enemies = []
        self.width = 320  # 20 screens wide
        self.height = 15  # 15 tiles high
        self.start_x = 32
        self.start_y = 200
        self.theme = "overworld"  # overworld, underground, castle, water
        
    def add_tile(self, x, y, tile_type):
        # Snap to grid
        grid_x = (x // TILE_SIZE) * TILE_SIZE
        grid_y = (y // TILE_SIZE) * TILE_SIZE
        # Remove existing tile at position
        self.tiles = [(tx, ty, tt) for tx, ty, tt in self.tiles 
                      if tx != grid_x or ty != grid_y]
        # Add new tile
        self.tiles.append((grid_x, grid_y, tile_type))
        
    def remove_tile(self, x, y):
        grid_x = (x // TILE_SIZE) * TILE_SIZE
        grid_y = (y // TILE_SIZE) * TILE_SIZE
        self.tiles = [(tx, ty, tt) for tx, ty, tt in self.tiles 
                      if tx != grid_x or ty != grid_y]
                      
    def add_enemy(self, x, y, enemy_type):
        self.enemies.append((x, y, enemy_type))

# Editor state
class Editor:
    def __init__(self):
        self.camera_x = 0
        self.camera_y = 0
        self.selected_tile = TileType.GROUND
        self.grid_visible = True
        self.test_mode = False
        self.current_level = Level()
        self.mario = None
        
        # Create default level floor
        for x in range(0, 50 * TILE_SIZE, TILE_SIZE):
            self.current_level.add_tile(x, 13 * TILE_SIZE, TileType.GROUND)
            self.current_level.add_tile(x, 14 * TILE_SIZE, TileType.GROUND)
            
    def handle_mouse(self, mouse_x, mouse_y, left_click, right_click):
        if self.test_mode:
            return
            
        world_x = mouse_x + self.camera_x
        world_y = mouse_y + self.camera_y
        
        if left_click:
            self.current_level.add_tile(world_x, world_y, self.selected_tile)
        elif right_click:
            self.current_level.remove_tile(world_x, world_y)
            
    def start_test(self):
        self.test_mode = True
        self.mario = Mario(self.current_level.start_x, self.current_level.start_y)
        self.test_enemies = []
        for ex, ey, et in self.current_level.enemies:
            if et == "goomba":
                self.test_enemies.append(Goomba(ex, ey))
                
    def stop_test(self):
        self.test_mode = False
        self.mario = None
        self.test_enemies = []
        
    def update(self, keys):
        if self.test_mode and self.mario:
            self.mario.update(self.current_level.tiles, keys)
            # Camera follow Mario
            self.camera_x = self.mario.x - WINDOW_WIDTH // 2
            self.camera_x = max(0, min(self.camera_x, 
                                      self.current_level.width * TILE_SIZE - WINDOW_WIDTH))
                                      
            for enemy in self.test_enemies:
                enemy.update(self.current_level.tiles)
        else:
            # Editor camera movement
            cam_speed = 8
            if keys[pygame.K_LEFT]:
                self.camera_x -= cam_speed
            if keys[pygame.K_RIGHT]:
                self.camera_x += cam_speed
            if keys[pygame.K_UP]:
                self.camera_y -= cam_speed
            if keys[pygame.K_DOWN]:
                self.camera_y += cam_speed
                
            self.camera_x = max(0, self.camera_x)
            self.camera_y = max(0, self.camera_y)
            
    def draw(self, surface):
        # Background
        if self.current_level.theme == "overworld":
            surface.fill(SKY_BLUE)
        elif self.current_level.theme == "underground":
            surface.fill(BLACK)
        else:
            surface.fill((32, 32, 32))
            
        # Draw tiles
        for tile_x, tile_y, tile_type in self.current_level.tiles:
            if (-TILE_SIZE < tile_x - self.camera_x < WINDOW_WIDTH and
                -TILE_SIZE < tile_y - self.camera_y < WINDOW_HEIGHT):
                draw_tile(surface, tile_type, 
                         int(tile_x - self.camera_x), 
                         int(tile_y - self.camera_y))
                         
        # Draw enemies in test mode
        if self.test_mode:
            for enemy in self.test_enemies:
                enemy.draw(surface, self.camera_x, self.camera_y)
                
        # Draw Mario in test mode
        if self.test_mode and self.mario:
            self.mario.draw(surface, self.camera_x, self.camera_y)
            
        # Grid overlay
        if self.grid_visible and not self.test_mode:
            for x in range(0, WINDOW_WIDTH, TILE_SIZE):
                pygame.draw.line(surface, (200, 200, 200), (x, 0), (x, WINDOW_HEIGHT))
            for y in range(0, WINDOW_HEIGHT, TILE_SIZE):
                pygame.draw.line(surface, (200, 200, 200), (0, y), (WINDOW_WIDTH, y))
                
        # UI overlay
        if not self.test_mode:
            # Toolbar background
            pygame.draw.rect(surface, BLACK, (0, 0, WINDOW_WIDTH, 32))
            pygame.draw.rect(surface, WHITE, (0, 0, WINDOW_WIDTH, 32), 1)
            
            # Draw tile palette
            palette_x = 8
            for i, tile_type in enumerate(TileType):
                if i > 8:  # Limit palette display
                    break
                tile_rect = pygame.Rect(palette_x, 8, TILE_SIZE, TILE_SIZE)
                draw_tile(surface, tile_type, palette_x, 8)
                if tile_type == self.selected_tile:
                    pygame.draw.rect(surface, WHITE, tile_rect, 2)
                palette_x += TILE_SIZE + 4
                
            # Mode indicator
            mode_text = font.render("TEST MODE - Press ESC to exit" if self.test_mode 
                                  else "EDIT MODE - Press Q to test", True, WHITE)
            surface.blit(mode_text, (WINDOW_WIDTH - 200, 8))
            
            # Instructions
            inst_y = WINDOW_HEIGHT - 60
            instructions = [
                "Left Click: Place Tile | Right Click: Remove",
                "Arrow Keys: Move Camera | G: Toggle Grid",
                "1-8: Select Tile | Q: Test Level | ESC: Exit Test"
            ]
            for inst in instructions:
                text = font.render(inst, True, WHITE)
                surface.blit(text, (8, inst_y))
                inst_y += 16

# Main game loop
def main():
    if not special_64_boot():
        return
        
    editor = Editor()
    running = True
    
    while running:
        keys = pygame.key.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        left_click = False
        right_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if editor.test_mode:
                        editor.stop_test()
                    else:
                        running = False
                        
                elif event.key == pygame.K_q:
                    if not editor.test_mode:
                        editor.start_test()
                        
                elif event.key == pygame.K_g:
                    editor.grid_visible = not editor.grid_visible
                    
                # Tile selection hotkeys
                elif pygame.K_1 <= event.key <= pygame.K_8:
                    tile_index = event.key - pygame.K_1
                    if tile_index < len(TileType):
                        editor.selected_tile = list(TileType)[tile_index]
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Check toolbar clicks
                    if event.pos[1] < 32:
                        palette_x = 8
                        for i, tile_type in enumerate(TileType):
                            if i > 8:
                                break
                            if palette_x <= event.pos[0] <= palette_x + TILE_SIZE:
                                editor.selected_tile = tile_type
                                break
                            palette_x += TILE_SIZE + 4
                    else:
                        left_click = True
                elif event.button == 3:
                    right_click = True
                    
        # Update
        editor.handle_mouse(mouse_x, mouse_y, left_click, right_click)
        editor.update(keys)
        
        # Draw
        editor.draw(window)
        
        # Show FPS
        fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
        window.blit(fps_text, (8, WINDOW_HEIGHT - 16))
        
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    main()
