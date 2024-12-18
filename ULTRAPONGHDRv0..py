import pygame
import random
import math
import numpy as np
import os
import json

# Initial variables
screen_width = 400
screen_height = 400
snake_color = (0, 255, 0)  # Green
food_color = (255, 0, 0)   # Red
snake_block_size = 20  # Increased snake block size for easier visibility
food_radius = 8  # Changed food radius for better visibility
log_file = "achievements.log"
audio_enabled = True

# Ensure log file exists
if not os.path.exists(log_file):
    with open(log_file, "w") as f:
        json.dump({"achievements": []}, f)

def generate_tone(frequency, duration, volume=0.5, sample_rate=44100):
    """Generate a simple tone (sine wave) as a playable pygame sound."""
    n_samples = int(round(duration * sample_rate))
    t = np.linspace(0, duration, n_samples, endpoint=False)
    waveform = volume * np.sin(2.0 * math.pi * frequency * t)
    waveform_int16 = np.int16(waveform * 32767)
    waveform_int16_stereo = np.column_stack((waveform_int16, waveform_int16))
    sound = pygame.sndarray.make_sound(waveform_int16_stereo)
    return sound

def draw_snake(screen, snake_list):
    for x, y in snake_list:
        pygame.draw.rect(screen, snake_color, [x, y, snake_block_size, snake_block_size])

def draw_food(screen, food_x, food_y):
    pygame.draw.circle(screen, food_color, (food_x, food_y), food_radius)

def save_achievement(achievement):
    """Save achievements to a persistent log."""
    with open(log_file, "r") as f:
        data = json.load(f)
    if achievement not in data["achievements"]:
        data["achievements"].append(achievement)
        with open(log_file, "w") as f:
            json.dump(data, f)

def load_achievements():
    """Load achievements from the log file."""
    with open(log_file, "r") as f:
        data = json.load(f)
    return data["achievements"]

def main_game():
    """Core Snake game logic."""
    global audio_enabled
    pygame.mixer.init(frequency=44100, size=-16, channels=2)
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Snake Game')
    clock = pygame.time.Clock()

    snake_x = screen_width / 2
    snake_y = screen_height / 2
    snake_list = []
    snake_length = 1

    food_x = round(random.randrange(0, screen_width - food_radius) / 10.0) * 10.0
    food_y = round(random.randrange(0, screen_height - food_radius) / 10.0) * 10.0

    snake_x_change = 0
    snake_y_change = 0

    eat_sound = generate_tone(frequency=440, duration=0.2)
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and snake_x_change == 0:
                    snake_x_change = -snake_block_size
                    snake_y_change = 0
                elif event.key == pygame.K_RIGHT and snake_x_change == 0:
                    snake_x_change = snake_block_size
                    snake_y_change = 0
                elif event.key == pygame.K_UP and snake_y_change == 0:
                    snake_y_change = -snake_block_size
                    snake_x_change = 0
                elif event.key == pygame.K_DOWN and snake_y_change == 0:
                    snake_y_change = snake_block_size
                    snake_x_change = 0

        if snake_x >= screen_width or snake_x < 0 or snake_y >= screen_height or snake_y < 0:
            running = False

        snake_x += snake_x_change
        snake_y += snake_y_change
        screen.fill((0, 0, 0))

        snake_head = [snake_x, snake_y]
        snake_list.append(snake_head)

        if len(snake_list) > snake_length:
            del snake_list[0]

        for segment in snake_list[:-1]:
            if segment == snake_head:
                running = False

        draw_snake(screen, snake_list)
        draw_food(screen, food_x, food_y)

        if abs(snake_x - food_x) < snake_block_size and abs(snake_y - food_y) < snake_block_size:
            food_x = round(random.randrange(0, screen_width - food_radius) / 10.0) * 10.0
            food_y = round(random.randrange(0, screen_height - food_radius) / 10.0) * 10.0
            snake_length += 1
            score += 10
            if audio_enabled:
                eat_sound.play()

        pygame.display.update()
        clock.tick(15)

    save_achievement(f"Scored {score} points!")
    font = pygame.font.SysFont(None, 50)
    msg = font.render("Game Over!", True, (255, 255, 255))
    screen.blit(msg, [screen_width / 6, screen_height / 3])
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()
    quit()

def main_menu():
    """Display the main menu."""
    global audio_enabled
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Arcade Menu')
    font = pygame.font.SysFont(None, 40)
    clock = pygame.time.Clock()

    while True:
        screen.fill((0, 0, 128))
        title = font.render("Arcade Main Menu", True, (255, 255, 255))
        start = font.render("1. Start Game", True, (255, 255, 255))
        settings = font.render("2. Audio Settings", True, (255, 255, 255))
        achievements = font.render("3. View Achievements", True, (255, 255, 255))
        quit_game = font.render("4. Quit", True, (255, 255, 255))

        screen.blit(title, (100, 50))
        screen.blit(start, (100, 150))
        screen.blit(settings, (100, 200))
        screen.blit(achievements, (100, 250))
        screen.blit(quit_game, (100, 300))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    main_game()
                elif event.key == pygame.K_2:
                    audio_enabled = not audio_enabled
                elif event.key == pygame.K_3:
                    view_achievements(screen, font)
                elif event.key == pygame.K_4:
                    pygame.quit()
                    quit()
        clock.tick(15)

def view_achievements(screen, font):
    """View achievements on screen."""
    achievements = load_achievements()
    screen.fill((0, 0, 0))
    title = font.render("Achievements", True, (255, 255, 255))
    screen.blit(title, (100, 50))
    y_offset = 100
    for achievement in achievements:
        line = font.render(achievement, True, (255, 255, 255))
        screen.blit(line, (50, y_offset))
        y_offset += 40
    pygame.display.update()
    pygame.time.wait(5000)

if __name__ == "__main__":
    main_menu()
