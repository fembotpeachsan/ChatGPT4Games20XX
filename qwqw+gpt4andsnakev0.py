import tkinter as tk
from tkinter import ttk
import random

# Game dimensions
WIDTH = 600
HEIGHT = 400
DELAY = 100  # Initial delay in milliseconds

# Snake segments size
SNAKE_SIZE = 20

# Initial snake length
INITIAL_SNAKE_LENGTH = 3


class SnakeGame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Create canvas for the game board
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, background='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Initialize game variables
        self.snake = []
        self.food_pos = None
        self.score = 0
        self.game_over = False
        self.speed = DELAY

        # Direction variables (start moving to the right)
        self.direction = 'Right'
        self.next_direction = 'Right'

        # Place initial food
        self.place_food()

        # Initialize snake in the center
        start_x = WIDTH // 2
        start_y = HEIGHT // 2
        for i in range(INITIAL_SNAKE_LENGTH):
            x = start_x - i * SNAKE_SIZE
            y = start_y
            self.snake.append((x, y))

        # Draw initial snake
        self.draw_snake()

        # Bind keys for direction control
        self.parent.bind("<Up>", self.change_direction)
        self.parent.bind("<Down>", self.change_direction)
        self.parent.bind("<Left>", self.change_direction)
        self.parent.bind("<Right>", self.change_direction)

        # Display score
        self.score_text = self.canvas.create_text(10, 10, text=f"Score: {self.score}",
                                                  font=('Arial', 14), fill='white', anchor='nw')

        # Start the game loop
        self.after(self.speed, self.game_loop)

    def game_loop(self):
        if not self.game_over:
            self.direction = self.next_direction
            self.move_snake()
            self.check_collision()
            self.draw_snake()
            self.after(self.speed, self.game_loop)
        else:
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Game Over! Press R to Restart",
                                    font=('Arial', 24), fill='red')
            self.parent.bind("<r>", self.restart_game)

    def draw_snake(self):
        # Clear previous snake positions
        self.canvas.delete("snake")

        for pos in self.snake:
            x, y = pos
            self.canvas.create_rectangle(x, y, x + SNAKE_SIZE, y + SNAKE_SIZE,
                                         fill='green', tags="snake")

    def place_food(self):
        while True:
            x = random.randint(0, (WIDTH - SNAKE_SIZE) // SNAKE_SIZE) * SNAKE_SIZE
            y = random.randint(0, (HEIGHT - SNAKE_SIZE) // SNAKE_SIZE) * SNAKE_SIZE
            food = (x, y)
            if food not in self.snake:
                self.food_pos = food
                break
        self.draw_food()

    def draw_food(self):
        # Remove existing food
        self.canvas.delete("food")
        x, y = self.food_pos
        self.canvas.create_oval(x, y, x + SNAKE_SIZE, y + SNAKE_SIZE,
                                fill='red', tags="food")

    def move_snake(self):
        head_x, head_y = self.snake[0]
        if self.direction == 'Up':
            new_head = (head_x, head_y - SNAKE_SIZE)
        elif self.direction == 'Down':
            new_head = (head_x, head_y + SNAKE_SIZE)
        elif self.direction == 'Left':
            new_head = (head_x - SNAKE_SIZE, head_y)
        elif self.direction == 'Right':
            new_head = (head_x + SNAKE_SIZE, head_y)

        # Insert the new head
        self.snake.insert(0, new_head)

        # Check if food is eaten
        if self.snake[0] == self.food_pos:
            self.score += 1
            self.speed = max(50, self.speed - 2)  # Increase speed with a cap
            self.canvas.itemconfigure(self.score_text, text=f"Score: {self.score}")
            self.place_food()
        else:
            # Remove the tail segment
            self.snake.pop()

    def check_collision(self):
        head_x, head_y = self.snake[0]

        # Check collision with walls
        if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
            self.game_over = True
            return

        # Check collision with itself
        if self.snake[0] in self.snake[1:]:
            self.game_over = True

    def change_direction(self, event):
        new_direction = event.keysym
        opposites = {'Up': 'Down', 'Down': 'Up', 'Left': 'Right', 'Right': 'Left'}
        if new_direction in opposites and opposites[new_direction] != self.direction:
            self.next_direction = new_direction

    def restart_game(self, event):
        # Reset game variables
        self.snake = []
        self.food_pos = None
        self.score = 0
        self.game_over = False
        self.speed = DELAY
        self.direction = 'Right'
        self.next_direction = 'Right'

        # Reinitialize snake
        start_x = WIDTH // 2
        start_y = HEIGHT // 2
        for i in range(INITIAL_SNAKE_LENGTH):
            x = start_x - i * SNAKE_SIZE
            y = start_y
            self.snake.append((x, y))

        # Place food and redraw snake
        self.place_food()
        self.draw_snake()
        self.canvas.itemconfigure(self.score_text, text=f"Score: {self.score}")
        self.game_loop()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Snake Game")
    game = SnakeGame(root)
    game.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
