import pygame
import random
from typing import List, Tuple
import math
import time
from enum import Enum

# Try to import numpy, but provide a fallback if it's not available
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: NumPy not available. Using simplified sound engine.")

class GameState(Enum):
    INTRO = 0
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

class SoundEngine:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
        
        # Dictionary to store sound effects
        self.sounds = {}
        
        # Use numpy for high-quality sound if available
        if NUMPY_AVAILABLE:
            self.sounds = {
                'shoot': self.generate_sound_numpy([440.0], 0.1),
                'explosion': self.generate_sound_numpy([100, 50], 0.2),
                'hit': self.generate_sound_numpy([220.0, 440.0], 0.1),
                'game_over': self.generate_sound_numpy([440.0, 220.0, 110.0], 0.5),
                'menu_select': self.generate_sound_numpy([880.0, 440.0], 0.1)
            }
        else:
            # Fallback to pygame.sndarray for simple sound generation
            try:
                self.sounds = {
                    'shoot': self.generate_sound_pygame(440.0, 0.1),
                    'explosion': self.generate_sound_pygame(100, 0.2),
                    'hit': self.generate_sound_pygame(220.0, 0.1),
                    'game_over': self.generate_sound_pygame(330.0, 0.5),
                    'menu_select': self.generate_sound_pygame(660.0, 0.1)
                }
            except:
                print("Warning: Sound generation failed. Game will run without sound.")

    def generate_sound_numpy(self, frequencies: List[float], duration: float):
        """Generate sound using numpy for best quality"""
        try:
            sample_rate = 44100
            samples = []
            for freq in frequencies:
                t = np.linspace(0, duration, int(sample_rate * duration))
                samples.append(np.sin(2 * np.pi * freq * t))
            
            mixed = np.mean(samples, axis=0)
            mixed = np.int16(mixed * 32767)
            return pygame.mixer.Sound(mixed.tobytes())
        except Exception as e:
            print(f"Warning: Failed to generate sound with numpy: {e}")
            # Fall back to pygame sound
            return self.generate_sound_pygame(frequencies[0], duration)

    def generate_sound_pygame(self, frequency: float, duration: float):
        """Generate a simple sound using pygame (fallback method)"""
        try:
            sample_rate = 44100
            buffer = []
            max_sample = 32767  # 16-bit
            
            # Generate a simple sine wave
            for i in range(int(sample_rate * duration)):
                t = i / sample_rate  # time in seconds
                sample = int(max_sample * math.sin(2 * math.pi * frequency * t))
                buffer.append(sample)
            
            # Convert buffer to bytes
            try:
                import array
                sound_array = array.array('h', buffer)  # signed short
                return pygame.mixer.Sound(sound_array)
            except:
                return pygame.mixer.Sound(bytes(buffer))
        except Exception as e:
            print(f"Warning: Failed to generate fallback sound: {e}")
            # Create a silent sound as last resort
            return pygame.mixer.Sound(bytes([0] * 1000))

    def play(self, sound_name: str):
        """Play a sound if it exists"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                print(f"Warning: Failed to play sound '{sound_name}'")

class SpaceInvaders:
    def __init__(self):
        pygame.init()
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Space Invaders")
        
        # Initialize sound engine
        self.sound_engine = SoundEngine()
        
        # Colors
        self.COLORS = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'green': (0, 255, 0),
            'red': (255, 0, 0),
            'purple': (128, 0, 128),
            'yellow': (255, 255, 0),
            'blue': (0, 0, 255)
        }
        
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 74)
        self.title_font = pygame.font.Font(None, 100)
        
        # Game state
        self.state = GameState.INTRO
        self.intro_start_time = time.time()
        self.intro_duration = 5  # seconds
        self.high_score = self.load_high_score()
        
        # Initialize game objects
        self.init_game_objects()
        
    def init_game_objects(self):
        # Player
        self.player_width = 50
        self.player_height = 30
        self.player_x = self.WIDTH // 2
        self.player_y = self.HEIGHT - 50
        self.player_speed = 5
        self.player_lives = 3
        
        # Enemies
        self.enemy_rows = 5
        self.enemy_cols = 11
        self.enemy_width = 40
        self.enemy_height = 30
        self.enemy_spacing = 20
        self.enemies: List[dict] = []
        self.enemy_direction = 1
        self.enemy_speed = 1
        self.enemy_descent = 30
        
        # Bullets
        self.bullets: List[dict] = []
        self.enemy_bullets: List[dict] = []
        self.bullet_speed = 7
        self.enemy_bullet_speed = 5
        self.bullet_width = 4
        self.bullet_height = 12
        
        # Game state
        self.score = 0
        self.game_over = False
        self.clock = pygame.time.Clock()
        
        # Initialize enemies
        self.init_enemies()
        
    def init_enemies(self):
        self.enemies = []
        for row in range(self.enemy_rows):
            for col in range(self.enemy_cols):
                enemy = {
                    'x': col * (self.enemy_width + self.enemy_spacing) + 50,
                    'y': row * (self.enemy_height + self.enemy_spacing) + 50,
                    'alive': True,
                    'type': row  # Different enemy types for different rows
                }
                self.enemies.append(enemy)
    
    def draw_player(self):
        # Draw player ship as a triangle
        points = [
            (self.player_x, self.player_y),
            (self.player_x - self.player_width//2, self.player_y + self.player_height),
            (self.player_x + self.player_width//2, self.player_y + self.player_height)
        ]
        pygame.draw.polygon(self.screen, self.COLORS['green'], points)
    
    def draw_enemy(self, enemy):
        if enemy['alive']:
            # Draw different enemy shapes based on row type
            if enemy['type'] == 0:
                # Square with antennae
                pygame.draw.rect(self.screen, self.COLORS['red'],
                               (enemy['x'], enemy['y'], self.enemy_width, self.enemy_height))
                pygame.draw.line(self.screen, self.COLORS['red'],
                               (enemy['x'] + 10, enemy['y']),
                               (enemy['x'] + 10, enemy['y'] - 10))
                pygame.draw.line(self.screen, self.COLORS['red'],
                               (enemy['x'] + 30, enemy['y']),
                               (enemy['x'] + 30, enemy['y'] - 10))
            else:
                # Octagon shape
                points = [
                    (enemy['x'] + 10, enemy['y']),
                    (enemy['x'] + 30, enemy['y']),
                    (enemy['x'] + 40, enemy['y'] + 15),
                    (enemy['x'] + 30, enemy['y'] + 30),
                    (enemy['x'] + 10, enemy['y'] + 30),
                    (enemy['x'], enemy['y'] + 15)
                ]
                pygame.draw.polygon(self.screen, self.COLORS['purple'], points)
    
    def move_enemies(self):
        move_down = False
        for enemy in self.enemies:
            if enemy['alive']:
                if (enemy['x'] >= self.WIDTH - self.enemy_width and self.enemy_direction > 0) or \
                   (enemy['x'] <= 0 and self.enemy_direction < 0):
                    move_down = True
                    break
        
        if move_down:
            self.enemy_direction *= -1
            for enemy in self.enemies:
                enemy['y'] += self.enemy_descent
        else:
            for enemy in self.enemies:
                enemy['x'] += self.enemy_direction * self.enemy_speed
    
    def shoot_bullet(self):
        bullet = {
            'x': self.player_x,
            'y': self.player_y,
            'width': self.bullet_width,
            'height': self.bullet_height
        }
        self.bullets.append(bullet)
        self.sound_engine.play('shoot')
    
    def enemy_shoot(self):
        # Random enemies shoot
        for enemy in self.enemies:
            if enemy['alive'] and random.random() < 0.001:
                bullet = {
                    'x': enemy['x'] + self.enemy_width//2,
                    'y': enemy['y'] + self.enemy_height,
                    'width': self.bullet_width,
                    'height': self.bullet_height
                }
                self.enemy_bullets.append(bullet)
                self.sound_engine.play('shoot')
    
    def check_collisions(self):
        # Check player bullets hitting enemies
        for bullet in self.bullets[:]:
            for enemy in self.enemies:
                if enemy['alive']:
                    if (bullet['x'] > enemy['x'] and 
                        bullet['x'] < enemy['x'] + self.enemy_width and
                        bullet['y'] > enemy['y'] and 
                        bullet['y'] < enemy['y'] + self.enemy_height):
                        enemy['alive'] = False
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        self.score += 100
                        self.sound_engine.play('explosion')
        
        # Check enemy bullets hitting player
        for bullet in self.enemy_bullets[:]:
            if (bullet['x'] > self.player_x - self.player_width//2 and
                bullet['x'] < self.player_x + self.player_width//2 and
                bullet['y'] > self.player_y and
                bullet['y'] < self.player_y + self.player_height):
                self.player_lives -= 1
                self.enemy_bullets.remove(bullet)
                self.sound_engine.play('hit')
                if self.player_lives <= 0:
                    self.game_over = True
                    self.state = GameState.GAME_OVER
                    self.sound_engine.play('game_over')
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
    
    def update_game(self):
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.player_x > self.player_width//2:
            self.player_x -= self.player_speed
        if keys[pygame.K_RIGHT] and self.player_x < self.WIDTH - self.player_width//2:
            self.player_x += self.player_speed
        
        # Update game state
        self.move_enemies()
        self.enemy_shoot()
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet['y'] -= self.bullet_speed
            if bullet['y'] < 0:
                self.bullets.remove(bullet)
        
        for bullet in self.enemy_bullets[:]:
            bullet['y'] += self.enemy_bullet_speed
            if bullet['y'] > self.HEIGHT:
                self.enemy_bullets.remove(bullet)
        
        self.check_collisions()
        
        # Check win condition
        if not any(enemy['alive'] for enemy in self.enemies):
            self.state = GameState.GAME_OVER
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
    
    def draw_game(self):
        self.screen.fill(self.COLORS['black'])
        self.draw_player()
        
        # Draw enemies
        for enemy in self.enemies:
            self.draw_enemy(enemy)
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.rect(self.screen, self.COLORS['green'],
                           (bullet['x'], bullet['y'], bullet['width'], bullet['height']))
        
        for bullet in self.enemy_bullets:
            pygame.draw.rect(self.screen, self.COLORS['red'],
                           (bullet['x'], bullet['y'], bullet['width'], bullet['height']))
        
        # Draw score and lives
        score_text = self.font.render(f'Score: {self.score}', True, self.COLORS['white'])
        lives_text = self.font.render(f'Lives: {self.player_lives}', True, self.COLORS['white'])
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 40))

    def draw_intro(self):
        self.screen.fill(self.COLORS['black'])
        current_time = time.time() - self.intro_start_time
        
        # Fade in effect
        alpha = min(255, int(current_time * 255))
        
        # Team Flames text
        team_text = self.title_font.render('TEAM FLAMES', True, self.COLORS['red'])
        team_rect = team_text.get_rect(center=(self.WIDTH/2, self.HEIGHT/2 - 50))
        
        # Year text
        year_text = self.big_font.render('[20XX]', True, self.COLORS['yellow'])
        year_rect = year_text.get_rect(center=(self.WIDTH/2, self.HEIGHT/2 + 20))
        
        # Presents text
        presents_text = self.font.render('PRESENTS', True, self.COLORS['white'])
        presents_rect = presents_text.get_rect(center=(self.WIDTH/2, self.HEIGHT/2 + 80))
        
        # Draw with alpha
        team_surface = pygame.Surface((team_text.get_width(), team_text.get_height()), pygame.SRCALPHA)
        team_surface.fill((255, 0, 0, 0))
        team_text.set_alpha(alpha)
        team_surface.blit(team_text, (0, 0))
        
        year_surface = pygame.Surface((year_text.get_width(), year_text.get_height()), pygame.SRCALPHA)
        year_surface.fill((255, 255, 0, 0))
        year_text.set_alpha(alpha)
        year_surface.blit(year_text, (0, 0))
        
        presents_surface = pygame.Surface((presents_text.get_width(), presents_text.get_height()), pygame.SRCALPHA)
        presents_surface.fill((255, 255, 255, 0))
        presents_text.set_alpha(alpha)
        presents_surface.blit(presents_text, (0, 0))
        
        self.screen.blit(team_text, team_rect)
        self.screen.blit(year_text, year_rect)
        self.screen.blit(presents_text, presents_rect)
        
        # Add some particle effects
        for _ in range(5):
            x = random.randint(0, self.WIDTH)
            y = random.randint(0, self.HEIGHT)
            pygame.draw.circle(self.screen, self.COLORS['yellow'], (x, y), 2)
        
        if current_time >= self.intro_duration:
            self.state = GameState.MENU
            self.sound_engine.play('menu_select')

    def draw_menu(self):
        self.screen.fill(self.COLORS['black'])
        
        # Title
        title = self.big_font.render('SPACE INVADERS', True, self.COLORS['green'])
        title_rect = title.get_rect(center=(self.WIDTH/2, 150))
        self.screen.blit(title, title_rect)
        
        # Menu options
        start_text = self.font.render('Press SPACE to Start', True, self.COLORS['white'])
        high_score_text = self.font.render(f'High Score: {self.high_score}', True, self.COLORS['blue'])
        quit_text = self.font.render('Press Q to Quit', True, self.COLORS['red'])
        
        self.screen.blit(start_text, (self.WIDTH/2 - 100, 300))
        self.screen.blit(high_score_text, (self.WIDTH/2 - 100, 350))
        self.screen.blit(quit_text, (self.WIDTH/2 - 100, 400))
        
        # Add some particle effects
        for _ in range(3):
            x = random.randint(0, self.WIDTH)
            y = random.randint(0, self.HEIGHT)
            pygame.draw.circle(self.screen, self.COLORS['green'], (x, y), 1)
    
    def draw_game_over(self):
        self.screen.fill(self.COLORS['black'])
        
        # Game over text
        game_over = self.big_font.render('GAME OVER', True, self.COLORS['red'])
        game_over_rect = game_over.get_rect(center=(self.WIDTH/2, self.HEIGHT/2 - 50))
        self.screen.blit(game_over, game_over_rect)
        
        # Score text
        score_text = self.font.render(f'Final Score: {self.score}', True, self.COLORS['white'])
        score_rect = score_text.get_rect(center=(self.WIDTH/2, self.HEIGHT/2 + 20))
        self.screen.blit(score_text, score_rect)
        
        # High score text
        if self.score >= self.high_score:
            high_score_text = self.font.render('NEW HIGH SCORE!', True, self.COLORS['yellow'])
        else:
            high_score_text = self.font.render(f'High Score: {self.high_score}', True, self.COLORS['blue'])
        high_score_rect = high_score_text.get_rect(center=(self.WIDTH/2, self.HEIGHT/2 + 60))
        self.screen.blit(high_score_text, high_score_rect)
        
        # Restart text
        restart_text = self.font.render('Press R to Restart', True, self.COLORS['green'])
        restart_rect = restart_text.get_rect(center=(self.WIDTH/2, self.HEIGHT/2 + 120))
        self.screen.blit(restart_text, restart_rect)
    
    def reset_game(self):
        self.score = 0
        self.player_lives = 3
        self.player_x = self.WIDTH // 2
        self.bullets = []
        self.enemy_bullets = []
        self.init_enemies()
        self.game_over = False
    
    def load_high_score(self):
        try:
            with open('highscore.txt', 'r') as f:
                return int(f.read())
        except:
            return 0
    
    def save_high_score(self):
        with open('highscore.txt', 'w') as f:
            f.write(str(self.high_score))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if self.state == GameState.MENU:
                            self.state = GameState.PLAYING
                            self.sound_engine.play('menu_select')
                        elif self.state == GameState.PLAYING:
                            self.shoot_bullet()
                    elif event.key == pygame.K_r and self.state == GameState.GAME_OVER:
                        self.reset_game()
                        self.state = GameState.PLAYING
                        self.sound_engine.play('menu_select')

            if self.state == GameState.INTRO:
                self.draw_intro()
            elif self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.PLAYING:
                self.update_game()
                self.draw_game()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = SpaceInvaders()
    game.run()
