import pygame
import time
import random
import numpy as np

# Initialize Pygame
pygame.init()

# Define colors
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

# Set display dimensions
width = 600
height = 400

# Create the display
dis = pygame.display.set_mode((width, height))
pygame.display.set_caption('Snake Game')

# Set the clock
clock = pygame.time.Clock()

# Set the snake block size and speed
snake_block = 10
snake_speed = 15

# Define the font styles
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

# Initialize the mixer
pygame.mixer.init()

def generate_waveform(frequency, duration, sample_rate=44100, waveform='square'):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    if waveform == 'square':
        wave = 0.5 * (1 + np.sign(np.sin(2 * np.pi * frequency * t)))
    elif waveform == 'triangle':
        wave = 2 * np.abs(2 * (t * frequency - np.floor(0.5 + t * frequency))) - 1
    elif waveform == 'sawtooth':
        wave = 2 * (t * frequency - np.floor(0.5 + t * frequency))
    elif waveform == 'noise':
        wave = np.random.uniform(-1, 1, t.shape)
    else:
        wave = np.sin(2 * np.pi * frequency * t)
    return (wave * 32767).astype(np.int16)

def play_sound(frequency, duration, waveform='square'):
    sample_rate = 44100
    waveform_data = generate_waveform(frequency, duration, sample_rate, waveform)
    stereo_waveform_data = np.column_stack((waveform_data, waveform_data))  # Convert to 2D array for stereo
    sound = pygame.sndarray.make_sound(stereo_waveform_data)
    sound.play()

def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, black, [x[0], x[1], snake_block, snake_block])

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [width / 6, height / 3])

def show_score(score):
    value = score_font.render("Your Score: " + str(score), True, yellow)
    dis.blit(value, [0, 0])

def gameLoop():
    game_over = False
    game_close = False

    x1 = width / 2
    y1 = height / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, height - snake_block) / 10.0) * 10.0

    while not game_over:

        while game_close:
            dis.fill(blue)
            message("You Lost! Press C-Play Again or Q-Quit", red)
            show_score(Length_of_snake - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        if x1 >= width or x1 < 0 or y1 >= height or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change
        dis.fill(blue)
        pygame.draw.rect(dis, green, [foodx, foody, snake_block, snake_block])
        snake_Head = [x1, y1]
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(snake_block, snake_List)
        show_score(Length_of_snake - 1)

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            play_sound(440, 0.1, 'square')  # Play sound when food is eaten
            foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, height - snake_block) / 10.0) * 10.0
            Length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

# Run the game
gameLoop()
