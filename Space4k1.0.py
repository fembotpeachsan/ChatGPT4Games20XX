import pygame
import sys
import random
import math
import numpy as np

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
PLAYER_WIDTH, PLAYER_HEIGHT = 60, 20
PLAYER_SPEED = 5
BULLET_WIDTH, BULLET_HEIGHT = 4, 12
BULLET_SPEED = 7
INVADER_ROWS, INVADER_COLS = 5, 11  # 11 cols like original
INVADER_SIZE = 30
INVADER_X_GAP = 10
INVADER_Y_GAP = 10
INVADER_DROP = 10
BUNKER_COUNT = 4
BUNKER_BLOCK = 8
UFO_HEIGHT = 20
UFO_SPEED = 3
UFO_SCORE_VALUES = [50, 100, 150, 300]

# Initialize Pygame
def generate_tone(frequency, duration, volume=0.3):
    sample_rate = 44100
    n = int(sample_rate * duration)
    t = np.linspace(0, duration, n, False)
    wave = np.sin(2 * math.pi * frequency * t)
    audio = (wave * (2**15 - 1) * volume).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo)

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders (OG)")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
large_font = pygame.font.SysFont(None, 48)

# Sound effects
shoot_sound = generate_tone(880, 0.1)
invader_kill_sound = generate_tone(330, 0.2)
player_explosion_sound = generate_tone(150, 0.3)
ufo_sound = generate_tone(440, 0.5)

