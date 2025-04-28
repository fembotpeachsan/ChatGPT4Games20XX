import asyncio
import platform
import pygame
import sys

# Constants
WIDTH, HEIGHT = 600, 400
FPS = 60

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

def setup():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SMB3 Inspired Pygame Program")
    return screen, pygame.time.Clock()

def update_loop(screen, clock, rect_x, rect_y, rect_width, rect_height, speed):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if platform.system() != "Emscripten":
                pygame.quit()
                sys.exit()
            return False, rect_x

    rect_x += speed
    if rect_x > WIDTH:
        rect_x = -rect_width

    screen.fill(BLACK)
    pygame.draw.rect(screen, BLUE, (rect_x, rect_y, rect_width, rect_height))
    pygame.display.flip()
    clock.tick(FPS)
    return True, rect_x

async def main():
    screen, clock = setup()
    rect_x, rect_y = 50, HEIGHT - 50
    rect_width, rect_height = 40, 40
    speed = 5
    running = True

    while running:
        running, rect_x = update_loop(screen, clock, rect_x, rect_y, rect_width, rect_height, speed)
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
