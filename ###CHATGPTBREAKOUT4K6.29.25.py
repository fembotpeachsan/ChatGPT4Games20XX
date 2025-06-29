import pygame
import numpy as np
import math
import sys
import random

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
TITLE = "BREAKOUT SWITCH 2 - Fixed Timestep"

PALETTE = {
    "black": (15, 15, 15),
    "white": (230, 230, 230),
    "pink": (255, 105, 180),
    "cyan": (0, 255, 255),
    "red": (255, 80, 80),
    "blue": (60, 120, 255),
    "green": (80, 255, 80),
}
BRICK_COLORS = [PALETTE["red"], PALETTE["pink"], PALETTE["blue"], PALETTE["green"]]

AUDIO_FREQ = 22050
AUDIO_CHANNELS = 2
AUDIO_BUFFER = 512

def generate_sound(freq=440, duration_ms=100, waveform='sine', duty_cycle=0.5, attack_ms=5, decay_ms=50):
    try:
        sample_rate = AUDIO_FREQ
        num_samples = int(sample_rate * duration_ms / 1000.0)
        buf = np.zeros((num_samples, AUDIO_CHANNELS), dtype=np.int16)
        max_amp = 2**15 - 1
        for i in range(num_samples):
            t = float(i) / sample_rate
            # simple ADSR envelope
            if i < attack_ms * sample_rate / 1000:
                envelope = (i / (attack_ms * sample_rate / 1000))
            else:
                envelope = 1.0 - (i - attack_ms * sample_rate / 1000) / (decay_ms * sample_rate / 1000)
            envelope = max(0, envelope)
            if waveform == 'sine':
                raw_wave = math.sin(2 * math.pi * freq * t)
            elif waveform == 'square':
                raw_wave = 1 if math.sin(2 * math.pi * freq * t) > (1 - 2 * duty_cycle) else -1
            elif waveform == 'triangle':
                raw_wave = 2 * (t * freq - math.floor(t * freq + 0.5))
                raw_wave = 2 * abs(raw_wave) - 1
            elif waveform == 'noise':
                raw_wave = random.uniform(-1, 1)
            elif waveform == 'sawtooth':
                raw_wave = 2 * (t * freq - math.floor(t * freq)) - 1
            else:
                raw_wave = 0
            sample = int(max_amp * raw_wave * envelope)
            buf[i, 0] = sample
            buf[i, 1] = sample
        return pygame.sndarray.make_sound(buf.copy(order='C'))
    except Exception:
        class Silent:
            def play(self): pass
        return Silent()

class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([100, 20])
        self.image.fill(PALETTE["cyan"])
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        self.speed = 8
        self.use_mouse = True

    def update(self, dt, time_warp_factor):
        keys = pygame.key.get_pressed()
        move_speed = self.speed * dt * time_warp_factor
        if keys[pygame.K_a]:
            self.rect.x -= move_speed
            self.use_mouse = False
        if keys[pygame.K_d]:
            self.rect.x += move_speed
            self.use_mouse = False
        if self.use_mouse:
            mouse_x, _ = pygame.mouse.get_pos()
            self.rect.centerx = mouse_x
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

class Ball(pygame.sprite.Sprite):
    def __init__(self, paddle):
        super().__init__()
        self.image = pygame.Surface([12, 12], pygame.SRCALPHA)
        pygame.draw.circle(self.image, PALETTE["white"], (6, 6), 6)
        self.rect = self.image.get_rect()
        self.radius = 6
        self.speed = 5  # <--- SLOWER BALL SPEED!
        self.velocity = pygame.math.Vector2(0, 0)
        self.on_paddle = True
        self.paddle = paddle
        self.true_pos = pygame.math.Vector2(self.rect.center)
        self.reset()

    def launch(self):
        if self.on_paddle:
            angle = random.uniform(-math.pi * 0.75, -math.pi * 0.25)
            self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * self.speed
            self.on_paddle = False

    def reset(self):
        self.on_paddle = True
        self.velocity.xy = (0, 0)
        self.true_pos.xy = (self.paddle.rect.centerx, self.paddle.rect.top - self.radius)
        self.rect.center = self.true_pos

    def update(self, dt, time_warp_factor):
        if self.on_paddle:
            self.true_pos.x = self.paddle.rect.centerx
            self.true_pos.y = self.paddle.rect.top - self.radius
        else:
            # fixed timestep: dt = 1 always simulates as though 60 FPS
            self.true_pos += self.velocity * dt
        self.rect.center = self.true_pos
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.velocity.x *= -1
            self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            self.true_pos.x = self.rect.centerx
            return "bounce"
        if self.rect.top <= 0:
            self.velocity.y *= -1
            self.rect.top = 0
            self.true_pos.y = self.rect.centery
            return "bounce"
        return None

