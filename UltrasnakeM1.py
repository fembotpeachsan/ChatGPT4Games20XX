import sys
import time
from turtle import Screen, Turtle
from random import randint

# --- Game Settings (Nokia Style) ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
SQUARE_SIZE = 20
MAX_GRID_X = (SCREEN_WIDTH // 2 // SQUARE_SIZE) - 1
MIN_GRID_X = - (SCREEN_WIDTH // 2 // SQUARE_SIZE)
MAX_GRID_Y = (SCREEN_HEIGHT // 2 // SQUARE_SIZE) - 1
MIN_GRID_Y = - (SCREEN_HEIGHT // 2 // SQUARE_SIZE) + 1

BG_COLOR = "#c7f0d8"
SNAKE_COLOR = "black"
FOOD_COLOR = "black"
TEXT_COLOR = "black"

# --- Timing Settings ---
TARGET_FPS = 60.0
FRAME_DELAY = 1.0 / TARGET_FPS  # How long each frame *should* take

# --- Snake Speed Settings ---
INITIAL_MOVE_INTERVAL = 0.20  # Start with a move every 0.2 seconds
SPEED_INCREMENT = 0.005  # Reduce interval by this amount per food (faster)
MIN_MOVE_INTERVAL = 0.05  # Fastest snake move interval (20 moves/sec)

# --- Initialize Screen ---
screen = Screen()
screen.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
screen.title("Snake Classic - Smooth")
screen.bgcolor(BG_COLOR)
screen.tracer(0)  # Crucial: Turn off automatic screen updates

# --- Initialize Drawing Turtle (Pen) ---
pen = Turtle()
pen.speed(0)
pen.shape("square")
pen.shapesize(stretch_wid=SQUARE_SIZE/20, stretch_len=SQUARE_SIZE/20)
pen.color(SNAKE_COLOR)
pen.penup()
pen.hideturtle()

# --- Score Display ---
score_pen = Turtle()
score_pen.speed(0)
score_pen.color(TEXT_COLOR)
score_pen.penup()
score_pen.hideturtle()
score_pen.goto(0, SCREEN_HEIGHT / 2 - 40)
score = 0
score_pen.write(f"Score: {score}", align="center", font=("Courier", 18, "normal"))

# --- Direction Display ---
direction_pen = Turtle()
direction_pen.speed(0)
direction_pen.color(TEXT_COLOR)
direction_pen.penup()
direction_pen.hideturtle()
direction_pen.goto(-SCREEN_WIDTH / 2 + 80, SCREEN_HEIGHT / 2 - 40)

# --- Game Over Display ---
game_over_pen = Turtle()
game_over_pen.speed(0)
game_over_pen.color(TEXT_COLOR)
game_over_pen.penup()
game_over_pen.hideturtle()

# --- Snake ---
snake_body = [[0, 0], [-1, 0], [-2, 0]]
direction = "right"
pending_direction = direction  # Buffer for direction changes between moves
grow_snake = False
needs_redraw = True  # Flag to force initial draw

# --- Food ---
food_pos = [0, 0]

# --- Game Speed Control ---
current_move_interval = INITIAL_MOVE_INTERVAL

# --- Controls ---
controls_used = "None"
game_running = True  # Flag to track if game is still running

# --- Sound Functions ---
def play_beep():
    print('\a', end='', flush=True)

def play_food_sound():
    print('\a\a', end='', flush=True)

def play_game_over_sound():
    print('\a\a\a', end='', flush=True)
    print(" > GAME OVER < ")

# --- Helper Function to Draw Squares ---
def draw_square(turtle_pen, grid_x, grid_y, color):
    """Draws a filled square at the specified grid coordinates."""
    screen_x = grid_x * SQUARE_SIZE
    screen_y = grid_y * SQUARE_SIZE
    turtle_pen.goto(screen_x, screen_y)
    turtle_pen.color(color)
    turtle_pen.stamp()

# --- Generate Food ---
def generate_food():
    global food_pos, needs_redraw
    while True:
        food_pos[0] = randint(MIN_GRID_X, MAX_GRID_X)
        food_pos[1] = randint(MIN_GRID_Y, MAX_GRID_Y)
        is_on_snake = False
        for segment in snake_body:
            if segment == food_pos:
                is_on_snake = True
                break
        if not is_on_snake:
            break
    needs_redraw = True  # Signal that the food needs drawing

# --- Update Snake Logic (No Drawing Here) ---
def update_snake_logic():
    global snake_body, direction, food_pos, grow_snake, score, current_move_interval, needs_redraw, pending_direction, game_running

    # Apply pending direction change safely
    direction = pending_direction

    # Update direction display safely
    try:
        if game_running:  # Only attempt to update if game is still running
            direction_pen.clear()
            direction_pen.write(f"Direction: {direction} | Controls: {controls_used}", align="left", font=("Courier", 14, "normal"))
    except:
        # If there's an error with the turtle, we'll just skip the direction display
        pass

    head = snake_body[0][:]
    if direction == "right":
        head[0] += 1
    elif direction == "left":
        head[0] -= 1
    elif direction == "up":
        head[1] += 1
    elif direction == "down":
        head[1] -= 1

    # Check for collisions with walls
    if not (MIN_GRID_X <= head[0] <= MAX_GRID_X and MIN_GRID_Y <= head[1] <= MAX_GRID_Y):
        return "game_over"  # Return status

    # Check for collisions with self
    if head in snake_body[1:]:
        return "game_over"  # Return status

    ate_food = False
    if head == food_pos:
        grow_snake = True
        score += 10
        play_food_sound()
        current_move_interval = max(MIN_MOVE_INTERVAL, current_move_interval - SPEED_INCREMENT)
        ate_food = True
        # Score update needs redraw trigger
        try:
            if game_running:
                score_pen.clear()
                score_pen.write(f"Score: {score}", align="center", font=("Courier", 18, "normal"))
        except:
            pass  # Skip if there's an error with the turtle

    else:
        grow_snake = False

    snake_body.insert(0, head)

    if not grow_snake:
        snake_body.pop()  # Remove tail logical position

    needs_redraw = True  # Signal that the snake/food state changed

    if ate_food:
        generate_food()  # Generate new food logical position

    return "ok"  # Return status

# --- Draw Game State ---
def draw_game_state():
    """Clears previous drawings and redraws snake and food based on current state."""
    try:
        if game_running:
            pen.clearstamps()  # Efficiently remove all previous snake/food stamps

            # Draw food
            draw_square(pen, food_pos[0], food_pos[1], FOOD_COLOR)

            # Draw snake
            for segment in snake_body:
                draw_square(pen, segment[0], segment[1], SNAKE_COLOR)
    except:
        pass  # Skip if there's an error with the turtle

# --- Game Over ---
def game_over():
    global game_running
    game_running = False  # Set the flag to indicate game is over
    play_game_over_sound()
    try:
        game_over_pen.goto(0, 0)
        game_over_pen.write("GAME OVER", align="center", font=("Courier", 36, "bold"))
        screen.update()  # Show Game Over message
        time.sleep(3)
        screen.bye()  # Attempt to close turtle window gracefully
    except:
        pass  # Handle case where window may already be closed
    sys.exit()

# --- Change Direction (Stores pending change) ---
def set_pending_direction(new_dir, control_type="Arrow"):
    global pending_direction, direction, controls_used
    # Prevent the snake from reversing onto itself *immediately*
    if new_dir == "right" and direction != "left":
        pending_direction = new_dir
        controls_used = control_type
    elif new_dir == "left" and direction != "right":
        pending_direction = new_dir
        controls_used = control_type
    elif new_dir == "up" and direction != "down":
        pending_direction = new_dir
        controls_used = control_type
    elif new_dir == "down" and direction != "up":
        pending_direction = new_dir
        controls_used = control_type

# --- Keyboard Bindings ---
screen.listen()
# Arrow key controls
screen.onkeypress(lambda: set_pending_direction("right", "Arrow"), "Right")
screen.onkeypress(lambda: set_pending_direction("left", "Arrow"), "Left")
screen.onkeypress(lambda: set_pending_direction("up", "Arrow"), "Up")
screen.onkeypress(lambda: set_pending_direction("down", "Arrow"), "Down")
# WASD controls
screen.onkeypress(lambda: set_pending_direction("right", "WASD"), "d")
screen.onkeypress(lambda: set_pending_direction("left", "WASD"), "a")
screen.onkeypress(lambda: set_pending_direction("up", "WASD"), "w")
screen.onkeypress(lambda: set_pending_direction("down", "WASD"), "s")
# Also add capital letter binding for WASD
screen.onkeypress(lambda: set_pending_direction("right", "WASD"), "D")
screen.onkeypress(lambda: set_pending_direction("left", "WASD"), "A")
screen.onkeypress(lambda: set_pending_direction("up", "WASD"), "W")
screen.onkeypress(lambda: set_pending_direction("down", "WASD"), "S")

# --- Initial Setup ---
generate_food()  # Place the first food item (logical position)
# Initial draw is handled by needs_redraw flag

# Write initial direction display
direction_pen.write(f"Direction: {direction} | Controls: {controls_used}", align="left", font=("Courier", 14, "normal"))

# --- Main Game Loop (Fixed Timestep) ---
last_frame_time = time.perf_counter()  # Use perf_counter for higher precision timing
time_since_last_move = 0.0

while game_running:
    frame_start_time = time.perf_counter()
    delta_time = frame_start_time - last_frame_time
    last_frame_time = frame_start_time

    time_since_last_move += delta_time

    # --- Game Logic Update ---
    if time_since_last_move >= current_move_interval:
        game_status = update_snake_logic()
        if game_status == "game_over":
            break  # Exit loop immediately on game over condition
        time_since_last_move -= current_move_interval  # Subtract interval, don't reset to 0

    # --- Drawing ---
    if needs_redraw:
        draw_game_state()  # Redraw snake and food if state changed
        needs_redraw = False  # Reset flag

    # Update screen at fixed rate
    try:
        screen.update()
    except:
        game_running = False
        break

    # --- Frame Rate Control ---
    frame_end_time = time.perf_counter()
    elapsed_time = frame_end_time - frame_start_time
    sleep_time = FRAME_DELAY - elapsed_time
    if sleep_time > 0:
        time.sleep(sleep_time)  # Sleep to maintain target FPS

# --- Post-Loop ---
if not game_running:  # Ensure game_over runs if loop broken by game_status
    game_over()
