import pygame
import sys
import random
import numpy as np
import sounddevice as sd
import threading

# Initialize pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Space Invaders")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Set up font for score
font = pygame.font.Font(None, 36)

# Player settings
player_x = 300
player_y = 350
player_x_change = 0
player_width = 50
player_height = 30
player_lives = 3
player_speed = 5

# Enemy settings
enemy_width = 50
enemy_height = 30
enemy_speed = 2
enemy_move_down = 40
num_enemies_x = 6
num_enemies_y = 3
enemies = []
for i in range(num_enemies_x):
    for j in range(num_enemies_y):
        x = 50 + i * (enemy_width + 10)
        y = 50 + j * (enemy_height + 10)
        enemies.append({'x': x, 'y': y, 'x_change': enemy_speed})

# Bullet settings
bullet_width = 5
bullet_height = 10
bullet_color = WHITE
bullet_speed = 7
bullets = []

# Score
score = 0

# Set up the clock for 60 FPS
clock = pygame.time.Clock()

# Sound settings
sample_rate = 44100

def play_sound(frequency, duration=0.2, volume=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Generate a sine wave
    wave = np.sin(2 * np.pi * frequency * t)
    # Apply an exponential decay to create a synthwave effect
    envelope = np.exp(-5 * t)
    sound = volume * wave * envelope
    sd.play(sound, sample_rate)
    sd.wait()

def play_sound_async(frequency, duration=0.2, volume=0.5):
    threading.Thread(target=play_sound, args=(frequency, duration, volume)).start()

# Game loop
running = True
while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        
        # Check for keystroke events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_x_change = -player_speed
            if event.key == pygame.K_RIGHT:
                player_x_change = player_speed
            if event.key == pygame.K_SPACE:
                # Create a new bullet
                bullet_x = player_x + player_width // 2 - bullet_width // 2
                bullet_y = player_y
                bullets.append({'x': bullet_x, 'y': bullet_y})
                # Play shooting sound
                play_sound_async(frequency=800, duration=0.1, volume=0.3)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player_x_change = 0
    
    # Update player position
    player_x += player_x_change
    if player_x <= 0:
        player_x = 0
    elif player_x >= 600 - player_width:
        player_x = 600 - player_width
    
    # Update enemy positions
    move_down = False
    for enemy in enemies:
        enemy['x'] += enemy['x_change']
        if enemy['x'] <= 0 or enemy['x'] >= 600 - enemy_width:
            move_down = True
            break
    
    if move_down:
        for enemy in enemies:
            enemy['x_change'] = -enemy['x_change']
            enemy['y'] += enemy_move_down
            if enemy['y'] >= player_y:
                player_lives -= 1
                if player_lives == 0:
                    running = False
    
    # Update bullet positions
    for bullet in bullets[:]:
        bullet['y'] -= bullet_speed
        if bullet['y'] < 0:
            bullets.remove(bullet)
    
    # Check for collisions
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if (enemy['x'] < bullet['x'] < enemy['x'] + enemy_width) and \
               (enemy['y'] < bullet['y'] < enemy['y'] + enemy_height):
                enemies.remove(enemy)
                bullets.remove(bullet)
                score += 1
                # Play explosion sound
                play_sound_async(frequency=200, duration=0.3, volume=0.5)
                break
    
    # Draw player
    pygame.draw.rect(screen, GREEN, (player_x, player_y, player_width, player_height))
    
    # Draw enemies
    for enemy in enemies:
        pygame.draw.rect(screen, RED, (enemy['x'], enemy['y'], enemy_width, enemy_height))
    
    # Draw bullets
    for bullet in bullets:
        pygame.draw.rect(screen, bullet_color, (bullet['x'], bullet['y'], bullet_width, bullet_height))
    
    # Render score and lives
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {player_lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (500, 10))
    
    # Update the display
    pygame.display.update()
    
    # Maintain 60 FPS
    clock.tick(60)