class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface([60, 25])
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class BreakoutGame:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init(AUDIO_FREQ, -16, AUDIO_CHANNELS, AUDIO_BUFFER)
        except Exception:
            pass
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 18)
        self.running = True
        self.game_state = "playing"
        self.all_sprites = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()
        self.paddle = Paddle()
        self.ball = Ball(self.paddle)
        self.all_sprites.add(self.paddle, self.ball)
        self.create_bricks()
        self.time_warp_factor = 1.0
        self.sfx = {
            "bounce": generate_sound(freq=350, duration_ms=50, waveform='square'),
            "break": generate_sound(freq=100, duration_ms=150, waveform='noise', decay_ms=100),
            "paddle_hit": generate_sound(freq=220, duration_ms=70, waveform='sine'),
            "win": generate_sound(freq=880, duration_ms=300, waveform='sawtooth', attack_ms=10, decay_ms=250),
            "lose": generate_sound(freq=110, duration_ms=500, waveform='sawtooth', decay_ms=400)
        }
        self.crt_overlay = self.create_crt_overlay()

    def create_bricks(self):
        brick_w, brick_h, gap = 60, 25, 5
        for row in range(4):
            for col in range(10):
                x = 50 + col * (brick_w + gap)
                y = 50 + row * (brick_h + gap)
                brick = Brick(x, y, BRICK_COLORS[row % len(BRICK_COLORS)])
                self.all_sprites.add(brick)
                self.bricks.add(brick)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN) and (event.key == pygame.K_ESCAPE or event.type == pygame.QUIT):
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_state == "playing": self.ball.launch()
                else: self.__init__()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.ball.reset()
            if event.type == pygame.MOUSEMOTION:
                self.paddle.use_mouse = True
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_a, pygame.K_d):
                self.paddle.use_mouse = False
        keys = pygame.key.get_pressed()
        # no time warp on fixed-timestep engine
        self.time_warp_factor = 1.0

    def update(self):
        if self.game_state != "playing": return
        # fixed dt to simulate 60 FPS speed regardless of actual frame rate
        dt = 1.0
        self.all_sprites.update(dt, self.time_warp_factor)
        if self.ball.rect.bottom > SCREEN_HEIGHT:
            self.sfx["lose"].play()
            self.game_state = "game_over"
            return
        sound_event = self.ball.update(dt, self.time_warp_factor)
        if sound_event == "bounce": self.sfx["bounce"].play()
        if pygame.sprite.collide_rect(self.ball, self.paddle) and self.ball.velocity.y > 0:
            self.sfx["paddle_hit"].play()
            self.ball.velocity.y *= -1
            offset = (self.ball.rect.centerx - self.paddle.rect.centerx) / (self.paddle.rect.width / 2)
            self.ball.velocity.x = self.ball.speed * offset * 1.2
            self.ball.velocity = self.ball.velocity.normalize() * self.ball.speed
            self.ball.rect.bottom = self.paddle.rect.top
            self.ball.true_pos.y = self.ball.rect.centery
        collided = pygame.sprite.spritecollideany(self.ball, self.bricks)
        if collided:
            self.sfx["break"].play()
            collided.kill()
            self.ball.velocity.y *= -1
        if not self.bricks:
            self.sfx["win"].play()
            self.game_state = "win"

    def draw_overlay(self):
        fps = self.clock.get_fps()
        texts = [f"FPS: {fps:.1f}", "FIXED TIMESTEP MODE", f"BRICKS: {len(self.bricks)}"]
        for i, txt in enumerate(texts):
            surf = self.font.render(txt, True, PALETTE["white"])
            self.screen.blit(surf, (10, 10 + 20*i))
        if self.game_state in ("game_over", "win"):
            msg = "YOU WIN!" if self.game_state == "win" else "GAME OVER"
            extra = "- CLICK TO RESTART"
            text = self.font.render(f"{msg} {extra}", True, PALETTE["green"] if self.game_state=="win" else PALETTE["red"])
            self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))

    def draw(self):
        self.screen.fill(PALETTE["black"])
        self.all_sprites.draw(self.screen)
        self.draw_overlay()
        self.screen.blit(self.crt_overlay, (0, 0))
        pygame.display.flip()
        self.clock.tick(FPS)

    def create_crt_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        scan_alpha, vig_alpha = 25, 40
        for y in range(SCREEN_HEIGHT):
            if y % 3 == 0:
                pygame.draw.line(overlay, (0,0,0,scan_alpha), (0,y), (SCREEN_WIDTH,y))
            d = abs(y - SCREEN_HEIGHT/2)/(SCREEN_HEIGHT/2)
            alpha = int(vig_alpha * d*d)
            pygame.draw.line(overlay, (0,0,0,alpha), (0,y), (SCREEN_WIDTH,y))
        return overlay

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    BreakoutGame().run()
