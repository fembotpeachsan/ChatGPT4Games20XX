import pygame
import sys
import random
import math
import numpy

# --- Initialization ---
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

# --- Screen Dimensions ---
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("LOBSTA PONG 90s MODE")

# --- Clock & FPS ---
clock = pygame.time.Clock()
FPS = 60

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (222, 40, 40)
BLUE = (58, 160, 255)
YELLOW = (252, 232, 69)
GRAY = (64, 64, 64)
LED_ON = (250, 0, 40)
LED_OFF = (36, 5, 16)
MENU_CURSOR = (255, 64, 16)

# --- Fonts ---
def arcade_font(size):
    return pygame.font.SysFont("Courier New", size, bold=True)  # Courier feels 90s enough & pixelly

font_big = arcade_font(84)
font_menu = arcade_font(52)
font_score = arcade_font(90)
font_over = arcade_font(112)
font_small = arcade_font(38)

# --- CRT Overlay ---
def draw_crt(surface):
    # Even scanlines
    scanline = pygame.Surface((surface.get_width(), 2), pygame.SRCALPHA)
    scanline.fill((0,0,0,36))
    for y in range(0, surface.get_height(), 4):
        surface.blit(scanline, (0, y))
    # Fake shadow mask
    for x in range(0, surface.get_width(), 4):
        pygame.draw.line(surface, (0,0,0,15), (x,0), (x,surface.get_height()))

# --- SFX Generator ---
def make_sound(frequency, duration=0.12, vol=0.13):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
    t = numpy.linspace(0., duration, n_samples)
    wave = numpy.sign(numpy.sin(2 * math.pi * frequency * t))  # More square wave (arcade)
    max_sample = 2**(16 - 1) - 1
    buf[:, 0] = (wave * max_sample * vol).astype(numpy.int16)
    buf[:, 1] = buf[:, 0]
    return pygame.sndarray.make_sound(buf)

snd_menu_move = make_sound(520, 0.09)
snd_menu_select = make_sound(1440, 0.12)
snd_beep = make_sound(700, 0.06)
snd_bop = make_sound(300, 0.06)
snd_score = make_sound(1100, 0.18, 0.18)
snd_lose = make_sound(80, 0.4, 0.23)

