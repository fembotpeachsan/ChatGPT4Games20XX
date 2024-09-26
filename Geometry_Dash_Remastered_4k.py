aimport pygame
import json
import os
import time
import base64

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1280, 720  # Increased resolution for better editor space
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
BLUE = (65, 105, 225)
GREEN = (34, 139, 34)
GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)
CYAN = (0, 255, 255)
YELLOW = (255, 215, 0)
FONT = pygame.font.Font(None, 24)
TITLE_FONT = pygame.font.Font(None, 48)

# Player properties
PLAYER_SIZE = 40
PLAYER_X = 100
PLAYER_Y_START = HEIGHT - PLAYER_SIZE - 60
JUMP_HEIGHT = -15
DOUBLE_JUMP_HEIGHT = -12
JUMP_PAD_HEIGHT = -20
GRAVITY = 0.8

# Ground properties
GROUND_HEIGHT = 60

# Game variables
score = 0
level = []
scroll_speed = 5
player_jumps = 0
dash_speed_multiplier = 1
dash_duration = 0
dash_start_time = 0

# Load images (placeholder rectangles)
BLOCK_IMG = pygame.Surface((40, 40))
BLOCK_IMG.fill(WHITE)
SPIKE_IMG = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.polygon(SPIKE_IMG, RED, [(0, 40), (20, 0), (40, 40)])
MOVING_PLATFORM_IMG = pygame.Surface((80, 20))
MOVING_PLATFORM_IMG.fill(GREEN)
PORTAL_IMG = pygame.Surface((40, 40))
PORTAL_IMG.fill(YELLOW)  # Yellow portal
DASH_ORB_IMG = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.circle(DASH_ORB_IMG, CYAN, (15, 15), 15)
JUMP_PAD_IMG = pygame.Surface((40, 20), pygame.SRCALPHA)
pygame.draw.rect(JUMP_PAD_IMG, YELLOW, (0, 0, 40, 20))
pygame.draw.polygon(JUMP_PAD_IMG, RED, [(0, 20), (20, 0), (40, 20)])

# Level data
LEVELS = {
    "1-1": [
        {"type": "block", "x": 200, "y": 400},
        {"type": "block", "x": 240, "y": 400},
        {"type": "moving_platform", "x": 280, "y": 350, "direction": "horizontal", "move_range": 100},
        {"type": "spike", "x": 320, "y": 460},
        {"type": "block", "x": 360, "y": 400},
        {"type": "block", "x": 400, "y": 400},
        {"type": "spike", "x": 440, "y": 460},
        {"type": "portal", "x": 500, "y": 400},
        {"type": "dash_orb", "x": 600, "y": 500},
        {"type": "jump_pad", "x": 700, "y": 500}
    ],
}

# --- Level Sharing Functions ---

def encode_level(level_data):
    """
    Encode the level data into a Base64 string for sharing.
    """
    level_json = json.dumps(level_data)
    level_bytes = level_json.encode('utf-8')
    level_b64 = base64.urlsafe_b64encode(level_bytes).decode('utf-8')
    return level_b64

def decode_level(level_code):
    """
    Decode the Base64 string back into level data.
    """
    try:
        level_bytes = base64.urlsafe_b64decode(level_code)
        level_json = level_bytes.decode('utf-8')
        level_data = json.loads(level_json)
        return level_data
    except Exception as e:
        print(f"Error decoding level: {e}")
        return None

# --- Existing Functions ---

def load_level(level_data):
    global level
    level = level_data

def draw_player(x, y):
    pygame.draw.rect(screen, BLUE, (x, y, PLAYER_SIZE, PLAYER_SIZE))

def draw_level(scroll_offset):
    for obj in level:
        obj_x = obj['x'] - scroll_offset
        obj_y = obj['y']
        if obj['type'] == 'block':
            screen.blit(BLOCK_IMG, (obj_x, obj_y))
        elif obj['type'] == 'spike':
            screen.blit(SPIKE_IMG, (obj_x, obj_y))
        elif obj['type'] == 'moving_platform':
            # Handle moving platforms
            direction = obj.get('direction', 'horizontal')
            move_range = obj.get('move_range', 100)
            speed = obj.get('speed', 2)
            original_x = obj.get('original_x', obj['x'])
            original_y = obj.get('original_y', obj['y'])
            current_time = pygame.time.get_ticks()
            if 'start_time' not in obj:
                obj['start_time'] = current_time
            elapsed = (current_time - obj['start_time']) / 1000
            if direction == 'horizontal':
                obj_x = original_x + move_range * pygame.math.sin(elapsed * speed)
            else:
                obj_y = original_y + move_range * pygame.math.sin(elapsed * speed)
            screen.blit(MOVING_PLATFORM_IMG, (obj_x - scroll_offset, obj_y))
        elif obj['type'] == 'portal':
            screen.blit(PORTAL_IMG, (obj_x, obj_y))
        elif obj['type'] == 'dash_orb':
            screen.blit(DASH_ORB_IMG, (obj_x, obj_y))
        elif obj['type'] == 'jump_pad':
            screen.blit(JUMP_PAD_IMG, (obj_x, obj_y))

