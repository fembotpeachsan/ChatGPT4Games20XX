import pygame
import sys
import numpy as np

# Initialize Pygame mixer with NumPy support
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 20
PADDLE_SPEED = 5
BALL_SPEED_X, BALL_SPEED_Y = 5, 5

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NumPy Pong with SFX")

# Fonts
font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 50)
font_small = pygame.font.Font(None, 36)

# Sound generation
def generate_sound(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    return np.int16(wave * 32767)

def play_sound(frequency, duration):
    sound_array = generate_sound(frequency, duration)
    sound = pygame.sndarray.make_sound(sound_array)
    sound.play()

# Game Objects
def reset_ball():
    ball.center = (WIDTH // 2, HEIGHT // 2)
    global BALL_SPEED_X, BALL_SPEED_Y, left_score, right_score, current_state
    BALL_SPEED_X *= -1
    BALL_SPEED_Y = np.random.choice([-5, 5])
    
    if left_score >= 5 or right_score >= 5:
        current_state = 'restart'

# Game Initialization
left_paddle = pygame.Rect(10, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WIDTH - 20, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

left_score = 0
right_score = 0

# Game States
MENU = 'menu'
GAME = 'game'
CREDITS = 'credits'
QUIT_GAME = 'quit'
RESTART = 'restart'

current_state = MENU

# Button Class
class Button:
    def __init__(self, text, pos, font, base_color, hover_color):
        self.text = text
        self.pos = pos
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.rendered_text = self.font.render(self.text, True, self.base_color)
        self.rect = self.rendered_text.get_rect(center=self.pos)

    def draw(self, surface, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            color = self.hover_color
        else:
            color = self.base_color
        self.rendered_text = self.font.render(self.text, True, color)
        surface.blit(self.rendered_text, self.rect)

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]

# Create Buttons
start_button = Button("Start Game", (WIDTH // 2, HEIGHT // 2 - 50), font_medium, WHITE, GRAY)
credits_button = Button("Credits", (WIDTH // 2, HEIGHT // 2 + 20), font_medium, WHITE, GRAY)
quit_button = Button("Quit", (WIDTH // 2, HEIGHT // 2 + 90), font_medium, WHITE, GRAY)
back_button = Button("Back to Menu", (WIDTH // 2, HEIGHT - 100), font_medium, WHITE, GRAY)

# Credits Content
credits_lines = [
    "Pong Game",
    "",
    "Developed by:",
    "Cat-San" "[C] 20XX-25",
    "",
    "Thanks for playing!"
]

# Main Menu Function
def main_menu():
    global current_state
    while current_state == MENU:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BLACK)

        # Draw Title
        title_text = font_large.render("PONG", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_text, title_rect)

        # Draw Buttons
        start_button.draw(screen, mouse_pos)
        credits_button.draw(screen, mouse_pos)
        quit_button.draw(screen, mouse_pos)

        # Handle Button Clicks
        if start_button.is_clicked(mouse_pos, mouse_pressed):
            current_state = GAME
        if credits_button.is_clicked(mouse_pos, mouse_pressed):
            current_state = CREDITS
        if quit_button.is_clicked(mouse_pos, mouse_pressed):
            current_state = QUIT_GAME

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Credits Screen Function
def credits_screen():
    global current_state
    while current_state == CREDITS:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BLACK)

        # Draw Credits Text
        for idx, line in enumerate(credits_lines):
            credit_text = font_small.render(line, True, WHITE)
            credit_rect = credit_text.get_rect(center=(WIDTH // 2, HEIGHT // 4 + idx * 40))
            screen.blit(credit_text, credit_rect)

        # Draw Back Button
        back_button.draw(screen, mouse_pos)

        # Handle Back Button Click
        if back_button.is_clicked(mouse_pos, mouse_pressed):
            current_state = MENU

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Game Loop Function
def game_loop():
    global current_state, BALL_SPEED_X, BALL_SPEED_Y, left_score, right_score

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and left_paddle.top > 0:
            left_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
            left_paddle.y += PADDLE_SPEED
        if keys[pygame.K_ESCAPE]:
            current_state = MENU
            return

        # AI for right paddle
        if ball.centery < right_paddle.centery and right_paddle.top > 0:
            right_paddle.y -= PADDLE_SPEED
        if ball.centery > right_paddle.centery and right_paddle.bottom < HEIGHT:
            right_paddle.y += PADDLE_SPEED

        # Ball movement
        ball.x += BALL_SPEED_X
        ball.y += BALL_SPEED_Y

        # Ball collision with top and bottom
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            BALL_SPEED_Y = -BALL_SPEED_Y
            play_sound(440, 0.1)  # Play sound on collision with top/bottom

        # Ball collision with paddles
        if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
            BALL_SPEED_X = -BALL_SPEED_X
            play_sound(880, 0.1)  # Play sound on collision with paddles

        # Ball out of bounds
        if ball.left <= 0:
            right_score += 1
            reset_ball()
            play_sound(220, 0.1)  # Play sound on scoring
        if ball.right >= WIDTH:
            left_score += 1
            reset_ball()
            play_sound(220, 0.1)  # Play sound on scoring

        # Drawing
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, left_paddle)
        pygame.draw.rect(screen, WHITE, right_paddle)
        pygame.draw.ellipse(screen, WHITE, ball)
        pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

        # Draw Scores
        left_text = font_large.render(str(left_score), True, WHITE)
        screen.blit(left_text, (WIDTH // 4 - left_text.get_width() // 2, 20))
        right_text = font_large.render(str(right_score), True, WHITE)
        screen.blit(right_text, (WIDTH * 3 // 4 - right_text.get_width() // 2, 20))

        pygame.display.flip()
        clock.tick(60)

# Restart Screen Function
def restart_screen():
    global current_state, left_score, right_score
    while current_state == RESTART:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    left_score = 0
                    right_score = 0
                    current_state = GAME
                elif event.key == pygame.K_n:
                    current_state = QUIT_GAME

        screen.fill(BLACK)

        # Draw Restart Message
        restart_text = font_large.render("Restart? Y/N", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(restart_text, restart_rect)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Main Loop
while True:
    if current_state == MENU:
        main_menu()
    elif current_state == CREDITS:
        credits_screen()
    elif current_state == GAME:
        game_loop()
    elif current_state == RESTART:
        restart_screen()
    elif current_state == QUIT_GAME:
        pygame.quit()
        sys.exit()
