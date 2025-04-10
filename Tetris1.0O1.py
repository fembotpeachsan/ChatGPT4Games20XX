import pygame
import sys
import random
import numpy as np

# -------------------------------------------------------------------
# Sound generation: beep with pure numpy data, no external files
# -------------------------------------------------------------------
def generate_sound(frequency=440, duration=0.1, volume=0.5):
    """ Generate a simple sine wave sound and return it as a pygame Sound. """
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    wave = np.sin(2 * np.pi * frequency * t)  # Sine wave

    # Convert to 16-bit data
    wave_integers = np.int16(wave * volume * 32767)
    # Make it stereo
    stereo_wave = np.column_stack((wave_integers, wave_integers))

    return pygame.sndarray.make_sound(stereo_wave)

# -------------------------------------------------------------------
# Tetris game
# -------------------------------------------------------------------
class Tetris:
    def __init__(self, width=10, height=20, tile_size=20):
        """
        :param width:     Number of columns in the Tetris grid
        :param height:    Number of rows in the Tetris grid
        :param tile_size: Pixel size of each tile in the grid
        """
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.top_left_x = 100  # Adjusted so the Tetris board is centered in the 600×400 window
        self.top_left_y = 20

        # Shapes (Tetrominoes): each is a list of 4 coordinate pairs
        # Coordinates refer to a 4x4 bounding box for each piece
        # (r, c) format
        self.shapes = [
            # S
            [[0,0], [0,1], [1,1], [1,2]],
            # Z
            [[0,2], [0,1], [1,1], [1,0]],
            # I
            [[0,1], [1,1], [2,1], [3,1]],
            # O
            [[0,0], [0,1], [1,0], [1,1]],
            # J
            [[0,0], [1,0], [2,0], [2,1]],
            # L
            [[0,1], [1,1], [2,1], [2,0]],
            # T
            [[0,1], [1,0], [1,1], [1,2]]
        ]
        # Colors for each shape (R, G, B)
        # Note: These are arbitrary, purely code-based; no images used.
        self.shape_colors = [
            (0, 255, 255),
            (255, 0, 255),
            (0, 255, 0),
            (255, 255, 0),
            (0, 0, 255),
            (255, 165, 0),
            (128, 0, 128)
        ]

        # Set up grid: each cell holds (r, g, b) or None for empty
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]

        # Current piece variables
        self.current_piece = None
        self.current_piece_color = None
        self.current_piece_x = 0  # Position in grid coordinates
        self.current_piece_y = 0

        # For game logic
        self.level = 1
        self.score = 0
        self.fall_time = 0
        self.fall_speed = 0.5  # lower => faster piece falling

        # Generate beep sounds
        self.lock_sound   = generate_sound(frequency=440, duration=0.05, volume=0.4)  # piece lock
        self.clear_sound  = generate_sound(frequency=550, duration=0.15, volume=0.4)  # line clear
        self.move_sound   = generate_sound(frequency=330, duration=0.03, volume=0.4)  # move/rotate

    def create_new_piece(self):
        """Select a random shape as the new falling piece."""
        shape = random.choice(self.shapes)
        color = self.shape_colors[self.shapes.index(shape)]
        self.current_piece = shape
        self.current_piece_color = color
        # piece spawns near top-center
        self.current_piece_x = self.width // 2 - 2
        self.current_piece_y = 0

    def rotate_shape(self, shape):
        """Rotate shape 90 degrees clockwise around (2x2 or 4x4) bounding box."""
        # Each coordinate [r,c] -> [c, -r] with an offset to keep them in bounding box
        # We can handle 4x4 bounding by max row/col = 3
        # (row, col) -> (col, 3 - row)
        rotated = [[c, 3 - r] for (r, c) in shape]
        # Then shift shape so it’s in the minimal bounding box. This helps with collisions.
        # We can skip the bounding shift if we want, but let's do a “re-center” approach:
        min_r = min(r for r, c in rotated)
        min_c = min(c for r, c in rotated)
        # shift so shape doesn’t go into negative grid positions
        rotated = [[r - min_r, c - min_c] for (r, c) in rotated]
        return rotated

    def valid_space(self, shape, offset_x, offset_y):
        """Check if a piece in a given position is valid (not colliding or out of bounds)."""
        for (row, col) in shape:
            new_x = col + offset_x
            new_y = row + offset_y
            # Check boundaries
            if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
                return False
            # Check if cell is occupied
            if self.grid[new_y][new_x] is not None:
                return False
        return True

    def lock_piece_in_grid(self):
        """Lock the current piece’s cells into the grid."""
        for (r, c) in self.current_piece:
            grid_x = self.current_piece_x + c
            grid_y = self.current_piece_y + r
            # place color in grid
            if 0 <= grid_y < self.height and 0 <= grid_x < self.width:
                self.grid[grid_y][grid_x] = self.current_piece_color

        self.lock_sound.play()
        # After locking, create new piece
        self.create_new_piece()
        # If new piece is immediately invalid => game over scenario
        if not self.valid_space(self.current_piece, self.current_piece_x, self.current_piece_y):
            # Reset grid, score, etc.
            self.reset_game()

    def clear_lines(self):
        """Check for full rows, remove them, and shift everything above down."""
        full_rows = []
        for row in range(self.height):
            if None not in self.grid[row]:
                full_rows.append(row)

        # Clear lines
        if full_rows:
            for row in full_rows:
                del self.grid[row]
                self.grid.insert(0, [None for _ in range(self.width)])
            # Score calculation: 1 line => 40 points, 2 => 100, 3 => 300, 4 => 1200
            line_cleared_count = len(full_rows)
            if line_cleared_count == 1:
                self.score += 40 * self.level
            elif line_cleared_count == 2:
                self.score += 100 * self.level
            elif line_cleared_count == 3:
                self.score += 300 * self.level
            elif line_cleared_count >= 4:
                self.score += 1200 * self.level
            self.clear_sound.play()

    def move_down(self):
        """Try moving the piece down by 1 row."""
        if self.valid_space(self.current_piece, self.current_piece_x, self.current_piece_y + 1):
            self.current_piece_y += 1
        else:
            # Lock piece and then clear lines
            self.lock_piece_in_grid()
            self.clear_lines()

    def move(self, dx):
        """Move piece left or right by dx if valid."""
        if self.valid_space(self.current_piece, self.current_piece_x + dx, self.current_piece_y):
            self.current_piece_x += dx
            self.move_sound.play()

    def rotate_current_piece(self):
        """Rotate the current falling piece."""
        rotated = self.rotate_shape(self.current_piece)
        if self.valid_space(rotated, self.current_piece_x, self.current_piece_y):
            self.current_piece = rotated
            self.move_sound.play()

    def reset_game(self):
        """Reset everything for a new game."""
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.score = 0
        self.level = 1
        self.create_new_piece()

    def draw_window(self, surface):
        # Background fill
        surface.fill((0, 0, 0))

        # Title
        font = pygame.font.SysFont('Courier', 30, bold=True)
        label = font.render("TETRIS CLONE", True, (255, 255, 255))
        surface.blit(label, (self.top_left_x + 40, 0))

        # Draw current score
        score_label = font.render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(score_label, (self.top_left_x + 40, 340))

        # Draw the grid with locked pieces
        for row in range(self.height):
            for col in range(self.width):
                cell_color = self.grid[row][col]
                if cell_color:
                    pygame.draw.rect(
                        surface,
                        cell_color,
                        (
                            self.top_left_x + col * self.tile_size,
                            self.top_left_y + row * self.tile_size,
                            self.tile_size,
                            self.tile_size
                        )
                    )

        # Draw the current falling piece
        if self.current_piece is not None:
            for (r, c) in self.current_piece:
                x = self.top_left_x + (self.current_piece_x + c) * self.tile_size
                y = self.top_left_y + (self.current_piece_y + r) * self.tile_size
                pygame.draw.rect(
                    surface,
                    self.current_piece_color,
                    (x, y, self.tile_size, self.tile_size)
                )

        # Draw horizontal/vertical lines for the play area
        # This helps visualize the Tetris grid
        for i in range(self.height + 1):
            pygame.draw.line(
                surface,
                (128, 128, 128),
                (self.top_left_x, self.top_left_y + i * self.tile_size),
                (self.top_left_x + self.width * self.tile_size, self.top_left_y + i * self.tile_size)
            )
        for j in range(self.width + 1):
            pygame.draw.line(
                surface,
                (128, 128, 128),
                (self.top_left_x + j * self.tile_size, self.top_left_y),
                (self.top_left_x + j * self.tile_size, self.top_left_y + self.height * self.tile_size)
            )

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
def main():
    pygame.init()
    # Initialize sound
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    # Create the window: 600x400
    width, height = 600, 400
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Tetris Clone")

    clock = pygame.time.Clock()

    game = Tetris(width=10, height=20, tile_size=20)
    game.create_new_piece()

    running = True
    fall_timer = 0

    while running:
        dt = clock.tick(60) / 1000.0  # delta time in seconds
        fall_timer += dt

        # Check events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move(-1)
                elif event.key == pygame.K_RIGHT:
                    game.move(1)
                elif event.key == pygame.K_DOWN:
                    game.move_down()
                elif event.key == pygame.K_UP:
                    game.rotate_current_piece()

        # Automatically move piece down
        if fall_timer > game.fall_speed:
            game.move_down()
            fall_timer = 0

        # Draw
        game.draw_window(screen)
        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
