from ursina import *
from ursina.shaders import lit_with_shadows_shader
from random import randint

app = Ursina()

# Scene setup
window.color = color.light_gray
ground = Entity(model='plane', scale=(50,1,50), texture='grass', 
               texture_scale=(10,10), collider='box')

# Player class with improved movement
class Player(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.red,
            scale=(1,2,1),
            position=(0,5,0),
            collider='box',
            shader=lit_with_shadows_shader
        )
        self.speed = 6
        self.jump_height = 5
        self.gravity = 1.2
        self.velocity = Vec3(0,0,0)
        self.camera_pivot = Entity(parent=self, y=2)
        self.grounded = False
        
        camera.parent = self.camera_pivot
        camera.position = (0, 1, -8)
        camera.rotation = (15, 0, 0)

    def update(self):
        movement = self.camera_pivot.forward * (held_keys['w'] - held_keys['s']) + \
                   self.camera_pivot.right * (held_keys['d'] - held_keys['a'])
        movement = movement.normalized()
        
        self.velocity = lerp(self.velocity, movement * self.speed, time.dt * 5)
        self.velocity.y -= self.gravity * time.dt
        
        self.grounded = self.intersects(ground).hit
        if self.grounded and self.velocity.y < 0:
            self.velocity.y = 0
            
        self.position += self.velocity * time.dt
        
        if self.y < -10:
            self.position = (0,10,0)
        
        self.camera_pivot.rotation_y += mouse.velocity[0] * 40
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x - mouse.velocity[1] * 40, -60, 60)

    def input(self, key):
        if key == 'space' and self.grounded:
            self.velocity.y = self.jump_height

# Battlefield Elements
class MountainTerrain(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            scale=(30,10,30),
            position=(0,5,30),
            rotation=(0,0,15),
            texture='rock',
            collider='mesh'
        )

class Bobomb(Entity):
    def __init__(self, position):
        super().__init__(
            model='sphere',
            color=color.black,
            scale=0.8,
            position=position,
            collider='sphere'
        )
        self.speed = 2
        
    def update(self):
        self.rotation_y += 50 * time.dt
        if distance(self, player) < 5:
            self.position += (player.position - self.position).normalized() * self.speed * time.dt

class ChainChomp(Entity):
    def __init__(self):
        super().__init__(
            model='sphere',
            color=color.black,
            scale=1.5,
            position=(10,3,15),
            collider='sphere'
        )
        self.chain = Entity(model=Circle(6), color=color.gray, scale=0.3, eternal=True)
        self.anchor = Entity(position=(10,5,15))
        self.t = 0
        
    def update(self):
        self.t += time.dt
        self.position = self.anchor.position + Vec3(math.sin(self.t*2)*3, 0, math.cos(self.t*2)*3)
        self.chain.position = self.anchor.position
        self.chain.look_at(self)

class RollingBoulder(Entity):
    def __init__(self, path_start, path_end):
        super().__init__(
            model='sphere',
            texture='rock',
            scale=2,
            position=path_start,
            collider='sphere'
        )
        self.path = [path_start, path_end]
        self.speed = 3
        
    def update(self):
        self.position = lerp(self.position, self.path[1], time.dt * self.speed)
        self.rotation_y += 100 * time.dt
        if distance(self, self.path[1]) < 1:
            self.path.reverse()

# Level Construction
mountain = MountainTerrain()
chomp = ChainChomp()
boulders = [RollingBoulder((x*10,5,40), (x*10,5,55)) for x in range(-2,3)]
bobombs = [Bobomb((randint(-15,15),3, randint(20,40))) for _ in range(8)]

# Teetering Bridge
bridge = Entity(
    model='cube', 
    scale=(15,0.2,3), 
    position=(0,8,25),
    texture='wood',
    collider='box'
)

# Floating Island
floating_island = Entity(
    model='cube',
    scale=(5,1,5),
    position=(0,25,40),
    texture='grass',
    collider='box'
)
power_star = Entity(
    model='star',
    color=color.yellow,
    scale=0.5,
    position=floating_island.position + (0,2,0),
    collider='mesh'
)

# Game Systems
score = 0
score_text = Text(text='Stars: 0', position=(-0.85, 0.45))

def update():
    global score
    hit_info = player.intersects()
    if hit_info.hit:
        if hit_info.entity == power_star:
            score += 1
            score_text.text = f'Stars: {score}'
            destroy(power_star)
        elif isinstance(hit_info.entity, Bobomb):
            player.position = (0,10,0)

player = Player()
mouse.locked = True
Sky()

app.run()
