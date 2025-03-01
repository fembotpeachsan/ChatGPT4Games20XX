import pygame
import random
import sys
import time
import math
import numpy as np

# Initialize pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (169, 169, 169)
DARK_GREEN = (0, 100, 0)

# Game settings
CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 15
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT + 40  # Extra space for score
FPS = 12

# Create the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Nokia Snake')
clock = pygame.time.Clock()

# Nokia-style Audio Engine
class AudioEngine:
    def __init__(self):
        self.sample_rate = 44100
        self.volume = 0.3
    
    def _create_sound(self, data):
        """Convert audio data to pygame Sound object"""
        sound = pygame.mixer.Sound(buffer=data)
        sound.set_volume(self.volume)
        return sound
    
    def _generate_tone(self, frequency, duration, volume=1.0, decay=1.0):
        """Generate a simple sine wave tone"""
        num_samples = int(self.sample_rate * duration)
        buf = np.zeros((num_samples, 2), dtype=np.float32)
        max_sample = 2**(16 - 1) - 1
        
        for s in range(num_samples):
            t = float(s) / self.sample_rate
            # Apply decay to simulate Nokia tone character
            vol = volume * ((num_samples - s) / num_samples) ** decay
            value = int(max_sample * vol * math.sin(2 * math.pi * frequency * t))
            buf[s][0] = buf[s][1] = value
        
        return buf.astype(np.int16)
    
    def generate_menu_sound(self):
        """Generate Nokia-style menu navigation sound"""
        tone = self._generate_tone(1200, 0.05, self.volume, decay=0.5)
        return self._create_sound(tone)
    
    def generate_select_sound(self):
        """Generate Nokia-style selection sound"""
        duration = 0.1
        samples1 = self._generate_tone(1318.5, duration/2, self.volume)
        samples2 = self._generate_tone(1567.98, duration/2, self.volume)
        combined = np.vstack((samples1, samples2))
        return self._create_sound(combined)
    
    def generate_game_over_sound(self):
        """Generate Nokia-style game over sound"""
        duration = 0.7
        samples = []
        freqs = [660, 587.33, 523.25, 493.88, 440]
        
        for i, freq in enumerate(freqs):
            tone_duration = duration / len(freqs)
            decay = 1.0 + i * 0.2  # Increase decay for each tone
            tone = self._generate_tone(freq, tone_duration, self.volume, decay)
            samples.append(tone)
        
        combined = np.vstack(tuple(samples))
        return self._create_sound(combined)
    
    def generate_food_sound(self):
        """Generate Nokia-style food pickup sound"""
        duration = 0.1
        samples1 = self._generate_tone(1174.66, duration/2, self.volume)
        samples2 = self._generate_tone(1396.91, duration/2, self.volume)
        combined = np.vstack((samples1, samples2))
        return self._create_sound(combined)
    
    def generate_move_sound(self):
        """Generate a very soft movement sound"""
        return self._create_sound(self._generate_tone(440, 0.02, self.volume * 0.1))
    
    def generate_startup_sound(self):
        """Generate Nokia-style startup sound"""
        duration = 1.0
        samples = []
        freqs = [1318.5, 987.77, 1174.66, 987.77, 880, 783.99]
        durations = [0.2, 0.1, 0.1, 0.1, 0.2, 0.3]
        
        for freq, dur in zip(freqs, durations):
            tone = self._generate_tone(freq, dur, self.volume)
            samples.append(tone)
        
        combined = np.vstack(tuple(samples))
        return self._create_sound(combined)

# Initialize audio engine
audio_engine = AudioEngine()

# Preload sounds
menu_sound = audio_engine.generate_menu_sound()
select_sound = audio_engine.generate_select_sound()
game_over_sound = audio_engine.generate_game_over_sound()
food_sound = audio_engine.generate_food_sound()
move_sound = audio_engine.generate_move_sound()
startup_sound = audio_engine.generate_startup_sound()

