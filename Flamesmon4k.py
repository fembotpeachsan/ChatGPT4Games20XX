import pygame
import sys

# --- Initialization ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokémon Emerald Style Battle (Zero-Shot No PNG)")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# --- Colors ---
SKY_COLOR = (135, 206, 235)
GROUND_COLOR = (222, 184, 135)
TEXTBOX_COLOR = (255, 255, 255)
BORDER_COLOR = (0, 0, 0)
HP_GREEN = (0, 255, 0)
HP_RED = (255, 0, 0)
TEXT_COLOR = (0, 0, 0)

# --- Sprite System ---
class Sprite:
    def __init__(self, x, y, sprite_data, palette, pixel_scale=5):
        self.base_x = x
        self.base_y = y
        self.x = x
        self.y = y
        self.sprite_data = sprite_data
        self.palette = palette
        self.pixel_scale = pixel_scale
        self.surface = self.build_surface()
        self.anim_offset = 0
        self.animating = False

    def build_surface(self):
        width = len(self.sprite_data[0]) * self.pixel_scale
        height = len(self.sprite_data) * self.pixel_scale
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        for y, row in enumerate(self.sprite_data):
            for x, color_index in enumerate(row):
                color = self.palette[color_index]
                if color != (0, 0, 0, 0):
                    pygame.draw.rect(
                        surf,
                        color,
                        (x * self.pixel_scale, y * self.pixel_scale, self.pixel_scale, self.pixel_scale)
                    )
        return surf

    def start_attack_anim(self):
        self.animating = True
        self.anim_offset = 0

    def update(self):
        if self.animating:
            self.anim_offset += 2
            self.x = self.base_x + self.anim_offset
            if self.anim_offset >= 10:
                self.animating = False
                self.x = self.base_x

    def draw(self, target_surface):
        target_surface.blit(self.surface, (self.x, self.y))

# --- Text System ---
class TextPrinter:
    def __init__(self, text, x, y, speed=2):
        self.text = text
        self.x = x
        self.y = y
        self.speed = speed
        self.index = 0
        self.counter = 0
        self.done = False

    def update(self):
        if not self.done:
            self.counter += 1
            if self.counter % self.speed == 0:
                self.index += 1
                if self.index >= len(self.text):
                    self.done = True

    def draw(self, target_surface):
        render_text = font.render(self.text[:self.index], True, TEXT_COLOR)
        target_surface.blit(render_text, (self.x, self.y))

    def reset(self, new_text):
        self.text = new_text
        self.index = 0
        self.counter = 0
        self.done = False

# --- Menu System ---
class Menu:
    def __init__(self, options, x, y):
        self.options = options
        self.x = x
        self.y = y
        self.selected = 0

    def draw(self, target_surface):
        for i, option in enumerate(self.options):
            color = (0, 0, 0)
            text = font.render(option, True, color)
            target_surface.blit(text, (self.x + i*160, self.y))
        cursor = font.render("▶", True, color)
        target_surface.blit(cursor, (self.x - 30 + self.selected*160, self.y))

    def move(self, direction):
        self.selected = (self.selected + direction) % len(self.options)

    def get_selected(self):
        return self.options[self.selected]

# --- Battle System ---
player_health = 100
enemy_health = 100
max_health = 100

player_turn = True
battle_state = "intro"  # intro -> menu -> player_attack -> enemy_attack -> win/lose

# Sprites
palette = [
    (0, 0, 0, 0),
    (255, 215, 0),
    (255, 0, 0),
    (220, 20, 60),
    (255, 255, 255),
]

player_sprite_data = [
    [0,0,1,1,1,1,0,0],
    [0,1,2,2,2,2,1,0],
    [1,2,1,1,1,1,2,1],
    [1,2,1,4,4,1,2,1],
    [1,2,1,4,4,1,2,1],
    [1,2,1,1,1,1,2,1],
    [0,1,2,2,2,2,1,0],
    [0,0,1,1,1,1,0,0],
]

enemy_sprite_data = [
    [0,3,3,0,0,3,3,0],
    [3,2,2,3,3,2,2,3],
    [3,2,2,2,2,2,2,3],
    [0,3,2,2,2,2,3,0],
    [0,3,2,4,4,2,3,0],
    [0,0,3,2,2,3,0,0],
    [0,0,0,3,3,0,0,0],
    [0,0,0,0,0,0,0,0],
]

player_sprite = Sprite(100, HEIGHT//2 + 80, player_sprite_data, palette, pixel_scale=8)
enemy_sprite = Sprite(WIDTH-200, 80, enemy_sprite_data, palette, pixel_scale=8)

# Text and Menu
battle_text = TextPrinter("A wild Corrupted Bowser appeared!", 30, HEIGHT-120)
menu = Menu(["FIGHT", "BAG", "POKéMON", "RUN"], 80, HEIGHT-70)

# HP Bar
def draw_hp_bar(x, y, current_hp, max_hp):
    bar_width = 100
    bar_height = 10
    ratio = current_hp / max_hp
    if ratio < 0: ratio = 0
    if ratio > 1: ratio = 1
    color = HP_GREEN if ratio > 0.3 else HP_RED
    pygame.draw.rect(screen, (100, 100, 100), (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, color, (x, y, bar_width * ratio, bar_height))
    pygame.draw.rect(screen, BORDER_COLOR, (x, y, bar_width, bar_height), 2)

# --- Main Loop ---
while True:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if battle_state == "menu":
                if event.key == pygame.K_LEFT:
                    menu.move(-1)
                if event.key == pygame.K_RIGHT:
                    menu.move(1)
                if event.key == pygame.K_RETURN:
                    selected = menu.get_selected()
                    if selected == "FIGHT":
                        battle_text.reset("Pirate Flames used Petal Strike!")
                        player_sprite.start_attack_anim()
                        battle_state = "player_attack"
                    elif selected == "RUN":
                        battle_text.reset("Got away safely!")
                        battle_state = "end"

    # --- Update ---
    player_sprite.update()
    enemy_sprite.update()
    battle_text.update()

    if battle_text.done:
        if battle_state == "intro":
            battle_text.reset("What will Pirate Flames do?")
            battle_state = "menu"
        elif battle_state == "player_attack":
            enemy_health -= 30
            if enemy_health <= 0:
                battle_text.reset("Enemy fainted!")
                battle_state = "end"
            else:
                battle_text.reset("Corrupted Bowser attacks!")
                enemy_sprite.start_attack_anim()
                battle_state = "enemy_attack"
        elif battle_state == "enemy_attack":
            player_health -= 20
            if player_health <= 0:
                battle_text.reset("Pirate Flames fainted!")
                battle_state = "end"
            else:
                battle_text.reset("What will Pirate Flames do?")
                battle_state = "menu"

    # --- Draw ---
    screen.fill(SKY_COLOR)
    pygame.draw.rect(screen, GROUND_COLOR, (0, HEIGHT//2, WIDTH, HEIGHT//2))

    enemy_sprite.draw(screen)
    player_sprite.draw(screen)

    draw_hp_bar(WIDTH-250, 60, enemy_health, max_health)
    draw_hp_bar(100, HEIGHT//2 + 60, player_health, max_health)

    pygame.draw.rect(screen, TEXTBOX_COLOR, (0, HEIGHT-150, WIDTH, 150))
    pygame.draw.rect(screen, BORDER_COLOR, (0, HEIGHT-150, WIDTH, 150), 5)

    battle_text.draw(screen)

    if battle_state == "menu":
        menu.draw(screen)

    pygame.display.flip()
