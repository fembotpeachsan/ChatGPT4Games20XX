import pygame
import sys
import random
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Pong')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 50, 160)
PINK = (200, 0, 100)
YELLOW = (255, 255, 0)

# Game settings
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
BALL_SIZE = 15
PADDLE_SPEED = 7
BALL_SPEED = 5    
AI_SPEED = 4      
WINNING_SCORE = 5

# Generate synthesized sounds
def create_synth_sound(frequency, duration, volume=0.5, fade=True):
    sample_rate = 44100
    n_samples = int(duration * sample_rate)
    
    # Create a sine wave with the given frequency
    buf = np.sin(2 * np.pi * np.arange(n_samples) * frequency / sample_rate)
    
    # Apply fade in/out if requested
    if fade:
        fade_len = int(n_samples * 0.1)  # 10% fade in/out
        fade_in = np.linspace(0, 1, fade_len)
        fade_out = np.linspace(1, 0, fade_len)
        buf[:fade_len] *= fade_in
        buf[-fade_len:] *= fade_out
    
    # Apply volume
    buf = (buf * volume * 32767).astype(np.int16)
    
    # Convert to stereo by duplicating the mono channel
    stereo_buf = np.column_stack((buf, buf))
    
    # Create a pygame Sound object
    sound = pygame.mixer.Sound(stereo_buf)
    return sound

# Create game sounds with synthwave style
paddle_hit_sound = create_synth_sound(880, 0.08)  # Higher pitched hit
wall_hit_sound = create_synth_sound(440, 0.05)    # Lower pitched hit
score_sound = create_synth_sound(220, 0.4)        # Low note for scoring
startup_sound = create_synth_sound(440, 0.6, volume=0.3)
game_over_sound = create_synth_sound(220, 1.0, volume=0.6)  # Game over sound

# Arpeggiated startup chord
def play_startup_arpeggio():
    # Synthwave style chord arpeggio
    notes = [440, 554, 659, 880, 1108]  # A, C#, E, A, C# (A major chord)
    for note in notes:
        sound = create_synth_sound(note, 0.1, volume=0.2)
        sound.play()
        pygame.time.wait(100)

def reset_ball():
    return (
        SCREEN_WIDTH//2 - BALL_SIZE//2,
        SCREEN_HEIGHT//2 - BALL_SIZE//2,
        BALL_SPEED * random.choice((1, -1)),
        BALL_SPEED * random.choice((1, -1))
    )

def game_over_screen(winner):
    game_over_sound.play()
    
    # Set up fonts
    title_font = pygame.font.Font(None, 74)
    msg_font = pygame.font.Font(None, 36)
    
    # Create game over messages
    if winner == "player":
        title_text = title_font.render('YOU WIN!', True, PINK)
    else:
        title_text = title_font.render('GAME OVER', True, BLUE)
    
    restart_text = msg_font.render('Press Y to Restart', True, WHITE)
    exit_text = msg_font.render('Press N to Exit', True, WHITE)
    
    # Game over loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True  # Restart game
                if event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                    return False  # Exit to main menu
        
        # Draw game over screen
        screen.fill(BLACK)
        
        # Draw synthwave-style grid
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(screen, BLUE, (0, y), (SCREEN_WIDTH, y), 1)
        
        # Draw game over text
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3)))
        screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        screen.blit(exit_text, exit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)))
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)

