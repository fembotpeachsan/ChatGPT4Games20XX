import pygame
import sys
import random
import time
import numpy

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)

# Setup the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ATARI MAIN MENU")
clock = pygame.time.Clock()

# Generate simple sound effects
def generate_beep(frequency=440, duration_ms=100):
    sample_rate = 44100
    n_samples = int(sample_rate * (duration_ms / 1000))
    t = numpy.linspace(0, duration_ms / 1000, n_samples, False)
    tone = numpy.sin(frequency * 2 * numpy.pi * t) * 32767
    # Reshape the tone to be 2D (stereo) by duplicating the mono channel
    stereo_tone = numpy.column_stack((tone, tone)).astype(numpy.int16)
    sound = pygame.sndarray.make_sound(stereo_tone)
    return sound

# Sound effects
select_sound = generate_beep(440, 100)
confirm_sound = generate_beep(660, 200)

# Load fonts (use built-in fonts for Atari authenticity)
title_font = pygame.font.SysFont("courier", 80, bold=True)
menu_font = pygame.font.SysFont("courier", 36, bold=True)
small_font = pygame.font.SysFont("courier", 18)

# Menu options
menu_items = ["START", "OPTIONS", "HIGH SCORES", "EXIT"]
current_selection = 0

# Star field effect (for background)
stars = []
for _ in range(100):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    speed = random.uniform(0.5, 2.0)
    brightness = random.randint(100, 255)
    stars.append([x, y, speed, brightness])

