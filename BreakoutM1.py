import pygame
import sys
import numpy as np

# Initialize Pygame
pygame.init()

# Game constants
WIDTH = 800
HEIGHT = 600
BALL_RADIUS = 10
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
BRICK_ROWS = 6
BRICK_COLUMNS = 10
BRICK_WIDTH = 60
BRICK_HEIGHT = 20
BRICK_PADDING = 10
BRICK_OFFSET_TOP = 50
BRICK_OFFSET_LEFT = (WIDTH - (BRICK_COLUMNS * (BRICK_WIDTH + BRICK_PADDING))) // 2
LIVES = 3

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (200, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (160, 32, 240)
ORANGE = (255, 165, 0)

# Sound constants
SAMPLE_RATE = 44100
BIT_DEPTH = -16  # Signed 16-bit
CHANNELS = 1
BUFFER_SIZE = 1024

# Set up the main display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DeepSeek+O1 Mini Breakout v0.x")

# Initialize sound system with desired parameters
pygame.mixer.quit()  # Ensure mixer is re-initialized with correct settings
pygame.mixer.init(frequency=SAMPLE_RATE, size=BIT_DEPTH, channels=CHANNELS, buffer=BUFFER_SIZE)

def generate_square_wave(frequency=440, duration=0.1, volume=0.5):
    """Generate a square wave sound using NumPy."""
    sample_count = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, sample_count, endpoint=False)
    # Generate square wave: 1.0 for first half of the period, -1.0 for the second half
    wave = 0.5 * (1 + np.sign(np.sin(2 * np.pi * frequency * t)))
    # Scale to desired volume and 16-bit signed integers
    audio = (wave * volume * 32767).astype(np.int16)
    sound = pygame.sndarray.make_sound(audio)
    return sound

# Create game sounds
bounce_sound = generate_square_wave(
    frequency=987,  # B5 note
    duration=0.08,
    volume=0.3
)

brick_hit_sound = generate_square_wave(
    frequency=660,  # E5 note
    duration=0.05,
    volume=0.4
)

game_over_sound = generate_square_wave(
    frequency=220,  # A3 note
    duration=0.5,
    volume=0.5
)

# Initialize player paddle
player = {
    "x": WIDTH // 2 - PADDLE_WIDTH // 2,
    "y": HEIGHT - PADDLE_HEIGHT - 30,
    "width": PADDLE_WIDTH,
    "height": PADDLE_HEIGHT,
    "speed": 7
}

# Initialize ball
ball = {
    "x": WIDTH // 2,
    "y": HEIGHT // 2,
    "radius": BALL_RADIUS,
    "dx": 4,
    "dy": -4
}

# Initialize bricks
bricks = []
colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
for row in range(BRICK_ROWS):
    brick_row = []
    for col in range(BRICK_COLUMNS):
        brick_x = BRICK_OFFSET_LEFT + col * (BRICK_WIDTH + BRICK_PADDING)
        brick_y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_PADDING)
        brick = pygame.Rect(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT)
        brick_color = colors[row % len(colors)]
        brick_row.append({"rect": brick, "color": brick_color, "hit": False})
    bricks.append(brick_row)

# Game control variables
clock = pygame.time.Clock()
running = True
key_pressed = {
    'a': False,
    'd': False
}
font = pygame.font.SysFont("Arial", 24)
large_font = pygame.font.SysFont("Arial", 72)
menu_font = pygame.font.SysFont("Arial", 48)

# Score and lives
score = 0
lives_remaining = LIVES

def draw_game():
    """Render the game objects on the screen."""
    # Clear screen with black
    screen.fill(BLACK)

    # Draw player paddle in green
    pygame.draw.rect(screen, GREEN,
                     (player["x"], player["y"],
                      player["width"], player["height"]))

    # Draw ball in white
    pygame.draw.circle(screen, WHITE,
                      (int(ball["x"]), int(ball["y"])),
                      ball["radius"])

    # Draw bricks
    for row in bricks:
        for brick in row:
            if not brick["hit"]:
                pygame.draw.rect(screen, brick["color"], brick["rect"])

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (5, 5))

    # Draw lives
    lives_text = font.render(f"Lives: {lives_remaining}", True, WHITE)
    screen.blit(lives_text, (WIDTH - 100, 5))

