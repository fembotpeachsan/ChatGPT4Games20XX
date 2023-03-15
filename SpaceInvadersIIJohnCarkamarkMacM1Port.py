import pygame as pg, sys, random as r

WIDTH, HEIGHT = 800, 600
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('Space Invaders')

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
        if self.rect.x < 0 or self.rect.x > WIDTH - self.rect.width: self.lr *= -1

player, bullets, enemies = Obj(40, 20, (WIDTH-40)//2, HEIGHT-40, WHITE), pg.sprite.Group(), pg.sprite.Group()
for i in range(50, 550, 50): enemies.add(Obj(20, 20, i, 50, WHITE, lr=r.choice([-1, 1])))

running = True
while running:
    for e in pg.event.get():
        if e.type == pg.QUIT: running = False
        if e.type == pg.KEYDOWN and e.key == pg.K_SPACE: bullets.add(Obj(4, 10, player.rect.x+18, player.rect.y, WHITE, ud=-10))
    keys = pg.key.get_pressed()
    if keys[pg.K_LEFT]: player.lr = -5
    if keys[pg.K_RIGHT]: player.lr = 5
    if not (keys[pg.K_LEFT] or keys[pg.K_RIGHT]): player.lr = 0
    player.update()
    bullets.update()
    enemies.update()
    pg.sprite.groupcollide(bullets, enemies, True, True)
    screen.fill(BLACK)
    screen.blit(player.image, player.rect)
    bullets.draw(screen)
    enemies.draw(screen)
    pg.display.flip()
    pg.time.delay(30)

pg.quit()
sys.exit()
