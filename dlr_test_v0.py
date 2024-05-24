import pygame
import random

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Cat's Climber Feest Y2K4 M1 MAC")

white = 255, 255, 255
black = 0, 0, 0
desert = 210, 180, 140
player_c = 255, 215, 0
rock_c = 139, 69, 19
enemy_c = 255, 0, 0

font_title = pygame.font.Font(None, 72)
font_prompt = pygame.font.Font(None, 36)

player_speed = 5
rock_speed = 2
enemy_speed = 3
spawn_rate = 60

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(player_c)
        self.rect = self.image.get_rect(center=(width // 2, height - 25))

    def update(self):
        keys = pygame.key.get_pressed()
        self.rect.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_speed
        self.rect.clamp_ip(screen.get_rect())

class Rock(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(rock_c)
        self.rect = self.image.get_rect(topleft=(random.randint(0, width - 20), -20))

    def update(self):
        self.rect.y += rock_speed
        if self.rect.top > height:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(enemy_c)
        self.rect = self.image.get_rect(topleft=(random.randint(0, width - 30), -30))

    def update(self):
        self.rect.y += enemy_speed
        if self.rect.top > height:
            self.kill()

def start_menu():
    title = font_title.render("Cat's Climber Feest Y2K4 M1 MAC", True, white)
    title_rect = title.get_rect(center=(width // 2, height // 3))
    prompt = font_prompt.render("Press Z or Enter to Start", True, white)
    prompt_rect = prompt.get_rect(center=(width // 2, height // 2))

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key in (pygame.K_z, pygame.K_RETURN)):
                return e.type != pygame.QUIT

        screen.fill(black)
        screen.blit(title, title_rect)
        screen.blit(prompt, prompt_rect)
        pygame.display.flip()

def game_over():
    game_over_text = font_title.render("Game Over", True, white)
    game_over_rect = game_over_text.get_rect(center=(width // 2, height // 3))
    prompt = font_prompt.render("Press Y to Restart or N to Quit", True, white)
    prompt_rect = prompt.get_rect(center=(width // 2, height // 2))

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_n):
                return False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_y:
                return True

        screen.fill(black)
        screen.blit(game_over_text, game_over_rect)
        screen.blit(prompt, prompt_rect)
        pygame.display.flip()

def game():
    player = Player()
    rocks = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player, *rocks, *enemies)
    clock = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False

        if random.randrange(spawn_rate) == 0:
            rocks.add(Rock())
            enemies.add(Enemy())

        all_sprites.update()

        if pygame.sprite.spritecollideany(player, rocks) or pygame.sprite.spritecollideany(player, enemies):
            return game_over()

        screen.fill(desert)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)

while True:
    if not start_menu():
        break
    if not game():
        break

pygame.quit()
