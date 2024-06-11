import tkinter as tk
from tkinter import messagebox

# Optimize Tkinter for M1 Mac (No guaranteed performance gain)
try:
    from ctypes import cdll
    cdll.LoadLibrary('libX11.so').XInitThreads()
except:
    pass 

class GeometryDashGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Geometry Dash")
        self.root.geometry("600x400")
        self.root.resizable(False, False) 

        # Menu (Consider simplifying if performance is critical)
        menubar = tk.Menu(root)
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Game Over", command=self.game_over)
        game_menu.add_command(label="Restart", command=self.restart_game)
        menubar.add_cascade(label="File", menu=game_menu)
        root.config(menu=menubar)

        # Canvas 
        self.canvas = tk.Canvas(root, bg='black', highlightthickness=0) # highlightthickness=0 for potential minor improvement
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Player 
        self.player = self.canvas.create_rectangle(50, 350, 70, 370, fill='red')

        # Bind keys
        root.bind("<space>", self.jump)

        # Variables
        self.jump_speed = -10
        self.gravity = 1
        self.player_speed = 0
        self.is_jumping = False

        # Start game loop
        self.update_game()

    def jump(self, event=None): # Allow jump to be called without an event
        if not self.is_jumping:
            self.player_speed = self.jump_speed
            self.is_jumping = True

    def game_over(self):
        if messagebox.showinfo("Game Over", "Game Over! Do you want to restart?"):
            self.restart_game()

    def restart_game(self):
        self.canvas.coords(self.player, 50, 350, 70, 370)
        self.player_speed = 0
        self.is_jumping = False

    def update_game(self):
        # Apply gravity
        self.player_speed += self.gravity
        self.canvas.move(self.player, 0, self.player_speed)

        # Check for landing
        pos = self.canvas.coords(self.player)
        if pos[3] >= 400:
            self.canvas.coords(self.player, pos[0], 380, pos[2], 400)
            self.player_speed = 0
            self.is_jumping = False

        # Continue updating the game
        self.root.after(16, self.update_game)  # 16ms for smoother ~60fps

if __name__ == "__main__":
    root = tk.Tk()
    game = GeometryDashGame(root)
    root.mainloop()
