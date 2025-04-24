from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()
window.title = "SM64-like Ursina Test"
window.fps_counter.enabled = True
window.exit_button.visible = False
window.update_interval = 1/60

# --- Constants ---
GRAVITY = 1
JUMP_HEIGHT = 2.2
WALK_SPEED = 5
RUN_SPEED = 10
CAMERA_DIST = 12
CAMERA_HEIGHT = 6

# --- Player ---
class Mario(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.azure,
            scale=(1,2,1),
            collider='box',
            position=(0,2,0)
        )
        self.controller = FirstPersonController(
            model=None, collider=None, enabled=False
        )
        self.speed = WALK_SPEED
        self.jump_height = JUMP_HEIGHT
        self.grounded = False
        self.vel_y = 0
        self.health = 3
        self.max_health = 3
        self.coins = 0
        self.invuln = 0
        self.can_double_jump = False
        self.double_jumped = False
        self.wall_jump_cooldown = 0
        self.star_timer = 0
        self.fireballs = 0
        self.ground_pound = False
        self.long_jump = False
        self.last_wall = None

    def update(self):
        # Gravity
        if not self.grounded:
            self.vel_y -= GRAVITY * time.dt * 2
        else:
            self.vel_y = max(self.vel_y, 0)
        self.y += self.vel_y

        # Ground check
        self.grounded = False
        hits = boxcast(self.world_position + (0,0.1,0), (0,-1,0), distance=0.15, thickness=(0.7,0.05,0.7))
        if hits.hit:
            self.grounded = True
            self.double_jumped = False
            self.ground_pound = False
            self.long_jump = False
            self.vel_y = 0
            self.y = hits.world_point[1] + 1

        # Invulnerability
        if self.invuln > 0:
            self.invuln -= time.dt
            self.visible = int(self.invuln*10)%2==0
        else:
            self.visible = True

        # Star
        if self.star_timer > 0:
            self.star_timer -= time.dt
            self.color = color.yellow
            if self.star_timer <= 0:
                self.color = color.azure

        # Wall jump cooldown
        if self.wall_jump_cooldown > 0:
            self.wall_jump_cooldown -= time.dt

        # Movement
        move = Vec3(0,0,0)
        if held_keys['w']: move += camera.forward
        if held_keys['s']: move -= camera.forward
        if held_keys['a']: move -= camera.right
        if held_keys['d']: move += camera.right
        move.y = 0
        if move.length() > 0:
            move = move.normalized() * self.speed * time.dt
            self.position += move

        # Run
        if held_keys['shift']:
            self.speed = RUN_SPEED
        else:
            self.speed = WALK_SPEED

        # Camera follow
        cam_target = self.position + Vec3(0,CAMERA_HEIGHT,0) - camera.forward*CAMERA_DIST
        camera.position = lerp(camera.position, cam_target, 8*time.dt)
        camera.look_at(self.position + Vec3(0,1,0))

        # Respawn if fall
        if self.y < -20:
            self.take_damage(1)
            self.position = (0,5,0)
            self.vel_y = 0

    def jump(self):
        if self.grounded:
            self.vel_y = self.jump_height
            self.grounded = False
        elif self.can_double_jump and not self.double_jumped:
            self.vel_y = self.jump_height
            self.double_jumped = True
        elif self.wall_jump_cooldown <= 0:
            # Wall jump
            for d in [(1,0,0),(-1,0,0),(0,0,1),(0,0,-1)]:
                hit = boxcast(self.position, d, distance=0.7, thickness=(0.7,1.8,0.7))
                if hit.hit and hit.entity != self.last_wall:
                    self.vel_y = self.jump_height
                    self.position += Vec3(*d)*0.5
                    self.wall_jump_cooldown = 0.3
                    self.last_wall = hit.entity
                    break

    def do_ground_pound(self):
        if not self.grounded and not self.ground_pound:
            self.vel_y = -8
            self.ground_pound = True

    def do_long_jump(self):
        if self.grounded and held_keys['shift']:
            self.vel_y = self.jump_height*1.1
            forward = camera.forward
            forward.y = 0
            self.position += forward.normalized()*2
            self.long_jump = True

    def take_damage(self, amount):
        if self.invuln > 0 or self.star_timer > 0:
            return
        self.health -= amount
        self.invuln = 1.5
        if self.health <= 0:
            self.respawn()
        health_text.text = f'Health: {self.health}'

    def respawn(self):
        self.position = (0,5,0)
        self.health = self.max_health
        self.coins = 0
        self.invuln = 2
        health_text.text = f'Health: {self.health}'
        coin_text.text = f'Coins: {self.coins}'

    def collect_coin(self):
        self.coins += 1
        coin_text.text = f'Coins: {self.coins}'
        if self.coins % 50 == 0:
            self.health = min(self.health+1, self.max_health)
            health_text.text = f'Health: {self.health}'

    def collect_powerup(self, ptype):
        if ptype == 'mushroom':
            self.max_health += 1
            self.health = self.max_health
            health_text.text = f'Health: {self.health}'
        elif ptype == 'flower':
            self.fireballs = 10
        elif ptype == 'star':
            self.star_timer = 8

