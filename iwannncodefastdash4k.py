import pygame
import json
import os
import sys
import random
import numpy as np
import sounddevice as sd

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
BLUE = (0, 191, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 215, 0)
PURPLE = (138, 43, 226)
GREEN = (0, 255, 0)
FONT = pygame.font.Font(None, 36)
TITLE_FONT = pygame.font.Font(None, 72)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash Clone")

# Ensure directories exist
os.makedirs("levels/campaigns", exist_ok=True)
os.makedirs("emodpacks", exist_ok=True)
os.makedirs("levels", exist_ok=True)

# Sound Functions
def generate_sound(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    return wave

def play_sound(frequency, duration):
    sound = generate_sound(frequency, duration)
    sd.play(sound, samplerate=44100)
    sd.wait()

# Button Class
class Button:
    def __init__(self, text, pos, font, width=200, height=50, bg_color=GRAY, text_color=WHITE):
        self.text = text
        self.pos = pos
        self.font = font
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.text_color = text_color
        self.rect = pygame.Rect(pos[0], pos[1], width, height)

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Border
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# Main Menu Function
def main_menu(screen):
    play_button = Button("Play Game", (WIDTH // 2 - 100, 200), FONT)
    edit_button = Button("Edit Level", (WIDTH // 2 - 100, 300), FONT)
    load_campaign_button = Button("Load Campaign", (WIDTH // 2 - 100, 400), FONT)
    load_emodpack_button = Button("Load Emodpack", (WIDTH // 2 - 100, 500), FONT)
    quit_button = Button("Quit", (WIDTH // 2 - 100, 600), FONT)

    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if play_button.is_clicked(event):
                select_level(screen)
            if edit_button.is_clicked(event):
                level_editor(screen)
            if load_campaign_button.is_clicked(event):
                select_campaign(screen)
            if load_emodpack_button.is_clicked(event):
                select_emodpack(screen)
            if quit_button.is_clicked(event):
                pygame.quit()
                sys.exit()

        # Draw Buttons
        play_button.draw(screen)
        edit_button.draw(screen)
        load_campaign_button.draw(screen)
        load_emodpack_button.draw(screen)
        quit_button.draw(screen)

        # Draw Title
        title_text = TITLE_FONT.render("Geometry Dash Clone", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH//2, 100))
        screen.blit(title_text, title_rect)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Select Level Function (for playing single levels)
def select_level(screen):
    back_button = Button("Back", (50, 50), FONT, width=100, height=40, bg_color=GRAY)
    # List available levels
    level_files = [f for f in os.listdir("levels") if f.endswith(".json") and not os.path.isdir(os.path.join("levels", f))]
    level_buttons = []
    for idx, level_file in enumerate(level_files):
        btn = Button(level_file.replace(".json", ""), (WIDTH//2 - 100, 150 + idx * 60), FONT)
        level_buttons.append(btn)

    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if back_button.is_clicked(event):
                return
            for btn in level_buttons:
                if btn.is_clicked(event):
                    load_level(screen, os.path.join("levels", btn.text + ".json"))
                    return

        # Draw Buttons
        back_button.draw(screen)
        for btn in level_buttons:
            btn.draw(screen)

        # Instructions
        instructions = [
            "Select a Level to Play",
            "Click on the level name to start"
        ]
        for i, instr in enumerate(instructions):
            text = FONT.render(instr, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 50 + i * 30))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Select Campaign Function
def select_campaign(screen):
    back_button = Button("Back", (50, 50), FONT, width=100, height=40, bg_color=GRAY)
    # List available campaigns
    campaign_dirs = [d for d in os.listdir("levels/campaigns") if os.path.isdir(os.path.join("levels/campaigns", d))]
    campaign_buttons = []
    for idx, campaign_dir in enumerate(campaign_dirs):
        btn = Button(campaign_dir, (WIDTH//2 - 100, 150 + idx * 60), FONT)
        campaign_buttons.append(btn)

    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if back_button.is_clicked(event):
                return
            for btn in campaign_buttons:
                if btn.is_clicked(event):
                    load_campaign(screen, os.path.join("levels/campaigns", btn.text))
                    return

        # Draw Buttons
        back_button.draw(screen)
        for btn in campaign_buttons:
            btn.draw(screen)

        # Instructions
        instructions = [
            "Select a Campaign to Play",
            "Click on the campaign name to start"
        ]
        for i, instr in enumerate(instructions):
            text = FONT.render(instr, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 50 + i * 30))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Select Emodpack Function
def select_emodpack(screen):
    global current_emodpack
    back_button = Button("Back", (50, 50), FONT, width=100, height=40, bg_color=GRAY)
    # List available emodpacks
    emodpack_dirs = [d for d in os.listdir("emodpacks") if os.path.isdir(os.path.join("emodpacks", d))]
    emodpack_buttons = []
    for idx, pack_dir in enumerate(emodpack_dirs):
        btn = Button(pack_dir, (WIDTH//2 - 100, 150 + idx * 60), FONT)
        emodpack_buttons.append(btn)

    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if back_button.is_clicked(event):
                return
            for btn in emodpack_buttons:
                if btn.is_clicked(event):
                    current_emodpack = btn.text
                    print(f"Emodpack '{current_emodpack}' loaded.")
                    # Emodpacks can change colors or other properties as needed
                    # For simplicity, this example changes object colors based on emodpack
                    return

        # Draw Buttons
        back_button.draw(screen)
        for btn in emodpack_buttons:
            btn.draw(screen)

        # Instructions
        instructions = [
            "Select an Emodpack to Load",
            "Click on the emodpack name to apply"
        ]
        for i, instr in enumerate(instructions):
            text = FONT.render(instr, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 50 + i * 30))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Load a single level
def load_level(screen, level_path):
    try:
        with open(level_path, 'r') as f:
            level_data = json.load(f)
    except Exception as e:
        print(f"Error loading level: {e}")
        return

    # Extract objects
    objects = level_data.get("objects", [])

    # Initialize player
    player_size = 40
    player_x = 100
    player_y_start = HEIGHT - player_size - 60
    player_y = player_y_start
    player_y_velocity = 0
    gravity = 0.8
    flipped_gravity = -0.8
    current_gravity = gravity
    is_flipped = False
    player_rotation = 0

    # Game Loop
    running = True
    score = 0
    scroll_offset = 0
    dash_timer = 0

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if player_y == player_y_start or player_y == 0:
                        player_y_velocity = -15 if not is_flipped else 15
                        play_sound(440, 0.1)

        # Auto-scroll
        scroll_speed = 5
        if dash_timer > 0:
            scroll_speed *= 2
            dash_timer -= 1
        scroll_offset += scroll_speed

        # Apply gravity
        player_y_velocity += current_gravity
        player_y += player_y_velocity

        # Collision with ground or ceiling
        if not is_flipped:
            if player_y >= HEIGHT - player_size - 60:
                player_y = HEIGHT - player_size - 60
                player_y_velocity = 0
        else:
            if player_y <= 0:
                player_y = 0
                player_y_velocity = 0

        # Player rectangle
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

        # Draw objects and handle collisions
        for obj in objects.copy():
            obj_x = obj['x'] - scroll_offset
            obj_y = obj['y']
            obj_type = obj['type']
            obj_rect = pygame.Rect(obj_x, obj_y, 40, 40)

            # Draw object based on type
            if obj_type == 'block':
                pygame.draw.rect(screen, WHITE, obj_rect)
            elif obj_type == 'spike':
                points = [(obj_x, obj_y + 40), (obj_x + 20, obj_y), (obj_x + 40, obj_y + 40)]
                pygame.draw.polygon(screen, RED, points)
            elif obj_type == 'gravity_portal':
                pygame.draw.circle(screen, PURPLE, obj_rect.center, 20)
            elif obj_type == 'dash_orb':
                pygame.draw.circle(screen, YELLOW, obj_rect.center, 10)

            # Collision Detection
            if player_rect.colliderect(obj_rect):
                if obj_type == 'spike':
                    print(f"Game Over! Final Score: {score}")
                    play_sound(500, 0.2)
                    return
                elif obj_type == 'gravity_portal':
                    is_flipped = not is_flipped
                    current_gravity = flipped_gravity if is_flipped else gravity
                    player_y_velocity = 0
                elif obj_type == 'dash_orb':
                    dash_timer = 30
                    play_sound(880, 0.1)
                    objects.remove(obj)

        # Rotate player
        player_rotation = (player_rotation + scroll_speed) % 360
        rotated_player = pygame.transform.rotate(pygame.Surface((player_size, player_size)), player_rotation)
        rotated_player.fill(BLUE)
        rotated_rect = rotated_player.get_rect(center=player_rect.center)
        screen.blit(rotated_player, rotated_rect.topleft)

        # Update score
        score += 1
        score_text = FONT.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Load Campaign Function
def load_campaign(screen, campaign_path):
    # List all level JSONs in campaign
    level_files = [f for f in os.listdir(campaign_path) if f.endswith(".json")]
    level_files.sort()  # Ensure order

    for level_file in level_files:
        level_path = os.path.join(campaign_path, level_file)
        load_level(screen, level_path)

    print("Campaign Completed!")
    play_sound(600, 0.5)

# Level Editor Function
def level_editor(screen):
    back_button = Button("Back to Menu", (50, 50), FONT, width=200, height=50, bg_color=GRAY)
    current_object = 'block'
    editor_grid_size = 40
    editor_scroll_x = 0
    dragging = False
    selected_object = None
    undo_stack = []
    redo_stack = []
    level = []

    # Load existing level or start fresh
    def load_existing_level():
        nonlocal level
        # For simplicity, start with an empty level or load a default
        level = []

    load_existing_level()

    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if back_button.is_clicked(event):
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                x = (event.pos[0] + editor_scroll_x) // editor_grid_size * editor_grid_size
                y = event.pos[1] // editor_grid_size * editor_grid_size

                if event.button == 1:  # Left click to place/remove
                    for obj in level:
                        if obj['x'] == x and obj['y'] == y:
                            undo_stack.append({'action': 'remove', 'object': obj.copy()})
                            level.remove(obj)
                            break
                    else:
                        new_obj = {'type': current_object, 'x': x, 'y': y, 'color': get_object_color(current_object)}
                        undo_stack.append({'action': 'add', 'object': new_obj.copy()})
                        level.append(new_obj)

                elif event.button == 3:  # Right click to select/move
                    for obj in level:
                        if obj['x'] == x and obj['y'] == y:
                            selected_object = obj
                            dragging = True
                            break

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    dragging = False
                    selected_object = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_object = 'block'
                elif event.key == pygame.K_2:
                    current_object = 'spike'
                elif event.key == pygame.K_3:
                    current_object = 'gravity_portal'
                elif event.key == pygame.K_4:
                    current_object = 'dash_orb'
                elif event.key == pygame.K_s:
                    save_level_editor(level, screen)
                elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    undo_edit(undo_stack, redo_stack, level)
                elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    redo_edit(undo_stack, redo_stack, level)
                elif event.key == pygame.K_ESCAPE:
                    return

        # Handle dragging
        if dragging and selected_object:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            selected_object['x'] = (mouse_x + editor_scroll_x) // editor_grid_size * editor_grid_size
            selected_object['y'] = mouse_y // editor_grid_size * editor_grid_size

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            editor_scroll_x = max(0, editor_scroll_x - 5)
        if keys[pygame.K_RIGHT]:
            editor_scroll_x += 5

        # Draw grid
        for x in range(0, WIDTH + editor_grid_size, editor_grid_size):
            pygame.draw.line(screen, GRAY, (x - editor_scroll_x % editor_grid_size, 0),
                             (x - editor_scroll_x % editor_grid_size, HEIGHT))
        for y in range(0, HEIGHT, editor_grid_size):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

        # Draw objects
        for obj in level:
            obj_x = obj['x'] - editor_scroll_x
            obj_y = obj['y']
            obj_type = obj['type']
            color = obj.get('color', WHITE)
            if obj_type == 'block':
                pygame.draw.rect(screen, color, (obj_x, obj_y, 40, 40))
            elif obj_type == 'spike':
                points = [(obj_x, obj_y + 40), (obj_x + 20, obj_y), (obj_x + 40, obj_y + 40)]
                pygame.draw.polygon(screen, color, points)
            elif obj_type == 'gravity_portal':
                pygame.draw.circle(screen, color, (obj_x + 20, obj_y + 20), 20)
            elif obj_type == 'dash_orb':
                pygame.draw.circle(screen, color, (obj_x + 20, obj_y + 20), 10)

        # Draw current object at mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = mouse_x // editor_grid_size * editor_grid_size
        grid_y = mouse_y // editor_grid_size * editor_grid_size
        color = get_object_color(current_object)
        if current_object == 'block':
            pygame.draw.rect(screen, color, (grid_x, grid_y, 40, 40))
        elif current_object == 'spike':
            points = [(grid_x, grid_y + 40), (grid_x + 20, grid_y), (grid_x + 40, grid_y + 40)]
            pygame.draw.polygon(screen, color, points)
        elif current_object == 'gravity_portal':
            pygame.draw.circle(screen, color, (grid_x + 20, grid_y + 20), 20)
        elif current_object == 'dash_orb':
            pygame.draw.circle(screen, color, (grid_x + 20, grid_y + 20), 10)

        # Draw Buttons
        back_button.draw(screen)

        # Draw UI instructions
        instructions = [
            "Left click: Place/Remove object",
            "Right click: Select/Move object",
            "1: Select Block",
            "2: Select Spike",
            "3: Select Gravity Portal",
            "4: Select Dash Orb",
            "S: Save Level",
            "CTRL+Z: Undo",
            "CTRL+Y: Redo",
            "Arrow keys: Scroll",
            "ESC: Exit Editor"
        ]
        for i, instruction in enumerate(instructions):
            text = FONT.render(instruction, True, WHITE)
            screen.blit(text, (10, 10 + i * 30))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Save Level Editor Function
def save_level_editor(level, screen):
    def get_metadata(screen):
        """
        Simple metadata input dialog.
        """
        metadata = {
            "level_name": "Untitled_Level",
            "author": "Unknown",
            "description": ""
        }

        input_active = False
        input_boxes = {
            'level_name': pygame.Rect(200, 150, 400, 40),
            'author': pygame.Rect(200, 250, 400, 40),
            'description': pygame.Rect(200, 350, 400, 40)
        }
        colors = {'inactive': GRAY, 'active': WHITE}
        active_field = 'level_name'
        text = {'level_name': '', 'author': '', 'description': ''}
        color = {'level_name': colors['inactive'], 'author': colors['inactive'], 'description': colors['inactive']}
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for field in input_boxes:
                        if input_boxes[field].collidepoint(event.pos):
                            active_field = field
                            color[field] = colors['active']
                        else:
                            color[field] = colors['inactive']
                if event.type == pygame.KEYDOWN:
                    if input_active:
                        if event.key == pygame.K_RETURN:
                            if active_field == 'level_name':
                                active_field = 'author'
                                color['level_name'] = colors['inactive']
                                color['author'] = colors['active']
                            elif active_field == 'author':
                                active_field = 'description'
                                color['author'] = colors['inactive']
                                color['description'] = colors['active']
                            elif active_field == 'description':
                                metadata["description"] = text['description']
                                return metadata
                            text[active_field] = ''
                        elif event.key == pygame.K_BACKSPACE:
                            text[active_field] = text[active_field][:-1]
                        else:
                            text[active_field] += event.unicode

            screen.fill(BLACK)
            # Instructions
            instructions = [
                "Enter Level Metadata",
                "Press ENTER to switch fields",
                "After description, press ENTER to save"
            ]
            for i, instr in enumerate(instructions):
                rendered_text = FONT.render(instr, True, WHITE)
                screen.blit(rendered_text, (WIDTH//2 - rendered_text.get_width()//2, 50 + i * 30))

            # Render input boxes and labels
            for field, box in input_boxes.items():
                pygame.draw.rect(screen, color[field], box, 2)
                if field == 'level_name':
                    label = "Level Name:"
                elif field == 'author':
                    label = "Author:"
                elif field == 'description':
                    label = "Description:"
                label_text = FONT.render(label, True, WHITE)
                screen.blit(label_text, (box.x - 150, box.y + 5))
                rendered_text = FONT.render(text[field], True, WHITE)
                screen.blit(rendered_text, (box.x + 5, box.y + 5))

            pygame.display.flip()
            clock.tick(30)

    # Prompt metadata
    metadata = get_metadata(screen)

    # Structure JSON
    level_data = {
        "metadata": metadata,
        "objects": level
    }

    # Save to file
    filename = metadata["level_name"].replace(" ", "_") + ".json"
    filepath = os.path.join("levels", filename)
    with open(filepath, 'w') as f:
        json.dump(level_data, f, indent=4)

    print(f"Level saved as {filepath}")
    play_sound(300, 0.2)

# Undo Edit Function
def undo_edit(undo_stack, redo_stack, level):
    if undo_stack:
        last_action = undo_stack.pop()
        redo_stack.append(last_action)
        if last_action['action'] == 'add':
            if last_action['object'] in level:
                level.remove(last_action['object'])
        elif last_action['action'] == 'remove':
            level.append(last_action['object'])

# Redo Edit Function
def redo_edit(undo_stack, redo_stack, level):
    if redo_stack:
        last_action = redo_stack.pop()
        undo_stack.append(last_action)
        if last_action['action'] == 'add':
            level.append(last_action['object'])
        elif last_action['action'] == 'remove':
            if last_action['object'] in level:
                level.remove(last_action['object'])

# Load Campaign Function
def load_campaign(screen, campaign_path):
    # List all level JSONs in campaign
    level_files = [f for f in os.listdir(campaign_path) if f.endswith(".json")]
    level_files.sort()  # Ensure order

    for level_file in level_files:
        level_path = os.path.join(campaign_path, level_file)
        load_level(screen, level_path)

    print("Campaign Completed!")
    play_sound(600, 0.5)

# Get Object Color Function
def get_object_color(obj_type):
    """
    Assign colors based on object type for enhanced JSON output.
    """
    colors = {
        'block': WHITE,
        'spike': RED,
        'gravity_portal': PURPLE,
        'dash_orb': YELLOW
    }
    return colors.get(obj_type, WHITE)

# Logo Screen Function
def logo_screen(screen):
    logo_text = TITLE_FONT.render("Geometry Dash Clone", True, WHITE)
    logo_rect = logo_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.fill(BLACK)
    screen.blit(logo_text, logo_rect)
    pygame.display.flip()
    pygame.time.delay(2000)  # Display logo for 2 seconds

# Main Function
def main():
    logo_screen(screen)
    main_menu(screen)

if __name__ == "__main__":
    main()
