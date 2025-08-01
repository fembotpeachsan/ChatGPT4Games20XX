"""
koopa_mashup.py – GTA-Mini & Mario-Mini in one file
Cat.sys ✕ ChatGPT • 2025-08-01
No external assets • 60 FPS • vibes ON
"""

import pygame, sys, random, math
pygame.mixer.pre_init(44100, -16, 2, 256)
pygame.init()

# ─── Globals ──────────────────────────────────────────────────────────
WIDTH, HEIGHT = 640, 400
FPS           = 60
screen        = pygame.display.set_mode((WIDTH, HEIGHT))
clock         = pygame.time.Clock()
FONT          = pygame.font.SysFont(None, 24)

# Colors
WHITE, BLACK  = (255,255,255), (0,0,0)
RED, BLUE     = (255,0,0), (0,0,255)
GREEN, YELLOW = (0,255,0), (255,255,0)
GRAY, DGRAY   = (100,100,100), (50,50,50)
SKY           = (135,206,235)
BROWN         = (139,69,19)

MENU, GTA, MARIO = "menu", "gta", "mario"
state            = MENU

def blit_center(text, y, col=WHITE):
    surf = FONT.render(text, True, col)
    screen.blit(surf, surf.get_rect(center=(WIDTH//2, y)))

# ────────────────────── GTA-Mini ──────────────────────────────────────
class GTA_Game:
    class Player:
        def __init__(self):
            self.pos = pygame.Vector2(WIDTH/2, HEIGHT/2)
            self.speed = 140               # px / s
            self.size = 10
            self.color = RED
            self.in_car = False
            self.car = None
            self.health = 100
        def move(self, direction, dt):
            if self.in_car and self.car:
                self.car.move(direction, dt)
            else:
                self.pos += direction * self.speed * dt
                self.pos.x = max(self.size, min(WIDTH-self.size,  self.pos.x))
                self.pos.y = max(self.size, min(HEIGHT-self.size, self.pos.y))
        def try_enter(self, cars):
            if self.in_car: return
            for car in cars:
                if self.pos.distance_to(car.pos+car.size/2) < 30:
                    self.in_car, self.car, car.active = True, car, True
                    break
        def exit_car(self):
            if self.in_car:
                self.in_car = False
                self.pos.update(self.car.pos + self.car.size/2)
                self.car.active = False
                self.car = None
        def draw(self, surf):
            if not self.in_car:
                pygame.draw.circle(surf, self.color, self.pos, self.size)

    class Car:
        def __init__(self):
            self.pos   = pygame.Vector2(random.randint(50, WIDTH-50),
                                        random.randint(50, HEIGHT-50))
            self.size  = pygame.Vector2(30, 20)
            self.speed = 180
            self.color = BLUE
            self.active= False
        def move(self, direction, dt):
            self.pos += direction * self.speed * dt
            self.pos.x = max(0, min(self.pos.x, WIDTH  - self.size.x))
            self.pos.y = max(0, min(self.pos.y, HEIGHT - self.size.y))
        def draw(self, surf):
            pygame.draw.rect(surf, self.color, (*self.pos, *self.size))

    class Ped:
        def __init__(self):
            self.pos = pygame.Vector2(random.randint(0, WIDTH),
                                      random.randint(0, HEIGHT))
            self.dir = pygame.Vector2(1,0).rotate(random.uniform(0,360))
            self.speed = 40
        def update(self, dt):
            self.pos += self.dir * self.speed * dt
            if random.random() < .02:
                self.dir.rotate_ip(random.uniform(-90,90))
            if not (0 < self.pos.x < WIDTH):  self.dir.x *= -1
            if not (0 < self.pos.y < HEIGHT): self.dir.y *= -1
        def draw(self, surf): pygame.draw.circle(surf, GREEN, self.pos, 6)

    class Bullet:
        def __init__(self, pos, direction):
            self.pos = pygame.Vector2(pos)
            self.dir = direction.normalize()
            self.speed = 320
        def update(self, dt): self.pos += self.dir * self.speed * dt
        def offscreen(self):  return not (0 < self.pos.x < WIDTH and 0 < self.pos.y < HEIGHT)
        def draw(self, surf): pygame.draw.circle(surf, BLACK, self.pos, 3)

    def __init__(self):
        self.player  = self.Player()
        self.cars    = [self.Car() for _ in range(3)]
        self.peds    = [self.Ped() for _ in range(5)]
        self.money   = [pygame.Vector2(random.randint(0,WIDTH), random.randint(0,HEIGHT)) for _ in range(4)]
        self.bullets = []
        self.score   = 0
        self.wanted  = 0

    # --- Controls specific to GTA scene ---
    def handle_keydown(self, key):
        if key == pygame.K_e:
            if self.player.in_car: self.player.exit_car()
            else:                  self.player.try_enter(self.cars)

    def handle_mouse(self, pos):
        if not self.player.in_car:
            direction = pygame.Vector2(pos) - (self.player.pos)
            if direction.length_squared():
                self.bullets.append(self.Bullet(self.player.pos, direction))

    # --- Per-frame update & draw ---
    def update(self, dt):
        # movement input
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT]),
            (keys[pygame.K_s] or keys[pygame.K_DOWN])  - (keys[pygame.K_w] or keys[pygame.K_UP]))
        if direction.length_squared(): direction.scale_to_length(1)
        self.player.move(direction, dt)

        for ped in self.peds: ped.update(dt)
        for b in self.bullets[:]:
            b.update(dt)
            if b.offscreen(): self.bullets.remove(b)

        # money pickup
        player_pos = self.player.pos if not self.player.in_car else self.player.car.pos + self.player.car.size/2
        for m in self.money[:]:
            if player_pos.distance_to(m) < 18:
                self.money.remove(m)
                self.money.append(pygame.Vector2(random.randint(0,WIDTH), random.randint(0,HEIGHT)))
                self.score += 10
        if self.score > 100: self.wanted = 1

    def draw(self, surf):
        surf.fill(WHITE)
        # street & buildings
        for i in range(5):
            pygame.draw.rect(surf, GRAY, (i*128, 0, 100, 60))
            pygame.draw.rect(surf, GRAY, (i*128, HEIGHT-60, 100, 60))
        pygame.draw.rect(surf, DGRAY, (0, HEIGHT//2-40, WIDTH, 80))
        # entities
        for car in self.cars:  car.draw(surf)
        for ped in self.peds:  ped.draw(surf)
        for m   in self.money: pygame.draw.circle(surf, YELLOW, m, 5)
        for b   in self.bullets: b.draw(surf)
        self.player.draw(surf)
        # UI
        surf.blit(FONT.render(f"Score: {self.score}",  True, BLACK), (10,10))
        surf.blit(FONT.render(f"Wanted: {self.wanted}",True, RED),   (10,30))

# ───────────────────── Mario-Mini ─────────────────────────────────────
class Mario_Game:
    GRAVITY = 900; JUMP = -350; SPEED = 150
    class Player(pygame.sprite.Sprite):
        def __init__(self, y_floor):
            super().__init__()
            self.image = pygame.Surface((30,50)); self.image.fill(RED)
            self.rect  = self.image.get_rect(midbottom=(120, y_floor))
            self.vy    = 0; self.on_ground = False
        def update(self, dt):
            self.vy += Mario_Game.GRAVITY * dt
            self.rect.y += self.vy * dt
        def jump(self):
            if self.on_ground: self.vy = Mario_Game.JUMP
    class Plat(pygame.sprite.Sprite):
        def __init__(self,x,y,w,h):
            super().__init__()
            self.image = pygame.Surface((w,h)); self.image.fill(BROWN)
            self.rect  = self.image.get_rect(topleft=(x,y))
    class Enemy(pygame.sprite.Sprite):
        def __init__(self,x,y):
            super().__init__()
            self.image = pygame.Surface((30,30)); self.image.fill(YELLOW)
            self.rect  = self.image.get_rect(topleft=(x,y))
            self.dir = 1
        def update(self,dt):
            self.rect.x += 60*self.dir*dt
            if self.rect.left<=0 or self.rect.right>=WIDTH: self.dir*=-1
    def __init__(self):
        floor = HEIGHT-50
        self.all  = pygame.sprite.Group()
        self.plat = pygame.sprite.Group(self.Plat(0,floor,WIDTH,50),
                                        self.Plat(300,300,200,20),
                                        self.Plat(100,200,150,20),
                                        self.Plat(450,150,150,20))
        self.enem = pygame.sprite.Group(self.Enemy(400,270),
                                        self.Enemy(200,170))
        self.goal = pygame.sprite.Sprite()
        self.goal.image = pygame.Surface((20,60)); self.goal.image.fill(GREEN)
        self.goal.rect  = self.goal.image.get_rect(bottomleft=(600,floor))
        self.player = self.Player(floor)
        self.all.add(self.plat, self.enem, self.goal, self.player)
    def keydown(self,key):
        if key==pygame.K_SPACE: self.player.jump()
    def update(self,dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  self.player.rect.x -= self.SPEED*dt
        if keys[pygame.K_RIGHT]: self.player.rect.x += self.SPEED*dt
        self.all.update(dt)
        # collisions
        self.player.on_ground=False
        for p in self.plat:
            if self.player.rect.colliderect(p.rect) and self.player.vy>0:
                self.player.rect.bottom = p.rect.top
                self.player.vy = 0; self.player.on_ground=True
        if pygame.sprite.spritecollideany(self.player,self.enem):
            blit_center("Game Over!", HEIGHT//2, RED); pygame.display.flip(); pygame.time.delay(800); return False
        if self.player.rect.colliderect(self.goal.rect):
            blit_center("You Win!", HEIGHT//2, GREEN); pygame.display.flip(); pygame.time.delay(800); return False
        return True
    def draw(self,surf): surf.fill(SKY); self.all.draw(surf)

# ─── Scene instances ────────────────────────────────────────────────
gta   = GTA_Game()
mario = Mario_Game()

# ─── Main Loop ───────────────────────────────────────────────────────
while True:
    dt = clock.tick(FPS)/1000.0
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN:
            if state==MENU:
                if e.key==pygame.K_1: state=GTA
                if e.key==pygame.K_2: state=MARIO
            else:                             # in-game hotkeys
                if e.key==pygame.K_ESCAPE: state=MENU
                if state==GTA:   gta.handle_keydown(e.key)
                if state==MARIO: mario.keydown(e.key)
        if e.type == pygame.MOUSEBUTTONDOWN and state==GTA:
            gta.handle_mouse(e.pos)

    # update & draw current scene
    if state==MENU:
        screen.fill(DGRAY)
        blit_center("KOOPA DOUBLE DEMO", HEIGHT//2-40)
        blit_center("[1] GTA-Mini",      HEIGHT//2)
        blit_center("[2] Mario-Mini",    HEIGHT//2+30)
        blit_center("ESC in-game to return here", HEIGHT-28, YELLOW)
    elif state==GTA:
        gta.update(dt); gta.draw(screen)
    elif state==MARIO:
        if not mario.update(dt): state = MENU
        mario.draw(screen)

    pygame.display.flip()
