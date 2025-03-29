import pygame
import sys
import array
import random  # Added for random barrel ladder descent

pygame.init()
screen = pygame.display.set_mode((600, 400))
clock = pygame.time.Clock()

MENU, PLAYING = 0, 1
game_state = MENU

# Define fonts globally
hud_font = pygame.font.Font(None, 24)
challenge_font = pygame.font.Font(None, 36)

# Initialize sound mixer
pygame.mixer.init(frequency=22050, size=-16, channels=1)

# Create a simple "ding" sound using a square wave
def create_ding_sound():
    sample_rate = 22050
    duration = 0.1  # seconds
    frequency = 880  # Hz (A5 note)
    samples = int(sample_rate * duration)
    
    sound_array = array.array('h')  # 'h' for 16-bit signed integers
    for i in range(samples):
        value = 32767 if (i * frequency / sample_rate) % 1 < 0.5 else -32767
        sound_array.append(value)
    
    return pygame.mixer.Sound(sound_array)

ding_sound = create_ding_sound()

class ArcadeJumpman:
    def __init__(self):
        self.rect = pygame.Rect(480, 340, 16, 24)
        self.velocity_y = 0
        self.on_ground = False
        self.on_ladder = False
        self.lives = 3
        self.score = 0
        self.just_jumped_over = False
        self.last_jump_time = 0

class Barrel:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.falling = False

class DK:
    def __init__(self):
        self.rect = pygame.Rect(100, 50, 64, 64)
        self.anim_frame = 0

jumpman = ArcadeJumpman()
dk = DK()
barrels = []
platforms = [
    pygame.Rect(0, 368, 600, 32),
    pygame.Rect(0, 268, 500, 32),
    pygame.Rect(100, 168, 500, 32),
    pygame.Rect(0, 68, 500, 32)
]
ladders = [
    pygame.Rect(450, 268, 32, 100),
    pygame.Rect(150, 168, 32, 100),
    pygame.Rect(450, 68, 32, 100)
]

def game_loop():
    global game_state, jumpman
    game_start_time = 0
    show_climb_message = False
    last_frame_time = pygame.time.get_ticks()
    delta_time = 16
    last_barrel_spawn = 0
    dk_last_anim = 0

    while True:
        current_time = pygame.time.get_ticks()
        delta_time = current_time - last_frame_time
        last_frame_time = current_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if game_state == MENU:
                    if event.key in (pygame.K_z, pygame.K_SPACE):
                        game_state = PLAYING
                        jumpman = ArcadeJumpman()
                        barrels.clear()
                        game_start_time = current_time
                        show_climb_message = True
                        dk.anim_frame = 0
                        dk_last_anim = current_time
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU

        if game_state == PLAYING:
            elapsed_time = current_time - game_start_time
            show_climb_message = elapsed_time < 5000
            
            if not show_climb_message:
                handle_arcade_physics(delta_time)
                barrel_ai(delta_time, current_time)
            
            if current_time - dk_last_anim > 500:
                dk.anim_frame = (dk.anim_frame + 1) % 2
                dk_last_anim = current_time

            player_rect = jumpman.rect.inflate(-8, -8)
            jumpman.just_jumped_over = False
            
            # Check for winning condition
            if jumpman.rect.top < 68:  # Reached top platform
                print("Level Complete! 🍌")
                jumpman.score += 1000  # Bonus points for completion
                game_state = MENU
            
            for barrel in barrels[:]:
                barrel_rect = barrel.rect.inflate(-8, -8)
                if player_rect.colliderect(barrel_rect):
                    handle_player_death(current_time)
                    break
                elif (jumpman.velocity_y < 0 and
                      player_rect.bottom < barrel_rect.top and
                      player_rect.left < barrel_rect.right and
                      player_rect.right > barrel_rect.left and
                      current_time - jumpman.last_jump_time < 500):
                    if not jumpman.just_jumped_over:
                        jumpman.just_jumped_over = True
                        jumpman.score += 100
                        ding_sound.play()

        screen.fill((184, 184, 184))
        if game_state == PLAYING:
            draw_game_entities()
            draw_hud(hud_font, current_time, show_climb_message, elapsed_time)
        else:
            draw_menu()

        pygame.display.flip()
        clock.tick(60)