# Sprites as simple surfaces with wiggle
def make_invader_surfaces(color):
    surf1 = pygame.Surface((INVADER_SIZE, INVADER_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(surf1, color, (0, 0, INVADER_SIZE, INVADER_SIZE))
    surf2 = pygame.Surface((INVADER_SIZE, INVADER_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(surf2, color, (5, 0, INVADER_SIZE-10, INVADER_SIZE))
    return [surf1, surf2]

INVADER_COLORS = [(0,255,0), (255,165,0), (255,0,0)]
INVADER_SPRITES = [make_invader_surfaces(c) for c in INVADER_COLORS]
PLAYER_SURF = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
pygame.draw.rect(PLAYER_SURF, (0,255,255), (0,0,PLAYER_WIDTH,PLAYER_HEIGHT))
UFO_SURF = pygame.Surface((INVADER_SIZE, UFO_HEIGHT))
pygame.draw.rect(UFO_SURF, (255,255,255), (0,0,INVADER_SIZE, UFO_HEIGHT))

class Player:
    def __init__(self):
        self.rect = pygame.Rect((SCREEN_WIDTH-PLAYER_WIDTH)//2, SCREEN_HEIGHT-PLAYER_HEIGHT-10, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.bullets = []
        self.lives = 3
        self.score = 0

    def move(self, dx):
        self.rect.x += dx*PLAYER_SPEED
        self.rect.clamp_ip(screen.get_rect())

    def shoot(self):
        if len(self.bullets)<2:
            rect = pygame.Rect(self.rect.centerx-BULLET_WIDTH//2, self.rect.y-BULLET_HEIGHT, BULLET_WIDTH, BULLET_HEIGHT)
            self.bullets.append(rect)
            shoot_sound.play()

    def update(self):
        for b in self.bullets[:]:
            b.y -= BULLET_SPEED
            if b.bottom<0: self.bullets.remove(b)

    def draw(self):
        screen.blit(PLAYER_SURF, self.rect)
        for b in self.bullets: pygame.draw.rect(screen,(255,255,255),b)

class Invader:
    def __init__(self, row, col):
        self.row, self.col = row, col
        self.alive = True

class Formation:
    def __init__(self):
        self.invaders = [Invader(r,c) for r in range(INVADER_ROWS) for c in range(INVADER_COLS)]
        self.offset_x = 50
        self.offset_y = 50
        self.direction = 1
        self.move_timer = 0
        self.interval = 60
        self.frame = 0

    def update(self):
        # adjust speed interval
        alive = len([i for i in self.invaders if i.alive])
        total = INVADER_ROWS*INVADER_COLS
        # linear interp interval between 60 and 15
        self.interval = max(15, int(60 - (total-alive)/total*45))
        self.move_timer += 1
        if self.move_timer >= self.interval:
            self.move_timer = 0
            # move horizontally
            next_x = self.offset_x + self.direction*INVADER_SIZE
            # check bounds
            if next_x < 0 or next_x + (INVADER_COLS*(INVADER_SIZE+INVADER_X_GAP))-INVADER_X_GAP>SCREEN_WIDTH:
                self.direction *= -1
                self.offset_y += INVADER_DROP
            else:
                self.offset_x += self.direction*INVADER_X_GAP
            self.frame ^=1
            # play move tone
            freq = 200 + (5-self.frame)*50
            generate_tone(freq,0.05).play()

    def draw(self):
        for inv in self.invaders:
            if not inv.alive: continue
            x = self.offset_x + inv.col*(INVADER_SIZE+INVADER_X_GAP)
            y = self.offset_y + inv.row*(INVADER_SIZE+INVADER_Y_GAP)
            sprite = INVADER_SPRITES[inv.row//2%len(INVADER_SPRITES)][self.frame]
            screen.blit(sprite,(x,y))

class Bunker:
    def __init__(self, x):
        self.blocks = []
        for by in range(3):
            for bx in range(5):
                rect = pygame.Rect(x+bx*BUNKER_BLOCK, SCREEN_HEIGHT-150+by*BUNKER_BLOCK, BUNKER_BLOCK, BUNKER_BLOCK)
                self.blocks.append(rect)
    def draw(self):
        for b in self.blocks: pygame.draw.rect(screen,(0,255,0),b)

class UFO:
    def __init__(self):
        self.rect = pygame.Rect(-INVADER_SIZE,50,INVADER_SIZE,UFO_HEIGHT)
        self.alive = True
        self.score = random.choice(UFO_SCORE_VALUES)
    def update(self):
        self.rect.x += UFO_SPEED
        if self.rect.left>SCREEN_WIDTH: self.alive=False
    def draw(self):
        screen.blit(UFO_SURF,self.rect)

# Game loop

def main():
    player = Player()
    formation = Formation()
    bunkers = [Bunker(100 + i*150) for i in range(BUNKER_COUNT)]
    inv_bullets = []
    ufo = None
    next_ufo = pygame.time.get_ticks() + random.randint(20000,40000)

    running=True
    while running:
        dt = clock.tick(FPS)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            if e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE: player.shoot()
        keys=pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player.move(-1)
        if keys[pygame.K_RIGHT]: player.move(1)

        # updates
        player.update()
        formation.update()
        # player bullets vs invaders
        for b in player.bullets[:]:
            # invader hit
            for inv in formation.invaders:
                if not inv.alive: continue
                x = formation.offset_x + inv.col*(INVADER_SIZE+INVADER_X_GAP)
                y = formation.offset_y + inv.row*(INVADER_SIZE+INVADER_Y_GAP)
                rect = pygame.Rect(x,y,INVADER_SIZE,INVADER_SIZE)
                if b.colliderect(rect):
                    inv.alive=False
                    player.score += (5-inv.row)*10
                    invader_kill_sound.play()
                    player.bullets.remove(b)
                    break
            # bunker hit
            for bunker in bunkers:
                for block in bunker.blocks:
                    if b.colliderect(block):
                        bunker.blocks.remove(block)
                        if b in player.bullets: player.bullets.remove(b)
                        break
        # invader shooting
        for inv in formation.invaders:
            if not inv.alive: continue
            if random.random()<0.0005:
                x = formation.offset_x + inv.col*(INVADER_SIZE+INVADER_X_GAP)+INVADER_SIZE//2
                y = formation.offset_y + inv.row*(INVADER_SIZE+INVADER_Y_GAP)+INVADER_SIZE
                inv_bullets.append(pygame.Rect(x,y,BULLET_WIDTH,BULLET_HEIGHT))
        # update invader bullets
        for b in inv_bullets[:]:
            b.y += BULLET_SPEED-3
            # hit player
            if b.colliderect(player.rect):
                player.lives-=1
                player_explosion_sound.play()
                inv_bullets.remove(b)
            # hit bunker
            for bunker in bunkers:
                for block in bunker.blocks:
                    if b.colliderect(block): bunker.blocks.remove(block)
            if b.top>SCREEN_HEIGHT: inv_bullets.remove(b)
        # UFO spawn
        if not ufo and pygame.time.get_ticks()>next_ufo:
            ufo=UFO(); ufo_sound.play(); next_ufo=pygame.time.get_ticks()+random.randint(30000,60000)
        if ufo:
            ufo.update()
            # player hit UFO
            for b in player.bullets[:]:
                if b.colliderect(ufo.rect):
                    player.score+=ufo.score
                    invader_kill_sound.play()
                    ufo=None; player.bullets.remove(b)
            if ufo and not ufo.alive: ufo=None
        # lose/win
        if player.lives<=0 or any((formation.offset_y + inv.row*(INVADER_SIZE+INVADER_Y_GAP)+INVADER_SIZE)>=player.rect.y for inv in formation.invaders if inv.alive):
            game_over("GAME OVER", player.score)
            running=False
        if not any(inv.alive for inv in formation.invaders):
            game_over("YOU WIN!", player.score)
            running=False
        # draw
        screen.fill((0,0,0))
        player.draw()
        formation.draw()
        for b in inv_bullets: pygame.draw.rect(screen,(255,255,0),b)
        for bunker in bunkers: bunker.draw()
        if ufo: ufo.draw()
        hud = font.render(f"SCORE: {player.score}   LIVES: {player.lives}",True,(255,255,255))
        screen.blit(hud,(10,10))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

# Menus
def title_screen():
    while True:
        screen.fill((0,0,0))
        txt = large_font.render("SPACE INVADERS",True,(0,255,0))
        screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2-40)))
        txt2 = font.render("PRESS ENTER",True,(255,255,255))
        screen.blit(txt2, txt2.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2+20)))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN and e.key==pygame.K_RETURN: return


def game_over(msg, score):
    while True:
        screen.fill((0,0,0))
        t1 = large_font.render(msg,True,(255,0,0))
        t2 = font.render(f"FINAL SCORE: {score}",True,(255,255,255))
        t3 = font.render("PRESS ENTER TO RESTART",True,(255,255,0))
        screen.blit(t1,t1.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2-40)))
        screen.blit(t2,t2.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2)))
        screen.blit(t3,t3.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2+40)))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN and e.key==pygame.K_RETURN: main()

if __name__ == "__main__":
    title_screen()
    main()