def run_game():
    # Create game objects
    player = pygame.Rect(50, SCREEN_HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    opponent = pygame.Rect(SCREEN_WIDTH - 50 - PADDLE_WIDTH, SCREEN_HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(SCREEN_WIDTH//2 - BALL_SIZE//2, SCREEN_HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
    
    # Initialize scores
    player_score = 0
    opponent_score = 0
    font = pygame.font.Font(None, 74)
    
    # Ball speed
    ball.x, ball.y, ball_speed_x, ball_speed_y = reset_ball()
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and player.top > 0:
            player.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and player.bottom < SCREEN_HEIGHT:
            player.y += PADDLE_SPEED
        
        # AI opponent movement with delayed reaction and prediction
        prediction_error = random.randint(-30, 30)
        target_y = ball.centery + prediction_error
        
        if opponent.centery < target_y and opponent.bottom < SCREEN_HEIGHT:
            opponent.y += AI_SPEED
        if opponent.centery > target_y and opponent.top > 0:
            opponent.y -= AI_SPEED
        
        # Ball movement
        ball.x += ball_speed_x
        ball.y += ball_speed_y
        
        # Ball collisions with walls
        if ball.top <= 0:
            ball.top = 0
            ball_speed_y *= -1
            wall_hit_sound.play()
        if ball.bottom >= SCREEN_HEIGHT:
            ball.bottom = SCREEN_HEIGHT
            ball_speed_y *= -1
            wall_hit_sound.play()
        
        # Paddle collisions with improved physics
        if ball.colliderect(player):
            if abs(ball.left - player.right) < 10:
                ball.left = player.right
                ball_speed_x = abs(ball_speed_x)  # Ensure ball moves right
                # Add slight randomization to make gameplay more interesting
                relative_intersect_y = (player.centery - ball.centery) / (PADDLE_HEIGHT/2)
                ball_speed_y = -relative_intersect_y * BALL_SPEED
                
                # Play synthesized hit sound with pitch based on hit position
                pitch_factor = 1.0 + abs(relative_intersect_y) * 0.5
                hit_sound = create_synth_sound(880 * pitch_factor, 0.05)
                hit_sound.play()
        
        if ball.colliderect(opponent):
            if abs(ball.right - opponent.left) < 10:
                ball.right = opponent.left
                ball_speed_x = -abs(ball_speed_x)  # Ensure ball moves left
                relative_intersect_y = (opponent.centery - ball.centery) / (PADDLE_HEIGHT/2)
                ball_speed_y = -relative_intersect_y * BALL_SPEED
                
                # Play synthesized hit sound with pitch based on hit position
                pitch_factor = 1.0 + abs(relative_intersect_y) * 0.5
                hit_sound = create_synth_sound(660 * pitch_factor, 0.05)
                hit_sound.play()
        
        # Scoring with pause
        if ball.left <= 0:
            opponent_score += 1
            score_sound.play()
            pygame.time.wait(500)  # Add small pause after scoring
            
            # Check for game over
            if opponent_score >= WINNING_SCORE:
                if game_over_screen("opponent"):
                    return True  # Restart the game
                else:
                    return False  # Exit to main menu
            
            ball.x, ball.y, ball_speed_x, ball_speed_y = reset_ball()
            
        if ball.right >= SCREEN_WIDTH:
            player_score += 1
            score_sound.play()
            pygame.time.wait(500)  # Add small pause after scoring
            
            # Check for game over
            if player_score >= WINNING_SCORE:
                if game_over_screen("player"):
                    return True  # Restart the game
                else:
                    return False  # Exit to main menu
            
            ball.x, ball.y, ball_speed_x, ball_speed_y = reset_ball()
        
        # Drawing
        screen.fill(BLACK)
        
        # Draw synthwave-style grid (optional background)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(screen, BLUE, (0, y), (SCREEN_WIDTH, y), 1)
        
        # Draw paddles and ball with synthwave colors
        pygame.draw.rect(screen, PINK, player)
        pygame.draw.rect(screen, BLUE, opponent)
        pygame.draw.ellipse(screen, WHITE, ball)
        pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH//2, 0), (SCREEN_WIDTH//2, SCREEN_HEIGHT))
        
        # Score display
        player_text = font.render(str(player_score), True, PINK)
        opponent_text = font.render(str(opponent_score), True, BLUE)
        screen.blit(player_text, (SCREEN_WIDTH//4, 20))
        screen.blit(opponent_text, (3*SCREEN_WIDTH//4, 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    return False

def main():
    # Main menu loop
    menu_title_font = pygame.font.Font(None, 74)
    menu_font = pygame.font.Font(None, 36)
    credits_font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()
    
    # Play startup sound
    play_startup_arpeggio()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    startup_sound.play()
                    # Run game and check if player wants to restart
                    while run_game():
                        pass  # Continue restarting until False is returned
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        screen.fill(BLACK)
        
        # Draw synthwave-style grid (optional background)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(screen, BLUE, (0, y), (SCREEN_WIDTH, y), 1)
        
        # Draw title with synthwave style
        title_text = menu_title_font.render('PONG', True, PINK)
        title_shadow = menu_title_font.render('PONG', True, BLUE)
        screen.blit(title_shadow, title_shadow.get_rect(center=(SCREEN_WIDTH//2 + 4, SCREEN_HEIGHT//4 + 4)))
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4)))
        
        # Draw start instruction
        start_text = menu_font.render('Press SPACE to Play', True, WHITE)
        screen.blit(start_text, start_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        
        # Game info
        info_text = menu_font.render(f'First to {WINNING_SCORE} points wins!', True, YELLOW)
        screen.blit(info_text, info_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)))
        
        # Draw Team Flames credits
        credits_text1 = credits_font.render('Team Flames [C] 20XX', True, GRAY)
        credits_text2 = credits_font.render('1999-20XX', True, GRAY)
        
        screen.blit(credits_text1, credits_text1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 60)))
        screen.blit(credits_text2, credits_text2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 35)))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
