import pygame, random, sys, math
import numpy as np
import threading
from enum import Enum

pygame.init()
W, H, TILE = 960, 540, 40
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("Super Mario Wonder - NES Style Engine")
clock = pygame.time.Clock()

# --- GAME STATES ---
class GameMode(Enum):
    TITLE = "title"
    FILE_SELECT = "file_select"
    PLAYING = "playing"
    WONDER = "wonder"
    PAUSED = "paused"

class PowerUp(Enum):
    SMALL = "small"
    BIG = "big"
    FIRE = "fire"
    ELEPHANT = "elephant"

class Badge(Enum):
    NONE = "none"
    PARACHUTE = "parachute"
    DOLPHIN_KICK = "dolphin_kick"
    WALL_CLIMB = "wall_climb"
    FLOATING_HIGH_JUMP = "floating_high_jump"
    SPEED_RUN = "speed_run"

# --- 8-BIT SOUND ENGINE ---
def make_tone(frequency, duration_ms, volume=0.18, samplerate=22050):
    t = np.linspace(0, duration_ms / 1000, int(samplerate * duration_ms / 1000), False)
    wave = 0.6 * np.sign(np.sin(2 * np.pi * frequency * t))  # NES square wave
    audio = (wave * volume * 32767).astype(np.int16)
    return pygame.mixer.Sound(buffer=audio.tobytes())

pygame.mixer.init()

# Wonder transformation melody
wonder_melody = [
    (784, 200), (880, 200), (988, 200), (1047, 200), (988, 200), (880, 200),
    (784, 300), (0, 100), (1047, 400), (1175, 600)
]

# Title melody
title_melody = [
    (523, 300), (659, 300), (784, 300), (659, 300), (523, 300), (659, 300),
    (784, 600), (0, 200), (392, 300), (523, 300), (659, 300), (523, 300)
]

# Boss melody
boss_melody = [
    (440, 360), (523, 360), (587, 320), (659, 320), (587, 320), (523, 320),
    (440, 400), (0, 180), (349, 360), (392, 360), (466, 320), (523, 320)
]

# Create tone banks
wonder_tones = [(make_tone(f, d), d) if f > 0 else (None, d) for f, d in wonder_melody]
title_tones = [(make_tone(f, d), d) if f > 0 else (None, d) for f, d in title_melody]
boss_tones = [(make_tone(f, d), d) if f > 0 else (None, d) for f, d in boss_melody]

# Music control
music_playing = True
current_music = "title"

def play_melody_loop():
    global music_playing, current_music
    channel = pygame.mixer.Channel(0)
    while music_playing:
        if current_music == "title":
            current_tones = title_tones
        elif current_music == "boss":
            current_tones = boss_tones
        elif current_music == "wonder":
            current_tones = wonder_tones
        else:
            current_tones = title_tones
            
        for sound, duration in current_tones:
            if not music_playing:
                break
            if sound:
                channel.play(sound)
            pygame.time.wait(duration)
    channel.stop()

def start_music(music_type="title"):
    global music_playing, current_music
    music_playing = False
    pygame.time.wait(100)
    current_music = music_type
    music_playing = True
    threading.Thread(target=play_melody_loop, daemon=True).start()

# --- ENHANCED COLOR PALETTE ---
BG = (107, 140, 255)
BG_WONDER = (255, 100, 150)
GROUND = (188, 152, 84)
BLOCK = (252, 216, 120)
WONDER_BLOCK = (255, 200, 255)
MARIO_HAT = (236, 28, 36)
MARIO_SHIRT = (236, 28, 36)
MARIO_OVERALLS = (44, 80, 180)
MARIO_SKIN = (252, 220, 148)
MARIO_SHOES = (96, 52, 12)
ELEPHANT_GREY = (140, 140, 160)
WONDER_FLOWER = (255, 255, 100)
BADGE_COLOR = (255, 215, 0)
PARTICLE_COLORS = [(255, 255, 100), (255, 200, 255), (100, 200, 255)]

