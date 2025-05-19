import pygame
import random
import array # Required for generating sound byte arrays
import sys # For sys.exit()

# --- Constants ---
# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128) # For the middle line

# Paddle properties
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 80
PADDLE_SPEED_AI = 4 # AI paddle speed

# Ball properties
BALL_RADIUS = 8
INITIAL_BALL_SPEED_X = 4 # Initial horizontal speed
INITIAL_BALL_SPEED_Y = 4 # Initial vertical speed
MAX_BALL_SPEED_Y_FACTOR = 1.5 # To prevent ball from going too vertical after many hits

# Game properties
FPS = 60
WINNING_SCORE = 5

# --- Audio Constants ---
SAMPLE_RATE = 22050  # Samples per second for audio
AUDIO_FORMAT = -16   # Signed 16-bit audio
AUDIO_CHANNELS = 1   # Mono audio
AUDIO_BUFFER = 512   # Audio buffer size, smaller can mean less latency

# Sound effect definitions
PADDLE_HIT_FREQ = 440  # A4 note
PADDLE_HIT_DUR = 60    # Milliseconds
WALL_HIT_FREQ = 880    # A5 note (octave higher than paddle)
WALL_HIT_DUR = 40      # Milliseconds (shorter than paddle)
SCORE_FREQ = 660       # E5 note
SCORE_DUR = 200        # Milliseconds (longer for emphasis)
SOUND_VOLUME = 0.1     # Master volume for generated sounds (0.0 to 1.0)

# --- Initialization ---
pygame.init()

# Initialize Pygame Mixer
try:
    pygame.mixer.init(frequency=SAMPLE_RATE, size=AUDIO_FORMAT, channels=AUDIO_CHANNELS, buffer=AUDIO_BUFFER)
    print("Pygame mixer initialized successfully.")
except pygame.error as e:
    print(f"Cannot initialize Pygame mixer: {e}. Game will run without sound.")
    # Create a dummy mixer object if initialization fails, so sound calls don't crash
    class DummyMixer:
        def get_init(self): return None
        def quit(self): pass # Add quit method for dummy
    pygame.mixer = DummyMixer() # Replace actual mixer with dummy

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong - Mouse Control with Atari Sounds")

# Clock for controlling FPS
clock = pygame.time.Clock()

# Font for score display
try:
    score_font = pygame.font.Font(None, 74) # Default system font
    small_font = pygame.font.Font(None, 36) # Default system font for smaller messages
except:
    score_font = pygame.font.SysFont('arial', 74) # Fallback if default font not found
    small_font = pygame.font.SysFont('arial', 36) # Fallback for smaller messages


# --- Sound Generation Function ---
def generate_square_wave_sound(frequency, duration_ms, volume=0.1):
    """
    Generates a pygame.mixer.Sound object for a square wave.
    frequency: Frequency of the wave in Hz.
    duration_ms: Duration of the sound in milliseconds.
    volume: Volume factor (0.0 to 1.0).
    """
    if not pygame.mixer.get_init(): # Check if mixer is available
        class DummySound: # Fallback sound object that does nothing
            def play(self): pass
        return DummySound()

    actual_sample_rate, _, _ = pygame.mixer.get_init() # Get actual sample rate
    if actual_sample_rate is None: # Mixer might be dummy and get_init() might return (None, None, None)
         class DummySound:
            def play(self): pass
         return DummySound()

    num_samples = int(actual_sample_rate * duration_ms / 1000.0)
    if num_samples <= 0:  # Avoid creating an empty sound
        class DummySound:
            def play(self): pass
        return DummySound()

    wave_data = array.array("h", [0] * num_samples)  # 'h' for signed short (16-bit)
    max_amplitude = int(32767 * volume)  # Max amplitude for 16-bit signed audio, scaled by volume

    # Calculate samples per cycle and half cycle for the square wave
    if frequency <= 0: # Avoid division by zero if frequency is invalid
        frequency = 1 # Default to a low frequency to avoid error
    period_in_samples = actual_sample_rate / frequency
    half_period_in_samples = period_in_samples / 2.0

    current_sample_in_cycle = 0.0
    for i in range(num_samples):
        if current_sample_in_cycle < half_period_in_samples:
            wave_data[i] = max_amplitude
        else:
            wave_data[i] = -max_amplitude
        
        current_sample_in_cycle += 1.0
        if current_sample_in_cycle >= period_in_samples:
            current_sample_in_cycle -= period_in_samples # Reset for next cycle

    sound = pygame.mixer.Sound(buffer=wave_data)
    return sound

