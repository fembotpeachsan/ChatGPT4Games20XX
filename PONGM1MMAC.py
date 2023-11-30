import pygame
import random

# Define the Paddle class
class Paddle(pygame.Rect):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

    def move(self, up, down, screen_height):
        if up:
            self.y -= 5
        if down:
            self.y += 5
        self.y = max(min(self.y, screen_height - self.height), 0)

# Define the Ball class
class Ball(pygame.Rect):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        self.reset()

    def move_and_collide(self, paddles, screen_width, screen_height):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.top <= 0 or self.bottom >= screen_height:
            self.speed_y *= -1
        for paddle in paddles:
            if self.colliderect(paddle):
                self.speed_x *= -1
                self.speed_y += random.choice([-2, 2])
        if self.left <= 0 or self.right >= screen_width:
            return True
        return False

    def reset(self):
        self.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = random.choice([-5, 5])
        self.speed_y = random.choice([-5, 5])

# Main menu function
def main_menu(screen, font):
    menu_active = True
    while menu_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:  # Start game
                    menu_active = False
                elif event.key == pygame.K_c:  # View credits
                    credits_screen(screen, font)

        screen.fill((0, 0, 0))
        menu_text = font.render("PONG M1 MAC PORT by @Catdev", True, (255, 255, 255))
        start_text = font.render("Press Z to Start", True, (255, 255, 255))
        credits_text = font.render("Press C for Credits", True, (255, 255, 255))
        screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(credits_text, (SCREEN_WIDTH // 2 - credits_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        pygame.display.flip()
        clock.tick(60)

# Credits screen function
def credits_screen(screen, font):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:  # Press Z to go back
                    running = False
## [HDRV0]
        screen.fill((0, 0, 0))
        credits_title = font.render("Credits", True, (255, 255, 255))
        dev_text = font.render("Developed by @Catdev", True, (255, 255, 255))
        version_text = font.render("Version: INFDEV 1.0", True, (255, 255, 255))
        back_text = font.render("Press Z to go back", True, (255, 255, 255))
        screen.blit(credits_title, (SCREEN_WIDTH // 2 - credits_title.get_width() // 2, 100))
        screen.blit(dev_text, (SCREEN_WIDTH // 2 - dev_text.get_width() // 2, 150))
        screen.blit(version_text, (SCREEN_WIDTH // 2 - version_text.get_width() // 2, 200))
        screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT - 50))
        pygame.display.flip()
        clock.tick(60)

# Initialize Pygame and setup screen
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong")
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# Show main menu
main_menu(screen, font)

# Initialize game elements
left_paddle = Paddle(50, SCREEN_HEIGHT // 2 - 45, 15, 90)
right_paddle = Paddle(SCREEN_WIDTH - 65, SCREEN_HEIGHT // 2 - 45, 15, 90)
ball = Ball(SCREEN_WIDTH // 2 - 7.5, SCREEN_HEIGHT // 2 - 7.5, 15)
left_score, right_score = 0, 0

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Player input
    keys = pygame.key.get_pressed()
    left_paddle.move(keys[pygame.K_w], keys[pygame.K_s], SCREEN_HEIGHT)

    # Simple AI for right paddle
    right_paddle.move(ball.y < right_paddle.y, ball.y > right_paddle.y, SCREEN_HEIGHT)

    # Ball movement and scoring
    if ball.move_and_collide([left_paddle, right_paddle], SCREEN_WIDTH, SCREEN_HEIGHT):
        if ball.x < SCREEN_WIDTH // 2:
            right_score += 1
        else:
            left_score += 1
        ball.reset()

    # Drawing
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 255, 255), left_paddle)
    pygame.draw.rect(screen, (255, 255, 255), right_paddle)
    pygame.draw.ellipse(screen, (255, 255, 255), ball)
    left_score_text = font.render(str(left_score), True, (255, 255, 255))
    right_score_text = font.render(str(right_score), True, (255, 255, 255))
    screen.blit(left_score_text, (50, 20))
    screen.blit(right_score_text, (SCREEN_WIDTH - 80, 20))

    pygame.display.flip()
    clock.tick(60)
