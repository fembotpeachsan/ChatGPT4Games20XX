import pygame
import math
import random
import sys
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
LIGHT_BLUE = (173, 216, 230)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (128, 128, 128)

# Brick colors by row
BRICK_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, CYAN, PINK]

class AudioEngine:
    def __init__(self):
        self.sample_rate = 22050
        self.sounds = {}
        self.generate_sounds()
        
    def generate_tone(self, frequency, duration, wave_type='sine', fade_out=True):
        """Generate a tone with specified parameters"""
        frames = int(duration * self.sample_rate)
        arr = np.zeros(frames)
        
        for i in range(frames):
            if wave_type == 'sine':
                arr[i] = np.sin(2 * np.pi * frequency * i / self.sample_rate)
            elif wave_type == 'square':
                arr[i] = 1 if np.sin(2 * np.pi * frequency * i / self.sample_rate) > 0 else -1
            elif wave_type == 'sawtooth':
                arr[i] = 2 * (i * frequency / self.sample_rate - np.floor(0.5 + i * frequency / self.sample_rate))
            elif wave_type == 'triangle':
                arr[i] = 2 * np.abs(2 * (i * frequency / self.sample_rate - np.floor(0.5 + i * frequency / self.sample_rate))) - 1
        
        # Apply fade out to prevent clicking
        if fade_out and frames > 100:
            fade_frames = min(100, frames // 4)
            for i in range(fade_frames):
                arr[-(i+1)] *= (i / fade_frames)
        
        # Normalize and convert to 16-bit
        arr = (arr * 32767).astype(np.int16)
        
        # Convert to stereo
        stereo_arr = np.zeros((frames, 2), dtype=np.int16)
        stereo_arr[:, 0] = arr
        stereo_arr[:, 1] = arr
        
        return pygame.sndarray.make_sound(stereo_arr)
    
    def generate_noise(self, duration, frequency_range=(100, 1000)):
        """Generate filtered noise for effects"""
        frames = int(duration * self.sample_rate)
        noise = np.random.normal(0, 0.1, frames)
        
        # Simple low-pass filter effect
        for i in range(1, frames):
            noise[i] = noise[i] * 0.7 + noise[i-1] * 0.3
        
        # Apply frequency modulation
        for i in range(frames):
            freq = np.random.uniform(frequency_range[0], frequency_range[1])
            noise[i] *= np.sin(2 * np.pi * freq * i / self.sample_rate)
        
        # Normalize and convert
        noise = (noise * 16383).astype(np.int16)
        stereo_noise = np.zeros((frames, 2), dtype=np.int16)
        stereo_noise[:, 0] = noise
        stereo_noise[:, 1] = noise
        
        return pygame.sndarray.make_sound(stereo_noise)
    
    def generate_sweep(self, start_freq, end_freq, duration, wave_type='sine'):
        """Generate a frequency sweep"""
        frames = int(duration * self.sample_rate)
        arr = np.zeros(frames)
        
        for i in range(frames):
            # Linear frequency sweep
            progress = i / frames
            current_freq = start_freq + (end_freq - start_freq) * progress
            
            if wave_type == 'sine':
                arr[i] = np.sin(2 * np.pi * current_freq * i / self.sample_rate)
            elif wave_type == 'square':
                arr[i] = 1 if np.sin(2 * np.pi * current_freq * i / self.sample_rate) > 0 else -1
        
        # Fade out
        fade_frames = min(50, frames // 4)
        for i in range(fade_frames):
            arr[-(i+1)] *= (i / fade_frames)
        
        arr = (arr * 32767).astype(np.int16)
        stereo_arr = np.zeros((frames, 2), dtype=np.int16)
        stereo_arr[:, 0] = arr
        stereo_arr[:, 1] = arr
        
        return pygame.sndarray.make_sound(stereo_arr)
    
    def generate_sounds(self):
        """Generate all game sounds"""
        # Paddle hit - classic pong sound
        self.sounds['paddle_hit'] = self.generate_tone(220, 0.1, 'square')
        
        # Wall bounce - higher pitched
        self.sounds['wall_bounce'] = self.generate_tone(440, 0.08, 'square')
        
        # Brick destruction sounds - different for each color/row
        brick_freqs = [330, 370, 415, 466, 523, 587, 659, 740]  # Musical scale
        for i, freq in enumerate(brick_freqs):
            # Brick hit with a short sweep down
            self.sounds[f'brick_hit_{i}'] = self.generate_sweep(freq, freq * 0.7, 0.15, 'square')
        
        # Power-up sound (not used yet but ready)
        self.sounds['power_up'] = self.generate_sweep(220, 880, 0.3, 'sine')
        
        # Game over - descending tones
        self.sounds['game_over'] = self.generate_sweep(440, 110, 1.0, 'square')
        
        # Win - ascending victory fanfare
        self.sounds['win'] = self.generate_sweep(220, 880, 0.8, 'sine')
        
        # Ball reset/life lost
        self.sounds['life_lost'] = self.generate_sweep(330, 165, 0.5, 'square')
        
        # Menu blip
        self.sounds['menu_blip'] = self.generate_tone(800, 0.05, 'square')
        
        # Ambient background hum (very quiet)
        self.sounds['ambient'] = self.generate_tone(55, 1.0, 'sine')
        self.sounds['ambient'].set_volume(0.1)
    
    def play_sound(self, sound_name, volume=0.7):
        """Play a sound if it exists"""
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(volume)
            sound.play()
    
    def play_brick_hit(self, brick_row, volume=0.8):
        """Play appropriate brick hit sound based on row"""
        sound_name = f'brick_hit_{brick_row % 8}'
        self.play_sound(sound_name, volume)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.color = color
        self.life = 30
        self.max_life = 30
        self.size = random.randint(2, 4)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # gravity
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            color = (*self.color, alpha)
            # Create a surface for the particle with alpha
            particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (self.size, self.size), self.size)
            screen.blit(particle_surface, (self.x - self.size, self.y - self.size))

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8
        self.vx = random.choice([-4, 4])
        self.vy = -4
        self.max_speed = 8
        self.trail = []
        
    def update(self):
        # Add current position to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
            
        self.x += self.vx
        self.y += self.vy
        
        # Wall collisions
        if self.x <= self.radius or self.x >= SCREEN_WIDTH - self.radius:
            self.vx = -self.vx
            self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
            return 'wall_bounce'
            
        if self.y <= self.radius:
            self.vy = -self.vy
            self.y = self.radius
            return 'wall_bounce'
            
        return None
            
        # Limit speed
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > self.max_speed:
            self.vx = (self.vx / speed) * self.max_speed
            self.vy = (self.vy / speed) * self.max_speed
    
    def draw(self, screen):
        # Draw trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            trail_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (*WHITE, alpha), (self.radius, self.radius), self.radius - 2)
            screen.blit(trail_surface, (tx - self.radius, ty - self.radius))
        
        # Draw ball with glow effect
        for i in range(3):
            glow_radius = self.radius + i * 2
            glow_alpha = 100 - i * 30
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*WHITE, glow_alpha), (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (self.x - glow_radius, self.y - glow_radius))
        
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

