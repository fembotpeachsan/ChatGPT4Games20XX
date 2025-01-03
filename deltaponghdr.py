import pygame
import numpy as np

class SynthwavePong:
    def __init__(self):
        # Initialize pygame and mixer
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=1)
        
        # Screen setup
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Synthwave Pong")
        
        # Colors
        self.neon_blue = (54, 117, 227)
        self.neon_pink = (255, 20, 147)
        self.neon_green = (50, 205, 50)
        self.black = (0, 0, 0)
        
        # Game objects dimensions
        self.paddle_width = 20  # Changed to be thinner
        self.paddle_height = 100  # Changed to be taller
        self.ball_size = 15
        
        # Initialize game state
        self.reset_game()
        
        # Sound effects
        self.bloop_sound = self.generate_synth_sound(frequency=440, duration=0.1, volume=0.7)
        self.beep_sound = self.generate_synth_sound(frequency=880, duration=0.1, volume=0.7)
        
        # Game control
        self.clock = pygame.time.Clock()
        self.player_score = 0
        self.enemy_score = 0
        self.font = pygame.font.Font(None, 74)
        
    def generate_synth_sound(self, frequency, duration, volume=0.5, sample_rate=44100):
        amplitude = 32767 * volume
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        waveform = amplitude * np.sin(2 * np.pi * frequency * t)
        return pygame.mixer.Sound(buffer=waveform.astype(np.int16).tobytes())
    
    def reset_game(self):
        # Paddle positions
        self.player_paddle_x = self.width - self.paddle_width - 20
        self.enemy_paddle_x = 20
        self.player_paddle_y = (self.height - self.paddle_height) // 2
        self.enemy_paddle_y = (self.height - self.paddle_height) // 2
        
        # Ball position and speed
        self.ball_pos_x = self.width // 2
        self.ball_pos_y = self.height // 2
        self.ball_speed_x = 7 if np.random.random() > 0.5 else -7
        self.ball_speed_y = 7 if np.random.random() > 0.5 else -7
        
        # Game settings
        self.paddle_speed = 8
        self.enemy_speed = 6  # AI paddle speed
        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.player_paddle_y > 0:
            self.player_paddle_y -= self.paddle_speed
        if keys[pygame.K_DOWN] and self.player_paddle_y < self.height - self.paddle_height:
            self.player_paddle_y += self.paddle_speed
    
    def update_enemy_ai(self):
        # Simple AI: Follow the ball
        if self.enemy_paddle_y + self.paddle_height/2 < self.ball_pos_y:
            self.enemy_paddle_y += self.enemy_speed
        elif self.enemy_paddle_y + self.paddle_height/2 > self.ball_pos_y:
            self.enemy_paddle_y -= self.enemy_speed
        
        # Keep paddle within screen bounds
        self.enemy_paddle_y = max(0, min(self.height - self.paddle_height, self.enemy_paddle_y))
    
    def update_ball(self):
        self.ball_pos_x += self.ball_speed_x
        self.ball_pos_y += self.ball_speed_y
        
        # Wall collisions
        if self.ball_pos_y <= 0 or self.ball_pos_y >= self.height:
            self.ball_speed_y *= -1
            self.bloop_sound.play()
        
        # Paddle collisions with improved hit detection
        player_paddle_rect = pygame.Rect(self.player_paddle_x, self.player_paddle_y, 
                                       self.paddle_width, self.paddle_height)
        enemy_paddle_rect = pygame.Rect(self.enemy_paddle_x, self.enemy_paddle_y, 
                                      self.paddle_width, self.paddle_height)
        ball_rect = pygame.Rect(self.ball_pos_x - self.ball_size/2, 
                              self.ball_pos_y - self.ball_size/2,
                              self.ball_size, self.ball_size)
        
        if ball_rect.colliderect(player_paddle_rect) or ball_rect.colliderect(enemy_paddle_rect):
            self.ball_speed_x *= -1
            # Add slight randomization to ball direction
            self.ball_speed_y += (np.random.random() - 0.5) * 2
            self.bloop_sound.play()
        
        # Scoring
        if self.ball_pos_x < 0:
            self.player_score += 1
            self.beep_sound.play()
            self.reset_game()
        elif self.ball_pos_x > self.width:
            self.enemy_score += 1
            self.beep_sound.play()
            self.reset_game()
    
    def draw(self):
        self.screen.fill(self.black)
        
        # Draw paddles
        pygame.draw.rect(self.screen, self.neon_blue, 
                        (self.player_paddle_x, self.player_paddle_y, 
                         self.paddle_width, self.paddle_height))
        pygame.draw.rect(self.screen, self.neon_green, 
                        (self.enemy_paddle_x, self.enemy_paddle_y, 
                         self.paddle_width, self.paddle_height))
        
        # Draw ball
        pygame.draw.circle(self.screen, self.neon_pink, 
                         (int(self.ball_pos_x), int(self.ball_pos_y)), 
                         self.ball_size)
        
        # Draw scores
        player_text = self.font.render(str(self.player_score), True, self.neon_blue)
        enemy_text = self.font.render(str(self.enemy_score), True, self.neon_green)
        self.screen.blit(player_text, (self.width - 100, 50))
        self.screen.blit(enemy_text, (50, 50))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            self.handle_input()
            self.update_enemy_ai()
            self.update_ball()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = SynthwavePong()
    game.run()
