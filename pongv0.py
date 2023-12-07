import pygame

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Define screen dimensions
WIDTH = 800
HEIGHT = 600

# Define game objects
class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 100
        self.speed = 10

    def move_up(self):
        if self.y - self.speed > 0:
            self.y -= self.speed

    def move_down(self):
        if self.y + self.height + self.speed < HEIGHT:
            self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.dx = 5
        self.dy = 5

    def update(self):
        self.x += self.dx
        self.y += self.dy

        # Collision with walls
        if self.y + self.radius >= HEIGHT or self.y - self.radius <= 0:
            self.dy *= -1

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius)

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.dx *= -1

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()

# Create game objects
paddle_left = Paddle(20, HEIGHT // 2 - 50)
paddle_right = Paddle(WIDTH - 40, HEIGHT // 2 - 50)
ball = Ball(WIDTH // 2, HEIGHT // 2, 10)

# Initialize score
score_left = 0
score_right = 0

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        paddle_left.move_up()
    if keys[pygame.K_s]:
        paddle_left.move_down()

    # AI movement
    if ball.y < paddle_right.y + paddle_right.height // 2:
        paddle_right.move_up()
    elif ball.y > paddle_right.y + paddle_right.height // 2:
        paddle_right.move_down()

    # Update positions
    ball.update()

    # Collision detection
    if paddle_left.get_rect().colliderect(ball.x - ball.radius, ball.y - ball.radius, ball.radius * 2, ball.radius * 2):
        ball.dx *= -1
    if paddle_right.get_rect().colliderect(ball.x - ball.radius, ball.y - ball.radius, ball.radius * 2, ball.radius * 2):
        ball.dx *= -1

    # Scorekeeping
    if ball.x < 0:
        score_right += 1
        ball.reset()
    elif ball.x > WIDTH:
        score_left += 1
        ball.reset()

    # Rendering
    screen.fill(BLACK)
    paddle_left.draw(screen)
    paddle_right.draw(screen)
    ball.draw(screen)

    # Draw scores
    font = pygame.font.SysFont(None, 74)
    text = font.render(str(score_left), 1, WHITE)
    screen.blit(text, (250,10))
    text = font.render(str(score_right), 1, WHITE)
    screen.blit(text, (WIDTH - 250,10))

    pygame.display.flip()
    clock.tick(60)

# Quit pygame
pygame.quit()
