# test1_eatari_full_snake.py
import tkinter as tk
import pygame
import random
import numpy as np
import threading
import os
import sys

# -----------------------
#       SETTINGS
# -----------------------
WIDTH, HEIGHT = 600, 400    # Canvas size
GRID = 20                   # Size of each square in the grid
BASE_SPEED = 10             # Base speed for the "Normal" difficulty (ticks/sec)
OBSTACLE_COUNT = 8          # Number of random obstacles
HIGH_SCORE_FILE = "snake_highscore.txt"

# For storing user choices from the menu:
GAME_DIFFICULTY = "Normal"  # "Easy", "Normal", "Hard"
WALL_MODE = "Classic"       # "Classic" (with collisions) or "Wrap"

# Attempt to initialize pygame.mixer for sound:
try:
    pygame.mixer.init()
    SOUND = True
except:
    SOUND = False

# -----------------------
#     SOUND FUNCTION
# -----------------------
def beep(freq=200, duration=0.2):
    """
    Generate a sine wave beep at `freq` Hz for `duration` seconds using pygame.
    """
    if not SOUND:
        return
    sr = 44100
    samples = int(sr * duration)
    t = np.linspace(0, duration, samples, False)
    wave = (np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)
    buf = np.zeros((samples, 2), dtype=np.int16)
    buf[:, 0] = wave
    buf[:, 1] = wave
    try:
        sound = pygame.sndarray.make_sound(buf)
        sound.play()
    except:
        pass

# -----------------------
#   HIGH SCORE HANDLING
# -----------------------
def get_highscore():
    """
    Return the high score stored in HIGH_SCORE_FILE.
    If file doesn't exist or has invalid content, returns 0.
    """
    if not os.path.exists(HIGH_SCORE_FILE):
        return 0
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            value = f.read().strip()
            return int(value)
    except:
        return 0

def set_highscore(new_score):
    """
    If new_score is greater than the saved high score, update it.
    """
    current = get_highscore()
    if new_score > current:
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(new_score))

