import pygame
import random
import math
import struct
import sys

# ——— Settings —————————————————————————————————————————————
WIDTH, HEIGHT = 800, 600
FPS = 60

# Game States
STATE_MENU    = 0
STATE_PLAY    = 1
STATE_CREDITS = 2
STATE_WIN     = 3

# Invader grid
ROWS, COLS = 5, 11
INVADER_X_GAP, INVADER_Y_GAP = 48, 40
INVADER_START_Y = 100

# Speeds & timing
PLAYER_SPEED = 6
BULLET_SPEED = -12
INVADER_MOVE_X = 8
INVADER_MOVE_Y = 24
INVADER_MOVE_INTERVAL = 800  # ms
VIBE_INTERVAL = 500           # ms for background pulse
MENU_BLINK_INTERVAL = 500     # ms for blinking "PRESS START"

# Colors (NES palette vibes)
PALETTE = {
    "bg1": (8, 8, 32),
    "bg2": (16, 16, 48),
    "player": (124, 252, 0),
    "invader": (252, 0, 120),
    "bullet": (252, 252, 120),
    "text": (200, 200, 200)
}

# ——— Sound Generator —————————————————————————————————————
def create_sound(frequency=440, duration_ms=150, volume=0.5, wave_type='square'):
    sample_rate = 44100
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = bytearray()
    for i in range(n_samples):
        t = i / sample_rate
        if wave_type == 'square':
            s = volume * (1 if math.sin(2 * math.pi * frequency * t) >= 0 else -1)
        else:
            s = volume * math.sin(2 * math.pi * frequency * t)
        val = int(s * 32767)
        buf += struct.pack('<h', val) * 2
    return pygame.mixer.Sound(buffer=bytes(buf))

# ——— Pixel-Art Helpers ————————————————————————————————————
def make_sprite(pattern, color, scale):
    """Create a Surface from a list of strings ('1' = pixel on)."""
    h = len(pattern)
    w = len(pattern[0])
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y, row in enumerate(pattern):
        for x, c in enumerate(row):
            if c == '1':
                surf.set_at((x, y), color)
    return pygame.transform.scale(surf, (w*scale, h*scale))

# Patterns
INVADER_PAT = [
    "00111100",
    "01111110",
    "11011011",
    "11111111",
    "01111110",
    "00100100",
    "01000010",
    "10000001",
]
PLAYER_PAT = [
    "010",
    "111",
    "111",
    "111",
    "010",
]

# ——— Sprite Classes —————————————————————————————————————
class Player(pygame.sprite.Sprite):
    def __init__(self, sprite):
        super().__init__()
        self.image = sprite
        self.rect = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT - 30))
    def update(self):
        mx, _ = pygame.mouse.get_pos()
        self.rect.centerx = mx
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        super().__init__()
        self.image = sprite
        self.rect = self.image.get_rect(midbottom=(x, y))
    def update(self):
        self.rect.y += BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()