FONT = pygame.font.SysFont(None, 32)
BIG_FONT = pygame.font.SysFont(None, 48)
SMALL_FONT = pygame.font.SysFont(None, 24)

# --- GAME ENTITIES ---
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.vel = [0, 0]
        self.on_ground = False
        self.on_wall = False
        self.wall_dir = 0
        self.power_up = PowerUp.SMALL
        self.badge = Badge.NONE
        self.hp = 3
        self.invuln = 0
        self.coins = 0
        self.wonder_seeds = 0
        self.animation_frame = 0
        self.facing_right = True
        self.elephant_water = 100
        self.parachute_active = False
        self.wall_climb_timer = 0
        self.speed_boost = 1.0
        
    def update(self, keys, platforms, floor):
        # Movement based on badge
        base_speed = 5 * self.speed_boost if self.badge == Badge.SPEED_RUN else 5
        
        self.vel[0] = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * base_speed
        if self.vel[0] > 0:
            self.facing_right = True
        elif self.vel[0] < 0:
            self.facing_right = False
            
        # Jumping mechanics
        jump_power = -15 if self.badge == Badge.FLOATING_HIGH_JUMP else -12
        if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel[1] = jump_power
            
        # Wall climbing with badge
        if self.badge == Badge.WALL_CLIMB and self.on_wall and keys[pygame.K_UP]:
            self.vel[1] = -3
            self.wall_climb_timer = 10
            
        # Parachute mechanics
        if self.badge == Badge.PARACHUTE and keys[pygame.K_SHIFT] and self.vel[1] > 2:
            self.parachute_active = True
            self.vel[1] = min(self.vel[1], 2)
        else:
            self.parachute_active = False
            
        # Gravity
        gravity = 0.3 if self.badge == Badge.FLOATING_HIGH_JUMP and keys[pygame.K_SPACE] else 0.7
        self.vel[1] += gravity
        
        # Elephant spray water
        if self.power_up == PowerUp.ELEPHANT and keys[pygame.K_x] and self.elephant_water > 0:
            self.elephant_water -= 2
            return True  # Signal to create water spray
            
        # Animation
        if abs(self.vel[0]) > 0:
            self.animation_frame = (self.animation_frame + 1) % 20
            
        return False
        
    def draw(self, surface):
        if self.invuln % 8 < 4 or self.invuln == 0:
            if self.power_up == PowerUp.ELEPHANT:
                self.draw_elephant(surface)
            else:
                self.draw_mario(surface)
                
            # Draw parachute
            if self.parachute_active:
                pygame.draw.arc(surface, (255, 255, 255), 
                              (self.rect.x-10, self.rect.y-30, 60, 40), 
                              0, math.pi, 3)
                
    def draw_mario(self, surface):
        # Head
        pygame.draw.rect(surface, MARIO_SKIN, (self.rect.x+10, self.rect.y+4, 20, 14))
        pygame.draw.rect(surface, MARIO_HAT, (self.rect.x+10, self.rect.y+4, 20, 6))
        
        # Body
        shirt_color = MARIO_SHIRT if self.power_up != PowerUp.FIRE else (255, 255, 255)
        pygame.draw.rect(surface, shirt_color, (self.rect.x+12, self.rect.y+18, 16, 10))
        pygame.draw.rect(surface, MARIO_OVERALLS, (self.rect.x+12, self.rect.y+24, 16, 12))
        
        # Arms
        pygame.draw.rect(surface, shirt_color, (self.rect.x+2, self.rect.y+18, 10, 8))
        pygame.draw.rect(surface, shirt_color, (self.rect.x+28, self.rect.y+18, 10, 8))
        pygame.draw.rect(surface, MARIO_SKIN, (self.rect.x+2, self.rect.y+25, 8, 7))
        pygame.draw.rect(surface, MARIO_SKIN, (self.rect.x+30, self.rect.y+25, 8, 7))
        
        # Shoes
        pygame.draw.rect(surface, MARIO_SHOES, (self.rect.x+10, self.rect.y+36, 8, 6))
        pygame.draw.rect(surface, MARIO_SHOES, (self.rect.x+22, self.rect.y+36, 8, 6))
        
    def draw_elephant(self, surface):
        # Elephant body (larger)
        body = pygame.Rect(self.rect.x-10, self.rect.y-10, 60, 50)
        pygame.draw.ellipse(surface, ELEPHANT_GREY, body)
        
        # Trunk
        trunk_x = body.right-10 if self.facing_right else body.left-10
        pygame.draw.rect(surface, ELEPHANT_GREY, (trunk_x, body.centery, 20, 8))
        
        # Ears
        ear_size = 15
        pygame.draw.circle(surface, ELEPHANT_GREY, (body.x+10, body.y+10), ear_size)
        pygame.draw.circle(surface, ELEPHANT_GREY, (body.right-10, body.y+10), ear_size)
        
        # Hat
        pygame.draw.rect(surface, MARIO_HAT, (body.centerx-10, body.y-5, 20, 10))

