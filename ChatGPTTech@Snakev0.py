import pygame
import random
import sys
import numpy as np
import os

# Constants for game dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TILE_SIZE = 20
FPS = 10  # Slower frame rate for a retro feel

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_GREEN = (57, 255, 20)
NEON_RED = (255, 64, 64)
SYNTHWAVE_PURPLE = (135, 0, 255)
BUTTON_COLOR = (50, 50, 50)
BUTTON_HOVER_COLOR = (70, 70, 70)
TEXT_COLOR = WHITE

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Game States
MENU = 'menu'
GAME = 'game'
GAME_OVER = 'game_over'
CREDITS = 'credits'
HIGH_SCORES = 'high_scores'

# High Scores File
HIGH_SCORES_FILE = "high_scores.txt"
MAX_HIGH_SCORES = 5  # Number of top scores to keep


class Button:
    def __init__(self, text, pos, size, action):
        self.text = text
        self.rect = pygame.Rect(pos, size)
        self.color = BUTTON_COLOR
        self.action = action
        self.font = pygame.font.SysFont('Arial', 30)
        self.text_surf = self.font.render(self.text, True, TEXT_COLOR)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        # Update text_rect in case the button size changes
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        screen.blit(self.text_surf, self.text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action()
                return True
        return False


class HighScores:
    def __init__(self, file_path=HIGH_SCORES_FILE):
        self.file_path = file_path
        self.scores = self.load_scores()

    def load_scores(self):
        scores = []
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                for line in f:
                    try:
                        score = int(line.strip())
                        scores.append(score)
                    except ValueError:
                        continue
        return sorted(scores, reverse=True)[:MAX_HIGH_SCORES]

    def add_score(self, score):
        self.scores.append(score)
        self.scores = sorted(self.scores, reverse=True)[:MAX_HIGH_SCORES]
        self.save_scores()

    def save_scores(self):
        with open(self.file_path, 'w') as f:
            for score in self.scores:
                f.write(f"{score}\n")


class SnakeGame:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game - Synthwave NES Style")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = MENU  # Start with the menu

        # Initialize snake and food
        self.snake = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.snake_dir = RIGHT
        self.food = self.generate_food()

        # Initialize score
        self.score = 0
        self.high_scores = HighScores()

        # Initialize sound
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        # Create buttons for Menu and Game Over
        self.menu_buttons = [
            Button("Play", (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 60), (200, 50), self.start_game),
            Button("High Scores", (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2), (200, 50), self.show_high_scores),
            Button("Credits", (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 60), (200, 50), self.show_credits),
            Button("Exit", (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 120), (200, 50), self.exit_game)
        ]

        self.game_over_buttons = [
            Button("Restart", (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 60), (200, 50), self.start_game),
            Button("High Scores", (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2), (200, 50), self.show_high_scores),
            Button("Exit", (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 60), (200, 50), self.exit_game)
        ]

        # Create buttons for Credits and High Scores Screens
        self.credits_buttons = [
            Button("Back to Menu", (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100), (200, 50), self.back_to_menu)
        ]

        self.high_scores_buttons = [
            Button("Back to Menu", (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100), (200, 50), self.back_to_menu)
        ]

    def generate_food(self):
        while True:
            food_pos = (
                random.randrange(0, SCREEN_WIDTH, TILE_SIZE),
                random.randrange(0, SCREEN_HEIGHT, TILE_SIZE),
            )
            if food_pos not in self.snake:
                return food_pos

    def generate_sound(self, frequency, duration, waveform='sine'):
        """Generates a simple sound effect using numpy."""
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)

        # Select waveform
        if waveform == 'sine':
            wave = 0.5 * np.sin(2 * np.pi * frequency * t)
        elif waveform == 'square':
            wave = 0.5 * np.sign(np.sin(2 * np.pi * frequency * t))
        elif waveform == 'sawtooth':
            wave = 0.5 * (2 * (t * frequency - np.floor(t * frequency + 0.5)))
        else:
            wave = 0.5 * np.sin(2 * np.pi * frequency * t)  # Default to sine wave

        # Convert waveform to 16-bit audio format
        sound_data = np.int16(wave * 32767)

        # Ensure the sound data matches the mixer settings
        if pygame.mixer.get_init()[1] == 1:
            # Mono sound
            sound_buffer = pygame.sndarray.make_sound(sound_data)
        else:
            # Stereo sound, duplicate the mono signal
            stereo_sound_data = np.column_stack((sound_data, sound_data))
            sound_buffer = pygame.sndarray.make_sound(stereo_sound_data)

        return sound_buffer

    def play_beep(self):
        """Plays a beep sound (square wave)"""
        beep_sound = self.generate_sound(600, 0.1, waveform='square')
        beep_sound.play()

    def play_eat_sound(self):
        """Plays a sound when food is eaten"""
        eat_sound = self.generate_sound(440, 0.1, waveform='square')
        eat_sound.play()

    def start_game(self):
        """Action to start the game"""
        self.play_beep()
        self.state = GAME
        # Reset snake, direction, food, and score
        self.snake = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.snake_dir = RIGHT
        self.food = self.generate_food()
        self.score = 0

    def exit_game(self):
        """Action to exit the game"""
        self.play_beep()
        self.running = False

    def show_credits(self):
        """Action to show the Credits screen"""
        self.play_beep()
        self.state = CREDITS

    def show_high_scores(self):
        """Action to show the High Scores screen"""
        self.play_beep()
        self.state = HIGH_SCORES

    def back_to_menu(self):
        """Action to return to the Menu"""
        self.play_beep()
        self.state = MENU

    def move_snake(self):
        head_x, head_y = self.snake[0]
        dir_x, dir_y = self.snake_dir
        new_head = (head_x + dir_x * TILE_SIZE, head_y + dir_y * TILE_SIZE)

        # Check if snake hits the wall
        if (
            new_head[0] < 0
            or new_head[0] >= SCREEN_WIDTH
            or new_head[1] < 0
            or new_head[1] >= SCREEN_HEIGHT
        ):
            self.state = GAME_OVER
            self.check_high_score()
            return

        # Check if snake hits itself
        if new_head in self.snake:
            self.state = GAME_OVER
            self.check_high_score()
            return

        # Move snake
        self.snake.insert(0, new_head)

        # Check if snake eats the food
        if new_head == self.food:
            self.score += 1
            self.food = self.generate_food()
            # Play sound when food is eaten (using a square wave for a retro effect)
            self.play_eat_sound()
        else:
            self.snake.pop()  # Remove tail segment

    def check_high_score(self):
        """Check if the current score is a high score and update accordingly"""
        if len(self.high_scores.scores) < MAX_HIGH_SCORES or self.score > self.high_scores.scores[-1]:
            self.high_scores.add_score(self.score)

    def handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.snake_dir != DOWN:
                    self.snake_dir = UP
                elif event.key == pygame.K_DOWN and self.snake_dir != UP:
                    self.snake_dir = DOWN
                elif event.key == pygame.K_LEFT and self.snake_dir != RIGHT:
                    self.snake_dir = LEFT
                elif event.key == pygame.K_RIGHT and self.snake_dir != LEFT:
                    self.snake_dir = RIGHT

    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            for button in self.menu_buttons:
                if button.is_clicked(event):
                    break  # If a button is clicked, no need to check others

    def handle_game_over_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            for button in self.game_over_buttons:
                if button.is_clicked(event):
                    break  # If a button is clicked, no need to check others

    def handle_credits_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            for button in self.credits_buttons:
                if button.is_clicked(event):
                    break  # If a button is clicked, no need to check others

    def handle_high_scores_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            for button in self.high_scores_buttons:
                if button.is_clicked(event):
                    break  # If a button is clicked, no need to check others

    def draw_game(self):
        # Draw the synthwave grid background
        self.screen.fill(BLACK)
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(self.screen, SYNTHWAVE_PURPLE, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, SYNTHWAVE_PURPLE, (0, y), (SCREEN_WIDTH, y))

        # Draw snake
        for segment in self.snake:
            pygame.draw.rect(self.screen, NEON_GREEN, (*segment, TILE_SIZE, TILE_SIZE))

        # Draw food
        pygame.draw.rect(self.screen, NEON_RED, (*self.food, TILE_SIZE, TILE_SIZE))

        # Draw score
        score_font = pygame.font.SysFont('Arial', 24)
        score_surf = score_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_surf, (10, 10))

        # Apply scanline effect to mimic CRT
        for y in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(self.screen, BLACK, (0, y), (SCREEN_WIDTH, y), 1)

        pygame.display.flip()

    def draw_menu(self):
        # Fill background
        self.screen.fill(BLACK)

        # Draw title
        title_font = pygame.font.SysFont('Arial', 50)
        title_surf = title_font.render("Snake Game", True, SYNTHWAVE_PURPLE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 150))
        self.screen.blit(title_surf, title_rect)

        # Draw buttons
        for button in self.menu_buttons:
            button.draw(self.screen)

        pygame.display.flip()

    def draw_game_over(self):
        # Fill background
        self.screen.fill(BLACK)

        # Draw "Game Over" text
        over_font = pygame.font.SysFont('Arial', 50)
        over_surf = over_font.render("Game Over", True, SYNTHWAVE_PURPLE)
        over_rect = over_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        self.screen.blit(over_surf, over_rect)

        # Draw final score
        score_font = pygame.font.SysFont('Arial', 30)
        score_surf = score_font.render(f"Your Score: {self.score}", True, WHITE)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        self.screen.blit(score_surf, score_rect)

        # Draw buttons
        for button in self.game_over_buttons:
            button.draw(self.screen)

        pygame.display.flip()

    def draw_credits(self):
        # Fill background
        self.screen.fill(BLACK)

        # Draw "Credits" title
        credits_font = pygame.font.SysFont('Arial', 50)
        credits_surf = credits_font.render("Credits", True, SYNTHWAVE_PURPLE)
        credits_rect = credits_surf.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(credits_surf, credits_rect)

        # Display credits text
        credit_text = [
            "Snake Game by HildaGPT 1.0",
            "Inspired by Classic Snake",
            "Developed using Python and Pygame",
            "",
            "Thank you for playing!"
        ]

        text_font = pygame.font.SysFont('Arial', 24)
        for i, line in enumerate(credit_text):
            text_surf = text_font.render(line, True, WHITE)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, 200 + i * 40))
            self.screen.blit(text_surf, text_rect)

        # Draw buttons
        for button in self.credits_buttons:
            button.draw(self.screen)

        pygame.display.flip()

    def draw_high_scores(self):
        # Fill background
        self.screen.fill(BLACK)

        # Draw "High Scores" title
        hs_font = pygame.font.SysFont('Arial', 50)
        hs_surf = hs_font.render("High Scores", True, SYNTHWAVE_PURPLE)
        hs_rect = hs_surf.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(hs_surf, hs_rect)

        # Display high scores
        scores = self.high_scores.scores
        if not scores:
            scores = ["No high scores yet!"]

        text_font = pygame.font.SysFont('Arial', 24)
        for i, score in enumerate(scores, start=1):
            line = f"{i}. {score}"
            text_surf = text_font.render(line, True, WHITE)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, 200 + i * 40))
            self.screen.blit(text_surf, text_rect)

        # Draw buttons
        for button in self.high_scores_buttons:
            button.draw(self.screen)

        pygame.display.flip()

    def run(self):
        while self.running:
            if self.state == MENU:
                self.handle_menu_events()
                self.draw_menu()
            elif self.state == GAME:
                self.handle_game_events()
                self.move_snake()
                self.draw_game()
            elif self.state == GAME_OVER:
                self.handle_game_over_events()
                self.draw_game_over()
            elif self.state == CREDITS:
                self.handle_credits_events()
                self.draw_credits()
            elif self.state == HIGH_SCORES:
                self.handle_high_scores_events()
                self.draw_high_scores()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SnakeGame()
    game.run()