player = Mario()

# --- UI ---
coin_text = Text(text=f'Coins: {player.coins}', position=(-0.85, 0.45), scale=1.5, origin=(-0.5, 0))
health_text = Text(text=f'Health: {player.health}', position=(-0.85, 0.40), scale=1.5, origin=(-0.5, 0))
debug_text = Text(text='', position=(0.5, 0.45), scale=1.2, origin=(0.5, 0))

# --- World ---
Sky(color=color.cyan)
ground = Entity(model='plane', scale=100, color=color.lime, collider='box')
platforms = [
    Entity(model='cube', color=color.gray, position=(0,2,10), scale=(5,1,5), collider='box'),
    Entity(model='cube', color=color.gray, position=(-8,4,15), scale=(3,1,3), collider='box'),
    Entity(model='cube', color=color.gray, position=(8,6,20), scale=(4,1,4), collider='box'),
    Entity(model='cube', color=color.brown, position=(0,8,30), scale=(6,1,6), collider='box')
]

# Moving platform
moving_platform = Entity(model='cube', color=color.orange, position=(0,3,20), scale=(3,0.5,3), collider='box')
moving_dir = 1

# --- Coins ---
coins = []
for i in range(12):
    coins.append(Entity(
        model='sphere', color=color.yellow, position=(random.uniform(-10,10),1,random.uniform(5,30)),
        scale=0.5, collider='sphere', name='coin'
    ))
for p in platforms:
    coins.append(Entity(model='sphere', color=color.yellow, position=p.position+(0,1,0), scale=0.5, collider='sphere', name='coin'))

# --- Powerups ---
powerups = [
    Entity(model='sphere', color=color.red, position=platforms[0].position+(1,1,0), scale=0.7, collider='sphere', name='mushroom'),
    Entity(model='sphere', color=color.orange, position=platforms[1].position+(-1,1,0), scale=0.7, collider='sphere', name='flower'),
    Entity(model='sphere', color=color.white, position=platforms[2].position+(1,1,0), scale=0.7, collider='sphere', name='star')
]

# --- Enemies ---
class Goomba(Entity):
    def __init__(self, position):
        super().__init__(
            model='sphere', color=color.brown, position=position, scale=(1,0.7,1),
            collider='sphere', name='goomba'
        )
        self.speed = 2
        self.dir = random.choice([-1,1])
        self.alive = True

    def update(self):
        if not self.alive: return
        self.x += self.dir * self.speed * time.dt
        # Turn at edge
        if abs(self.x) > 15:
            self.dir *= -1
        # Player collision
        if distance(self, player) < 1.2 and self.alive:
            if player.y > self.y+0.7:
                self.alive = False
                self.disable()
                player.vel_y = player.jump_height*0.7
            elif player.star_timer > 0:
                self.alive = False
                self.disable()
            elif player.invuln <= 0:
                player.take_damage(1)

enemies = [Goomba((random.uniform(-10,10),1,random.uniform(5,30))) for _ in range(5)]
enemies += [Goomba(platforms[0].position+(2,1,0)), Goomba(platforms[1].position+(-2,1,0))]

# --- Update ---
def update():
    player.update()
    debug_text.text = f'Pos: {player.position.round(2)}'

    # Moving platform
    global moving_dir
    moving_platform.x += moving_dir * 2 * time.dt
    if abs(moving_platform.x) > 5:
        moving_dir *= -1

    # Coin collection
    for c in coins:
        if c.enabled and distance(player, c) < 1.2:
            c.disable()
            player.collect_coin()

    # Powerup collection
    for p in powerups:
        if p.enabled and distance(player, p) < 1.2:
            p.disable()
            player.collect_powerup(p.name)

    # Enemy update
    for e in enemies:
        e.update()

    # Mario on moving platform
    if abs(player.y - moving_platform.y) < 1.1 and abs(player.x - moving_platform.x) < 1.5 and abs(player.z - moving_platform.z) < 1.5:
        player.y = moving_platform.y + 1

# --- Input ---
def input(key):
    if key == 'space':
        player.jump()
    if key == 'q':
        player.do_ground_pound()
    if key == 'e':
        player.do_long_jump()
    if key == 'tab':
        player.can_double_jump = not player.can_double_jump
        print_on_screen(f"Double Jump {'ON' if player.can_double_jump else 'OFF'}", duration=1)
    if key == 'f' and player.fireballs > 0:
        # Fireball
        fb = Entity(model='sphere', color=color.red, position=player.position+(0,1,0), scale=0.3)
        fb.dir = camera.forward.normalized()
        fb.life = 2
        def fb_update():
            fb.position += fb.dir*12*time.dt
            fb.life -= time.dt
            for e in enemies:
                if e.enabled and distance(fb, e) < 1.2:
                    e.alive = False
                    e.disable()
                    fb.disable()
            if fb.life <= 0:
                fb.disable()
        fb.update = fb_update
        player.fireballs -= 1

# --- Run ---
app.run()
