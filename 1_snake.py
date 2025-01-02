

import pygame
import random
import math
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Snake Game")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)

# Snake settings
snake_block_size = 10
snake_speed = 15

clock = pygame.time.Clock()

font_style = pygame.font.SysFont(None, 50)

def generate_beep(freq, duration):
    # Create a simple sine wave for the beep sound
    sample_rate = 44100
    samples = (int(duration * sample_rate) // freq) + 1
    waveform = [int(32767.0 * math.sin(2.0 * math.pi * f / sample_rate)) for f in range(samples)]
    
    return pygame.sndarray.make_sound(np.array(waveform, dtype=np.int16))

def play_beep(freq, duration):
    beep_sound = generate_beep(freq, duration)
    beep_sound.play()

def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(screen, black, [x[0], x[1], snake_block, snake_block])

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [screen_width / 6, screen_height / 3])

def gameLoop():
    game_over = False
    game_close = False

    x1 = screen_width // 2
    y1 = screen_height // 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    foodx = round(random.randrange(0, screen_width - snake_block_size) / 10.0) * 10.0
    foody = round(random.randrange(0, screen_height - snake_block_size) / 10.0) * 10.0

    # Initialize mixer
    pygame.mixer.init()

    while not game_over:

        while game_close == True:
            screen.fill(black)
            message("You Lost! Press Q-Quit or C-Play Again", red)
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
                    x1_change = -snake_block_size
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block_size
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block_size
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block_size
                    x1_change = 0

        if x1 >= screen_width or x1 < 0 or y1 >= screen_height or y1 < 0:
            game_close = True
        x1 += x1_change
        y1 += y1_change
        screen.fill(white)
        pygame.draw.rect(screen, red, [foodx, foody, snake_block_size, snake_block_size])
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(snake_block_size, snake_List)

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            play_beep(440, 0.2)  # A beep at 440 Hz for a duration of 0.2 seconds
            foodx = round(random.randrange(0, screen_width - snake_block_size) / 10.0) * 10.0
            foody = round(random.randrange(0, screen_height - snake_block_size) / 10.0) * 10.0
            Length_of_snake += 1

        if game_close:
            play_beep(880, 0.5)  # A beep at 880 Hz for a duration of 0.5 seconds to indicate the end of the game
            pygame.mixer.music.stop()
            break

    pygame.quit()
    quit()

gameLoop()
