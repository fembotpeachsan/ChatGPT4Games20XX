 
# Title: Space Invaders
import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 640, 480
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

class Alien(pygame.Rect):
    def __init__(self):
        super().__init__(random.randint(0, WIDTH - 50), random.randint(0, 50), 50, 50)
        self.speed_x = 2
        self.speed_y = 1

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

class Bullet(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 5, 10)
        self.speed_y = -3

    def update(self):
        self.y += self.speed_y

class Player(pygame.Rect):
    def __init__(self):
        super().__init__(WIDTH / 2, HEIGHT - 50, 50, 50)

    def move_left(self):
        self.x -= 5
        if self.x < 0:
            self.x = 0

    def move_right(self):
        self.x += 5
        if self.x > WIDTH - 50:
            self.x = WIDTH - 50

def draw_alien(alien):
    pygame.draw.rect(screen, RED, alien)

def draw_bullet(bullet):
    pygame.draw.rect(screen, WHITE, bullet)

def draw_player(player):
    pygame.draw.rect(screen, GREEN, player)

def main():
    clock = pygame.time.Clock()
    score = 0
    aliens = [Alien() for _ in range(10)]
    bullets = []
    player = Player()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append(Bullet(player.x + 25, player.y))
                elif event.key == pygame.K_LEFT:
                    player.move_left()
                elif event.key == pygame.K_RIGHT:
                    player.move_right()

        screen.fill((0, 0, 0))

        for alien in aliens:
            draw_alien(alien)
            alien.update()
            if alien.x < -50 or alien.x > WIDTH + 50:
                score -= 10
                alien.x = random.randint(0, WIDTH - 50)
                alien.y = random.randint(0, 50)

        for bullet in bullets:
            draw_bullet(bullet)
            bullet.update()
            if bullet.y < 0:
                bullets.remove(bullet)
            else:
                for alien in aliens:
                    if bullet.colliderect(alien):
                        score += 10
                        bullets.remove(bullet)
                        aliens.remove(alien)

        player.move_left()  # Move the player horizontally

        draw_player(player)  # Draw the player at its updated position

        font = pygame.font.Font(None, 36)
        text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(text, (10, 10))

        if any(alien.x < -50 for alien in aliens):
            score -= 100
            print("Game Over! Your final score is", score)
            running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
 
