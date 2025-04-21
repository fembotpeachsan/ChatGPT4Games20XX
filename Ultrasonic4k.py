from ursina import *  # Import Ursina engine classes
import math
import random

# Constants and configuration
WORLD_SIZE = 100       # half-size of the world in X and Z (world extends from -100 to 100 in this example)
TERRAIN_RESOLUTION = 100  # number of points along one side of terrain grid (e.g., 100 -> 100x100 grid)
MAX_SPEED = 20         # maximum horizontal speed for player
ACCELERATION = 40      # acceleration rate for player movement
FRICTION = 8           # deceleration when no input
JUMP_FORCE = 15        # initial jump velocity
GRAVITY = 30           # gravity acceleration
BOOST_SPEED = 30       # speed boost pad target speed
AIR_CONTROL = 0.5      # multiplier for horizontal control in air (less than 1 for less control in air)
# Colors
TERRAIN_COLOR = color.green  # base color for terrain
PLAYER_COLOR = color.azure   # player (Sonic) color
RING_COLOR = color.yellow    # ring color
BOOST_PAD_COLOR = color.orange
JUMP_PAD_COLOR = color.red
RAIL_COLOR = color.gray

app = Ursina(vsync=True)  # Create the Ursina app, vsync on to cap at monitor refresh (60 FPS target)
window.color = color.cyan  # Sky/background color

# Terrain generation
terrain_heights = [[0]*TERRAIN_RESOLUTION for _ in range(TERRAIN_RESOLUTION)]
height_amp = 10.0  # maximum height amplitude
freq = 0.1         # frequency for height variation (lower -> smoother hills)
# Generate heights using simple sin/cos based noise (could use Perlin for better results)
for ix in range(TERRAIN_RESOLUTION):
    for iz in range(TERRAIN_RESOLUTION):
        # Coordinates centered at 0
        x = ix - TERRAIN_RESOLUTION//2
        z = iz - TERRAIN_RESOLUTION//2
        # Example height function: sum of two sine waves
        h = (math.sin(x*freq) + math.cos(z*freq)) * (height_amp/2)
        # Add a circular falloff towards edges (optional, to avoid steep edges)
        dist_to_center = math.sqrt(x*x + z*z)
        if dist_to_center > TERRAIN_RESOLUTION*0.4:
            # lower the edges gradually to zero at boundary
            falloff = (dist_to_center - TERRAIN_RESOLUTION*0.4) / (TERRAIN_RESOLUTION*0.1)
            falloff = min(falloff, 1)
            h *= (1 - falloff)
        terrain_heights[iz][ix] = h

# Create the terrain entity using the Terrain mesh from height values
terrain_entity = Entity(
    model=Terrain(height_values=terrain_heights), 
    color=TERRAIN_COLOR, 
    scale=(WORLD_SIZE*2, 1, WORLD_SIZE*2),  # Scale X and Z to world size, Y=1 (we already have height in values)
    collider='mesh'
)
# The terrain's height variation is baked into the model by Terrain. 
# We scaled X,Z to WORLD_SIZE*2 so that index range maps to coordinate range roughly.

# Platform generation
platforms = []
num_platforms = 10
for i in range(num_platforms):
    # Random position within world bounds
    px = random.uniform(-WORLD_SIZE*0.8, WORLD_SIZE*0.8)
    pz = random.uniform(-WORLD_SIZE*0.8, WORLD_SIZE*0.8)
    # Height at that position from terrain_heights (need to map coords to array indices)
    # Convert world coords to terrain_heights index:
    tx = int((px / (WORLD_SIZE*2) + 0.5) * (TERRAIN_RESOLUTION-1))
    tz = int((pz / (WORLD_SIZE*2) + 0.5) * (TERRAIN_RESOLUTION-1))
    base_y = terrain_heights[tz][tx] * terrain_entity.scale_y  # actual world height
    # Place platform somewhat above that
    py = base_y + random.uniform(5, 15)
    # Create a flat cube platform
    platform = Entity(model='cube', color=color.lime, scale=(random.uniform(3,6), 0.5, random.uniform(3,6)),
                      position=(px, py, pz), collider='box')
    platforms.append(platform)

