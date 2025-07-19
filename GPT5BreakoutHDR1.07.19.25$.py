import pygame
import sys
import numpy as np

# --- SOUND GEN SETUP ---
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
_, _, mixer_channels = pygame.mixer.get_init() or (44100, -16, 2)

def generate_tone(freq, duration, sample_rate=44100, volume=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = np.sin(2 * np.pi * freq * t)
    wave = (wave * volume * 32767).astype(np.int16)
    if mixer_channels == 2:
        wave = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(wave)

beep_sound = generate_tone(880, 0.05)
boop_sound = generate_tone(440, 0.1)
wall_boop  = generate_tone(220, 0.05)

WIDTH, HEIGHT = 640, 480
BG_COLOR = (0, 0, 0)
OUTLINE_COLOR = (255, 255, 255)

# --- MAIN MENU FUNCTION ---
def main_menu(screen, clock):
    font_big = pygame.font.SysFont(None, 56, bold=True)
    font_small = pygame.font.SysFont(None, 32)
    while True:
        screen.fill(BG_COLOR)
        title = font_big.render("Breakout: Tkinter Vibes", True, OUTLINE_COLOR)
        start = font_small.render("Press SPACE/ENTER or Click to Start", True, OUTLINE_COLOR)
        hint = font_small.render("Move: A/D    Launch: W", True, OUTLINE_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        screen.blit(start, (WIDTH//2 - start.get_width()//2, HEIGHT//2 + 20))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 70))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                boop_sound.play()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                boop_sound.play()
                return
        clock.tick(30)

# --- GAME FUNCTION ---
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Breakout: Tkinter Vibes")
    clock = pygame.time.Clock()
    main_menu(screen, clock)

    # --- GAME INIT ---
    PADDLE_COLOR = (200, 200, 200)
    BALL_COLOR = (255, 255, 255)
    BRICK_COLOR = (150, 150, 150)
    paddle_width, paddle_height = 80, 10
    paddle_x = WIDTH // 2 - paddle_width // 2
    paddle_y = HEIGHT - 30
    paddle_speed = 8

    ball_radius = 8
    ball_x = float(WIDTH // 2)
    ball_y = float(HEIGHT // 2)
    ball_dx = 3.0
    ball_dy = -3.0
    ball_launched = True
    ball_speed = 5.0

    brick_width = WIDTH // 10
    brick_height = 20
    bricks = []
    for row in range(5):
        for col in range(10):
            brick_x = col * brick_width
            brick_y = row * (brick_height + 5) + 30
            bricks.append(pygame.Rect(brick_x, brick_y, brick_width - 2, brick_height))

    lives = 3
    bricks_broken = 0

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            paddle_x = max(0, paddle_x - paddle_speed)
        if keys[pygame.K_d]:
            paddle_x = min(WIDTH - paddle_width, paddle_x + paddle_speed)
        if keys[pygame.K_w] and not ball_launched:
            ball_launched = True
            ball_dy = -ball_speed
            current_speed = np.sqrt(ball_dx ** 2 + ball_dy ** 2)
            if current_speed != ball_speed:
                ball_dx = ball_dx * ball_speed / current_speed
                ball_dy = ball_dy * ball_speed / current_speed

        if ball_launched:
            ball_x += ball_dx
            ball_y += ball_dy
            if ball_x - ball_radius < 0 or ball_x + ball_radius > WIDTH:
                ball_dx = -ball_dx
                ball_x = max(ball_radius, min(WIDTH - ball_radius, ball_x))
                wall_boop.play()
            if ball_y - ball_radius < 0:
                ball_dy = -ball_dy
                ball_y = max(ball_radius, ball_y)
                wall_boop.play()
            paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)
            ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius * 2, ball_radius * 2)
            if ball_rect.colliderect(paddle_rect) and ball_dy > 0:
                ball_dy = -ball_dy
                ball_y = paddle_y - ball_radius
                boop_sound.play()
                hit_pos = (ball_x - paddle_x) / paddle_width - 0.5
                ball_dx += hit_pos * 4
                current_speed = np.sqrt(ball_dx ** 2 + ball_dy ** 2)
                ball_dx = ball_dx * ball_speed / current_speed
                ball_dy = ball_dy * ball_speed / current_speed
            for i in range(len(bricks) - 1, -1, -1):
                if ball_rect.colliderect(bricks[i]):
                    ball_dy = -ball_dy
                    if ball_dy > 0:
                        ball_y = bricks[i].top - ball_radius
                    else:
                        ball_y = bricks[i].bottom + ball_radius
                    del bricks[i]
                    beep_sound.play()
                    bricks_broken += 1
                    break
            if ball_y + ball_radius > HEIGHT:
                lives -= 1
                ball_launched = False
                ball_x = WIDTH // 2
                ball_y = HEIGHT // 2
                ball_dx = 3 if np.random.random() > 0.5 else -3
                ball_dy = 0
                wall_boop.play()
                if lives <= 0:
                    running = False

        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, PADDLE_COLOR, (paddle_x, paddle_y, paddle_width, paddle_height))
        pygame.draw.rect(screen, OUTLINE_COLOR, (paddle_x, paddle_y, paddle_width, paddle_height), 1)
        pygame.draw.circle(screen, BALL_COLOR, (int(ball_x), int(ball_y)), ball_radius)
        pygame.draw.circle(screen, OUTLINE_COLOR, (int(ball_x), int(ball_y)), ball_radius, 1)
        for brick in bricks:
            pygame.draw.rect(screen, BRICK_COLOR, brick)
            pygame.draw.rect(screen, OUTLINE_COLOR, brick, 1)
        font = pygame.font.SysFont(None, 24)
        lives_text = font.render(f"Lives: {lives}", True, OUTLINE_COLOR)
        score_text = font.render(f"Broken: {bricks_broken}", True, OUTLINE_COLOR)
        screen.blit(lives_text, (10, 10))
        screen.blit(score_text, (WIDTH - 100, 10))
        if len(bricks) == 0:
            win_text = font.render("Win! All broken.", True, OUTLINE_COLOR)
            screen.blit(win_text, (WIDTH // 2 - 80, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(2000)
            running = False
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
