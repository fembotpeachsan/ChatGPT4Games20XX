import math
import time
import numpy as np
from pynput import keyboard
import random
import pygame

import synthwave.osc as osc
import synthwave.waveforms as waveforms

# --- Configuration ---
SAMPLE_RATE = 44100
FPS = 60
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# --- Pygame Setup ---
# Use SDL2 for better compatibility with M1 Macs (Rosetta or Native)
# It's good practice to specify the audio driver as well
import os
os.environ['SDL_AUDIODRIVER'] = 'coreaudio' # For macOS

pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 1024)
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()

# --- Synth Setup (for sound effects) ---
# Create instances of the Oscillator class 
osc_bounce = osc.Oscillator(waveforms.sine, amplitude=0.5, sample_rate=SAMPLE_RATE)
osc_score = osc.Oscillator(waveforms.square, amplitude=0.3, sample_rate=SAMPLE_RATE)


# --- Game Variables ---
ball_x, ball_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
ball_dx, ball_dy = 5, 5
paddle_a_y = SCREEN_HEIGHT // 2
paddle_b_y = SCREEN_HEIGHT // 2
score_a, score_b = 0, 0

# --- Game Constants ---
PADDLE_SPEED = 6
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
BALL_SIZE = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# --- Game Objects ---
class Paddle(pygame.Rect):
    def __init__(self, x, y, width, height, color, speed):
        super().__init__(x, y, width, height)
        self.color = color
        self.speed = speed

    def move(self, up=False):
        if up:
            self.y -= self.speed
        else:
            self.y += self.speed
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height)) # Keep paddle within screen bounds

    def draw(self, screen):
      pygame.draw.rect(screen, self.color, self)
    

class Ball(pygame.Rect):
    def __init__(self, x, y, size, color, dx, dy):
        super().__init__(x, y, size, size)
        self.color = color
        self.dx = dx
        self.dy = dy
        self.original_dx = dx
        self.original_dy = dy

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def reset(self):
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT // 2 - self.height // 2
        self.dx = self.original_dx * random.choice((1, -1))
        self.dy = self.original_dy * random.choice((1, -1))

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self)

# --- Functions ---

def play_sound(oscillator, note, duration):
    oscillator.set_frequency(440 * 2 ** ((note - 69) / 12))
    sound_wave = np.int16(oscillator.get_samples(int(duration * SAMPLE_RATE)))
    sound = pygame.sndarray.make_sound(sound_wave)
    sound.play()

# --- Initialize Game Objects ---
paddle_a = Paddle(20, paddle_a_y - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, WHITE, PADDLE_SPEED)
paddle_b = Paddle(SCREEN_WIDTH - 20 - PADDLE_WIDTH, paddle_b_y - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, WHITE, PADDLE_SPEED)
ball = Ball(ball_x - BALL_SIZE // 2, ball_y - BALL_SIZE // 2, BALL_SIZE, WHITE, ball_dx, ball_dy)

# --- Input Handling ---
def on_press(key):
    global paddle_a_y

    if key == keyboard.Key.up:
        paddle_a.move(up=True)

    elif key == keyboard.Key.down:
        paddle_a.move(up=False)

# --- Start Keyboard Listener ---
listener = keyboard.Listener(on_press=on_press)
listener.start()

# --- Game Loop ---
def game_loop():
    global ball_x, ball_y, ball_dx, ball_dy, paddle_a_y, paddle_b_y, score_a, score_b

    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- AI (Paddle B) ---
        if ball.y > paddle_b.y + paddle_b.height//2:
            paddle_b.move(up=False)
        elif ball.y < paddle_b.y:
            paddle_b.move(up=True)

        # --- Ball Movement ---
        ball.move()

        # --- Border Collisions (Top and Bottom) ---
        if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
            ball.dy *= -1
            play_sound(osc_bounce, 72, 0.05)

        # --- Paddle Collisions ---
        if ball.colliderect(paddle_a) or ball.colliderect(paddle_b):
            ball.dx *= -1
            play_sound(osc_bounce, 72, 0.05)

        # --- Scoring ---
        if ball.left <= 0:
            score_b += 1
            play_sound(osc_score, 80, 0.2)
            ball.reset()
            print(f"Player A: {score_a}  Player B: {score_b}")

        elif ball.right >= SCREEN_WIDTH:
            score_a += 1
            play_sound(osc_score, 80, 0.2)
            ball.reset()
            print(f"Player A: {score_a}  Player B: {score_b}")

        # --- Draw everything ---
        screen.fill(BLACK)
        paddle_a.draw(screen)
        paddle_b.draw(screen)
        ball.draw(screen)

        # --- Display Score ---
        font = pygame.font.Font(None, 74)
        score_text = font.render(str(score_a) + " - " + str(score_b), 1, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 10))

        pygame.display.flip()
        clock.tick(FPS)

# --- Start the Game ---
game_loop()

# --- Clean up Pygame and Keyboard Listener ---
pygame.quit()
listener.stop()
