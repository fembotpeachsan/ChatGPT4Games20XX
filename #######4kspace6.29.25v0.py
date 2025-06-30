#!/usr/bin/env python3
"""
O3PRO Space Invaders – Pure‑Vibes‑Only Edition
Author: Cat‑sama + OpenAI o3
Single‑file, asset‑free, runtime‑generated Space Invaders built on Pygame.

Controls
--------
Mouse X      – Ship horizontal position  
Spacebar     – Fire laser  
ESC / Q      – Quit
"""
import math, random, sys, time, array
import pygame as pg

# ────────────────────────────────────────────────────────────
# CONFIG
# ----------------------------------------------------------------
WIDTH, HEIGHT     = 640, 480          # 4:3 retro resolution
FPS               = 60
INV_COLS, INV_ROWS= 11, 5
INV_H_PADDING     = 32
INV_V_PADDING     = 28
INV_START_Y       = 80
INV_STEP_X        = 8                 # pixels per beat (slow march)
INV_BEAT_MS       = 550               # ≈ SNES "slow‑mo" cadence
INV_DROP          = 16                # pixels to descend on edge
PLAYER_COOLDOWN   = 320               # ms between shots
INV_COOLDOWN      = 900               # ms between bombs
SHIELD_COUNT      = 4
SHIELD_WIDTH      = 8 * 8             # 8×8 pixel bricks
SHIELD_HEIGHT     = 5 * 8
LIVES             = 3
PALETTE_BG        = (8, 8, 16)
PALETTE_PLAYER    = (64, 255, 64)
PALETTE_INV1      = (255, 64, 64)
PALETTE_INV2      = (255, 160, 64)
PALETTE_SHIELD    = (48, 200, 255)
PALETTE_LASER     = (255, 255, 255)
PALETTE_BOMB      = (255, 200, 200)
CRT_ALPHA         = 64                # intensity of scan‑lines

# ────────────────────────────────────────────────────────────
# UTILITIES
# ----------------------------------------------------------------
def make_wave(freq=440, dur=0.12, volume=0.4, sr=44100, duty=0.5):
    """Generate a square‑ish wave as pg.mixer.Sound without numpy."""
    n = int(sr * dur)
    buf = array.array("h")
    amp = int(volume * 32767)
    step = sr / freq
    for i in range(n):
        phase = (i % step) / step
        val = amp if phase < duty else -amp
        buf.append(val)
    return pg.mixer.Sound(buffer=buf.tobytes())

def now_ms():
    return pg.time.get_ticks()

# ────────────────────────────────────────────────────────────
# CORE CLASSES
# ----------------------------------------------------------------
class Player(pg.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = pg.Surface((32, 16))
        self.image.fill(PALETTE_PLAYER)
        self.rect = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT - 40))
        self.last_shot = 0

    def update(self):
        mx, _ = pg.mouse.get_pos()
        self.rect.centerx = max(16, min(WIDTH - 16, mx))

    def can_shoot(self):
        return now_ms() - self.last_shot > PLAYER_COOLDOWN

class Invader(pg.sprite.Sprite):
    SPRITE_PATTERNS = [
        # simple 8×8 rectangles alternating colours for row variety
        (PALETTE_INV1, 0.9),           # colour, points multiplier
        (PALETTE_INV1, 0.9),
        (PALETTE_INV2, 0.7),
        (PALETTE_INV2, 0.7),
        (PALETTE_INV2, 0.5),
    ]
    def __init__(self, col, row, group):
        super().__init__(group)
        colour, mul = self.SPRITE_PATTERNS[row]
        self.image = pg.Surface((20, 14))
        self.image.fill(colour)
        self.rect = self.image.get_rect()
        self.base_points = int(40 * mul)
        self.col, self.row = col, row

