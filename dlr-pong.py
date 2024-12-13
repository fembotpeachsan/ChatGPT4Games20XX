import math
import random
import numpy as np
import os
import pygame

# --- Constants ---
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NEON_BLUE = (0, 153, 255)
NEON_PINK = (255, 105, 180)
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
PADDLE_SPEED = 7
BALL_SIZE = 15
WINNING_SCORE = 10  # Define the score needed to win

LEADERBOARD_FILE = 'leaderboard.txt'

# --- Initialize Pygame ---
pygame.init()
pygame.font.init()

# Default sound settings
SOUND_CHANNELS = 2  # Stereo by default

pygame.mixer.init(frequency=44100, size=-16, channels=SOUND_CHANNELS, buffer=512)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Synthwave Pong")

font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# --- Sound Generation ---
def generate_sound(frequency, duration, decay, volume=0.8):
    """Generates a basic synth sound with decay."""
    sample_rate = 44100
    num_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, num_samples, False)
    envelope = np.exp(-t * decay)
    wave = (np.sin(2 * np.pi * frequency * t) * envelope * volume * 32767).astype(np.int16)
    if SOUND_CHANNELS == 2:
        stereo_wave = np.column_stack((wave, wave))  # Stereo sound
    else:
        stereo_wave = wave  # Mono sound
    return pygame.sndarray.make_sound(stereo_wave)

# --- Initialize Sound Effects ---
def initialize_sounds():
    global paddle_hit_sound, wall_hit_sound, score_sound
    paddle_hit_sound = generate_sound(400, 0.1, 5)
    wall_hit_sound = generate_sound(1000, 0.05, 10)
    score_sound = generate_sound(200, 0.3, 3, volume=0.5)

initialize_sounds()

# --- Leaderboard Management ---
def load_leaderboard():
    leaderboard = []
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as file:
            for line in file:
                name, score = line.strip().split(',')
                leaderboard.append((name, int(score)))
    return leaderboard

def save_leaderboard(leaderboard):
    leaderboard = sorted(leaderboard, key=lambda x: x[1], reverse=True)[:10]  # Keep top 10
    with open(LEADERBOARD_FILE, 'w') as file:
        for name, score in leaderboard:
            file.write(f"{name},{score}\n")

def add_to_leaderboard(name, score):
    leaderboard = load_leaderboard()
    leaderboard.append((name, score))
    save_leaderboard(leaderboard)

