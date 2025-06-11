import math
import tkinter as tk
import pygame
import sys
import array

# Initialize pygame mixer for sound (use mono audio and small buffer to reduce lag/2D audio issues)
pygame.mixer.pre_init(44100, -16, 1, 512)
try:
    pygame.mixer.init()
except Exception as e:
    # If mixer fails to initialize (e.g., no audio device), disable sound
    pygame.mixer = None

# Function to generate a beep sound (sine wave) without external files
def generate_beep(frequency=1000, duration_ms=150, volume=16000):
    sample_rate = 44100
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = array.array('h')
    for i in range(n_samples):
        # Generate a sine wave at the given frequency
        sample = volume * math.sin(2 * math.pi * frequency * i / sample_rate)
        buf.append(int(sample))
    sound = None
    if pygame.mixer and pygame.mixer.get_init():
        try:
            sound = pygame.mixer.Sound(buffer=buf.tobytes())
        except Exception:
            try:
                sound = pygame.mixer.Sound(buf.tobytes())
            except Exception:
                sound = None
    return sound

# Create the game window
root = tk.Tk()
root.title("Breakout")
root.resizable(False, False)  # fixed size window
WIDTH, HEIGHT = 600, 400

# Create canvas for drawing
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
canvas.pack()

# Game constants
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 10
PADDLE_Y = HEIGHT - 30  # paddle vertical position
BALL_RADIUS = 5
initial_speed = 4.0  # initial ball speed (pixels per frame at 60 FPS)

# Game state
lives = 3
score = 0

# Create score display
score_text = canvas.create_text(
    5, 5, anchor='nw', fill="white", font=("Courier", 12),
    text=f"Score: {score}   Lives: {lives}"
)

# Set up bricks (8 rows, 14 columns as in original Breakout)
brick_rows = 8
brick_cols = 14
brick_width = 40
brick_height = 15
brick_margin_x = (WIDTH - brick_cols * brick_width) // 2  # center bricks
brick_margin_y = 50  # top margin for bricks
bricks = []

for i in range(brick_rows):
    # Determine brick color and point value by row (used for scoring/speed logic only)
    if i < 2:
        color = "red"; points = 7
    elif i < 4:
        color = "orange"; points = 5
    elif i < 6:
        color = "green"; points = 3
    else:
        color = "yellow"; points = 1

    y = brick_margin_y + i * brick_height
    for j in range(brick_cols):
        x = brick_margin_x + j * brick_width
        # Draw every brick in white, but keep its "color" for gameplay logic
        brick_id = canvas.create_rectangle(
            x, y, x + brick_width, y + brick_height,
            fill="white", outline=""
        )
        bricks.append({"id": brick_id, "x": x, "y": y, "color": color, "points": points})

# Create paddle
paddle_x = WIDTH / 2
paddle_id = canvas.create_rectangle(
    paddle_x - PADDLE_WIDTH/2, PADDLE_Y,
    paddle_x + PADDLE_WIDTH/2, PADDLE_Y + PADDLE_HEIGHT,
    fill="white"
)

# Create ball
ball_x = WIDTH / 2
ball_y = PADDLE_Y - BALL_RADIUS - 1
ball_id = canvas.create_oval(
    ball_x - BALL_RADIUS, ball_y - BALL_RADIUS,
    ball_x + BALL_RADIUS, ball_y + BALL_RADIUS,
    fill="white"
)

ball_dx = initial_speed
ball_dy = -initial_speed

bounce_count = 0
speed_increased_4 = False
speed_increased_12 = False
orange_hit = False
red_hit = False

# Prepare sounds
beep_paddle = generate_beep(frequency=500)
beep_brick = generate_beep(frequency=1000)

def play_sound(sound):
    if sound and pygame.mixer and pygame.mixer.get_init():
        try:
            sound.play()
        except Exception:
            pass

# Mouse movement event
def on_mouse_move(event):
    global paddle_x
    half = PADDLE_WIDTH / 2
    new_x = max(half, min(WIDTH - half, event.x))
    paddle_x = new_x
    canvas.coords(
        paddle_id,
        paddle_x - half, PADDLE_Y,
        paddle_x + half, PADDLE_Y + PADDLE_HEIGHT
    )

canvas.bind('<Motion>', on_mouse_move)
canvas.focus_set()

game_running = True
level = 1

