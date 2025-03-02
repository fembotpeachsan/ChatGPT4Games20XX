import pygame
import numpy as np
import random
from pygame import gfxdraw
import math

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 600, 400
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 15
BALL_RADIUS = 10
BRICK_WIDTH, BRICK_HEIGHT = 50, 20
BRICK_ROWS, BRICK_COLS = 5, 11
BRICK_SPACING = 5
LIVES = 3
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [
    (255, 0, 0),    # Red
    (255, 165, 0),  # Orange
    (255, 255, 0),  # Yellow
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
]

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout")
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont('Arial', 24)

# Procedural sound generation
def generate_sound(frequency, duration, volume=0.5):
    """Generate a sound at the given frequency and duration"""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    # Create buffer with timecodes
    buf = np.zeros((n_samples, 2), dtype=np.float32)
    max_sample = 2**(16 - 1) - 1
    
    # Generate a sine wave
    for i in range(n_samples):
        t = i / sample_rate
        buf[i][0] = volume * math.sin(2 * math.pi * frequency * t) * max_sample
        buf[i][1] = buf[i][0]  # Copy to right channel
    
    sound = pygame.sndarray.make_sound(buf.astype(np.int16))
    return sound

# Generate sounds for different game events
hit_paddle_sound = generate_sound(440, 0.1)  # A4
hit_brick_sound = generate_sound(660, 0.1)   # E5
lose_life_sound = generate_sound(220, 0.3)   # A3
win_sound = generate_sound(880, 0.5)         # A5

# Background music generator
def generate_background_music():
    """Generate simple background 'music' using sin waves"""
    sample_rate = 44100
    duration = 5.0  # 5 seconds
    n_samples = int(sample_rate * duration)
    
    buf = np.zeros((n_samples, 2), dtype=np.float32)
    max_sample = 2**(16 - 1) - 1
    
    # Base frequencies for a simple chord progression (C major, G major, A minor, F major)
    chord_progression = [
        [261.63, 329.63, 392.00],  # C major
        [392.00, 493.88, 587.33],  # G major
        [220.00, 277.18, 329.63],  # A minor
        [349.23, 440.00, 523.25]   # F major
    ]
    
    chord_duration = duration / len(chord_progression)
    samples_per_chord = int(n_samples / len(chord_progression))
    
    # Generate the chord progression
    for c, chord in enumerate(chord_progression):
        for i in range(samples_per_chord):
            t = i / sample_rate
            sample = 0
            
            # Add each note in the chord
            for freq in chord:
                # Use a slight decay to make it sound more natural
                decay = 1.0 - (i / samples_per_chord) * 0.5
                sample += 0.2 * decay * math.sin(2 * math.pi * freq * t)
                
                # Add a little vibrato
                vibrato_speed = 5.0
                vibrato_depth = 0.005
                sample += 0.1 * decay * math.sin(2 * math.pi * (freq + math.sin(2 * math.pi * vibrato_speed * t) * vibrato_depth * freq) * t)
            
            # Add a simple bass line
            bass_freq = chord[0] / 2
            sample += 0.3 * decay * math.sin(2 * math.pi * bass_freq * t)
            
            # Add some percussion-like sounds every beat
            if int(t * 4) % 1 < 0.1:
                sample += 0.2 * random.random() * math.exp(-t * 20)
            
            # Write to buffer
            idx = c * samples_per_chord + i
            if idx < n_samples:
                buf[idx][0] = sample * max_sample
                buf[idx][1] = sample * max_sample
    
    sound = pygame.sndarray.make_sound(buf.astype(np.int16))
    return sound

# Generate and play background music
bg_music = generate_background_music()
bg_music.set_volume(0.3)
bg_music.play(-1)  # Loop indefinitely

# Game classes
class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = (WIDTH - self.width) // 2
        self.y = HEIGHT - 30
        self.speed = 8
        self.color = WHITE
    
    def move(self, direction):
        if direction == "left":
            self.x = max(0, self.x - self.speed)
        elif direction == "right":
            self.x = min(WIDTH - self.width, self.x + self.speed)
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Add some shading for 3D effect
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 1)
        pygame.draw.line(screen, (200, 200, 200), (self.x, self.y), (self.x + self.width, self.y), 1)

