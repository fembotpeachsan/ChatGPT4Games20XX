import os
import platform
import contextlib
import numpy as np
import random
import sys
from enum import Enum, auto
from typing import List, Tuple, Optional
import pygame

# Ensure compatibility with ARM Macs using Rosetta 2 (x86_64 emulation)
if platform.system() == "Darwin" and platform.machine() == "arm64":
    if not os.environ.get("RUNNING_UNDER_ROSETTA"):
        os.environ["RUNNING_UNDER_ROSETTA"] = "1"
        os.execvp("arch", ["arch", "-x86_64"] + ["/usr/bin/python3"] + [__file__])

class Direction(Enum):
    RIGHT = auto()
    LEFT = auto()
    UP = auto()
    DOWN = auto()

class GameState(Enum):
    RUNNING = auto()
    GAME_OVER = auto()
    PAUSED = auto()

class SoundManager:
    def __init__(self, volume: float = 0.5):
        self.volume = volume
        self.sound_enabled = False
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=2048)
            self.sound_enabled = True
        except pygame.error:
            print("Warning: Sound initialization failed. Game will run without sound.")

    def generate_sine_wave(self, frequency: float, duration: float, sample_rate: int = 44100) -> Optional[bytes]:
        """Generates a sine wave with specified parameters."""
        if not self.sound_enabled:
            return None
            
        try:
            t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
            waveform = (np.sin(2 * np.pi * frequency * t) * 32767 * self.volume).astype(np.int16)
            return waveform.tobytes()
        except Exception as e:
            print(f"Warning: Sound generation failed: {e}")
            return None

    def play_sound(self, frequency: float, duration: float) -> None:
        """Plays a sound with given frequency and duration."""
        if not self.sound_enabled:
            return

        try:
            waveform = self.generate_sine_wave(frequency, duration)
            if waveform:
                sound = pygame.mixer.Sound(buffer=waveform)
                sound.play()
                # Schedule cleanup after sound finishes
                pygame.time.set_timer(
                    pygame.USEREVENT + 1,
                    int(duration * 1000) + 100,
                    loops=1
                )
        except Exception as e:
            print(f"Warning: Sound playback failed: {e}")

    def cleanup(self) -> None:
        """Cleanup sound resources."""
        if self.sound_enabled:
            pygame.mixer.quit()

