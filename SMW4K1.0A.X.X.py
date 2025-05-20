
import pygame

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SMW-style Pygame Demo")

# Colors reminiscent of SMW
SKY = (114, 198, 206)
GROUND = (94, 73, 46)
MARIO = (255, 0, 0)
PIPE = (0, 160, 33)
PLATFORM = (221, 187, 153)

mario = pygame.Rect(50, HEIGHT - 90, 20, 28)
velocity = [0, 0]
jump_strength = -10
gravity = 0.5

level_data = [
    {
        "pipes": [pygame.Rect(400, HEIGHT - 80, 40, 40)],
        "platforms": [pygame.Rect(200, HEIGHT - 140, 60, 20)],
        "goal": pygame.Rect(760, HEIGHT - 80, 30, 40),
    }
]
current_level = 0
on_ground = False

font = pygame.font.SysFont("Helvetica", 20)
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        velocity[0] = -3
    elif keys[pygame.K_RIGHT]:
        velocity[0] = 3
    else:
        velocity[0] = 0
    if keys[pygame.K_SPACE] and on_ground:
        velocity[1] = jump_strength

    velocity[1] += gravity
    mario.x += velocity[0]
    mario.y += velocity[1]

    if mario.bottom >= HEIGHT - 40:
        mario.bottom = HEIGHT - 40
        velocity[1] = 0
        on_ground = True
    else:
        on_ground = False

    level = level_data[current_level]
    for platform in level["platforms"]:
        if mario.colliderect(platform) and velocity[1] >= 0:
            mario.bottom = platform.top
            velocity[1] = 0
            on_ground = True

    for pipe in level["pipes"]:
        if mario.colliderect(pipe):
            if velocity[0] > 0:
                mario.right = pipe.left
            elif velocity[0] < 0:
                mario.left = pipe.right

    if level["goal"] and mario.colliderect(level["goal"]):
        running = False

    screen.fill(SKY)
    pygame.draw.rect(screen, GROUND, (0, HEIGHT - 40, WIDTH, 40))
    for platform in level["platforms"]:
        pygame.draw.rect(screen, PLATFORM, platform)
    for pipe in level["pipes"]:
        pygame.draw.rect(screen, PIPE, pipe)
    pygame.draw.rect(screen, MARIO, mario)
    if level["goal"]:
        pygame.draw.rect(screen, (255, 255, 0), level["goal"])

    msg = font.render("SMW DEMO - reach the goal!", True, (255, 255, 255))
    screen.blit(msg, (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
