import pygame
import numpy as np
import tempfile
import wave
import sys

# Function to generate synthwave-style sound
def generate_synthwave_sound(frequency, duration, volume=0.5, sample_rate=44100):
    # Time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Primary sine wave
    primary_wave = np.sin(2 * np.pi * frequency * t) * volume
    
    # Detuned wave for a "fat" synth sound
    detuned_wave = np.sin(2 * np.pi * (frequency * 1.02) * t) * (volume * 0.5)
    
    # Sub oscillator for more bass (an octave lower)
    sub_wave = np.sin(2 * np.pi * (frequency / 2) * t) * (volume * 0.3)
    
    # Low Frequency Oscillator (LFO) for a sweeping effect
    lfo = np.sin(2 * np.pi * 0.5 * t) * 0.2
    modulated_wave = (primary_wave + detuned_wave + sub_wave) * (1.0 + lfo)
    
    # Add a touch of noise for texture
    noise = (np.random.normal(0, 0.005, len(t))) * volume * 0.2
    wave_data = modulated_wave + noise
    
    # Ensure the values are within the allowed range
    wave_data = np.clip(wave_data, -1, 1)
    wave_data = (wave_data * 32767).astype(np.int16)  # Convert to 16-bit PCM format
    
    # Create a temporary .wav file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
        with wave.open(f.name, 'w') as wave_file:
            wave_file.setnchannels(1)  # Mono
            wave_file.setsampwidth(2)  # 16 bits per sample
            wave_file.setframerate(sample_rate)
            wave_file.writeframes(wave_data.tobytes())
        return f.name

# Function to display a message on the screen
def display_message(screen, message, font_size=74, y_offset=0):
    font = pygame.font.Font(None, font_size)
    text = font.render(message, True, WHITE)
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2 + y_offset))

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("[Pong 1.0.0a] By CatsanHDR")

# Set up the clock for FPS control
clock = pygame.time.Clock()
fps = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Paddle dimensions
paddle_width = 20
paddle_height = 100
paddle_speed = 5

# Ball dimensions and speed
ball_radius = 10
initial_ball_speed_x = 4
initial_ball_speed_y = 4

# Paddle positions (constant x positions)
paddle1_x = 30
paddle2_x = screen_width - 50

# Score variables
score1 = 0
score2 = 0

# Function to reset the game (without resetting scores)
def reset_game():
    global paddle1_y, paddle2_y, ball_x, ball_y, ball_speed_x, ball_speed_y
    paddle1_y = screen_height // 2 - paddle_height // 2
    paddle2_y = screen_height // 2 - paddle_height // 2
    ball_x, ball_y = screen_width // 2, screen_height // 2
    # Randomize initial direction
    ball_speed_x = initial_ball_speed_x if np.random.rand() > 0.5 else -initial_ball_speed_x
    ball_speed_y = initial_ball_speed_y if np.random.rand() > 0.5 else -initial_ball_speed_y

# Initial Paddle and Ball positions
reset_game()

# Generate synthwave beep sound
beep_wav_file = generate_synthwave_sound(frequency=440, duration=0.1)
beep_sound = pygame.mixer.Sound(beep_wav_file)

# Function to display the main menu
def main_menu():
    menu_running = True
    while menu_running:
        screen.fill(BLACK)
        display_message(screen, "Synthwave Pong", font_size=100, y_offset=-150)
        display_message(screen, "Press S to Start or Q to Quit", font_size=50, y_offset=0)
        display_message(screen, "© CatsanHDR - 20XX", font_size=30, y_offset=150)
        display_message(screen, "Credits: Powered by OpenAI", font_size=20, y_offset=200)
        pygame.display.flip()

        # Handle menu events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:  # Start game
                    menu_running = False
                elif event.key == pygame.K_q:  # Quit game
                    pygame.quit()
                    sys.exit()

# Start with the main menu
main_menu()

# --- AI control function ---
def ai_control():
    global paddle2_y
    # Move paddle 2 (AI) towards the ball's y position
    if paddle2_y + paddle_height // 2 < ball_y:
        paddle2_y += (paddle_speed - 2)  # Slightly slower than the player for balance
    elif paddle2_y + paddle_height // 2 > ball_y:
        paddle2_y -= (paddle_speed - 2)  # Slightly slower than the player for balance
    
    # Keep the paddle within the screen bounds
    if paddle2_y < 0:
        paddle2_y = 0
    elif paddle2_y > screen_height - paddle_height:
        paddle2_y = screen_height - paddle_height

# --- Game loop ---
running = True
game_over = False
winner = None  # To keep track of who won

while running:
    clock.tick(fps)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_r:
                    # Reset scores and game state when restarting
                    score1 = 0
                    score2 = 0
                    reset_game()
                    game_over = False
                    winner = None
                elif event.key == pygame.K_q:
                    running = False

    if not game_over:
        # Handle paddle movement for Player 1 (human)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and paddle1_y > 0:
            paddle1_y -= paddle_speed
        if keys[pygame.K_s] and paddle1_y < screen_height - paddle_height:
            paddle1_y += paddle_speed

        # AI control for Player 2
        ai_control()

        # Ball movement
        ball_x += ball_speed_x
        ball_y += ball_speed_y

        # Ball collision with top and bottom walls
        if ball_y - ball_radius <= 0 or ball_y + ball_radius >= screen_height:
            ball_speed_y *= -1
            beep_sound.play()  # Play sound on collision

        # Ball collision with paddles
        # Player 1 Paddle
        if (ball_x - ball_radius <= paddle1_x + paddle_width and
                paddle1_y < ball_y < paddle1_y + paddle_height):
            ball_speed_x *= -1
            beep_sound.play()  # Play sound on collision

        # Player 2 Paddle
        if (ball_x + ball_radius >= paddle2_x and
                paddle2_y < ball_y < paddle2_y + paddle_height):
            ball_speed_x *= -1
            beep_sound.play()  # Play sound on collision

        # Ball goes out of bounds (reset position and update score)
        if ball_x < 0:
            score2 += 1  # Player 2 scores
            beep_sound.play()  # Optional: Play sound for scoring
            if score2 >= 5:
                game_over = True
                winner = "Player 2"
            reset_game()
        elif ball_x > screen_width:
            score1 += 1  # Player 1 scores
            beep_sound.play()  # Optional: Play sound for scoring
            if score1 >= 5:
                game_over = True
                winner = "Player 1"
            reset_game()

    # --- Drawing ---
    screen.fill(BLACK)  # Clear screen

    if not game_over:
        # Draw paddles
        pygame.draw.rect(screen, WHITE, (paddle1_x, paddle1_y, paddle_width, paddle_height))
        pygame.draw.rect(screen, WHITE, (paddle2_x, paddle2_y, paddle_width, paddle_height))

        # Draw ball
        pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), ball_radius)

        # Draw scores
        font = pygame.font.Font(None, 74)
        score_text = font.render(f"{score1}   {score2}", True, WHITE)
        screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, 20))
    else:
        # Game Over State
        screen.fill(BLACK)
        display_message(screen, "Game Over!", font_size=100, y_offset=-100)
        display_message(screen, f"{winner} Wins!", font_size=50, y_offset=-20)
        display_message(screen, "Press R to Restart or Q to Quit", font_size=40, y_offset=60)
        display_message(screen, "© CatsanHDR - 20XX", font_size=30, y_offset=150)
        display_message(screen, "Credits: Powered by OpenAI", font_size=20, y_offset=200)

    # Update display
    pygame.display.flip()

pygame.quit()
   
