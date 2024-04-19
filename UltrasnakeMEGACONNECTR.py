import pygame as pg
import sys
import random as r
from array import array

# Initialize Pygame and its mixer
pg.init()
pg.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Screen setup - fixed size window
WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('NX2 Augmenter SND Test 0.1 Infdev')

# Define colors
WHITE, BLACK = (255, 255, 255), (0, 0, 0)

# Define a function to generate beep sounds with varying frequencies
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pg.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pg.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * ((i // (sample_rate // frequency)) % 2)) for i in range(samples)]
    sound = pg.mixer.Sound(buffer=array('h', wave))
    sound.set_volume(0.1)
    return sound

# Create a list of sound objects for game events
sounds = {
    'shoot': generate_beep_sound(523.25, 0.1),  # Sound for shooting
    'hit': generate_beep_sound(587.33, 0.1),    # Sound for hitting an enemy
    'move': generate_beep_sound(659.25, 0.05)   # Sound for moving the player
}

class Obj(pg.sprite.Sprite):
    def __init__(self, w, h, x, y, clr, ud=0, lr=0):
        super().__init__()
        self.image = pg.Surface((w, h))
        self.image.fill(clr)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.ud, self.lr = ud, lr

    def update(self):
        self.rect.y += self.ud
        self.rect.x += self.lr
        if self.rect.x < 0 or self.rect.x > WIDTH - self.rect.width:
            self.lr *= -1

player, bullets, enemies = Obj(40, 20, (WIDTH-40)//2, HEIGHT-40, WHITE), pg.sprite.Group(), pg.sprite.Group()
for i in range(50, 550, 50):
    enemies.add(Obj(20, 20, i, 50, WHITE, lr=r.choice([-1, 1])))

running = True
while running:
    for e in pg.event.get():
        if e.type == pg.QUIT:
            running = False
        if e.type == pg.KEYDOWN:
            if e.key == pg.K_SPACE:
                bullets.add(Obj(4, 10, player.rect.x+18, player.rect.y, WHITE, ud=-10))
                sounds['shoot'].play()  # Play shoot sound
    keys = pg.key.get_pressed()
    if keys[pg.K_LEFT]:
        player.lr = -5
        sounds['move'].play()  # Play move sound
    if keys[pg.K_RIGHT]:
        player.lr = 5
        sounds['move'].play()  # Play move sound
    if not (keys[pg.K_LEFT] or keys[pg.K_RIGHT]):
        player.lr = 0

    player.update()
    bullets.update()
    enemies.update()

    if pg.sprite.groupcollide(bullets, enemies, True, True):
        sounds['hit'].play()  # Play hit sound when enemies are hit

    screen.fill(BLACK)
    screen.blit(player.image, player.rect)
    bullets.draw(screen)
    enemies.draw(screen)
    pg.display.flip()
    pg.time.delay(30)

pg.quit()
sys.exit()
