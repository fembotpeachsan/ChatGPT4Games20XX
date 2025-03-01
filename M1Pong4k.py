import pygame, random

pygame.init()  # Initialize pygame before creating the display

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Screen dimensions
WIDTH = 700
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Game state
done = False
clock = pygame.time.Clock()

class Paddle:
    def __init__(self, x, y):
        self.width = 10
        self.height = 100
        self.x = x
        self.y = y
        self.speed = 5

    def move_up(self):
        self.y -= self.speed
        if self.y < 0:
            self.y = 0
            print("OST: Wall hit - BEEP")

    def move_down(self):
        self.y += self.speed
        if self.y > HEIGHT - self.height:
            self.y = HEIGHT - self.height
            print("OST: Wall hit - BEEP")

    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))

class Ball:
    def __init__(self):
        self.size = 10
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.velocity_x = random.choice([4, -4])
        self.velocity_y = random.randint(-4, 4)

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Wall collision
        if self.y <= 0 or self.y >= HEIGHT - self.size:
            self.velocity_y = -self.velocity_y
            print("OST: Bounce - BOOP")

        # Out of bounds
        if self.x <= 0 or self.x >= WIDTH:
            self.reset()
            print("OST: Point scored - DING")

    def bounce(self):
        self.velocity_x = -self.velocity_x
        self.velocity_y = random.randint(-4, 4)
        print("OST: Paddle hit - PING")

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.velocity_x = random.choice([4, -4])
        self.velocity_y = random.randint(-4, 4)

    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.size, self.size))

# Game objects
player = Paddle(50, HEIGHT // 2 - 50)
opponent = Paddle(WIDTH - 60, HEIGHT // 2 - 50)
ball = Ball()

# Main loop
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # Input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player.move_up()
    if keys[pygame.K_s]:
        player.move_down()

    # Opponent AI
    if opponent.y + opponent.height // 2 > ball.y:
        opponent.move_up()
    if opponent.y + opponent.height // 2 < ball.y:
        opponent.move_down()

    # Ball logic
    ball.update()

    # Collision detection with directional check
    player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
    opponent_rect = pygame.Rect(opponent.x, opponent.y, opponent.width, opponent.height)
    ball_rect = pygame.Rect(ball.x, ball.y, ball.size, ball.size)

    # Bounce only if ball is moving towards the paddle
    if ball_rect.colliderect(player_rect) and ball.velocity_x < 0:
        ball.bounce()
    elif ball_rect.colliderect(opponent_rect) and ball.velocity_x > 0:
        ball.bounce()

    # Draw everything
    screen.fill(BLACK)
    player.draw()
    opponent.draw()
    ball.draw()
    pygame.draw.line(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 5)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