def game_loop():
    global score, player_jumps, scroll_speed, dash_speed_multiplier, dash_duration, dash_start_time
    player_y = PLAYER_Y_START
    player_y_velocity = 0
    score = 0
    on_ground = True
    scroll_offset = 0

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if on_ground:
                        player_y_velocity = JUMP_HEIGHT
                        on_ground = False
                        player_jumps = 1
                    elif player_jumps < 1:
                        player_y_velocity = DOUBLE_JUMP_HEIGHT
                        player_jumps += 1

        # Handle Dash duration
        if dash_speed_multiplier > 1:
            if current_time - dash_start_time > dash_duration:
                dash_speed_multiplier = 1

        player_y_velocity += GRAVITY
        player_y += player_y_velocity

        if player_y >= HEIGHT - PLAYER_SIZE - GROUND_HEIGHT:
            player_y = HEIGHT - PLAYER_SIZE - GROUND_HEIGHT
            player_y_velocity = 0
            on_ground = True
            player_jumps = 0

        player_rect = pygame.Rect(PLAYER_X, player_y, PLAYER_SIZE, PLAYER_SIZE)

        for obj in level:
            obj_rect = pygame.Rect(obj['x'] - scroll_offset, obj['y'], 40, 40)
            if player_rect.colliderect(obj_rect):
                if obj['type'] == 'spike':
                    print(f"Game Over! Final Score: {score}")
                    return True
                elif obj['type'] == 'portal':
                    print("Portal Activated! Level Jump!")
                    # Handle portal logic here (e.g., jump to a different part of the level)
                elif obj['type'] == 'dash_orb':
                    dash_speed_multiplier = 2  # Double the speed
                    dash_duration = 3000  # 3 seconds
                    dash_start_time = current_time
                    level.remove(obj)  # Remove the Dash Orb after collection
                elif obj['type'] == 'jump_pad':
                    player_y_velocity = JUMP_PAD_HEIGHT
                    on_ground = False
                    player_jumps = 1
                    level.remove(obj)  # Remove the Jump Pad after activation

        score += 1
        scroll_offset += scroll_speed * dash_speed_multiplier

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

# --- Enhanced Editor Loop ---

