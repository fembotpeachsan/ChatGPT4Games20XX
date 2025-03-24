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
SKY_BLUE = (135, 206, 235)
FOREST_GREEN = (34, 139, 34)

# Game states
FILE_SELECT = 0
GAME_PLAY = 1
current_state = FILE_SELECT

# Fonts
try:
    title_font = pygame.font.SysFont('Arial', 64)
    prompt_font = pygame.font.SysFont('Arial', 32)
except:
    # Fallback fonts if Arial isn't available
    title_font = pygame.font.Font(None, 64)
    prompt_font = pygame.font.Font(None, 32)

# Player class to better organize player-related data
class Player:
    def __init__(self):
        self.x = 100
        self.y = 450
        self.width = 40
        self.height = 60
        self.speed = 5
        self.jumping = False
        self.jump_count = 10
        self.ground_level = 500 - self.height

player = Player()

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

def draw_file_select():
    """Draw the file select screen."""
    screen.fill(BLUE)
    
    # Draw title
    title_text = title_font.render("ULTRA MARIO", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3))
    screen.blit(title_text, title_rect)
    
    # Draw prompt with slight animation
    prompt_text = prompt_font.render("PRESS Z OR ENTER", True, WHITE)
    prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    screen.blit(prompt_text, prompt_rect)

def draw_game():
    """Draw the main game screen."""
    # Sky background
    screen.fill(SKY_BLUE)
    
    # Draw ground
    pygame.draw.rect(screen, FOREST_GREEN, (0, 500, SCREEN_WIDTH, 100))
    
    # Draw player
    pygame.draw.rect(screen, RED, (player.x, player.y, player.width, player.height))
    
    # Draw game info
    game_info = prompt_font.render("ULTRA MARIO - GAME LOADED", True, BLACK)
    screen.blit(game_info, (20, 20))

def handle_player_movement():
    """Handle player movement controls and jumping."""
    keys = pygame.key.get_pressed()
    
    # Horizontal movement
    if keys[pygame.K_LEFT]:
        player.x -= player.speed
    if keys[pygame.K_RIGHT]:
        player.x += player.speed
    
    # Screen boundaries
    player.x = max(0, min(player.x, SCREEN_WIDTH - player.width))
    
    # Jumping mechanics
    if not player.jumping:
        if keys[pygame.K_UP] or keys[pygame.K_SPACE] or keys[pygame.K_z]:
            player.jumping = True
    else:
        if player.jump_count >= -10:
            neg = 1 if player.jump_count >= 0 else -1
            player.y -= (player.jump_count ** 2) * 0.5 * neg
            player.jump_count -= 1
        else:
            # Reset jump
            player.jumping = False
            player.jump_count = 10
    
    # Gravity and ground collision
    if player.y < player.ground_level:
        player.y += 10  # Gravity
    if player.y > player.ground_level:
        player.y = player.ground_level

def main():
    """Main entry point for the game."""
    global current_state
    
    running = True
    while running:
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if current_state == FILE_SELECT:
                    if event.key in (pygame.K_z, pygame.K_RETURN):
                        current_state = GAME_PLAY
        
        # Update and render
        if current_state == FILE_SELECT:
            draw_file_select()
        elif current_state == GAME_PLAY:
            handle_player_movement()
            draw_game()
        
        pygame.display.update()  # More efficient than flip() for this case
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
