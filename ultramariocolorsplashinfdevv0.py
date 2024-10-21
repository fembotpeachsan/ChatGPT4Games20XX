from ursina import *
import random

# Initialize Ursina
app = Ursina()

# Define custom colors
background_color = color.rgb(135, 206, 235)  # Light sky blue
title_color = color.rgb(255, 69, 0)          # Orange-red
button_color = color.rgb(255, 255, 255)      # White
button_highlight = color.rgb(230, 230, 230)  # Slightly darker white
button_text_color = color.rgb(50, 50, 50)    # Dark grey

# Pixel size for letters
pixel_size = 0.02

# Letter bitmaps (5x5 grid representation)
letter_bitmaps = {
    'A': [
        "  X  ",
        " X X ",
        "XXXXX",
        "X   X",
        "X   X"
    ],
    'B': [
        "XXXX ",
        "X   X",
        "XXXX ",
        "X   X",
        "XXXX "
    ],
    'C': [
        " XXXX",
        "X    ",
        "X    ",
        "X    ",
        " XXXX"
    ],
    'D': [
        "XXXX ",
        "X   X",
        "X   X",
        "X   X",
        "XXXX "
    ],
    'E': [
        "XXXXX",
        "X    ",
        "XXX  ",
        "X    ",
        "XXXXX"
    ],
    'I': [
        " XXX ",
        "  X  ",
        "  X  ",
        "  X  ",
        " XXX "
    ],
    'L': [
        "X    ",
        "X    ",
        "X    ",
        "X    ",
        "XXXXX"
    ],
    'M': [
        "X   X",
        "XX XX",
        "X X X",
        "X   X",
        "X   X"
    ],
    'O': [
        " XXX ",
        "X   X",
        "X   X",
        "X   X",
        " XXX "
    ],
    'R': [
        "XXXX ",
        "X   X",
        "XXXX ",
        "X  X ",
        "X   X"
    ],
    'T': [
        "XXXXX",
        "  X  ",
        "  X  ",
        "  X  ",
        "  X  "
    ],
    'U': [
        "X   X",
        "X   X",
        "X   X",
        "X   X",
        " XXX "
    ],
    '2': [
        " XXX ",
        "X   X",
        "  XX ",
        " X   ",
        "XXXXX"
    ],
    'D': [
        "XXXX ",
        "X   X",
        "X   X",
        "X   X",
        "XXXX "
    ],
    ' ': [
        "     ",
        "     ",
        "     ",
        "     ",
        "     "
    ],
    '.': [
        "     ",
        "     ",
        "     ",
        "     ",
        "  X  "
    ],
    # Add more letters as needed
}

# Function to create a letter entity
def create_letter(char, position, color=title_color):
    bitmap = letter_bitmaps.get(char.upper(), letter_bitmaps[' '])
    letter_entity = Entity(parent=camera.ui)
    for y, row in enumerate(bitmap):
        for x, pixel in enumerate(row):
            if pixel == 'X':
                Entity(
                    parent=letter_entity,
                    model='quad',
                    color=color,
                    scale=(pixel_size, pixel_size),
                    position=(x * pixel_size, -y * pixel_size, 0)
                )
    letter_entity.position = position
    return letter_entity

# Function to create text
def create_text(text, start_position, color=title_color):
    x_offset = 0
    for char in text:
        create_letter(char, position=start_position + Vec3(x_offset, 0, 0), color=color)
        # Assuming 5 columns per letter plus 1 space
        x_offset += (len(letter_bitmaps.get(char.upper(), letter_bitmaps[' '])[0]) + 1) * pixel_size

# Cloud class for background animation
class CloudEntity(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=camera.ui,
            model='quad',
            texture='white_cube',
            color=color.white,
            scale=(0.2, 0.1),
            position=(random.uniform(-0.6, 0.6), random.uniform(0.3, 0.5), 0),
            **kwargs
        )
        self.speed = random.uniform(0.01, 0.02)

    def update(self):
        self.x += time.dt * self.speed
        if self.x > 0.8:
            self.x = -0.8
            self.y = random.uniform(0.3, 0.5)

# Button class for the main menu
class MenuButton(Button):
    def __init__(self, text, action, position):
        super().__init__(
            parent=camera.ui,
            text='',  # We'll render text manually
            color=button_color,
            highlight_color=button_highlight,
            pressed_color=button_highlight,
            scale=(0.5, 0.1),
            position=position,
        )
        self.action = action
        # Create button text manually
        text_width = len(text) * (6 * pixel_size)  # 5 pixels plus 1 space
        create_text(
            text,
            start_position=self.position + Vec3(-text_width / 2, -0.015, -0.01),
            color=button_text_color
        )
    
    def input(self, key):
        if self.hovered and key == 'left mouse down':
            button_click_sound.play()  # Play button click sound
            self.action()

