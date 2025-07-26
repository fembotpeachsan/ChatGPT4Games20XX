import pygame, sys, random, numpy as np

# === INIT ===
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)  # Stereo
WIDTH, HEIGHT, FPS = 640, 480, 60
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("INSERT COIN - PONG 1979")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier", 36)

# === GAME OBJECTS ===
PADDLE_W, PADDLE_H = 12, 80
BALL_SIZE = 12
player = pygame.Rect(30, HEIGHT//2 - PADDLE_H//2, PADDLE_W, PADDLE_H)
cpu = pygame.Rect(WIDTH - 42, HEIGHT//2 - PADDLE_H//2, PADDLE_W, PADDLE_H)
ball = pygame.Rect(WIDTH//2, HEIGHT//2, BALL_SIZE, BALL_SIZE)
ball_vel = [random.choice([-4, 4]), random.choice([-3, 3])]
score_p, score_c = 0, 0
game_over = False

# === AUDIO ===
def square_beep(freq=440, duration=100):
    rate = 22050
    t = np.linspace(0, duration / 1000, int(rate * duration / 1000), endpoint=False)
    wave = 0.5 * np.sign(np.sin(2 * np.pi * freq * t))
    audio = (wave * 32767).astype(np.int16).reshape(-1, 1)
    stereo = np.repeat(audio, 2, axis=1)  # make stereo
    sound = pygame.sndarray.make_sound(stereo.copy())
    sound.play()

# === HELPERS ===
def reset_ball():
    ball.center = (WIDTH//2, HEIGHT//2)
    ball_vel[0] *= -1
    ball_vel[1] = random.choice([-3, -2, 2, 3])
    square_beep(220, 60)

def reset_game():
    global score_p, score_c, game_over
    score_p, score_c = 0, 0
    game_over = False
    reset_ball()

# === MAIN LOOP ===
def main():
    global score_p, score_c, game_over
    reset_ball()
    while True:
        screen.fill(BLACK)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        if not game_over:
            # PLAYER CONTROL (Mouse Y)
            mouse_y = pygame.mouse.get_pos()[1]
            player.centery = mouse_y
            player.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

            # CPU AI
            if cpu.centery < ball.centery: cpu.y += 4
            elif cpu.centery > ball.centery: cpu.y -= 4
            cpu.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

            # BALL
            ball.x += ball_vel[0]
            ball.y += ball_vel[1]

            if ball.top <= 0 or ball.bottom >= HEIGHT:
                ball_vel[1] *= -1
                square_beep(330, 50)

            if ball.colliderect(player) or ball.colliderect(cpu):
                ball_vel[0] *= -1
                square_beep(660, 50)

            if ball.left <= 0:
                score_c += 1
                reset_ball()
            elif ball.right >= WIDTH:
                score_p += 1
                reset_ball()

            if score_p >= 5 or score_c >= 5:
                game_over = True

        # DRAW
        pygame.draw.rect(screen, WHITE, player)
        pygame.draw.rect(screen, WHITE, cpu)
        pygame.draw.ellipse(screen, WHITE, ball)
        pygame.draw.aaline(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

        p_text = font.render(str(score_p), True, WHITE)
        c_text = font.render(str(score_c), True, WHITE)
        screen.blit(p_text, (WIDTH//4, 20))
        screen.blit(c_text, (WIDTH*3//4, 20))

        if game_over:
            msg = "WINNER PLAYER 1" if score_p > score_c else "CPU WINS"
            text = font.render(msg + "  (Y = Restart, N = Quit)", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            while True:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_y:
                            reset_game()
                            return main()
                        elif e.key == pygame.K_n:
                            pygame.quit(); sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

main()
