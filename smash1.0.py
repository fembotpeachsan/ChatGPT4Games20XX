import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Smash Flash-ish (No PNG Version)")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Define fonts
FONT = pygame.font.SysFont("Arial", 24, bold=True)

# Game states
STATE_MENU = 0
STATE_GAME = 1

# Character definitions (Name, Color)
CHARACTERS = [
    {"name": "Block Dude",     "color": (255, 0, 0)},
    {"name": "Circle Guy",     "color": (0, 255, 0)},
    {"name": "Triangle Gal",   "color": (0, 0, 255)},
    {"name": "Star Freak",     "color": (255, 255, 0)},
    {"name": "Generic Hero",   "color": (255, 128, 0)},
    {"name": "Villain Blob",   "color": (128, 0, 128)},
]

# For storing selected characters
player1_char = None
player2_char = None

# Spacing for the menu
CHAR_COLS = 3  # Number of columns in the character selection menu
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 60
BUTTON_MARGIN = 10

# Current game state
game_state = STATE_MENU

# Simple physics and position for the in-game characters
class Fighter:
    def __init__(self, x, y, width, height, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.on_ground = False

    def update(self):
        # Gravity
        self.vel_y += 0.5

        # Limit falling speed
        if self.vel_y > 10:
            self.vel_y = 10

        # Update positions
        self.x += self.vel_x
        self.y += self.vel_y

        # Collision with the floor (simple rectangle floor)
        floor_y = 500
        if self.y + self.height >= floor_y:
            self.y = floor_y - self.height
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

def render_character_menu(surface, characters, start_x, start_y, cols):
    """
    Renders character selection buttons in a grid layout.
    Returns a list of (button_rect, character_index) for click detection.
    """
    button_info_list = []
    row = 0
    col = 0

    for i, char in enumerate(characters):
        # Calculate position for the button
        x = start_x + col * (BUTTON_WIDTH + BUTTON_MARGIN)
        y = start_y + row * (BUTTON_HEIGHT + BUTTON_MARGIN)

        button_rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)

        # Draw the rectangle
        pygame.draw.rect(surface, (50, 50, 50), button_rect)
        # Draw the character color as a mini bar or something on the left
        color_bar_rect = pygame.Rect(x, y, 40, BUTTON_HEIGHT)
        pygame.draw.rect(surface, char["color"], color_bar_rect)

        # Render the text
        text_surface = FONT.render(char["name"], True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)

        button_info_list.append((button_rect, i))

        col += 1
        if col == cols:
            col = 0
            row += 1

    return button_info_list

def handle_menu_events(events, button_list):
    """
    Checks for mouse clicks on the character buttons.
    Returns the index of the clicked character if any, otherwise None.
    """
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for button_rect, char_idx in button_list:
                if button_rect.collidepoint(mouse_pos):
                    return char_idx
    return None

