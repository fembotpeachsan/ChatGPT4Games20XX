import pygame
import sys
import random

pygame.init()

# -----------------
# CONSTANTS & SETUP
# -----------------
WIDTH, HEIGHT = 800, 600
FPS = 60
TILE_SIZE = 40
FONT = pygame.font.SysFont("Courier", 20)

# Colors
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GREEN      = (34, 177,  76)
DARK_GREEN = (0,  155,   0)
BROWN      = (185, 122, 87)
BLUE       = (0,   0,  255)
RED        = (255, 0,    0)
GRAY       = (195, 195,195)
DARK_GRAY  = (100, 100,100)
LIGHT_GRAY = (220, 220,220)

# Screen, clock, caption
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokemon Red-Inspired Pygame Demo (No PNG)")
clock = pygame.time.Clock()

# -----------------
# WORLD & PLAYER
# -----------------
# Simple map: 0 = ground, 1 = grass
WORLD_MAP = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,1,0,0,1,1,1,0,0,1,1,1,0,0,1,1,1,0],
    [0,1,0,1,0,0,1,0,1,0,0,1,0,1,0,0,1,0,1,0],
    [0,1,1,1,0,0,1,1,1,0,0,1,1,1,0,0,1,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
]

# Player
player_rect = pygame.Rect(100, 100, TILE_SIZE // 2, TILE_SIZE // 2)
speed = 5

# Simple 2-frame animation
player_anim_frame = 0
player_anim_timer = 0
ANIM_INTERVAL = 10  # Toggle frames after these many logic ticks

# -----------------
# BATTLE SYSTEM
# -----------------
in_battle = False
player_hp = 20
max_player_hp = 20
enemy_hp = 15
max_enemy_hp = 15
battle_message = "A wild Pykemon appeared!"

menu_options = ["Fight", "Run"]
selected_option = 0

# -----------------
# HELPER FUNCTIONS
# -----------------
def draw_health_bar(x, y, current_hp, max_hp):
    """Draws a simple outlined health bar with a color fill."""
    bar_width = 150
    bar_height = 20
    pygame.draw.rect(screen, BLACK, (x, y, bar_width, bar_height), 2)  # Outline
    ratio = max(0, current_hp / max_hp)  # Prevent negative width
    fill_width = int(bar_width * ratio)
    # Turn bar red if HP < ~30%
    fill_color = (0, 200, 0) if ratio >= 0.3 else (200, 0, 0)
    pygame.draw.rect(screen, fill_color, (x+1, y+1, fill_width-2, bar_height-2))

def draw_tile(x, y, tile_type):
    """
    Draw a single map tile at grid (x, y).
    0 = ground tile, 1 = grass tile, all done with shapes/lines/circles (no PNG).
    """
    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    if tile_type == 0:
        # Ground tile: fill with brown, add diagonal lines for texture
        pygame.draw.rect(screen, BROWN, rect)
        for i in range(0, TILE_SIZE, 8):
            start_pos = (rect.x + i, rect.y)
            end_pos   = (rect.x, rect.y + i)
            pygame.draw.line(screen, DARK_GRAY, start_pos, end_pos, 1)
    else:
        # Grass tile: fill with green + circles as "blades"
        pygame.draw.rect(screen, GREEN, rect)
        # We seed a random generator with x & y for consistent "texture" each frame
        tile_rng = random.Random(x + y * 9999)
        for _ in range(3):  # a few random circles
            cx = rect.x + tile_rng.randint(5, TILE_SIZE - 5)
            cy = rect.y + tile_rng.randint(5, TILE_SIZE - 5)
            pygame.draw.circle(screen, DARK_GREEN, (cx, cy), 2)

def draw_world():
    """Draw the entire map by iterating the 2D list."""
    for y, row in enumerate(WORLD_MAP):
        for x, tile_type in enumerate(row):
            draw_tile(x, y, tile_type)

def update_player_animation(is_moving):
    """
    Toggle between two frames whenever the player is moving.
    If not moving, reset to standing frame 0.
    """
    global player_anim_timer, player_anim_frame
    if is_moving:
        player_anim_timer += 1
        if player_anim_timer >= ANIM_INTERVAL:
            player_anim_timer = 0
            player_anim_frame = 1 - player_anim_frame  # flip between 0 and 1
    else:
        player_anim_frame = 0
        player_anim_timer = 0

def draw_player():
    """Draw the player differently depending on current animation frame."""
    if player_anim_frame == 0:
        # Frame 0: standing
        pygame.draw.rect(screen, BLUE, player_rect)
    else:
        # Frame 1: "stepping" – just shifting the rectangle for a basic effect
        step_rect = player_rect.copy()
        step_rect.y -= 2  # shift upward a bit to mimic a step
        pygame.draw.rect(screen, BLUE, step_rect)

def start_battle():
    """Enter the battle state, resetting HP and message."""
    global in_battle, player_hp, enemy_hp, battle_message
    in_battle = True
    player_hp = max_player_hp
    enemy_hp = max_enemy_hp
    battle_message = "A wild Pykemon appeared!"

def draw_battle():
    """
    Clear screen, draw background, 'sprites', health bars, text, and menu options.
    """
    screen.fill(WHITE)
    # Simple ground rectangle
    pygame.draw.rect(screen, LIGHT_GRAY, (0, 300, WIDTH, 300))

    # Enemy: a big red circle up top
    pygame.draw.circle(screen, RED, (600, 200), 40)
    # Player: a blue rectangle at the bottom
    pygame.draw.rect(screen, BLUE, (100, 350, 40, 40))

    # Health bars
    draw_health_bar(500, 100, enemy_hp, max_enemy_hp)
    draw_health_bar(100, 450, player_hp, max_player_hp)

    # Labels
    enemy_label = FONT.render("Enemy", True, BLACK)
    screen.blit(enemy_label, (500, 70))
    player_label = FONT.render("You", True, BLACK)
    screen.blit(player_label, (100, 420))

    # Battle text (allow multiline with \n)
    lines = battle_message.split("\n")
    offset = 0
    for line in lines:
        msg_surf = FONT.render(line, True, BLACK)
        screen.blit(msg_surf, (50, 550 + offset))
        offset += 25

    # Menu
    for idx, option in enumerate(menu_options):
        color = RED if idx == selected_option else BLACK
        opt_surf = FONT.render(option, True, color)
        screen.blit(opt_surf, (500, 300 + idx * 30))

def handle_battle_input():
    """
    Respond to menu selection in battle: either FIGHT or RUN.
    """
    global in_battle, enemy_hp, player_hp, battle_message
    choice = menu_options[selected_option]

    if choice == "Fight":
        # Player attack
        dmg = random.randint(3, 6)
        enemy_hp -= dmg
        battle_message = f"You dealt {dmg} damage!"

        if enemy_hp <= 0:
            battle_message += "\nEnemy fainted!"
            in_battle = False
            return

        # Enemy attack
        enemy_dmg = random.randint(2, 5)
        player_hp -= enemy_dmg
        battle_message += f"\nEnemy dealt {enemy_dmg} damage!"

        if player_hp <= 0:
            battle_message += "\nYou fainted!"
            # You can either set in_battle = False or restart, etc.
    elif choice == "Run":
        battle_message = "You got away safely!"
        in_battle = False

# -----------------
# MAIN GAME LOOP
# -----------------
running = True
while running:
    clock.tick(FPS)

    # 1. Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if in_battle:
                # Battle menu navigation
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_z:
                    handle_battle_input()
            else:
                # Overworld action key
                if event.key == pygame.K_z:
                    # Force a battle or do something else
                    start_battle()

    # 2. Update game logic
    if in_battle:
        # Just draw battle screen, skip overworld logic
        draw_battle()
    else:
        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_LEFT]:
            player_rect.x -= speed
            moving = True
        if keys[pygame.K_RIGHT]:
            player_rect.x += speed
            moving = True
        if keys[pygame.K_UP]:
            player_rect.y -= speed
            moving = True
        if keys[pygame.K_DOWN]:
            player_rect.y += speed
            moving = True

        update_player_animation(moving)

        # Check random encounters if on grass
        tile_x = player_rect.centerx // TILE_SIZE
        tile_y = player_rect.centery // TILE_SIZE
        if 0 <= tile_y < len(WORLD_MAP) and 0 <= tile_x < len(WORLD_MAP[0]):
            if WORLD_MAP[tile_y][tile_x] == 1 and random.random() < 0.01:
                start_battle()

        # Draw overworld
        screen.fill(WHITE)
        draw_world()
        draw_player()

    # 3. Flip display
    pygame.display.flip()

pygame.quit()
sys.exit()
