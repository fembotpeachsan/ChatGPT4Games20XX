import pygame, random, sys
import numpy as np
import threading

pygame.init()
W, H, TILE = 720, 400, 40
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("NES-Style SMB3: Evil Waluigi Boss (Kamek Chiptune, Final Fix)")
clock = pygame.time.Clock()

# --- 8-BIT KAMEK-STYLE MELODY (Final Fix) ---
def make_tone(frequency, duration_ms, volume=0.18, samplerate=22050):
    t = np.linspace(0, duration_ms / 1000, int(samplerate * duration_ms / 1000), False)
    wave = 0.6 * np.sign(np.sin(2 * np.pi * frequency * t))  # NES square wave
    audio = (wave * volume * 32767).astype(np.int16)
    return pygame.mixer.Sound(buffer=audio.tobytes())

pygame.mixer.init()
melody = [
    (440, 360), (523, 360), (587, 320), (659, 320), (587, 320), (523, 320),
    (440, 400), (0, 180),   # Rest
    (349, 360), (392, 360), (466, 320), (523, 320), (466, 320), (392, 320),
    (349, 400), (0, 180),   # Rest
    (392, 220), (466, 220), (523, 220), (587, 220), (659, 220), (587, 220), (523, 220), (466, 220), (392, 340), (0, 250)
]
tones = []
for f, d in melody:
    if f > 0:
        tones.append((make_tone(f, d), d))
    else:
        tones.append((None, d))

# Global variable to control music
music_playing = True

def play_melody_loop():
    global music_playing
    channel = pygame.mixer.Channel(0)
    while music_playing:
        for sound, duration in tones:
            if not music_playing:
                break
            if sound:
                channel.play(sound)
            pygame.time.wait(duration)
    # Stop the channel when music should stop
    channel.stop()

threading.Thread(target=play_melody_loop, daemon=True).start()

# --- COLORS ---
BG = (107, 140, 255)
GROUND = (188, 152, 84)
BLOCK = (252, 216, 120)
MARIO_HAT = (236, 28, 36)
MARIO_SHIRT = (236, 28, 36)
MARIO_OVERALLS = (44, 80, 180)
MARIO_SKIN = (252, 220, 148)
MARIO_SHOES = (96, 52, 12)
WALUIGI_HAT = (128, 0, 192)
WALUIGI_SHIRT = (128, 0, 192)
WALUIGI_OVERALLS = (0, 0, 0)
WALUIGI_SKIN = (252, 220, 148)
WALUIGI_SHOES = (96, 52, 12)
BALL = (128, 0, 192)
FONT = pygame.font.SysFont(None, 32)

# --- LEVEL DATA ---
floor = pygame.Rect(0, H-TILE*2, W, TILE*2)
platforms = [pygame.Rect(3*TILE, H-5*TILE, 4*TILE, TILE),
             pygame.Rect(11*TILE, H-7*TILE, 4*TILE, TILE)]

# --- MARIO ---
mario = pygame.Rect(2*TILE, H-3*TILE, TILE, TILE)
mvel = [0,0]
on_ground = False
invuln = 0
hp = 3

# --- WALUIGI BOSS ---
waluigi = pygame.Rect(W-3*TILE, H-3*TILE, TILE, TILE)
wvel = [0,0]
waluigi_hp = 3
waluigi_dir = -1
waluigi_jump_timer = 60
waluigi_attack_timer = 90
waluigi_invuln = 0

# --- EVIL BALLS ---
balls = []

# --- GAME STATE ---
game_over = False
win = False

def draw_nes_mario(surface, rect):
    pygame.draw.rect(surface, MARIO_SKIN, (rect.x+10, rect.y+4, 20, 14))
    pygame.draw.rect(surface, MARIO_HAT, (rect.x+10, rect.y+4, 20, 6))
    pygame.draw.rect(surface, MARIO_SHIRT, (rect.x+12, rect.y+18, 16, 10))
    pygame.draw.rect(surface, MARIO_OVERALLS, (rect.x+12, rect.y+24, 16, 12))
    pygame.draw.rect(surface, MARIO_SHIRT, (rect.x+2, rect.y+18, 10, 8))
    pygame.draw.rect(surface, MARIO_SHIRT, (rect.x+28, rect.y+18, 10, 8))
    pygame.draw.rect(surface, MARIO_SKIN, (rect.x+2, rect.y+25, 8, 7))
    pygame.draw.rect(surface, MARIO_SKIN, (rect.x+30, rect.y+25, 8, 7))
    pygame.draw.rect(surface, MARIO_SHOES, (rect.x+10, rect.y+36, 8, 6))
    pygame.draw.rect(surface, MARIO_SHOES, (rect.x+22, rect.y+36, 8, 6))