# Rail generation
rails = []  # store rail segment entities for reference
# Create one example rail connecting two random platforms (if at least 2 exist)
if len(platforms) >= 2:
    p1 = platforms[0].position
    p2 = platforms[1].position
    # We will make a slight curve: include a midpoint higher than both
    mid = (p1 + p2) / 2
    mid_y = max(p1.y, p2.y) + 5
    mid = Vec3(mid.x, mid_y, mid.z)
    rail_path = [p1 + Vec3(0,1,0), mid, p2 + Vec3(0,1,0)]  # a simple 3-point path (slightly above platform centers)
    # Create segments along path
    num_segments = 10
    for i in range(num_segments):
        t = i / (num_segments - 1)
        # interpolate along first half and second half of path for simplicity (two linear segments):
        if t <= 0.5:
            # between p1 and mid
            t2 = t / 0.5
            point_a = rail_path[0]
            point_b = rail_path[1]
            seg_pos = point_a + (point_b - point_a) * t2
        else:
            t2 = (t - 0.5) / 0.5
            point_a = rail_path[1]
            point_b = rail_path[2]
            seg_pos = point_a + (point_b - point_a) * t2
        # Create a small segment (a thin cylinder) at this point, oriented roughly along the path
        seg = Entity(model='cylinder', color=RAIL_COLOR, scale=(0.2, 1, 0.2), position=seg_pos)
        # Orient the segment:
        # Determine direction vector (pointing to next point or previous if last segment)
        if i < num_segments - 1:
            # look towards next segment position (which would be computed at t + step)
            next_t = (i+1) / (num_segments - 1)
            if next_t <= 0.5:
                t3 = next_t / 0.5
                next_pos = rail_path[0] + (rail_path[1] - rail_path[0]) * t3
            else:
                t3 = (next_t - 0.5) / 0.5
                next_pos = rail_path[1] + (rail_path[2] - rail_path[1]) * t3
        else:
            # last segment, look towards previous
            prev_t = (i-1) / (num_segments - 1)
            if prev_t <= 0.5:
                t3 = prev_t / 0.5
                next_pos = rail_path[0] + (rail_path[1] - rail_path[0]) * t3
            else:
                t3 = (prev_t - 0.5) / 0.5
                next_pos = rail_path[1] + (rail_path[2] - rail_path[1]) * t3
        direction = (next_pos - seg_pos).normalized()
        # Set rotation: point the segment's up axis along the direction vector
        # The cylinder's default orientation is vertical (up axis = its height axis).
        # We find the rotation that aligns (0,1,0) to the direction vector:
        seg.look_at(seg_pos + direction)  # align forward (z) with direction
        seg.rotation_x -= 90  # adjust rotation: now the cylinder's up axis (which was Y) aligns with forward direction
        # Above: we oriented the forward to direction, but want the cylinder's height axis to align. 
        # We rotate by -90 around X to swing the cylinder up axis (Y) into the forward direction.
        # This is a quick hack; ideally we would use quaternion rotations.
        seg.scale_y = (next_pos - seg_pos).length() * 0.5 + 0.1  # stretch segment length to roughly half distance to next
        seg.collider = None  # rail segments themselves might not need collider; we'll use a trigger box for the rail path
        rails.append(seg)
    # Rail trigger (invisible): a long thin box along the rail path for detecting player contact
    rail_trigger = Entity(position=rail_path[1], model='cube', visible=False,
                          scale=(1,1, (p2 - p1).length() + 5), collider='box')
    # Rough alignment of trigger:
    rail_trigger.look_at(p2)
    rail_trigger.rotation_x = 0  # keep it horizontal
    rails.append(rail_trigger)
