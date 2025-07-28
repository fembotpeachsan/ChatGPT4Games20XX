import pygame
from math import sin, pi
from array import array

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Paddle class
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 10, 100)
        self.speed = 5

    def move(self, up_key, down_key):
        keys = pygame.key.get_pressed()
        if keys[up_key]:
            self.rect.y -= self.speed
        if keys[down_key]:
            self.rect.y += self.speed
        self.rect.y = max(0, min(HEIGHT - 100, self.rect.y))

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

# Ball class
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 10, 10)
        self.dx = 4
        self.dy = 4

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

# Generate beep sound
def generate_beep():
    sample_rate = 44100
    freq = 440
    duration = 0.1
    samples = int(sample_rate * duration)
    data = array('h', [int(4000 * sin(2 * pi * freq * t / sample_rate)) for t in range(samples)])
    return pygame.mixer.Sound(data)

beep = generate_beep()

# Main game function
def main():
    clock = pygame.time.Clock()
    player1 = Paddle(20, HEIGHT // 2 - 50)
    player2 = Paddle(WIDTH - 30, HEIGHT // 2 - 50)
    ball = Ball()
    score1 = 0
    score2 = 0
    running = True
    game_over = False

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    # Restart
                    score1 = 0
                    score2 = 0
                    ball.rect.center = (WIDTH // 2, HEIGHT // 2)
                    ball.dx = 4
                    ball.dy = 4
                    game_over = False
                elif event.key == pygame.K_n:
                    running = False

        if not game_over:
            player1.move(pygame.K_w, pygame.K_s)
            player2.move(pygame.K_UP, pygame.K_DOWN)
            ball.move()

            # Ball collisions with walls
            if ball.rect.top <= 0 or ball.rect.bottom >= HEIGHT:
                ball.dy *= -1
                beep.play()

            # Ball collisions with paddles
            if ball.rect.colliderect(player1.rect) or ball.rect.colliderect(player2.rect):
                ball.dx *= -1
                beep.play()

            # Scoring
            if ball.rect.left <= 0:
                score2 += 1
                ball.rect.center = (WIDTH // 2, HEIGHT // 2)
                ball.dx *= -1
            elif ball.rect.right >= WIDTH:
                score1 += 1
                ball.rect.center = (WIDTH // 2, HEIGHT // 2)
                ball.dx *= -1

            # Check win condition
            if score1 >= 5 or score2 >= 5:
                game_over = True

            # Draw elements
            player1.draw()
            player2.draw()
            ball.draw()

            # Draw scores
            font = pygame.font.Font(None, 74)
            text = font.render(str(score1), True, WHITE)
            screen.blit(text, (WIDTH // 4, 10))
            text = font.render(str(score2), True, WHITE)
            screen.blit(text, (WIDTH * 3 // 4, 10))

        if game_over:
            font = pygame.font.Font(None, 50)
            winner = "Player 1" if score1 >= 5 else "Player 2"
            text = font.render(f"Game Over! {winner} wins! Restart? (y/n)", True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