class WonderFlower:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.collected = False
        self.animation = 0
        
    def update(self):
        self.animation = (self.animation + 1) % 60
        
    def draw(self, surface):
        if not self.collected:
            # Animated wonder flower
            offset = math.sin(self.animation * 0.1) * 5
            center = (self.rect.centerx, self.rect.centery + offset)
            
            # Petals
            for i in range(8):
                angle = i * math.pi / 4
                petal_x = center[0] + math.cos(angle) * 15
                petal_y = center[1] + math.sin(angle) * 15
                pygame.draw.circle(surface, WONDER_FLOWER, (int(petal_x), int(petal_y)), 8)
                
            # Center
            pygame.draw.circle(surface, (255, 200, 0), center, 10)

class WonderSeed:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE//2, TILE//2)
        self.collected = False
        self.float_offset = random.random() * math.pi * 2
        
    def update(self):
        pass
        
    def draw(self, surface):
        if not self.collected:
            y_offset = math.sin(pygame.time.get_ticks() * 0.003 + self.float_offset) * 5
            pygame.draw.circle(surface, (255, 100, 255), 
                             (self.rect.centerx, self.rect.centery + y_offset), 10)
            pygame.draw.circle(surface, (255, 255, 255), 
                             (self.rect.centerx-3, self.rect.centery-3 + y_offset), 3)

class Particle:
    def __init__(self, x, y, vel_x, vel_y, color, lifetime=60):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.2
        self.lifetime -= 1
        
    def draw(self, surface):
        alpha = self.lifetime / self.max_lifetime
        size = int(5 * alpha)
        if size > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)

