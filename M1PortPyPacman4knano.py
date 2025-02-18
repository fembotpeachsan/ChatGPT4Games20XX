import pygame
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 30  # Each cell in the grid is 30x30 pixels
ROWS, COLS = HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Maze grid layout (1 = Wall, 0 = Empty path, 2 = Pellet, 3 = Ghost, 4 = Pac-Man)
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 3, 1, 0, 1, 3, 0, 0, 0, 0, 1, 3, 1, 0, 1, 3, 0, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Track pellet positions separately for score management
pellet_positions = [
    (row_idx, col_idx)
    for row_idx, row in enumerate(maze)
    for col_idx, cell in enumerate(row) if cell == 2
]

def display_message(screen, message, color=WHITE):
    """Display a centered message on the screen (used for life lost/game over)."""
    font = pygame.font.Font(None, 50)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(2000)

def get_positions():
    """Find initial positions of Pac-Man and ghosts in the maze."""
    pacman_pos = None
    ghost_positions = []
    for r_idx, row in enumerate(maze):
        for c_idx, cell in enumerate(row):
            if cell == 4:
                pacman_pos = [r_idx, c_idx]
            elif cell == 3:
                ghost_positions.append([r_idx, c_idx])
    return pacman_pos, ghost_positions

# Initialize game state variables
pacman_pos, ghost_positions = get_positions()
score = 0
lives = 3

def check_collision(screen):
    """Check for collisions between Pac-Man and any ghosts."""
    global lives, pacman_pos
    for ghost in ghost_positions:
        if pacman_pos == ghost:  # Pac-Man runs into a ghost
            lives -= 1
            if lives > 0:
                # Pac-Man loses a life
                display_message(screen, "You lost a life!", RED)
            else:
                # Game over
                display_message(screen, "Game Over!", RED)
                pygame.quit()
                exit()
            # Reset Pac-Man position after collision (if game continues)
            old_row, old_col = pacman_pos
            maze[old_row][old_col] = 0      # Clear old Pac-Man position
            pacman_pos = [1, 1]             # Reset Pac-Man to starting position
            maze[1][1] = 4                  # Place Pac-Man back in the maze

def draw_maze(screen):
    """Draw the maze, including walls, pellets, ghosts, and Pac-Man."""
    for r_idx, row in enumerate(maze):
        for c_idx, cell in enumerate(row):
            x, y = c_idx * GRID_SIZE, r_idx * GRID_SIZE
            if cell == 1:   # Wall
                pygame.draw.rect(screen, BLUE, (x, y, GRID_SIZE, GRID_SIZE))
            elif cell == 2: # Pellet
                pygame.draw.circle(screen, WHITE, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), 5)
            elif cell == 3: # Ghost
                pygame.draw.circle(screen, RED, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), 12)
            elif cell == 4: # Pac-Man
                pygame.draw.circle(screen, YELLOW, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), 12)

def move_pacman(direction, screen):
    """Move Pac-Man in the given direction if possible, update score and position."""
    global pacman_pos, score
    row, col = pacman_pos
    new_row, new_col = row, col
    # Determine new position based on direction
    if direction == "UP":
        new_row -= 1
    elif direction == "DOWN":
        new_row += 1
    elif direction == "LEFT":
        new_col -= 1
    elif direction == "RIGHT":
        new_col += 1
    # Move Pac-Man if the new cell is not a wall (1)
    if maze[new_row][new_col] != 1:
        # If there's a pellet at the new position, eat it and increase score
        if (new_row, new_col) in pellet_positions:
            pellet_positions.remove((new_row, new_col))
            score += 10
        # Update maze for Pac-Man movement
        maze[row][col] = 0            # Clear old position
        maze[new_row][new_col] = 4    # Move Pac-Man to new position
        pacman_pos = [new_row, new_col]
    # Check if this move caused a collision with a ghost
    check_collision(screen)

def move_ghosts(screen):
    """Move ghosts in random directions (if possible) and check collisions."""
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Possible movement offsets
    for ghost in ghost_positions:
        row, col = ghost
        random.shuffle(directions)  # Randomize direction order for each ghost
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            # Ghost can move into empty space or pellet space (0 or 2)
            if maze[new_row][new_col] in [0, 2]:
                # Clear the ghost's old position
                maze[row][col] = 0
                # If ghost was on a pellet, restore the pellet on the grid
                if (row, col) in pellet_positions:
                    maze[row][col] = 2
                # Update ghost's new position
                ghost[0], ghost[1] = new_row, new_col
                maze[new_row][new_col] = 3
                break  # Move to the next ghost after moving this one
    # After moving all ghosts, check for any collisions with Pac-Man
    check_collision(screen)

def main():
    """Main game loop: handles rendering, inputs, and game updates."""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Man (Beginner Version)")
    clock = pygame.time.Clock()
    # Game loop
    while True:
        screen.fill(BLACK)         # Clear the screen each frame
        draw_maze(screen)          # Draw all game elements
        # Render score and lives text
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 100, 10))
        # Move ghosts and update the display
        move_ghosts(screen)
        pygame.display.flip()
        # Event handling for quitting and arrow key presses
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move_pacman("UP", screen)
                elif event.key == pygame.K_DOWN:
                    move_pacman("DOWN", screen)
                elif event.key == pygame.K_LEFT:
                    move_pacman("LEFT", screen)
                elif event.key == pygame.K_RIGHT:
                    move_pacman("RIGHT", screen)
        clock.tick(5)  # Limit the game to 5 frames per second (controls speed)

if __name__ == "__main__":
    main()