def editor_loop():
    global level
    current_object = 'block'
    editor_grid_size = 40
    editor_scroll_x = 0
    dragging = False
    selected_object = None
    undo_stack = []
    redo_stack = []
    input_mode = False
    input_text = ''
    input_prompt = ''
    show_code = False
    level_code = ''

    # Object toolbar
    toolbar_items = [
        {'type': 'block', 'icon': BLOCK_IMG},
        {'type': 'spike', 'icon': SPIKE_IMG},
        {'type': 'moving_platform', 'icon': MOVING_PLATFORM_IMG},
        {'type': 'portal', 'icon': PORTAL_IMG},
        {'type': 'dash_orb', 'icon': DASH_ORB_IMG},
        {'type': 'jump_pad', 'icon': JUMP_PAD_IMG},
    ]
    toolbar_rects = []
    for i, item in enumerate(toolbar_items):
        rect = pygame.Rect(10, 10 + i * 50, 40, 40)
        toolbar_rects.append(rect)

    running = True
    while running:
        screen.fill(BLACK)
        # Draw grid
        for x in range(0, WIDTH, editor_grid_size):
            pygame.draw.line(screen, GRAY, (x - editor_scroll_x % editor_grid_size, 0),
                             (x - editor_scroll_x % editor_grid_size, HEIGHT))
        for y in range(0, HEIGHT, editor_grid_size):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if input_mode:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if input_prompt == 'Enter Level Code:':
                            loaded_level = decode_level(input_text)
                            if loaded_level is not None:
                                load_level(loaded_level)
                                print("Level loaded from code.")
                            else:
                                print("Invalid level code.")
                        input_mode = False
                        input_text = ''
                        input_prompt = ''
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode
                continue  # Skip other event handling when in input mode

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if event.button == 1:  # Left click
                    # Check if clicked on toolbar
                    for i, rect in enumerate(toolbar_rects):
                        if rect.collidepoint(mouse_x, mouse_y):
                            current_object = toolbar_items[i]['type']
                            break
                    else:
                        grid_x = (mouse_x + editor_scroll_x) // editor_grid_size * editor_grid_size
                        grid_y = mouse_y // editor_grid_size * editor_grid_size
                        # Place object
                        new_obj = {'type': current_object, 'x': grid_x, 'y': grid_y}
                        level.append(new_obj)
                        undo_stack.append(('add', new_obj))
                elif event.button == 3:  # Right click to delete
                    grid_x = (mouse_x + editor_scroll_x) // editor_grid_size * editor_grid_size
                    grid_y = mouse_y // editor_grid_size * editor_grid_size
                    for obj in level:
                        if obj['x'] == grid_x and obj['y'] == grid_y:
                            level.remove(obj)
                            undo_stack.append(('remove', obj))
                            break
                elif event.button == 2:  # Middle click to select/move
                    grid_x = (mouse_x + editor_scroll_x) // editor_grid_size * editor_grid_size
                    grid_y = mouse_y // editor_grid_size * editor_grid_size
                    for obj in level:
                        if obj['x'] == grid_x and obj['y'] == grid_y:
                            selected_object = obj
                            dragging = True
                            break

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:  # Release middle click
                    dragging = False
                    selected_object = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_level("levels/custom_level.json")
                    print("Level saved.")
                elif event.key == pygame.K_e:
                    # Generate code from level
                    level_code = encode_level(level)
                    show_code = True
                elif event.key == pygame.K_l:
                    # Enter code to load level
                    input_mode = True
                    input_prompt = 'Enter Level Code:'
                    input_text = ''
                elif event.key == pygame.K_u:
                    # Undo
                    if undo_stack:
                        action, obj = undo_stack.pop()
                        if action == 'add':
                            level.remove(obj)
                            redo_stack.append(('add', obj))
                        elif action == 'remove':
                            level.append(obj)
                            redo_stack.append(('remove', obj))
                elif event.key == pygame.K_r:
                    # Redo
                    if redo_stack:
                        action, obj = redo_stack.pop()
                        if action == 'add':
                            level.append(obj)
                            undo_stack.append(('add', obj))
                        elif action == 'remove':
                            level.remove(obj)
                            undo_stack.append(('remove', obj))
                elif event.key == pygame.K_ESCAPE:
                    return False  # Exit the editor

        if dragging and selected_object:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            selected_object['x'] = (mouse_x + editor_scroll_x) // editor_grid_size * editor_grid_size
            selected_object['y'] = mouse_y // editor_grid_size * editor_grid_size

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            editor_scroll_x = max(0, editor_scroll_x - 10)
        if keys[pygame.K_RIGHT]:
            editor_scroll_x += 10

        # Draw level
        draw_level(editor_scroll_x)

        # Draw selected object outline
        if dragging and selected_object:
            obj_x = selected_object['x'] - editor_scroll_x
            obj_y = selected_object['y']
            pygame.draw.rect(screen, BLUE, (obj_x, obj_y, 40, 40), 2)

        # Draw toolbar
        pygame.draw.rect(screen, GRAY, (0, 0, 60, HEIGHT))
        for i, rect in enumerate(toolbar_rects):
            screen.blit(toolbar_items[i]['icon'], (rect.x, rect.y))
            if current_object == toolbar_items[i]['type']:
                pygame.draw.rect(screen, YELLOW, rect, 2)

        # Input mode overlay
        if input_mode:
            pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 200, HEIGHT // 2 - 50, 400, 100))
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 200, HEIGHT // 2 - 50, 400, 100), 2)
            prompt_surface = FONT.render(input_prompt, True, WHITE)
            text_surface = FONT.render(input_text, True, WHITE)
            screen.blit(prompt_surface, (WIDTH // 2 - prompt_surface.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2))

        # Display level code
        if show_code:
            pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 300, HEIGHT // 2 - 100, 600, 200))
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 300, HEIGHT // 2 - 100, 600, 200), 2)
            lines = []
            code_str = f"Level Code:\n{level_code}"
            while len(code_str) > 60:
                lines.append(code_str[:60])
                code_str = code_str[60:]
            lines.append(code_str)
            for i, line in enumerate(lines):
                line_surface = FONT.render(line, True, WHITE)
                screen.blit(line_surface, (WIDTH // 2 - 280, HEIGHT // 2 - 80 + i * 20))
            instruction_surface = FONT.render("Press any key to continue...", True, WHITE)
            screen.blit(instruction_surface, (WIDTH // 2 - instruction_surface.get_width() // 2, HEIGHT // 2 + 80))
            pygame.display.flip()
            # Wait for key press to close code display
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        waiting = False
                    elif event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
            show_code = False

        # Display instructions at the bottom
        instructions = "S: Save  E: Export Code  L: Load Code  U: Undo  R: Redo  ESC: Exit"
        instr_surface = FONT.render(instructions, True, WHITE)
        screen.blit(instr_surface, (70, HEIGHT - 30))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

def save_level(filename):
    with open(filename, 'w') as f:
        json.dump(level, f, indent=4)

def load_custom_levels():
    custom_levels = []
    for filename in os.listdir("levels"):
        if filename.endswith(".json"):
            with open(os.path.join("levels", filename), 'r') as f:
                custom_levels.append(json.load(f))
    return custom_levels

def main_menu():
    play_button = Button("Play Game", (WIDTH // 2 - 75, 250), FONT)
    edit_button = Button("Level Editor", (WIDTH // 2 - 75, 320), FONT)
    custom_button = Button("Custom Levels", (WIDTH // 2 - 75, 390), FONT)
    share_button = Button("Load Level from Code", (WIDTH // 2 - 100, 460), FONT)
    quit_button = Button("Quit", (WIDTH // 2 - 50, 530), FONT)

    while True:
        screen.fill(BLACK)
        title = TITLE_FONT.render("Geometry Dash 2.4", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        play_button.draw(screen)
        edit_button.draw(screen)
        custom_button.draw(screen)
        share_button.draw(screen)
        quit_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if play_button.is_clicked(event.pos):
                        load_level(LEVELS["1-1"])
                        if game_loop():
                            continue
                        else:
                            return False
                    elif edit_button.is_clicked(event.pos):
                        if editor_loop():
                            continue
                        else:
                            return False
                    elif custom_button.is_clicked(event.pos):
                        custom_levels = load_custom_levels()
                        for custom_level in custom_levels:
                            load_level(custom_level)
                            if game_loop():
                                continue
                            else:
                                break
                    elif share_button.is_clicked(event.pos):
                        # Prompt user to enter a level code
                        input_mode = True
                        input_prompt = 'Enter Level Code:'
                        input_text = ''
                        while input_mode:
                            screen.fill(BLACK)
                            prompt_surface = FONT.render(input_prompt, True, WHITE)
                            text_surface = FONT.render(input_text, True, WHITE)
                            screen.blit(prompt_surface, (WIDTH // 2 - prompt_surface.get_width() // 2, HEIGHT // 2 - 40))
                            screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2))
                            pygame.display.flip()
                            for event in pygame.event.get():
                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_RETURN:
                                        loaded_level = decode_level(input_text)
                                        if loaded_level is not None:
                                            load_level(loaded_level)
                                            print("Level loaded from code.")
                                            if game_loop():
                                                continue
                                            else:
                                                return False
                                        else:
                                            print("Invalid level code.")
                                        input_mode = False
                                    elif event.key == pygame.K_BACKSPACE:
                                        input_text = input_text[:-1]
                                    else:
                                        input_text += event.unicode
                                elif event.type == pygame.QUIT:
                                    pygame.quit()
                                    exit()
                    elif quit_button.is_clicked(event.pos):
                        return False

        pygame.display.flip()
        pygame.time.Clock().tick(60)

class Button:
    def __init__(self, text, pos, font, bg=LIGHT_GRAY, fg=WHITE):
        self.x, self.y = pos
        self.font = font
        self.text = self.font.render(text, True, fg)
        self.surface = pygame.Surface((200, 50))
        self.surface.fill(bg)
        self.surface.blit(self.text, ((200 - self.text.get_width()) // 2, (50 - self.text.get_height()) // 2))
        self.rect = pygame.Rect(self.x, self.y, 200, 50)

    def draw(self, screen):
        screen.blit(self.surface, (self.x, self.y))

    def is_clicked(self, event_pos):
        return self.rect.collidepoint(event_pos)

# Create the "levels" directory if it doesn't exist
if not os.path.exists("levels"):
    os.makedirs("levels")

# Start the game
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Set up the display
pygame.display.set_caption("Geometry Dash 2.4")
main_menu()
pygame.quit()
