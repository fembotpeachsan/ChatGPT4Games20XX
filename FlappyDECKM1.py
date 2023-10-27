import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BIRD_Y = 300
GRAVITY = 1
JUMP = -15

# Initialize screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Initialize game variables
bird_y = BIRD_Y
bird_velocity = 0
pipes = [(800, 300)]
score = 0
game_over = False

while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bird_velocity = JUMP
            if event.key == pygame.K_r and game_over:
                bird_y = BIRD_Y
                bird_velocity = 0
                pipes = [(800, 300)]
                score = 0
                game_over = False

    if not game_over:
        # Update bird position
        bird_velocity += GRAVITY
        bird_y += bird_velocity

        # Update pipes and score
        new_pipes = []
        for x, gap_y in pipes:
            x -= 5
            if x > -50:
                new_pipes.append((x, gap_y))
                if x == 45:
                    score += 1
        pipes = new_pipes

        # Generate new pipes
        if len(pipes) == 0 or pipes[-1][0] <= 650:
            gap_y = random.randint(100, 400)
            pipes.append((800, gap_y))

        # Collision detection
        for x, gap_y in pipes:
            if 45 < x < 95 and not (gap_y < bird_y < gap_y + 150):
                game_over = True

        # Drawing
        screen.fill((255, 255, 255))  # White background

        # Draw bird
        pygame.draw.circle(screen, (255, 255, 0), (50, int(bird_y)), 15)

        # Draw pipes
        for x, gap_y in pipes:
            pygame.draw.rect(screen, (0, 128, 0), (x, 0, 50, gap_y))
            pygame.draw.rect(screen, (0, 128, 0), (x, gap_y + 150, 50, SCREEN_HEIGHT))

        # Draw score
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (700, 10))
    else:
        # Draw game over screen
        game_over_text = font.render("Game Over! Press 'R' to Restart", True, (255, 0, 0))
        screen.blit(game_over_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))

    pygame.display.update()
    clock.tick(60)