# --- LEVEL GENERATION ---
class Level:
    def __init__(self):
        self.floor = pygame.Rect(0, H-TILE*2, W, TILE*2)
        self.platforms = [
            pygame.Rect(3*TILE, H-5*TILE, 4*TILE, TILE),
            pygame.Rect(11*TILE, H-7*TILE, 4*TILE, TILE),
            pygame.Rect(18*TILE, H-4*TILE, 3*TILE, TILE),
        ]
        self.wonder_blocks = [
            pygame.Rect(7*TILE, H-8*TILE, TILE, TILE),
            pygame.Rect(15*TILE, H-10*TILE, TILE, TILE),
        ]
        self.coins = []
        self.generate_coins()
        self.wonder_active = False
        self.wonder_timer = 0
        self.wonder_effects = []
        
    def generate_coins(self):
        # Generate coin patterns
        for i in range(5):
            self.coins.append(pygame.Rect(5*TILE + i*TILE*2, H-6*TILE, 20, 20))
        for i in range(3):
            self.coins.append(pygame.Rect(12*TILE + i*30, H-9*TILE, 20, 20))
            
    def activate_wonder(self):
        self.wonder_active = True
        self.wonder_timer = 600  # 10 seconds
        start_music("wonder")
        
        # Random wonder effect
        effect = random.choice(["gravity", "blocks_alive", "time_slow", "rainbow"])
        self.wonder_effects.append(effect)
        
    def update(self):
        if self.wonder_active:
            self.wonder_timer -= 1
            if self.wonder_timer <= 0:
                self.wonder_active = False
                self.wonder_effects.clear()
                start_music("boss")
                
    def draw(self, surface):
        # Background
        bg_color = BG_WONDER if self.wonder_active else BG
        surface.fill(bg_color)
        
        # Ground
        pygame.draw.rect(surface, GROUND, self.floor)
        
        # Platforms
        for plat in self.platforms:
            color = WONDER_BLOCK if self.wonder_active else BLOCK
            pygame.draw.rect(surface, color, plat)
            
            # Animated blocks during wonder
            if self.wonder_active and "blocks_alive" in self.wonder_effects:
                # Draw eyes
                eye_y = plat.y + 10
                pygame.draw.circle(surface, (0,0,0), (plat.x + 10, eye_y), 5)
                pygame.draw.circle(surface, (0,0,0), (plat.right - 10, eye_y), 5)
                pygame.draw.circle(surface, (255,255,255), (plat.x + 12, eye_y-2), 2)
                pygame.draw.circle(surface, (255,255,255), (plat.right - 8, eye_y-2), 2)
                
        # Wonder blocks
        for block in self.wonder_blocks:
            pygame.draw.rect(surface, (200, 100, 200), block)
            pygame.draw.rect(surface, (255, 255, 255), block, 2)
            # Question mark
            text = FONT.render("?", True, (255, 255, 255))
            surface.blit(text, (block.x + 12, block.y + 8))
            
        # Coins
        for coin in self.coins:
            if coin:  # Check if coin still exists
                pygame.draw.circle(surface, (255, 215, 0), coin.center, 10)
                pygame.draw.circle(surface, (255, 255, 0), coin.center, 7)

