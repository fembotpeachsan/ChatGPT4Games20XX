import pygame

# Initialize PyGame and set up the window
pygame.init()
width = 800
height = 600
screen = pygame.display.set_mode((width, height))

# Define some colors and variables
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ball_x = 375
ball_y = 295
ball_dx = 1
ball_dy = 1
paddle_height = 50
paddle_width = 50
paddle_x = width // 2 - paddle_width // 2
paddle_y = height - 75
ball_size = 30
paddle_speed = 5

# Define some functions to handle keyboard input and move the paddle
def move_left():
    global paddle_x, paddle_y
    if paddle_x > 0:
        paddle_x -= paddle_speed

def move_right():
    global paddle_x, paddle_y
    if paddle_x < width - paddle_width:
        paddle_x += paddle_speed

# Define a function to draw the ball and paddle
def draw_ball():
    pygame.draw.circle(screen, BLACK, (ball_x, ball_y), ball_size)

def draw_paddle():
    pygame.draw.rect(screen, WHITE, (paddle_x, paddle_y, paddle_width, paddle_height))

# Define the main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                move_left()
            elif event.key == pygame.K_RIGHT:
                move_right()

    # Update the ball and paddle positions
    ball_x += ball_dx
    ball_y += ball_dy
    if ball_x > width - ball_size or ball_x < ball_size:
        ball_dx = -ball_dx
    if ball_y > height - ball_size or ball_y < 0:
        ball_dy = -ball_dy
    paddle_x += (paddle_speed * paddle_direction)

    # Draw everything on the screen
    screen.fill(BLACK)
    draw_ball()
    draw_paddle()
    pygame.display.update()
 make the whole game no png
