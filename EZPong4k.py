import pygame
import sys
import numpy as np
from random import randint, choice

class PongGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Constants
        self.WIDTH = 800
        self.HEIGHT = 600
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.PADDLE_WIDTH = 10
        self.PADDLE_HEIGHT = 100
        self.BALL_RADIUS = 7
        self.SPEED = 5
        self.BORDER_COLOR = (200, 200, 200)
        self.MAX_BALL_SPEED = 15
        
        # Game objects
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)  # Larger font for main menu
        
        # Game states
        self.in_main_menu = True
        
        # Sounds
        self.init_sounds()
        
        self.reset_game()
    
    def init_sounds(self):
        self.ball_hit_sound = self.generate_sine_wave(440, 0.2)  # A4 tone
        self.score_sound = self.generate_sine_wave(220, 0.3)    # A3 tone
        self.game_over_sound = self.generate_sine_wave(55, 1.0) # A1 deep bass
    
    def generate_sine_wave(self, frequency, duration):
        """Generate a sine wave sound at a given frequency and duration."""
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        wave = 0.5 * np.sin(2 * np.pi * frequency * t)  # Sine wave
        wave = np.int16(wave * 32767)  # Convert to 16-bit PCM
        
        sound = pygame.mixer.Sound(wave.tobytes())
        return sound
    
    def play_sound(self, sound):
        """Play a sound."""
        if sound:
            sound.play()
    
    def reset_game(self):
        # Paddle positions
        self.player_y = (self.HEIGHT - self.PADDLE_HEIGHT) // 2
        self.computer_y = (self.HEIGHT - self.PADDLE_HEIGHT) // 2
        
        # Ball properties
        self.ball_x = self.WIDTH // 2
        self.ball_y = self.HEIGHT // 2
        self.ball_speed_x = choice([-1, 1]) * self.SPEED
        self.ball_speed_y = choice([-1, 1]) * randint(3, 5)
        
        # Scores
        self.player_score = 0
        self.computer_score = 0
        
        # Game state
        self.paused = False
        self.game_over = False
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.in_main_menu:
                    if event.key == pygame.K_RETURN:
                        self.in_main_menu = False  # Exit main menu and start game
                else:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
        
        keys = pygame.key.get_pressed()
        if not self.in_main_menu and not self.game_over:
            if keys[pygame.K_UP] and self.computer_y > 0:
                self.computer_y -= self.SPEED
            if keys[pygame.K_DOWN] and self.computer_y + self.PADDLE_HEIGHT < self.HEIGHT:
                self.computer_y += self.SPEED
        
        return True
    
    def update_game_state(self):
        if self.paused or self.game_over or self.in_main_menu:
            return
            
        # Update ball position
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y
        
        # Simple AI for player paddle
        if self.ball_x < self.WIDTH // 2:
            if self.ball_y > self.player_y + self.PADDLE_HEIGHT // 2:
                self.player_y = min(self.player_y + self.SPEED, self.HEIGHT - self.PADDLE_HEIGHT)
            elif self.ball_y < self.player_y + self.PADDLE_HEIGHT // 2:
                self.player_y = max(self.player_y - self.SPEED, 0)
        
        # Ball collision with top and bottom
        if self.ball_y - self.BALL_RADIUS <= 0 or self.ball_y + self.BALL_RADIUS >= self.HEIGHT:
            self.ball_speed_y *= -1
            self.play_sound(self.ball_hit_sound)  # Play hit sound
        
        # Paddle collisions
        self.handle_paddle_collisions()
        
        # Score handling
        if self.ball_x < 0:
            self.computer_score += 1
            self.reset_ball()
            self.play_sound(self.score_sound)  # Play score sound
        elif self.ball_x > self.WIDTH:
            self.player_score += 1
            self.reset_ball()
            self.play_sound(self.score_sound)  # Play score sound
        
        # Check for game over
        if self.player_score >= 10 or self.computer_score >= 10:
            self.game_over = True
            self.play_sound(self.game_over_sound)  # Play game over sound
    
    def handle_paddle_collisions(self):
        # Player paddle collision
        if (self.player_y < self.ball_y < self.player_y + self.PADDLE_HEIGHT) and \
           self.ball_x - self.BALL_RADIUS <= 20:
            self.ball_speed_x = abs(self.ball_speed_x) * 1.1
            self.ball_speed_x = min(self.ball_speed_x, self.MAX_BALL_SPEED)
            self.ball_x = 20 + self.BALL_RADIUS
            self.play_sound(self.ball_hit_sound)  # Play hit sound
            
        # Computer paddle collision
        if (self.computer_y < self.ball_y < self.computer_y + self.PADDLE_HEIGHT) and \
           self.ball_x + self.BALL_RADIUS >= self.WIDTH - 20:
            self.ball_speed_x = -abs(self.ball_speed_x) * 1.1
            self.ball_speed_x = -min(abs(self.ball_speed_x), self.MAX_BALL_SPEED)
            self.ball_x = self.WIDTH - 20 - self.BALL_RADIUS
            self.play_sound(self.ball_hit_sound)  # Play hit sound
    
    def reset_ball(self):
        self.ball_x = self.WIDTH // 2
        self.ball_y = self.HEIGHT // 2
        self.ball_speed_x = choice([-1, 1]) * self.SPEED
        self.ball_speed_y = choice([-1, 1]) * randint(3, 5)
    
    def draw(self):
        self.screen.fill(self.BLACK)
        
        if self.in_main_menu:
            # Draw main menu
            title_text = self.font.render("CATGPT [C] Presents", True, self.WHITE)
            pong_text = self.font.render("PONG! v0.x", True, self.WHITE)
            info_text = self.font.render("Press Enter to Start", True, self.WHITE)
            
            self.screen.blit(title_text, 
                             (self.WIDTH // 2 - title_text.get_width() // 2, self.HEIGHT // 4))
            self.screen.blit(pong_text, 
                             (self.WIDTH // 2 - pong_text.get_width() // 2, self.HEIGHT // 4 + 60))
            self.screen.blit(info_text, 
                             (self.WIDTH // 2 - info_text.get_width() // 2, self.HEIGHT // 2))
        else:
            # Draw game elements
            # Borders
            pygame.draw.rect(self.screen, self.BORDER_COLOR, (0, 0, self.WIDTH, 5))
            pygame.draw.rect(self.screen, self.BORDER_COLOR, (0, 0, 5, self.HEIGHT))
            pygame.draw.rect(self.screen, self.BORDER_COLOR, (self.WIDTH - 5, 0, 5, self.HEIGHT))
            
            # Center line
            for y in range(0, self.HEIGHT, 20):
                pygame.draw.rect(self.screen, self.BORDER_COLOR, 
                                 (self.WIDTH//2 - 2, y, 4, 10))
            
            # Paddles
            pygame.draw.rect(self.screen, self.WHITE, 
                             (10, self.player_y, self.PADDLE_WIDTH, self.PADDLE_HEIGHT))
            pygame.draw.rect(self.screen, self.WHITE, 
                             (self.WIDTH - 20, self.computer_y, self.PADDLE_WIDTH, self.PADDLE_HEIGHT))
            
            # Ball
            pygame.draw.circle(self.screen, self.WHITE, 
                             (int(self.ball_x), int(self.ball_y)), self.BALL_RADIUS)
            
            # Scores
            player_text = self.font.render(f"AI: {self.player_score}", True, self.WHITE)
            computer_text = self.font.render(f"You: {self.computer_score}", True, self.WHITE)
            self.screen.blit(player_text, (self.WIDTH//4, 20))
            self.screen.blit(computer_text, (3*self.WIDTH//4 - computer_text.get_width(), 20))
            
            # Pause/game over text
            if self.paused:
                pause_text = self.font.render("PAUSED - Press P to resume", True, self.WHITE)
                self.screen.blit(pause_text, 
                               (self.WIDTH//2 - pause_text.get_width()//2, self.HEIGHT//2))
            elif self.game_over:
                winner = "AI" if self.player_score >= 10 else "You"
                game_over_text = self.font.render(f"Game Over - {winner} wins!", True, self.WHITE)
                restart_text = self.font.render("Press R to restart", True, self.WHITE)
                self.screen.blit(game_over_text, 
                               (self.WIDTH//2 - game_over_text.get_width()//2, self.HEIGHT//2))
                self.screen.blit(restart_text, 
                               (self.WIDTH//2 - restart_text.get_width()//2, self.HEIGHT//2 + 40))
    
    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            running = self.handle_input()
            if not self.in_main_menu:
                self.update_game_state()
            self.draw()
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PongGame()
    game.run()
