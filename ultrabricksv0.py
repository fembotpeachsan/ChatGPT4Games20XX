import pygame
import random
from array import array

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout with Synthwave")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Paddle properties
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
PADDLE_SPEED = 300

# Ball properties
BALL_SIZE = 20
BALL_SPEED = 200

# Brick properties
BRICK_WIDTH = 70
BRICK_HEIGHT = 30
BRICK_COLORS = [RED, GREEN, BLUE, YELLOW]

# Sound Manager
class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.sounds = {
            'paddle_hit': self.generate_beep_sound(440, 0.1),     # A4
            'brick_break': self.generate_beep_sound(587.33, 0.1), # D5
            'wall_hit': self.generate_beep_sound(329.63, 0.1),    # E4
            'game_over': self.generate_beep_sound(200, 0.5),      # Low tone
            'level_up': self.generate_beep_sound(880, 0.3)        # A5
        }
    
    def generate_beep_sound(self, frequency, duration):
        sample_rate = pygame.mixer.get_init()[0]
        max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
        samples = int(sample_rate * duration)
        wave = [int(max_amplitude * ((i // (sample_rate // frequency)) % 2)) 
                for i in range(samples)]
        sound = pygame.mixer.Sound(buffer=array('h', wave))
        sound.set_volume(0.1)
        return sound
    
    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

# Paddle class
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED

    def update(self, delta_time):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed * delta_time
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed * delta_time

        # Keep paddle within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

# Ball class
class Ball:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BALL_SIZE, BALL_SIZE)
        self.speed_x = BALL_SPEED * random.choice([-1, 1])
        self.speed_y = -BALL_SPEED

    def update(self, delta_time):
        self.rect.x += self.speed_x * delta_time
        self.rect.y += self.speed_y * delta_time

    def draw(self, surface):
        pygame.draw.ellipse(surface, WHITE, self.rect)

# Brick class
class Brick:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# Create bricks
def create_bricks():
    bricks = []
    for row in range(4):
        for col in range(10):
            x = col * (BRICK_WIDTH + 10) + 35
            y = row * (BRICK_HEIGHT + 10) + 50
            color = BRICK_COLORS[row % len(BRICK_COLORS)]
            bricks.append(Brick(x, y, color))
    return bricks

# Main game function
def main():
    clock = pygame.time.Clock()
    sound_manager = SoundManager()

    # Create game objects
    paddle = Paddle(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 50)
    ball = Ball(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2)
    bricks = create_bricks()

    score = 0
    lives = 3
    running = True

    while running:
        delta_time = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update game objects
        paddle.update(delta_time)
        ball.update(delta_time)

        # Ball collision with walls
        if ball.rect.left <= 0 or ball.rect.right >= WIDTH:
            ball.speed_x *= -1
            sound_manager.play('wall_hit')
        if ball.rect.top <= 0:
            ball.speed_y *= -1
            sound_manager.play('wall_hit')

        # Ball collision with paddle
        if ball.rect.colliderect(paddle.rect):
            ball.speed_y = -abs(ball.speed_y)
            sound_manager.play('paddle_hit')

        # Ball collision with bricks
        for brick in bricks[:]:
            if ball.rect.colliderect(brick.rect):
                bricks.remove(brick)
                ball.speed_y *= -1
                score += 10
                sound_manager.play('brick_break')
                break

        # Ball falls below paddle
        if ball.rect.top > HEIGHT:
            lives -= 1
            if lives > 0:
                ball = Ball(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2)
            else:
                sound_manager.play('game_over')
                running = False

        # Draw everything
        screen.fill(BLACK)
        paddle.draw(screen)
        ball.draw(screen)
        for brick in bricks:
            brick.draw(screen)

        # Draw score and lives
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        lives_text = font.render(f'Lives: {lives}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 100, 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