def update_game():
    """Update the game state, including player and ball positions."""
    global running, score, lives_remaining, bricks, ball

    # Update player position based on key presses
    if key_pressed['a'] and player["x"] > 0:
        player["x"] -= player["speed"]
    if key_pressed['d'] and player["x"] < WIDTH - player["width"]:
        player["x"] += player["speed"]

    # Update ball position
    ball["x"] += ball["dx"]
    ball["y"] += ball["dy"]

    # Ball collision with left and right walls
    if ball["x"] <= ball["radius"]:
        ball["x"] = ball["radius"]
        ball["dx"] *= -1
        bounce_sound.play()
    elif ball["x"] >= WIDTH - ball["radius"]:
        ball["x"] = WIDTH - ball["radius"]
        ball["dx"] *= -1
        bounce_sound.play()

    # Ball collision with top wall
    if ball["y"] <= ball["radius"]:
        ball["y"] = ball["radius"]
        ball["dy"] *= -1
        bounce_sound.play()

    # Ball collision with paddle
    paddle_rect = pygame.Rect(player["x"], player["y"], player["width"], player["height"])
    ball_rect = pygame.Rect(ball["x"] - ball["radius"], ball["y"] - ball["radius"],
                            ball["radius"]*2, ball["radius"]*2)
    if paddle_rect.colliderect(ball_rect):
        # Reflect the ball
        ball["dy"] *= -1
        ball["y"] = player["y"] - ball["radius"]
        bounce_sound.play()
        # Add ball speed variation based on where it hits the paddle
        hit_pos = (ball["x"] - (player["x"] + player["width"]/2)) / (player["width"]/2)
        ball["dx"] += 0.5 * hit_pos
        # Limit the maximum dx to prevent excessive speed
        max_speed = 10
        ball["dx"] = max(-max_speed, min(ball["dx"], max_speed))

    # Ball collision with bricks
    for row in bricks:
        for brick in row:
            if not brick["hit"] and brick["rect"].colliderect(ball_rect):
                brick["hit"] = True
                score += 10
                brick_hit_sound.play()
                # Determine collision side
                if abs(ball["x"] - brick["rect"].left) < ball["radius"] and ball["dx"] > 0:
                    ball["dx"] *= -1
                elif abs(ball["x"] - brick["rect"].right) < ball["radius"] and ball["dx"] < 0:
                    ball["dx"] *= -1
                else:
                    ball["dy"] *= -1
                return  # Only handle one brick collision per frame

    # Check if all bricks are destroyed
    if all(brick["hit"] for row in bricks for brick in row):
        # Reset bricks
        for row in bricks:
            for brick in row:
                brick["hit"] = False
        # Reset ball position and speed
        ball["x"] = WIDTH // 2
        ball["y"] = HEIGHT // 2
        ball["dx"] = 4 * (1 if np.random.rand() > 0.5 else -1)
        ball["dy"] = -4
        # Optional: Increase ball speed or add more bricks for higher levels

    # Game over condition: ball falls below the paddle
    if ball["y"] - ball["radius"] > HEIGHT:
        lives_remaining -= 1
        if lives_remaining <= 0:
            game_over_sound.play()
            pygame.time.wait(500)  # Let the sound play before exiting
            running = False
        else:
            # Reset ball and paddle positions
            ball["x"] = WIDTH // 2
            ball["y"] = HEIGHT // 2
            ball["dx"] = 4 * (1 if np.random.rand() > 0.5 else -1)
            ball["dy"] = -4
            player["x"] = WIDTH // 2 - PADDLE_WIDTH // 2
            pygame.time.wait(1000)  # Brief pause before continuing

def countdown():
    """Display a 3-2-1 countdown before the game starts."""
    for count in range(3, 0, -1):
        screen.fill(BLACK)
        count_text = large_font.render(str(count), True, WHITE)
        text_rect = count_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(count_text, text_rect)
        pygame.display.flip()
        pygame.time.wait(1000)  # Wait for 1 second

    # Display "Start!" briefly
    screen.fill(BLACK)
    start_text = large_font.render("Start!", True, WHITE)
    text_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(start_text, text_rect)
    pygame.display.flip()
    pygame.time.wait(500)  # Wait for half a second

def game_over_screen():
    """Display the game over screen."""
    screen.fill(BLACK)
    over_text = large_font.render("Game Over", True, RED)
    text_rect = over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(over_text, text_rect)

    score_text = font.render(f"Final Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    screen.blit(score_text, score_rect)

    prompt_text = font.render("Press any key to return to Main Menu", True, WHITE)
    prompt_rect = prompt_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
    screen.blit(prompt_text, prompt_rect)

    pygame.display.flip()

    # Wait for user to press a key
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
    main_menu()

def main_menu():
    """Display the main menu with options to start or quit."""
    menu = True
    selected = "start"

    while menu:
        screen.fill(BLACK)

        # Title
        title_text = large_font.render("DeepSeek+O1 Mini Breakout v0.x", True, PURPLE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_text, title_rect)

        # Start option
        if selected == "start":
            start_text = menu_font.render("Start Game", True, YELLOW)
        else:
            start_text = menu_font.render("Start Game", True, WHITE)
        start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(start_text, start_rect)

        # Quit option
        if selected == "quit":
            quit_text = menu_font.render("Quit", True, YELLOW)
        else:
            quit_text = menu_font.render("Quit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(quit_text, quit_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected = "start"
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected = "quit"
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if selected == "start":
                        menu = False
                        start_game()
                    elif selected == "quit":
                        menu = False
                        pygame.quit()
                        sys.exit()

def start_game():
    """Start the game with countdown."""
    global running, score, lives_remaining, bricks, ball, player

    # Reset score and lives
    score = 0
    lives_remaining = LIVES

    # Reset bricks
    for row in bricks:
        for brick in row:
            brick["hit"] = False

    # Reset ball position and speed
    ball["x"] = WIDTH // 2
    ball["y"] = HEIGHT // 2
    ball["dx"] = 4 * (1 if np.random.rand() > 0.5 else -1)
    ball["dy"] = -4

    # Reset paddle position
    player["x"] = WIDTH // 2 - PADDLE_WIDTH // 2

    # Display countdown
    countdown()

    # Start main game loop
    game_loop()

def game_loop():
    """Main game loop."""
    global running
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    key_pressed['a'] = True
                elif event.key == pygame.K_d:
                    key_pressed['d'] = True
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    key_pressed['a'] = False
                elif event.key == pygame.K_d:
                    key_pressed['d'] = False

        update_game()
        draw_game()
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 frames per second

        # Check for game over
        if lives_remaining <= 0:
            running = False

    # Show game over screen
    game_over_screen()

def main():
    """Main function to run the game."""
    main_menu()

# Run the game
if __name__ == "__main__":
    main()
