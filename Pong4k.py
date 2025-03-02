import pygame
import sys
import random
import numpy

# Initialize Pygame
pygame.init()

# Initialize mixer for audio
pygame.mixer.init(frequency=44100, size=-16, channels=2)  # Stereo (2 channels)

# Constants
WIDTH, HEIGHT = 640, 480
BALL_RADIUS = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 80
PADDLE_SPEED = 5
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Game states
MENU = 0
GAME = 1
SETTINGS = 2
CREDITS = 3

# Generate beep sounds in code (no external files)
def generate_beep(frequency=440, duration_ms=100):
    sample_rate = 44100
    n_samples = int(sample_rate * (duration_ms / 1000))
    t = numpy.linspace(0, duration_ms / 1000, n_samples, False)
    tone = numpy.sin(frequency * 2 * numpy.pi * t) * 32767
    # Reshape the tone to be 2D (stereo) by duplicating the mono channel
    stereo_tone = numpy.column_stack((tone, tone)).astype(numpy.int16)
    sound = pygame.sndarray.make_sound(stereo_tone)
    return sound

# Pre-generate beep sounds
paddle_hit_sound = generate_beep(440, 100)
score_sound = generate_beep(220, 250)
menu_select_sound = generate_beep(660, 80)

# Setup window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game with Menu")

# Create fonts
title_font = pygame.font.SysFont("arial", 60)
menu_font = pygame.font.SysFont("arial", 36)
game_font = pygame.font.SysFont("comicsans", 30)
credits_font = pygame.font.SysFont("arial", 24)

# Game variables
ball = pygame.Rect(WIDTH // 2 - BALL_RADIUS, HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
paddle1 = pygame.Rect(10, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = pygame.Rect(WIDTH - 10 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
score1 = 0
score2 = 0
clock = pygame.time.Clock()

# Game settings
audio_enabled = True
current_state = MENU
menu_selection = 0
settings_selection = 0

# Menu options
menu_options = ["PLAY", "SETTINGS", "CREDITS", "QUIT"]
settings_options = ["AUDIO: ON", "BACK"]

def reset_ball():
    global ball_vel_x, ball_vel_y
    ball.center = (WIDTH // 2, HEIGHT // 2)
    ball_vel_x = 4 * random.choice((1, -1))
    ball_vel_y = 4 * random.choice((1, -1))

def play_sound(sound):
    if audio_enabled:
        sound.play()

def draw_menu():
    window.fill(BLACK)
    
    # Draw title
    title_text = title_font.render("PONG", True, YELLOW)
    window.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))
    
    # Draw menu options
    for i, option in enumerate(menu_options):
        if i == menu_selection:
            color = RED  # Selected option
        else:
            color = WHITE
        
        text = menu_font.render(option, True, color)
        window.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 50))
    
    # Draw Atari-style decorations
    pygame.draw.rect(window, BLUE, (0, 0, WIDTH, 10))
    pygame.draw.rect(window, BLUE, (0, HEIGHT-10, WIDTH, 10))
    pygame.draw.rect(window, BLUE, (0, 0, 10, HEIGHT))
    pygame.draw.rect(window, BLUE, (WIDTH-10, 0, 10, HEIGHT))

def draw_settings():
    window.fill(BLACK)
    
    # Draw title
    title_text = title_font.render("SETTINGS", True, YELLOW)
    window.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))
    
    # Update audio text based on current setting
    settings_options[0] = f"AUDIO: {'ON' if audio_enabled else 'OFF'}"
    
    # Draw settings options
    for i, option in enumerate(settings_options):
        if i == settings_selection:
            color = RED  # Selected option
        else:
            color = WHITE
        
        text = menu_font.render(option, True, color)
        window.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 50))
    
    # Draw Atari-style decorations
    pygame.draw.rect(window, BLUE, (0, 0, WIDTH, 10))
    pygame.draw.rect(window, BLUE, (0, HEIGHT-10, WIDTH, 10))
    pygame.draw.rect(window, BLUE, (0, 0, 10, HEIGHT))
    pygame.draw.rect(window, BLUE, (WIDTH-10, 0, 10, HEIGHT))