# Snake representation
class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        for i in range(1, self.length):
            self.positions.append((self.positions[0][0] - i, self.positions[0][1]))
        self.direction = 'RIGHT'
        self.score = 0
        self.next_direction = self.direction
        
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        # Update direction
        self.direction = self.next_direction
        
        # Calculate new head position
        head = self.get_head_position()
        if self.direction == 'RIGHT':
            new_head = (head[0] + 1, head[1])
        elif self.direction == 'LEFT':
            new_head = (head[0] - 1, head[1])
        elif self.direction == 'UP':
            new_head = (head[0], head[1] - 1)
        elif self.direction == 'DOWN':
            new_head = (head[0], head[1] + 1)
        
        # Check for walls
        if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
            return False  # Game over
        
        # Check for collision with self
        if new_head in self.positions:
            return False  # Game over
        
        # Add new head
        self.positions.insert(0, new_head)
        
        # Remove tail if we haven't eaten food
        if len(self.positions) > self.length:
            self.positions.pop()
            
        return True
    
    def change_direction(self, direction):
        # Prevent 180-degree turns
        if (direction == 'RIGHT' and self.direction != 'LEFT') or \
           (direction == 'LEFT' and self.direction != 'RIGHT') or \
           (direction == 'UP' and self.direction != 'DOWN') or \
           (direction == 'DOWN' and self.direction != 'UP'):
            self.next_direction = direction
    
    def draw(self, surface):
        for i, pos in enumerate(self.positions):
            rect = pygame.Rect(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if i == 0:  # Head
                pygame.draw.rect(surface, DARK_GREEN, rect)
            else:  # Body
                pygame.draw.rect(surface, GREEN, rect)
                pygame.draw.rect(surface, DARK_GREEN, rect, 1)  # Border
    
    def grow(self):
        self.length += 1
        self.score += 10

# Food representation
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()
        
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    
    def draw(self, surface):
        rect = pygame.Rect(self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)  # Border

# Simple text renderer
def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.SysFont('Arial', size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

# Game menu
def show_menu():
    # Play startup sound when menu is first shown
    startup_sound.play()
    
    screen.fill(BLACK)
    
    # Draw Nokia-style border
    pygame.draw.rect(screen, GRAY, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 5)
    
    # Draw title
    draw_text(screen, 'SNAKE', 40, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4, GREEN)
    
    # Draw menu options
    draw_text(screen, 'Press SPACE to Start', 20, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    draw_text(screen, 'Press ESC to Quit', 20, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30)
    
    # Draw snake icon
    snake_icon_rect = pygame.Rect(WINDOW_WIDTH // 2 - 30, WINDOW_HEIGHT // 4 - 50, 60, 20)
    pygame.draw.rect(screen, GREEN, snake_icon_rect)
    
    pygame.display.update()
    
    # Menu loop
    waiting = True
    option_selected = 0
    menu_options = ["Start", "Quit"]
    last_key_time = 0
    key_delay = 200  # milliseconds
    
    while waiting:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if current_time - last_key_time > key_delay:
                    last_key_time = current_time
                    
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        menu_sound.play()
                        option_selected = (option_selected + 1) % len(menu_options)
                    
                    elif event.key == pygame.K_SPACE:
                        select_sound.play()
                        pygame.time.wait(300)  # Wait for sound to play
                        waiting = False
                        
                    elif event.key == pygame.K_ESCAPE:
                        select_sound.play()
                        pygame.time.wait(300)  # Wait for sound to play
                        pygame.quit()
                        sys.exit()

# Game over screen
def show_game_over(score):
    # Play game over sound
    game_over_sound.play()
    pygame.time.wait(700)  # Wait for sound to complete
    
    screen.fill(BLACK)
    
    # Draw Nokia-style border
    pygame.draw.rect(screen, GRAY, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 5)
    
    # Draw text
    draw_text(screen, 'GAME OVER', 40, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4, RED)
    draw_text(screen, f'Score: {score}', 30, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    draw_text(screen, 'Press SPACE to Play Again', 20, WINDOW_WIDTH // 2, WINDOW_HEIGHT * 3 // 4)
    draw_text(screen, 'Press ESC to Quit', 20, WINDOW_WIDTH // 2, WINDOW_HEIGHT * 3 // 4 + 30)
    
    pygame.display.update()
    
    # Wait for player input
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    select_sound.play()
                    pygame.time.wait(300)  # Wait for sound to play
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    select_sound.play()
                    pygame.time.wait(300)  # Wait for sound to play
                    pygame.quit()
                    sys.exit()

# Main game function
def game_loop():
    snake = Snake()
    food = Food()
    
    # Ensure food doesn't spawn on the snake
    while food.position in snake.positions:
        food.randomize_position()
    
    game_over = False
    last_direction_change = 0
    direction_change_delay = 100  # milliseconds
    
    while not game_over:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if current_time - last_direction_change > direction_change_delay:
                    last_direction_change = current_time
                    
                    old_direction = snake.direction
                    
                    if event.key == pygame.K_UP:
                        snake.change_direction('UP')
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction('DOWN')
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction('LEFT')
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction('RIGHT')
                    
                    # Play move sound when direction actually changes
                    if old_direction != snake.direction:
                        move_sound.play()
                        
                    elif event.key == pygame.K_ESCAPE:
                        game_over = True
        
        # Update snake position
        if not snake.update():
            # Game over when snake hits wall or itself
            show_game_over(snake.score)
            return
        
        # Check if snake ate food
        if snake.get_head_position() == food.position:
            snake.grow()
            food_sound.play()
            food.randomize_position()
            # Ensure food doesn't spawn on the snake
            while food.position in snake.positions:
                food.randomize_position()
                
            # Increase speed slightly based on length
            if snake.length % 5 == 0:
                global FPS
                FPS = min(FPS + 1, 20)
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw Nokia-style border
        pygame.draw.rect(screen, GRAY, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 5)
        
        # Draw grid (optional)
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            for y in range(0, WINDOW_HEIGHT - 40, CELL_SIZE):
                cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, (20, 20, 20), cell_rect, 1)
        
        # Draw game objects
        snake.draw(screen)
        food.draw(screen)
        
        # Draw score
        draw_text(screen, f'Score: {snake.score}', 18, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30)
        
        pygame.display.update()
        clock.tick(FPS)

# Main game loop
def main():
    while True:
        global FPS
        FPS = 12  # Reset FPS for each new game
        show_menu()
        game_loop()

# Start the game
if __name__ == "__main__":
    main()