# --- Game Functions ---
def reset_ball():
    global ball, ball_speed
    ball.center = (WIDTH // 2, HEIGHT // 2)
    ball_speed[0] = random.choice([-5, 5])
    ball_speed[1] = random.choice([-5, 5])

def draw_score(p1_score, p2_score):
    score_text = font.render(f"{p1_score} - {p2_score}", True, NEON_BLUE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

# --- Particle Effects ---
class Particle:
    def __init__(self, x, y, color, speed, angle):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.angle = angle
        self.size = random.randint(3, 8)
        self.life = random.randint(30, 60)

    def update(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.size -= 0.1
        self.life -= 1

    def draw(self, surface):
        if self.size > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

particles = []

def create_particles(x, y, color):
    for _ in range(random.randint(10, 20)):
        speed = random.uniform(2, 5)
        angle = random.uniform(0, 2 * math.pi)
        particles.append(Particle(x, y, color, speed, angle))

# --- Menu Functions ---
def main_menu():
    menu_options = ["Start Game", "Leaderboard", "Settings", "Exit"]
    selected = 0

    while True:
        screen.fill(BLACK)
        title_text = large_font.render("Synthwave Pong", True, NEON_BLUE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

        for i, option in enumerate(menu_options):
            color = NEON_PINK if i == selected else WHITE
            option_text = font.render(option, True, color)
            screen.blit(option_text, (WIDTH // 2 - option_text.get_width() // 2, 250 + i * 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if menu_options[selected] == "Start Game":
                        game_loop()
                    elif menu_options[selected] == "Leaderboard":
                        leaderboard_menu()
                    elif menu_options[selected] == "Settings":
                        settings_menu()
                    elif menu_options[selected] == "Exit":
                        pygame.quit()
                        exit()

def leaderboard_menu():
    leaderboard = load_leaderboard()
    while True:
        screen.fill(BLACK)
        title_text = large_font.render("Leaderboard", True, NEON_BLUE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        if not leaderboard:
            no_scores_text = font.render("No scores yet.", True, WHITE)
            screen.blit(no_scores_text, (WIDTH // 2 - no_scores_text.get_width() // 2, 200))
        else:
            for i, (name, score) in enumerate(leaderboard[:10]):
                entry_text = font.render(f"{i + 1}. {name} - {score}", True, NEON_PINK)
                screen.blit(entry_text, (WIDTH // 2 - entry_text.get_width() // 2, 150 + i * 40))

        back_text = font.render("Press ESC to return to Main Menu", True, WHITE)
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 100))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

def settings_menu():
    global SOUND_CHANNELS
    sound_options = ["Stereo", "Mono"]
    selected = 0
    current_sound = "Stereo" if SOUND_CHANNELS == 2 else "Mono"

    while True:
        screen.fill(BLACK)
        title_text = large_font.render("Settings", True, NEON_BLUE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

        for i, option in enumerate(sound_options):
            color = NEON_PINK if i == selected else WHITE
            option_text = font.render(option, True, color)
            screen.blit(option_text, (WIDTH // 2 - option_text.get_width() // 2, 250 + i * 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(sound_options)
                elif event.key == pygame.K_RETURN:
                    if sound_options[selected] == "Stereo":
                        SOUND_CHANNELS = 2
                    else:
                        SOUND_CHANNELS = 1
                    pygame.mixer.quit()
                    pygame.mixer.init(frequency=44100, size=-16, channels=SOUND_CHANNELS, buffer=512)
                    initialize_sounds()
                elif event.key == pygame.K_ESCAPE:
                    return

def game_over(winner_score, loser_score):
    # Prompt for player's name
    name = ""
    input_active = True
    while input_active:
        screen.fill(BLACK)
        game_over_text = large_font.render("Game Over", True, NEON_BLUE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 100))

        if winner_score > loser_score:
            winner = "Player 1"
            score = winner_score
        else:
            winner = "Player 2"
            score = loser_score

        winner_text = font.render(f"{winner} wins with {score} points!", True, NEON_PINK)
        screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, 200))

        prompt_text = font.render("Enter your name: " + name, True, WHITE)
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, 300))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name.strip() == "":
                        name = "Anonymous"
                    add_to_leaderboard(name, score)
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 10:
                        name += event.unicode

def game_loop():
    global player1, player2, ball, ball_speed, player1_score, player2_score

    # Initialize game objects
    player1 = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    player2 = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
    ball_speed = [5, 5]
    player1_score = 0
    player2_score = 0
    particles.clear()

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # --- Player Input ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player1.top > 0:
            player1.y -= PADDLE_SPEED
        if keys[pygame.K_s] and player1.bottom < HEIGHT:
            player1.y += PADDLE_SPEED
        if keys[pygame.K_UP] and player2.top > 0:
            player2.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and player2.bottom < HEIGHT:
            player2.y += PADDLE_SPEED

        # --- Ball Movement ---
        ball.x += ball_speed[0]
        ball.y += ball_speed[1]

        # --- Ball Collisions ---
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            wall_hit_sound.play()
            ball_speed[1] *= -1
            create_particles(ball.centerx, ball.centery, NEON_PINK)

        if ball.colliderect(player1) or ball.colliderect(player2):
            paddle_hit_sound.play()
            if ball.colliderect(player1):
                ball_speed[0] = abs(ball_speed[0]) * 1.1  # Ensure it moves right
                create_particles(ball.centerx, ball.centery, NEON_BLUE)
            else:
                ball_speed[0] = -abs(ball_speed[0]) * 1.1  # Ensure it moves left
                create_particles(ball.centerx, ball.centery, NEON_PINK)
            ball_speed[1] *= 1.1

        # --- Scoring ---
        if ball.left <= 0:
            player2_score += 1
            score_sound.play()
            reset_ball()
        if ball.right >= WIDTH:
            player1_score += 1
            score_sound.play()
            reset_ball()

        # --- Check for Winning ---
        if player1_score >= WINNING_SCORE or player2_score >= WINNING_SCORE:
            running = False
            game_over(player1_score, player2_score)

        # --- Drawing ---
        screen.fill(BLACK)

        # Draw particles
        for particle in particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.life <= 0:
                particles.remove(particle)

        pygame.draw.rect(screen, NEON_BLUE, player1)
        pygame.draw.rect(screen, NEON_PINK, player2)
        pygame.draw.ellipse(screen, WHITE, ball)
        draw_score(player1_score, player2_score)

        # --- Update Display ---
        pygame.display.flip()
        clock.tick(60)

# --- Start the Game ---
if __name__ == "__main__":
    main_menu()
    pygame.quit()
