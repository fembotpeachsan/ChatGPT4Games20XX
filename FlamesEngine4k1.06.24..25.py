import pygame, random, sys

pygame.init()

# Screen setup
WIDTH, HEIGHT, FPS = 600, 400, 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Kaizo Charizard Boss Fight")

# Colors
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
FIRE_ORANGE, FIRE_RED = (255, 100, 0), (255, 0, 0)
GROUND_COLOR, PLAYER_COLOR = (60, 200, 60), (255, 255, 0)

# Game constants
GRAVITY, GROUND_Y = 0.5, HEIGHT - 50

# Entities state
charizard_pos, charizard_hp, charizard_dir, charizard_cooldown = [WIDTH // 2, 80], 3, 1, 0
fireballs, shots = [], []
player, player_vel_y, player_speed, player_jump, on_ground = pygame.Rect(100, GROUND_Y - 30, 20, 30), 0, 3, -8, True

# Draw functions
def draw_charizard(x, y):
    pygame.draw.polygon(screen, FIRE_ORANGE, [(x, y), (x - 20, y + 40), (x + 20, y + 40)])
    pygame.draw.polygon(screen, FIRE_RED, [(x - 20, y + 10), (x - 60, y + 30), (x - 20, y + 30)])
    pygame.draw.polygon(screen, FIRE_RED, [(x + 20, y + 10), (x + 60, y + 30), (x + 20, y + 30)])
    pygame.draw.circle(screen, WHITE, (x - 5, y + 5), 2)
    pygame.draw.circle(screen, WHITE, (x + 5, y + 5), 2)

def draw_fireballs():
    for x, y, _ in fireballs:
        pygame.draw.circle(screen, FIRE_RED, (int(x), int(y)), 5)

def draw_ground():
    pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

def draw_shots():
    for s in shots:
        pygame.draw.rect(screen, PLAYER_COLOR, s)

def draw_hp_bar():
    for i in range(charizard_hp):
        pygame.draw.rect(screen, FIRE_ORANGE, (10 + i * 25, 10, 20, 10))

# Game mechanics
def fireball_attack():
    global charizard_cooldown
    if charizard_cooldown <= 0:
        fireballs.append([charizard_pos[0], charizard_pos[1] + 40, random.choice([-2, -1, 1, 2])])
        charizard_cooldown = 30
    else:
        charizard_cooldown -= 1

def update_fireballs():
    fireballs[:] = [[x + dx, y + 4, dx] for x, y, dx in fireballs if y + 4 < HEIGHT]

def move_charizard():
    global charizard_dir
    charizard_pos[0] += charizard_dir * 2
    if charizard_pos[0] < 50 or charizard_pos[0] > WIDTH - 50:
        charizard_dir *= -1

def handle_player_input():
    global player_vel_y, on_ground
    keys = pygame.key.get_pressed()
    player.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_speed
    if keys[pygame.K_SPACE] and on_ground:
        player_vel_y, on_ground = player_jump, False
    if keys[pygame.K_z] and len(shots) < 3:
        shots.append(pygame.Rect(player.centerx, player.y, 4, 8))

def apply_gravity():
    global on_ground, player_vel_y
    player.y += int(player_vel_y)
    player_vel_y += GRAVITY
    if player.y >= GROUND_Y - player.height:
        player.y, player_vel_y, on_ground = GROUND_Y - player.height, 0, True

def update_shots():
    global charizard_hp
    for s in shots[:]:
        s.y -= 6
        if abs(s.centerx - charizard_pos[0]) < 20 and abs(s.y - (charizard_pos[1] + 20)) < 20:
            charizard_hp -= 1
            shots.remove(s)
    shots[:] = [s for s in shots if s.y > 0]

# Main loop
while True:
    screen.fill(BLACK)
    if pygame.event.get(pygame.QUIT):
        pygame.quit()
        sys.exit()

    handle_player_input()
    apply_gravity()
    move_charizard()
    fireball_attack()
    update_fireballs()
    update_shots()

    draw_ground()
    draw_charizard(*charizard_pos)
    draw_fireballs()
    draw_shots()
    pygame.draw.rect(screen, PLAYER_COLOR, player)
    draw_hp_bar()

    if charizard_hp <= 0:
        font = pygame.font.SysFont(None, 48)
        text = font.render("Charizard Defeated!", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(FPS)
