import pygame
from pygame.locals import *
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
BIRD_Y_CHANGE = 4
BIRD_START_Y = SCREEN_HEIGHT // 2
BIRD_SIZE = 30
PIPE_WIDTH = 50
PIPE_GAP = 200
PIPE_SPEED = 2

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
BLACK = (0, 0, 0)

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird Clone with Scoring')

bird_y = BIRD_START_Y
bird_dy = 0
pipes = [(SCREEN_WIDTH, SCREEN_HEIGHT // 2 + PIPE_GAP // 2)]
score = 0

font = pygame.font.SysFont(None, 36)

clock = pygame.time.Clock()

def check_collision(bird_y, pipes):
    bird_rect = pygame.Rect(SCREEN_WIDTH // 2 - BIRD_SIZE // 2, bird_y, BIRD_SIZE, BIRD_SIZE)
    for pipe in pipes:
        upper_pipe_rect = pygame.Rect(pipe[0], 0, PIPE_WIDTH, pipe[1] - PIPE_GAP // 2)
        lower_pipe_rect = pygame.Rect(pipe[0], pipe[1] + PIPE_GAP // 2, PIPE_WIDTH, SCREEN_HEIGHT)
        if bird_rect.colliderect(upper_pipe_rect) or bird_rect.colliderect(lower_pipe_rect):
            return True
    return False

running = True
while running:
    screen.fill(WHITE)

    # Check for events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                bird_dy = -BIRD_Y_CHANGE

    # Update bird position
    bird_dy += 0.5  # Adjusted gravity for a more "floaty" feel
    bird_y += bird_dy
    pygame.draw.rect(screen, RED, (SCREEN_WIDTH // 2 - BIRD_SIZE // 2, bird_y, BIRD_SIZE, BIRD_SIZE))

    # Update pipes
    for i in range(len(pipes)):
        pipes[i] = (pipes[i][0] - PIPE_SPEED, pipes[i][1])
        pygame.draw.rect(screen, GREEN, (pipes[i][0], 0, PIPE_WIDTH, pipes[i][1] - PIPE_GAP // 2))
        pygame.draw.rect(screen, GREEN, (pipes[i][0], pipes[i][1] + PIPE_GAP // 2, PIPE_WIDTH, SCREEN_HEIGHT))

    # Remove off-screen pipes
    pipes = [pipe for pipe in pipes if pipe[0] + PIPE_WIDTH > 0]

    # Add new pipes
    if not pipes or pipes[-1][0] < SCREEN_WIDTH - SCREEN_WIDTH // 2.5:
        new_pipe_y = PIPE_GAP + (SCREEN_HEIGHT - 2 * PIPE_GAP) * random.random()
        pipes.append((SCREEN_WIDTH, new_pipe_y))
        score += 1

    # Display score
    score_text = font.render(str(score), True, BLACK)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 50))

    # Check for collision
    if check_collision(bird_y, pipes) or bird_y < 0 or bird_y > SCREEN_HEIGHT:
        running = False

    pygame.display.flip()
    clock.tick(30)  # Reduced frame rate for slower gameplay

pygame.quit()
