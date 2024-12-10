import pygame

pygame.init()

# Screen
w, h = 800, 600
screen = pygame.display.set_mode((w, h))
pygame.display.set_caption("Pong")

# Colors
b, wt, o, lb = (0, 0, 0), (255, 255, 255), (235, 149, 52), (173, 216, 230)

# Game elements
pw, ph, ps = 15, 80, 5
p1x, p1y = 50, h // 2 - ph // 2
p2x, p2y = w - 50 - pw, h // 2 - ph // 2
bs, bx, by, bsx, bsy = 15, w // 2 - 7, h // 2 - 7, 4, 4
p1s, p2s = 0, 0
f = pygame.font.Font(None, 50)

# Game loop
c = pygame.time.Clock()
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    # Paddle movement
    k = pygame.key.get_pressed()
    p1y = max(0, min(p1y - ps if k[pygame.K_w] else p1y + ps if k[pygame.K_s] else p1y, h - ph))
    p2y = max(0, min(p2y - ps if k[pygame.K_UP] else p2y + ps if k[pygame.K_DOWN] else p2y, h - ph))

    # Ball movement
    bx += bsx
    by += bsy
    bsy = -bsy if by <= 0 or by >= h - bs else bsy
    if bx <= p1x + pw and p1y <= by <= p1y + ph or bx >= p2x - bs and p2y <= by <= p2y + ph:
        bsx = -bsx

    # Scoring
    if bx < 0:
        p2s += 1
        bx, by = w // 2 - 7, h // 2 - 7
    elif bx > w:
        p1s += 1
        bx, by = w // 2 - 7, h // 2 - 7

    # Drawing
    screen.fill(b)
    pygame.draw.rect(screen, o, (0, 0, w, h), 50)
    pygame.draw.rect(screen, lb, (0, 0, w, h), 25)
    for i in range(0, h, 40):
        pygame.draw.line(screen, wt, (w // 2, i), (w // 2, i + 20), 5)
    pygame.draw.rect(screen, wt, (p1x, p1y, pw, ph))
    pygame.draw.rect(screen, wt, (p2x, p2y, pw, ph))
    pygame.draw.rect(screen, wt, (bx, by, bs, bs))
    screen.blit(f.render(str(p1s), True, wt), (w // 4, 50))
    screen.blit(f.render(str(p2s), True, wt), (w * 3 // 4 - 25, 50))
    screen.blit(f.render("PONG", True, o), (w // 2 - 50, 30))
    screen.blit(f.render("PLAYER 1", True, wt), (85, h - 70))
    screen.blit(f.render("PLAYER 2", True, wt), (w - 210, h - 70))

    pygame.display.flip()
    c.tick(60)

pygame.quit()