# --- MAIN GAME CLASS ---
class WonderGame:
    def __init__(self):
        self.game_mode = GameMode.TITLE
        self.level = Level()
        self.player = Player(2*TILE, H-3*TILE)
        self.wonder_flower = WonderFlower(20*TILE, H-6*TILE)
        self.wonder_seeds = [
            WonderSeed(8*TILE, H-9*TILE),
            WonderSeed(16*TILE, H-11*TILE),
        ]
        self.particles = []
        self.enemies = []
        self.selected_option = 0
        self.selected_badge = Badge.NONE
        self.game_over = False
        self.win = False
        
        # Initialize Waluigi boss
        self.waluigi = pygame.Rect(W-3*TILE, H-3*TILE, TILE, TILE)
        self.wvel = [0,0]
        self.waluigi_hp = 3
        self.waluigi_dir = -1
        self.waluigi_jump_timer = 60
        self.waluigi_attack_timer = 90
        self.waluigi_invuln = 0
        self.balls = []
        
    def handle_collisions(self):
        # Player movement and collisions
        self.player.rect.x += self.player.vel[0]
        if self.player.rect.left < 0: 
            self.player.rect.left = 0
        if self.player.rect.right > W: 
            self.player.rect.right = W
            
        # Wall detection for wall climbing
        self.player.on_wall = False
        for plat in self.level.platforms + [self.level.floor]:
            if self.player.rect.colliderect(plat):
                if self.player.vel[0] > 0: 
                    self.player.rect.right = plat.left
                    self.player.on_wall = True
                    self.player.wall_dir = 1
                if self.player.vel[0] < 0: 
                    self.player.rect.left = plat.right
                    self.player.on_wall = True
                    self.player.wall_dir = -1
                    
        # Vertical movement
        self.player.rect.y += self.player.vel[1]
        self.player.on_ground = False
        for plat in self.level.platforms + [self.level.floor]:
            if self.player.rect.colliderect(plat):
                if self.player.vel[1] > 0:
                    self.player.rect.bottom = plat.top
                    self.player.on_ground = True
                if self.player.vel[1] < 0:
                    self.player.rect.top = plat.bottom
                self.player.vel[1] = 0
                
        # Coin collection
        for coin in self.level.coins[:]:
            if coin and self.player.rect.colliderect(coin):
                self.player.coins += 1
                self.level.coins.remove(coin)
                # Coin particles
                for i in range(5):
                    self.particles.append(Particle(
                        coin.centerx, coin.centery,
                        random.uniform(-2, 2), random.uniform(-5, -2),
                        (255, 215, 0)
                    ))
                    
        # Wonder flower collection
        if not self.wonder_flower.collected and self.player.rect.colliderect(self.wonder_flower.rect):
            self.wonder_flower.collected = True
            self.level.activate_wonder()
            # Wonder particles
            for i in range(20):
                self.particles.append(Particle(
                    self.wonder_flower.rect.centerx, self.wonder_flower.rect.centery,
                    random.uniform(-5, 5), random.uniform(-8, 0),
                    random.choice(PARTICLE_COLORS)
                ))
                
        # Wonder seed collection
        for seed in self.wonder_seeds:
            if not seed.collected and self.player.rect.colliderect(seed.rect):
                seed.collected = True
                self.player.wonder_seeds += 1
                
        # Wonder block interaction
        for block in self.level.wonder_blocks:
            if self.player.rect.colliderect(block) and self.player.vel[1] < 0:
                # Give power-up or badge
                if random.random() < 0.5:
                    self.player.power_up = PowerUp.ELEPHANT
                else:
                    available_badges = [b for b in Badge if b != Badge.NONE]
                    self.player.badge = random.choice(available_badges)
                    
    def update_waluigi(self):
        if not self.game_over:
            if self.waluigi_invuln > 0: 
                self.waluigi_invuln -= 1
                
            # Movement
            self.waluigi.x += self.waluigi_dir * 3
            if self.waluigi.left < TILE or self.waluigi.right > W-TILE: 
                self.waluigi_dir *= -1
                
            # Platform collisions
            for plat in self.level.platforms + [self.level.floor]:
                if self.waluigi.colliderect(plat):
                    if self.waluigi_dir > 0: 
                        self.waluigi.right = plat.left
                    if self.waluigi_dir < 0: 
                        self.waluigi.left = plat.right
                    self.waluigi_dir *= -1
                    
            # Jumping
            self.waluigi_jump_timer -= 1
            if self.waluigi_jump_timer <= 0:
                self.waluigi_jump_timer = random.randint(40, 70)
                self.wvel[1] = -10
                
            # Gravity
            self.wvel[1] += 0.5
            self.waluigi.y += int(self.wvel[1])
            
            for plat in self.level.platforms + [self.level.floor]:
                if self.waluigi.colliderect(plat):
                    if self.wvel[1] > 0:
                        self.waluigi.bottom = plat.top
                    if self.wvel[1] < 0:
                        self.waluigi.top = plat.bottom
                    self.wvel[1] = 0
                    
            # Attack
            self.waluigi_attack_timer -= 1
            if self.waluigi_attack_timer <= 0:
                self.waluigi_attack_timer = random.randint(50, 100)
                self.balls.append([self.waluigi.centerx, self.waluigi.bottom, 
                                 random.choice([-4,4]), 7])
                                 
        # Update balls
        for ball in self.balls[:]:
            ball[0] += ball[2]
            ball[1] += ball[3]
            ball[3] += 0.3
            
            ball_rect = pygame.Rect(ball[0]-10, ball[1]-10, 20, 20)
            
            if ball_rect.colliderect(self.player.rect) and self.player.invuln == 0:
                self.player.hp -= 1
                self.player.invuln = 40
                if self.player.hp <= 0:
                    self.game_over = True
                    music_playing = False
                    
            if ball_rect.top > H:
                self.balls.remove(ball)
                
        # Player-Waluigi collision
        if self.player.rect.colliderect(self.waluigi):
            if self.player.vel[1] > 2 and self.waluigi_invuln == 0:
                # Stomp on Waluigi
                self.waluigi_hp -= 1
                self.waluigi_invuln = 40
                self.player.vel[1] = -10
                
                if self.waluigi_hp <= 0:
                    self.win = True
                    self.game_over = True
                    music_playing = False
            elif self.player.invuln == 0:
                # Take damage
                self.player.hp -= 1
                self.player.invuln = 40
                if self.player.hp <= 0:
                    self.game_over = True
                    music_playing = False
                    
    def draw_waluigi(self, surface):
        if self.waluigi_invuln % 6 < 3 or self.waluigi_invuln == 0:
            # Draw Waluigi
            pygame.draw.rect(surface, (252, 220, 148), (self.waluigi.x+10, self.waluigi.y+4, 20, 14))
            pygame.draw.rect(surface, (128, 0, 192), (self.waluigi.x+10, self.waluigi.y+4, 20, 6))
            pygame.draw.ellipse(surface, (255,200,60), (self.waluigi.x+24, self.waluigi.y+10, 8,8))
            pygame.draw.rect(surface, (128, 0, 192), (self.waluigi.x+12, self.waluigi.y+18, 16, 10))
            pygame.draw.rect(surface, (0, 0, 0), (self.waluigi.x+12, self.waluigi.y+24, 16, 12))
            pygame.draw.rect(surface, (128, 0, 192), (self.waluigi.x+2, self.waluigi.y+18, 10, 8))
            pygame.draw.rect(surface, (128, 0, 192), (self.waluigi.x+28, self.waluigi.y+18, 10, 8))
            pygame.draw.rect(surface, (252, 220, 148), (self.waluigi.x+2, self.waluigi.y+25, 8, 7))
            pygame.draw.rect(surface, (252, 220, 148), (self.waluigi.x+30, self.waluigi.y+25, 8, 7))
            pygame.draw.rect(surface, (96, 52, 12), (self.waluigi.x+10, self.waluigi.y+36, 8, 6))
            pygame.draw.rect(surface, (96, 52, 12), (self.waluigi.x+22, self.waluigi.y+36, 8, 6))
            pygame.draw.line(surface, (40,30,10), (self.waluigi.x+16, self.waluigi.y+17), 
                           (self.waluigi.x+26, self.waluigi.y+17), 3)
                           
        # Draw balls
        for ball in self.balls:
            pygame.draw.circle(surface, (128, 0, 192), (int(ball[0]), int(ball[1])), 10)
            
    def draw_hud(self, surface):
        # Top HUD background
        pygame.draw.rect(surface, (0,0,0), (0, 0, W, 60))
        
        # Player info
        player_text = FONT.render("MARIO", True, (255,255,255))
        surface.blit(player_text, (20, 10))
        hp_text = FONT.render(f"HP: {self.player.hp}", True, (255,255,255))
        surface.blit(hp_text, (20, 35))
        
        # Coins
        coin_text = FONT.render(f"🟡×{self.player.coins:02d}", True, (255,255,255))
        surface.blit(coin_text, (200, 20))
        
        # Wonder Seeds
        seed_text = FONT.render(f"✨×{self.player.wonder_seeds}", True, (255,100,255))
        surface.blit(seed_text, (350, 20))
        
        # Power-up
        power_text = FONT.render(f"Power: {self.player.power_up.value}", True, (255,255,255))
        surface.blit(power_text, (500, 10))
        
        # Badge
        badge_text = FONT.render(f"Badge: {self.player.badge.value}", True, BADGE_COLOR)
        surface.blit(badge_text, (500, 35))
        
        # Wonder timer
        if self.level.wonder_active:
            wonder_text = BIG_FONT.render("WONDER TIME!", True, WONDER_FLOWER)
            text_rect = wonder_text.get_rect(center=(W//2, 100))
            surface.blit(wonder_text, text_rect)
            
            timer_text = FONT.render(f"{self.level.wonder_timer // 60}", True, (255,255,255))
            timer_rect = timer_text.get_rect(center=(W//2, 140))
            surface.blit(timer_text, timer_rect)
            
        # Boss HP
        if self.waluigi_hp > 0:
            boss_text = FONT.render(f"Waluigi HP: {self.waluigi_hp}", True, (255,0,0))
            surface.blit(boss_text, (W-200, 20))
            
    def draw_title_screen(self, surface):
        surface.fill(BG)
        
        # Title box
        title_box = pygame.Rect(W//2-300, 80, 600, 250)
        pygame.draw.rect(surface, (200, 100, 50), title_box)
        pygame.draw.rect(surface, (150, 50, 0), title_box, 5)
        
        # Title text with wonder effects
        title1 = BIG_FONT.render("SUPER MARIO", True, (0,0,0))
        title2 = BIG_FONT.render("WONDER", True, (255,255,255))
        title3 = FONT.render("ENGINE DEMO", True, (255,255,0))
        
        surface.blit(title1, (title_box.x + 170, title_box.y + 40))
        surface.blit(title2, (title_box.x + 210, title_box.y + 100))
        surface.blit(title3, (title_box.x + 220, title_box.y + 160))
        
        # Menu options
        options = ["Start Game", "Select Badge", "Quit"]
        for i, option in enumerate(options):
            y = 360 + i * 40
            color = (255,255,255) if i == self.selected_option else (150,150,150)
            text = FONT.render(option, True, color)
            surface.blit(text, (W//2 - text.get_width()//2, y))
            
            if i == self.selected_option:
                # Wonder flower selector
                flower_x = W//2 - text.get_width()//2 - 40
                pygame.draw.circle(surface, WONDER_FLOWER, (flower_x, y+15), 12)
                pygame.draw.circle(surface, (255,200,0), (flower_x, y+15), 8)
                
        # Instructions
        inst_text = SMALL_FONT.render("Arrow Keys: Move  Space: Jump  X: Special  Enter: Select", 
                                     True, (200,200,200))
        surface.blit(inst_text, (W//2 - inst_text.get_width()//2, H-40))
        
    def draw_badge_select(self, surface):
        surface.fill(BG)
        
        title = BIG_FONT.render("SELECT BADGE", True, (0,0,0))
        surface.blit(title, (W//2 - title.get_width()//2, 40))
        
        badges = [
            (Badge.NONE, "No Badge", "Play without any special abilities"),
            (Badge.PARACHUTE, "Parachute Cap", "Hold SHIFT to glide slowly"),
            (Badge.DOLPHIN_KICK, "Dolphin Kick", "Enhanced swimming (not implemented)"),
            (Badge.WALL_CLIMB, "Wall Climb", "Climb walls by holding UP"),
            (Badge.FLOATING_HIGH_JUMP, "Floating Jump", "Hold SPACE for floaty jumps"),
            (Badge.SPEED_RUN, "Speed Runner", "Move 50% faster"),
        ]
        
        for i, (badge, name, desc) in enumerate(badges):
            y = 120 + i * 60
            box = pygame.Rect(100, y, W-200, 50)
            
            if i == self.selected_option:
                pygame.draw.rect(surface, BADGE_COLOR, box)
                pygame.draw.rect(surface, (200,150,0), box, 3)
            else:
                pygame.draw.rect(surface, (100,100,100), box)
                pygame.draw.rect(surface, (50,50,50), box, 3)
                
            name_text = FONT.render(name, True, (0,0,0))
            desc_text = SMALL_FONT.render(desc, True, (50,50,50))
            surface.blit(name_text, (box.x + 20, box.y + 5))
            surface.blit(desc_text, (box.x + 20, box.y + 28))
            
        back_text = FONT.render("Press Q to go back", True, (200,200,200))
        surface.blit(back_text, (W//2 - back_text.get_width()//2, H-40))
        
    def run(self):
        running = True
        start_music("title")
        
        while running:
            keys = pygame.key.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.KEYDOWN:
                    if self.game_mode == GameMode.TITLE:
                        if event.key == pygame.K_UP:
                            self.selected_option = (self.selected_option - 1) % 3
                        elif event.key == pygame.K_DOWN:
                            self.selected_option = (self.selected_option + 1) % 3
                        elif event.key == pygame.K_RETURN:
                            if self.selected_option == 0:
                                self.game_mode = GameMode.PLAYING
                                start_music("boss")
                            elif self.selected_option == 1:
                                self.game_mode = GameMode.FILE_SELECT
                                self.selected_option = 0
                            elif self.selected_option == 2:
                                running = False
                                
                    elif self.game_mode == GameMode.FILE_SELECT:
                        if event.key == pygame.K_UP:
                            self.selected_option = (self.selected_option - 1) % 6
                        elif event.key == pygame.K_DOWN:
                            self.selected_option = (self.selected_option + 1) % 6
                        elif event.key == pygame.K_RETURN:
                            badges = [Badge.NONE, Badge.PARACHUTE, Badge.DOLPHIN_KICK,
                                    Badge.WALL_CLIMB, Badge.FLOATING_HIGH_JUMP, Badge.SPEED_RUN]
                            self.player.badge = badges[self.selected_option]
                            self.game_mode = GameMode.TITLE
                            self.selected_option = 0
                        elif event.key == pygame.K_q:
                            self.game_mode = GameMode.TITLE
                            self.selected_option = 0
                            
                    elif self.game_mode == GameMode.PLAYING and self.game_over:
                        if event.key == pygame.K_r:
                            self.__init__()
                            self.game_mode = GameMode.PLAYING
                            start_music("boss")
                        elif event.key == pygame.K_q:
                            self.__init__()
                            self.game_mode = GameMode.TITLE
                            start_music("title")
                            
            # Game logic
            if self.game_mode == GameMode.PLAYING and not self.game_over:
                # Update player
                water_spray = self.player.update(keys, self.level.platforms, self.level.floor)
                
                # Handle collisions
                self.handle_collisions()
                
                # Update level
                self.level.update()
                
                # Update entities
                self.wonder_flower.update()
                for seed in self.wonder_seeds:
                    seed.update()
                    
                # Update Waluigi
                self.update_waluigi()
                
                # Update particles
                for particle in self.particles[:]:
                    particle.update()
                    if particle.lifetime <= 0:
                        self.particles.remove(particle)
                        
                # Update invulnerability
                if self.player.invuln > 0:
                    self.player.invuln -= 1
                    
                # Create water spray particles
                if water_spray:
                    dir_mult = 1 if self.player.facing_right else -1
                    for i in range(3):
                        self.particles.append(Particle(
                            self.player.rect.centerx + dir_mult * 20,
                            self.player.rect.centery,
                            dir_mult * random.uniform(3, 6),
                            random.uniform(-2, 2),
                            (100, 150, 255)
                        ))
                        
            # Drawing
            if self.game_mode == GameMode.TITLE:
                self.draw_title_screen(screen)
            elif self.game_mode == GameMode.FILE_SELECT:
                self.draw_badge_select(screen)
            elif self.game_mode == GameMode.PLAYING:
                # Draw level
                self.level.draw(screen)
                
                # Draw entities
                self.wonder_flower.draw(screen)
                for seed in self.wonder_seeds:
                    seed.draw(screen)
                    
                # Draw particles
                for particle in self.particles:
                    particle.draw(screen)
                    
                # Draw player
                self.player.draw(screen)
                
                # Draw Waluigi
                self.draw_waluigi(screen)
                
                # Draw HUD
                self.draw_hud(screen)
                
                # Game over message
                if self.game_over:
                    overlay = pygame.Surface((W, H))
                    overlay.set_alpha(128)
                    overlay.fill((0,0,0))
                    screen.blit(overlay, (0,0))
                    
                    if self.win:
                        msg = "YOU WIN!"
                        color = WONDER_FLOWER
                    else:
                        msg = "GAME OVER"
                        color = (255,0,0)
                        
                    game_over_text = BIG_FONT.render(msg, True, color)
                    restart_text = FONT.render("Press R to Restart, Q for Title", True, (255,255,255))
                    
                    screen.blit(game_over_text, (W//2 - game_over_text.get_width()//2, H//2 - 50))
                    screen.blit(restart_text, (W//2 - restart_text.get_width()//2, H//2 + 20))
                    
            pygame.display.flip()
            clock.tick(60)
            
        music_playing = False
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = WonderGame()
    game.run()
