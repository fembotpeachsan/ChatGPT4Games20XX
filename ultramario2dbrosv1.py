#!/usr/bin/env python3
"""
Mario Bros Arcade – Vibes Remix Edition
---------------------------------------
Pure Pygame, M1 Mac tested, 60 FPS
Vibesy Mode: Press 'V' for ultra vibes.
Main Menu: Press Space to Start, with chiptune intro (synth).
"""

import pygame
import numpy as np
import math
import sys
import random

# --- INIT ------------------------------------------------------------------- #
pygame.init()
WIDTH, HEIGHT = 960, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mario Bros Arcade – VIBES REMIX")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("monospace", 32, bold=True)

# --- COLORS & VIBES -------------------------------------------------------- #
BASE_BG = (0, 40, 64)
BASE_PLAT = (32, 168, 32)
VIBES_COLORS = [
    (255, 64, 255), (32, 255, 128), (64, 224, 255), (255, 224, 64)
]

# --- SOUND SYNTH: GAME BOY STYLE -------------------------------------------- #
def play_menu_music():
    rate = 22050
    t = np.linspace(0, 2, 2 * rate)
    # Little Mario Bros/GB chiptune riff
    notes = [220, 440, 392, 330, 220, 330, 392, 440, 0, 392, 0, 330, 220]
    arr = np.zeros_like(t)
    for i, note in enumerate(notes):
        if note == 0: continue
        start = int(i * rate * 0.16)
        end = int((i+1) * rate * 0.16)
        arr[start:end] = 0.18 * np.sign(np.sin(2 * np.pi * note * t[start:end])) # Square wave!
    # Make array stereo for pygame mixer
    arr_stereo = np.column_stack([arr, arr])
    sound = pygame.sndarray.make_sound((arr_stereo * 32767).astype(np.int16))
    sound.play()
    return sound

# --- MARIO + PHYSICS ------------------------------------------------------- #
class Mario:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 80
        self.dx, self.dy = 0, 0
        self.on_ground = True
        self.big = False
        self.lives = 3
        self.score = 0
        self.flip = False

    def rect(self):  # For collisions
        return pygame.Rect(self.x-20, self.y-40, 40, 40 if not self.big else 64)

    def update(self, keys, plats, enemies, coins):
        # Controls
        if keys[pygame.K_LEFT]:  self.dx -= 1.5
        if keys[pygame.K_RIGHT]: self.dx += 1.5
        if keys[pygame.K_SPACE] and self.on_ground:
            self.dy = -18 if self.big else -14
            self.on_ground = False

        # Physics
        self.dy += 1.2  # Gravity
        self.x += self.dx
        self.y += self.dy
        self.dx *= 0.8

        # Screen wrap
        if self.x < 0: self.x = WIDTH
        if self.x > WIDTH: self.x = 0

        # Floor + Platforms
        self.on_ground = False
        for p in plats:
            if self.rect().colliderect(p):
                if self.dy > 0 and self.y < p.y:  # Land on top
                    self.y = p.y - (40 if not self.big else 64)
                    self.dy = 0
                    self.on_ground = True

        # Enemies
        for e in enemies:
            if self.rect().colliderect(e.rect()):
                if self.dy > 0:  # Stomp
                    e.die()
                    self.dy = -9
                    self.score += 200
                else:
                    self.lives -= 1
                    self.x, self.y = WIDTH // 2, HEIGHT - 80
                    self.dx, self.dy = 0, 0

        # Coins
        for c in coins[:]:
            if self.rect().colliderect(c):
                coins.remove(c)
                self.score += 100

# --- ENEMY ------------------------------------------------------ #
class Enemy:
    def __init__(self, x, y, kind='turtle'):
        self.x = x
        self.y = y
        self.dx = random.choice([-6, 6])
        self.alive = True
        self.kind = kind

    def rect(self):
        return pygame.Rect(self.x-18, self.y-36, 36, 36)

    def update(self, plats):
        if not self.alive: return
        self.x += self.dx
        # Screen wrap
        if self.x < 0: self.x = WIDTH
        if self.x > WIDTH: self.x = 0
        # Gravity + plats
        self.y += 8
        for p in plats:
            if self.rect().colliderect(p):
                if self.y < p.y:
                    self.y = p.y - 36

    def draw(self, surf, vibe_mode, frame):
        color = (0, 200, 64) if self.kind == 'turtle' else (200, 64, 0)
        if vibe_mode: color = VIBES_COLORS[frame % len(VIBES_COLORS)]
        pygame.draw.rect(surf, color, self.rect())

    def die(self):
        self.alive = False
        self.x, self.y = random.randint(60, WIDTH-60), 60