# Retro Atari logo effect
def draw_retro_logo(text, y_pos):
    # Shadow effect (common in Atari games)
    shadow_text = title_font.render(text, True, BLUE)
    screen.blit(shadow_text, (WIDTH // 2 - shadow_text.get_width() // 2 + 4, y_pos + 4))
    
    # Main text
    main_text = title_font.render(text, True, ORANGE)
    screen.blit(main_text, (WIDTH // 2 - main_text.get_width() // 2, y_pos))

# Scanline effect (common in old CRT displays)
def draw_scanlines():
    for y in range(0, HEIGHT, 2):
        pygame.draw.line(screen, (0, 0, 0, 50), (0, y), (WIDTH, y), 1)

# Draw the border in Atari style
def draw_border():
    border_width = 10
    colors = [BLUE, RED, YELLOW]
    
    # Draw pulsating border
    pulse = (pygame.time.get_ticks() // 500) % 3
    pygame.draw.rect(screen, colors[pulse], (0, 0, WIDTH, border_width))
    pygame.draw.rect(screen, colors[pulse], (0, HEIGHT - border_width, WIDTH, border_width))
    pygame.draw.rect(screen, colors[pulse], (0, 0, border_width, HEIGHT))
    pygame.draw.rect(screen, colors[pulse], (WIDTH - border_width, 0, border_width, HEIGHT))

# Copyright text in Atari style
def draw_copyright():
    copyright_text = small_font.render("[C] Flames Corp 20XX [2026]", True, WHITE)
    screen.blit(copyright_text, (WIDTH // 2 - copyright_text.get_width() // 2, HEIGHT - 30))

# Update star positions for animation
def update_stars():
    for star in stars:
        star[1] += star[2]  # Move star down based on speed
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)

# Draw the star field
def draw_stars():
    for star in stars:
        color = (star[3], star[3], star[3])  # Brightness
        pygame.draw.circle(screen, color, (int(star[0]), int(star[1])), 1)

# Main menu drawing function
def draw_menu():
    screen.fill(BLACK)
    
    # Draw star field background
    draw_stars()
    
    # Draw Atari-style border
    draw_border()
    
    # Draw logo
    draw_retro_logo("PONG", 80)
    
    # Draw menu options
    for i, item in enumerate(menu_items):
        if i == current_selection:
            # Selected item: pulsating color and special indicator
            color = YELLOW if (pygame.time.get_ticks() // 200) % 2 == 0 else RED
            text = "> " + item + " <"
        else:
            color = WHITE
            text = item
        
        menu_text = menu_font.render(text, True, color)
        screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, 250 + i * 50))
    
    # Draw scanlines for CRT effect
    draw_scanlines()
    
    # Draw copyright
    draw_copyright()

# Game variables for Pong
BALL_RADIUS = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 80
PADDLE_SPEED = 5

ball = pygame.Rect(WIDTH // 2 - BALL_RADIUS, HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
paddle1 = pygame.Rect(10, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = pygame.Rect(WIDTH - 10 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
score1 = 0
score2 = 0
ball_vel_x = 4 * random.choice((1, -1))
ball_vel_y = 4 * random.choice((1, -1))

# Game states
MENU = 0
GAME = 1
OPTIONS = 2
HIGHSCORES = 3

current_state = MENU
audio_enabled = True

# Create sounds for game
paddle_hit_sound = generate_beep(440, 100)
score_sound = generate_beep(220, 250)

def reset_ball():
    global ball_vel_x, ball_vel_y
    ball.center = (WIDTH // 2, HEIGHT // 2)
    ball_vel_x = 4 * random.choice((1, -1))
    ball_vel_y = 4 * random.choice((1, -1))

def play_sound(sound):
    if audio_enabled:
        sound.play()

def draw_game():
    screen.fill(BLACK)
    
    # Draw game elements
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.rect(screen, WHITE, paddle1)
    pygame.draw.rect(screen, WHITE, paddle2)
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
    
    # Draw score
    score_text = menu_font.render(f"{score1}    {score2}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))
    
    # Draw back option
    back_text = small_font.render("ESC - BACK TO MENU", True, WHITE)
    screen.blit(back_text, (10, 10))

def draw_options():
    screen.fill(BLACK)
    
    # Draw title
    title_text = title_font.render("OPTIONS", True, YELLOW)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))
    
    # Draw audio option
    audio_text = menu_font.render(f"AUDIO: {'ON' if audio_enabled else 'OFF'}", True, 
                                 YELLOW if current_selection == 0 else WHITE)
    screen.blit(audio_text, (WIDTH // 2 - audio_text.get_width() // 2, 250))
    
    # Draw back option
    back_text = menu_font.render("BACK", True, 
                                YELLOW if current_selection == 1 else WHITE)
    screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, 300))
    
    # Draw border
    draw_border()
    
    # Draw instructions
    instructions = small_font.render("PRESS ENTER TO TOGGLE / SELECT", True, WHITE)
    screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 60))

def draw_highscores():
    screen.fill(BLACK)
    
    # Draw title
    title_text = title_font.render("HIGH SCORES", True, YELLOW)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))
    
    # Draw some sample scores
    scores = [("AAA", 999), ("BBB", 888), ("CCC", 777), ("DDD", 666), ("EEE", 555)]
    
    for i, (name, score) in enumerate(scores):
        score_text = menu_font.render(f"{i+1}. {name} - {score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 200 + i * 50))
    
    # Draw border
    draw_border()
    
    # Draw back instruction
    back_text = small_font.render("PRESS ESCAPE TO RETURN", True, RED)
    screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 60))

# Main game loop
running = True
last_key_time = 0
key_delay = 200  # milliseconds
options_items = ["AUDIO", "BACK"]
options_selection = 0

while running:
    clock.tick(FPS)
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Handle key presses with delay to prevent too fast navigation
    keys = pygame.key.get_pressed()
    
    if current_state == MENU:
        if current_time - last_key_time > key_delay:
            if keys[pygame.K_UP]:
                current_selection = (current_selection - 1) % len(menu_items)
                play_sound(select_sound)
                last_key_time = current_time
            elif keys[pygame.K_DOWN]:
                current_selection = (current_selection + 1) % len(menu_items)
                play_sound(select_sound)
                last_key_time = current_time
            elif keys[pygame.K_RETURN]:
                play_sound(confirm_sound)
                if menu_items[current_selection] == "START":
                    current_state = GAME
                    score1 = 0
                    score2 = 0
                    reset_ball()
                elif menu_items[current_selection] == "OPTIONS":
                    current_state = OPTIONS
                    options_selection = 0
                elif menu_items[current_selection] == "HIGH SCORES":
                    current_state = HIGHSCORES
                elif menu_items[current_selection] == "EXIT":
                    running = False
                last_key_time = current_time
        
        # Update star positions
        update_stars()
        
        # Draw everything
        draw_menu()
    
    elif current_state == GAME:
        # Handle paddle movement
        if keys[pygame.K_w] and paddle1.top > 0:
            paddle1.y -= PADDLE_SPEED
        if keys[pygame.K_s] and paddle1.bottom < HEIGHT:
            paddle1.y += PADDLE_SPEED
        
        # Simple AI for second paddle
        if paddle2.centery < ball.centery and paddle2.bottom < HEIGHT:
            paddle2.y += PADDLE_SPEED
        elif paddle2.centery > ball.centery and paddle2.top > 0:
            paddle2.y -= PADDLE_SPEED
        
        # Ball movement
        ball.x += ball_vel_x
        ball.y += ball_vel_y
        
        # Wall collision
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_vel_y *= -1
        
        # Paddle collision
        if ball.colliderect(paddle1) and ball_vel_x < 0:
            ball_vel_x *= -1
            play_sound(paddle_hit_sound)
        if ball.colliderect(paddle2) and ball_vel_x > 0:
            ball_vel_x *= -1
            play_sound(paddle_hit_sound)
        
        # Score
        if ball.left <= 0:
            score2 += 1
            play_sound(score_sound)
            reset_ball()
        if ball.right >= WIDTH:
            score1 += 1
            play_sound(score_sound)
            reset_ball()
        
        # Check for escape key to return to menu
        if keys[pygame.K_ESCAPE] and current_time - last_key_time > key_delay:
            current_state = MENU
            last_key_time = current_time
        
        draw_game()
    
    elif current_state == OPTIONS:
        if current_time - last_key_time > key_delay:
            if keys[pygame.K_UP]:
                options_selection = (options_selection - 1) % len(options_items)
                play_sound(select_sound)
                last_key_time = current_time
            elif keys[pygame.K_DOWN]:
                options_selection = (options_selection + 1) % len(options_items)
                play_sound(select_sound)
                last_key_time = current_time
            elif keys[pygame.K_RETURN]:
                play_sound(confirm_sound)
                if options_selection == 0:  # Toggle audio
                    audio_enabled = not audio_enabled
                elif options_selection == 1:  # Back
                    current_state = MENU
                last_key_time = current_time
            elif keys[pygame.K_ESCAPE]:
                current_state = MENU
                last_key_time = current_time
        
        draw_options()
    
    elif current_state == HIGHSCORES:
        if keys[pygame.K_ESCAPE] and current_time - last_key_time > key_delay:
            current_state = MENU
            last_key_time = current_time
        
        draw_highscores()
    
    # Display on screen
    pygame.display.flip()

# Clean up
pygame.quit()
sys.exit()