class Paddle:
    def __init__(self, x, y):
        self.width = 100
        self.height = 15
        self.x = x - self.width // 2
        self.y = y
        self.target_x = self.x
        
    def update(self, mouse_x):
        self.target_x = mouse_x - self.width // 2
        self.target_x = max(0, min(SCREEN_WIDTH - self.width, self.target_x))
        
        # Smooth movement
        self.x += (self.target_x - self.x) * 0.3
        
    def draw(self, screen):
        # Draw paddle with gradient effect
        for i in range(self.height):
            color_intensity = 255 - (i * 15)
            color = (color_intensity, color_intensity, 255)
            pygame.draw.rect(screen, color, (self.x, self.y + i, self.width, 1))
        
        # Draw highlight
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, 2))

class Brick:
    def __init__(self, x, y, color, points=10):
        self.x = x
        self.y = y
        self.width = 75
        self.height = 20
        self.color = color
        self.points = points
        self.destroyed = False
        
    def draw(self, screen):
        if not self.destroyed:
            # Draw brick with 3D effect
            # Main brick
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            
            # Highlights
            pygame.draw.rect(screen, tuple(min(255, c + 50) for c in self.color), 
                           (self.x, self.y, self.width, 2))
            pygame.draw.rect(screen, tuple(min(255, c + 50) for c in self.color), 
                           (self.x, self.y, 2, self.height))
            
            # Shadows
            pygame.draw.rect(screen, tuple(max(0, c - 50) for c in self.color), 
                           (self.x, self.y + self.height - 2, self.width, 2))
            pygame.draw.rect(screen, tuple(max(0, c - 50) for c in self.color), 
                           (self.x + self.width - 2, self.y, 2, self.height))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Breakout 4K - Full Vibes Edition")
        self.clock = pygame.time.Clock()
        
        # Initialize audio engine
        try:
            self.audio = AudioEngine()
            self.audio_enabled = True
        except:
            print("Audio initialization failed - continuing without sound")
            self.audio_enabled = False
        
        self.reset_game()
        
    def reset_game(self):
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.paddle = Paddle(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.bricks = []
        self.particles = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.won = False
        
        # Create bricks
        rows = 8
        cols = 10
        brick_width = 75
        brick_height = 20
        padding = 5
        start_x = (SCREEN_WIDTH - (cols * (brick_width + padding))) // 2
        start_y = 50
        
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (brick_width + padding)
                y = start_y + row * (brick_height + padding)
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                points = (rows - row) * 10
                self.bricks.append(Brick(x, y, color, points))
    
    def handle_collisions(self):
        # Ball-paddle collision
        if (self.ball.y + self.ball.radius >= self.paddle.y and
            self.ball.y - self.ball.radius <= self.paddle.y + self.paddle.height and
            self.ball.x >= self.paddle.x and
            self.ball.x <= self.paddle.x + self.paddle.width):
            
            if self.ball.vy > 0:  # Only if ball is moving down
                # Calculate hit position on paddle (-1 to 1)
                hit_pos = (self.ball.x - (self.paddle.x + self.paddle.width/2)) / (self.paddle.width/2)
                
                # Reflect ball with angle based on hit position
                self.ball.vy = -abs(self.ball.vy)
                self.ball.vx = hit_pos * 6
                
                # Ensure ball doesn't get stuck in paddle
                self.ball.y = self.paddle.y - self.ball.radius
                
                # Play paddle hit sound
                if self.audio_enabled:
                    self.audio.play_sound('paddle_hit')
        
        # Ball-brick collisions
        for brick in self.bricks:
            if not brick.destroyed:
                if (self.ball.x + self.ball.radius >= brick.x and
                    self.ball.x - self.ball.radius <= brick.x + brick.width and
                    self.ball.y + self.ball.radius >= brick.y and
                    self.ball.y - self.ball.radius <= brick.y + brick.height):
                    
                    # Determine collision side
                    overlap_left = (self.ball.x + self.ball.radius) - brick.x
                    overlap_right = (brick.x + brick.width) - (self.ball.x - self.ball.radius)
                    overlap_top = (self.ball.y + self.ball.radius) - brick.y
                    overlap_bottom = (brick.y + brick.height) - (self.ball.y - self.ball.radius)
                    
                    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                    
                    if min_overlap == overlap_left or min_overlap == overlap_right:
                        self.ball.vx = -self.ball.vx
                    else:
                        self.ball.vy = -self.ball.vy
                    
                    # Destroy brick and add particles
                    brick.destroyed = True
                    self.score += brick.points
                    
                    # Create particles
                    for _ in range(15):
                        px = brick.x + brick.width // 2
                        py = brick.y + brick.height // 2
                        self.particles.append(Particle(px, py, brick.color))
                    
                    # Play brick hit sound based on row
                    if self.audio_enabled:
                        # Calculate which row this brick is in
                        brick_row = int((brick.y - 50) // 25)  # 50 is start_y, 25 is height + padding
                        self.audio.play_brick_hit(brick_row)
                    
                    # Speed up ball slightly
                    self.ball.vx *= 1.02
                    self.ball.vy *= 1.02
                    
                    break
    
    def update(self):
        if not self.game_over and not self.won:
            mouse_x, _ = pygame.mouse.get_pos()
            self.paddle.update(mouse_x)
            
            # Update ball and check for wall bounces
            ball_collision = self.ball.update()
            if ball_collision == 'wall_bounce' and self.audio_enabled:
                self.audio.play_sound('wall_bounce')
            
            self.handle_collisions()
            
            # Update particles
            self.particles = [p for p in self.particles if p.life > 0]
            for particle in self.particles:
                particle.update()
            
            # Check for ball falling off screen
            if self.ball.y > SCREEN_HEIGHT:
                self.lives -= 1
                if self.audio_enabled:
                    self.audio.play_sound('life_lost')
                    
                if self.lives <= 0:
                    self.game_over = True
                    if self.audio_enabled:
                        self.audio.play_sound('game_over')
                else:
                    self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
            
            # Check for win condition
            if all(brick.destroyed for brick in self.bricks):
                self.won = True
                if self.audio_enabled:
                    self.audio.play_sound('win')
    
    def draw(self):
        # Background gradient
        for y in range(SCREEN_HEIGHT):
            color_intensity = int(20 + (y / SCREEN_HEIGHT) * 30)
            color = (color_intensity, color_intensity, color_intensity + 10)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Draw game objects
        for brick in self.bricks:
            brick.draw(self.screen)
        
        for particle in self.particles:
            particle.draw(self.screen)
        
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        
        # Draw UI
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.lives}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 100, 10))
        
        # Draw game over or win message
        if self.game_over:
            big_font = pygame.font.Font(None, 72)
            game_over_text = big_font.render("GAME OVER", True, RED)
            restart_text = font.render("Play Again? Press Y for Yes, N for No", True, WHITE)
            score_text = font.render(f"Final Score: {self.score}", True, YELLOW)
            
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(restart_text, restart_rect)
        
        elif self.won:
            big_font = pygame.font.Font(None, 72)
            win_text = big_font.render("YOU WIN!", True, GREEN)
            score_text = font.render(f"Final Score: {self.score}", True, YELLOW)
            restart_text = font.render("Play Again? Press Y for Yes, N for No", True, WHITE)
            
            text_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            
            self.screen.blit(win_text, text_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(restart_text, restart_rect)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_n:
                    if self.audio_enabled:
                        self.audio.play_sound('menu_blip')
                    return False
                elif event.key == pygame.K_r or event.key == pygame.K_y:
                    if self.audio_enabled:
                        self.audio.play_sound('menu_blip')
                    self.reset_game()
                # Easter egg: Press '5' for instant game over (as requested)
                elif event.key == pygame.K_5:
                    if not self.game_over and not self.won:
                        self.lives = 0
                        self.game_over = True
                        if self.audio_enabled:
                            self.audio.play_sound('game_over')
        return True
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