def main():
    global game_state, player1_char, player2_char

    # Create two fighters
    # (For the sake of demonstration, they will be created after selection.)
    fighter1 = None
    fighter2 = None

    # Track which player is choosing a character (start with Player 1)
    current_player_select = 1

    running = True
    while running:
        clock.tick(60)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))  # Clear screen

        if game_state == STATE_MENU:
            # Display instructions
            title_text = FONT.render(
                f"Select Character for Player {current_player_select}",
                True, (255, 255, 255)
            )
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

            # Render character menu
            button_list = render_character_menu(
                screen,
                CHARACTERS,
                start_x=SCREEN_WIDTH // 2 - (CHAR_COLS * (BUTTON_WIDTH + BUTTON_MARGIN)) // 2,
                start_y=120,
                cols=CHAR_COLS
            )

            # Check if a character was clicked
            selected_idx = handle_menu_events(events, button_list)
            if selected_idx is not None:
                if current_player_select == 1:
                    player1_char = CHARACTERS[selected_idx]
                    current_player_select = 2
                elif current_player_select == 2:
                    player2_char = CHARACTERS[selected_idx]
                    # Both players have selected; enter game state
                    # Create the actual fighters
                    fighter1 = Fighter(200, 100, 40, 60, player1_char["color"])
                    fighter2 = Fighter(550, 100, 40, 60, player2_char["color"])
                    game_state = STATE_GAME

        elif game_state == STATE_GAME:
            # Basic controls
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                fighter1.vel_x = -fighter1.speed
            elif keys[pygame.K_d]:
                fighter1.vel_x = fighter1.speed
            else:
                fighter1.vel_x = 0

            if keys[pygame.K_w] and fighter1.on_ground:
                fighter1.vel_y = -10

            # Let's give player 2 some controls (arrow keys)
            if keys[pygame.K_LEFT]:
                fighter2.vel_x = -fighter2.speed
            elif keys[pygame.K_RIGHT]:
                fighter2.vel_x = fighter2.speed
            else:
                fighter2.vel_x = 0

            if keys[pygame.K_UP] and fighter2.on_ground:
                fighter2.vel_y = -10

            # Update fighters
            fighter1.update()
            fighter2.update()

            # Draw fighters
            fighter1.draw(screen)
            fighter2.draw(screen)

            # Draw a simple floor
            pygame.draw.rect(screen, (100, 100, 100), (0, 500, SCREEN_WIDTH, 100))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
    import pygame
    import sys

    # Initialize Pygame
    pygame.init()

    # Screen dimensions
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Smash Flash-ish (No PNG Version)")

    # Clock for controlling frame rate
    clock = pygame.time.Clock()

    # Define fonts
    FONT = pygame.font.SysFont("Arial", 24, bold=True)

    # Game states
    STATE_MENU = 0
    STATE_GAME = 1

    # Character definitions (Name, Color)
    CHARACTERS = [
        {"name": "Block Dude",     "color": (255, 0, 0)},
        {"name": "Circle Guy",     "color": (0, 255, 0)},
        {"name": "Triangle Gal",   "color": (0, 0, 255)},
        {"name": "Star Freak",     "color": (255, 255, 0)},
        {"name": "Generic Hero",   "color": (255, 128, 0)},
        {"name": "Villain Blob",   "color": (128, 0, 128)},
    ]

    # For storing selected characters
    player1_char = None
    player2_char = None

    # Spacing for the menu
    CHAR_COLS = 3  # Number of columns in the character selection menu
    BUTTON_WIDTH, BUTTON_HEIGHT = 200, 60
    BUTTON_MARGIN = 10

    # Current game state
    game_state = STATE_MENU

    # Simple physics and position for the in-game characters
    class Fighter:
        def __init__(self, x, y, width, height, color=(255, 0, 0)):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.color = color
            self.vel_x = 0
            self.vel_y = 0
            self.speed = 5
            self.on_ground = False

        def update(self):
            # Gravity
            self.vel_y += 0.5

            # Limit falling speed
            if self.vel_y > 10:
                self.vel_y = 10

            # Update positions
            self.x += self.vel_x
            self.y += self.vel_y

            # Collision with the floor (simple rectangle floor)
            floor_y = 500
            if self.y + self.height >= floor_y:
                self.y = floor_y - self.height
                self.vel_y = 0
                self.on_ground = True
            else:
                self.on_ground = False

        def draw(self, surface):
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

    def render_character_menu(surface, characters, start_x, start_y, cols):
        """
        Renders character selection buttons in a grid layout.
        Returns a list of (button_rect, character_index) for click detection.
        """
        button_info_list = []
        row = 0
        col = 0

        for i, char in enumerate(characters):
            # Calculate position for the button
            x = start_x + col * (BUTTON_WIDTH + BUTTON_MARGIN)
            y = start_y + row * (BUTTON_HEIGHT + BUTTON_MARGIN)

            button_rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)

            # Draw the rectangle
            pygame.draw.rect(surface, (50, 50, 50), button_rect)
            # Draw the character color as a mini bar or something on the left
            color_bar_rect = pygame.Rect(x, y, 40, BUTTON_HEIGHT)
            pygame.draw.rect(surface, char["color"], color_bar_rect)

            # Render the text
            text_surface = FONT.render(char["name"], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            surface.blit(text_surface, text_rect)

            button_info_list.append((button_rect, i))

            col += 1
            if col == cols:
                col = 0
                row += 1

        return button_info_list

    def handle_menu_events(events, button_list):
        """
        Checks for mouse clicks on the character buttons.
        Returns the index of the clicked character if any, otherwise None.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for button_rect, char_idx in button_list:
                    if button_rect.collidepoint(mouse_pos):
                        return char_idx
        return None

    def main():
        global game_state, player1_char, player2_char

        # Create two fighters
        # (For the sake of demonstration, they will be created after selection.)
        fighter1 = None
        fighter2 = None

        # Track which player is choosing a character (start with Player 1)
        current_player_select = 1

        running = True
        while running:
            clock.tick(60)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((0, 0, 0))  # Clear screen

            if game_state == STATE_MENU:
                # Display instructions
                title_text = FONT.render(
                    f"Select Character for Player {current_player_select}",
                    True, (255, 255, 255)
                )
                screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

                # Render character menu
                button_list = render_character_menu(
                    screen,
                    CHARACTERS,
                    start_x=SCREEN_WIDTH // 2 - (CHAR_COLS * (BUTTON_WIDTH + BUTTON_MARGIN)) // 2,
                    start_y=120,
                    cols=CHAR_COLS
                )

                # Check if a character was clicked
                selected_idx = handle_menu_events(events, button_list)
                if selected_idx is not None:
                    if current_player_select == 1:
                        player1_char = CHARACTERS[selected_idx]
                        current_player_select = 2
                    elif current_player_select == 2:
                        player2_char = CHARACTERS[selected_idx]
                        # Both players have selected; enter game state
                        # Create the actual fighters
                        fighter1 = Fighter(200, 100, 40, 60, player1_char["color"])
                        fighter2 = Fighter(550, 100, 40, 60, player2_char["color"])
                        game_state = STATE_GAME

            elif game_state == STATE_GAME:
                # Basic controls
                keys = pygame.key.get_pressed()
                if keys[pygame.K_a]:
                    fighter1.vel_x = -fighter1.speed
                elif keys[pygame.K_d]:
                    fighter1.vel_x = fighter1.speed
                else:
                    fighter1.vel_x = 0

                if keys[pygame.K_w] and fighter1.on_ground:
                    fighter1.vel_y = -10

                # Let's give player 2 some controls (arrow keys)
                if keys[pygame.K_LEFT]:
                    fighter2.vel_x = -fighter2.speed
                elif keys[pygame.K_RIGHT]:
                    fighter2.vel_x = fighter2.speed
                else:
                    fighter2.vel_x = 0

                if keys[pygame.K_UP] and fighter2.on_ground:
                    fighter2.vel_y = -10

                # Update fighters
                fighter1.update()
                fighter2.update()

                # Draw fighters
                fighter1.draw(screen)
                fighter2.draw(screen)

                # Draw a simple floor
                pygame.draw.rect(screen, (100, 100, 100), (0, 500, SCREEN_WIDTH, 100))

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    if __name__ == "__main__":
        main()
