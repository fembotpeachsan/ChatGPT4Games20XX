import pygame

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash 2.2 Clone")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Fonts
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)

# Player properties
player_size = 40
player_x = 100
player_y = HEIGHT - player_size - 60
player_y_velocity = 0
jump_height = -15
gravity = 0.8
on_ground = True

# Ground properties
ground_height = 60

# Game variables
score = 0
level = []
scroll_speed = 5  # Speed at which the level scrolls
current_level_index = 0

# Load images (placeholder rectangles)
block_img = pygame.Surface((40, 40))
block_img.fill(WHITE)
spike_img = pygame.Surface((40, 40))
pygame.draw.polygon(spike_img, RED, [(0, 40), (20, 0), (40, 40)])

# Built-in levels (tech demos)
tech_levels = {
    "1-1": [
        {"type": "block", "x": 300, "y": 500},
        {"type": "spike", "x": 450, "y": 460},
        {"type": "block", "x": 500, "y": 500},
        {"type": "spike", "x": 550, "y": 460},
        {"type": "block", "x": 650, "y": 500},
        {"type": "block", "x": 750, "y": 500},
        {"type": "spike", "x": 800, "y": 460},
        {"type": "block", "x": 850, "y": 500},
        {"type": "block", "x": 950, "y": 500},
        {"type": "spike", "x": 1000, "y": 460},
        {"type": "block", "x": 1100, "y": 500},
        {"type": "block", "x": 1200, "y": 500},
        {"type": "spike", "x": 1250, "y": 460},
    ],
}

# Function to load level
def load_level(level_data):
    global level
    level = level_data

# Draw player function
def draw_player(x, y):
    pygame.draw.rect(screen, BLUE, (x, y, player_size, player_size))

# Draw level function
def draw_level(scroll_offset):
    for obj in level:
        if obj['type'] == 'block':
            screen.blit(block_img, (obj['x'] - scroll_offset, obj['y']))
        elif obj['type'] == 'spike':
            screen.blit(spike_img, (obj['x'] - scroll_offset, obj['y']))

# Game loop
def game_loop():
    global player_y, player_y_velocity, score, on_ground
    player_y = HEIGHT - player_size - ground_height
    player_y_velocity = 0
    score = 0
    on_ground = True
    scroll_offset = 0  # Offset for scrolling

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and on_ground:
                    player_y_velocity = jump_height
                    on_ground = False

        # Update player position
        player_y_velocity += gravity
        player_y += player_y_velocity

        # Check ground collision
        if player_y >= HEIGHT - player_size - ground_height:
            player_y = HEIGHT - player_size - ground_height
            player_y_velocity = 0
            on_ground = True

        # Collision with obstacles
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        for obj in level:
            obj_rect = pygame.Rect(obj['x'] - scroll_offset, obj['y'], 40, 40)
            if player_rect.colliderect(obj_rect):
                if obj['type'] == 'spike':
                    print(f"Game Over! Final Score: {score}")
                    return True

        # Increase score
        score += 1

        # Update scroll offset
        scroll_offset += scroll_speed

        # Clear the screen
        screen.fill(BLACK)

        # Draw level and player
        draw_level(scroll_offset)
        draw_player(player_x, player_y)

        # Display score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Check for level completion (example condition)
        if score >= 100:  # Example condition for level completion
            print(f"Level {current_level_index + 1} Complete!")
            return False

        # Update the display
        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Main menu
def main_menu():
    global current_level_index

    play_button = Button("Play Level 1-1", (WIDTH // 2 - 50, 250), font)
    edit_button = Button("Edit", (WIDTH // 2 - 50, 350), font)
    quit_button = Button("Quit", (WIDTH // 2 - 50, 450), font)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if play_button.is_clicked(event.pos):
                        current_level_index = 0  # Load level 1-1
                        load_level(tech_levels["1-1"])  # Load the first tech demo
                        if game_loop():
                            continue
                        else:
                            return False
                    elif edit_button.is_clicked(event.pos):
                        # Placeholder for editor loop
                        print("Editor loop not implemented yet.")
                        continue
                    elif quit_button.is_clicked(event.pos):
                        return False

        screen.fill(BLACK)

        title = title_font.render("Geometry Dash", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Draw buttons
        screen.blit(play_button.surface, (play_button.x, play_button.y))
        screen.blit(edit_button.surface, (edit_button.x, edit_button.y))
        screen.blit(quit_button.surface, (quit_button.x, quit_button.y))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Button class
class Button:
    def __init__(self, text, pos, font, bg=BLACK):
        self.x, self.y = pos
        self.font = font
        self.text = self.font.render(text, True, WHITE)
        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])

    def is_clicked(self, event_pos):
        return self.rect.collidepoint(event_pos)

main_menu()
pygame.quit()
