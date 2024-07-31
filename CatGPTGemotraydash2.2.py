import pygame
import random
import json
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash 2.2 (No Media)")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Fonts
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)

# Game modes
CUBE = 0
SHIP = 1
BALL = 2
UFO = 3
WAVE = 4

# Player properties
player_size = 40
player_x = 100
player_y = HEIGHT - player_size - 60
player_y_velocity = 0
jump_height = -15
gravity = 0.8

# Ground properties
ground_height = 60

# Game variables
score = 0
game_mode = CUBE
practice_mode = False

# Level editor variables
editor_grid_size = 40
editor_scroll_x = 0
current_object = 'block'

# Button class for menu
class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Create menu buttons
play_button = Button(300, 200, 200, 50, "Play", BLUE, WHITE)
edit_button = Button(300, 300, 200, 50, "Level Editor", GREEN, WHITE)
quit_button = Button(300, 400, 200, 50, "Quit", RED, WHITE)

# Level structure
level = []

def save_level(name):
    with open(f"{name}.json", "w") as f:
        json.dump(level, f)

def load_level(name):
    global level
    try:
        with open(f"{name}.json", "r") as f:
            level = json.load(f)
    except FileNotFoundError:
        level = []

def draw_player(x, y):
    if game_mode == CUBE:
        pygame.draw.rect(screen, RED, (x - editor_scroll_x, y, player_size, player_size))
    elif game_mode == SHIP:
        pygame.draw.polygon(screen, BLUE, [
            (x - editor_scroll_x, y),
            (x - editor_scroll_x + player_size, y + player_size//2),
            (x - editor_scroll_x, y + player_size)
        ])
    elif game_mode == BALL:
        pygame.draw.circle(screen, GREEN, (x - editor_scroll_x + player_size//2, y + player_size//2), player_size//2)
    elif game_mode == UFO:
        pygame.draw.ellipse(screen, YELLOW, (x - editor_scroll_x, y, player_size, player_size//2))
    elif game_mode == WAVE:
        pygame.draw.polygon(screen, PURPLE, [
            (x - editor_scroll_x, y + player_size//2),
            (x - editor_scroll_x + player_size//2, y),
            (x - editor_scroll_x + player_size, y + player_size//2),
            (x - editor_scroll_x + player_size//2, y + player_size)
        ])

def draw_level():
    for obj in level:
        if obj['type'] == 'block':
            pygame.draw.rect(screen, WHITE, (obj['x'] - editor_scroll_x, obj['y'], editor_grid_size, editor_grid_size))
        elif obj['type'] == 'spike':
            pygame.draw.polygon(screen, WHITE, [
                (obj['x'] - editor_scroll_x, obj['y'] + editor_grid_size),
                (obj['x'] - editor_scroll_x + editor_grid_size//2, obj['y']),
                (obj['x'] - editor_scroll_x + editor_grid_size, obj['y'] + editor_grid_size)
            ])
        elif obj['type'] == 'orb':
            pygame.draw.circle(screen, YELLOW, (obj['x'] - editor_scroll_x + editor_grid_size//2, obj['y'] + editor_grid_size//2), editor_grid_size//2)
        elif obj['type'] == 'portal':
            pygame.draw.rect(screen, PURPLE, (obj['x'] - editor_scroll_x, obj['y'], editor_grid_size, editor_grid_size*2))

def draw_ground():
    pygame.draw.rect(screen, WHITE, (0, HEIGHT - ground_height, WIDTH, ground_height))

def display_score():
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def display_mode():
    mode_text = font.render(f"{game_mode_to_string(game_mode)} MODE", True, WHITE)
    screen.blit(mode_text, (WIDTH - mode_text.get_width() - 10, 10))

def display_practice():
    if practice_mode:
        practice_text = font.render("PRACTICE MODE", True, GREEN)
        screen.blit(practice_text, (WIDTH // 2 - practice_text.get_width() // 2, 10))

def game_mode_to_string(mode):
    return {CUBE: "CUBE", SHIP: "SHIP", BALL: "BALL", UFO: "UFO", WAVE: "WAVE"}[mode]

def game_loop():
    global player_y, player_y_velocity, score, game_mode, practice_mode, editor_scroll_x

    player_y = HEIGHT - player_size - 60
    player_y_velocity = 0
    score = 0
    editor_scroll_x = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_mode in [CUBE, SHIP, UFO] and player_y == HEIGHT - player_size - ground_height:
                        player_y_velocity = jump_height
                    elif game_mode == BALL:
                        player_y_velocity *= -1
                elif event.key == pygame.K_m:
                    game_mode = (game_mode + 1) % 5
                elif event.key == pygame.K_p:
                    practice_mode = not practice_mode
                elif event.key == pygame.K_ESCAPE:
                    return True

        # Update player position
        if game_mode in [CUBE, BALL, UFO]:
            player_y_velocity += gravity
        elif game_mode == SHIP:
            player_y_velocity += gravity / 4
        elif game_mode == WAVE:
            player_y_velocity = math.sin(editor_scroll_x * 0.1) * 5

        player_y += player_y_velocity

        if player_y > HEIGHT - player_size - ground_height:
            player_y = HEIGHT - player_size - ground_height
            player_y_velocity = 0
        elif player_y < 0:
            player_y = 0
            player_y_velocity = 0

        # Move level (simulating player movement)
        editor_scroll_x += 5

        # Check for collision
        for obj in level:
            if (player_x < obj['x'] - editor_scroll_x + 40 and
                player_x + player_size > obj['x'] - editor_scroll_x and
                player_y < obj['y'] + 40 and
                player_y + player_size > obj['y']):
                if obj['type'] == 'block' or obj['type'] == 'spike':
                    if not practice_mode:
                        print(f"Game Over! Final Score: {score}")
                        return True
                    else:
                        player_y = HEIGHT - player_size - ground_height
                        player_y_velocity = 0
                elif obj['type'] == 'orb':
                    player_y_velocity = jump_height
                elif obj['type'] == 'portal':
                    game_mode = (game_mode + 1) % 5

        # Increase score
        score += 1

        # Clear the screen
        screen.fill(BLACK)

        # Draw game elements
        draw_ground()
        draw_level()
        draw_player(player_x, player_y)
        display_score()
        display_mode()
        display_practice()

        # Update the display
        pygame.display.flip()

        # Control the frame rate
        pygame.time.Clock().tick(60)

def editor_loop():
    global current_object, editor_scroll_x

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x = (event.pos[0] + editor_scroll_x) // editor_grid_size * editor_grid_size
                    y = event.pos[1] // editor_grid_size * editor_grid_size
                    level.append({'type': current_object, 'x': x, 'y': y})
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_object = 'block'
                elif event.key == pygame.K_2:
                    current_object = 'spike'
                elif event.key == pygame.K_3:
                    current_object = 'orb'
                elif event.key == pygame.K_4:
                    current_object = 'portal'
                elif event.key == pygame.K_s:
                    save_level("custom_level")
                elif event.key == pygame.K_l:
                    load_level("custom_level")
                elif event.key == pygame.K_ESCAPE:
                    return True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            editor_scroll_x = max(0, editor_scroll_x - 5)
        if keys[pygame.K_RIGHT]:
            editor_scroll_x += 5

        # Clear the screen
        screen.fill(BLACK)

        # Draw grid
        for x in range(0, WIDTH + editor_grid_size, editor_grid_size):
            pygame.draw.line(screen, GRAY, (x - editor_scroll_x % editor_grid_size, 0),
                             (x - editor_scroll_x % editor_grid_size, HEIGHT))
        for y in range(0, HEIGHT, editor_grid_size):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

        # Draw level
        draw_level()

        # Draw current object at mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = mouse_x // editor_grid_size * editor_grid_size
        grid_y = mouse_y // editor_grid_size * editor_grid_size
        if current_object == 'block':
            pygame.draw.rect(screen, WHITE, (grid_x, grid_y, editor_grid_size, editor_grid_size))
        elif current_object == 'spike':
            pygame.draw.polygon(screen, WHITE, [
                (grid_x, grid_y + editor_grid_size),
                (grid_x + editor_grid_size//2, grid_y),
                (grid_x + editor_grid_size, grid_y + editor_grid_size)
            ])
        elif current_object == 'orb':
            pygame.draw.circle(screen, YELLOW, (grid_x + editor_grid_size//2, grid_y + editor_grid_size//2), editor_grid_size//2)
        elif current_object == 'portal':
            pygame.draw.rect(screen, PURPLE, (grid_x, grid_y, editor_grid_size, editor_grid_size*2))

        # Display instructions
        instructions = [
            "Left click: Place object",
            "1: Select block",
            "2: Select spike",
            "3: Select orb",
            "4: Select portal",
            "S: Save level",
            "L: Load level",
            "Arrow keys: Scroll",
            "ESC: Exit editor"
        ]
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, WHITE)
            screen.blit(text, (10, 10 + i * 30))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

def main_menu():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if play_button.is_clicked(event.pos):
                        if game_loop():
                            continue
                        else:
                            return False
                    elif edit_button.is_clicked(event.pos):
                        if editor_loop():
                            continue
                        else:
                            return False
                    elif quit_button.is_clicked(event.pos):
                        return False

        screen.fill(BLACK)

        title = title_font.render("Geometry Dash 2.2 [Topcat] 20XX Modding edition PY 1.0 a", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

        play_button.draw(screen)
        edit_button.draw(screen)
        quit_button.draw(screen)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

main_menu()
pygame.quit()
