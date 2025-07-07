import pygame, sys, math
pygame.init()

TILE = 32
W, H = 20 * TILE, 15 * TILE
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

# Level map: 0 = empty, 1 = ground
level = [[0]*20 for _ in range(15)]
for x in range(20):
    level[13][x] = 1  # ground
    if x in range(5, 10):
        level[10][x] = 1  # platform

# Mario state
mario = {
    'x': 2*TILE, 'y': 11*TILE,
    'vx': 0, 'vy': 0,
    'on_ground': False,
    'w': 24, 'h': 32
}

# King Boo state
boo = {
    'x': 14*TILE, 'y': 8.5*TILE,
    'vx': 0, 'vy': 0,
    'dir': -1,
    'float_timer': 0,
    'w': 48, 'h': 48
}

def draw_tile(x, y, t):
    if t == 1:
        pygame.draw.rect(screen, (70,180,255), (x*TILE, y*TILE, TILE, TILE))

def draw_level():
    for y, row in enumerate(level):
        for x, t in enumerate(row):
            draw_tile(x, y, t)

def mario_rect():
    return pygame.Rect(int(mario['x']), int(mario['y']), mario['w'], mario['h'])

def boo_rect():
    return pygame.Rect(int(boo['x']), int(boo['y']), boo['w'], boo['h'])

def draw_mario():
    x, y = int(mario['x']), int(mario['y'])
    # Body (blue overalls)
    pygame.draw.rect(screen, (60, 80, 200), (x+6, y+16, 12, 16), border_radius=5)
    # Face
    pygame.draw.ellipse(screen, (255, 226, 185), (x+4, y+4, 16, 14))
    # Hat
    pygame.draw.ellipse(screen, (220,0,0), (x+5, y-4, 14, 8))
    # Eyes
    pygame.draw.ellipse(screen, (0,0,0), (x+8, y+10, 2, 5))
    pygame.draw.ellipse(screen, (0,0,0), (x+14, y+10, 2, 5))
    # Arms
    pygame.draw.rect(screen, (255, 226, 185), (x, y+18, 5, 12), border_radius=3)
    pygame.draw.rect(screen, (255, 226, 185), (x+19, y+18, 5, 12), border_radius=3)
    # Shoes
    pygame.draw.rect(screen, (120, 60, 20), (x+5, y+32, 6, 6), border_radius=2)
    pygame.draw.rect(screen, (120, 60, 20), (x+13, y+32, 6, 6), border_radius=2)

def draw_king_boo():
    x, y = int(boo['x'] + boo['w']//2), int(boo['y'] + boo['h']//2)
    # Body (blue-white)
    pygame.draw.circle(screen, (200,220,255), (x, y), 24)
    pygame.draw.circle(screen, (90,130,255), (x, y), 24, 4)  # blue outline
    # Face (SMW-style)
    pygame.draw.ellipse(screen, (255,255,255), (x-18, y-15, 36, 28))
    pygame.draw.arc(screen, (0,0,255), (x-22, y-18, 44, 32), 3.7, 2.7, 4)
    # Eyes
    pygame.draw.ellipse(screen, (0,0,180), (x-10, y-8, 7, 12))
    pygame.draw.ellipse(screen, (0,0,180), (x+3, y-8, 7, 12))
    # Mouth
    pygame.draw.ellipse(screen, (255,80,80), (x-7, y+6, 14, 8))
    # Teeth
    pygame.draw.rect(screen, (255,255,255), (x-4, y+10, 3, 5))
    pygame.draw.rect(screen, (255,255,255), (x+1, y+10, 3, 5))
    # Crown (yellow w/ red jewel)
    pygame.draw.polygon(screen, (255,240,80), [(x-5,y-25),(x+5,y-25),(x,y-32)])
    pygame.draw.circle(screen, (255,80,80), (x, y-30), 2)

def collide_tile(x, y, w, h):
    for i in range(int(x)//TILE, int(x+w-1)//TILE+1):
        for j in range(int(y)//TILE, int(y+h-1)//TILE+1):
            if 0 <= i < 20 and 0 <= j < 15 and level[j][i]:
                return True
    return False

def move_mario():
    keys = pygame.key.get_pressed()
    # X physics (SMW: fast accel, friction)
    accel = 1.2
    fric = 0.84 if mario['on_ground'] else 0.94
    mario['vx'] *= fric
    if keys[pygame.K_LEFT]:  mario['vx'] -= accel
    if keys[pygame.K_RIGHT]: mario['vx'] += accel
    # Limit speed
    mario['vx'] = max(-5, min(5, mario['vx']))

    # Y physics (gravity, jump)
    gravity = 0.75 if not mario['on_ground'] else 2
    mario['vy'] += gravity
    if mario['vy'] > 12: mario['vy'] = 12
    if keys[pygame.K_z] or keys[pygame.K_SPACE]:
        if mario['on_ground']:
            mario['vy'] = -13.5  # SMW-style jump
            mario['on_ground'] = False

    # X move/collision
    nx = mario['x'] + mario['vx']
    if not collide_tile(nx, mario['y'], mario['w'], mario['h']):
        mario['x'] = nx
    else:
        # Nudge out of wall
        while not collide_tile(mario['x'] + (1 if mario['vx'] > 0 else -1), mario['y'], mario['w'], mario['h']):
            mario['x'] += (1 if mario['vx'] > 0 else -1)
        mario['vx'] = 0

    # Y move/collision
    ny = mario['y'] + mario['vy']
    mario['on_ground'] = False
    if not collide_tile(mario['x'], ny, mario['w'], mario['h']):
        mario['y'] = ny
    else:
        # Hit floor/ceiling
        if mario['vy'] > 0:
            mario['on_ground'] = True
        while not collide_tile(mario['x'], mario['y'] + (1 if mario['vy'] > 0 else -1), mario['w'], mario['h']):
            mario['y'] += (1 if mario['vy'] > 0 else -1)
        mario['vy'] = 0

def move_boo():
    dx = (mario['x'] + mario['w']//2) - (boo['x'] + boo['w']//2)
    boo['float_timer'] += 0.03
    boo['y'] = 8.5*TILE + 16 * math.sin(boo['float_timer'])

    keys = pygame.key.get_pressed()
    mario_looks_left = keys[pygame.K_LEFT]
    looking_away = (dx < 0 and not mario_looks_left) or (dx > 0 and mario_looks_left)
    if looking_away:
        speed = 1.8
        if abs(dx) > 3:
            boo['x'] += speed if dx > 0 else -speed

    boo['x'] = max(10*TILE, min(boo['x'], 17*TILE))

def check_events():
    if mario_rect().colliderect(boo_rect()):
        print("Boss defeated! (Or you got haunted!)")
        pygame.time.wait(1200)
        pygame.quit()
        sys.exit()

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: sys.exit()
    screen.fill((150,220,255))
    draw_level()
    move_mario()
    draw_mario()
    move_boo()
    draw_king_boo()
    check_events()
    pygame.display.flip()
    clock.tick(60)
