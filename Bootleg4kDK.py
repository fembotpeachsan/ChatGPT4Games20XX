import pygame
import sys
import random

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize the sound mixer

# Screen setup
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Donkey Kong")
clock = pygame.time.Clock()

# Sound generation function
def generate_square_wave(frequency, duration, volume=0.5):
    sample_rate = 44100
    period = sample_rate // frequency
    high = int(32767 * volume)
    low = -high
    total_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(total_samples):
        if (i % period) < (period // 2):
            samples.append(high)
        else:
            samples.append(low)
    
    # Convert samples to bytes
    buf = bytearray()
    for s in samples:
        buf.extend(s.to_bytes(2, 'little', signed=True))
    
    return pygame.mixer.Sound(buffer=bytes(buf))

# Create sound effects
jump_sound = generate_square_wave(880, 0.1)
hurt_sound = generate_square_wave(220, 0.3)
climb_sound = generate_square_wave(440, 0.05)
win_sound = generate_square_wave(1320, 0.5)
game_over_sound = generate_square_wave(110, 0.5)
barrel_roll_sound = generate_square_wave(600, 0.05)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
WIN = 3

class Player:
    def __init__(self):
        self.width = 20
        self.height = 30
        self.x = 50
        self.y = HEIGHT - 50
        self.speed = 5
        self.jump_power = 15
        self.vel_y = 0
        self.is_jumping = False
        self.on_ladder = False
        self.direction = 1
        self.lives = 3
        self.score = 0
        self.prev_on_ladder = False  # Track ladder state for sound

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, 10))
        pygame.draw.rect(screen, WHITE, (self.x + 5, self.y + 5, 5, 5))

    def move(self, platforms, ladders):
        keys = pygame.key.get_pressed()
        prev_y = self.y

        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.direction = -1
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.direction = 1

        self.x = max(0, min(WIDTH - self.width, self.x))

        if keys[pygame.K_UP] and not self.is_jumping and not self.on_ladder:
            self.vel_y = -self.jump_power
            self.is_jumping = True

        self.on_ladder = False
        for ladder in ladders:
            if (self.x + self.width > ladder.x and 
                self.x < ladder.x + ladder.width and
                self.y + self.height > ladder.y and 
                self.y < ladder.y + ladder.height):
                
                if keys[pygame.K_UP]:
                    self.y -= 3
                if keys[pygame.K_DOWN]:
                    self.y += 3
                self.on_ladder = True
                break

        if not self.on_ladder:
            self.vel_y += 1
            self.y += self.vel_y
            on_ground = False
            for platform in platforms:
                if (self.y + self.height >= platform.y and 
                    self.y + self.height <= platform.y + 10 and
                    self.x + self.width > platform.x and 
                    self.x < platform.x + platform.width):
                    
                    self.y = platform.y - self.height
                    self.is_jumping = False
                    self.vel_y = 0
                    on_ground = True
                    break
            if not on_ground and not self.is_jumping:
                self.is_jumping = True

class Platform:
    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width

    def draw(self):
        pygame.draw.rect(screen, BROWN, (self.x, self.y, self.width, 10))

class Ladder:
    def __init__(self, x, y, height):
        self.x = x
        self.y = y
        self.width = 20
        self.height = height

    def draw(self):
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
        for i in range(5):
            pygame.draw.rect(screen, BLACK, (self.x, self.y + i * (self.height//5), self.width, 3))

class Barrel:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = 2
        self.direction = 1
        self.falling = False
        self.vel_y = 0

    def draw(self):
        pygame.draw.ellipse(screen, BROWN, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x + 5, self.y + 5, 10, 2))

    def update(self, platforms):
        if not self.falling:
            self.x += self.speed * self.direction
            on_platform = False
            for platform in platforms:
                if (self.y + self.height >= platform.y and 
                    self.y + self.height <= platform.y + 10 and
                    self.x + self.width > platform.x and 
                    self.x < platform.x + platform.width):
                    
                    on_platform = True
                    if self.x <= platform.x or self.x + self.width >= platform.x + platform.width:
                        self.direction *= -1
                        self.falling = True
                    break
            if not on_platform:
                self.falling = True
        else:
            self.vel_y += 0.5
            self.y += self.vel_y
            for platform in platforms:
                if (self.y + self.height >= platform.y and 
                    self.y + self.height <= platform.y + 10 and
                    self.x + self.width > platform.x and 
                    self.x < platform.x + platform.width):
                    
                    self.y = platform.y - self.height
                    self.falling = False
                    self.vel_y = 0
                    break

class DonkeyKong:
    def __init__(self):
        self.x = 100
        self.y = 50
        self.width = 60
        self.height = 60
        self.animation_frame = 0
        self.barrel_cooldown = 0

    def draw(self):
        pygame.draw.rect(screen, BROWN, (self.x, self.y, self.width, self.height))
        if self.animation_frame < 15:
            pygame.draw.rect(screen, BROWN, (self.x - 10, self.y + 20, 10, 10))
            pygame.draw.rect(screen, BROWN, (self.x + self.width, self.y + 20, 10, 10))
        else:
            pygame.draw.rect(screen, BROWN, (self.x - 10, self.y + 10, 10, 20))
            pygame.draw.rect(screen, BROWN, (self.x + self.width, self.y + 10, 10, 20))
        self.animation_frame = (self.animation_frame + 1) % 30

    def update(self, barrels, platforms):
        self.barrel_cooldown -= 1
        if self.barrel_cooldown <= 0 and random.random() < 0.02:
            barrels.append(Barrel(self.x + 30, self.y + 30))
            self.barrel_cooldown = 60

class Princess:
    def __init__(self):
        self.x = WIDTH - 100
        self.y = 50
        self.width = 20
        self.height = 30

    def draw(self):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x + 5, self.y + 5, 5, 5))

