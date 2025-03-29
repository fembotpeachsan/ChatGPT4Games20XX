import pygame
import sys
import random

# Pygame initialization for M1 Macs
pygame.init()
screen = pygame.display.set_mode((600, 400), pygame.DOUBLEBUF | pygame.SCALED)
pygame.display.set_caption("Donkery Kong Arcade Edition")
clock = pygame.time.Clock()

# Game state constants
MENU, PLAYING, CREDITS = 0, 1, 2
game_state = MENU

# Arcade physics constants
GRAVITY = 0.8
JUMP_FORCE = -14
MOVE_SPEED = 4
LADDER_SPEED = 3
PLATFORM_HEIGHT = 20

# Authentic color palette
COLORS = {
    "DK_RED": (231, 52, 35),
    "MARIO_BLUE": (40, 40, 255),
    "BARREL_BROWN": (142, 62, 32),
    "BACKGROUND": (184, 184, 184),
    "PLATFORM": (142, 62, 32),
    "LADDER": (80, 80, 80),
    "TEXT": (255, 223, 0)
}

class ArcadeJumpman:
    def __init__(self):
        self.rect = pygame.Rect(480, 340, 24, 32)
        self.velocity_y = 0
        self.on_ground = True
        self.on_ladder = False
        self.direction = 1
        self.lives = 3
        self.score = 0

class DonkeyKong:
    def __init__(self):
        self.rect = pygame.Rect(80, 60, 64, 48)
        self.anim_frame = 0
        self.anim_timer = 0

class Barrel:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.speed = 3
        self.direction = 1
        self.falling = False

# Level setup
platforms = [
    pygame.Rect(0, 380, 600, PLATFORM_HEIGHT),  # Ground
    pygame.Rect(100, 300, 200, PLATFORM_HEIGHT),
    pygame.Rect(300, 220, 200, PLATFORM_HEIGHT),
    pygame.Rect(100, 140, 200, PLATFORM_HEIGHT)
]

ladders = [
    pygame.Rect(460, 340, 16, 120),
    pygame.Rect(380, 220, 16, 120),
    pygame.Rect(140, 140, 16, 120)
]

# Game entities
jumpman = ArcadeJumpman()
dk = DonkeyKong()
barrels = []

def draw_menu():
    screen.fill(COLORS["BACKGROUND"])
    title_font = pygame.font.Font("freesansbold.ttf", 48)
    
    title = title_font.render("DONKERY KONG", True, COLORS["TEXT"])
    screen.blit(title, (300 - title.get_width()//2, 80))
    
    prompt = title_font.render("PRESS Z TO START", True, COLORS["TEXT"])
    screen.blit(prompt, (300 - prompt.get_width()//2, 200))
    
    copyright = pygame.font.Font(None, 24).render(
        "© 2024 DEEPSEEK ARCADE", True, COLORS["TEXT"])
    screen.blit(copyright, (10, 370))

def handle_arcade_physics():
    # Horizontal movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        jumpman.rect.x -= MOVE_SPEED
        jumpman.direction = -1
    if keys[pygame.K_RIGHT]:
        jumpman.rect.x += MOVE_SPEED
        jumpman.direction = 1
    
    # Vertical movement
    jumpman.velocity_y += GRAVITY
    jumpman.rect.y += jumpman.velocity_y
    jumpman.on_ground = False
    
    # Platform collision
    for platform in platforms:
        if jumpman.rect.colliderect(platform):
            if jumpman.velocity_y > 0:
                jumpman.rect.bottom = platform.top
                jumpman.velocity_y = 0
                jumpman.on_ground = True
    
    # Ladder climbing
    jumpman.on_ladder = False
    for ladder in ladders:
        if jumpman.rect.colliderect(ladder):
            jumpman.on_ladder = True
            if keys[pygame.K_UP]:
                jumpman.rect.y -= LADDER_SPEED
            if keys[pygame.K_DOWN]:
                jumpman.rect.y += LADDER_SPEED
    
    # Jumping
    if keys[pygame.K_SPACE] and jumpman.on_ground:
        jumpman.velocity_y = JUMP_FORCE
        jumpman.on_ground = False

def barrel_ai():
    # DK animation
    dk.anim_timer += 1
    if dk.anim_timer > 30:
        dk.anim_frame = (dk.anim_frame + 1) % 2
        dk.anim_timer = 0
    
    # Barrel spawning
    if random.randint(0, 100) < 2 and dk.anim_frame == 1:
        barrels.append(Barrel(dk.rect.x + 48, dk.rect.y + 32))
    
    # Barrel movement
    for barrel in barrels[:]:
        barrel.falling = True
        for platform in platforms:
            if barrel.rect.colliderect(platform):
                barrel.falling = False
                barrel.rect.bottom = platform.top
                barrel.direction = random.choice([-1, 1]) if random.random() < 0.2 else barrel.direction
                break
        
        if barrel.falling:
            barrel.rect.y += 4
        else:
            barrel.rect.x += barrel.speed * barrel.direction
        
        if barrel.rect.x < -50 or barrel.rect.x > 650:
            barrels.remove(barrel)
            jumpman.score += 100

def game_loop():
    global game_state
    
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if game_state == MENU and event.key in (pygame.K_z, pygame.K_SPACE):
                    game_state = PLAYING
                    jumpman.__init__()
                    barrels.clear()
                
                if game_state == PLAYING and event.key == pygame.K_ESCAPE:
                    game_state = MENU
        
        # Game logic
        if game_state == PLAYING:
            handle_arcade_physics()
            barrel_ai()
            
            # Collision detection
            for barrel in barrels:
                if jumpman.rect.colliderect(barrel.rect):
                    jumpman.lives -= 1
                    if jumpman.lives > 0:
                        jumpman.rect.topleft = (480, 340)
                    else:
                        game_state = MENU
                    break
        
        # Rendering
        screen.fill(COLORS["BACKGROUND"])
        
        if game_state == PLAYING:
            # Draw platforms
            for platform in platforms:
                pygame.draw.rect(screen, COLORS["PLATFORM"], platform)
            
            # Draw ladders
            for ladder in ladders:
                pygame.draw.rect(screen, COLORS["LADDER"], ladder)
            
            # Draw DK
            pygame.draw.rect(screen, COLORS["DK_RED"], dk.rect)
            
            # Draw barrels
            for barrel in barrels:
                pygame.draw.circle(screen, COLORS["BARREL_BROWN"], barrel.rect.center, 8)
            
            # Draw Jumpman
            pygame.draw.rect(screen, COLORS["MARIO_BLUE"], jumpman.rect)
            
            # Draw HUD
            font = pygame.font.Font(None, 24)
            lives_text = font.render(f"LIVES: {jumpman.lives}", True, COLORS["TEXT"])
            score_text = font.render(f"SCORE: {jumpman.score}", True, COLORS["TEXT"])
            screen.blit(lives_text, (10, 10))
            screen.blit(score_text, (400, 10))
        
        elif game_state == MENU:
            draw_menu()
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    game_loop()