def draw_nes_waluigi(surface, rect):
    pygame.draw.rect(surface, WALUIGI_SKIN, (rect.x+10, rect.y+4, 20, 14))
    pygame.draw.rect(surface, WALUIGI_HAT, (rect.x+10, rect.y+4, 20, 6))
    pygame.draw.ellipse(surface, (255,200,60), (rect.x+24, rect.y+10, 8,8))
    pygame.draw.rect(surface, WALUIGI_SHIRT, (rect.x+12, rect.y+18, 16, 10))
    pygame.draw.rect(surface, WALUIGI_OVERALLS, (rect.x+12, rect.y+24, 16, 12))
    pygame.draw.rect(surface, WALUIGI_SHIRT, (rect.x+2, rect.y+18, 10, 8))
    pygame.draw.rect(surface, WALUIGI_SHIRT, (rect.x+28, rect.y+18, 10, 8))
    pygame.draw.rect(surface, WALUIGI_SKIN, (rect.x+2, rect.y+25, 8, 7))
    pygame.draw.rect(surface, WALUIGI_SKIN, (rect.x+30, rect.y+25, 8, 7))
    pygame.draw.rect(surface, WALUIGI_SHOES, (rect.x+10, rect.y+36, 8, 6))
    pygame.draw.rect(surface, WALUIGI_SHOES, (rect.x+22, rect.y+36, 8, 6))
    pygame.draw.line(surface, (40,30,10), (rect.x+16, rect.y+17), (rect.x+26, rect.y+17), 3)

def reset():
    global mario, mvel, on_ground, invuln, hp
    global waluigi, wvel, waluigi_hp, waluigi_dir, waluigi_jump_timer, waluigi_attack_timer, waluigi_invuln
    global balls, game_over, win, music_playing
    mario = pygame.Rect(2*TILE, H-3*TILE, TILE, TILE)
    mvel = [0,0]
    on_ground = False
    invuln = 0
    hp = 3
    waluigi = pygame.Rect(W-3*TILE, H-3*TILE, TILE, TILE)
    wvel = [0,0]
    waluigi_hp = 3
    waluigi_dir = -1
    waluigi_jump_timer = 60
    waluigi_attack_timer = 90
    waluigi_invuln = 0
    balls = []
    game_over = False
    win = False
    music_playing = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN and game_over:
            reset()

    screen.fill(BG)
    pygame.draw.rect(screen, GROUND, floor)
    for plat in platforms:
        pygame.draw.rect(screen, BLOCK, plat)

    keys = pygame.key.get_pressed()
    if not game_over:
        mvel[0] = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 5
        if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and on_ground:
            mvel[1] = -12
        mvel[1] += 0.7

        mario.x += mvel[0]
        if mario.left < 0: mario.left = 0
        if mario.right > W: mario.right = W
        for plat in platforms+[floor]:
            if mario.colliderect(plat):
                if mvel[0]>0: mario.right = plat.left
                if mvel[0]<0: mario.left = plat.right

        mario.y += mvel[1]
        on_ground = False
        for plat in platforms+[floor]:
            if mario.colliderect(plat):
                if mvel[1]>0:
                    mario.bottom = plat.top
                    on_ground = True
                if mvel[1]<0:
                    mario.top = plat.bottom
                mvel[1] = 0

        if invuln > 0: invuln -= 1

    if invuln % 8 < 4 or invuln == 0:
        draw_nes_mario(screen, mario)

    if not game_over:
        if waluigi_invuln > 0: waluigi_invuln -= 1
        waluigi.x += waluigi_dir * 3
        if waluigi.left < TILE or waluigi.right > W-TILE: waluigi_dir *= -1
        for plat in platforms+[floor]:
            if waluigi.colliderect(plat):
                if waluigi_dir>0: waluigi.right = plat.left
                if waluigi_dir<0: waluigi.left = plat.right
                waluigi_dir *= -1
        waluigi_jump_timer -= 1
        if waluigi_jump_timer <= 0:
            waluigi_jump_timer = random.randint(40, 70)
            wvel[1] = -10
        wvel[1] += 0.5
        waluigi.y += int(wvel[1])
        for plat in platforms+[floor]:
            if waluigi.colliderect(plat):
                if wvel[1]>0:
                    waluigi.bottom = plat.top
                if wvel[1]<0:
                    waluigi.top = plat.bottom
                wvel[1] = 0
        waluigi_attack_timer -= 1
        if waluigi_attack_timer <= 0:
            waluigi_attack_timer = random.randint(50, 100)
            balls.append([waluigi.centerx, waluigi.bottom, random.choice([-4,4]), 7])
    if waluigi_invuln % 6 < 3 or waluigi_invuln == 0:
        draw_nes_waluigi(screen, waluigi)

    for ball in balls[:]:
        ball[0] += ball[2]
        ball[1] += ball[3]
        ball[3] += 0.3
        r = pygame.Rect(ball[0]-10, ball[1]-10, 20, 20)
        pygame.draw.circle(screen, BALL, r.center, 10)
        if r.colliderect(mario) and invuln==0 and not game_over:
            hp -= 1
            invuln = 40
            if hp<=0: 
                game_over=True
                music_playing = False
        if r.top > H:
            balls.remove(ball)

    if mario.colliderect(waluigi) and mvel[1]>2 and waluigi_invuln==0 and not game_over:
        waluigi_hp -= 1
        waluigi_invuln = 40
        mvel[1] = -10
        if waluigi_hp<=0:
            win=True
            game_over=True
            music_playing = False

    if mario.colliderect(waluigi) and invuln==0 and not game_over and mvel[1]<=0:
        hp -= 1
        invuln = 40
        if hp<=0: 
            game_over=True
            music_playing = False

    msg = f"Mario HP: {hp}   Waluigi HP: {waluigi_hp}"
    if win: msg += "  YOU WIN!"
    elif game_over: msg += "  GAME OVER! Press any key"
    t = FONT.render(msg, 1, (0,0,0))
    screen.blit(t, (12,12))

    pygame.display.flip()
    clock.tick(60)
