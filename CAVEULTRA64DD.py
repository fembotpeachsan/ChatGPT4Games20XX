from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import random, sin, cos

app = Ursina()

class Voxel(Button):
    def __init__(self, position = (0,0,0)):
        super().__init__(
            parent = scene,
            position = position,
            model = 'cube',
            origin_y = 0.5,
            texture = 'white_cube',
            color = color.color(0, 0, random.uniform(0.9, 1.0)),
            highlight_color = color.lime,
        )

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                voxel = Voxel(position=self.position + mouse.normal)
            if key == 'right mouse down':
                destroy(self)

class AI(Entity):
    def __init__(self):
        super().__init__(
            parent = scene,
            model = 'cube',
            color = color.red,
        )

    def update(self):
        self.look_at(player)
        self.position += self.forward * time.dt

class Player(FirstPersonController):
    def __init__(self):
        super().__init__()
        self.version_text = Text(text='Version: 1.0.0', position=(-0.5,-0.4), scale=2)

    def update(self):
        super().update()  # Run the original update method
        if self.position.y < -20:  # If the player falls into the void
            self.position = (10, 10, 10)  # Respawn player at the center of the map

for z in range(20):
    for x in range(20):
        y = sin(x)*cos(z)*5  # Simple terrain generation using sine and cosine
        y = round(y)
        for y in range(y+1):
            voxel = Voxel(position=(x,y,z))

player = Player()
player.position = (10, 10, 10)  # Spawn player in the center of the map

ai = AI()

app.run()
