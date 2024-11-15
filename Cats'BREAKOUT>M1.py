# Description: A simple breakout game with a ball, paddle, and bricks.
### Code
# breakoutv0.py
import pygame
import sys
import random

# Game constants
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 20
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 10
BRICK_WIDTH, BRICK_HEIGHT = 80, 20
FPS = 60

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

class Ball:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - BALL_RADIUS * 2
        self.speed_x = random.choice([-1, 1])
        self.speed_y = random.choice([-1, 1])

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.y > HEIGHT:
            return False
        elif self.y < BALL_RADIUS:
            self.speed_y *= -1
        elif self.x + BALL_RADIUS > WIDTH or self.x - BALL_RADIUS < 0:
            self.speed_x *= -1

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), BALL_RADIUS)

class Paddle:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - PADDLE_HEIGHT * 3
        self.speed_x = 0

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= 5
        elif keys[pygame.K_RIGHT] and self.x < WIDTH - PADDLE_WIDTH:
            self.x += 5

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT))

class Brick:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.removed = False

    def draw(self, screen):
        if not self.removed:
            pygame.draw.rect(screen, RED, (self.x, self.y, BRICK_WIDTH, BRICK_HEIGHT))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    ball = Ball()
    paddle = Paddle()
    bricks = [
        Brick(100, 50),
        Brick(200, 50),
        Brick(300, 50),
        Brick(400, 50),
        Brick(500, 50),
        Brick(100, 150),
        Brick(200, 150),
        Brick(300, 150),
        Brick(400, 150),
        Brick(500, 150),
    ]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        keys = pygame.key.get_pressed()

        paddle.update(keys)
        ball.update()
        for brick in bricks:
            if (brick.x < ball.x + BALL_RADIUS and
                    ball.x - BALL_RADIUS < brick.x + BRICK_WIDTH and
                    brick.y < ball.y + BALL_RADIUS and
                    ball.y - BALL_RADIUS < brick.y + BRICK_HEIGHT):
                brick.removed = True

        screen.fill((0, 0, 0))
        for brick in bricks:
            brick.draw(screen)
        paddle.draw(screen)
        ball.draw(screen)

        if (ball.x > WIDTH or ball.x < 0) and not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            return
        elif ball.y > HEIGHT - BALL_RADIUS * 2:
            return

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
 #       if (snake.body[-1][0] > apple.x and