def game_loop():
    global ball_x, ball_y, ball_dx, ball_dy, bounce_count
    global speed_increased_4, speed_increased_12, orange_hit, red_hit
    global score, lives, game_running, level

    if not game_running:
        return

    new_x = ball_x + ball_dx
    new_y = ball_y + ball_dy

    # Wall bounces
    if new_x - BALL_RADIUS < 0:
        new_x, ball_dx = BALL_RADIUS, -ball_dx; bounce_count += 1; play_sound(beep_paddle)
    elif new_x + BALL_RADIUS > WIDTH:
        new_x, ball_dx = WIDTH - BALL_RADIUS, -ball_dx; bounce_count += 1; play_sound(beep_paddle)
    if new_y - BALL_RADIUS < 0:
        new_y, ball_dy = BALL_RADIUS, -ball_dy; bounce_count += 1; play_sound(beep_paddle)

    # Paddle bounce
    if ball_dy > 0:
        pl, pt, pr, pb = canvas.coords(paddle_id)
        if new_y + BALL_RADIUS >= pt and ball_y + BALL_RADIUS <= pt:
            if new_x + BALL_RADIUS >= pl and new_x - BALL_RADIUS <= pr:
                new_y = pt - BALL_RADIUS
                speed = math.sqrt(ball_dx**2 + ball_dy**2)
                hit_pos = (new_x - (pl + pr)/2) / (PADDLE_WIDTH/2)
                hit_pos = max(-1, min(1, hit_pos))
                ball_dx = hit_pos * speed
                ball_dy = -math.sqrt(max(speed**2 - ball_dx**2, 0))
                bounce_count += 1
                play_sound(beep_paddle)

    # Brick collision
    hit_brick = None
    for brick in list(bricks):
        bx, by = brick["x"], brick["y"]
        if not (
            new_x + BALL_RADIUS < bx or new_x - BALL_RADIUS > bx + brick_width or
            new_y + BALL_RADIUS < by or new_y - BALL_RADIUS > by + brick_height
        ):
            hit_brick = brick
            bricks.remove(brick)
            canvas.delete(brick["id"])
            score += brick["points"]
            canvas.itemconfig(score_text, text=f"Score: {score}   Lives: {lives}")

            if brick["color"] == "orange" and not orange_hit:
                orange_hit = True
                ball_dx *= 1.1; ball_dy *= 1.1
            if brick["color"] == "red" and not red_hit:
                red_hit = True
                ball_dx *= 1.1; ball_dy *= 1.1

            # Bounce direction
            bl, bt = bx, by
            br_, bb = bx + brick_width, by + brick_height
            overlap_x = min(br_, new_x + BALL_RADIUS) - max(bl, new_x - BALL_RADIUS)
            overlap_y = min(bb, new_y + BALL_RADIUS) - max(bt, new_y - BALL_RADIUS)
            if overlap_x > 0 and overlap_y > 0:
                if overlap_x < overlap_y:
                    ball_dx = -ball_dx
                else:
                    ball_dy = -ball_dy
            else:
                ball_dy = -ball_dy

            play_sound(beep_brick)
            bounce_count += 1
            break

    # Handle all-bricks-cleared
    if hit_brick and len(bricks) == 0:
        if level == 1:
            level = 2
            for i in range(brick_rows):
                if i < 2:
                    color = "red"; points = 7
                elif i < 4:
                    color = "orange"; points = 5
                elif i < 6:
                    color = "green"; points = 3
                else:
                    color = "yellow"; points = 1
                y = brick_margin_y + i * brick_height
                for j in range(brick_cols):
                    x = brick_margin_x + j * brick_width
                    brick_id = canvas.create_rectangle(
                        x, y, x + brick_width, y + brick_height,
                        fill="white", outline=""
                    )
                    bricks.append({"id": brick_id, "x": x, "y": y, "color": color, "points": points})
        else:
            canvas.create_text(
                WIDTH/2, HEIGHT/2,
                text="YOU WIN!", fill="white", font=("Arial", 24)
            )
            game_running = False

    # Ball falls off bottom
    if new_y + BALL_RADIUS >= HEIGHT:
        lives -= 1
        canvas.itemconfig(score_text, text=f"Score: {score}   Lives: {lives}")
        if lives > 0:
            ball_x, ball_y = WIDTH/2, PADDLE_Y - BALL_RADIUS - 1
            ball_dx = initial_speed if ball_dx > 0 else -initial_speed
            ball_dy = -initial_speed
            canvas.coords(
                ball_id,
                ball_x - BALL_RADIUS, ball_y - BALL_RADIUS,
                ball_x + BALL_RADIUS, ball_y + BALL_RADIUS
            )
        else:
            canvas.create_text(
                WIDTH/2, HEIGHT/2,
                text="GAME OVER", fill="white", font=("Arial", 24)
            )
            game_running = False

        if game_running:
            root.after(16, game_loop)
        return

    # Speed increases at bounce thresholds
    if not speed_increased_4 and bounce_count >= 4:
        speed_increased_4 = True
        ball_dx *= 1.1; ball_dy *= 1.1
    if not speed_increased_12 and bounce_count >= 12:
        speed_increased_12 = True
        ball_dx *= 1.1; ball_dy *= 1.1

    # Update ball position
    ball_x, ball_y = new_x, new_y
    canvas.coords(
        ball_id,
        int(ball_x - BALL_RADIUS), int(ball_y - BALL_RADIUS),
        int(ball_x + BALL_RADIUS), int(ball_y + BALL_RADIUS)
    )

    if game_running:
        root.after(16, game_loop)

# Start loop & cleanup
root.after(16, game_loop)

def on_close():
    global game_running
    game_running = False
    try:
        pygame.mixer.quit()
    except Exception:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

if pygame.mixer and pygame.mixer.get_init():
    pygame.mixer.quit()
###### [] ChatGPT + Team Flames [] 20XX