class Shield(pg.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pg.Surface((SHIELD_WIDTH, SHIELD_HEIGHT), pg.SRCALPHA)
        self.rect = self.image.get_rect(midtop=pos)
        self._build()

    def _build(self):
        brick = pg.Surface((8,8))
        brick.fill(PALETTE_SHIELD)
        for y in range(0, SHIELD_HEIGHT, 8):
            for x in range(0, SHIELD_WIDTH, 8):
                if not (y < 8 and (x<8 or x>=SHIELD_WIDTH-8)):  # carve arch
                    self.image.blit(brick, (x,y))

    def damage(self, point):
        # knock out 8×8 cell where hit occurred
        lx = (point[0] - self.rect.x)//8*8
        ly = (point[1] - self.rect.y)//8*8
        pg.draw.rect(self.image, (0,0,0,0), (lx, ly, 8, 8))

class Projectile(pg.sprite.Sprite):
    def __init__(self, pos, vel, colour, group):
        super().__init__(group)
        self.image = pg.Surface((3, 12))
        self.image.fill(colour)
        self.rect = self.image.get_rect(midbottom=pos)
        self.vel = vel

    def update(self):
        self.rect.y += self.vel
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

# ────────────────────────────────────────────────────────────
# MAIN GAME OBJECT
# ----------------------------------------------------------------
class SpaceInvadersGame:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 1, 512)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("O3PRO Space Invaders")
        self.clock = pg.time.Clock()
        self._build_crt()
        self._load_sfx()
        self.font = pg.font.SysFont("Courier", 20, bold=True)
        self.reset()

    def reset(self):
        self.all_sprites = pg.sprite.Group()
        self.invaders    = pg.sprite.Group()
        self.player_bul  = pg.sprite.Group()
        self.inv_bombs   = pg.sprite.Group()
        self.shields     = pg.sprite.Group()
        self.player = Player(self.all_sprites)
        self.lives = LIVES
        self.score = 0
        self.state = "PLAY"
        self._init_invaders()
        self._init_shields()
        self.inv_dir = 1
        self.inv_last_move = now_ms()
        self.inv_last_shot = now_ms()

    # ────────────────────────────────── BUILD WORLD
    def _init_invaders(self):
        start_x = (WIDTH - (INV_COLS-1)*INV_H_PADDING) // 2
        for row in range(INV_ROWS):
            for col in range(INV_COLS):
                inv = Invader(col, row, self.all_sprites)
                inv.rect.topleft = (start_x + col*INV_H_PADDING,
                                    INV_START_Y + row*INV_V_PADDING)
                self.invaders.add(inv)

    def _init_shields(self):
        gap = WIDTH // (SHIELD_COUNT + 1)
        for i in range(SHIELD_COUNT):
            Shield((gap*(i+1), HEIGHT-100), [self.all_sprites, self.shields])

    # ────────────────────────────────── SOUND
    def _load_sfx(self):
        self.sfx_shoot   = make_wave(880, 0.07, 0.35)
        self.sfx_kill    = make_wave(120, 0.18, 0.5)
        self.sfx_bomb    = make_wave(260, 0.1, 0.4, duty=0.25)
        self.sfx_player_hit = make_wave(60, 0.25, 0.6)
        self.sfx_win     = make_wave(1040, 0.4, 0.5)
        self.sfx_gameover= make_wave(40, 0.7, 0.6)

    # ────────────────────────────────── CRT overlay
    def _build_crt(self):
        self.crt = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        for y in range(0, HEIGHT, 2):
            pg.draw.line(self.crt, (0,0,0, CRT_ALPHA), (0,y), (WIDTH,y))

    # ────────────────────────────────── GAME LOOP
    def run(self):
        while True:
            self._events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

    def _events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit(); sys.exit()
            if e.type == pg.KEYDOWN and e.key in (pg.K_ESCAPE, pg.K_q):
                pg.quit(); sys.exit()
            if self.state == "PLAY" and e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                if self.player.can_shoot():
                    self.player.last_shot = now_ms()
                    x = self.player.rect.centerx
                    y = self.player.rect.top
                    Projectile((x,y), -8, PALETTE_LASER, [self.all_sprites, self.player_bul])
                    self.sfx_shoot.play()

        if self.state != "PLAY" and pg.mouse.get_pressed()[0]:
            self.reset()

    # ────────────────────────────────── UPDATE WORLD
    def _update(self):
        if self.state != "PLAY":
            return

        self.all_sprites.update()
        self._invader_march()
        self._invader_fire()
        self._handle_collisions()

    def _invader_march(self):
        if now_ms() - self.inv_last_move < INV_BEAT_MS:
            return
        self.inv_last_move = now_ms()
        dx = INV_STEP_X * self.inv_dir
        # check edge collision BEFORE moving
        future_edges = [inv.rect.right+dx for inv in self.invaders] if self.inv_dir==1 else \
                       [inv.rect.left+dx for inv in self.invaders]
        if (max(future_edges) >= WIDTH-10 and self.inv_dir==1) or \
           (min(future_edges) <= 10 and self.inv_dir==-1):
            # hit side – reverse & drop
            self.inv_dir *= -1
            for inv in self.invaders:
                inv.rect.y += INV_DROP
                # lose condition
                if inv.rect.bottom >= HEIGHT-120:
                    self._game_over(False)
        else:
            for inv in self.invaders:
                inv.rect.x += dx

    def _invader_fire(self):
        if now_ms() - self.inv_last_shot < INV_COOLDOWN:
            return
        self.inv_last_shot = now_ms()
        shooters = {}
        for inv in self.invaders:
            shooters.setdefault(inv.col, inv)       # lowest row per column
        if shooters:
            gun = random.choice(list(shooters.values()))
            Projectile(gun.rect.midbottom, 5, PALETTE_BOMB, [self.all_sprites, self.inv_bombs])
            self.sfx_bomb.play()

    # ────────────────────────────────── COLLISIONS
    def _handle_collisions(self):
        # player bullets → invaders
        hits = pg.sprite.groupcollide(self.invaders, self.player_bul, True, True)
        if hits:
            for inv in hits:
                self.score += inv.base_points
            self.sfx_kill.play()
            if not self.invaders:
                self._game_over(True)

        # player bullets → shields
        for bullet in self.player_bul:
            hit = pg.sprite.spritecollideany(bullet, self.shields)
            if hit:
                hit.damage(bullet.rect.center)
                bullet.kill()

        # bombs → shields
        for bomb in self.inv_bombs:
            hit = pg.sprite.spritecollideany(bomb, self.shields)
            if hit:
                hit.damage(bomb.rect.center)
                bomb.kill()

        # bombs → player
        if pg.sprite.spritecollideany(self.player, self.inv_bombs):
            self.inv_bombs.empty()
            self.lives -= 1
            self.sfx_player_hit.play()
            if self.lives <= 0:
                self._game_over(False)

    # ────────────────────────────────── END STATES
    def _game_over(self, win):
        self.state = "WIN" if win else "LOSE"
        (self.sfx_win if win else self.sfx_gameover).play()
        self.end_time = now_ms()

    # ────────────────────────────────── DRAW
    def _draw(self):
        self.screen.fill(PALETTE_BG)
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.crt, (0,0))           # scan‑lines

        # HUD
        score_s = self.font.render(f"Score {self.score}", True, (200,255,200))
        lives_s = self.font.render(f"Lives {self.lives}", True, (200,255,200))
        self.screen.blit(score_s, (10,8))
        self.screen.blit(lives_s, (WIDTH - lives_s.get_width() - 10, 8))

        # end‑screen overlay
        if self.state in ("WIN", "LOSE"):
            alpha = min(180, (now_ms()-self.end_time)//4)
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            overlay.fill((0,0,0,alpha))
            self.screen.blit(overlay,(0,0))
            msg = "YOU WIN!" if self.state=="WIN" else "GAME OVER"
            text = self.font.render(msg, True, (255,255,255))
            sub  = self.font.render("Click to restart", True, (255,255,255))
            self.screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2 - 10)))
            self.screen.blit(sub,  sub.get_rect(center=(WIDTH//2, HEIGHT//2 + 18)))

        pg.display.flip()

# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    SpaceInvadersGame().run()
