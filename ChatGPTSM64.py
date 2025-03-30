from ursina import *
from ursina.shaders import lit_with_shadows_shader
from random import randint
import math

app = Ursina()

# Scene setup
window.color = color.light_gray
ground = Entity(model='plane', scale=(50,1,50), texture='grass', 
               texture_scale=(10,10), collider='box')

# Improved Player class
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
        self.speed = 8
        self.jump_height = 6
        self.gravity = 1.5
        self.velocity = Vec3(0,0,0)
        self.camera_pivot = Entity(parent=self, y=2)
        self.grounded = False
        self.invincible = False
        self.invincible_timer = 0
        
        camera.parent = self.camera_pivot
        camera.position = (0, 1, -8)
        camera.rotation = (15, 0, 0)

    def update(self):
        # Smoother movement with diagonal normalization
        movement = self.camera_pivot.forward * (held_keys['w'] - held_keys['s']) + \
                  self.camera_pivot.right * (held_keys['d'] - held_keys['a'])
        if movement.length() > 0:
            movement = movement.normalized()
        
        self.velocity.x = movement.x * self.speed
        self.velocity.z = movement.z * self.speed
        
        # Improved gravity system
        self.velocity.y -= self.gravity * time.dt * 60
        
        self.grounded = self.intersects(ground).hit
        if self.grounded and self.velocity.y < 0:
            self.velocity.y = 0
            
        self.position += self.velocity * time.dt
        
        # Reset position with invincibility
        if self.y < -10:
            self.position = (0,10,0)
            self.invincible = True
            self.invincible_timer = 2
            
        # Camera controls with sensitivity adjustment
        self.camera_pivot.rotation_y += mouse.velocity[0] * 30
        self.camera_pivot.rotation_x = clamp(
            self.camera_pivot.rotation_x - mouse.velocity[1] * 30,
            -60, 60
        )
        
        # Invincibility timer
        if self.invincible:
            self.invincible_timer -= time.dt
            if self.invincible_timer <= 0:
                self.invincible = False

    def input(self, key):
        if key == 'space' and self.grounded:
            self.velocity.y = self.jump_height

# Enhanced Battlefield Elements
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
        self.speed = 2.5
        
    def update(self):
        self.rotation_y += 70 * time.dt
        if distance(self, player) < 5 and not player.invincible:
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
        self.chain = [Entity(model='sphere', color=color.gray, scale=0.15, eternal=True) for _ in range(8)]
        self.anchor = Entity(position=(10,5,15))
        self.t = 0
        
    def update(self):
        self.t += time.dt * 1.5
        self.position = self.anchor.position + Vec3(math.sin(self.t*2)*4, 0, math.cos(self.t*2)*4)
        
        # Update chain segments
        for i, link in enumerate(self.chain):
            link.position = lerp(self.anchor.position, self.position, i/len(self.chain))

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
        self.speed = 4
        self.direction = 1
        
    def update(self):
        target = self.path[0] if self.direction == -1 else self.path[1]
        self.position = lerp(self.position, target, time.dt * self.speed/10)
        self.rotation_y += 150 * time.dt
        
        if distance(self, target) < 1:
            self.direction *= -1

# Level Construction
mountain = MountainTerrain()
chomp = ChainChomp()
boulders = [RollingBoulder((x*10,5,40), (x*10,5,55)) for x in range(-2,3)]
bobombs = [Bobomb((randint(-20,20),3,randint(25,45))) for _ in range(10)]

# Improved Teetering Bridge
bridge = Entity(
    model='cube', 
    scale=(15,0.2,3), 
    position=(0,8,25),
    texture='wood',
    collider='box',
    rotation=(0,0,5)
)

# Enhanced Floating Island
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
    position=floating_island.position + Vec3(0,2,0),
    collider='mesh',
    eternal=True
)

# Game Systems
score = 0
score_text = Text(text='Stars: 0', position=(-0.85, 0.45), origin=(-0.5,-0.5))

# Fixed Title Text
title_text = Text(
    text='PROJECT SM64 DREAMIN EDITION M1 MAC PORT',
    position=(0, 0.4), 
    scale=1.8, 
    origin=(0, 0),
    background=True,
    background_color=color.black66
)

def update():
    global score
    hit_info = player.intersects()
    if hit_info.hit:
        if hit_info.entity == power_star:
            score += 1
            score_text.text = f'Stars: {score}'
            power_star.blink(color.white, duration=0.5)
            power_star.position = Vec3(randint(-20,20), 25, randint(25,45))  # Fixed tuple syntax
            
        elif isinstance(hit_info.entity, Bobomb) and not player.invincible:
            player.position = Vec3(0,10,0)  # Fixed tuple syntax
            player.invincible = True
            player.invincible_timer = 2
            destroy(hit_info.entity)
            bobombs.remove(hit_info.entity)

player = Player()
mouse.locked = True
Sky(texture='sky_sunset')

app.run()
