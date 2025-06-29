import pygame, sys, math, random
from array import array

# ---------- CONFIG ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
BLACK  = (  0,   0,   0)
WHITE  = (250, 250, 250)
GREEN  = ( 80, 255,  80)
PINK   = (255,  80, 255)
BLUE   = ( 80, 160, 255)
RED    = (255,  60,  60)
PALETTE = [WHITE, GREEN, PINK, BLUE, RED]

INV_COLS, INV_ROWS = 10, 5
INV_H_SPACING, INV_V_SPACING = 50, 40
INV_START_X, INV_START_Y = 120, 80
INV_MOVE_INTERVAL = 30        # frames between steps (slow SNES pace)
INV_STEP_X = 10               # pixels per horizontal step
INV_STEP_Y = 16               # pixels down when edge hit

PLAYER_SPEED = 4
BULLET_SPEED = -8
INV_BULLET_SPEED = 4
PLAYER_COOLDOWN = 20          # frames
INV_SHOOT_INTERVAL = 90       # frames

SHIELD_Y = 420
SHIELD_BLOCK = 8
SHIELD_W, SHIELD_H = 10, 5    # blocks
LIVES = 3

SAMPLE_RATE = 44100

# ---------- SFX ----------
def tone(freq=440, ms=100, volume=0.5):
    length = int(SAMPLE_RATE*ms/1000)
    buf = array('h')
    factor = 2*math.pi*freq/SAMPLE_RATE
    for i in range(length):
        sample = int(volume*32767*math.sin(i*factor))
        buf.append(sample)
    return pygame.mixer.Sound(buffer=buf)

pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 512)
pygame.init()
pygame.display.set_caption("Space Invaders - SNES Slow Mo")

# Sounds
SND_SHOOT      = tone(880, 120, .4)
SND_INV_HIT    = tone(660, 80,  .4)
SND_SHIELD_HIT = tone(330, 60,  .3)
SND_PLAYER_HIT = tone(110, 400, .5)
SND_WIN        = tone(1046,600, .6)

# Screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock  = pygame.time.Clock()

font  = pygame.font.SysFont("Courier", 24, bold=True)

