import pygame
import sys
import random
import numpy as np

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# Constants
WIDTH = 600
HEIGHT = 400
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
BALL_SIZE = 15
PADDLE_SPEED = 5
BALL_SPEED = 7

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Fonts
title_font = pygame.font.Font(None, 74)
menu_font = pygame.font.Font(None, 36)

# Game states
MENU = 0
GAME = 1
SETTINGS = 2
CREDITS = 3

# Settings
settings = {
    'sound_enabled': True,
    'difficulty': 'Normal',
    'paddle_speed': PADDLE_SPEED
}

# Generate sound effects using numpy (no media files needed)
def generate_beep(frequency, duration):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    samples = np.sin(2 * np.pi * frequency * t)
    samples = np.int16(samples * 32767)
    stereo_samples = np.column_stack((samples, samples))  # Create 2D array for stereo
    return pygame.sndarray.make_sound(stereo_samples)

# Create sound effects
hit_sound = generate_beep(440, 0.1)  # A4 note
score_sound = generate_beep(330, 0.2)  # E4 note

# Create game objects
player = pygame.Rect(50, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
opponent = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)

# Ball direction
ball_speed_x = BALL_SPEED * random.choice((1, -1))
ball_speed_y = BALL_SPEED * random.choice((1, -1))

# Score
player_score = 0
opponent_score = 0

def draw_menu():
    screen.fill(BLACK)
    title = title_font.render("PONG", True, WHITE)
    play = menu_font.render("Press SPACE to Play", True, WHITE)
    settings_text = menu_font.render("Press S for Settings", True, WHITE)
    credits_text = menu_font.render("Press C for Credits", True, WHITE)
    
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    screen.blit(play, (WIDTH//2 - play.get_width()//2, 200))
    screen.blit(settings_text, (WIDTH//2 - settings_text.get_width()//2, 250))
    screen.blit(credits_text, (WIDTH//2 - credits_text.get_width()//2, 300))

def draw_settings():
    screen.fill(BLACK)
    title = menu_font.render("Settings", True, WHITE)
    sound = menu_font.render(f"Sound: {'ON' if settings['sound_enabled'] else 'OFF'} (Press 1)", True, WHITE)
    diff = menu_font.render(f"Difficulty: {settings['difficulty']} (Press 2)", True, WHITE)
    back = menu_font.render("Press ESC to return", True, WHITE)
    
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    screen.blit(sound, (WIDTH//2 - sound.get_width()//2, 200))
    screen.blit(diff, (WIDTH//2 - diff.get_width()//2, 250))
    screen.blit(back, (WIDTH//2 - back.get_width()//2, 350))

def draw_credits():
    screen.fill(BLACK)
    title = menu_font.render("Credits", True, WHITE)
    credit = menu_font.render("© Flams Co", True, WHITE)
    back = menu_font.render("Press ESC to return", True, WHITE)
    
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    screen.blit(credit, (WIDTH//2 - credit.get_width()//2, 200))
    screen.blit(back, (WIDTH//2 - back.get_width()//2, 350))

def move_paddle(paddle, up=True):
    if up and paddle.top > 0:
        paddle.y -= settings['paddle_speed']
    if not up and paddle.bottom < HEIGHT:
        paddle.y += settings['paddle_speed']

def reset_ball():
    ball.center = (WIDTH//2, HEIGHT//2)
    return BALL_SPEED * random.choice((1, -1)), BALL_SPEED * random.choice((1, -1))

def main():
    global ball_speed_x, ball_speed_y, player_score, opponent_score
    
    game_state = MENU
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if game_state == MENU:
                    if event.key == pygame.K_SPACE:
                        game_state = GAME
                        player_score = opponent_score = 0
                    elif event.key == pygame.K_s:
                        game_state = SETTINGS
                    elif event.key == pygame.K_c:
                        game_state = CREDITS
                
                elif game_state == SETTINGS:
                    if event.key == pygame.K_ESCAPE:
                        game_state = MENU
                    elif event.key == pygame.K_1:
                        settings['sound_enabled'] = not settings['sound_enabled']
                    elif event.key == pygame.K_2:
                        if settings['difficulty'] == 'Normal':
                            settings['difficulty'] = 'Hard'
                            settings['paddle_speed'] = PADDLE_SPEED * 1.5
                        else:
                            settings['difficulty'] = 'Normal'
                            settings['paddle_speed'] = PADDLE_SPEED
                
                elif game_state == CREDITS:
                    if event.key == pygame.K_ESCAPE:
                        game_state = MENU
                
                elif game_state == GAME:
                    if event.key == pygame.K_ESCAPE:
                        game_state = MENU

        if game_state == MENU:
            draw_menu()
        
        elif game_state == SETTINGS:
            draw_settings()
        
        elif game_state == CREDITS:
            draw_credits()
        
        elif game_state == GAME:
            # Get keyboard state
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                move_paddle(player, up=True)
            if keys[pygame.K_s]:
                move_paddle(player, up=False)
            
            # Simple AI for opponent
            if opponent.centery < ball.centery and opponent.bottom < HEIGHT:
                move_paddle(opponent, up=False)
            if opponent.centery > ball.centery and opponent.top > 0:
                move_paddle(opponent, up=True)

            # Ball movement
            ball.x += ball_speed_x
            ball.y += ball_speed_y

            # Ball collisions
            if ball.top <= 0 or ball.bottom >= HEIGHT:
                ball_speed_y *= -1
                if settings['sound_enabled']:
                    hit_sound.play()
            
            if ball.colliderect(player) or ball.colliderect(opponent):
                ball_speed_x *= -1
                if settings['sound_enabled']:
                    hit_sound.play()

            # Scoring
            if ball.left <= 0:
                opponent_score += 1
                if settings['sound_enabled']:
                    score_sound.play()
                ball_speed_x, ball_speed_y = reset_ball()
            
            if ball.right >= WIDTH:
                player_score += 1
                if settings['sound_enabled']:
                    score_sound.play()
                ball_speed_x, ball_speed_y = reset_ball()

            # Drawing
            screen.fill(BLACK)
            pygame.draw.rect(screen, WHITE, player)
            pygame.draw.rect(screen, WHITE, opponent)
            pygame.draw.ellipse(screen, WHITE, ball)
            pygame.draw.aaline(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))
            
            # Score display
            player_text = menu_font.render(str(player_score), True, WHITE)
            opponent_text = menu_font.render(str(opponent_score), True, WHITE)
            screen.blit(player_text, (WIDTH//4, 20))
            screen.blit(opponent_text, (3*WIDTH//4, 20))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
