from ursina import *
from ursina.shaders import lit_with_shadows_shader

app = Ursina()

# Scene setup
window.color = color.light_gray
ground = Entity(model='plane', scale=(20,1,20), texture='white_cube', 
                texture_scale=(20,20), collider='box')  # patch the bugs $ > test.py

# Player class
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
        self.speed = 5
        self.jump_height = 4
        self.gravity = 1
        self.velocity = Vec3(0,0,0)
        self.camera_pivot = Entity(parent=self, y=2)
        self.grounded = False
        
        camera.parent = self.camera_pivot
        camera.position = (0, 0, -8)
        camera.rotation = (10, 0, 0)

    def update(self):
        # Movement relative to camera
        movement = self.camera_pivot.forward * (held_keys['w'] - held_keys['s']) + \
                   self.camera_pivot.right * (held_keys['d'] - held_keys['a'])
        movement = movement.normalized()
        
        self.velocity = lerp(self.velocity, movement * self.speed, time.dt * 5)
        self.velocity.y -= self.gravity * time.dt
        
        # Ground check
        self.grounded = self.intersects(ground).hit
        if self.grounded and self.velocity.y < 0:
            self.velocity.y = 0
        
        # Velocity clamping
        self.velocity = Vec3(
            clamp(self.velocity.x, -self.speed, self.speed),
            clamp(self.velocity.y, -10, 10),
            clamp(self.velocity.z, -self.speed, self.speed)
        )
        
        self.position += self.velocity * time.dt
        
        if self.y < -10:
            self.position = (0,5,0)
        
        # Camera rotation
        self.camera_pivot.rotation_y += mouse.velocity[0] * 40
        self.camera_pivot.rotation_x -= mouse.velocity[1] * 40
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -60, 60)

    def input(self, key):
        if key == 'space' and self.grounded:
            self.velocity.y = self.jump_height

# Level elements
platform = Entity(model='cube', scale=(5,1,5), position=(0,10,0), 
                  collider='box', texture='white_cube')
coin = Entity(model='sphere', color=color.yellow, scale=0.5, 
              position=(0,12,0), collider='sphere')
goal = Entity(model='cube', color=color.gold, scale=(2,2,2), 
              position=(5,12,0), collider='box')

# Game systems
score = 0
score_text = Text(text='Score: 0', position=(-0.8, 0.45))

def update():
    global score
    hit_info = player.intersects()
    if hit_info.hit:
        if hit_info.entity == coin:
            score += 10
            score_text.text = f'Score: {score}'
            destroy(coin)
        if hit_info.entity == goal:
            print('LEVEL COMPLETE!')
            application.pause()

player = Player()
mouse.locked = True
Sky()

app.run()
