import pygame
import sys
import random

# Initialize Pygame with MacOS optimizations
pygame.init()
screen = pygame.display.set_mode((600, 400), pygame.DOUBLEBUF)
pygame.display.set_caption("Donkery Kong M1 Edition")
clock = pygame.time.Clock()

# Game state management
global game_state
MENU, PLAYING, CREDITS = 0, 1, 2
game_state = MENU

# Physics constants
GRAVITY = 0.5
JUMP_FORCE = -12
PLATFORM_HEIGHT = 20

# Color definitions
COLORS = {
    "RED": (255, 0, 0),
    "BROWN": (139, 69, 19),
    "BLUE": (0, 0, 255),
    "BLACK": (0, 0, 0),
    "CREAM": (255, 253, 208),
    "YELLOW": (255, 255, 0)
}

# Optimized game objects
class Jumpman:
    def __init__(self):
        self.rect = pygame.Rect(300, 300, 30, 50)
        self.velocity_y = 0
        self.on_ground = False
        self.lives = 3
        self.score = 0

class DonkeyKong:
    def __init__(self):
        self.rect = pygame.Rect(50, 50, 80, 60)
        self.animation_frame = 0

class Barrel:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.speed = random.randint(3, 5)
        self.falling = False

# Initialize entities
jumpman = Jumpman()
dk = DonkeyKong()
barrels = []
ramps = [
    pygame.Rect(100, 150, 200, PLATFORM_HEIGHT),
    pygame.Rect(300, 250, 200, PLATFORM_HEIGHT)
]

# Font handling
def get_font(size):
    return pygame.font.Font(None, size)

def handle_jumpman_physics():
    jumpman.velocity_y += GRAVITY
    jumpman.rect.y += jumpman.velocity_y
    jumpman.on_ground = False

    for platform in ramps:
        if jumpman.rect.colliderect(platform):
            if jumpman.velocity_y > 0:
                jumpman.rect.bottom = platform.top
                jumpman.velocity_y = 0
                jumpman.on_ground = True

    jumpman.rect.x = max(0, min(jumpman.rect.x, 570))
    jumpman.rect.y = max(0, min(jumpman.rect.y, 350))

def handle_barrel_physics():
    for barrel in barrels[:]:
        barrel.falling = True
        for platform in ramps:
            if barrel.rect.colliderect(platform):
                barrel.falling = False
                barrel.rect.bottom = platform.top
                break

        if barrel.falling:
            barrel.rect.y += 4
        else:
            barrel.rect.x += barrel.speed

        if barrel.rect.x > 600:
            barrels.remove(barrel)
            jumpman.score += 100

def draw_menu():
    screen.fill(COLORS["BLACK"])
    title = get_font(48).render("DONKERY KONG", True, COLORS["RED"])
    screen.blit(title, (300 - title.get_width()//2, 50))
    pygame.display.flip()

def game_loop():
    global game_state  # Critical fix here
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if game_state == MENU and event.key == pygame.K_RETURN:
                    game_state = PLAYING
                    jumpman.__init__()  # Reset player
                    barrels.clear()
                
                if game_state == PLAYING and event.key == pygame.K_SPACE:
                    if jumpman.on_ground:
                        jumpman.velocity_y = JUMP_FORCE

        if game_state == PLAYING:
            keys = pygame.key.get_pressed()
            jumpman.rect.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 5
            handle_jumpman_physics()
            
            # Barrel spawning
            if random.random() < 0.02:
                barrels.append(Barrel(dk.rect.x + 40, dk.rect.y + 50))
            
            handle_barrel_physics()

            # Collision check
            for barrel in barrels:
                if jumpman.rect.colliderect(barrel.rect):
                    jumpman.lives -= 1
                    if jumpman.lives <= 0:
                        game_state = MENU
                    else:
                        jumpman.rect.topleft = (300, 300)
                    break

        # Drawing
        screen.fill(COLORS["CREAM"])
        if game_state == PLAYING:
            pygame.draw.rect(screen, COLORS["RED"], dk.rect)
            pygame.draw.rect(screen, COLORS["BLUE"], jumpman.rect)
            for barrel in barrels:
                pygame.draw.circle(screen, COLORS["BROWN"], barrel.rect.center, 10)
            
            # HUD
            lives_text = get_font(24).render(f"Lives: {jumpman.lives}", True, COLORS["BLACK"])
            screen.blit(lives_text, (10, 10))
        elif game_state == MENU:
            draw_menu()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    game_loop()
