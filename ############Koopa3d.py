from ursina import *
import random

app = Ursina()

# Set up the scene
Sky(color=color.azure)
ground = Entity(model='plane', scale=(50, 1, 50), color=color.green.tint(-.2), texture='white_cube', texture_scale=(50, 50))
player = Entity(model='sphere', color=color.red, position=(0, 1, 0), scale=1)

# Create the Koopa Shell
class KoopaShell(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='cube',
            color=color.red,
            scale=(1, 0.7, 1.2),
            **kwargs
        )
        
        # Add shell details
        self.shell_details = Entity(
            parent=self,
            model='cube',
            color=color.white,
            scale=(0.8, 0.05, 1),
            position=(0, 0.35, 0)
        )
        
        # Add rim to shell
        self.shell_rim = Entity(
            parent=self,
            model='cube',
            color=color.dark_gray,
            scale=(1.1, 0.2, 1.3),
            position=(0, -0.3, 0)
        )
        
        # Movement variables
        self.velocity = 0
        self.rotation_speed = 0
        self.max_speed = 10
        self.acceleration = 5
        self.turn_speed = 3
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 0.5
        
    def update(self):
        # Handle movement
        self.rotation_y += self.rotation_speed * time.dt
        
        # Move forward based on rotation
        direction = Vec3(
            self.forward.x * self.velocity,
            0,
            self.forward.z * self.velocity
        )
        
        self.position += direction * time.dt
        
        # Apply gravity
        if self.is_jumping:
            self.y += self.jump_velocity * time.dt
            self.jump_velocity -= self.gravity
            
            if self.y <= 0.35:  # Ground level
                self.y = 0.35
                self.is_jumping = False
                self.jump_velocity = 0
        
        # Tilt the shell when turning
        self.rotation_z = -self.rotation_speed * 2
        
        # Make the shell wobble a bit when moving
        if abs(self.velocity) > 0.1:
            self.rotation_x = sin(time.time() * 10) * 5
        else:
            self.rotation_x = lerp(self.rotation_x, 0, time.dt * 5)
    
    def input(self, key):
        if key == 'w':
            self.velocity = min(self.velocity + self.acceleration, self.max_speed)
        elif key == 's':
            self.velocity = max(self.velocity - self.acceleration, -self.max_speed/2)
        elif key == 'a':
            self.rotation_speed = -self.turn_speed
        elif key == 'd':
            self.rotation_speed = self.turn_speed
        elif key == 'space' and not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = 8
        elif key == 'w up' or key == 's up':
            self.velocity = lerp(self.velocity, 0, time.dt * 5)
        elif key == 'a up' or key == 'd up':
            self.rotation_speed = 0

# Create the Koopa Shell
shell = KoopaShell(position=(0, 0.35, 0))

# Add some obstacles and platforms
platform1 = Entity(model='cube', color=color.brown, position=(5, 1, 5), scale=(3, 0.5, 3))
platform2 = Entity(model='cube', color=color.brown, position=(-5, 2, -5), scale=(3, 0.5, 3))
platform3 = Entity(model='cube', color=color.brown, position=(10, 3, -10), scale=(3, 0.5, 3))

# Add some coins to collect
coins = []
for i in range(10):
    coin = Entity(
        model='sphere',
        color=color.yellow,
        position=(
            random.uniform(-20, 20),
            random.uniform(1, 5),
            random.uniform(-20, 20)
        ),
        scale=0.5
    )
    coins.append(coin)

# Camera setup
camera.position = (0, 10, -15)
camera.rotation_x = 30

# Camera follow function
def update():
    camera.position = lerp(
        camera.position,
        shell.position + Vec3(0, 10, -15),
        time.dt * 2
    )
    camera.look_at(shell.position)
    
    # Check coin collection
    for coin in coins[:]:
        if distance(shell.position, coin.position) < 1.5:
            coins.remove(coin)
            destroy(coin)
            shell.color = color.lerp(shell.color, color.random_color(), 0.5)

# Add lighting
light = DirectionalLight()
light.look_at(Vec3(1, -1, 1))

# Instructions
Text(
    text='Controls: W/S - Move, A/D - Turn, Space - Jump, Collect coins!',
    position=(-0.85, 0.47),
    scale=0.8,
    background=True
)

app.run()