def handle_arcade_physics(delta):
    keys = pygame.key.get_pressed()
    move_speed = 0.25 * delta
    
    if keys[pygame.K_LEFT]:
        jumpman.rect.x = max(0, jumpman.rect.x - int(move_speed))
    if keys[pygame.K_RIGHT]:
        jumpman.rect.x = min(576, jumpman.rect.x + int(move_speed))
    
    jumpman.velocity_y += 0.5 * (delta / 16)
    jumpman.rect.y += int(jumpman.velocity_y)
    jumpman.on_ground = False
    
    for platform in platforms:
        if jumpman.rect.colliderect(platform):
            if jumpman.velocity_y > 0:
                jumpman.rect.bottom = platform.top
                jumpman.velocity_y = 0
                jumpman.on_ground = True
    
    jumpman.on_ladder = any(jumpman.rect.clip(l) == jumpman.rect for l in ladders)
    if jumpman.on_ladder:
        climb_speed = int(0.15 * delta)
        if keys[pygame.K_UP]:
            jumpman.rect.y = max(0, jumpman.rect.y - climb_speed)
        if keys[pygame.K_DOWN]:
            jumpman.rect.y = min(368, jumpman.rect.y + climb_speed)
    
    if keys[pygame.K_SPACE] and jumpman.on_ground:
        jumpman.velocity_y = -12 * (delta / 16)
        jumpman.on_ground = False
        jumpman.last_jump_time = pygame.time.get_ticks()

def barrel_ai(delta, current_time):
    global last_barrel_spawn
    barrel_spawn_rate = 1500
    barrel_speed = 0.15 * delta
    fall_speed = int(5 * (delta / 16))
    
    if current_time - last_barrel_spawn > barrel_spawn_rate:
        barrels.append(Barrel(dk.rect.x + 48, dk.rect.y + 32))
        last_barrel_spawn = current_time
    
    for barrel in barrels[:]:
        # First handle falling movement
        if barrel.falling:
            barrel.rect.y += fall_speed
            # Check collision with platforms
            for platform in platforms:
                if barrel.rect.colliderect(platform):
                    barrel.rect.bottom = platform.top
                    barrel.falling = False
                    break
        
        # Then handle horizontal movement and ladder descent
        if not barrel.falling:
            # Check if barrel is near a ladder
            for ladder in ladders:
                if (ladder.left - 5 < barrel.rect.centerx < ladder.right + 5 and
                    abs(barrel.rect.bottom - ladder.top) < 5 and
                    random.random() < 0.3):  # 30% chance to go down ladder
                    barrel.rect.centerx = ladder.centerx  # Align with ladder
                    barrel.falling = True
                    break
            else:  # If not falling down a ladder, move horizontally
                barrel.rect.x += int(barrel_speed)
            
            # Check if barrel should fall off platform
            barrel.falling = not any(barrel.rect.colliderect(p) for p in platforms)
        
        # Remove barrels that go off screen
        if barrel.rect.x > 650 or barrel.rect.y > 400:
            barrels.remove(barrel)
            jumpman.score = min(jumpman.score + 100, 999999)

def handle_player_death(current_time):
    jumpman.lives -= 1
    if jumpman.lives > 0:
        jumpman.rect.topleft = (480, 340)
        barrels.clear()
    else:
        global game_state
        game_state = MENU
        jumpman.score = 0

def draw_game_entities():
    for platform in platforms:
        pygame.draw.rect(screen, (142, 62, 32), platform)
    for ladder in ladders:
        pygame.draw.rect(screen, (80, 80, 80), ladder)
    pygame.draw.rect(screen, (231, 52, 35), dk.rect)
    pygame.draw.rect(screen, (40, 40, 255), jumpman.rect)
    for barrel in barrels:
        pygame.draw.circle(screen, (142, 62, 32), barrel.rect.center, 8)

def draw_hud(font, current_time, show_climb, elapsed):
    screen.blit(font.render(f"LIVES: {jumpman.lives}", True, (255, 223, 0)), (10, 10))
    screen.blit(font.render(f"SCORE: {jumpman.score:06d}", True, (255, 223, 0)), (400, 10))
    
    if show_climb:
        time_remaining = max(0, 5 - (elapsed // 1000))
        text = challenge_font.render("HOW HIGH CAN YOU CLIMB?", True, (255, 223, 0))
        screen.blit(text, text.get_rect(center=(300, 150)))
        timer_text = challenge_font.render(str(time_remaining), True, (255, 0, 0))
        screen.blit(timer_text, timer_text.get_rect(center=(300, 200)))

def draw_menu():
    font = pygame.font.Font(None, 36)
    text = font.render("PRESS Z OR SPACE TO START", True, (255, 223, 0))
    screen.blit(text, text.get_rect(center=(300, 200)))

if __name__ == "__main__":
    last_barrel_spawn = 0
    game_loop()
