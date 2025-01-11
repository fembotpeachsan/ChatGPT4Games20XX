from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

class BetaMario64HUD(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui)

        # Initialize counters
        self.coins = 0
        self.stars = 0
        self.health = 8  # Maximum health (8 segments)

        # Power Meter (Health Bar)
        self.power_meter = Sprite(
            parent=self,
            texture='circle',
            position=Vec2(-0.8, 0.4),
            scale=0.15,
            color=color.red
        )

        # Coin Counter
        self.coin_icon = Sprite(
            parent=self,
            texture='coin',
            position=Vec2(0.7, 0.4),
            scale=0.1
        )
        self.coin_text = Text(
            parent=self,
            text="x 0",
            position=Vec2(0.73, 0.39),
            scale=2,
            color=color.white
        )

        # Star Counter
        self.star_icon = Sprite(
            parent=self,
            texture='star',
            position=Vec2(0.7, 0.3),
            scale=0.1
        )
        self.star_text = Text(
            parent=self,
            text="x 0",
            position=Vec2(0.73, 0.29),
            scale=2,
            color=color.white
        )

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update_hud(self):
        """
        Updates HUD elements (e.g., coin and star counters, health).
        """
        self.coin_text.text = f"x {self.coins}"
        self.star_text.text = f"x {self.stars}"
        # Scale power meter based on health
        self.power_meter.scale = 0.15 * (self.health / 8)

class DynamicGameTest(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for _ in range(50):  # Add 50 dynamic cubes
            Entity(
                model='cube',
                color=color.random_color(),
                position=(random.uniform(-20, 20), random.uniform(0, 10), random.uniform(-20, 20)),
                collider='box'
            )

app = Ursina()

# Game Environment
window.color = color.black  # Void-like background
ground = Entity(model='plane', scale=50, collider='box', visible=False)

# Player
player = FirstPersonController()
player.gravity = 1

# HUD
beta_mario_64_hud = BetaMario64HUD()

# Dynamic Game Test
dynamic_test = DynamicGameTest()

def update():
    """
    Global update function called every frame.
    """
    # Simulate collecting coins and stars
    if held_keys['c']:
        beta_mario_64_hud.coins += 1
    if held_keys['s']:
        beta_mario_64_hud.stars += 1
    if held_keys['h']:
        beta_mario_64_hud.health = max(0, beta_mario_64_hud.health - 1)

    beta_mario_64_hud.update_hud()

app.run()
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController


class FileSelectScreen(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui)

        # Background
        self.bg = Entity(
            parent=self,
            model='quad',
            texture='white_cube',
            color=color.dark_gray,
            scale=(1.5, 1, 1),
            z=1
        )

        # Title
        self.title = Text(
            text="File Select",
            scale=3,
            position=Vec2(0, 0.4),
            parent=self
        )

        # Save file buttons
        self.file_slots = []
        for i in range(3):  # Create 3 save file slots
            button = Button(
                text=f"File {i + 1}",
                scale=(0.6, 0.1),
                position=(0, 0.2 - i * 0.2),
                parent=self,
                on_click=lambda i=i: self.select_file(i)
            )
            self.file_slots.append(button)

        # Selected file
        self.selected_file = None

        # Start button (hidden initially)
        self.start_button = Button(
            text="Start Game",
            scale=(0.4, 0.1),
            position=(0, -0.4),
            color=color.azure,
            parent=self,
            visible=False,
            on_click=self.start_game
        )

        for key, value in kwargs.items():
            setattr(self, key, value)

    def select_file(self, file_index):
        """
        Called when a file slot is selected.
        """
        self.selected_file = file_index + 1
        for i, button in enumerate(self.file_slots):
            button.color = color.lime if i == file_index else color.white
        self.start_button.visible = True
        print(f"Selected File {self.selected_file}")

    def start_game(self):
        """
        Starts the game with the selected file.
        """
        print(f"Starting game with File {self.selected_file}")
        self.disable()  # Hide the file select screen


class BetaMario64HUD(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui)

        # Example HUD setup
        self.coin_text = Text(
            parent=self,
            text="x 0",
            position=Vec2(0.7, 0.4),
            scale=2,
            color=color.white
        )


class Game(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        # HUD
        self.hud = BetaMario64HUD()

        # Player
        self.player = FirstPersonController()
        self.player.gravity = 1  # Standard gravity

        # Ground
        Entity(model='plane', scale=50, collider='box', visible=False)


app = Ursina()

# File Select Screen
file_select_screen = FileSelectScreen()

# Game (disabled initially)
game = Game(enabled=False)


def update():
    """
    Global update function.
    """
    # Transition to game once file is selected
    if not file_select_screen.enabled and not game.enabled:
        game.enabled = True


app.run()
