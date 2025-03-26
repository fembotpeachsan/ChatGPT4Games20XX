# test.py
# -------------------------------------------------
# A minimal Ursina scene resembling Peach's Castle
# with a simple player entity and basic movement.
# -------------------------------------------------

from ursina import *
import random
import math

app = Ursina()

# Window settings
window.title = "Peach's Castle - B3313 Test Map"
window.borderless = False
Texture.default_filtering = None
window.color = color.black

# -------------------------------------------------
# Player (white cube) with simple movement & jumping
# -------------------------------------------------
class Player(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.white,
            position=(0, 0.5, 4),  # Start at the castle entrance
            scale=(0.5, 1, 0.5),
            collider='box'
        )
        self.speed = 6
        self.jump_power = 8
        self.velocity_y = 0
        self.grounded = True  # Start as grounded
        self.move_dir = Vec3(0,0,0)
        self.gravity_enabled = False  # Disable gravity by default

    def update(self):
        # Gather movement input
        move_input = Vec3(
            held_keys['d'] - held_keys['a'],
            0,
            held_keys['w'] - held_keys['s']
        )

        # Smooth directional movement
        if move_input.length() > 0:
            move_input = move_input.normalized()
            self.move_dir = lerp(self.move_dir, move_input, 6 * time.dt)
        else:
            self.move_dir = lerp(self.move_dir, Vec3(0,0,0), 4 * time.dt)

        # Apply movement
        move_amount = self.move_dir * self.speed
        self.position += move_amount * time.dt

        # Face the direction of movement
        if self.move_dir.length() > 0.1:
            target_angle = math.degrees(math.atan2(-self.move_dir.x, -self.move_dir.z))
            self.rotation_y = lerp(self.rotation_y, target_angle, 10 * time.dt)

        # Only apply gravity if enabled
        if self.gravity_enabled:
            self.velocity_y -= 20 * time.dt
            self.y += self.velocity_y * time.dt

            # Raycast for ground collision
            hit_info = raycast(
                self.world_position + Vec3(0, 0.1, 0),
                Vec3(0, -1, 0),
                distance=0.6,
                ignore=[self]
            )
            self.grounded = hit_info.hit
            if self.grounded:
                self.velocity_y = 0
                # Adjust y so we rest neatly on top of blocks
                self.y = hit_info.world_point.y + 0.5

    def input(self, key):
        # Jump if on ground and gravity is enabled
        if key == 'space' and self.grounded and self.gravity_enabled:
            self.velocity_y = self.jump_power
        
        # Toggle gravity with G key
        elif key == 'g':
            self.gravity_enabled = not self.gravity_enabled
            if not self.gravity_enabled:
                self.velocity_y = 0  # Reset vertical velocity when disabling gravity
                
        # Quit on ESC
        elif key == 'escape':
            application.quit()


# -------------------------------------------------
# Basic cubic block for castle geometry
# -------------------------------------------------
class Block(Entity):
    def __init__(self, position=(0, 0, 0), color=color.light_gray, scale=(1,1,1)):
        super().__init__(
            model='cube',
            color=color,
            position=position,
            scale=scale,
            collider='box'
        )


# -------------------------------------------------
# Castle generation
# -------------------------------------------------
def create_peachs_castle():
    # Ground courtyard
    Entity(
        model='cube',
        scale=(30, 1, 30),
        position=(0, -0.5, 0),
        color=color.green,
        collider='box'
    )

    # Castle base (front wall)
    for x in range(-4, 5):
        for y in range(0, 5):
            Block(position=(x, y, 5), color=color.light_gray)

    # Castle sides
    for z in range(4, 9):
        for y in range(0, 5):
            Block(position=(-4, y, z), color=color.gray)
            Block(position=(4, y, z), color=color.gray)

    # Castle towers
    for x in [-4, 4]:
        for z in [8]:
            for y in range(5, 8):
                Block(position=(x, y, z), color=color.gray)

    # Castle door (thin block)
    Block(position=(0, 0, 4), color=color.brown, scale=(2,2,0.2))

    # Floating star block inside
    Block(position=(0, 2, 6), color=color.yellow, scale=(0.7, 0.7, 0.7))


# -------------------------------------------------
# Setup camera and top-level update for camera follow
# -------------------------------------------------
camera.position = (0, 5, -15)
camera_offset = Vec3(0, 5, -15)

def update():
    # Smooth camera follow
    desired = player.world_position + camera_offset
    camera.world_position = lerp(camera.world_position, desired, 4 * time.dt)
    camera.look_at(player.position + Vec3(0,1,0))


# -------------------------------------------------
# Initialize game
# -------------------------------------------------
player = Player()
create_peachs_castle()

app.run()