class Ball:
    def __init__(self):
        self.radius = BALL_RADIUS
        self.reset()
        self.color = WHITE
        self.max_speed = 7
        self.trail = []
        self.trail_length = 5
    
    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        
        # Start with a random angle, but make sure it's not too vertical
        angle = random.uniform(0.2, 0.8) * math.pi
        if random.choice([True, False]):
            angle = math.pi - angle  # Go left sometimes
            
        speed = 5
        self.dx = speed * math.cos(angle)
        self.dy = -speed * math.sin(angle)  # Negative so it goes up
    
    def move(self, paddle, bricks):
        # Save position for trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)
        
        # Update position
        self.x += self.dx
        self.y += self.dy
        
        # Wall collision
        if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
            self.dx *= -1
            hit_paddle_sound.play()  # Reuse sound for wall hits
        
        if self.y - self.radius <= 0:
            self.dy *= -1
            hit_paddle_sound.play()  # Reuse sound for ceiling hits
        
        # Paddle collision
        if (self.y + self.radius >= paddle.y and
            self.x >= paddle.x and self.x <= paddle.x + paddle.width):
            
            # Calculate deflection based on where ball hit the paddle
            relative_intersect_x = (paddle.x + (paddle.width / 2)) - self.x
            normalized_intersect_x = relative_intersect_x / (paddle.width / 2)
            bounce_angle = normalized_intersect_x * (math.pi / 3)  # Maximum 60 degree bounce
            
            # Set new direction with slight speed increase
            speed = min(math.sqrt(self.dx**2 + self.dy**2) * 1.05, self.max_speed)
            self.dx = speed * -math.sin(bounce_angle)
            self.dy = speed * -math.cos(bounce_angle)
            
            # Make sure the ball is above the paddle
            self.y = paddle.y - self.radius
            
            hit_paddle_sound.play()
        
        # Check if ball is below paddle (out of bounds)
        if self.y + self.radius > HEIGHT:
            return False
        
        # Brick collision
        for brick in bricks[:]:
            if brick.visible and self.brick_collision(brick):
                brick.visible = False
                hit_brick_sound.play()
                
                # Reflect ball based on which side of the brick was hit
                brick_center_x = brick.x + BRICK_WIDTH / 2
                brick_center_y = brick.y + BRICK_HEIGHT / 2
                
                # Determine if we hit the brick more horizontally or vertically
                dx = abs(self.x - brick_center_x) / (BRICK_WIDTH / 2)
                dy = abs(self.y - brick_center_y) / (BRICK_HEIGHT / 2)
                
                if dx > dy:
                    self.dx *= -1
                else:
                    self.dy *= -1
                
                bricks.remove(brick)
                
        return True
    
    def brick_collision(self, brick):
        # Simple AABB collision detection
        return (self.x + self.radius > brick.x and
                self.x - self.radius < brick.x + BRICK_WIDTH and
                self.y + self.radius > brick.y and
                self.y - self.radius < brick.y + BRICK_HEIGHT)
    
    def draw(self):
        # Draw trail
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i + 1) / len(self.trail))
            radius = int(self.radius * (i + 1) / len(self.trail))
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (radius, radius), radius)
            screen.blit(s, (trail_x - radius, trail_y - radius))
        
        # Draw ball with anti-aliasing
        gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius, self.color)
        gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius, self.color)
        
        # Add a highlight for 3D effect
        highlight_pos = (int(self.x - self.radius/3), int(self.y - self.radius/3))
        gfxdraw.filled_circle(screen, *highlight_pos, max(2, self.radius//4), (220, 220, 220))

class Brick:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.visible = True
        
        # For visual effects
        self.highlights = []
        for _ in range(3):
            px = random.randint(0, BRICK_WIDTH-3)
            py = random.randint(0, BRICK_HEIGHT-3)
            self.highlights.append((px, py, random.randint(1, 2)))
    
    def draw(self):
        if self.visible:
            # Draw main brick
            pygame.draw.rect(screen, self.color, (self.x, self.y, BRICK_WIDTH, BRICK_HEIGHT))
            
            # Draw border
            pygame.draw.rect(screen, BLACK, (self.x, self.y, BRICK_WIDTH, BRICK_HEIGHT), 1)
            
            # Add highlights for 3D effect
            dark_color = tuple(max(0, c - 50) for c in self.color)
            light_color = tuple(min(255, c + 50) for c in self.color)
            
            # Bottom edge (shadow)
            pygame.draw.rect(screen, dark_color, (self.x, self.y + BRICK_HEIGHT - 3, BRICK_WIDTH, 3))
            
            # Top edge (highlight)
            pygame.draw.rect(screen, light_color, (self.x, self.y, BRICK_WIDTH, 2))
            
            # Small random highlights
            for px, py, size in self.highlights:
                pygame.draw.rect(screen, light_color, (self.x + px, self.y + py, size, size))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed = random.uniform(1, 3)
        angle = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.life = 30
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        return self.life > 0
    
    def draw(self):
        alpha = int(255 * (self.life / 30))
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(s, (*self.color, alpha), (0, 0, self.size, self.size))
        screen.blit(s, (int(self.x), int(self.y)))

class Game:
    def __init__(self):
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = []
        self.particles = []
        self.lives = LIVES
        self.score = 0
        self.level = 1
        self.game_state = "playing"  # playing, game_over, win, pause
        self.create_bricks()
    
    def create_bricks(self):
        self.bricks = []
        top_offset = 50  # Start from this y position
        
        for row in range(BRICK_ROWS):
            color = COLORS[row % len(COLORS)]
            for col in range(BRICK_COLS):
                x = col * (BRICK_WIDTH + BRICK_SPACING) + ((WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_SPACING) - BRICK_SPACING)) // 2)
                y = row * (BRICK_HEIGHT + BRICK_SPACING) + top_offset
                self.bricks.append(Brick(x, y, color))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                if event.key == pygame.K_SPACE:
                    if self.game_state == "game_over" or self.game_state == "win":
                        self.__init__()  # Reset the game
                    elif self.game_state == "pause":
                        self.game_state = "playing"
                    else:
                        self.game_state = "pause"
                
                if event.key == pygame.K_r:
                    self.__init__()  # Reset the game
        
        # Continuous key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.paddle.move("left")
        if keys[pygame.K_RIGHT]:
            self.paddle.move("right")
        
        return True
    
    def update(self):
        if self.game_state != "playing":
            return
        
        # Move ball
        ball_in_bounds = self.ball.move(self.paddle, self.bricks)
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Ball out of bounds
        if not ball_in_bounds:
            self.lives -= 1
            lose_life_sound.play()
            
            # Generate particles for visual effect
            for _ in range(20):
                self.particles.append(Particle(self.ball.x, HEIGHT, WHITE))
            
            if self.lives <= 0:
                self.game_state = "game_over"
            else:
                self.ball.reset()
        
        # Check win condition
        if len(self.bricks) == 0:
            if self.game_state != "win":  # Only play sound once
                win_sound.play()
            self.game_state = "win"
    
    def draw(self):
        # Background
        screen.fill(BLACK)
        
        # Draw starfield background
        for i in range(100):
            x = (i * 37 + pygame.time.get_ticks() // 100) % WIDTH
            y = (i * 17 + pygame.time.get_ticks() // 150) % HEIGHT
            size = 1 if i % 4 != 0 else 2
            brightness = 128 + 127 * math.sin(pygame.time.get_ticks() / 1000 + i)
            color = (brightness, brightness, brightness)
            pygame.draw.rect(screen, color, (x, y, size, size))
        
        # Draw game elements
        self.paddle.draw()
        for brick in self.bricks:
            brick.draw()
        self.ball.draw()
        
        # Draw particles
        for particle in self.particles:
            particle.draw()
        
        # Draw UI
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.lives}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))
        screen.blit(level_text, ((WIDTH - level_text.get_width()) // 2, 10))
        
        # Game state messages
        if self.game_state == "pause":
            pause_text = font.render("PAUSED - Press SPACE to continue", True, WHITE)
            text_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(pause_text, text_rect)
        
        elif self.game_state == "game_over":
            over_text = font.render("GAME OVER - Press SPACE to restart", True, WHITE)
            text_rect = over_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(over_text, text_rect)
        
        elif self.game_state == "win":
            win_text = font.render("YOU WIN! - Press SPACE to play again", True, WHITE)
            text_rect = win_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(win_text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        
        while running:
            clock.tick(FPS)
            
            # Process events
            running = self.handle_events()
            
            # Update game state
            self.update()
            
            # Draw everything
            self.draw()
        
        pygame.quit()

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()
