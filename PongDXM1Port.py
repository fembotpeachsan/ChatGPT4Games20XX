import pygame
import random
import numpy as np
import math
import os

# M1 Optimization Configuration
os.environ['SDL_VIDEODRIVER'] = 'cocoa'  # Optimized for macOS
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Core Game Parameters
SCREEN_SIZE = (1280, 800)
BG_COLOR = (15, 15, 25)
PADDLE_COLOR = (100, 200, 255)
BALL_COLOR = (255, 100, 150)
PADDLE_SIZE = (18, 120)
BALL_RADIUS = 12
# --- MODIFIED: Reduced initial ball speed ---
INIT_BALL_SPEED = 6 # Was 9
# --- MODIFIED: Reduced maximum ball speed ---
MAX_BALL_SPEED = 12 # Was 16
WIN_SCORE = 7

# Enhanced AI System
AI_PROFILES = {
    "easy": (0.7, 0.08, 0.15),
    "medium": (0.85, 0.12, 0.25),
    "hard": (0.95, 0.18, 0.35)
}

# Audio Synthesis Engine
SAMPLE_RATE = 48000
SOUND_PROFILES = {
    'hit': (660, 0.06),
    'score': (880, 0.15),
    'wall': (330, 0.08),
    'power': (1200, 0.1)
}

