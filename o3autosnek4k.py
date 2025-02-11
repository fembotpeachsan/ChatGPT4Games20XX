import pygame
import sys
import random
import heapq
import numpy as np

# --- Mixer Pre-initialization for Mono Sound ---
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()  # Initialize pygame (this may reinitialize the mixer)

# ----- Configuration -----
CELL_SIZE = 20                   
GRID_WIDTH = 30                  
GRID_HEIGHT = 30                 
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10                         

# ----- Audio Generation Helper -----
def generate_sound(frequency, duration, volume=1.0, sample_rate=44100):
    """
    Generate a pygame Sound object containing a sine wave tone.
    If the mixer is stereo, convert the one-dimensional array to a two-dimensional array.
    """
    n_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    waveform = np.sin(2 * np.pi * frequency * t) * volume
    # Convert waveform to 16-bit signed integers
    waveform_integers = np.int16(waveform * 32767)
    
    # Check mixer initialization settings
    mixer_init = pygame.mixer.get_init()
    if mixer_init is not None:
        channels = mixer_init[2]
    else:
        channels = 2  # Assume stereo if not found

    if channels == 1:
        # Mono: keep as a one-dimensional array.
        pass
    else:
        # Stereo: duplicate the channel so that the array becomes 2D.
        waveform_integers = np.column_stack((waveform_integers, waveform_integers))
    
    sound = pygame.sndarray.make_sound(waveform_integers)
    return sound

# (The rest of your code remains the same...)
# ----- A* Pathfinding Helpers -----
def manhattan(cell, goal):
    return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])

def get_neighbors(cell, grid_width, grid_height):
    x, y = cell
    neighbors = []
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_width and 0 <= ny < grid_height:
            neighbors.append((nx, ny))
    return neighbors

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path[1:]

def find_path(snake, food, grid_width, grid_height):
    obstacles = set(snake[:-1])
    start = snake[0]
    goal = food

    open_set = []
    heapq.heappush(open_set, (manhattan(start, goal), 0, start))
    came_from = {}
    g_score = {start: 0}
    closed_set = set()

    while open_set:
        f, g, current = heapq.heappop(open_set)
        if current == goal:
            return reconstruct_path(came_from, current)
        if current in closed_set:
            continue
        closed_set.add(current)
        for neighbor in get_neighbors(current, grid_width, grid_height):
            if neighbor in obstacles and neighbor != goal:
                continue
            tentative_g = g + 1
            if neighbor in g_score and tentative_g >= g_score[neighbor]:
                continue
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g
            f_score = tentative_g + manhattan(neighbor, goal)
            heapq.heappush(open_set, (f_score, tentative_g, neighbor))
    return []

def get_safe_move(snake, grid_width, grid_height):
    head = snake[0]
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        new_head = (head[0] + dx, head[1] + dy)
        if 0 <= new_head[0] < grid_width and 0 <= new_head[1] < grid_height:
            if new_head not in snake:
                return new_head
    return None

def place_food(snake, grid_width, grid_height):
    while True:
        food = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
        if food not in snake:
            return food

# ----- Main Game Loop -----
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake Game with A* Pathfinding")
    clock = pygame.time.Clock()
    
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    food = place_food(snake, GRID_WIDTH, GRID_HEIGHT)
    
    # Load the sound effect for when the snake eats the food.
    eat_sound = generate_sound(440, 0.1, volume=0.5)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        path = find_path(snake, food, GRID_WIDTH, GRID_HEIGHT)
        if path:
            next_move = path[0]
        else:
            next_move = get_safe_move(snake, GRID_WIDTH, GRID_HEIGHT)
            if next_move is None:
                print("Game Over: No safe moves available!")
                running = False
                continue
        
        snake.insert(0, next_move)
        
        if next_move == food:
            food = place_food(snake, GRID_WIDTH, GRID_HEIGHT)
            eat_sound.play()
        else:
            snake.pop()
        
        if snake[0] in snake[1:]:
            print("Game Over: Snake collided with itself!")
            running = False
        
        screen.fill((0, 0, 0))
        for cell in snake:
            pygame.draw.rect(screen, (0, 255, 0),
                             (cell[0] * CELL_SIZE, cell[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, (255, 0, 0),
                         (food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
