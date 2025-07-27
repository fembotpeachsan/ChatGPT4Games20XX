import pygame
import sys
import random
import math
import os

# === KOOPA ENGINE 3.3 (M1 MAC EDITION) ===
# Fixed for M1 Mac compatibility - handles missing sounds gracefully

# Initialize Pygame with better M1 Mac settings
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# --- Constants & Setup ---
FPS = 60
TILE = 32
ROOM_W, ROOM_H = 16, 11
WIDTH, HEIGHT = ROOM_W * TILE, ROOM_H * TILE + 64
GRAVITY = 0.5
JUMP_POWER = -11

# --- World Grid ---
GRID_W, GRID_H = 8, 8

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY_BLUE = (104, 137, 255)
GROUND = (223, 113, 38)
BLOCK_SHADOW = (139, 69, 19)
COIN = (255, 220, 40)
PLAYER_COLOR = (229, 57, 53)
ENEMY_COLOR = (46, 125, 50)
HUD_BG = (30, 30, 40)
HEART = (230, 40, 64)
XP_BAR = (100, 160, 255)
SWORD_COLOR = (200, 200, 200)

# --- Font Loading (M1 Mac Compatible) ---
def load_fonts():
    """Load fonts with fallbacks for M1 Mac compatibility"""
    try:
        # Try system fonts first
        HUD_FONT = pygame.font.SysFont("menlo", 16, True)
        GAME_OVER_FONT = pygame.font.SysFont("menlo", 42, True)
        SUB_GAME_OVER_FONT = pygame.font.SysFont("menlo", 20, True)
    except:
        try:
            # Fallback to courier
            HUD_FONT = pygame.font.SysFont("courier", 18, True)
            GAME_OVER_FONT = pygame.font.SysFont("courier", 48, True)
            SUB_GAME_OVER_FONT = pygame.font.SysFont("courier", 22, True)
        except:
            # Final fallback to default font
            HUD_FONT = pygame.font.Font(None, 24)
            GAME_OVER_FONT = pygame.font.Font(None, 64)
            SUB_GAME_OVER_FONT = pygame.font.Font(None, 32)
    
    return HUD_FONT, GAME_OVER_FONT, SUB_GAME_OVER_FONT

HUD_FONT, GAME_OVER_FONT, SUB_GAME_OVER_FONT = load_fonts()

# --- Sound System (Optional - Won't Crash if Missing) ---
class SoundManager:
    def __init__(self):
        self.sounds_enabled = True
        self.sounds = {}
        self.load_sounds()
    
    def load_sounds(self):
        """Load sounds with graceful fallback if files missing"""
        sound_files = {
            'jump': ('jump.wav', 0.4),
            'coin': ('coin.wav', 0.6),
            'hit_player': ('player_hit.wav', 0.8),
            'hit_enemy': ('enemy_hit.wav', 0.7),
            'sword_swing': ('sword.wav', 0.5),
            'level_up': ('levelup.wav', 0.9),
            'enemy_die': ('enemy_die.wav', 0.6),
            'game_over': ('gameover.wav', 1.0)
        }
        
        for name, (filename, volume) in sound_files.items():
            try:
                # Check if file exists first
                if os.path.exists(filename):
                    sound = pygame.mixer.Sound(filename)
                    sound.set_volume(volume)
                    self.sounds[name] = sound
                else:
                    print(f"Warning: {filename} not found - sound disabled")
                    self.sounds[name] = None
            except pygame.error as e:
                print(f"Warning: Could not load {filename}: {e}")
                self.sounds[name] = None
        
        # If no sounds loaded successfully, disable sound system
        if not any(self.sounds.values()):
            self.sounds_enabled = False
            print("Sound system disabled - game will run silently")
    
    def play(self, sound_name):
        """Play a sound if available"""
        if self.sounds_enabled and sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except:
                pass  # Ignore sound errors during gameplay

