import pygame
import sys
import random

# --- Constants ---
WIDTH, HEIGHT = 600, 400
FPS = 60
TILE = 20
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (40, 80, 255)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 80)

# --- ASCII Tiles ---
TILEMAP = {
    ' ': None, # Empty
    '#': BROWN, # Block
    '?': YELLOW, # Question
    'M': RED, # Mario (drawn separately)
    'E': GREEN, # Enemy
    'X': BLUE, # Exit flag
    'G': (60,200,60), # Grass
}

# --- Simple Level Generator ---
def gen_level(world, level):
    rows = 20
    cols = WIDTH // TILE
    level = [[' ' for _ in range(cols)] for _ in range(rows)]
    # Base ground
    for x in range(cols):
        level[rows-2][x] = 'G'
        level[rows-1][x] = '#'
    # Add blocks
    for _ in range(5 + world*2):
        x = random.randint(5, cols-6)
        y = random.randint(8, rows-6)
        level[y][x] = '#'
    # Add ? blocks
    for _ in range(3):
        x = random.randint(5, cols-6)
        y = random.randint(6, rows-10)
        level[y][x] = '?'
    # Add enemies
    for _ in range(2+level):
        x = random.randint(8, cols-8)
        y = rows-3
        level[y][x] = 'E'
    # Place exit flag
    level[rows-3][cols-2] = 'X'
    return level

# --- Player (Mario) ---
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.score = 0
        self.lives = 3
    def rect(self):
        return pygame.Rect(self.x, self.y, TILE, TILE)