else:
    rail_trigger = None

# Rings generation
rings = []
num_rings = 50
for i in range(num_rings):
    rx = random.uniform(-WORLD_SIZE*0.9, WORLD_SIZE*0.9)
    rz = random.uniform(-WORLD_SIZE*0.9, WORLD_SIZE*0.9)
    # get terrain height at (rx, rz)
    tx = int((rx / (WORLD_SIZE*2) + 0.5) * (TERRAIN_RESOLUTION-1))
    tz = int((rz / (WORLD_SIZE*2) + 0.5) * (TERRAIN_RESOLUTION-1))
    base_h = terrain_heights[tz][tx] * terrain_entity.scale_y
    ry = base_h + random.uniform(1, 3)  # a bit above ground
    ring = Entity(model='torus', color=RING_COLOR, scale=1, position=(rx, ry, rz), collider='box')
    # Rotate ring to face outward (so it's standing vertically):
    ring.rotation_x = 90
    rings.append(ring)

# Speed boost pads generation
boost_pads = []
for i in range(5):
    bx = random.uniform(-WORLD_SIZE*0.7, WORLD_SIZE*0.7)
    bz = random.uniform(-WORLD_SIZE*0.7, WORLD_SIZE*0.7)
    tx = int((bx / (WORLD_SIZE*2) + 0.5) * (TERRAIN_RESOLUTION-1))
    tz = int((bz / (WORLD_SIZE*2) + 0.5) * (TERRAIN_RESOLUTION-1))
    base_h = terrain_heights[tz][tx] * terrain_entity.scale_y
    by = base_h + 0.1  # just above ground
    pad = Entity(model='cube', color=BOOST_PAD_COLOR, scale=(2,0.1,2), position=(bx, by, bz), collider='box')
    # Orient pad to boost in some direction (for simplicity, face toward world center or a random angle)
    angle = random.choice([0,90,180,270])
    pad.rotation_y = angle
    boost_pads.append(pad)

# Jump pads (springs) generation
jump_pads = []
for i in range(5):
    jx = random.uniform(-WORLD_SIZE*0.7, WORLD_SIZE*0.7)
    jz = random.uniform(-WORLD_SIZE*0.7, WORLD_SIZE*0.7)
    tx = int((jx / (WORLD_SIZE*2) + 0.5) * (TERRAIN_RESOLUTION-1))
    tz = int((jz / (WORLD_SIZE*2) + 0.5) * (TERRAIN_RESOLUTION-1))
    base_h = terrain_heights[tz][tx] * terrain_entity.scale_y
    jy = base_h + 0.5
    pad = Entity(model='cone', color=JUMP_PAD_COLOR, scale=1, position=(jx, jy, jz), collider='box')
    # Make sure the cone is upright (pointing up)
    pad.rotation_x = 0
    jump_pads.append(pad)

