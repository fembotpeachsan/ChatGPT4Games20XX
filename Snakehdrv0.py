import pygame
import random
from array import array

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)

# Screen dimensions
screen_width = 800
screen_height = 600

# Snake properties
block_size = 10
snake_speed = 15

# Font for displaying score and messages
font_style = pygame.font.SysFont(None, 25)
menu_font_style = pygame.font.SysFont(None, 50)

# Function to display score on screen
def display_score(score):
    value = font_style.render("Your Score: " + str(score), True, white)
    dis.blit(value, [0, 0])

# Function to draw the snake
def draw_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, green, [x[0], x[1], block_size, block_size])

# Function to display a message on the screen
def message(msg, color, font, y_displace=0):
    mesg = font.render(msg, True, color)
    mesg_rect = mesg.get_rect(center=(screen_width / 2, screen_height / 2 + y_displace))
    dis.blit(mesg, mesg_rect)

# Define a function to generate beep sounds with varying frequencies
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * ((i // (sample_rate // frequency)) % 2)) for i in range(samples)]
    sound = pygame.mixer.Sound(buffer=array('h', wave))
    sound.set_volume(0.1)
    return sound

# Create beep sounds
start_sound = generate_beep_sound(880, 0.1)  # A5
eat_sound = generate_beep_sound(440, 0.1)    # A4
game_over_sound = generate_beep_sound(220, 0.1)  # A3

# Main game loop
def game_loop():
    global dis
    dis = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Snake Game')

    game_over = False
    game_close = False
    game_over_sound_played = False

    x1 = screen_width / 2
    y1 = screen_height / 2
    x1_change = 0
    y1_change = 0

    snake_list = []
    snake_length = 1

    foodx = round(random.randrange(0, screen_width - block_size) / 10.0) * 10.0
    foody = round(random.randrange(0, screen_height - block_size) / 10.0) * 10.0

    clock = pygame.time.Clock()

    # Start menu loop
    start_menu = True
    while start_menu:
        dis.fill(black)
        message("Press Z or SPACE to Start", white, menu_font_style)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_z:
                    start_sound.play()
                    start_menu = False

    while not game_over:
        while game_close:
            dis.fill(black)
            message("You Lost! Press C-Play Again or Q-Quit", red, font_style, -50)
            display_score(snake_length - 1)
            pygame.display.update()
            if not game_over_sound_played:
                game_over_sound.play()
                game_over_sound_played = True

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -block_size
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = block_size
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -block_size
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = block_size
                    x1_change = 0

        if x1 >= screen_width or x1 < 0 or y1 >= screen_height or y1 < 0:
            game_close = True
        x1 += x1_change
        y1 += y1_change
        dis.fill(black)
        pygame.draw.rect(dis, red, [foodx, foody, block_size, block_size])
        snake_head = []
        snake_head.append(x1)
        snake_head.append(y1)
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        for x in snake_list[:-1]:
            if x == snake_head:
                game_close = True

        draw_snake(block_size, snake_list)
        display_score(snake_length - 1)

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, screen_width - block_size) / 10.0) * 10.0
            foody = round(random.randrange(0, screen_height - block_size) / 10.0) * 10.0
            snake_length += 1
            eat_sound.play()

        clock.tick(snake_speed)

    pygame.quit()
    quit()

game_loop()