# --- Draw Functions ---
def draw_tile(surf, kind, x, y):
    if kind and kind in TILEMAP:
        color = TILEMAP[kind]
        pygame.draw.rect(surf, color, (x*TILE, y*TILE, TILE, TILE))
        # ? block dots
        if kind == '?':
            pygame.draw.circle(surf, (220,220,0), (x*TILE+TILE//2, y*TILE+TILE//2), 4)
        # Grass tufts
        if kind == 'G':
            pygame.draw.line(surf, (34,139,34), (x*TILE+4, y*TILE+18), (x*TILE+16, y*TILE+18), 2)
        # Exit flag
        if kind == 'X':
            pygame.draw.rect(surf, WHITE, (x*TILE+14, y*TILE-16, 3, 26))
            pygame.draw.polygon(surf, BLUE, [(x*TILE+17, y*TILE-16), (x*TILE+34, y*TILE-9), (x*TILE+17, y*TILE)])
    
def draw_player(surf, px, py):
    # Simple Mario: Head, body, arms, legs
    base_x = int(px)
    base_y = int(py)
    pygame.draw.rect(surf, RED, (base_x+4, base_y, 12, 10))    # Hat
    pygame.draw.rect(surf, (255,180,120), (base_x+6, base_y+10, 8, 8))  # Face
    pygame.draw.rect(surf, BLUE, (base_x+4, base_y+18, 12, 12))  # Body
    pygame.draw.line(surf, (255,180,120), (base_x+4, base_y+18), (base_x, base_y+28), 3) # Left arm
    pygame.draw.line(surf, (255,180,120), (base_x+16, base_y+18), (base_x+20, base_y+28), 3) # Right arm
    pygame.draw.line(surf, (50,50,50), (base_x+8, base_y+30), (base_x+8, base_y+40), 3) # Left leg
    pygame.draw.line(surf, (50,50,50), (base_x+12, base_y+30), (base_x+12, base_y+40), 3) # Right leg

def draw_enemy(surf, x, y):
    # Simple goomba: body + face
    pygame.draw.ellipse(surf, (130,70,30), (x+2, y+6, 16, 14))
    pygame.draw.line(surf, BLACK, (x+6, y+14), (x+6, y+18), 2)
    pygame.draw.line(surf, BLACK, (x+14, y+14), (x+14, y+18), 2)
    pygame.draw.arc(surf, BLACK, (x+6, y+10, 8, 8), 3.14, 0, 1)

# --- Main Game Class ---
class MarioForever:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Mario Forever – 5 Worlds, 3 Levels, No PNGs!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Consolas', 18)
        self.state = 'file_select' # file_select, map, level, win, gameover
        self.selected_file = 0
        self.saves = [None, None, None]
        self.file_highlights = [0, 0, 0]
        self.world = 0
        self.level = 0
        self.map_scroll = 0
        self.player = Player(2*TILE, HEIGHT-4*TILE)
        self.level_data = None
        self.load_level()

    def load_level(self):
        if self.state == 'level':
            self.level_data = gen_level(self.world, self.level)
            self.player.x = 2*TILE
            self.player.y = HEIGHT-5*TILE
            self.player.vx = 0
            self.player.vy = 0
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if self.state == 'file_select':
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_UP:
                        self.selected_file = (self.selected_file-1)%3
                    elif e.key == pygame.K_DOWN:
                        self.selected_file = (self.selected_file+1)%3
                    elif e.key == pygame.K_RETURN:
                        # Start game
                        self.state = 'map'
                        self.world = 0
                        self.level = 0
            elif self.state == 'map':
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RIGHT:
                        self.level += 1
                        if self.level >= 3:
                            self.level = 0
                            self.world += 1
                            if self.world >= 5:
                                self.state = 'win'
                                return
                    elif e.key == pygame.K_RETURN:
                        self.state = 'level'
                        self.load_level()
            elif self.state == 'level':
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        self.state = 'map'
                        return
        # Simple controls (level only)
        if self.state == 'level':
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.vx = -3
            elif keys[pygame.K_RIGHT]:
                self.player.vx = 3
            else:
                self.player.vx = 0
            if keys[pygame.K_SPACE] and self.player.on_ground:
                self.player.vy = -9
                self.player.on_ground = False

    def update(self):
        if self.state == 'level':
            self.player.vy += 0.5 # gravity
            self.player.x += self.player.vx
            self.player.y += self.player.vy
            # Collisions (crude)
            self.player.on_ground = False
            tx = int(self.player.x//TILE)
            ty = int((self.player.y+TILE)//TILE)
            if ty < len(self.level_data) and tx < len(self.level_data[0]):
                if self.level_data[ty][tx] in ['#','G']:
                    self.player.y = ty*TILE-TILE
                    self.player.vy = 0
                    self.player.on_ground = True
            # End level
            if tx >= (WIDTH//TILE)-2 and ty >= (len(self.level_data)-4):
                self.state = 'map'
                self.level += 1
                if self.level >= 3:
                    self.level = 0
                    self.world += 1
                    if self.world >= 5:
                        self.state = 'win'
                self.load_level()
    
    def draw(self):
        self.screen.fill(BLACK)
        if self.state == 'file_select':
            self.draw_file_select()
        elif self.state == 'map':
            self.draw_map()
        elif self.state == 'level':
            self.draw_level()
        elif self.state == 'win':
            self.draw_win()
        elif self.state == 'gameover':
            self.draw_gameover()
        pygame.display.flip()
    
    def draw_file_select(self):
        title = self.font.render("MARIO FOREVER - FILE SELECT", 1, WHITE)
        self.screen.blit(title, (WIDTH//2-120, 50))
        for i in range(3):
            col = (200,200,50) if i==self.selected_file else (150,150,150)
            pygame.draw.rect(self.screen, col, (WIDTH//2-80, 120+60*i, 160, 40), 0, 12)
            ftext = self.font.render(f"File {i+1}", 1, BLACK)
            self.screen.blit(ftext, (WIDTH//2-40, 130+60*i))
        hint = self.font.render("UP/DOWN to pick, ENTER to start", 1, WHITE)
        self.screen.blit(hint, (WIDTH//2-140, 320))
    
    def draw_map(self):
        title = self.font.render(f"WORLD {self.world+1} - MAP", 1, WHITE)
        self.screen.blit(title, (WIDTH//2-80, 50))
        # Simple map: dots for levels
        for w in range(5):
            for l in range(3):
                x = WIDTH//2-120+80*l
                y = 120+40*w
                col = GREEN if (w==self.world and l==self.level) else (90,90,90)
                pygame.draw.circle(self.screen, col, (x, y), 16)
                ltext = self.font.render(f"{w+1}-{l+1}", 1, BLACK)
                self.screen.blit(ltext, (x-14, y-8))
        hint = self.font.render("RIGHT=Next, ENTER=Play, ESC=Quit", 1, WHITE)
        self.screen.blit(hint, (WIDTH//2-160, 320))
    
    def draw_level(self):
        for y, row in enumerate(self.level_data):
            for x, cell in enumerate(row):
                draw_tile(self.screen, cell, x, y)
                if cell == 'E':
                    draw_enemy(self.screen, x*TILE, y*TILE)
                if cell == 'X':
                    pygame.draw.rect(self.screen, BLUE, (x*TILE+6, y*TILE-10, 8, 24))
        draw_player(self.screen, self.player.x, self.player.y)
        hud = self.font.render(f"W{self.world+1}-{self.level+1}  LIVES:{self.player.lives}", 1, WHITE)
        self.screen.blit(hud, (20, 10))
    
    def draw_win(self):
        text = self.font.render("YOU WIN! THANKS FOR PLAYING!", 1, YELLOW)
        self.screen.blit(text, (WIDTH//2-160, HEIGHT//2-20))
    def draw_gameover(self):
        text = self.font.render("GAME OVER!", 1, RED)
        self.screen.blit(text, (WIDTH//2-70, HEIGHT//2-20))

if __name__ == "__main__":
    MarioForever().run()
