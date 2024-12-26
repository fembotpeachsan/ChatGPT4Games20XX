import sys
import platform
import pygame
import numpy as np
import random
import os
from typing import List, Tuple

# Hide Pygame support prompt
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Compatibility check for Rosetta or native environment
def check_compatibility():
    """Check system compatibility and Pygame installation."""
    system_info = f"Running on {platform.system()} {platform.machine()}."
    print(system_info)
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        print("Detected Apple Silicon (M1/M2). Ensure you're using the correct Python architecture.")
    try:
        pygame.init()
        pygame.display.init()
        pygame.mixer.init()
        print("Pygame initialized successfully.")
        return True
    except Exception as e:
        print(f"Error initializing Pygame: {e}")
        print("Please ensure Pygame is installed correctly for your architecture.")
        print("Try reinstalling Pygame with: pip install pygame --force-reinstall")
        return False

# Game Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 80, 10
BALL_DIAMETER = 10
BALL_VELOCITY = 5
BRICK_WIDTH, BRICK_HEIGHT = 60, 15

# Synthwave Color Palette
SYNTHWAVE_COLORS = {
    "bg": (10, 10, 30),
    "paddle": (255, 100, 150),
    "ball": (255, 200, 50),
    "bricks": [(255, 100, 100), (100, 255, 200), (150, 100, 255)],
    "text": (255, 255, 255)
}

# Sound Engine
class SoundEngine:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.enabled = True
            self.bounce_sound = self.generate_synth_sound(440, 0.1, 0.5)  # A4 note
            self.brick_sound = self.generate_synth_sound(880, 0.1, 0.5)   # A5 note
            print("SoundEngine initialized successfully.")
        except Exception as e:
            print(f"Sound disabled: {e}")
            self.enabled = False

    @staticmethod
    def generate_synth_sound(frequency: float, duration: float, volume: float = 0.5) -> pygame.mixer.Sound:
        try:
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
            waveform = volume * np.sin(2 * np.pi * frequency * t)
            sound = np.int16(waveform * 32767).tobytes()
            return pygame.mixer.Sound(buffer=sound)
        except Exception as e:
            print(f"Error generating sound: {e}")
            return None

    def play_sound(self, sound):
        if self.enabled and sound:
            try:
                sound.play()
            except Exception as e:
                print(f"Error playing sound: {e}")

# Paddle class
class Paddle:
    def __init__(self):
        self.rect = pygame.Rect(
            (SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, 
             SCREEN_HEIGHT - 30),
            (PADDLE_WIDTH, PADDLE_HEIGHT)
        )
        self.color = SYNTHWAVE_COLORS["paddle"]

    def update(self):
        self.rect.centerx = pygame.mouse.get_pos()[0]
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.color, self.rect)

# Ball class
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 
            (BALL_DIAMETER, BALL_DIAMETER)
        )
        angle = random.uniform(-45, 45)  # Random initial angle between -45 and 45 degrees
        self.direction = [np.cos(np.radians(angle)), -np.sin(np.radians(angle))]

    def update(self, sound_engine: SoundEngine) -> bool:
        self.rect.x += int(self.direction[0] * BALL_VELOCITY)
        self.rect.y += int(self.direction[1] * BALL_VELOCITY)

        # Wall collisions
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction[0] *= -1
            sound_engine.play_sound(sound_engine.bounce_sound)

        if self.rect.top <= 0:
            self.direction[1] *= -1
            sound_engine.play_sound(sound_engine.bounce_sound)

        if self.rect.bottom > SCREEN_HEIGHT:
            return True  # Ball fell out of bounds

        return False

    def draw(self, screen: pygame.Surface):
        pygame.draw.ellipse(screen, SYNTHWAVE_COLORS["ball"], self.rect)

# Brick class
class Brick:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = random.choice(SYNTHWAVE_COLORS["bricks"])

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.color, self.rect)

# Main Game Class
class Game:
    def __init__(self):
        if not check_compatibility():
            sys.exit(1)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Synthwave Brick Breaker")

        self.clock = pygame.time.Clock()
        self.sound_engine = SoundEngine()
        self.reset_game()

    def reset_game(self):
        """Reset the game state."""
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = [
            Brick(x, y) 
            for x in range(0, SCREEN_WIDTH, BRICK_WIDTH) 
            for y in range(50, SCREEN_HEIGHT // 3, BRICK_HEIGHT)  # Start bricks 50px from top
        ]
        self.score = 0
        self.lives = 3

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.paddle.update()
            ball_out_of_bounds = self.ball.update(self.sound_engine)

            if ball_out_of_bounds:
                self.lives -= 1
                print(f"Lives remaining: {self.lives}")
                if self.lives <= 0:
                    print("Game Over!")
                    running = False
                else:
                    self.ball = Ball()  # Reset ball position and direction

            # Collision detection: Ball and Paddle
            if self.ball.rect.colliderect(self.paddle.rect):
                self.ball.direction[1] *= -1
                self.ball.rect.bottom = self.paddle.rect.top  # Prevent sticking
                self.sound_engine.play_sound(self.sound_engine.bounce_sound)

            # Collision detection: Ball and Bricks
            for brick in self.bricks[:]:
                if self.ball.rect.colliderect(brick.rect):
                    self.ball.direction[1] *= -1
                    self.bricks.remove(brick)
                    self.sound_engine.play_sound(self.sound_engine.brick_sound)
                    self.score += 1
                    print(f"Score: {self.score}")

            # Drawing
            self.screen.fill(SYNTHWAVE_COLORS["bg"])
            self.paddle.draw(self.screen)
            self.ball.draw(self.screen)
            for brick in self.bricks:
                brick.draw(self.screen)

            # Display Score and Lives
            self.display_stats()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def display_stats(self):
        """Display the current score and lives."""
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, SYNTHWAVE_COLORS["text"])
        lives_text = font.render(f"Lives: {self.lives}", True, SYNTHWAVE_COLORS["text"])
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))

if __name__ == "__main__":
    Game().run()
