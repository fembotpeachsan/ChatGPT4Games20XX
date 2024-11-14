# Description: A simple Pong game in Pygame
import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH = 800
HEIGHT = 600
BALL_RADIUS = 10

# Create the game screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up the ball
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_speed_x = -5
ball_speed_y = 5

# Set up the paddles
paddle1_x = 10
paddle1_y = HEIGHT // 2
paddle2_x = WIDTH - 40
paddle2_y = HEIGHT // 2

# Set up the scores
score1 = 0
score2 = 0

# Game loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    # Move the paddles
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        paddle1_y -= 5
    if keys[pygame.K_s]:
        paddle1_y += 5

    if keys[pygame.K_UP]:
        paddle2_y -= 5
    if keys[pygame.K_DOWN]:
        paddle2_y += 5

    # Move the ball
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Collision with top and bottom walls
    if ball_y < 0:
        ball_y = 0
        ball_speed_y *= -1
    elif ball_y > HEIGHT - BALL_RADIUS:
        ball_y = HEIGHT - BALL_RADIUS
        ball_speed_y *= -1

    # Collision with left and right paddles
    if (ball_x < paddle1_x + 10 and 
            ball_y > paddle1_y - 50 and 
            ball_y < paddle1_y + 50):
        ball_x = paddle1_x + 10
        ball_speed_x *= -1

    if (ball_x > paddle2_x - 20 and 
            ball_y > paddle2_y - 50 and 
            ball_y < paddle2_y + 50):
        ball_x = paddle2_x - 20
        ball_speed_x *= -1

    # Collision with left wall (goal)
    if ball_x < 0:
        score2 += 1
        print("Player 2 scores!")
        ball_x = WIDTH // 2
        ball_y = HEIGHT // 2

    # Collision with right wall (goal)
    if ball_x > WIDTH - BALL_RADIUS:
        score1 += 1
        print("Player 1 scores!")
        ball_x = WIDTH // 2
        ball_y = HEIGHT // 2

    # Draw everything
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, (paddle1_x, paddle1_y - 25, 10, 50))
    pygame.draw.rect(screen, WHITE, (paddle2_x, paddle2_y - 25, 20, 50))
    pygame.draw.ellipse(screen, WHITE, (ball_x, ball_y, BALL_RADIUS * 2, BALL_RADIUS * 2))

    # Draw the scores
    font = pygame.font.Font(None, 36)
    text = font.render(str(score1) + " - " + str(score2), 1, WHITE)
    screen.blit(text, (WIDTH // 2 - 50, 10))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.delay(1000 // 60)

    # Check if a player has won
    if score1 >= 11:
        print("Player 1 wins!")
        break

    if score2 >= 11:
        print("Player 2 wins!")
        break
 #  Path: pacman4k.py
