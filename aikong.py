  import pygame
from array import array
import sys
# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Screen settings
WIDTH, HEIGHT = 640, 480
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Donkey Kong")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)

# Fonts
font = pygame.font.Font(None, 36)

# Platform settings
PLATFORM_HEIGHT = 15
platforms = [
    pygame.Rect(50, HEIGHT - 50, 540, PLATFORM_HEIGHT),
    pygame.Rect(100, HEIGHT - 120, 440, PLATFORM_HEIGHT),
    pygame.Rect(50, HEIGHT - 190, 540, PLATFORM_HEIGHT),
    pygame.Rect(100, HEIGHT - 260, 440, PLATFORM_HEIGHT),
    pygame.Rect(50, HEIGHT - 330, 540, PLATFORM_HEIGHT),
    pygame.Rect(50, HEIGHT - 400, 540, PLATFORM_HEIGHT)
]

# Player settings
MARIO_WIDTH, MARIO_HEIGHT = 20, 20
mario = pygame.Rect(50, HEIGHT - 70, MARIO_WIDTH, MARIO_HEIGHT)
MARIO_SPEED = 4
GRAVITY = 0.5
JUMP_HEIGHT = 10
mario_y_vel = 0
mario_on_ground = False

# Barrel settings
BARREL_SIZE = 20
barrels = []
BARREL_SPEED = 3
BARREL_DROP_SPEED = 5
BARREL_SPAWN_INTERVAL = 1500
last_barrel_spawn_time = pygame.time.get_ticks()

# Donkey Kong settings
DONKEY_KONG_WIDTH, DONKEY_KONG_HEIGHT = 60, 40
donkey_kong = pygame.Rect(50, HEIGHT - 360, DONKEY_KONG_WIDTH, DONKEY_KONG_HEIGHT)

# Ladder settings
ladders = [
    pygame.Rect(280, HEIGHT - 65, 20, 70),
    pygame.Rect(150, HEIGHT - 135, 20, 70),
    pygame.Rect(400, HEIGHT - 205, 20, 70),
    pygame.Rect(250, HEIGHT - 275, 20, 70),
    pygame.Rect(500, HEIGHT - 345, 20, 70)
]

# Score and lives
score = 0
lives = 3

# Define a function to generate beep sounds with varying frequencies
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * ((i // (sample_rate // frequency)) % 2)) for i in range(samples)]
    sound = pygame.mixer.Sound(buffer=array('h', wave))
    sound.set_volume(0.1)
    return sound

# Sound effects
jump_sound = generate_beep_sound(440, 0.1)  # A4
score_sound = generate_beep_sound(523.25, 0.1)  # C5
collision_sound = generate_beep_sound(587.33, 0.1)  # D5
game_over_sound = generate_beep_sound(659.25, 0.1)  # E5

# Draw everything
def draw():
    screen.fill(BLACK)
    for platform in platforms:
        pygame.draw.rect(screen, BROWN, platform)
    for ladder in ladders:
        pygame.draw.rect(screen, BLUE, ladder)
    pygame.draw.rect(screen, RED, mario)
    pygame.draw.rect(screen, YELLOW, donkey_kong)
    for barrel in barrels:
        pygame.draw.ellipse(screen, RED, barrel)
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (WIDTH - 110, 10))
    pygame.display.flip()

# Check if Mario is on a platform
def check_mario_on_platform():
    global mario_on_ground, mario_y_vel
    mario_on_ground = False
    for platform in platforms:
        if mario.colliderect(platform) and mario.bottom <= platform.top + 10:
            mario_on_ground = True
            mario_y_vel = 0
            mario.bottom = platform.top
            break

# Check if Mario is on a ladder
def check_mario_on_ladder():
    for ladder in ladders:
        if mario.colliderect(ladder):
            return True
    return False

# Move barrels down the platforms
def move_barrels():
    global lives
    for barrel in barrels:
        if barrel.colliderect(mario):
            collision_sound.play()
            lives -= 1
            barrels.clear()
            mario.topleft = (50, HEIGHT - 70)
            if lives == 0:
                game_over_sound.play()
                print("Game Over")
                pygame.quit()
                sys.exit()

        barrel.y += BARREL_DROP_SPEED

        for platform in platforms:
            if barrel.colliderect(platform) and barrel.bottom <= platform.top + 10:
                barrel.bottom = platform.top
                if platform.left == 50:
                    barrel_direction = 1
                else:
                    barrel_direction = -1
                break
        else:
            barrel_direction = 1

        barrel.x += BARREL_SPEED * barrel_direction

        if barrel.left < 0 or barrel.right > WIDTH:
            barrels.remove(barrel)

# Spawn barrels
def spawn_barrels():
    global last_barrel_spawn_time
    current_time = pygame.time.get_ticks()
    if current_time - last_barrel_spawn_time >= BARREL_SPAWN_INTERVAL:
        barrel = pygame.Rect(donkey_kong.left, donkey_kong.bottom, BARREL_SIZE, BARREL_SIZE)
        barrels.append(barrel)
        last_barrel_spawn_time = current_time

# Game loop
while True:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    # Move Mario
    if keys[pygame.K_LEFT]:
        mario.x -= MARIO_SPEED
    if keys[pygame.K_RIGHT]:
        mario.x += MARIO_SPEED
    if keys[pygame.K_SPACE] and mario_on_ground:
        jump_sound.play()
        mario_y_vel = -JUMP_HEIGHT

    # Apply gravity to Mario
    mario_y_vel += GRAVITY
    mario.y += mario_y_vel

    # Keep Mario within the screen boundaries
    if mario.left < 0:
        mario.left = 0
    if mario.right > WIDTH:
        mario.right = WIDTH

    # Check if Mario is on a platform or ladder
    check_mario_on_platform()
    if check_mario_on_ladder():
        mario_y_vel = 0
        if keys[pygame.K_UP]:
            mario.y -= MARIO_SPEED
        if keys[pygame.K_DOWN]:
            mario.y += MARIO_SPEED

    # Spawn and move barrels
    spawn_barrels()
    move_barrels()

    # Update score based on Mario's position
    if mario_on_ground:
        for platform in platforms:
            if mario.colliderect(platform):
                score_sound.play()
                score += 1
                break

    # Draw everything
    draw()
