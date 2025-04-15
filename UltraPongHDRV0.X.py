import pygame
import math
import random
import os
import platform
import subprocess
import time

# Try to import winsound on Windows for beep capabilities
try:
    import winsound
    has_winsound = True
except ImportError:
    has_winsound = False

# Initialize Pygame with error handling
try:
    pygame.init()
except pygame.error as e:
    print(f"Error initializing pygame: {e}")
    exit(1)

# Set up the game window
screen_width = 800
screen_height = 600
try:
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pong - 60 FPS")
except pygame.error as e:
    print(f"Error creating display: {e}")
    pygame.quit()
    exit(1)

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)

# Constants
FPS = 60
MAX_SCORE = 5

# Define paddle properties
paddle_width = 20
paddle_height = 100
paddle_speed = 8
paddle1 = pygame.Rect(50, screen_height // 2 - paddle_height // 2, paddle_width, paddle_height)
paddle2 = pygame.Rect(screen_width - 50 - paddle_width, screen_height // 2 - paddle_height // 2, paddle_width, paddle_height)

# Define ball properties
ball_size = 20
ball_rect = pygame.Rect(screen_width // 2 - ball_size // 2, screen_height // 2 - ball_size // 2, ball_size, ball_size)
ball_x = float(ball_rect.centerx)
ball_y = float(ball_rect.centery)
ball_speed = 5.0
ball_dx = random.choice([-1, 1]) * ball_speed
ball_dy = random.choice([-1, 1]) * ball_speed

# Set up font for score display
try:
    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 72)
except pygame.error:
    print("Warning: Unable to load font. Using system default.")
    try:
        font = pygame.font.SysFont('Arial', 36)
        large_font = pygame.font.SysFont('Arial', 72)
    except:
        print("Error: Could not load any font.")
        pygame.quit()
        exit(1)

# Improved Feedback system with actual sound
class FeedbackSystem:
    def __init__(self):
        self.last_beep_time = 0
        self.beep_duration = 100  # milliseconds
        self.is_beeping = False
        self.beep_color = white
        self.beep_rect = pygame.Rect(0, 0, 0, 0)
        self.beep_type = ""
        self.system = platform.system()
    
    def make_sound(self, freq, duration=100):
        """Make an actual beep sound using system capabilities without media files."""
        try:
            if has_winsound and self.system == 'Windows':
                # Windows - use winsound
                winsound.Beep(freq, duration)
            elif self.system == 'Darwin':  # macOS
                # macOS - use afplay with a generated sound
                subprocess.call(['osascript', '-e', 
                    f'beep {1 if freq < 800 else 2}'])
            elif self.system == 'Linux':
                # Linux - try to use the console bell
                sys_command = f"echo -e '\\a'"
                subprocess.call(sys_command, shell=True)
            else:
                # Fallback - just print to console
                print(f"*{freq}Hz BEEP*")
        except Exception as e:
            print(f"Sound error: {e}")
    
    def beep(self, screen_pos=(0,0), size=10, color=white, type="beep"):
        """Trigger a beep with visual feedback."""
        self.is_beeping = True
        self.last_beep_time = pygame.time.get_ticks()
        self.beep_color = color
        self.beep_rect = pygame.Rect(screen_pos[0]-size//2, screen_pos[1]-size//2, size, size)
        self.beep_type = type
        
        # Make different sounds based on the type of event
        if type == "beep":
            # Paddle hit - higher pitch
            self.make_sound(1000, 50)
        elif type == "boop":
            # Wall hit - lower pitch
            self.make_sound(500, 50)
        elif type == "score":
            # Scoring - series of beeps
            self.make_sound(1500, 75)
        elif type == "gameover":
            # Game over - victory sound
            self.make_sound(800, 100)
            time.sleep(0.1)
            self.make_sound(1000, 100)
            time.sleep(0.1)
            self.make_sound(1200, 150)
    
    def update(self, screen):
        """Update and render visual feedback."""
        current_time = pygame.time.get_ticks()
        if self.is_beeping and current_time - self.last_beep_time < self.beep_duration:
            # Visual feedback
            pygame.draw.rect(screen, self.beep_color, self.beep_rect)
        else:
            self.is_beeping = False

# Create feedback system
feedback = FeedbackSystem()

# Set up the game clock
clock = pygame.time.Clock()

# Initialize scores
score1 = 0  # Left player
score2 = 0  # Right player

# Function to reset the ball to the center with random direction
def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x = screen_width / 2
    ball_y = screen_height / 2
    angle = random.uniform(0.5, 1.0) * math.pi * random.choice([-1, 1])
    ball_dx = ball_speed * math.cos(angle)
    ball_dy = ball_speed * math.sin(angle)
    ball_rect.center = (int(ball_x), int(ball_y))

# Reset the entire game
def reset_game():
    global score1, score2
    score1 = 0
    score2 = 0
    reset_ball()
    paddle1.y = screen_height // 2 - paddle_height // 2
    paddle2.y = screen_height // 2 - paddle_height // 2

# Simple splash screen function
def show_splash_screen():
    splash = True
    # Play startup sound
    feedback.make_sound(800, 200)
    while splash:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                feedback.make_sound(1200, 100)
                splash = False
                
        screen.fill(black)
        title = large_font.render("PONG", True, white)
        instructions = font.render("Press any key to start", True, white)
        controls = font.render("W/S - Left paddle, UP/DOWN - Right paddle", True, white)
        fps_info = font.render("Locked at 60 FPS", True, green)
        
        screen.blit(title, (screen_width//2 - title.get_width()//2, screen_height//3))
        screen.blit(instructions, (screen_width//2 - instructions.get_width()//2, screen_height//2))
        screen.blit(controls, (screen_width//2 - controls.get_width()//2, screen_height//2 + 50))
        screen.blit(fps_info, (screen_width//2 - fps_info.get_width()//2, screen_height//2 + 100))
        
        pygame.display.flip()
        clock.tick(FPS)

# Game over screen function
def show_game_over_screen(winner):
    global running
    
    # Play game over sound
    feedback.beep((screen_width//2, screen_height//2), 50, (255, 215, 0), "gameover")
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    # Restart the game
                    reset_game()
                    feedback.make_sound(1200, 100)
                    waiting = False
                elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                    # Exit the game
                    running = False
                    waiting = False
        
        # Draw the game over screen
        screen.fill(black)
        
        # Draw the game state in the background
        pygame.draw.line(screen, white, (screen_width // 2, 0), (screen_width // 2, screen_height), 2)
        pygame.draw.circle(screen, white, (screen_width // 2, screen_height // 2), 50, 2)
        pygame.draw.rect(screen, white, paddle1)
        pygame.draw.rect(screen, white, paddle2)
        
        # Draw the game over text
        game_over_text = large_font.render("GAME OVER", True, red)
        winner_text = font.render(f"Player {winner} wins!", True, white)
        restart_text = font.render("Play again? (Y/N)", True, white)
        
        screen.blit(game_over_text, (screen_width//2 - game_over_text.get_width()//2, screen_height//3))
        screen.blit(winner_text, (screen_width//2 - winner_text.get_width()//2, screen_height//2))
        screen.blit(restart_text, (screen_width//2 - restart_text.get_width()//2, screen_height//2 + 50))
        
        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

# Show FPS counter function
def show_fps(fps):
    fps_display = font.render(f"{fps:.1f} FPS", True, green)
    screen.blit(fps_display, (10, 10))

# Show the splash screen
show_splash_screen()

# Reset the ball for the start of the game
reset_ball()

# Main game loop
running = True
game_active = True
last_wall_hit_time = 0
last_paddle_hit_time = 0
min_sound_interval = 150  # Minimum milliseconds between sounds to prevent sound spam
frame_times = []  # For FPS calculation

while running:
    start_time = time.time()
    current_time = pygame.time.get_ticks()
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    if game_active:
        # Get keyboard input
        keys = pygame.key.get_pressed()
        # Move paddle1 (left) with W and S keys
        if keys[pygame.K_w]:
            paddle1.y -= paddle_speed
        if keys[pygame.K_s]:
            paddle1.y += paddle_speed
        # Move paddle2 (right) with UP and DOWN arrows
        if keys[pygame.K_UP]:
            paddle2.y -= paddle_speed
        if keys[pygame.K_DOWN]:
            paddle2.y += paddle_speed

        # Keep paddles within screen bounds
        if paddle1.top < 0:
            paddle1.top = 0
        if paddle1.bottom > screen_height:
            paddle1.bottom = screen_height
        if paddle2.top < 0:
            paddle2.top = 0
        if paddle2.bottom > screen_height:
            paddle2.bottom = screen_height

        # Update ball position
        ball_x += ball_dx
        ball_y += ball_dy
        ball_rect.center = (int(ball_x), int(ball_y))

        # Ball collision with top and bottom walls
        if (ball_rect.top <= 0 or ball_rect.bottom >= screen_height) and current_time - last_wall_hit_time > min_sound_interval:
            ball_dy = -ball_dy
            feedback.beep((ball_rect.centerx, ball_rect.centery), 15, (100, 100, 255), "boop")
            last_wall_hit_time = current_time

        # Ball collision with paddles
        paddle_hit = False
        
        if ball_rect.colliderect(paddle1) and current_time - last_paddle_hit_time > min_sound_interval:
            # Calculate reflection angle based on where the ball hits the paddle
            relative_intersect_y = (paddle1.centery - ball_rect.centery) / (paddle1.height / 2)
            bounce_angle = relative_intersect_y * (math.pi / 4)
            ball_dx = abs(ball_dx) * 1.05
            ball_dy = -ball_speed * math.sin(bounce_angle)
            ball_x = paddle1.right + ball_size / 2
            feedback.beep((ball_rect.centerx, ball_rect.centery), 20, (255, 100, 100), "beep")
            last_paddle_hit_time = current_time
            paddle_hit = True
        
        elif ball_rect.colliderect(paddle2) and current_time - last_paddle_hit_time > min_sound_interval:
            relative_intersect_y = (paddle2.centery - ball_rect.centery) / (paddle2.height / 2)
            bounce_angle = relative_intersect_y * (math.pi / 4)
            ball_dx = -abs(ball_dx) * 1.05
            ball_dy = -ball_speed * math.sin(bounce_angle)
            ball_x = paddle2.left - ball_size / 2
            feedback.beep((ball_rect.centerx, ball_rect.centery), 20, (255, 100, 100), "beep")
            last_paddle_hit_time = current_time
            paddle_hit = True

        # Cap maximum ball speed
        max_ball_speed = 15
        current_speed = math.sqrt(ball_dx**2 + ball_dy**2)
        if current_speed > max_ball_speed:
            speed_ratio = max_ball_speed / current_speed
            ball_dx *= speed_ratio
            ball_dy *= speed_ratio

        # Scoring when ball goes out of bounds
        if ball_rect.left <= 0:
            score2 += 1
            feedback.beep((screen_width//2, screen_height//2), 30, (0, 255, 0), "score")
            reset_ball()
            # Check for game over
            if score2 >= MAX_SCORE:
                game_active = False
                show_game_over_screen(2)
        elif ball_rect.right >= screen_width:
            score1 += 1
            feedback.beep((screen_width//2, screen_height//2), 30, (0, 255, 0), "score")
            reset_ball()
            # Check for game over
            if score1 >= MAX_SCORE:
                game_active = False
                show_game_over_screen(1)

    # Draw everything
    screen.fill(black)
    
    # Draw center line
    pygame.draw.line(screen, white, (screen_width // 2, 0), (screen_width // 2, screen_height), 2)
    # Draw center circle
    pygame.draw.circle(screen, white, (screen_width // 2, screen_height // 2), 50, 2)
    
    pygame.draw.rect(screen, white, paddle1)
    pygame.draw.rect(screen, white, paddle2)
    pygame.draw.ellipse(screen, white, ball_rect)

    # Draw scores
    score1_text = font.render(str(score1), True, white)
    score2_text = font.render(str(score2), True, white)
    screen.blit(score1_text, (screen_width // 4, 50))
    screen.blit(score2_text, (3 * screen_width // 4 - score2_text.get_width(), 50))
    
    # Draw score limit indicator
    score_limit_text = font.render(f"First to {MAX_SCORE} wins!", True, green)
    screen.blit(score_limit_text, (screen_width//2 - score_limit_text.get_width()//2, 10))
    
    # Update and draw feedback effects
    feedback.update(screen)
    
    # Calculate and display FPS
    end_time = time.time()
    frame_time = end_time - start_time
    frame_times.append(frame_time)
    # Keep only the last 30 frames for FPS calculation
    if len(frame_times) > 30:
        frame_times.pop(0)
    
    avg_frame_time = sum(frame_times) / len(frame_times)
    current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
    
    show_fps(current_fps)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate at 60 FPS
    clock.tick(FPS)

# Play exit sound
feedback.make_sound(400, 200)

# Clean up and exit
pygame.quit()