# --- MAIN MENU --------------------------------------------------- #
def main_menu():
    vibe_frame = 0
    vibe_mode = False
    menu_music = play_menu_music()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE:
                    menu_music.stop()
                    return vibe_mode
                if ev.key == pygame.K_v:
                    vibe_mode = not vibe_mode
        # BG
        if vibe_mode:
            bg = [c + int(32*math.sin(pygame.time.get_ticks()/333)) for c in BASE_BG]
            bg = tuple(min(255,max(0,v)) for v in bg)
            screen.fill(bg)
        else:
            screen.fill(BASE_BG)
        # Title
        txt = FONT.render("MARIO BROS ARCADE – VIBES REMIX", 1, (255,255,255))
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 120))
        # Press Space
        t2 = FONT.render("Press SPACE to Start", 1, (200,255,100))
        screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2))
        t3 = FONT.render("Press V for VIBESY MODE", 1, (180,160,255))
        screen.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT//2 + 60))
        # GB style block
        for y in range(8):
            for x in range(18):
                col = (80, 200, 120) if (x+y+vibe_frame)%3==0 else (64,120,100)
                pygame.draw.rect(screen, col, (80+44*x, 90+28*y, 40, 24), 0, border_radius=6)
        pygame.display.flip()
        clock.tick(60)
        vibe_frame += 1

# --- GAME LOOP --------------------------------------------------- #
def game_loop(vibe_mode):
    player = Mario()
    platforms = [pygame.Rect(0, HEIGHT-40, WIDTH, 40),
                 pygame.Rect(100, 520, 760, 24),
                 pygame.Rect(0, 320, 320, 24),
                 pygame.Rect(640, 320, 320, 24)]
    enemies = [Enemy(160, 520), Enemy(800, 320, 'crab')]
    coins = [pygame.Rect(random.randint(60,WIDTH-60), random.choice([520,320])-28, 24,24) for _ in range(8)]
    frame = 0

    running = True
    while running:
        keys = pygame.key.get_pressed()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE: sys.exit()
                if ev.key == pygame.K_r:
                    return 'restart'
                if ev.key == pygame.K_v:
                    vibe_mode = not vibe_mode

        # --- UPDATE ---
        player.update(keys, platforms, [e for e in enemies if e.alive], coins)
        for e in enemies: e.update(platforms)

        # --- DRAW ---
        if vibe_mode:
            # Cycle BG and warp
            warp = 16 * math.sin(frame/20)
            bg = [int((c + 128 + 127*math.sin(frame/33 + i)))%256 for i, c in enumerate(BASE_BG)]
            screen.fill(bg)
        else:
            screen.fill(BASE_BG)

        # Platforms
        for p in platforms:
            plat_col = BASE_PLAT
            if vibe_mode: plat_col = VIBES_COLORS[frame % len(VIBES_COLORS)]
            pygame.draw.rect(screen, plat_col, p, 0, border_radius=12)

        # Coins
        for c in coins:
            col = COIN_COLOR = (255,255,80) if not vibe_mode else VIBES_COLORS[frame % len(VIBES_COLORS)]
            pygame.draw.ellipse(screen, col, c)

        # Enemies
        for e in enemies: e.draw(screen, vibe_mode, frame)

        # Player
        mario_col = (240,32,32) if not vibe_mode else VIBES_COLORS[(frame+2) % len(VIBES_COLORS)]
        pygame.draw.rect(screen, mario_col, player.rect(), 0, border_radius=16)
        pygame.draw.rect(screen, (255,255,255), player.rect(), 2)

        # HUD
        scoretxt = FONT.render(f"Score: {player.score}", 1, (255,240,200))
        livetxt = FONT.render(f"Lives: {player.lives}", 1, (255,180,120))
        screen.blit(scoretxt, (36, 16))
        screen.blit(livetxt, (WIDTH-180, 16))

        # Vibe effect overlay
        if vibe_mode and (frame%6<3):
            surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(surf, (255,255,255,20), (0,0,WIDTH,HEIGHT), 0)
            screen.blit(surf, (int(warp),-int(warp)))

        pygame.display.flip()
        clock.tick(60)
        frame += 1

        # Game Over
        if player.lives <= 0:
            running = False

    # --- GAME OVER SCREEN --- #
    overtxt = FONT.render("GAME OVER", 1, (255,80,80))
    screen.blit(overtxt, (WIDTH//2 - overtxt.get_width()//2, HEIGHT//2 - 40))
    pygame.display.flip()
    pygame.time.wait(1800)

# --- MAIN -------------------------------------------------------- #
if __name__ == "__main__":
    while True:
        vibe_mode = main_menu()
        res = game_loop(vibe_mode)
        if res == 'restart':
            continue
        break
