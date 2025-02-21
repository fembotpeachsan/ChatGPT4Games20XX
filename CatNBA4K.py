import pygame
import tkinter as tk
from tkinter import messagebox
import numpy as np

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)  # 44.1kHz, 16-bit, mono

# Window settings
WIDTH, HEIGHT = 600, 400
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NBA 2K x Metal Gear Solid Fusion")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Player properties
player_x, player_y = 50, HEIGHT - 50
player_speed = 5
player_crouched = False

# Ball properties
ball_x, ball_y = player_x + 20, player_y
ball_speed = 10
ball_in_air = False

# Hoop properties
hoop_x, hoop_y = WIDTH - 50, 100

# Guard properties
guard_x, guard_y = WIDTH // 2, HEIGHT // 2
guard_speed = 2
guard_direction = 1

# Generate synthetic sound effects
def generate_sound(frequency, duration):
    sample_rate = 44100
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)  # Sine wave
    sound_data = (wave * 32767).astype(np.int16)  # Convert to 16-bit PCM
    return pygame.mixer.Sound(buffer=sound_data)

# Sound effects
dribble_sound = generate_sound(100, 0.1)  # Low thud for dribble
shoot_sound = generate_sound(300, 0.2)    # Higher pitch for shooting
alert_sound = generate_sound(500, 0.3)    # Sharp tone for guard alert

# Tkinter Start Menu
start_game_flag = False  # Flag to control game start

def start_game():
    global start_game_flag
    start_game_flag = True
    root.quit()  # Exit Tkinter main loop cleanly

root = tk.Tk()
root.title("Game Menu")
root.geometry("300x200")
tk.Label(root, text="NBA 2K x Metal Gear Fusion", font=("Arial", 16)).pack(pady=20)
tk.Button(root, text="Start Game", command=start_game, font=("Arial", 12)).pack(pady=20)
tk.Button(root, text="Quit", command=root.quit, font=("Arial", 12)).pack(pady=20)

# Run Tkinter menu and check flag afterward
root.mainloop()
if start_game_flag:
    root.destroy()  # Destroy Tkinter window after mainloop ends
    # Game loop
    def game_loop():
        global player_x, player_y, player_crouched, ball_x, ball_y, ball_in_air, guard_x, guard_y, guard_direction
        
        running = True
        clock = pygame.time.Clock()
        dribble_timer = 0  # To control dribble sound frequency

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Player movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player_x > 0:
                player_x -= player_speed
                dribble_timer += 1
                if dribble_timer % 20 == 0 and not ball_in_air:
                    dribble_sound.play()
            if keys[pygame.K_RIGHT] and player_x < WIDTH - 20:
                player_x += player_speed
                dribble_timer += 1
                if dribble_timer % 20 == 0 and not ball_in_air:
                    dribble_sound.play()
            if keys[pygame.K_DOWN]:
                player_crouched = True
                player_speed = 2  # Slower when crouching (stealth)
            else:
                player_crouched = False
                player_speed = 5
            if keys[pygame.K_SPACE] and not ball_in_air:  # Shoot ball
                ball_in_air = True
                shoot_sound.play()

            # Ball physics
            if ball_in_air:
                ball_y -= ball_speed
                if ball_y < hoop_y + 10 and hoop_x - 10 < ball_x < hoop_x + 10:
                    ball_in_air = False  # Score!
                    ball_x, ball_y = player_x + 20, player_y
                elif ball_y < 0:
                    ball_in_air = False  # Reset ball if it misses
                    ball_x, ball_y = player_x + 20, player_y
            else:
                ball_x, ball_y = player_x + 20, player_y

            # Guard movement and simple detection
            guard_x += guard_speed * guard_direction
            if guard_x > WIDTH - 20 or guard_x < 0:
                guard_direction *= -1
            
            # Basic guard detection
            if abs(player_x - guard_x) < 50 and abs(player_y - guard_y) < 50 and not player_crouched:
                alert_sound.play()

            # Drawing
            WINDOW.fill(BLACK)
            pygame.draw.rect(WINDOW, WHITE, (player_x, player_y, 20, 20))  # Player
            pygame.draw.circle(WINDOW, RED, (int(ball_x), int(ball_y)), 10)  # Ball
            pygame.draw.rect(WINDOW, WHITE, (hoop_x, hoop_y, 20, 5))  # Hoop
            pygame.draw.rect(WINDOW, (0, 255, 0), (guard_x, guard_y, 20, 20))  # Guard

            pygame.display.flip()
            clock.tick(60)  # 60 FPS

        pygame.quit()

    game_loop()
else:
    pygame.quit()  # Quit Pygame if user exits via Quit button