# ---------- GAME OBJECTS ----------
class Player:
    def __init__(self):
        self.w, self.h = 50, 20
        self.x = WIDTH//2 - self.w//2
        self.y = HEIGHT - 60
        self.cool = 0
        self.lives = LIVES
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += PLAYER_SPEED
        self.x = max(0, min(WIDTH-self.w, self.x))
        if self.cool: self.cool -=1
    def shoot(self, bullets):
        if self.cool==0:
            bullets.append([self.x+self.w//2, self.y, BULLET_SPEED, 'player'])
            SND_SHOOT.play()
            self.cool = PLAYER_COOLDOWN
    def draw(self, surf):
        pygame.draw.rect(surf, WHITE, self.rect())

class Invaders:
    def __init__(self):
        self.invaders=[]
        for r in range(INV_ROWS):
            for c in range(INV_COLS):
                x = INV_START_X + c * INV_H_SPACING
                y = INV_START_Y + r * INV_V_SPACING
                self.invaders.append(pygame.Rect(x, y, 32, 24))
        self.dir = 1
        self.timer = INV_MOVE_INTERVAL
    def step(self):
        edge_hit=False
        for inv in self.invaders:
            inv.x += self.dir * INV_STEP_X
            if inv.right >= WIDTH-20 or inv.left <= 20:
                edge_hit=True
        if edge_hit:
            self.dir *= -1
            for inv in self.invaders:
                inv.y += INV_STEP_Y
    def update(self):
        self.timer -=1
        if self.timer<=0:
            self.step()
            self.timer = INV_MOVE_INTERVAL
    def draw(self, surf):
        for i,inv in enumerate(self.invaders):
            color = PALETTE[(i//INV_COLS)%len(PALETTE)]
            pygame.draw.rect(surf, color, inv)
    def shoot(self, bullets):
        shooters = {}
        for inv in self.invaders:
            shooters.setdefault(inv.x//INV_H_SPACING,[]).append(inv)
        if shooters:
            col = random.choice(list(shooters.keys()))
            inv = max(shooters[col], key=lambda i:i.y)
            bullets.append([inv.centerx, inv.bottom, INV_BULLET_SPEED, 'inv'])
    def bottom(self):
        return max(inv.bottom for inv in self.invaders) if self.invaders else 0

class Shields:
    def __init__(self):
        self.blocks=[]
        spacing = (WIDTH-4*SHIELD_W*SHIELD_BLOCK)//5
        for b in range(4):
            base_x = spacing + b*(spacing+SHIELD_W*SHIELD_BLOCK)
            for yb in range(SHIELD_H):
                for xb in range(SHIELD_W):
                    if yb<2 or xb not in (0,SHIELD_W-1): # carve out
                        rect = pygame.Rect(base_x+xb*SHIELD_BLOCK,
                                           SHIELD_Y+yb*SHIELD_BLOCK,
                                           SHIELD_BLOCK, SHIELD_BLOCK)
                        self.blocks.append(rect)
    def draw(self,surf):
        for rect in self.blocks:
            pygame.draw.rect(surf, GREEN, rect)
    def hit(self,bullet):
        for rect in self.blocks:
            if rect.collidepoint(bullet[0], bullet[1]):
                self.blocks.remove(rect)
                return True
        return False

# ---------- CRT Overlay ----------
crt = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for y in range(0, HEIGHT, 2):
    pygame.draw.line(crt,(0,0,0,50),(0,y),(WIDTH,y))

# ---------- GAME LOOP ----------
def main():
    player = Player()
    invaders = Invaders()
    shields  = Shields()
    bullets  = []
    inv_shoot_timer = INV_SHOOT_INTERVAL
    state = 'PLAY'
    while True:
        # ---------- EVENTS ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if state=='PLAY' and event.type==pygame.KEYDOWN and event.key in (pygame.K_SPACE,pygame.K_z,pygame.K_RETURN):
                player.shoot(bullets)
            if state!='PLAY' and event.type==pygame.KEYDOWN:
                main(); return

        keys=pygame.key.get_pressed()
        if state=='PLAY':
            # ---------- UPDATE ----------
            player.update(keys)
            invaders.update()

            # bullets
            for b in bullets[:]:
                b[1]+=b[2]
                if b[1]<0 or b[1]>HEIGHT:
                    bullets.remove(b)

            # collisions
            for b in bullets[:]:
                if b[3]=='player':
                    # invader hit
                    for inv in invaders.invaders:
                        if inv.collidepoint(b[0],b[1]):
                            invaders.invaders.remove(inv)
                            bullets.remove(b)
                            SND_INV_HIT.play()
                            break
                if b in bullets and shields.hit(b):
                    bullets.remove(b)
                    SND_SHIELD_HIT.play()
                if b in bullets and b[3]=='inv':
                    if player.rect().collidepoint(b[0],b[1]):
                        bullets.remove(b)
                        player.lives-=1
                        SND_PLAYER_HIT.play()
                        if player.lives<=0:
                            state='LOSE'
                            break

            # invader bullets
            inv_shoot_timer-=1
            if inv_shoot_timer<=0:
                invaders.shoot(bullets)
                inv_shoot_timer = INV_SHOOT_INTERVAL

            # lose conditions
            if invaders.bottom()>=player.y-10:
                state='LOSE'
            # win
            if not invaders.invaders:
                state='WIN'; SND_WIN.play()

        # ---------- DRAW ----------
        screen.fill(BLACK)
        if state=='PLAY':
            player.draw(screen)
            invaders.draw(screen)
            shields.draw(screen)
            for b in bullets:
                color = WHITE if b[3]=='player' else RED
                pygame.draw.rect(screen, color, (b[0]-2, b[1]-6, 4, 8))
            # HUD
            lives_surf = font.render(f"Lives: {player.lives}", True, WHITE)
            screen.blit(lives_surf,(10,10))
        else:
            msg = "YOU WIN!" if state=='WIN' else "GAME OVER"
            txt = font.render(msg,True,PINK if state=='WIN' else RED)
            screen.blit(txt,(WIDTH//2-txt.get_width()//2, HEIGHT//2-40))
            sub = font.render("Press any key", True, WHITE)
            screen.blit(sub,(WIDTH//2-sub.get_width()//2, HEIGHT//2+10))
        # CRT overlay
        screen.blit(crt,(0,0))
        pygame.display.flip()
        clock.tick(FPS)

if __name__=="__main__":
    main()