# --- Create Sound Effects ---
paddle_hit_sound = generate_square_wave_sound(PADDLE_HIT_FREQ, PADDLE_HIT_DUR, SOUND_VOLUME)
wall_hit_sound = generate_square_wave_sound(WALL_HIT_FREQ, WALL_HIT_DUR, SOUND_VOLUME)
score_sound = generate_square_wave_sound(SCORE_FREQ, SCORE_DUR, SOUND_VOLUME)


# --- Game Objects and Variables ---
player_paddle = pygame.Rect(30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ai_paddle = pygame.Rect(SCREEN_WIDTH - 30 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_RADIUS, SCREEN_HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
ball_speed_x = INITIAL_BALL_SPEED_X * random.choice((1, -1))
ball_speed_y = INITIAL_BALL_SPEED_Y * random.choice((1, -1))
player_score = 0
ai_score = 0
game_running = True # Master game loop control

# --- Helper Functions ---
def draw_elements():
    screen.fill(BLACK)
    # Draw dashed middle line
    for i in range(0, SCREEN_HEIGHT, 20): # Dash height 10, gap 10
        pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH // 2 - 1, i, 2, 10))
    pygame.draw.rect(screen, WHITE, player_paddle)
    pygame.draw.rect(screen, WHITE, ai_paddle)
    pygame.draw.ellipse(screen, WHITE, ball) # Draw ball as an ellipse (circle)
    
    # Draw scores
    player_score_text = score_font.render(str(player_score), True, WHITE)
    ai_score_text = score_font.render(str(ai_score), True, WHITE)
    screen.blit(player_score_text, (SCREEN_WIDTH // 4, 20))
    # Adjust AI score text position to be aligned from its right side
    screen.blit(ai_score_text, (SCREEN_WIDTH * 3 // 4 - ai_score_text.get_width(), 20)) 
    pygame.display.flip()

def reset_ball():
    global ball_speed_x, ball_speed_y
    ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    ball_speed_x = INITIAL_BALL_SPEED_X * random.choice((1, -1))
    ball_speed_y = INITIAL_BALL_SPEED_Y * random.choice((1, -1))
    pygame.time.wait(500) # Brief pause before ball starts moving

def display_message(message, sub_message="", game_over_prompt=False):
    """
    Displays a message on the screen and waits for player input.
    Returns:
        "play_again" if game_over_prompt is True and 'Y' is pressed.
        "quit" if game_over_prompt is True and 'N' is pressed, or if QUIT event occurs.
        "continue" if game_over_prompt is False and any key/mouse is pressed.
    """
    screen.fill(BLACK)
    large_font_render = score_font # Use the existing score_font as large_font
    
    text_surface = large_font_render.render(message, True, WHITE)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 30))
    screen.blit(text_surface, text_rect)

    if sub_message:
        sub_text_surface = small_font.render(sub_message, True, WHITE)
        sub_text_rect = sub_text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30))
        screen.blit(sub_text_surface, sub_text_rect)
    
    pygame.display.flip()
    
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit" # Signal to quit the game entirely
            if event.type == pygame.KEYDOWN:
                if game_over_prompt:
                    if event.key == pygame.K_y:
                        return "play_again"
                    if event.key == pygame.K_n:
                        return "quit"
                else: # Not a game over prompt, any key continues
                    return "continue"
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over_prompt:
                # Mouse click only continues for non-game-over prompts (like initial screen)
                return "continue" 
        clock.tick(FPS) # Keep the clock ticking to process events properly

# --- Game Start Screen ---
initial_action = display_message("PONG", "Click or Press Key to Start")
if initial_action == "quit":
    game_running = False # If user closes window on title screen

# --- Main Game Loop ---
while game_running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        if event.type == pygame.MOUSEMOTION:
            player_paddle.centery = event.pos[1]
            # Keep paddle within screen bounds
            if player_paddle.top < 0: player_paddle.top = 0
            if player_paddle.bottom > SCREEN_HEIGHT: player_paddle.bottom = SCREEN_HEIGHT

    if not game_running: # Check if game_running was set to False by display_message
        break

    # --- Game Logic ---
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Ball collision with top/bottom walls
    if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
        ball_speed_y *= -1
        wall_hit_sound.play()
        # Add slight random variation to y speed after wall hit to prevent stale gameplay
        ball_speed_y += random.uniform(-0.2, 0.2)
        # Clamp ball_speed_y to prevent it from becoming too large or too small
        if abs(ball_speed_y) > abs(ball_speed_x * MAX_BALL_SPEED_Y_FACTOR):
            ball_speed_y = ball_speed_x * MAX_BALL_SPEED_Y_FACTOR * (1 if ball_speed_y > 0 else -1)
        elif abs(ball_speed_y) < abs(INITIAL_BALL_SPEED_Y * 0.5): # Prevent ball from getting too slow vertically
             ball_speed_y = INITIAL_BALL_SPEED_Y * 0.5 * (1 if ball_speed_y > 0 else -1)


    # Ball collision with paddles
    collided_with_player = ball.colliderect(player_paddle)
    collided_with_ai = ball.colliderect(ai_paddle)

    if collided_with_player:
        ball_speed_x *= -1
        paddle_hit_sound.play()
        delta_y = ball.centery - player_paddle.centery
        ball_speed_y = delta_y * 0.15 # Adjust y speed based on where it hits the paddle
        ball_speed_x *= 1.05 # Slightly increase ball speed after each paddle hit
        # Ensure ball is placed outside the paddle to prevent sticking
        if ball_speed_x < 0: # Moving left, hit by player (should be moving right now)
             ball.left = player_paddle.right 
        else: # This case should ideally not happen if logic is correct, but as a fallback
             ball.right = player_paddle.left


    if collided_with_ai:
        ball_speed_x *= -1
        paddle_hit_sound.play()
        delta_y = ball.centery - ai_paddle.centery
        ball_speed_y = delta_y * 0.15
        ball_speed_x *= 1.05
        # Ensure ball is placed outside the paddle
        if ball_speed_x > 0: # Moving right, hit by AI (should be moving left now)
            ball.right = ai_paddle.left
        else: # Fallback
            ball.left = ai_paddle.right


    # AI Paddle movement (simple AI)
    # AI tries to center its paddle with the ball's center y-coordinate
    if ai_paddle.centery < ball.centery and abs(ai_paddle.centery - ball.centery) > PADDLE_SPEED_AI / 2 :
        ai_paddle.y += PADDLE_SPEED_AI
    elif ai_paddle.centery > ball.centery and abs(ai_paddle.centery - ball.centery) > PADDLE_SPEED_AI / 2:
        ai_paddle.y -= PADDLE_SPEED_AI
    # Keep AI paddle within screen bounds
    if ai_paddle.top < 0: ai_paddle.top = 0
    if ai_paddle.bottom > SCREEN_HEIGHT: ai_paddle.bottom = SCREEN_HEIGHT

    # Scoring
    if ball.left <= 0: # AI scores
        ai_score += 1
        score_sound.play()
        if ai_score >= WINNING_SCORE:
            action = display_message("GAME OVER", "AI Wins! Play Again? (Y/N)", game_over_prompt=True)
            if action == "play_again":
                player_score = 0
                ai_score = 0
                reset_ball()
            elif action == "quit":
                game_running = False
        else:
            reset_ball() # Reset ball if game is not over

    if ball.right >= SCREEN_WIDTH: # Player scores
        player_score += 1
        score_sound.play()
        if player_score >= WINNING_SCORE:
            action = display_message("GAME OVER", "Player Wins! Play Again? (Y/N)", game_over_prompt=True)
            if action == "play_again":
                player_score = 0
                ai_score = 0
                reset_ball()
            elif action == "quit":
                game_running = False
        else:
            reset_ball() # Reset ball if game is not over

    # --- Drawing ---
    if game_running: # Only draw if the game is supposed to be actively running
        draw_elements()

    # --- Frame Rate Control ---
    clock.tick(FPS)

# --- Quit Pygame ---
pygame.mixer.quit() # Quit the mixer
pygame.quit()
sys.exit() # Ensure the program closes properly

