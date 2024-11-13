import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Set up the display
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Atari-Style Space Invaders")

class Player(pygame.Rect):
    def __init__(self):
        super().__init__(WIDTH // 2, HEIGHT - 50, 50, 50)
        self.speed_x = 0
        self.speed_y = 0

    def move(self):
        if self.x + self.speed_x > 0 and self.x + self.speed_x < WIDTH:
            self.x += self.speed_x
        if self.y + self.speed_y > 0 and self.y + self.speed_y < HEIGHT - 50:
            self.y += self.speed_y

class Alien(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 30, 20)
        self.speed_x = random.choice([-2, 2])

    def move(self):
        if (random.random() < 0.05 and
                self.x + self.speed_x > 0 and
                self.x + self.speed_x < WIDTH - 30):
            self.x += self.speed_x
        elif (random.random() < 0.02 and
                self.y + 5 > 0 and
                self.y + 5 < HEIGHT - 50):
            self.y -= 5

    def reset(self, x, y):
        super().__init__(x, y, 30, 20)
        self.speed_x = random.choice([-2, 2])

class Bullet(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 5, 10)
        self.speed_y = 5

    def move(self):
        self.y += self.speed_y

def draw_text(text, size, x, y):
    font = pygame.font.SysFont("arial", size)
    text_surface = font.render(str(text), True, (255, 255, 255))
    win.blit(text_surface, (x, y))

def main():
    clock = pygame.time.Clock()
    score = 0
    player = Player()
    aliens = [Alien(random.randint(30, WIDTH - 60), random.randint(50, HEIGHT // 2)) for _ in range(10)]
    bullets = []
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append(Bullet(player.x + player.width // 2, player.y))
                elif event.key == pygame.K_w and player.speed_y != -5:
                    player.speed_y = -5
                elif event.key == pygame.K_s and player.speed_y != 5:
                    player.speed_y = 5
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_w, pygame.K_s):
                    player.speed_y = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x + player.speed_x > 0:
            player.speed_x = -5
        elif keys[pygame.K_d] and player.x + player.speed_x < WIDTH - 50:
            player.speed_x = 5
        else:
            player.speed_x = 0

        for bullet in bullets[:]:
            bullet.move()
            if (bullet.y > HEIGHT or
                    not win.get_rect().contains(bullet)):
                bullets.remove(bullet)
            elif any(bullet.colliderect(ali) for ali in aliens):
                score += 1
                bullets.remove(bullet)

        player.move()

        for alien in aliens:
            alien.move()
            if (random.random() < 0.05 and
                    alien.x + alien.width > WIDTH or
                    alien.x < 0):
                for a in aliens[:]:
                    if a == alien:
                        continue
                    a.reset(random.randint(30, WIDTH - 60), random.randint(50, HEIGHT // 2))

        collisions = [bullet.colliderect(ali) for bullet in bullets for ali in aliens]
        if any(c for c in collisions):
            score -= 1

        win.fill((0, 0, 0))
        pygame.draw.rect(win, WHITE, player)
        for alien in aliens:
            pygame.draw.rect(win, RED, alien)
        for bullet in bullets:
            pygame.draw.rect(win, (255, 255, 0), bullet)

        if any(alien.y > HEIGHT - 50 and not win.get_rect().contains(alien) for alien in aliens):
            running = False
            draw_text("Game Over!", 60, WIDTH // 2 - 150, HEIGHT // 2)
            pygame.display.update()
            pygame.time.wait(2000)

        if score >= len(aliens):
            running = False
            draw_text("You Win!", 60, WIDTH // 2 - 120, HEIGHT // 2 + 50)
            pygame.display.update()
            pygame.time.wait(2000)

        pygame.draw.line(win, WHITE, (0, HEIGHT - 40), (WIDTH, HEIGHT - 40), 5)

        draw_text(f"Score: {score}", 30, 10, 10)

        pygame.display.update()

        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
