import pygame
import json
import os
import random
import numpy as np
import sounddevice as sd

# Initialize Pygame
pygame.init()

# Constants (colors, fonts, etc.)
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
FONT = pygame.font.Font(None, 36)
TITLE_FONT = pygame.font.Font(None, 72)

# Player properties
PLAYER_SIZE = 40
PLAYER_X = 100
PLAYER_Y_START = HEIGHT - PLAYER_SIZE - 60
JUMP_HEIGHT = -15
GRAVITY = 0.8

# Ground properties
GROUND_HEIGHT = 60

# Game variables
score = 0
level = []
scroll_speed = 5
current_level_index = 0  # Keep track of the current level

# Load images (placeholder rectangles)
BLOCK_IMG = pygame.Surface((40, 40))
BLOCK_IMG.fill(WHITE)
SPIKE_IMG = pygame.Surface((40, 40))
pygame.draw.polygon(SPIKE_IMG, RED, [(0, 40), (20, 0), (40, 40)])

# Level data (including Stereo Madness and a custom tech demo)
LEVELS = {
    "1-1": [  # Stereo Madness (simplified)
        {"type": "block", "x": 200, "y": 400},
        {"type": "block", "x": 240, "y": 400},
        {"type": "block", "x": 280, "y": 400},
        {"type": "spike", "x": 320, "y": 460},
        {"type": "block", "x": 360, "y": 400},
        {"type": "block", "x": 400, "y": 400},
        {"type": "spike", "x": 440, "y": 460},
        # Add more blocks and spikes as needed for Stereo Madness
    ],
    "1-2": [  # Custom Tech Demo
        {"type": "block", "x": 100, "y": 400},
        {"type": "spike", "x": 250, "y": 460},
        {"type": "block", "x": 300, "y": 400},
        {"type": "block", "x": 500, "y": 400},
        {"type": "spike", "x": 650, "y": 460},
    ],
}

# --- Functions ---

def load_level(level_data):
    global level
    level = level_data

def draw_player(x, y):
    pygame.draw.rect(screen, BLUE, (x, y, PLAYER_SIZE, PLAYER_SIZE))

def draw_level(scroll_offset):
    for obj in level:
        if obj['type'] == 'block':
            screen.blit(BLOCK_IMG, (obj['x'] - scroll_offset, obj['y']))
        elif obj['type'] == 'spike':
            screen.blit(SPIKE_IMG, (obj['x'] - scroll_offset, obj['y']))

def game_loop():
    global score
    player_y = PLAYER_Y_START
    player_y_velocity = 0
    score = 0
    on_ground = True
    scroll_offset = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and on_ground:
                    player_y_velocity = JUMP_HEIGHT
                    on_ground = False

        player_y_velocity += GRAVITY
        player_y += player_y_velocity

        if player_y >= HEIGHT - PLAYER_SIZE - GROUND_HEIGHT:
            player_y = HEIGHT - PLAYER_SIZE - GROUND_HEIGHT
            player_y_velocity = 0
            on_ground = True

        player_rect = pygame.Rect(PLAYER_X, player_y, PLAYER_SIZE, PLAYER_SIZE)
        for obj in level:
            obj_rect = pygame.Rect(obj['x'] - scroll_offset, obj['y'], 40, 40)
            if player_rect.colliderect(obj_rect) and obj['type'] == 'spike':
                print(f"Game Over! Final Score: {score}")
                return True

        score += 1
        scroll_offset += scroll_speed

        screen.fill(BLACK)
        draw_level(scroll_offset)
        draw_player(PLAYER_X, player_y)

        score_text = FONT.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if score >= 200:
            print("Level Complete!")
            return True

        pygame.display.flip()
        pygame.time.Clock().tick(60)

def editor_loop():
    global level
    current_object = 'block'
    editor_grid_size = 40
    editor_scroll_x = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x = (event.pos[0] + editor_scroll_x) // editor_grid_size * editor_grid_size
                    y = event.pos[1] // editor_grid_size * editor_grid_size
                    for obj in level:
                        if obj['x'] == x and obj['y'] == y:
                            level.remove(obj)
                            break
                    else:
                        level.append({'type': current_object, 'x': x, 'y': y})
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_object = 'block'
                elif event.key == pygame.K_2:
                    current_object = 'spike'
                elif event.key == pygame.K_s:
                    save_level("custom_level.json")

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            editor_scroll_x = max(0, editor_scroll_x - 5)
        if keys[pygame.K_RIGHT]:
            editor_scroll_x += 5

        screen.fill(BLACK)
        for x in range(0, WIDTH + editor_grid_size, editor_grid_size):
            pygame.draw.line(screen, GRAY, (x - editor_scroll_x % editor_grid_size, 0),
                             (x - editor_scroll_x % editor_grid_size, HEIGHT))
        for y in range(0, HEIGHT, editor_grid_size):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

        draw_level(editor_scroll_x)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = mouse_x // editor_grid_size * editor_grid_size
        grid_y = mouse_y // editor_grid_size * editor_grid_size
        if current_object == 'block':
            screen.blit(BLOCK_IMG, (grid_x, grid_y))
        elif current_object == 'spike':
            screen.blit(SPIKE_IMG, (grid_x, grid_y))

        instructions = [
            "Left click: Place/Remove object",
            "1: Select block",
            "2: Select spike",
            "S: Save level",
            "Arrow keys: Scroll",
            "ESC: Exit editor"
        ]
        for i, instruction in enumerate(instructions):
            text = FONT.render(instruction, True, WHITE)
            screen.blit(text, (10, 10 + i * 30))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

def main_menu():
    play_button = Button("Play Game", (WIDTH // 2 - 75, 250), FONT)
    edit_button = Button("Edit", (WIDTH // 2 - 50, 350), FONT)
    quit_button = Button("Quit", (WIDTH // 2 - 50, 450), FONT)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if play_button.is_clicked(event.pos):
                        load_level(LEVELS["1-1"])  # Load the integrated Stereo Madness level
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
        title = TITLE_FONT.render("Geometry Dash", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        screen.blit(play_button.surface, (play_button.x, play_button.y))
        screen.blit(edit_button.surface, (edit_button.x, edit_button.y))
        screen.blit(quit_button.surface, (quit_button.x, quit_button.y))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

class Button:
    def __init__(self, text, pos, font, bg=BLACK):
        self.x, self.y = pos
        self.font = font
        self.text = self.font.render(text, True, WHITE)
        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])

    def is_clicked(self, event_pos):
        return self.rect.collidepoint(event_pos)

# Create the "levels" directory if it doesn't exist
if not os.path.exists("levels"):
    os.makedirs("levels")

# Start the game
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Set up the display
main_menu()
pygame.quit()
