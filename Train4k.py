from ursina import *
import math

# Initialize the Ursina app
app = Ursina()

# Game variables
track_radius = 10       # Radius of the circular track
train_speed = 0         # Current speed of the train
max_speed = 1           # Maximum speed limit
acceleration = 0.01     # Rate of acceleration/deceleration
theta = 0               # Angular position on the track
stop_timer = 0          # Timer for passenger boarding at the station

# Load the train (using a placeholder cube; replace with 'train.obj')
train = Entity(model='cube', scale=(2, 1, 1), color=color.blue)

# Load the Shyguy conductor (placeholder cube; replace with 'shyguy.obj')
shyguy = Entity(model='cube', scale=0.2, position=(0, 1, 0), parent=train, color=color.red)

# Create the ground (Mario Kart-inspired grassy terrain)
ground = Entity(model='plane', scale=100, texture='grass', collider='box')

# Add a station at theta=0 (position=(track_radius, 0, 0))
station = Entity(model='cube', scale=(2, 1, 2), position=(track_radius, 0.5, 0), color=color.gray)

# Add Mario Kart-themed scenery (e.g., trees at 45-degree intervals)
for i in range(8):
    angle = i * 45
    pos = Vec3(
        (track_radius + 2) * math.cos(math.radians(angle)),
        0,
        (track_radius + 2) * math.sin(math.radians(angle))
    )
    Entity(model='cube', scale=(1, 2, 1), position=pos, color=color.green)  # Placeholder trees

# Set up the camera (initial position)
camera.position = (0, 5, -10)

# Create a speedometer UI
speed_text = Text(text='Speed: 0', position=(-0.5, 0.4), scale=2)

# Update function to handle game logic
def update():
    global theta, train_speed, stop_timer

    # Speed control with 'w' (accelerate) and 's' (brake)
    if held_keys['w']:
        train_speed += acceleration * time.dt
        if train_speed > max_speed:
            train_speed = max_speed
    if held_keys['s']:
        train_speed -= acceleration * time.dt
        if train_speed < 0:
            train_speed = 0

    # Update train's angular position (theta) based on speed
    theta += (train_speed / track_radius) * time.dt

    # Update train's position on the circular track
    train.position = Vec3(
        track_radius * math.cos(theta),
        0,
        track_radius * math.sin(theta)
    )

    # Orient the train to face the direction of movement
    direction = Vec3(-math.sin(theta), 0, math.cos(theta))
    train.rotation_y = math.degrees(math.atan2(direction.x, direction.z))

    # Update camera to follow the train from behind
    camera.position = train.position - direction.normalized() * 10 + Vec3(0, 5, 0)
    camera.look_at(train)

    # Update speedometer display
    speed_text.text = f'Speed: {train_speed:.2f}'

    # Station interaction: board passengers when stopped
    if train_speed == 0 and distance(train.position, station.position) < 1:
        stop_timer += time.dt
        if stop_timer > 2:  # After 2 seconds, add a passenger
            passenger = Entity(
                model='cube',
                position=(0, 1.5, 0),
                parent=train,
                color=color.yellow
            )  # Placeholder passenger
            stop_timer = 0  # Reset timer
    else:
        stop_timer = 0

# Run the game
app.run()