class QuantumState:
    def __init__(self):
        self.active_players = 1
        self.difficulty = "medium"
        self.paused = False
        self.ball_trail = []
        self.power_ups = []
        self.score = [0, 0]  # Added score attribute initialization
        self.paddle_left = pygame.Rect(80, SCREEN_SIZE[1]//2 - PADDLE_SIZE[1]//2, *PADDLE_SIZE)
        self.paddle_right = pygame.Rect(SCREEN_SIZE[0]-80-PADDLE_SIZE[0], SCREEN_SIZE[1]//2 - PADDLE_SIZE[1]//2, *PADDLE_SIZE)
        # Initialize ball and velocity here to ensure they exist before reset_quantum_field might be called implicitly
        self.ball = pygame.Rect(0, 0, BALL_RADIUS*2, BALL_RADIUS*2) # Placeholder rect
        self.ball_velocity = [0, 0]
        self.reset_quantum_field() # Now call reset

    def reset_quantum_field(self):
        """Resets ball position, velocity, trail, power-ups, and screen shake."""
        self.ball = pygame.Rect(SCREEN_SIZE[0]//2 - BALL_RADIUS, SCREEN_SIZE[1]//2 - BALL_RADIUS,
                              BALL_RADIUS*2, BALL_RADIUS*2)
        # Calculate initial velocity based on the potentially modified INIT_BALL_SPEED
        theta = random.uniform(-math.pi/3, math.pi/3)
        theta += math.pi if random.random() < 0.5 else 0
        self.ball_velocity = [
            INIT_BALL_SPEED * math.cos(theta),
            INIT_BALL_SPEED * math.sin(theta)
        ]
        # Ensure the ball starts within bounds (though center start should be fine)
        self.ball.clamp_ip(pygame.Rect(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1]))
        self.ball_trail.clear()
        self.power_ups.clear()
        self.screen_shake = 0 # Assuming screen_shake might be used elsewhere

def generate_quantum_sound(freq, duration):
    """Waveform synthesis using numpy vectorization"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    # Simple sine wave generation
    wave = 0.5 * np.sin(2 * np.pi * freq * t)
    # Apply an exponential decay envelope
    envelope = np.exp(-t * 5) # Adjust the '5' for faster/slower decay
    wave *= envelope
    # Scale to 16-bit integer range
    wave_scaled = (wave * 32767).astype(np.int16)
    # Create stereo sound by stacking the mono wave
    stereo_wave = np.column_stack((wave_scaled, wave_scaled))
    return pygame.sndarray.make_sound(stereo_wave)

class CyberPongEngine:
    def __init__(self):
        pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, 512) # Pre-initialize mixer
        pygame.init()
        self.display = pygame.display.set_mode(SCREEN_SIZE, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("QUANTUM PONG R1-ZERO")
        self.chrono = pygame.time.Clock()
        self.typeface = pygame.font.Font(None, 84) # Use default font
        self.sound_lib = {k: generate_quantum_sound(*v) for k, v in SOUND_PROFILES.items()}
        self.quantum_state = QuantumState()
        self.particles = [] # Particle system for effects

    def process_energy_input(self):
        """Handles user input like quitting, pausing, and paddle movement."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit # Cleanly exit the program
            if event.type == pygame.KEYDOWN: # Handle key presses once
                if event.key == pygame.K_p:
                    self.quantum_state.paused = not self.quantum_state.paused
                    # No need for wait, just toggle state

        # Continuous key presses for movement (only if not paused)
        if not self.quantum_state.paused:
            keys = pygame.key.get_pressed()
            paddle_speed = 7 # Define paddle speed locally or as a constant

            # Player 1 controls
            if keys[pygame.K_w] and self.quantum_state.paddle_left.top > 0:
                self.quantum_state.paddle_left.y -= paddle_speed
            if keys[pygame.K_s] and self.quantum_state.paddle_left.bottom < SCREEN_SIZE[1]:
                self.quantum_state.paddle_left.y += paddle_speed

            # Player 2 controls (if active)
            if self.quantum_state.active_players == 2:
                if keys[pygame.K_UP] and self.quantum_state.paddle_right.top > 0:
                    self.quantum_state.paddle_right.y -= paddle_speed
                if keys[pygame.K_DOWN] and self.quantum_state.paddle_right.bottom < SCREEN_SIZE[1]:
                    self.quantum_state.paddle_right.y += paddle_speed

            # Clamp paddles to screen bounds after movement
            self.quantum_state.paddle_left.clamp_ip(pygame.Rect(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1]))
            self.quantum_state.paddle_right.clamp_ip(pygame.Rect(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1]))


    def execute_ai_routines(self):
        """Controls the AI paddle if only one player is active."""
        if self.quantum_state.active_players == 1 and not self.quantum_state.paused:
            react_chance, precision_factor, speed_factor = AI_PROFILES[self.quantum_state.difficulty]

            # Only react some of the time based on react_chance
            if random.random() < react_chance:
                # Calculate target position with some random error based on precision
                target_y = self.quantum_state.ball.centery
                paddle_center_offset = random.uniform(-PADDLE_SIZE[1]/2, PADDLE_SIZE[1]/2) * (1 - precision_factor)
                ideal_paddle_top = target_y - PADDLE_SIZE[1]/2 + paddle_center_offset

                # Calculate the difference and move the paddle smoothly
                dy = ideal_paddle_top - self.quantum_state.paddle_right.y
                move_speed = abs(dy) * speed_factor # AI speed depends on distance and profile
                move_speed = min(move_speed, 7) # Cap AI speed similar to player

                # Move paddle
                if dy > 0: # Need to move down
                    self.quantum_state.paddle_right.y += min(dy, move_speed)
                elif dy < 0: # Need to move up
                    self.quantum_state.paddle_right.y += max(dy, -move_speed)

                # Clamp AI paddle to screen bounds
                self.quantum_state.paddle_right.clamp_ip(pygame.Rect(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1]))

    def calculate_quantum_dynamics(self):
        """Updates ball position, handles collisions, and scoring."""
        if self.quantum_state.paused:
            return # Do nothing if paused

        # Update ball trail
        now = pygame.time.get_ticks()
        # Keep trail points only if they are recent (e.g., within 250ms)
        self.quantum_state.ball_trail = [(pos, timestamp) for pos, timestamp in self.quantum_state.ball_trail if now - timestamp < 250]
        # Add current ball position to the trail
        self.quantum_state.ball_trail.append((self.quantum_state.ball.center, now))

        # Update particles (move them and decrease lifetime)
        self.particles = [
            [(p[0][0] + p[1][0], p[0][1] + p[1][1]), p[1], p[2] - 1]
            for p in self.particles if p[2] > 0 # Keep only particles with lifetime > 0
        ]

        # Move the ball
        self.quantum_state.ball.x += self.quantum_state.ball_velocity[0]
        self.quantum_state.ball.y += self.quantum_state.ball_velocity[1]

        # Ball collision with top/bottom walls
        if self.quantum_state.ball.top <= 0:
            self.quantum_state.ball_velocity[1] *= -1
            self.quantum_state.ball.top = 0 # Correct position to prevent sticking
            self.sound_lib['wall'].play()
        elif self.quantum_state.ball.bottom >= SCREEN_SIZE[1]:
            self.quantum_state.ball_velocity[1] *= -1
            self.quantum_state.ball.bottom = SCREEN_SIZE[1] # Correct position
            self.sound_lib['wall'].play()

        # Ball collision with paddles
        collided_paddle = None
        if self.quantum_state.ball.colliderect(self.quantum_state.paddle_left):
            collided_paddle = self.quantum_state.paddle_left
            self.quantum_state.ball.left = collided_paddle.right # Correct position
            direction = 1 # Ball moving right
        elif self.quantum_state.ball.colliderect(self.quantum_state.paddle_right):
            collided_paddle = self.quantum_state.paddle_right
            self.quantum_state.ball.right = collided_paddle.left # Correct position
            direction = -1 # Ball moving left

        if collided_paddle:
            self.sound_lib['hit'].play()

            # Calculate bounce angle based on where it hit the paddle
            offset = (self.quantum_state.ball.centery - collided_paddle.centery) / (collided_paddle.height / 2)
            offset = max(-1, min(1, offset)) # Clamp offset between -1 and 1
            bounce_angle = offset * (math.pi / 3) # Max bounce angle (e.g., 60 degrees)

            # Calculate current speed and potentially increase it
            current_speed = math.hypot(*self.quantum_state.ball_velocity)
            new_speed = min(current_speed * 1.05, MAX_BALL_SPEED) # Increase speed slightly, cap at max

            # Set new velocity based on angle and speed
            self.quantum_state.ball_velocity[0] = direction * new_speed * math.cos(bounce_angle)
            self.quantum_state.ball_velocity[1] = new_speed * math.sin(bounce_angle)

            # Create particles effect on collision
            self.particles += [
                [list(self.quantum_state.ball.center), # Start position
                 [random.uniform(-3, 3), random.uniform(-3, 3)], # Random velocity
                 random.randint(10, 20)] # Random lifetime
                for _ in range(12) # Number of particles
            ]

        # Ball goes out of bounds (scoring)
        scored = False
        if self.quantum_state.ball.left <= 0:
            self.quantum_state.score[1] += 1 # Right player scores
            scored = True
        elif self.quantum_state.ball.right >= SCREEN_SIZE[0]:
            self.quantum_state.score[0] += 1 # Left player scores
            scored = True

        if scored:
            self.sound_lib['score'].play()
            # Check for win condition (optional)
            if self.quantum_state.score[0] >= WIN_SCORE or self.quantum_state.score[1] >= WIN_SCORE:
                print(f"Game Over! Final Score: {self.quantum_state.score[0]} - {self.quantum_state.score[1]}")
                # You might want to add a game over state here instead of just resetting
                self.quantum_state.score = [0, 0] # Reset score for now
            self.quantum_state.reset_quantum_field() # Reset ball for next round


    def render_quantum_field(self):
        """Draws all game elements, trails, particles, and scores."""
        self.display.fill(BG_COLOR) # Clear screen with background color

        # Draw center line (optional, simple dashed line)
        line_gap = 20
        line_height = 10
        for y in range(line_height // 2, SCREEN_SIZE[1], line_gap):
             pygame.draw.rect(self.display, (50, 50, 70), (SCREEN_SIZE[0]//2 - 1, y, 2, line_height))


        # Draw ball trail
        if self.quantum_state.ball_trail:
            num_points = len(self.quantum_state.ball_trail)
            for i, (pos, _) in enumerate(self.quantum_state.ball_trail):
                # Fade alpha based on position in trail (older points are dimmer)
                alpha = int(200 * (i / num_points)) # Adjust 200 for max trail brightness
                # Shrink radius based on position in trail
                radius = BALL_RADIUS * (0.2 + 0.8 * (i / num_points))
                # Create a surface for transparency
                trail_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, (*BALL_COLOR[:3], alpha), (radius, radius), radius)
                self.display.blit(trail_surf, (pos[0] - radius, pos[1] - radius))

        # Draw particles
        for p in self.particles:
            pos, _, lifetime = p
            if lifetime > 0:
                # Fade alpha based on remaining lifetime
                alpha = int(150 * (lifetime / 20)) # Adjust 150 for max particle brightness, 20 is max lifetime
                # Simple white particles
                pygame.draw.circle(self.display, (255, 255, 255, alpha), (int(pos[0]), int(pos[1])), max(1, lifetime // 4)) # Size shrinks

        # Draw paddles
        pygame.draw.rect(self.display, PADDLE_COLOR, self.quantum_state.paddle_left, border_radius=4)
        pygame.draw.rect(self.display, PADDLE_COLOR, self.quantum_state.paddle_right, border_radius=4)

        # Draw ball
        pygame.draw.ellipse(self.display, BALL_COLOR, self.quantum_state.ball)

        # Draw scores
        score_text = self.typeface.render(f"{self.quantum_state.score[0]}  {self.quantum_state.score[1]}", True, (220, 220, 220)) # Slightly off-white
        score_rect = score_text.get_rect(center=(SCREEN_SIZE[0] // 2, 50)) # Position score at top center
        self.display.blit(score_text, score_rect)

        # Draw Pause Overlay if paused
        if self.quantum_state.paused:
            overlay = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA) # Surface with alpha
            overlay.fill((0, 0, 0, 150))  # Semi-transparent black
            self.display.blit(overlay, (0, 0))
            pause_text = self.typeface.render("PAUSED", True, (255, 255, 255))
            pause_rect = pause_text.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2))
            self.display.blit(pause_text, pause_rect)

    def initiate_quantum_loop(self):
        """The main game loop."""
        while True:
            self.process_energy_input()       # Handle inputs
            self.execute_ai_routines()        # Update AI (if applicable)
            self.calculate_quantum_dynamics() # Update game state (ball, collisions)
            self.render_quantum_field()       # Draw everything

            pygame.display.flip()             # Update the full screen
            self.chrono.tick(144)             # Limit frame rate to 144 FPS

# --- Main Execution ---
if __name__ == "__main__":
    try:
        quantum_engine = CyberPongEngine()
        quantum_engine.initiate_quantum_loop()
    except SystemExit:
        print("Exiting Quantum Pong.") # Handle clean exit
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc() # Print detailed error information
        pygame.quit() # Ensure Pygame quits on error