def setup_game():
    platforms = [
        Platform(0, HEIGHT - 20, WIDTH),
        Platform(100, HEIGHT - 100, 400),
        Platform(0, HEIGHT - 180, 400),
        Platform(200, HEIGHT - 260, 400),
        Platform(0, HEIGHT - 340, 400)
    ]
    ladders = [
        Ladder(350, HEIGHT - 100, 80),
        Ladder(150, HEIGHT - 180, 80),
        Ladder(250, HEIGHT - 260, 80),
        Ladder(350, HEIGHT - 340, 80)
    ]
    return platforms, ladders, Player(), DonkeyKong(), Princess(), []

def main():
    platforms, ladders, player, dk, princess, barrels = setup_game()
    game_state = MENU
    font = pygame.font.SysFont(None, 36)
    prev_jump_state = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if game_state == MENU and event.key == pygame.K_RETURN:
                    game_state = PLAYING
                if (game_state == GAME_OVER or game_state == WIN) and event.key == pygame.K_r:
                    platforms, ladders, player, dk, princess, barrels = setup_game()
                    game_state = PLAYING

        screen.fill(BLACK)
        keys = pygame.key.get_pressed()

        if game_state == MENU:
            title = font.render("DONKEY KONG", True, RED)
            start = font.render("Press ENTER to Start", True, WHITE)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 50))
            screen.blit(start, (WIDTH//2 - start.get_width()//2, HEIGHT//2 + 50))
        
        elif game_state == PLAYING:
            prev_barrel_count = len(barrels)
            prev_jump_state = player.is_jumping
            prev_lives = player.lives

            player.move(platforms, ladders)
            dk.update(barrels, platforms)

            # Jump sound
            if player.is_jumping and not prev_jump_state:
                jump_sound.play()

            # Barrel throw sound
            if len(barrels) > prev_barrel_count:
                barrel_roll_sound.play()

            # Ladder climbing sound
            if player.on_ladder and (keys[pygame.K_UP] or keys[pygame.K_DOWN]):
                climb_sound.play()

            for barrel in barrels[:]:
                barrel.update(platforms)
                if (player.x < barrel.x + barrel.width and
                    player.x + player.width > barrel.x and
                    player.y < barrel.y + barrel.height and
                    player.y + player.height > barrel.y):
                    
                    player.lives -= 1
                    hurt_sound.play()
                    barrels.remove(barrel)
                    if player.lives <= 0:
                        game_over_sound.play()
                        game_state = GAME_OVER

            if (player.x < princess.x + princess.width and
                player.x + player.width > princess.x and
                player.y < princess.y + princess.height and
                player.y + player.height > princess.y):
                
                win_sound.play()
                game_state = WIN

            barrels = [b for b in barrels if b.y < HEIGHT]

            # Draw game objects
            for platform in platforms:
                platform.draw()
            for ladder in ladders:
                ladder.draw()
            for barrel in barrels:
                barrel.draw()
            dk.draw()
            princess.draw()
            player.draw()

            # HUD
            lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
            score_text = font.render(f"Score: {player.score}", True, WHITE)
            screen.blit(lives_text, (10, 10))
            screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))
        
        elif game_state == GAME_OVER:
            game_over = font.render("GAME OVER", True, RED)
            restart = font.render("Press R to Restart", True, WHITE)
            screen.blit(game_over, (WIDTH//2 - game_over.get_width()//2, HEIGHT//2 - 50))
            screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 50))
        
        elif game_state == WIN:
            win = font.render("YOU WIN!", True, YELLOW)
            restart = font.render("Press R to Restart", True, WHITE)
            screen.blit(win, (WIDTH//2 - win.get_width()//2, HEIGHT//2 - 50))
            screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 50))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
