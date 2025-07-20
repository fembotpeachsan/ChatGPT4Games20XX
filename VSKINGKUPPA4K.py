#!/usr/bin/env python3
"""
test.py – “Super Mario World Final Boss – Accurate Recreation”
Fixed & optimised for rock‑solid 60 FPS.
"""

import math
import numpy as np
import pygame

# --------------------------------------------------------------------------- #
# 1.  Audio & Pygame initialisation                                            #
# --------------------------------------------------------------------------- #
SAMPLE_RATE = 44100
pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, 512)           # <── key for stutter‑free audio
pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.SCALED | pygame.DOUBLEBUF | pygame.HWSURFACE    # vs‑sync‑friendly flags
)
pygame.display.set_caption("Super Mario World – Bowser (fixed)")
clock = pygame.time.Clock()

# --------------------------------------------------------------------------- #
# 2.  Palette & helpers                                                        #
# --------------------------------------------------------------------------- #
BLACK = (0, 0, 0)
WHITE = (248, 248, 248)
RED = (248, 56, 0)
GREEN = (0, 168, 0)
BLUE = (0, 0, 168)
YELLOW = (248, 188, 0)
ORANGE = (248, 120, 88)
BROWN = (168, 76, 0)
SKIN = (248, 208, 176)
LAVA_RED = (248, 0, 0)
LAVA_ORANGE = (248, 168, 0)
GRAY = (136, 136, 136)
DARK_GRAY = (68, 68, 68)

