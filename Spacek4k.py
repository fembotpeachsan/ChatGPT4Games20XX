

import tkinter as tk
import winsound
import threading

# Game configuration constants
WIDTH = 600
HEIGHT = 400
PLAYER_SPEED = 10       # pixels to move the player per key press
INVADER_STEP_X = 2      # horizontal movement step for invaders per frame
INVADER_DROP_Y = 20     # vertical drop for invaders when they reach a boundary
BULLET_SPEED = 5        # vertical movement step for bullet per frame
NUM_INVADER_ROWS = 3    # number of rows of invaders
NUM_INVADER_COLS = 6    # number of columns of invaders
INVADER_SIZE = 20       # size of each invader (width and height of the rectangle)
INVADER_X_SPACING = 40  # horizontal spacing between invaders (center to center)
INVADER_Y_SPACING = 30  # vertical spacing between invader rows
INVADER_START_X = 50    # initial x position of the leftmost invader
INVADER_START_Y = 50    # initial y position of the top row of invaders
BEEP_FREQ = 1000        # frequency for "beep" sound (Hz)
BOOP_FREQ = 500         # frequency for "boop" sound (Hz)
BEEP_DURATION = 100     # duration for "beep" sound (ms)
BOOP_DURATION = 100     # duration for "boop" sound (ms)

class SpaceInvadersGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Space Invaders")
        # Create canvas for drawing game elements
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
        self.canvas.pack()
        
        # Game state
        self.game_over = False
        self.invader_direction = 1  # 1 for moving right, -1 for moving left
        
        # Create player
        self.player_width = 30
        self.player_height = 20
        self.player_x = WIDTH / 2  # player horizontal center position
        self.player_y = HEIGHT - self.player_height - 10  # player top position (10 px above bottom)
        # Draw player as a rectangle
        self.player_id = self.canvas.create_rectangle(
            self.player_x - self.player_width/2,
            self.player_y,
            self.player_x + self.player_width/2,
            self.player_y + self.player_height,
            fill="green"
        )
        
        # Create invaders
        self.invaders = []  # list to store invader canvas item IDs
        for row in range(NUM_INVADER_ROWS):
            for col in range(NUM_INVADER_COLS):
                x = INVADER_START_X + col * INVADER_X_SPACING
                y = INVADER_START_Y + row * INVADER_Y_SPACING
                invader_id = self.canvas.create_rectangle(
                    x, y,
                    x + INVADER_SIZE, y + INVADER_SIZE,
                    fill="red", tags="invader"
                )
                self.invaders.append(invader_id)
        
        # Bullet state
        self.bullet_id = None  # canvas item ID for the bullet (None if no bullet active)
        self.bullet_x = 0
        self.bullet_y = 0
        
        # Bind keyboard events
        root.bind("<Left>", self.move_left)
        root.bind("<Right>", self.move_right)
        root.bind("<space>", self.shoot)
        
        # Start the game loop
        self.game_loop()
    
    def play_sound(self, frequency, duration):
        """Play a sound using winsound.Beep in a separate thread to avoid blocking."""
        # Only attempt to play sound if winsound is available (should be on Windows)
        if hasattr(winsound, "Beep"):
            threading.Thread(target=lambda: winsound.Beep(frequency, duration)).start()
    
    def move_left(self, event):
        """Handle left arrow key press to move player left."""
        if self.game_over:
            return  # ignore inputs if game is over
        # Calculate new position and ensure it doesn't go out of bounds
        left_edge = self.player_x - self.player_width/2
        if left_edge <= 0:
            return  # already at left edge, cannot move further left
        # Determine movement distance (clamp to edge if necessary)
        dx = -PLAYER_SPEED
        if left_edge + dx < 0:
            dx = -left_edge  # move exactly to the edge
        # Move player and update player_x
        self.canvas.move(self.player_id, dx, 0)
        self.player_x += dx
    
    def move_right(self, event):
        """Handle right arrow key press to move player right."""
        if self.game_over:
            return
        right_edge = self.player_x + self.player_width/2
        if right_edge >= WIDTH:
            return  # at right edge, cannot move further right
        dx = PLAYER_SPEED
        if right_edge + dx > WIDTH:
            dx = WIDTH - right_edge  # move exactly to the edge
        self.canvas.move(self.player_id, dx, 0)
        self.player_x += dx
    
    def shoot(self, event):
        """Handle spacebar press to shoot a bullet."""
        if self.game_over:
            return
        # Only shoot if no bullet is currently on screen
        if self.bullet_id is None:
            # Create a new bullet just above the player
            bullet_width = 4
            bullet_height = 10
            bullet_x1 = self.player_x - bullet_width/2
            bullet_x2 = self.player_x + bullet_width/2
            bullet_y1 = self.player_y  # top of player is starting bottom of bullet
            bullet_y2 = self.player_y - bullet_height
            # Draw bullet as a small rectangle (yellow color)
            self.bullet_id = self.canvas.create_rectangle(
                bullet_x1, bullet_y2, bullet_x2, bullet_y1, fill="yellow"
            )
            # Set bullet position state (bottom of bullet for tracking)
            self.bullet_x = self.player_x
            self.bullet_y = bullet_y1  # bottom of bullet
            # Play shooting sound (beep)
            self.play_sound(BEEP_FREQ, BEEP_DURATION)
    
    def game_loop(self):
        """Main game loop: updates game state and schedules the next frame."""
        if self.game_over:
            return  # stop the loop if game is over
        
        # Move bullet upward if it exists
        if self.bullet_id is not None:
            # Move the bullet up by BULLET_SPEED
            self.canvas.move(self.bullet_id, 0, -BULLET_SPEED)
            self.bullet_y -= BULLET_SPEED
            # Remove bullet if it goes off the screen
            if self.bullet_y < 0:
                # Bullet is off-screen, delete it
                self.canvas.delete(self.bullet_id)
                self.bullet_id = None
        
        # Determine invader movement (horizontal or drop)
        # Check if any invader is at a boundary for potential drop
        hit_edge = False
        leftmost_x = WIDTH
        rightmost_x = 0
        for invader in list(self.invaders):  # use list copy because we may modify invaders list later
            coords = self.canvas.coords(invader)
            if not coords:
                continue
            x1, y1, x2, y2 = coords
            if x1 < leftmost_x:
                leftmost_x = x1
            if x2 > rightmost_x:
                rightmost_x = x2
        # Decide if we need to drop and reverse direction
        if self.invader_direction == 1 and rightmost_x + INVADER_STEP_X >= WIDTH:
            hit_edge = True
        elif self.invader_direction == -1 and leftmost_x - INVADER_STEP_X <= 0:
            hit_edge = True
        
        if hit_edge:
            # Move all invaders down by INVADER_DROP_Y and reverse horizontal direction
            for invader in self.invaders:
                self.canvas.move(invader, 0, INVADER_DROP_Y)
            self.invader_direction *= -1
        else:
            # Move invaders horizontally
            for invader in self.invaders:
                self.canvas.move(invader, self.invader_direction * INVADER_STEP_X, 0)
        
        # Check for collisions between bullet and invaders
        if self.bullet_id is not None:
            # Get bullet's bounding box
            bx1, by1, bx2, by2 = self.canvas.coords(self.bullet_id)
            # Find any items overlapping the bullet
            hits = self.canvas.find_overlapping(bx1, by1, bx2, by2)
            for item in hits:
                # If an invader is hit
                if item in self.invaders:
                    # Remove the invader
                    self.invaders.remove(item)
                    self.canvas.delete(item)
                    # Delete the bullet
                    self.canvas.delete(self.bullet_id)
                    self.bullet_id = None
                    # Play "boop" sound for invader hit
                    self.play_sound(BOOP_FREQ, BOOP_DURATION)
                    break  # exit loop, one bullet can hit only one invader at a time
        
        # Check game over conditions
        if not self.invaders:
            # All invaders are destroyed, player wins
            self.game_over = True
            self.canvas.create_text(WIDTH/2, HEIGHT/2, fill="white", font=("Arial", 24),
                                     text="YOU WIN!")
        else:
            # If any invader has reached the level of the player (or bottom of screen)
            for invader in self.invaders:
                x1, y1, x2, y2 = self.canvas.coords(invader)
                if y2 >= self.player_y:  # invader bottom passed player's top
                    self.game_over = True
                    self.canvas.create_text(WIDTH/2, HEIGHT/2, fill="red", font=("Arial", 24),
                                             text="GAME OVER")
                    break
        
        # Schedule the next game loop iteration if game is not over
        if not self.game_over:
            self.root.after(20, self.game_loop)

# Initialize and start the game
if __name__ == "__main__":
    root = tk.Tk()
    game = SpaceInvadersGame(root)
    root.mainloop()