# --- Menu Dither BG ---
def draw_menu_bg(surface):
    for y in range(0, surface.get_height(), 8):
        color = RED if (y//8)%2 == 0 else BLUE
        pygame.draw.rect(surface, color, (0, y, surface.get_width(), 8))

# --- Game Sprites ---
class Paddle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([18, 140])
        self.image.fill(WHITE)
        pygame.draw.rect(self.image, BLUE, (0,0,18,140), 3)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 12

    def move_up(self):
        self.rect.y -= self.speed
        if self.rect.top < 0:
            self.rect.top = 0

    def move_down(self):
        self.rect.y += self.speed
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def ai_move(self, ball):
        # Classic 90s rubber-band AI
        if self.rect.centery < ball.rect.centery and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed * 0.75
        if self.rect.centery > ball.rect.centery and self.rect.top > 0:
            self.rect.y -= self.speed * 0.75

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([26, 26], pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, WHITE, (0,0,26,26))
        pygame.draw.ellipse(self.image, RED, (4,4,18,18), 2)
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = 10 * random.choice((1, -1))
        self.speed_y = 10 * random.choice((1, -1))

    def update(self):
        self.rect.x += int(self.speed_x)
        self.rect.y += int(self.speed_y)
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y *= -1
            snd_bop.play()

    def bounce(self):
        self.speed_x *= -1.08
        self.speed_y += random.uniform(-1.4, 1.4)
        snd_beep.play()

# --- Main Menu ---
def main_menu():
    selected = 0
    options = ["INSERT COIN", "START GAME", "QUIT"]
    tick = 0
    screen_shake = 0
    while True:
        tick += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                    snd_menu_move.play()
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                    snd_menu_move.play()
                if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                    snd_menu_select.play()
                    screen_shake = 16
                    if options[selected] == "START GAME":
                        return
                    if options[selected] == "QUIT":
                        pygame.quit(); sys.exit()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # Draw dithered bg
        draw_menu_bg(screen)
        # Main Title
        title = font_big.render("LOBSTA PONG", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 60))
        # "90s MODE" splash
        splash = font_menu.render("90s MODE", True, RED if (tick//10)%2 else BLUE)
        screen.blit(splash, (SCREEN_WIDTH//2 - splash.get_width()//2, 165))
        # Menu options
        for i, opt in enumerate(options):
            color = YELLOW if i == selected else WHITE
            font_used = font_menu if opt != "INSERT COIN" else font_small
            txt = font_used.render(opt, True, color)
            # Add some shake for selection effect
            yoffset = 300 + i * 90 + (random.randint(-screen_shake, screen_shake) if i==selected and screen_shake else 0)
            screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, yoffset))
            # Pixel cursor triangle
            if i == selected:
                pygame.draw.polygon(screen, MENU_CURSOR, [
                    (SCREEN_WIDTH//2 - txt.get_width()//2 - 40, yoffset+30),
                    (SCREEN_WIDTH//2 - txt.get_width()//2 - 15, yoffset+18),
                    (SCREEN_WIDTH//2 - txt.get_width()//2 - 40, yoffset+6),
                ])
        if screen_shake > 0: screen_shake -= 1

        # CRT lines on top
        draw_crt(screen)
        pygame.display.flip()
        clock.tick(FPS)

# --- Sprites & Score Reset ---
def reset_game():
    global player1_score, player2_score, game_over
    player1_score = 0
    player2_score = 0
    game_over = False
    ball.reset()
    player1.rect.centery = SCREEN_HEIGHT // 2
    player2.rect.centery = SCREEN_HEIGHT // 2

all_sprites = pygame.sprite.Group()
paddles = pygame.sprite.Group()
player1 = Paddle(60, SCREEN_HEIGHT // 2 - 70)
player2 = Paddle(SCREEN_WIDTH - 78, SCREEN_HEIGHT // 2 - 70)
ball = Ball()
all_sprites.add(player1, player2, ball)
paddles.add(player1, player2)
WIN_SCORE = 5

player1_score = 0
player2_score = 0
game_over = False

def draw_led_score(val, x, y, color=LED_ON):
    # Simulate 7-seg LED style with thick font and color
    txt = font_score.render(str(val), True, color)
    # Draw drop shadow
    txt_shadow = font_score.render(str(val), True, LED_OFF)
    screen.blit(txt_shadow, (x+8, y+10))
    screen.blit(txt, (x, y))

def run_game():
    global game_over
    reset_game()
    running = True
    tick = 0
    shake_amt = 0
    while running:
        tick += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_y:
                        reset_game()
                        shake_amt = 0
                    if event.key == pygame.K_n:
                        return
        if not game_over:
            # Human: right, AI: left
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                player2.move_up()
            if keys[pygame.K_DOWN]:
                player2.move_down()
            player1.ai_move(ball)
            # Ball physics
            ball.update()
            if pygame.sprite.spritecollide(ball, paddles, False):
                ball.bounce()
            if ball.rect.left <= 0:
                player2_score += 1
                snd_score.play()
                ball.reset()
            elif ball.rect.right >= SCREEN_WIDTH:
                player1_score += 1
                snd_score.play()
                ball.reset()
            if player1_score >= WIN_SCORE or player2_score >= WIN_SCORE:
                game_over = True
                snd_lose.play()
                shake_amt = 18

        # --- Drawing ---
        # BG stripes like a 90s arcade attract screen
        for y in range(0, SCREEN_HEIGHT, 32):
            col = (24,24,24) if (y//32)%2 else (56,56,56)
            pygame.draw.rect(screen, col, (0, y, SCREEN_WIDTH, 32))
        # Net
        for y in range(10, SCREEN_HEIGHT, 34):
            pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2 - 3, y, 6, 18))

        # --- Score (LED look) ---
        draw_led_score(player1_score, SCREEN_WIDTH//4, 32, BLUE)
        draw_led_score(player2_score, SCREEN_WIDTH*3//4-56, 32, RED)
        # Sprites
        if shake_amt > 0:
            offset = random.randint(-shake_amt, shake_amt)
        else:
            offset = 0
        all_sprites.draw(screen)
        # CRT on top of all
        draw_crt(screen)
        # Game over screen (big white text, shake)
        if game_over:
            txt = font_over.render("GAME OVER", True, YELLOW)
            prompt = font_menu.render("Y = Restart    N = Quit", True, WHITE)
            x_shake = offset if shake_amt else 0
            screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2 + x_shake, SCREEN_HEIGHT//2 - 170))
            screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2 + x_shake, SCREEN_HEIGHT//2 + 30))
            if shake_amt > 0: shake_amt -= 2

        pygame.display.flip()
        clock.tick(FPS)

# --- MAIN LOOP ---
while True:
    main_menu()
    run_game()