# Create global sound manager
sound_manager = SoundManager()

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE-4, TILE)
        self.vx, self.vy = 0, 0
        self.hp = 6
        self.max_hp = 6
        self.xp = 0
        self.xp_to_next = 20
        self.level = 1
        self.facing = 1
        self.on_ground = False
        
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 15
        self.enemies_hit_this_swing = []
        
        self.hit_timer = 0
    
    def get_attack_rect(self):
        if self.facing == 1:
            return pygame.Rect(self.rect.right, self.rect.centery - 8, 24, 16)
        else:
            return pygame.Rect(self.rect.left - 24, self.rect.centery - 8, 24, 16)
    
    def take_damage(self, amount, knockback_source_rect):
        if self.hit_timer <= 0:
            sound_manager.play('hit_player')
            self.hp -= amount
            self.hit_timer = 90  # Invincibility frames
            self.vy = -5  # Knockback
            if knockback_source_rect.centerx > self.rect.centerx:
                self.vx = -8
            else:
                self.vx = 8
            return True
        return False
    
    def update(self, keys):
        if self.hit_timer > 0:
            self.hit_timer -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Allow movement control shortly after being hit
        if self.hit_timer < 75:
            self.vx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 4
            if self.vx > 0:
                self.facing = 1
            if self.vx < 0:
                self.facing = -1
        
        if keys[pygame.K_UP] and self.on_ground:
            sound_manager.play('jump')
            self.vy = JUMP_POWER
        
        if keys[pygame.K_z] and self.attack_cooldown <= 0 and not self.attacking:
            sound_manager.play('sword_swing')
            self.attacking = True
            self.attack_timer = 10
            self.attack_cooldown = 25
            self.enemies_hit_this_swing = []
        
        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False
        
        # Apply gravity
        self.vy += GRAVITY
        if self.vy > 8:
            self.vy = 8
    
    def move_and_collide(self, blocks):
        # Move X
        self.rect.x += int(self.vx)
        for block in blocks:
            if self.rect.colliderect(block):
                if self.vx > 0:
                    self.rect.right = block.left
                if self.vx < 0:
                    self.rect.left = block.right
        
        # Move Y
        self.rect.y += int(self.vy)
        self.on_ground = False
        for block in blocks:
            if self.rect.colliderect(block):
                if self.vy > 0:
                    self.rect.bottom = block.top
                    self.on_ground = True
                    self.vy = 0
                if self.vy < 0:
                    self.rect.top = block.bottom
                    self.vy = 0
    
    def gain_xp(self, amount):
        self.xp += amount
        leveled_up = False
        while self.xp >= self.xp_to_next:
            leveled_up = True
            self.level += 1
            self.xp -= self.xp_to_next
            self.xp_to_next = int(self.xp_to_next * 1.5)
            self.max_hp += 1
        if leveled_up:
            sound_manager.play('level_up')
            self.hp = self.max_hp  # Fully heal on level up

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE-4, TILE)
        self.vx = random.choice([-1.5, 1.5])
        self.vy = 0
        self.hp = 2
        self.on_ground = False
        self.hit_timer = 0
        self.aggro = False
        self.aggro_range = TILE * 5
    
    def take_damage(self, amount, knockback_dir):
        sound_manager.play('hit_enemy')
        self.hp -= amount
        self.hit_timer = 20
        self.vx = 4 * knockback_dir
        self.vy = -3
    
    def update_and_collide(self, blocks, player_rect):
        if self.hit_timer > 0:
            self.hit_timer -= 1
        
        # Aggro Logic
        distance_to_player = math.hypot(
            self.rect.centerx - player_rect.centerx,
            self.rect.centery - player_rect.centery
        )
        if distance_to_player < self.aggro_range:
            self.aggro = True
        
        if self.aggro and self.on_ground and self.hit_timer <= 0:
            if player_rect.centerx < self.rect.centerx:
                self.vx = -2
            else:
                self.vx = 2
        elif self.hit_timer > 0:
            # Slow down during hit stun
            self.vx *= 0.8
        else:
            # Revert to patrol if not aggro
            self.aggro = False
            if abs(self.vx) < 1:
                self.vx = random.choice([-1.5, 1.5])
        
        # Standard Physics
        self.vy += GRAVITY
        if self.vy > 8:
            self.vy = 8
        
        self.rect.x += int(self.vx)
        for block in blocks:
            if self.rect.colliderect(block):
                if self.vx > 0:
                    self.rect.right = block.left
                if self.vx < 0:
                    self.rect.left = block.right
                self.vx *= -1
        
        self.rect.y += int(self.vy)
        self.on_ground = False
        for block in blocks:
            if self.rect.colliderect(block):
                if self.vy > 0:
                    self.rect.bottom = block.top
                    self.on_ground = True
                    self.vy = 0
                if self.vy < 0:
                    self.rect.top = block.bottom
                    self.vy = 0
        
        # Ledge detection
        if self.on_ground and not self.aggro:
            probe_x = self.rect.right + 5 if self.vx > 0 else self.rect.left - 5
            ledge_probe = pygame.Rect(probe_x, self.rect.bottom + 5, 1, 1)
            found_ground = any(ledge_probe.colliderect(b) for b in blocks)
            if not found_ground:
                self.vx *= -1
    
    def draw(self, surface):
        # Flash when hit
        if self.hit_timer % 10 < 5:
            pygame.draw.rect(surface, ENEMY_COLOR, self.rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Koopa Engine 3.3: M1 Mac Edition")
        self.clock = pygame.time.Clock()
        self.game_state = 'playing'
        self.player = Player(4 * TILE, 7 * TILE)
        self.room_x, self.room_y = GRID_W // 2, GRID_H // 2
        self.rooms = self.generate_world()
        self.score = 0
    
    def generate_world(self):
        rooms = {}
        for gy in range(GRID_H):
            for gx in range(GRID_W):
                rooms[(gx, gy)] = self.generate_room(gx, gy)
        return rooms
    
    def generate_room(self, gx, gy):
        room = {'blocks': [], 'coins': [], 'enemies': []}
        
        # Create borders based on grid position
        for x in range(ROOM_W):
            if gy == 0:
                room['blocks'].append(pygame.Rect(x*TILE, 0, TILE, TILE))
            if gy == GRID_H - 1:
                room['blocks'].append(pygame.Rect(x*TILE, (ROOM_H-1)*TILE, TILE, TILE))
        
        for y in range(ROOM_H):
            if gx == 0:
                room['blocks'].append(pygame.Rect(0, y*TILE, TILE, TILE))
            if gx == GRID_W - 1:
                room['blocks'].append(pygame.Rect((ROOM_W-1)*TILE, y*TILE, TILE, TILE))
        
        # Room generation variety
        room_type = random.choice(['standard', 'pillars', 'floor_gaps'])
        
        if room_type == 'standard':
            for _ in range(random.randint(4, 8)):
                x, y = random.randint(2, ROOM_W-3), random.randint(2, ROOM_H-3)
                if not (4 < x < 10 and 4 < y < 8):
                    room['blocks'].append(pygame.Rect(x*TILE, y*TILE, TILE, TILE))
        
        elif room_type == 'pillars':
            for i in range(3, ROOM_W - 3, 3):
                h = random.randint(3, ROOM_H - 4)
                for j in range(h):
                    room['blocks'].append(pygame.Rect(i*TILE, (ROOM_H - 2 - j)*TILE, TILE, TILE))
        
        elif room_type == 'floor_gaps':
            for x in range(1, ROOM_W-1):
                if random.random() > 0.3:
                    room['blocks'].append(pygame.Rect(x*TILE, (ROOM_H-2)*TILE, TILE, TILE))
        
        # Add coins
        for _ in range(random.randint(2, 4)):
            x, y = random.randint(2, ROOM_W-3), random.randint(2, ROOM_H-3)
            room['coins'].append(pygame.Rect(x*TILE+8, y*TILE+8, 16, 16))
        
        # Add enemies (not in start room)
        if random.random() < 0.6 and not (gx == GRID_W//2 and gy == GRID_H//2):
            x, y = random.randint(3, ROOM_W-4), 3
            room['enemies'].append(Enemy(x*TILE, y*TILE))
        
        return room
    
    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif self.game_state == 'game_over':
                        running = False
            
            if self.game_state == 'playing':
                self.update_game()
            
            self.draw()
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def update_game(self):
        keys = pygame.key.get_pressed()
        current_room = self.rooms[(self.room_x, self.room_y)]
        
        self.player.update(keys)
        self.player.move_and_collide(current_room['blocks'])
        
        # Update enemies
        for enemy in current_room['enemies']:
            enemy.update_and_collide(current_room['blocks'], self.player.rect)
            if self.player.rect.colliderect(enemy.rect):
                self.player.take_damage(1, enemy.rect)
        
        # Player attack collision
        if self.player.attacking:
            attack_r = self.player.get_attack_rect()
            for enemy in current_room['enemies']:
                if enemy not in self.player.enemies_hit_this_swing and attack_r.colliderect(enemy.rect):
                    knockback_dir = 1 if self.player.facing == 1 else -1
                    enemy.take_damage(1, knockback_dir)
                    self.player.enemies_hit_this_swing.append(enemy)
        
        # Remove dead enemies
        for enemy in current_room['enemies'][:]:
            if enemy.hp <= 0:
                sound_manager.play('enemy_die')
                current_room['enemies'].remove(enemy)
                self.score += 10
                self.player.gain_xp(8)
        
        # Coin collision
        for coin in current_room['coins'][:]:
            if self.player.rect.colliderect(coin):
                sound_manager.play('coin')
                current_room['coins'].remove(coin)
                self.score += 1
                self.player.gain_xp(2)
        
        if self.player.hp <= 0:
            sound_manager.play('game_over')
            self.game_state = 'game_over'
        
        # Room transitions
        if self.player.rect.right < 0 and self.room_x > 0:
            self.room_x -= 1
            self.player.rect.left = WIDTH - TILE
        elif self.player.rect.left > WIDTH - TILE and self.room_x < GRID_W - 1:
            self.room_x += 1
            self.player.rect.right = TILE
        elif self.player.rect.bottom < TILE and self.room_y > 0:
            self.room_y -= 1
            self.player.rect.top = (ROOM_H-2)*TILE - self.player.rect.height
        elif self.player.rect.top > (ROOM_H-2)*TILE and self.room_y < GRID_H - 1:
            self.room_y += 1
            self.player.rect.bottom = TILE
    
    def draw_hud(self):
        # Main HUD container
        pygame.draw.rect(self.screen, HUD_BG, (0, HEIGHT-64, WIDTH, 64))
        
        # Health
        for i in range(self.player.max_hp):
            color = HEART if i < self.player.hp else (50, 30, 30)
            pygame.draw.rect(self.screen, color, (16+i*24, HEIGHT-52, 20, 16), border_radius=4)
        
        # XP Bar
        xp_rect_bg = pygame.Rect(16, HEIGHT-30, 200, 14)
        pygame.draw.rect(self.screen, BLACK, xp_rect_bg, border_radius=4)
        if self.player.xp_to_next > 0:
            xp_width = int(xp_rect_bg.width * self.player.xp / self.player.xp_to_next)
            xp_rect_fg = pygame.Rect(xp_rect_bg.x, xp_rect_bg.y, xp_width, xp_rect_bg.height)
            pygame.draw.rect(self.screen, XP_BAR, xp_rect_fg, border_radius=4)
        
        # Text Info
        lvl_text = f'LVL {self.player.level}'
        score_text = f'SCORE: {self.score}'
        lvl_surf = HUD_FONT.render(lvl_text, True, WHITE)
        score_surf = HUD_FONT.render(score_text, True, WHITE)
        self.screen.blit(lvl_surf, (230, HEIGHT-52))
        self.screen.blit(score_surf, (230, HEIGHT-30))
        
        # Room Coords
        room_coord_text = f'ROOM: ({self.room_x - GRID_W//2}, {self.room_y - GRID_H//2})'
        room_surf = HUD_FONT.render(room_coord_text, True, WHITE)
        self.screen.blit(room_surf, (WIDTH - room_surf.get_width() - 10, HEIGHT - 30))
    
    def draw(self):
        if self.game_state == 'playing':
            self.screen.fill(SKY_BLUE)
            current_room = self.rooms[(self.room_x, self.room_y)]
            
            # Draw ground and platforms with shadows
            for block in current_room['blocks']:
                pygame.draw.rect(self.screen, BLOCK_SHADOW, block.move(0, 4))
                pygame.draw.rect(self.screen, GROUND, block)
            
            # Draw coins
            for coin in current_room['coins']:
                pygame.draw.ellipse(self.screen, COIN, coin)
            
            # Draw enemies
            for enemy in current_room['enemies']:
                enemy.draw(self.screen)
            
            # Draw Player (flash when invincible)
            if self.player.hit_timer % 10 < 5:
                pygame.draw.rect(self.screen, PLAYER_COLOR, self.player.rect)
            
            # Draw attack visual
            if self.player.attacking:
                pygame.draw.rect(self.screen, SWORD_COLOR, self.player.get_attack_rect())
            
            self.draw_hud()
        
        elif self.game_state == 'game_over':
            self.screen.fill(BLACK)
            center_x, center_y = self.screen.get_rect().center
            
            # Main "GAME OVER"
            text_surf = GAME_OVER_FONT.render("GAME OVER", True, HEART)
            self.screen.blit(text_surf, text_surf.get_rect(center=(center_x, center_y - 20)))
            
            # Final Score
            score_text = f'FINAL SCORE: {self.score}'
            score_surf = SUB_GAME_OVER_FONT.render(score_text, True, WHITE)
            self.screen.blit(score_surf, score_surf.get_rect(center=(center_x, center_y + 30)))
            
            # Quit instruction
            quit_surf = SUB_GAME_OVER_FONT.render("Press any key to quit", True, WHITE)
            self.screen.blit(quit_surf, quit_surf.get_rect(center=(center_x, center_y + 70)))


if __name__ == '__main__':
    game = Game()
    game.run()