# Player (Sonic) entity and controller
class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='sphere',
            color=PLAYER_COLOR,
            scale=1,
            collider='sphere',
            **kwargs
        )
        self.velocity = Vec3(0,0,0)
        self.on_ground = False
        self.on_rail = False
        self.rail_direction = Vec3(0,0,0)
        self.rail_entity = None  # which rail trigger we're on

    def update(self):
        # Handle movement input
        move_dir = Vec3(0, 0, 0)
        # Determine forward direction for movement (on ground, aligned with camera's forward on XZ plane)
        # We use camera.forward but zero out its y to prevent moving into ground when camera is angled
        cam_forward = Vec3(camera.forward.x, 0, camera.forward.z).normalized()
        cam_right = Vec3(camera.right.x, 0, camera.right.z).normalized()
        # Use WASD for movement
        if held_keys['w'] or held_keys['up arrow']:
            move_dir += cam_forward
        if held_keys['s'] or held_keys['down arrow']:
            move_dir -= cam_forward
        if held_keys['a'] or held_keys['left arrow']:
            move_dir -= cam_right
        if held_keys['d'] or held_keys['right arrow']:
            move_dir += cam_right
        move_dir = move_dir.normalized()  # only direction (length 1 or 0)
        # Apply acceleration or friction
        if self.on_ground or self.on_rail:
            # On ground/rail: full control
            if move_dir != Vec3(0,0,0):
                # Accelerate in desired direction (project current velocity on move_dir maybe for smoother turning)
                target_speed_vec = move_dir * MAX_SPEED
                # Increment velocity towards target_speed_vec
                self.velocity.x = lerp(self.velocity.x, target_speed_vec.x, ACCELERATION * time.dt)
                self.velocity.z = lerp(self.velocity.z, target_speed_vec.z, ACCELERATION * time.dt)
            else:
                # No input: apply friction (slow down)
                speed = Vec3(self.velocity.x, 0, self.velocity.z)
                new_speed = speed - speed.normalized() * FRICTION * time.dt
                # Stop if speed is small
                if speed.length() < 0.5:
                    new_speed = Vec3(0,0,0)
                self.velocity.x = new_speed.x
                self.velocity.z = new_speed.z
        else:
            # In air: reduced control
            if move_dir != Vec3(0,0,0):
                self.velocity.x += move_dir.x * ACCELERATION * AIR_CONTROL * time.dt
                self.velocity.z += move_dir.z * ACCELERATION * AIR_CONTROL * time.dt
                # Clamp horizontal speed in air to MAX_SPEED (not to exceed Sonic's top speed)
                horizontal_speed = math.sqrt(self.velocity.x**2 + self.velocity.z**2)
                if horizontal_speed > MAX_SPEED:
                    factor = MAX_SPEED / horizontal_speed
                    self.velocity.x *= factor
                    self.velocity.z *= factor
            # Apply slight air drag (optional, to avoid endless gliding)
            self.velocity.x *= (1 - 0.1 * time.dt)
            self.velocity.z *= (1 - 0.1 * time.dt)
        # Jump input
        if held_keys['space']:
            # If on ground or on rail, allow jump
            if self.on_ground or self.on_rail:
                self.velocity.y = JUMP_FORCE
                self.on_ground = False
                if self.on_rail:
                    # Jumping off a rail disengages it
                    self.on_rail = False
                    self.rail_entity = None

        # Gravity (only if not on rail)
        if not self.on_rail:
            self.velocity.y -= GRAVITY * time.dt

        # Move player by velocity
        self.position += self.velocity * time.dt

        # Loop world: wrap around boundaries
        if self.x > WORLD_SIZE:
            self.x = -WORLD_SIZE
        elif self.x < -WORLD_SIZE:
            self.x = WORLD_SIZE
        if self.z > WORLD_SIZE:
            self.z = -WORLD_SIZE
        elif self.z < -WORLD_SIZE:
            self.z = WORLD_SIZE

        # Terrain collision/ground detection:
        # Find height of terrain under player’s x,z:
        tx = int(((self.x / (WORLD_SIZE*2)) + 0.5) * (TERRAIN_RESOLUTION-1))
        tz = int(((self.z / (WORLD_SIZE*2)) + 0.5) * (TERRAIN_RESOLUTION-1))
        tx = max(0, min(TERRAIN_RESOLUTION-1, tx))
        tz = max(0, min(TERRAIN_RESOLUTION-1, tz))
        terrain_height = terrain_heights[tz][tx] * terrain_entity.scale_y
        # If below terrain, push up to surface:
        if self.y < terrain_height:
            self.y = terrain_height
            self.velocity.y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Platform collision: simple approach, check each platform
        for plat in platforms:
            # If player is above platform and within its horizontal bounds and close in height, stand on it
            # Platform bounds:
            halfx = plat.scale_x * 0.5
            halfz = plat.scale_z * 0.5
            if (plat.x - halfx <= self.x <= plat.x + halfx) and (plat.z - halfz <= self.z <= plat.z + halfz):
                plat_top = plat.y + plat.scale_y * 0.5  # since origin is center
                if self.y < plat_top + 2 and self.y > plat_top - 5 and self.velocity.y < 0:
                    # player is landing on platform
                    self.y = plat_top
                    self.velocity.y = 0
                    self.on_ground = True

        # Rail interaction
        if rail_trigger:
            if self.intersects(rail_trigger).hit and not self.on_rail:
                # Player got onto the rail trigger
                self.on_rail = True
                self.rail_entity = rail_trigger
                # Determine direction along rail: we can use the rail_trigger's orientation (forward)
                # If player's velocity dot trigger.forward is positive, go forward, else backward:
                dir_sign = 1 if self.velocity.dot(rail_trigger.forward) >= 0 else -1
                self.rail_direction = rail_trigger.forward * dir_sign * 20  # give a set speed along rail
                # Align player to rail (optional): we could rotate the player to face along rail
                self.rotation_y = rail_trigger.rotation_y
                # Nullify gravity while on rail (done by skipping gravity above)
                self.velocity.y = 0
            if self.on_rail:
                # Slide along rail
                self.position += rail_trigger.forward * 20 * time.dt  # move at constant speed along rail
                self.velocity = rail_trigger.forward * 20  # maintain velocity along rail for when leaving
                # Check if reached end of rail (roughly if player is near either end point of trigger)
                # We can compute distance from the center of trigger; if > half length of trigger + buffer, end rail.
                trigger_length = rail_trigger.scale_z
                dist_from_center = abs((self.position - rail_trigger.position).dot(rail_trigger.forward))
                if dist_from_center > trigger_length*0.5:
                    # left the rail trigger region
                    self.on_rail = False
                    self.rail_entity = None
        # Rings collection
        for ring in rings:
            if ring.enabled and self.intersects(ring).hit:
                # Collect ring
                ring.enabled = False
                # (We could increment a score counter here; for now, just disable ring)
        # Speed boost pads
        for pad in boost_pads:
            if self.intersects(pad).hit:
                # Apply boost in pad's forward direction
                # pad.forward gives direction of its local z-axis
                boost_dir = Vec3(pad.forward.x, 0, pad.forward.z).normalized()
                self.velocity.x = boost_dir.x * BOOST_SPEED
                self.velocity.z = boost_dir.z * BOOST_SPEED
                # Small upward nudge to keep on ground
                self.velocity.y = 2
        # Jump pads
        for pad in jump_pads:
            if self.intersects(pad).hit:
                # Launch upward
                self.velocity.y = JUMP_FORCE * 1.5  # a stronger jump
                # Optionally, slight forward push if needed (e.g., along world forward)
                # Here we won't add forward push unless needed for gameplay.
                self.on_ground = False

        # Ensure player does not go below world bottom (in case of falling off things)
        if self.y < -50:
            # Respawn at start if fell out of world bounds (for safety)
            self.position = (0, terrain_heights[TERRAIN_RESOLUTION//2][TERRAIN_RESOLUTION//2] * terrain_entity.scale_y + 5, 0)
            self.velocity = Vec3(0,0,0)
            self.on_ground = False
            self.on_rail = False

# Create player and camera
player = Player(position=(0, terrain_heights[TERRAIN_RESOLUTION//2][TERRAIN_RESOLUTION//2] * terrain_entity.scale_y + 1, 0))
# Attach a smooth follow camera
camera.add_script(SmoothFollow(target=player, offset=[0, 5, -20], speed=4))
# Optionally, disable mouse control of camera if any (to lock camera behind player)
mouse.locked = False
# Turn off Ursina's default camera controls if active (EditorCamera etc. is not enabled by default, so okay)

# UI or debugging
window.title = "Sonic Frontiers-style Test World"
window.fps_counter.enabled = True  # show FPS
# We could add a Text element to show collected rings count, but skipping for now.

app.run()