# -----------------------
#    SNAKE GAME CLASS
# -----------------------
class AtariSnake:
    def __init__(self, canvas, root):
        self.c = canvas
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.close_game)
        
        # Difficulty modifies speed:
        if GAME_DIFFICULTY == "Easy":
            self.speed = BASE_SPEED * 0.7
        elif GAME_DIFFICULTY == "Hard":
            self.speed = BASE_SPEED * 1.5
        else:
            self.speed = BASE_SPEED
        
        # Create initial snake:
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = "Right"
        
        # Score:
        self.score = 0
        self.highscore = get_highscore()
        
        # Obstacles:
        self.obstacles = self.make_obstacles(OBSTACLE_COUNT)

        # Normal Food + Special Food
        self.food = self.new_food()
        self.special_food = None
        self.special_food_active = False
        self.special_counter = 0  # countdown for special fruit existence
        
        # Game State
        self.playing = True
        self.paused = False
        
        # Start the game loop:
        self.run()

    def close_game(self):
        """
        Called when the window is closed.
        """
        self.playing = False
        self.root.destroy()

    def make_obstacles(self, count):
        """
        Create a list of random obstacle positions (rectangles are 1 grid wide).
        They won't overlap with the initial snake's body or the default snake spawn.
        """
        obstacles = []
        taken_positions = set(self.snake)
        # We'll ensure there's some room around the snake's spawn:
        for _ in range(count):
            while True:
                ox = random.randint(0, (WIDTH - GRID) // GRID) * GRID
                oy = random.randint(0, (HEIGHT - GRID) // GRID) * GRID
                if (ox, oy) not in taken_positions:
                    obstacles.append((ox, oy))
                    taken_positions.add((ox, oy))
                    break
        return obstacles

    def new_food(self):
        """
        Return a random position for food that isn't on the snake or obstacles.
        """
        while True:
            x = random.randint(0, (WIDTH - GRID) // GRID) * GRID
            y = random.randint(0, (HEIGHT - GRID) // GRID) * GRID
            if (x, y) not in self.snake and (x, y) not in self.obstacles:
                return (x, y)

    def spawn_special_food(self):
        """
        Occasionally spawns special food that may have special effect.
        It stays for some time, then disappears if not eaten.
        """
        # 10% chance to spawn special food after eating normal food:
        chance = random.random()
        if chance < 0.10 and not self.special_food_active:
            while True:
                x = random.randint(0, (WIDTH - GRID) // GRID) * GRID
                y = random.randint(0, (HEIGHT - GRID) // GRID) * GRID
                if (x, y) not in self.snake and (x, y) not in self.obstacles and (x, y) != self.food:
                    self.special_food = (x, y)
                    self.special_food_active = True
                    # special fruit stays for up to 100 ticks
                    self.special_counter = 100
                    break

    def draw(self):
        """
        Draw everything on the canvas:
        - snake
        - obstacles
        - normal food
        - special food
        - score
        - high score
        """
        self.c.delete("all")
        # Draw obstacles:
        for ox, oy in self.obstacles:
            self.c.create_rectangle(ox, oy, ox + GRID, oy + GRID, fill="gray25", outline="black")
        
        # Draw snake:
        for i, (x, y) in enumerate(self.snake):
            color = "lime" if i == 0 else "green"
            self.c.create_rectangle(x, y, x + GRID, y + GRID, fill=color, width=1)
        
        # Normal food:
        fx, fy = self.food
        self.c.create_rectangle(fx, fy, fx + GRID, fy + GRID, fill="red", outline="black")
        
        # Special food if active:
        if self.special_food_active and self.special_food is not None:
            sx, sy = self.special_food
            self.c.create_oval(sx, sy, sx + GRID, sy + GRID, fill="gold", outline="black")

        # Score and High Score text
        self.c.create_text(5, 5, anchor="nw", 
                           text=f"Score: {self.score}   Highscore: {self.highscore}", 
                           fill="white", font=("Courier", 12))

        # Paused display
        if self.paused:
            self.c.create_text(WIDTH//2, HEIGHT//2, text="PAUSED", fill="yellow", font=("Courier", 24))

    def update(self):
        """
        Update the snake's position, handle collisions, spawn special food, etc.
        """
        if self.paused or not self.playing:
            return

        # Move snake
        x, y = self.snake[0]
        if self.direction == "Up":
            y -= GRID
        elif self.direction == "Down":
            y += GRID
        elif self.direction == "Left":
            x -= GRID
        elif self.direction == "Right":
            x += GRID

        # Handle wrap or wall collisions:
        if WALL_MODE == "Wrap":
            x %= WIDTH
            y %= HEIGHT
        else:
            # Classic mode with walls:
            if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
                self.game_over()
                return

        head = (x, y)

        # Check if snake hits itself or an obstacle
        if head in self.snake or head in self.obstacles:
            self.game_over()
            return

        # Insert new head
        self.snake.insert(0, head)

        # Check if we ate normal food
        if head == self.food:
            self.score += 1
            beep(800, 0.1)
            self.food = self.new_food()
            # Possibly spawn special fruit:
            self.spawn_special_food()
        else:
            self.snake.pop()

        # Check if we ate special food
        if self.special_food_active and head == self.special_food:
            self.score += 3  # special fruit is worth 3 points
            beep(1200, 0.15)
            self.special_food_active = False
            self.special_food = None

        # Decrement special fruit timer if active
        if self.special_food_active:
            self.special_counter -= 1
            if self.special_counter <= 0:
                # Time out the special fruit
                self.special_food_active = False
                self.special_food = None

    def game_over(self):
        """
        Trigger game over state, show text, record high score.
        """
        self.playing = False
        beep(100, 0.5)
        # Update high score if needed
        set_highscore(self.score)
        self.highscore = get_highscore()
        # Show game over text with a prompt:
        self.c.create_text(WIDTH//2, HEIGHT//2, text="GAME OVER", fill="white", font=("Courier", 24))
        self.c.create_text(WIDTH//2, HEIGHT//2 + 30, text="Play Again? (Y/N)", fill="gray", font=("Courier", 16))
        self.root.bind("<KeyPress>", self.reset_prompt)

    def reset_prompt(self, e):
        """
        After game over, pressing Y restarts the game,
        pressing N (or Escape) quits the entire program.
        """
        key = e.keysym.lower()
        if key == 'y':
            self.root.destroy()
            main_game()
        elif key == 'n' or key == 'escape':
            self.root.destroy()
            sys.exit()  # quit the program

    def tick(self):
        """
        The main repeated loop: update -> draw -> schedule next tick.
        """
        if self.playing:
            self.update()
            self.draw()
        # If still playing or paused, keep ticking:
        self.c.after(int(1000 // self.speed), self.tick)

    def run(self):
        """
        Start the repeating tick function.
        """
        self.tick()

    def keys(self, e):
        """
        Handle key presses for movement and pausing.
        """
        if not self.playing:
            return

        k = e.keysym
        # Movement controls
        if k == "Up" and self.direction != "Down": 
            self.direction = "Up"
        elif k == "Down" and self.direction != "Up": 
            self.direction = "Down"
        elif k == "Left" and self.direction != "Right": 
            self.direction = "Left"
        elif k == "Right" and self.direction != "Left": 
            self.direction = "Right"

        # Pause toggle
        elif k.lower() == 'p':
            self.paused = not self.paused

        # Quit
        elif k == 'Escape':
            self.playing = False
            self.root.destroy()

# -----------------------
#     MENU FUNCTIONS
# -----------------------
def menu():
    """
    The initial menu screen where you pick difficulty and wall mode.
    Press Enter to start the game.
    """
    root = tk.Tk()
    root.title("ULTRA!Pong 0.x.x SNAKE - Menu")

    cv = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
    cv.pack()

    # We'll show some text instructions:
    title_text = cv.create_text(
        WIDTH//2, HEIGHT//4,
        text="ULTRA!Pong 0.x.x SNAKE",
        fill="lime", font=("Courier", 32)
    )

    # Menu options
    # Difficulty
    difficulties = ["Easy", "Normal", "Hard"]
    diff_index = 1  # default to "Normal"
    wall_modes = ["Classic", "Wrap"]
    wall_index = 0  # default to "Classic"

    diff_text = cv.create_text(
        WIDTH//2, HEIGHT//2 - 40,
        text=f"Difficulty: {difficulties[diff_index]}",
        fill="white", font=("Courier", 16)
    )
    wall_text = cv.create_text(
        WIDTH//2, HEIGHT//2,
        text=f"Wall Mode: {wall_modes[wall_index]}",
        fill="white", font=("Courier", 16)
    )

    instruction_text = cv.create_text(
        WIDTH//2, HEIGHT - 60,
        text="Use Up/Down to change difficulty\nLeft/Right to change wall mode\nPress ENTER to Start",
        fill="gray", font=("Courier", 12)
    )

    def redraw_text():
        cv.itemconfig(diff_text, text=f"Difficulty: {difficulties[diff_index]}")
        cv.itemconfig(wall_text, text=f"Wall Mode: {wall_modes[wall_index]}")

    def key_handler(e):
        nonlocal diff_index, wall_index

        if e.keysym == "Up":
            diff_index = (diff_index - 1) % len(difficulties)
            beep(300, 0.05)
            redraw_text()
        elif e.keysym == "Down":
            diff_index = (diff_index + 1) % len(difficulties)
            beep(300, 0.05)
            redraw_text()
        elif e.keysym == "Left":
            wall_index = (wall_index - 1) % len(wall_modes)
            beep(300, 0.05)
            redraw_text()
        elif e.keysym == "Right":
            wall_index = (wall_index + 1) % len(wall_modes)
            beep(300, 0.05)
            redraw_text()
        elif e.keysym == "Return":
            # Assign global settings:
            global GAME_DIFFICULTY, WALL_MODE
            GAME_DIFFICULTY = difficulties[diff_index]
            WALL_MODE = wall_modes[wall_index]
            root.destroy()
            main_game()
        elif e.keysym == 'Escape':
            root.destroy()

    root.bind("<KeyPress>", key_handler)
    root.mainloop()

def main_game():
    """
    Create the game window and start the AtariSnake instance.
    """
    win = tk.Tk()
    win.title("ULTRA!Pong 0.x.x SNAKE Engine")
    canvas = tk.Canvas(win, width=WIDTH, height=HEIGHT, bg="black")
    canvas.pack()
    game = AtariSnake(canvas, win)
    win.bind("<KeyPress>", game.keys)
    win.mainloop()

# -----------------------
#         BOOT
# -----------------------
if __name__ == "__main__":
    # Run the menu in a separate thread so we don't block if desired,
    # but typically you can just call menu() directly.
    threading.Thread(target=menu).start()
