import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 640, 480
BLOCK_SIZE = 20
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the font
font = pygame.font.Font(None, 36)

# Set up the clock
clock = pygame.time.Clock()

class SnakeGame:
    def __init__(self):
        self.snake = [(200, 200), (220, 200), (240, 200)]
        self.direction = 'RIGHT'
        self.apple = self.generate_apple()

    def generate_apple(self):
        while True:
            x = random.randint(0, WIDTH - BLOCK_SIZE) // BLOCK_SIZE * BLOCK_SIZE
            y = random.randint(0, HEIGHT - BLOCK_SIZE) // BLOCK_SIZE * BLOCK_SIZE
            if (x, y) not in self.snake:
                return (x, y)

    def update(self):
        head = self.snake[-1]
        if self.direction == 'UP':
            new_head = (head[0], head[1] - BLOCK_SIZE)
        elif self.direction == 'DOWN':
            new_head = (head[0], head[1] + BLOCK_SIZE)
        elif self.direction == 'LEFT':
            new_head = (head[0] - BLOCK_SIZE, head[1])
        elif self.direction == 'RIGHT':
            new_head = (head[0] + BLOCK_SIZE, head[1])

        if (new_head[0] < 0 or new_head[0] >= WIDTH or
            new_head[1] < 0 or new_head[1] >= HEIGHT or
            new_head in self.snake):
            return False

        self.snake.append(new_head)
        if self.snake[-1] == self.apple:
            self.apple = self.generate_apple()
        else:
            self.snake.pop(0)

        return True

    def draw(self):
        screen.fill(WHITE)

        for x, y in self.snake:
            pygame.draw.rect(screen, RED, (x, y, BLOCK_SIZE, BLOCK_SIZE))

        pygame.draw.rect(screen, (0, 0, 255), (*self.apple, BLOCK_SIZE, BLOCK_SIZE))
        text = font.render(f'Score: {len(self.snake)}', True, (0, 0, 0))
        screen.blit(text, (10, 10))

def main():
    game = SnakeGame()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and game.direction != 'DOWN':
                    game.direction = 'UP'
                elif event.key == pygame.K_DOWN and game.direction != 'UP':
                    game.direction = 'DOWN'
                elif event.key == pygame.K_LEFT and game.direction != 'RIGHT':
                    game.direction = 'LEFT'
                elif event.key == pygame.K_RIGHT and game.direction != 'LEFT':
                    game.direction = 'RIGHT'

        if not game.update():
            break

        game.draw()
        pygame.display.flip()

        clock.tick(10)

if __name__ == '__main__':
    main()