def make_beep(freq, duration, volume=0.5):
    """Return a Pygame Sound with given frequency/duration (seconds)."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    wave = (volume * np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)

# Pre‑baked game SFX
jump_snd   = make_beep(523.25, 0.10)
stun_snd   = make_beep(392.00, 0.15)
throw_snd  = make_beep(659.25, 0.10)
hit_snd    = make_beep(261.63, 0.20, 0.8)
ball_snd   = make_beep(329.63, 0.12)
win_snd    = make_beep(784.00, 0.30)
lose_snd   = make_beep(130.81, 0.30, 0.7)

# --------------------------------------------------------------------------- #
# 3.  Sprite factories (render once → reuse)                                   #
# --------------------------------------------------------------------------- #
def build_surface(size, draw_callback) -> pygame.Surface:
    surf = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
    draw_callback(surf)
    return surf

def mario_sprite(facing_right=True):
    def _draw(surf):
        # === Mario pixel art ===
        px = [
            (7,1,RED),(8,1,RED),(9,1,RED),(10,1,RED),(11,1,RED),
            (6,2,RED),(7,2,RED),(8,2,RED),(9,2,RED),(10,2,RED),(11,2,RED),(12,2,RED),
            (5,3,RED),(6,3,RED),(7,3,RED),(8,3,RED),(9,3,RED),(10,3,RED),(11,3,RED),(12,3,RED),(13,3,RED),
            (5,4,BROWN),(6,4,BROWN),(7,4,BROWN),(8,4,SKIN),(9,4,BROWN),(10,4,SKIN),(11,4,SKIN),(12,4,SKIN),
            (4,5,BROWN),(5,5,BROWN),(6,5,BROWN),(7,5,BROWN),(8,5,SKIN),(9,5,SKIN),(10,5,SKIN),(11,5,SKIN),(12,5,SKIN),(13,5,BROWN),
            (4,6,BROWN),(5,6,BROWN),(6,6,BROWN),(7,6,BLACK),(8,6,BROWN),(9,6,SKIN),(10,6,BLACK),(11,6,SKIN),(12,6,BROWN),
            (4,7,BROWN),(5,7,BROWN),(6,7,SKIN),(7,7,SKIN),(8,7,SKIN),(9,7,SKIN),(10,7,SKIN),(11,7,SKIN),
            (6,8,BLUE),(7,8,BLUE),(8,8,RED),(9,8,RED),(10,8,RED),(11,8,BLUE),(12,8,BLUE),
            (5,9,BLUE),(6,9,BLUE),(7,9,BLUE),(8,9,RED),(9,9,RED),(10,9,RED),(11,9,BLUE),(12,9,BLUE),(13,9,BLUE),
            (4,10,BLUE),(5,10,BLUE),(6,10,BLUE),(7,10,BLUE),(8,10,RED),(9,10,RED),(10,10,RED),(11,10,BLUE),(12,10,BLUE),(13,10,BLUE),
            (3,11,BLUE),(4,11,BLUE),(5,11,BLUE),(11,11,BLUE),(12,11,BLUE),(13,11,BLUE),
            (6,12,BLUE),(7,12,BLUE),(8,12,BLUE),(9,12,BLUE),(10,12,BLUE),
            (2,13,BROWN),(3,13,BROWN),(4,13,YELLOW),(5,13,YELLOW),(11,13,YELLOW),(12,13,YELLOW),
            (2,14,BROWN),(3,14,BROWN),(4,14,BROWN),(5,14,YELLOW),(6,14,YELLOW),(11,14,YELLOW),(12,14,YELLOW),(13,14,BROWN),
            (3,15,BROWN),(4,15,BROWN),(5,15,BROWN),(6,15,BROWN),(12,15,BROWN),(13,15,BROWN)
        ]
        for x, y, col in px:
            if not facing_right:
                x = 18 - x
            surf.fill(col, pygame.Rect(x, y, 1, 1))
    return build_surface((18, 16), _draw)

MARIO_RIGHT = mario_sprite(True)
MARIO_LEFT  = mario_sprite(False)

def mechakoopa_sprite(stunned=False):
    def _draw(surf):
        surf.fill(GRAY, (5, 5, 10, 10))
        surf.fill(DARK_GRAY, (6, 6, 8, 8))
        surf.fill(WHITE, (7, 7, 2, 2))
        surf.fill(WHITE, (11, 7, 2, 2))
        surf.fill(YELLOW, (4, 15, 5, 5))
        surf.fill(YELLOW, (11, 15, 5, 5))
        if stunned:
            pygame.draw.line(surf, BLACK, (7, 9), (13, 9), 2)
    return build_surface((20, 20), _draw)

MECHA_NORMAL = mechakoopa_sprite(False)
MECHA_STUNNED = mechakoopa_sprite(True)

def bowser_surface():
    def _draw(surf):
        # Clown car
        pygame.draw.rect(surf, BLUE,  (10, 30, 30, 20))
        pygame.draw.circle(surf, BLUE, (25, 25), 20)
        pygame.draw.rect(surf, YELLOW, (20, 45, 10, 5))
        # Bowser body
        surf.fill(GREEN,  (15, 5, 20, 25))
        surf.fill(ORANGE, (20, 25, 10, 5))
        surf.fill(WHITE,  (18, 10, 4, 4))
        surf.fill(WHITE,  (28, 10, 4, 4))
        surf.fill(RED,    (22, 0,  6, 5))
        surf.fill(BROWN,  (15, 5,  5, 5))
    return build_surface((50, 50), _draw)

BOWSER_IMG = bowser_surface()

def ball_surface():
    def _draw(surf):
        pygame.draw.circle(surf, GRAY,  (15, 15), 15)
        pygame.draw.circle(surf, WHITE, (10, 10), 5)
        pygame.draw.circle(surf, DARK_GRAY, (20, 20), 3)
    return build_surface((30, 30), _draw)

BALL_IMG = ball_surface()

# --------------------------------------------------------------------------- #
# 4.  Game objects                                                             #
# --------------------------------------------------------------------------- #
all_sprites = pygame.sprite.Group()
mechakoopas = pygame.sprite.Group()
balls = pygame.sprite.Group()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = MARIO_RIGHT
        self.rect = self.image.get_rect(midbottom=(50, HEIGHT - 60))
        self.vel = pygame.Vector2()
        self.on_ground = True
        self.carrying = None
        self.facing_right = True

    def update(self):
        self.vel.y += 0.8                     # gravity
        self.rect.y += self.vel.y
        if self.rect.bottom >= HEIGHT - 60:   # ground collision
            self.rect.bottom = HEIGHT - 60
            self.vel.y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        self.rect.x += self.vel.x
        self.rect.clamp_ip(screen.get_rect())  # stay on screen

        self.image = MARIO_RIGHT if self.facing_right else MARIO_LEFT
        if self.carrying:
            self.carrying.rect.midtop = self.rect.midtop
            self.carrying.set_stunned(True)

class Bowser(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = BOWSER_IMG
        self.rect = self.image.get_rect(centerx=WIDTH//2, y=50)
        self.t = 0
        self.health = 3
        self.dir = 1
        self.phase = 0

    def update(self):
        self.t += 1
        self.rect.x += self.dir * (1 + self.phase)
        self.rect.y = 50 + math.sin(self.t * 0.05) * (20 + 10 * self.phase)
        if self.rect.left < 20 or self.rect.right > WIDTH - 20:
            self.dir *= -1
        # Spawn mechanics
        if self.t % (180 - 30 * self.phase) == 0:
            mechakoopa = MechaKoopa(self.rect.centerx, self.rect.bottom)
            mechakoopas.add(mechakoopa)
            throw_snd.play()
        if self.t % (360 - 60 * self.phase) == 0:
            Ball(self.rect.centerx, self.rect.bottom)
            ball_snd.play()
        if self.health < 3:
            self.phase = 3 - self.health

class MechaKoopa(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = MECHA_NORMAL
        self.rect = self.image.get_rect(centerx=x, y=y)
        self.vel_x = -2
        self.stunned = False
        self.stun_frames = 0
        self.throw_vel_y = 0

    def set_stunned(self, value):
        self.stunned = value
        self.stun_frames = 0
        self.image = MECHA_STUNNED if value else MECHA_NORMAL

    def update(self):
        if self.throw_vel_y:                  # being thrown
            self.rect.y += self.throw_vel_y
            self.throw_vel_y += 0.8
            if self.rect.bottom >= HEIGHT - 60:
                self.kill()
            return

        if self.stunned:
            self.stun_frames += 1
            if self.stun_frames > 300:
                self.set_stunned(False)
        else:
            self.rect.x += self.vel_x
            if self.rect.left < 0 or self.rect.right > WIDTH:
                self.vel_x *= -1
            self.rect.bottom = HEIGHT - 60

class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, balls)
        self.image = BALL_IMG
        self.rect = self.image.get_rect(centerx=x, y=y)
        self.vel_y = 0

    def update(self):
        self.vel_y += 0.8
        self.rect.y += self.vel_y
        if self.rect.top > HEIGHT:
            self.kill()

# --------------------------------------------------------------------------- #
# 5.  Static background                                                        #
# --------------------------------------------------------------------------- #
def draw_background():
    screen.fill(BLACK)
    # castle wall stripes
    for i in range(0, WIDTH, 20):
        pygame.draw.rect(screen, GRAY, (i, 0, 10, HEIGHT - 50))
    # lava
    pygame.draw.rect(screen, LAVA_RED, (0, HEIGHT - 50, WIDTH, 50))
    t = pygame.time.get_ticks() / 200
    for i in range(10):
        x = 50 + i * 60
        y = HEIGHT - 30 + math.sin(i + t) * 5
        pygame.draw.circle(screen, LAVA_ORANGE, (x, y), 20)

# --------------------------------------------------------------------------- #
# 6.  Game loop                                                                #
# --------------------------------------------------------------------------- #
player = Player()
bowser = Bowser()

running = True
while running:
    dt = clock.tick(60)          # cap to 60 FPS, returns milliseconds since last call
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE and player.on_ground:
                player.vel.y = -15
                player.on_ground = False
                jump_snd.play()
            elif ev.key == pygame.K_DOWN and player.carrying is None:
                for m in pygame.sprite.spritecollide(player, mechakoopas, False):
                    if m.stunned and m.throw_vel_y == 0:
                        player.carrying = m
                        break
            elif ev.key == pygame.K_UP and player.carrying:
                m = player.carrying
                player.carrying = None
                m.throw_vel_y = -18
                m.rect.midbottom = player.rect.midtop
                throw_snd.play()

    keys = pygame.key.get_pressed()
    player.vel.x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 6
    player.facing_right = player.vel.x >= 0

    # Update world
    all_sprites.update()

    # Player -> MechaKoopa stomp
    for m in pygame.sprite.spritecollide(player, mechakoopas, False):
        if not m.stunned and player.vel.y > 0 and player.rect.bottom <= m.rect.centery:
            m.set_stunned(True)
            player.vel.y = -10
            stun_snd.play()

    # Thrown MechaKoopa -> Bowser hit
    for m in mechakoopas:
        if m.throw_vel_y < 0 and pygame.sprite.collide_rect(m, bowser):
            bowser.health -= 1
            m.kill()
            hit_snd.play()
            if bowser.health <= 0:
                win_snd.play()
                print("You defeated Bowser!")
                running = False

    # Ball / Bowser collisions with player
    if pygame.sprite.spritecollide(player, balls, True):
        lose_snd.play()
        print("Hit by ball! Game Over.")
        running = False
    if pygame.sprite.collide_rect(player, bowser):
        lose_snd.play()
        print("Hit by Bowser! Game Over.")
        running = False

    # Draw
    draw_background()
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
