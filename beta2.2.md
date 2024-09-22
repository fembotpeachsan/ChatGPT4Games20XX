import pygame
import json
import os

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

# Load images (placeholder rectangles)
BLOCK_IMG = pygame.Surface((40, 40))
BLOCK_IMG.fill(WHITE)
SPIKE_IMG = pygame.Surface((40, 40))
pygame.draw.polygon(SPIKE_IMG, RED, [(0, 40), (20, 0), (40, 40)])

# Level data (two tech demo levels)
LEVELS = {
    "1-1": [
        {"type": "block", "x": 200, "y": 400},
        {"type": "spike", "x": 350, "y": 460},
        {"type": "block", "x": 400, "y": 400}
    ],
    "1-2": [
        {"type": "block", "x": 200, "y": 400},
        {"type": "spike", "x": 350, "y": 460},
        {"type": "block", "x": 450, "y": 400},
        {"type": "block", "x": 600, "y": 400},
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
    on_ground = True
    scroll_offset = 0
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and on_ground:
                    player_y_velocity = JUMP_HEIGHT
                    on_ground = False

        # Update player position
        player_y_velocity += GRAVITY
        player_y += player_y_velocity

        # Check ground collision
        if player_y >= HEIGHT - PLAYER_SIZE - GROUND_HEIGHT:
            player_y = HEIGHT - PLAYER_SIZE - GROUND_HEIGHT
            player_y_velocity = 0
            on_ground = True

        # Collision with obstacles
        player_rect = pygame.Rect(PLAYER_X, player_y, PLAYER_SIZE, PLAYER_SIZE)
        for obj in level:
            obj_rect = pygame.Rect(obj['x'] - scroll_offset, obj['y'], 40, 40)
            if player_rect.colliderect(obj_rect):
                if obj['type'] == 'spike':
                    print(f"Game Over! Final Score: {score}")
                    return True

        # Increase score and scroll
        score += 1
        scroll_offset += scroll_speed

        # Draw everything
        screen.fill(BLACK)
        draw_level(scroll_offset)
        draw_player(PLAYER_X, player_y)

        # Display score
        score_text = FONT.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Check for level completion
        if score >= 200:
            print(f"Level Complete!")
            return True

        pygame.display.flip()
        pygame.time.Clock().tick(60)

def save_level(filename):
    with open(filename, 'w') as f:
        json.dump(level, f)

def load_level_from_file(filename):
    global level
    with open(filename, 'r') as f:
        level = json.load(f)

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
                x = (event.pos[0] + editor_scroll_x) // editor_grid_size * editor_grid_size
                y = event.pos[1] // editor_grid_size * editor_grid_size
                if event.button == 1:  # Left click: Place/Remove
                    level[:] = [obj for obj in level if not (obj['x'] == x and obj['y'] == y)]
                    level.append({'type': current_object, 'x': x, 'y': y})
                elif event.button == 3:  # Right click: Remove
                    level[:] = [obj for obj in level if not (obj['x'] == x and obj['y'] == y)]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_object = 'block'
                elif event.key == pygame.K_2:
                    current_object = 'spike'
                elif event.key == pygame.K_s:
                    save_level("custom_level.json")
                elif event.key == pygame.K_l:
                    load_level_from_file("custom_level.json")
                elif event.key == pygame.K_ESCAPE:
                    return True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            editor_scroll_x = max(0, editor_scroll_x - 5)
        if keys[pygame.K_RIGHT]:
            editor_scroll_x += 5

        screen.fill(BLACK)

        # Draw grid
        for x in range(0, WIDTH + editor_grid_size, editor_grid_size):
            pygame.draw.line(screen, GRAY, (x - editor_scroll_x % editor_grid_size, 0),
                             (x - editor_scroll_x % editor_grid_size, HEIGHT))
        for y in range(0, HEIGHT, editor_grid_size):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

        draw_level(editor_scroll_x)

        # Draw current object at mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = mouse_x // editor_grid_size * editor_grid_size
        grid_y = mouse_y // editor_grid_size * editor_grid_size
        if current_object == 'block':
            screen.blit(BLOCK_IMG, (grid_x, grid_y))
        elif current_object == 'spike':
            screen.blit(SPIKE_IMG, (grid_x, grid_y))

        # Display instructions
        instructions = [
            "Left click: Place/Remove object",
            "Right click: Remove object",
            "1: Select block",
            "2: Select spike",
            "S: Save level",
            "L: Load level",
            "Arrow keys: Scroll",
            "ESC: Exit editor"
        ]
        for i, instruction in enumerate(instructions):
            text = FONT.render(instruction, True, WHITE)
            screen.blit(text, (10, 10 + i * 30))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

def level_select():
    level_files = [f for f in os.listdir("levels") if f.endswith(".json")]
    buttons = []
    for i, filename in enumerate(level_files):
        button_text = filename[:-5]
        button_y = 150 + i * 50
        buttons.append(Button(button_text, (WIDTH // 2 - 100, button_y), FONT))

    back_button = Button("Back", (WIDTH // 2 - 50, HEIGHT - 50), FONT)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, button in enumerate(buttons):
                        if button.is_clicked(event.pos):
                            load_level_from_file(os.path.join("levels", level_files[i]))
                            if game_loop():
                                break
                    if back_button.is_clicked(event.pos):
                        return True

        screen.fill(BLACK)

        title = TITLE_FONT.render("Select Level", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        for button in buttons:
            screen.blit(button.surface, (button.x, button.y))
        screen.blit(back_button.surface, (back_button.x, back_button.y))

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
                        if level_select():
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
