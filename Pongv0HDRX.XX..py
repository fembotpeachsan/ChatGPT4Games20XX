import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 10
PAD_WIDTH = 8
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH // 2
HALF_PAD_HEIGHT = PAD_HEIGHT // 2
LEFT = False
RIGHT = True

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Initialize screen and clock
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()

# Initialize variables
ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_vel = [0, 0]
paddle1_vel = 0
paddle2_vel = 0
paddle1_pos = HEIGHT // 2
paddle2_pos = HEIGHT // 2
score1 = 0
score2 = 0

# Helper functions
def spawn_ball(direction):
    global ball_pos, ball_vel
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    ball_vel = [random.randrange(120, 240) // 60, random.randrange(60, 180) // 60]
    if direction == LEFT:
        ball_vel[0] = -ball_vel[0]

def draw(canvas):
    global paddle1_pos, paddle2_pos, ball_pos, ball_vel, score1, score2
    
    # Update paddle positions
    if paddle1_pos + paddle1_vel >= HALF_PAD_HEIGHT and paddle1_pos + paddle1_vel <= HEIGHT - HALF_PAD_HEIGHT:
        paddle1_pos += paddle1_vel
    if paddle2_pos + paddle2_vel >= HALF_PAD_HEIGHT and paddle2_pos + paddle2_vel <= HEIGHT - HALF_PAD_HEIGHT:
        paddle2_pos += paddle2_vel
    
    # Update ball position
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]
    
    # Collision with top and bottom walls
    if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= HEIGHT - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]
    
    # Collision with paddles
    if (ball_pos[0] <= BALL_RADIUS + PAD_WIDTH and paddle1_pos - HALF_PAD_HEIGHT <= ball_pos[1] <= paddle1_pos + HALF_PAD_HEIGHT) or \
       (ball_pos[0] >= WIDTH - BALL_RADIUS - PAD_WIDTH and paddle2_pos - HALF_PAD_HEIGHT <= ball_pos[1] <= paddle2_pos + HALF_PAD_HEIGHT):
        ball_vel[0] = -ball_vel[0] * 1.1
    
    # Scoring
    if ball_pos[0] <= BALL_RADIUS:
        score2 += 1
        spawn_ball(RIGHT)
    elif ball_pos[0] >= WIDTH - BALL_RADIUS:
        score1 += 1
        spawn_ball(LEFT)
    
    # Draw paddles and ball
    pygame.draw.line(canvas, WHITE, [PAD_WIDTH, 0], [PAD_WIDTH, HEIGHT], 1)
    pygame.draw.line(canvas, WHITE, [WIDTH - PAD_WIDTH, 0], [WIDTH - PAD_WIDTH, HEIGHT], 1)
    pygame.draw.circle(canvas, WHITE, ball_pos, BALL_RADIUS, 0)
    pygame.draw.polygon(canvas, WHITE, [[PAD_WIDTH // 2, paddle1_pos - HALF_PAD_HEIGHT], [PAD_WIDTH // 2, paddle1_pos + HALF_PAD_HEIGHT], [PAD_WIDTH, paddle1_pos + HALF_PAD_HEIGHT], [PAD_WIDTH, paddle1_pos - HALF_PAD_HEIGHT]], 0)
    pygame.draw.polygon(canvas, WHITE, [[WIDTH - PAD_WIDTH // 2, paddle2_pos - HALF_PAD_HEIGHT], [WIDTH - PAD_WIDTH // 2, paddle2_pos + HALF_PAD_HEIGHT], [WIDTH - PAD_WIDTH, paddle2_pos + HALF_PAD_HEIGHT], [WIDTH - PAD_WIDTH, paddle2_pos - HALF_PAD_HEIGHT]], 0)
    
    # Draw scores
    font = pygame.font.Font(None, 48)
    label = font.render(str(score1), True, WHITE)
    canvas.blit(label, (WIDTH // 4, 50))
    label = font.render(str(score2), True, WHITE)
    canvas.blit(label, (WIDTH - WIDTH // 4, 50))

# Initialize
spawn_ball(RIGHT)

# Game loop
while True:
    window.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                paddle1_vel = -5
            elif event.key == pygame.K_s:
                paddle1_vel = 5
            elif event.key == pygame.K_UP:
                paddle2_vel = -5
            elif event.key == pygame.K_DOWN:
                paddle2_vel = 5
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_s:
                paddle1_vel = 0
            elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                paddle2_vel = 0
    
    draw(window)
    pygame.display.update()
    clock.tick(60)