class Invader(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        super().__init__()
        self.image = sprite
        self.rect = self.image.get_rect(topleft=(x, y))

# ——— Initialization —————————————————————————————————————
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(5)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vibe Invaders")
clock = pygame.time.Clock()

# Sounds
shoot_snd = create_sound(880, 60, 0.4, 'square')
expl_snd  = create_sound(150, 300, 0.5, 'square')

# Sprites
SCALE = 4
player_sprite  = make_sprite(PLAYER_PAT, PALETTE["player"], SCALE)
invader_sprite = make_sprite(INVADER_PAT, PALETTE["invader"], SCALE)
bullet_sprite  = pygame.Surface((4, 12))
bullet_sprite.fill(PALETTE["bullet"])

# Groups
all_sprites = pygame.sprite.Group()
invaders    = pygame.sprite.Group()
bullets     = pygame.sprite.Group()
player      = Player(player_sprite)
all_sprites.add(player)

def spawn_invaders():
    # clear old invaders
    for inv in invaders.sprites():
        all_sprites.remove(inv)
    invaders.empty()
    # spawn new wave
    for row in range(ROWS):
        for col in range(COLS):
            x = 60 + col * INVADER_X_GAP
            y = INVADER_START_Y + row * INVADER_Y_GAP
            inv = Invader(x, y, invader_sprite)
            invaders.add(inv)
            all_sprites.add(inv)

spawn_invaders()
move_dir = 1

# timers
pygame.time.set_timer(pygame.USEREVENT+1, INVADER_MOVE_INTERVAL)
pygame.time.set_timer(pygame.USEREVENT+2, VIBE_INTERVAL)
pygame.time.set_timer(pygame.USEREVENT+3, MENU_BLINK_INTERVAL)

font  = pygame.font.SysFont('Consolas', 32)
small = pygame.font.SysFont('Consolas', 24)

state = STATE_MENU
score = 0
vibe_toggle = False
menu_blink  = True

running = True
while running:
    dt = clock.tick(FPS)
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        # timer events
        if ev.type == pygame.USEREVENT+2:
            vibe_toggle = not vibe_toggle
        if ev.type == pygame.USEREVENT+3:
            menu_blink = not menu_blink

        # menu inputs
        if state == STATE_MENU:
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    state = STATE_PLAY
                    score = 0
                    spawn_invaders()
                    bullets.empty()
                elif ev.key == pygame.K_c:
                    state = STATE_CREDITS

        # gameplay inputs
        elif state == STATE_PLAY:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                b = Bullet(player.rect.centerx, player.rect.top, bullet_sprite)
                all_sprites.add(b)
                bullets.add(b)
                shoot_snd.play()
            if ev.type == pygame.USEREVENT+1:
                edge = any(
                    (i.rect.right >= WIDTH and move_dir == 1) or 
                    (i.rect.left <= 0 and move_dir == -1) 
                    for i in invaders
                )
                if edge:
                    for i in invaders:
                        i.rect.y += INVADER_MOVE_Y
                    move_dir *= -1
                else:
                    for i in invaders:
                        i.rect.x += INVADER_MOVE_X * move_dir

        # credits inputs
        elif state == STATE_CREDITS:
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                state = STATE_MENU

        # win-screen inputs
        elif state == STATE_WIN:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_y:
                    # restart
                    score = 0
                    spawn_invaders()
                    bullets.empty()
                    state = STATE_PLAY
                elif ev.key == pygame.K_n:
                    running = False

    # game logic
    if state == STATE_PLAY:
        all_sprites.update()
        hits = pygame.sprite.groupcollide(invaders, bullets, True, True)
        if hits:
            expl_snd.play()
            score += len(hits) * 10
        # loss condition
        if pygame.sprite.spritecollideany(player, invaders) or any(i.rect.bottom >= player.rect.top for i in invaders):
            state = STATE_MENU
        # win condition
        if not invaders:
            state = STATE_WIN

    # drawing
    bg = PALETTE['bg2'] if vibe_toggle else PALETTE['bg1']
    screen.fill(bg)

    if state == STATE_MENU:
        title = font.render("V I B E   I N V A D E R S", True, PALETTE['text'])
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
        if menu_blink:
            prompt = small.render("PRESS START (ENTER/SPACE)", True, PALETTE['text'])
            screen.blit(prompt, prompt.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))
        credit_note = small.render("[C] Credits", True, PALETTE['text'])
        screen.blit(credit_note, credit_note.get_rect(center=(WIDTH//2, HEIGHT//2 + 60)))

    elif state == STATE_PLAY:
        all_sprites.draw(screen)
        scr = small.render(f"SCORE: {score}", True, PALETTE['text'])
        screen.blit(scr, (20,20))

    elif state == STATE_CREDITS:
        lines = [
            "CREDITS",
            "",
            "Concept & Code: @TEAM FLAMES [20XX]",
            "Inspired by Atari® classics",
            "",
            "Press [Esc] or [Enter] to Return"
        ]
        for i, txt in enumerate(lines):
            surf = small.render(txt, True, PALETTE['text'])
            screen.blit(surf, surf.get_rect(center=(WIDTH//2, 150 + i*40)))

    elif state == STATE_WIN:
        win_txt = font.render("YOU WIN!", True, PALETTE['text'])
        prompt = small.render("Restart? Y = Yes   N = No", True, PALETTE['text'])
        screen.blit(win_txt, win_txt.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))
        screen.blit(prompt, prompt.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))

    pygame.display.flip()

pygame.quit()
sys.exit()
