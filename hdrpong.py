import pygame
import sys
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the game window
window_width = 800
window_height = 600
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Pong")

# Set up the game clock
clock = pygame.time.Clock()

# Set up the paddles
paddle_width = 10
paddle_height = 100
paddle_speed = 5
left_paddle = pygame.Rect(50, window_height // 2 - paddle_height // 2, paddle_width, paddle_height)
right_paddle = pygame.Rect(window_width - 50 - paddle_width, window_height // 2 - paddle_height // 2, paddle_width, paddle_height)

# Set up the ball
ball_radius = 10
ball_speed_x = 5
ball_speed_y = 5
max_ball_speed = 7  # Prevent the ball from going too fast
ball = pygame.Rect(window_width // 2 - ball_radius // 2, window_height // 2 - ball_radius // 2, ball_radius, ball_radius)

# Set up the score
left_score = 0
right_score = 0
font = pygame.font.Font(None, 74)

# Function to generate beep sound
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * ((i // (sample_rate // frequency)) % 2)) for i in range(samples)]
    sound_array = np.array(wave, dtype=np.int16)
    sound_array = np.ascontiguousarray(sound_array)  # Ensure the array is C-contiguous
    stereo_sound_array = np.column_stack((sound_array, sound_array))  # Create a 2D array for stereo sound
    sound = pygame.sndarray.make_sound(stereo_sound_array)
    sound.set_volume(0.1)
    return sound

# Load beep sound
beep_sound = generate_beep_sound()

# AI Player Logic (Right paddle moves based on the ball position)
def ai_move_paddle():
    if right_paddle.centery < ball.centery and right_paddle.bottom < window_height:
        right_paddle.y += paddle_speed
    elif right_paddle.centery > ball.centery and right_paddle.top > 0:
        right_paddle.y -= paddle_speed

# Restart prompt
def ask_for_restart():
    while True:
        window.fill((0, 0, 0))
        restart_text = font.render("Restart? Y/N", True, (255, 255, 255))
        window.blit(restart_text, (window_width // 4, window_height // 2))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                if event.key == pygame.K_n:
                    pygame.quit()
                    sys.exit()

# Reset game
def reset_game():
    global left_score, right_score, ball_speed_x, ball_speed_y
    left_score = 0
    right_score = 0
    ball.x = window_width // 2 - ball_radius // 2
    ball.y = window_height // 2 - ball_radius // 2
    ball_speed_x = 5
    ball_speed_y = 5

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get the state of the keys
    keys = pygame.key.get_pressed()

    # Move the left paddle
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= paddle_speed
    if keys[pygame.K_s] and left_paddle.bottom < window_height:
        left_paddle.y += paddle_speed

    # Move the right paddle (AI-controlled)
    ai_move_paddle()

    # Move the ball
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Check for collisions with the walls
    if ball.top <= 0 or ball.bottom >= window_height:
        ball_speed_y *= -1

    if ball.left <= 0:
        right_score += 1
        ball.x = window_width // 2 - ball_radius // 2
        ball.y = window_height // 2 - ball_radius // 2
        ball_speed_x = abs(ball_speed_x)  # Ensure the ball moves towards the right
        ball_speed_y = np.random.choice([-5, 5])  # Reset ball with random Y direction

    if ball.right >= window_width:
        left_score += 1
        ball.x = window_width // 2 - ball_radius // 2
        ball.y = window_height // 2 - ball_radius // 2
        ball_speed_x = -abs(ball_speed_x)  # Ensure the ball moves towards the left
        ball_speed_y = np.random.choice([-5, 5])  # Reset ball with random Y direction

    # Check for collisions with the paddles
    if ball.colliderect(left_paddle):
        ball_speed_x = abs(ball_speed_x)  # Move the ball towards the right
        ball_speed_y += np.random.uniform(-1, 1)  # Add a bit of randomness to the bounce
        ball_speed_x = min(ball_speed_x, max_ball_speed)  # Limit ball speed
        beep_sound.play()  # Play beep sound on collision

    if ball.colliderect(right_paddle):
        ball_speed_x = -abs(ball_speed_x)  # Move the ball towards the left
        ball_speed_y += np.random.uniform(-1, 1)  # Add a bit of randomness to the bounce
        ball_speed_x = max(ball_speed_x, -max_ball_speed)  # Limit ball speed
        beep_sound.play()  # Play beep sound on collision

    # Draw the paddles and the ball
    window.fill((0, 0, 0))  # Clear the screen
    pygame.draw.rect(window, (255, 255, 255), left_paddle)
    pygame.draw.rect(window, (255, 255, 255), right_paddle)
    pygame.draw.ellipse(window, (255, 255, 255), ball)

    # Draw the score
    left_score_text = font.render(str(left_score), True, (255, 255, 255))
    right_score_text = font.render(str(right_score), True, (255, 255, 255))
    window.blit(left_score_text, (window_width // 4, 10))
    window.blit(right_score_text, (window_width * 3 // 4, 10))

    # Check for game over condition
    if left_score >= 5 or right_score >= 5:
        if ask_for_restart():
            reset_game()
        else:
            running = False

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
