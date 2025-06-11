import tkinter as tk
import random
import threading
import time

CELL_SIZE = 30
COLUMNS = 10
ROWS = 20
DELAY = 300  # milliseconds

SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]],
}

COLORS = {
    'I': 'cyan',
    'O': 'yellow',
    'T': 'purple',
    'S': 'green',
    'Z': 'red',
    'J': 'blue',
    'L': 'orange',
    None: 'black'
}

# Tetris "vibe" - simple beeper melody (Tetris theme A) using winsound (Windows only)
def tetris_ost_vibe():
    try:
        import winsound
        melody = [
            (659, 150), (494, 75), (523, 75), (587, 150), (523, 75), (494, 75),
            (440, 150), (440, 75), (523, 75), (659, 150), (587, 75), (523, 75),
            (494, 225), (523, 75), (587, 150), (659, 150), (523, 75), (440, 75),
            (440, 150), (523, 75), (587, 75), (659, 150), (523, 75), (494, 75),
            (523, 150), (587, 75), (659, 75), (523, 225), (440, 75), (440, 75)
        ]
        while True:
            for freq, dur in melody:
                winsound.Beep(freq, dur)
    except Exception:
        pass  # If not on Windows or winsound fails, just skip

class Tetris:
    def __init__(self, root):
        self.root = root
        self.root.title("Tetris")
        self.root.resizable(False, False)  # Disable maximize button
        self.canvas = tk.Canvas(root, width=COLUMNS*CELL_SIZE, height=ROWS*CELL_SIZE, bg='black')
        self.canvas.pack()
        self.board = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.score = 0

        self.current_shape = None
        self.current_pos = None
        self.current_type = None

        self.game_over = False

        self.root.bind("<Key>", self.key_pressed)
        self.spawn_new_shape()
        self.update()

    def spawn_new_shape(self):
        self.current_type = random.choice(list(SHAPES.keys()))
        self.current_shape = [row[:] for row in SHAPES[self.current_type]]
        self.current_pos = [0, COLUMNS // 2 - len(self.current_shape[0]) // 2]
        if self.check_collision(self.current_shape, self.current_pos):
            self.game_over = True

    def rotate(self, shape):
        return [list(row) for row in zip(*shape[::-1])]

    def check_collision(self, shape, pos):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = pos[1] + x
                    new_y = pos[0] + y
                    if new_x < 0 or new_x >= COLUMNS or new_y < 0 or new_y >= ROWS:
                        return True
                    if self.board[new_y][new_x]:
                        return True
        return False

    def freeze_shape(self):
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.board[self.current_pos[0]+y][self.current_pos[1]+x] = self.current_type
        self.clear_lines()
        self.spawn_new_shape()

    def clear_lines(self):
        new_board = []
        lines_cleared = 0
        for row in self.board:
            if all(row):
                lines_cleared += 1
            else:
                new_board.append(row)
        for _ in range(lines_cleared):
            new_board.insert(0, [None for _ in range(COLUMNS)])
        self.board = new_board
        self.score += lines_cleared

    def move(self, dx, dy):
        new_pos = [self.current_pos[0]+dy, self.current_pos[1]+dx]
        if not self.check_collision(self.current_shape, new_pos):
            self.current_pos = new_pos

    def drop(self):
        while not self.check_collision(self.current_shape, [self.current_pos[0]+1, self.current_pos[1]]):
            self.current_pos[0] += 1
        self.freeze_shape()

    def key_pressed(self, event):
        if self.game_over:
            return
        if event.keysym == 'Left':
            self.move(-1, 0)
        elif event.keysym == 'Right':
            self.move(1, 0)
        elif event.keysym == 'Down':
            self.move(0, 1)
        elif event.keysym == 'Up':
            rotated = self.rotate(self.current_shape)
            if not self.check_collision(rotated, self.current_pos):
                self.current_shape = rotated
        elif event.keysym == 'space':
            self.drop()
        self.draw()

    def update(self):
        if not self.game_over:
            if not self.check_collision(self.current_shape, [self.current_pos[0]+1, self.current_pos[1]]):
                self.current_pos[0] += 1
            else:
                self.freeze_shape()
            self.draw()
            self.root.after(DELAY, self.update)
        else:
            self.draw_game_over()

    def draw(self):
        self.canvas.delete("all")
        # Draw board
        for y in range(ROWS):
            for x in range(COLUMNS):
                color = COLORS[self.board[y][x]]
                self.draw_cell(x, y, color)
        # Draw current shape
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_cell(self.current_pos[1]+x, self.current_pos[0]+y, COLORS[self.current_type])
        # Draw score
        self.canvas.create_text(5, 5, anchor='nw', fill='white', font=('Arial', 14), text=f"Score: {self.score}")

    def draw_cell(self, x, y, color):
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='gray')

    def draw_game_over(self):
        self.draw()
        self.canvas.create_text(COLUMNS*CELL_SIZE//2, ROWS*CELL_SIZE//2, text="GAME OVER", fill="white", font=('Arial', 24))

if __name__ == "__main__":
    root = tk.Tk()
    # Disable maximize button (Windows only)
    root.resizable(False, False)
    # Start Tetris OST "vibe" in background thread
    threading.Thread(target=tetris_ost_vibe, daemon=True).start()
    game = Tetris(root)
    root.mainloop()