# Small button class for options and credits menu
class SmallButton(Button):
    def __init__(self, text, action, position):
        super().__init__(
            parent=camera.ui,
            text='',
            color=button_color,
            highlight_color=button_highlight,
            pressed_color=button_highlight,
            scale=(0.1, 0.05),
            position=position,
        )
        self.action = action
        # Create button text manually
        create_text(
            text,
            start_position=self.position + Vec3(-0.02, 0.015, -0.01),
            color=button_text_color
        )
    
    def input(self, key):
        if self.hovered and key == 'left mouse down':
            button_click_sound.play()  # Play button click sound
            self.action()

# Main menu class
class MainMenu(Entity):
    def __init__(self):
        super().__init__()

        # Background
        self.background = Entity(
            parent=camera.ui,
            model='quad',
            texture=None,
            color=background_color,
            scale=(2, 1, 1),
            z=1
        )

        # Background clouds
        self.clouds = [CloudEntity() for _ in range(5)]

        # Title
        create_text(
            "ULTRA. MARIO 2D",
            start_position=Vec3(-0.4, 0.3, -0.01),
            color=title_color
        )

        # Buttons
        self.start_button = MenuButton('START GAME', action=self.start_game, position=(0, 0.1))
        self.options_button = MenuButton('OPTIONS', action=self.open_options, position=(0, -0.05))
        self.credits_button = MenuButton('CREDITS', action=self.open_credits, position=(0, -0.2))
        self.exit_button = MenuButton('EXIT', action=self.exit_game, position=(0, -0.35))

    def start_game(self):
        print("Starting game...")
        # Placeholder for starting game logic
        pass

    def open_options(self):
        menu_manager.options_menu.enabled = True
        self.enabled = False

    def open_credits(self):
        menu_manager.credits_menu.enabled = True
        self.enabled = False

    def exit_game(self):
        print("Exiting game...")
        application.quit()

# Options menu class
class OptionsMenu(Entity):
    def __init__(self):
        super().__init__()
        self.enabled = False  # Hidden by default

        # Background overlay
        self.background = Entity(
            parent=camera.ui,
            model='quad',
            texture=None,
            color=color.black.tint(-0.3),
            scale=(2, 1, 1),
            z=2
        )

        # Title
        create_text(
            "OPTIONS",
            start_position=Vec3(-0.1, 0.3, -0.01),
            color=title_color
        )

        # Back button
        self.back_button = SmallButton('BACK', action=self.go_back, position=(0, -0.25))

    def go_back(self):
        menu_manager.main_menu.enabled = True
        self.enabled = False

# Credits menu class
class CreditsMenu(Entity):
    def __init__(self):
        super().__init__()
        self.enabled = False  # Hidden by default

        # Background overlay
        self.background = Entity(
            parent=camera.ui,
            model='quad',
            texture=None,
            color=color.black.tint(-0.3),
            scale=(2, 1, 1),
            z=2
        )

        # Title
        create_text(
            "CREDITS",
            start_position=Vec3(-0.2, 0.3, -0.01),
            color=title_color
        )

        # Credits Text
        credits = [
            "Developer:",
            "Your Name",
            "",
            "Music:",
            "Composer Name",
            "",
            "Art:",
            "Artist Name",
            "",
            "Special Thanks:",
            "Person 1",
            "Person 2",
            "Person 3"
        ]

        y_pos = 0.1
        for line in credits:
            create_text(
                line,
                start_position=Vec3(-0.4, y_pos, -0.01),
                color=button_text_color
            )
            y_pos -= 0.05

        # Back button
        self.back_button = SmallButton('BACK', action=self.go_back, position=(0, -0.25))

    def go_back(self):
        menu_manager.main_menu.enabled = True
        self.enabled = False

# Menu Manager
class MenuManager:
    def __init__(self):
        self.main_menu = MainMenu()
        self.options_menu = OptionsMenu()
        self.credits_menu = CreditsMenu()

# Create menu manager
menu_manager = MenuManager()

# Load sound assets (replace with actual file names you have)
try:
    background_music = Audio('background_music.ogg', loop=True, autoplay=False, volume=0.5)
except:
    # Fallback to a default sound if file not found
    background_music = Audio('coin', loop=True, autoplay=False, volume=0.5)

try:
    button_click_sound = Audio('button_click.ogg', autoplay=False, volume=0.7)
except:
    # Fallback to a default sound if file not found
    button_click_sound = Audio('coin', autoplay=False, volume=0.7)

try:
    ambient_wind = Audio('ambient_wind.ogg', loop=True, autoplay=False, volume=0.3)
except:
    # Fallback to a default sound if file not found
    ambient_wind = Audio('ambient_laser', loop=True, autoplay=False, volume=0.3)

# Start background music and ambient sound
background_music.play()
ambient_wind.play()

# Run the game
app.run()
