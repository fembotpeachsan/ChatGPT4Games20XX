from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

game_title = 'Mario & Luigi RPG Test Game'
game_version = '0.1'
window.title = game_title

# Basic character class
class Character(Entity):
    def __init__(self, name, **kwargs):
        super().__init__()
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)

# Basic environment class
class Environment(Entity):
    def __init__(self, name, **kwargs):
        super().__init__()
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)

# Toad Town environment
class ToadTown(Environment):
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.ground = Entity(model='plane', scale=(50, 1, 50), color=color.green, collider='box')
        # Create simple buildings
        for i in range(5):
            building = Entity(model='cube', scale=(3, 5, 3), position=(i * 5 - 10, 2.5, 3), color=color.brown)
            roof = Entity(model='cone', scale=(3, 4, 3), position=(i * 5 - 10, 5, 3), color=color.red)

# Instantiate Toad Town
toad_town = ToadTown('Toad Town')

# Player controller for navigation
player = FirstPersonController()
player.cursor.visible = False
player.gravity = 0.5
player.position = (0, 5, 15)  # Adjusted spawn position

sky = Sky()

# Function to save the game state
def save_game(file_name):
    with open(file_name, 'w') as file:
        file.write(f'Title: {game_title}\n')
        file.write(f'Version: {game_version}\n')

save_game('rpgtest.y')

app.run()
