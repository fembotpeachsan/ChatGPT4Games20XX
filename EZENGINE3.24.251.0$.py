import pygame
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ULTRA MARIO")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Game states
FILE_SELECT = 0
GAME_PLAY = 1
current_state = FILE_SELECT

# Fonts
title_font = pygame.font.SysFont('Arial', 64)
prompt_font = pygame.font.SysFont('Arial', 32)

# Player attributes
player_x = 100
player_y = 450
player_width = 40
player_height = 60
player_speed = 5
player_jump = False
player_jump_count = 10
gravity = 1

# Game loop
clock = pygame.time.Clock()
running = True

def draw_file_select():
    """Draw the file select screen."""
    screen.fill(BLUE)
    
    # Draw title
    title_text = title_font.render("ULTRA MARIO", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3))
    screen.blit(title_text, title_rect)
    
    # Draw prompt
    prompt_text = prompt_font.render("PRESS Z OR ENTER", True, WHITE)
    prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    screen.blit(prompt_text, prompt_rect)

def draw_game():
    """Draw the main game screen."""
    screen.fill((135, 206, 235))  # Sky blue
    
    # Draw ground
    pygame.draw.rect(screen, (34, 139, 34), (0, 500, SCREEN_WIDTH, 100))
    
    # Draw player (simple red rectangle for now)
    pygame.draw.rect(screen, RED, (player_x, player_y, player_width, player_height))
    
    # Draw game info
    game_info = prompt_font.render("ULTRA MARIO - GAME LOADED", True, BLACK)
    screen.blit(game_info, (20, 20))

def handle_player_movement():
    """Handle player movement controls."""
    global player_x, player_y, player_jump, player_jump_count
    
    keys = pygame.key.get_pressed()
    
    # Left and right movement
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    
    # Keep player within screen bounds
    if player_x < 0:
        player_x = 0
    if player_x > SCREEN_WIDTH - player_width:
        player_x = SCREEN_WIDTH - player_width
    
    # Jumping
    if not player_jump:
        if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
            player_jump = True
    else:
        if player_jump_count >= -10:
            neg = 1
            if player_jump_count < 0:
                neg = -1
            player_y -= (player_jump_count ** 2) * 0.5 * neg
            player_jump_count -= 1
        else:
            player_jump = False
            player_jump_count = 10
    
    # Apply gravity (simple ground collision)
    if player_y > 500 - player_height:
        player_y = 500 - player_height

# Main game loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Check for key press in file select screen
        if current_state == FILE_SELECT:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z or event.key == pygame.K_RETURN:
                    current_state = GAME_PLAY
    
    # Draw appropriate screen based on current state
    if current_state == FILE_SELECT:
        draw_file_select()
    else:  # GAME_PLAY
        handle_player_movement()
        draw_game()
    
    pygame.display.flip()
    clock.tick(60)

# Quit the game
pygame.quit()
sys.exit()
