import pygame
import tkinter as tk
from tkinter import messagebox
import sys
import random
import os
import numpy as np

# Pre-initialize the mixer for a 44100 Hz, 16-bit, mono sound
pygame.mixer.pre_init(44100, -16, 1, 512)

def generate_sound(frequency=440, duration_ms=100, volume=0.5, sample_rate=44100):
    """
    Generate a pygame sound object with a sine wave tone.
    frequency: tone frequency in Hz
    duration_ms: duration of the tone in milliseconds
    volume: amplitude scaling (0.0 to 1.0)
    """
    n_samples = int(sample_rate * (duration_ms / 1000.0))
    t = np.linspace(0, duration_ms/1000, n_samples, endpoint=False)
    tone = np.sin(2 * np.pi * frequency * t) * volume
    # Convert to 16-bit signed integers
    tone = (tone * 32767).astype(np.int16)
    sound = pygame.sndarray.make_sound(tone)
    return sound

class PongGame:
    def __init__(self, master):
        master.withdraw()  # Hide the main Tkinter window
        self.master = master

        # Initialize Pygame
        pygame.init()

        # Set up the window
        self.width = 600
        self.height = 400
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pong -  [C] Team Flames 20XX")

        # Colors
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)

        # Game objects
        self.paddle_width = 10
        self.paddle_height = 60
        self.player1_x = 10
        self.player1_y = self.height // 2 - self.paddle_height // 2
        self.player2_x = self.width - self.paddle_width - 10
        self.player2_y = self.height // 2 - self.paddle_height // 2
        self.paddle_speed = 7

        self.ball_size = 10
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_speed_x = 5 * random.choice((1, -1))
        self.ball_speed_y = 5 * random.choice((1, -1))

        # Scores
        self.player1_score = 0
        self.player2_score = 0

        # Font using a system font.
        self.font = pygame.font.SysFont("Arial", 30, bold=True)

        # Generate simple sounds:
        # "beep" for collisions (440 Hz) and "boop" for scoring (300 Hz)
        self.beep_sound = generate_sound(frequency=440, duration_ms=100, volume=0.5)
        self.boop_sound = generate_sound(frequency=300, duration_ms=150, volume=0.5)

        self.clock = pygame.time.Clock()
        self.run()

    def draw(self):
        self.screen.fill(self.black)

        # Draw paddles
        pygame.draw.rect(self.screen, self.white, (self.player1_x, self.player1_y, self.paddle_width, self.paddle_height))
        pygame.draw.rect(self.screen, self.white, (self.player2_x, self.player2_y, self.paddle_width, self.paddle_height))

        # Draw ball
        pygame.draw.rect(self.screen, self.white, (self.ball_x, self.ball_y, self.ball_size, self.ball_size))

        # Draw scores – centered at the top
        score_text = self.font.render(f"{self.player1_score}   {self.player2_score}", True, self.white)
        score_rect = score_text.get_rect(center=(self.width // 2, 30))
        self.screen.blit(score_text, score_rect)

        # Draw center line
        pygame.draw.line(self.screen, self.white, (self.width // 2, 0), (self.width // 2, self.height), 3)
        pygame.display.flip()

    def move_ball(self):
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y

        # Bounce off top/bottom
        if self.ball_y <= 0 or self.ball_y + self.ball_size >= self.height:
            self.ball_speed_y *= -1
            self.play_beep("collision")

        # Bounce off paddles
        if (
            self.player1_x <= self.ball_x <= self.player1_x + self.paddle_width
            and self.player1_y <= self.ball_y + self.ball_size <= self.player1_y + self.paddle_height
        ) or (
            self.player2_x <= self.ball_x + self.ball_size <= self.player2_x + self.paddle_width
            and self.player2_y <= self.ball_y + self.ball_size <= self.player2_y + self.paddle_height
        ):
            self.ball_speed_x *= -1
            self.play_beep("collision")

        # Score points and reset ball
        if self.ball_x < 0:
            self.player2_score += 1
            self.reset_ball()
            self.play_beep("score")
        elif self.ball_x + self.ball_size > self.width:
            self.player1_score += 1
            self.reset_ball()
            self.play_beep("score")

        # End the game when a player reaches 10 points
        if self.player1_score >= 10 or self.player2_score >= 10:
            self.end_game()

    def move_paddles(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.player1_y > 0:
            self.player1_y -= self.paddle_speed
        if keys[pygame.K_s] and self.player1_y + self.paddle_height < self.height:
            self.player1_y += self.paddle_speed
        if keys[pygame.K_UP] and self.player2_y > 0:
            self.player2_y -= self.paddle_speed
        if keys[pygame.K_DOWN] and self.player2_y + self.paddle_height < self.height:
            self.player2_y += self.paddle_speed

    def reset_ball(self):
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_speed_x = 5 * random.choice((1, -1))
        self.ball_speed_y = 5 * random.choice((1, -1))
        pygame.time.delay(500)  # Short pause after scoring

    def play_beep(self, sound_type="collision"):
        """
        Plays a sound effect.
        Use "collision" for paddle/wall bounces and "score" for scoring events.
        """
        if sound_type == "score":
            self.boop_sound.play()
        else:
            self.beep_sound.play()

    def end_game(self):
        winner = "Player 1" if self.player1_score > self.player2_score else "Player 2"
        # Stop any playing music (if applicable)
        pygame.mixer.music.stop()
        if self.show_winner_message(winner):
            self.restart_game()  # Restart the game if the user chooses to play again
        else:
            self.quit_game()

    def show_winner_message(self, winner):
        result = messagebox.askyesno("Game Over", f"{winner} Wins!\nPlay again?")
        return result

    def restart_game(self):
        self.player1_score = 0
        self.player2_score = 0
        self.reset_ball()
        self.run()  # Restart the game loop

    def quit_game(self):
        pygame.quit()
        self.master.destroy()
        sys.exit()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

            self.move_paddles()
            self.move_ball()
            self.draw()
            self.clock.tick(60)

# Set up Tkinter root window (hidden)
root = tk.Tk()
root.withdraw()

# Create and run the game
game = PongGame(root)
root.mainloop()