class SnakeGame:
    def __init__(self, width: int = 640, height: int = 480):
        pygame.init()
        
        # Game Constants
        self.WIDTH = width
        self.HEIGHT = height
        self.FPS = 15  # Lowered FPS for better control
        self.SNAKE_SIZE = 20
        self.SPEED = 0.2  # Snake movement speed modifier (adjustable)
        
        # Initialize managers
        self.sound_manager = SoundManager(volume=0.5)
        
        # Display setup
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Snake Game with Synthesized Audio")
        self.clock = pygame.time.Clock()
        
        # Game state initialization
        self.reset_game()

    def reset_game(self) -> None:
        """Reset the game to initial state."""
        self.snake_position = [100, 50]
        self.snake_body = [[100, 50], [80, 50], [60, 50]]
        self.direction = Direction.RIGHT
        self.change_to = self.direction
        self.score = 0
        self.game_state = GameState.RUNNING
        self.spawn_food()

    def spawn_food(self) -> None:
        """Spawn food in a valid position (not on snake)."""
        while True:
            x = random.randrange(1, (self.WIDTH // self.SNAKE_SIZE)) * self.SNAKE_SIZE
            y = random.randrange(1, (self.HEIGHT // self.SNAKE_SIZE)) * self.SNAKE_SIZE
            self.food_position = [x, y]
            if self.food_position not in self.snake_body:
                break

    def handle_input(self) -> bool:
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == GameState.RUNNING:
                        self.game_state = GameState.PAUSED
                    elif self.game_state == GameState.PAUSED:
                        self.game_state = GameState.RUNNING
                
                if self.game_state == GameState.RUNNING:
                    if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                        self.change_to = Direction.UP
                    if event.key == pygame.K_DOWN and self.direction != Direction.UP:
                        self.change_to = Direction.DOWN
                    if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                        self.change_to = Direction.LEFT
                    if event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                        self.change_to = Direction.RIGHT
                
                if self.game_state == GameState.GAME_OVER and event.key == pygame.K_r:
                    self.reset_game()
            
            # Handle sound cleanup event
            elif event.type == pygame.USEREVENT + 1:
                pygame.mixer.stop()  # Stop any playing sounds
        
        return True

    def check_food_collision(self) -> bool:
        """Check if snake has collected food."""
        snake_rect = pygame.Rect(
            self.snake_position[0],
            self.snake_position[1],
            self.SNAKE_SIZE,
            self.SNAKE_SIZE
        )
        food_rect = pygame.Rect(
            self.food_position[0],
            self.food_position[1],
            self.SNAKE_SIZE,
            self.SNAKE_SIZE
        )
        return snake_rect.colliderect(food_rect)

    def update(self) -> None:
        """Update game state."""
        if self.game_state != GameState.RUNNING:
            return

        # Update direction
        self.direction = self.change_to

        # Update snake position
        new_position = self.snake_position.copy()
        if self.direction == Direction.UP:
            new_position[1] -= self.SNAKE_SIZE
        elif self.direction == Direction.DOWN:
            new_position[1] += self.SNAKE_SIZE
        elif self.direction == Direction.LEFT:
            new_position[0] -= self.SNAKE_SIZE
        elif self.direction == Direction.RIGHT:
            new_position[0] += self.SNAKE_SIZE

        # Check collision with walls
        if (new_position[0] < 0 or new_position[0] >= self.WIDTH or
            new_position[1] < 0 or new_position[1] >= self.HEIGHT):
            self.game_over()
            return

        # Check collision with self
        if new_position in self.snake_body[1:]:
            self.game_over()
            return

        # Update snake body
        self.snake_position = new_position
        self.snake_body.insert(0, list(self.snake_position))
        
        # Check food collision using rect collision
        if self.check_food_collision():
            self.score += 1
            self.sound_manager.play_sound(440, 0.2)  # Food collection sound
            self.spawn_food()
        else:
            self.snake_body.pop()

    def game_over(self) -> None:
        """Handle game over state."""
        self.sound_manager.play_sound(200, 0.5)  # Game over sound
        self.game_state = GameState.GAME_OVER

    def draw(self) -> None:
        """Draw the game state."""
        self.window.fill((0, 0, 0))  # Black background
        
        # Draw snake
        for pos in self.snake_body:
            pygame.draw.rect(
                self.window, 
                (0, 255, 0),
                pygame.Rect(pos[0], pos[1], self.SNAKE_SIZE, self.SNAKE_SIZE)
            )
        
        # Draw food
        pygame.draw.rect(
            self.window,
            (255, 0, 0),
            pygame.Rect(
                self.food_position[0],
                self.food_position[1],
                self.SNAKE_SIZE,
                self.SNAKE_SIZE
            )
        )

        # Draw score
        font = pygame.font.SysFont('comicsans', 20)
        score_surface = font.render(f'Score: {self.score}', True, (255, 255, 255))
        self.window.blit(score_surface, (10, 10))

        # Draw game over or pause screen
        if self.game_state == GameState.GAME_OVER:
            font = pygame.font.SysFont('comicsans', 50)
            game_over_surface = font.render(f'Game Over! Score: {self.score}', True, (255, 255, 255))
            restart_surface = font.render('Press R to Restart', True, (255, 255, 255))
            
            game_over_rect = game_over_surface.get_rect(midtop=(self.WIDTH // 2, self.HEIGHT // 4))
            restart_rect = restart_surface.get_rect(midtop=(self.WIDTH // 2, self.HEIGHT // 2))
            
            self.window.blit(game_over_surface, game_over_rect)
            self.window.blit(restart_surface, restart_rect)
        
        elif self.game_state == GameState.PAUSED:
            font = pygame.font.SysFont('comicsans', 50)
            pause_surface = font.render('PAUSED', True, (255, 255, 255))
            pause_rect = pause_surface.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.window.blit(pause_surface, pause_rect)

        pygame.display.flip()

    def run(self) -> None:
        """Main game loop."""
        running = True
        try:
            while running:
                running = self.handle_input()
                self.update()
                self.draw()
                self.clock.tick(self.FPS)
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Cleanup game resources."""
        self.sound_manager.cleanup()
        pygame.quit()

if __name__ == "__main__":
    try:
        game = SnakeGame()
        game.run()
    except KeyboardInterrupt:
        print("\nGame terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        sys.exit(0)