def draw_credits():
    window.fill(BLACK)
    
    # Draw title
    title_text = title_font.render("CREDITS", True, YELLOW)
    window.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))
    
    # Draw credits content
    copyright_text = credits_font.render("[C] Flames Corp 20XX [2026]", True, WHITE)
    window.blit(copyright_text, (WIDTH // 2 - copyright_text.get_width() // 2, HEIGHT // 2))
    
    # Draw back instruction
    back_text = menu_font.render("PRESS ESCAPE TO RETURN", True, RED)
    window.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 100))
    
    # Draw Atari-style decorations
    pygame.draw.rect(window, BLUE, (0, 0, WIDTH, 10))
    pygame.draw.rect(window, BLUE, (0, HEIGHT-10, WIDTH, 10))
    pygame.draw.rect(window, BLUE, (0, 0, 10, HEIGHT))
    pygame.draw.rect(window, BLUE, (WIDTH-10, 0, 10, HEIGHT))

def draw_game():
    window.fill(BLACK)
    
    # Draw game elements
    pygame.draw.ellipse(window, WHITE, ball)
    pygame.draw.rect(window, WHITE, paddle1)
    pygame.draw.rect(window, WHITE, paddle2)
    pygame.draw.aaline(window, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
    
    # Draw score
    score_text = game_font.render(f"{score1}    {score2}", True, WHITE)
    window.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

# Initialize ball velocity for the first game
ball_vel_x = 4 * random.choice((1, -1))
ball_vel_y = 4 * random.choice((1, -1))

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if current_state == MENU:
                if event.key == pygame.K_UP:
                    menu_selection = (menu_selection - 1) % len(menu_options)
                    play_sound(menu_select_sound)
                elif event.key == pygame.K_DOWN:
                    menu_selection = (menu_selection + 1) % len(menu_options)
                    play_sound(menu_select_sound)
                elif event.key == pygame.K_RETURN:
                    play_sound(menu_select_sound)
                    if menu_options[menu_selection] == "PLAY":
                        current_state = GAME
                        score1 = 0
                        score2 = 0
                        reset_ball()
                    elif menu_options[menu_selection] == "SETTINGS":
                        current_state = SETTINGS
                        settings_selection = 0
                    elif menu_options[menu_selection] == "CREDITS":
                        current_state = CREDITS
                    elif menu_options[menu_selection] == "QUIT":
                        running = False
            
            elif current_state == SETTINGS:
                if event.key == pygame.K_UP:
                    settings_selection = (settings_selection - 1) % len(settings_options)
                    play_sound(menu_select_sound)
                elif event.key == pygame.K_DOWN:
                    settings_selection = (settings_selection + 1) % len(settings_options)
                    play_sound(menu_select_sound)
                elif event.key == pygame.K_RETURN:
                    play_sound(menu_select_sound)
                    if settings_selection == 0:  # Toggle audio
                        audio_enabled = not audio_enabled
                    elif settings_selection == 1:  # Back
                        current_state = MENU
                elif event.key == pygame.K_ESCAPE:
                    current_state = MENU
            
            elif current_state == CREDITS:
                if event.key == pygame.K_ESCAPE:
                    current_state = MENU
            
            elif current_state == GAME:
                if event.key == pygame.K_ESCAPE:
                    current_state = MENU
    
    # Handle game logic based on current state
    if current_state == GAME:
        # Handle paddle movement
        keys = pygame.key.get_pressed()
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
    
    # Draw current screen based on state
    if current_state == MENU:
        draw_menu()
    elif current_state == SETTINGS:
        draw_settings()
    elif current_state == CREDITS:
        draw_credits()
    elif current_state == GAME:
        draw_game()
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Clean up
pygame.quit()
sys.exit()
