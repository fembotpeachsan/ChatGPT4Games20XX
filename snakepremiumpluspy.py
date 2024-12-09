import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Define Colors
WHITE = (255, 255, 255)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (50, 153, 213)

# Set up display
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
CELL_SIZE = 20

# Calculate number of cells in grid
GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Snake Game')

clock = pygame.time.Clock()

font_style = pygame.font.SysFont(None, 35)
score_font = pygame.font.SysFont(None, 35)

def your_score(score):
    value = score_font.render("Your Score: " + str(score), True, BLACK)
    screen.blit(value, [0, 0])

def our_snake(cell_size, snake_list):
    for x in snake_list:
        pygame.draw.rect(screen, GREEN, [x[0], x[1], cell_size, cell_size])

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [WINDOW_WIDTH / 6, WINDOW_HEIGHT / 3])

def gameLoop():
    game_over = False
    game_close = False

    x1 = WINDOW_WIDTH / 2
    y1 = WINDOW_HEIGHT / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    # Place food randomly
    foodx = round(random.randrange(0, WINDOW_WIDTH - CELL_SIZE) / CELL_SIZE) * CELL_SIZE
    foody = round(random.randrange(0, WINDOW_HEIGHT - CELL_SIZE) / CELL_SIZE) * CELL_SIZE

    while not game_over:

        while game_close:
            screen.fill(BLUE)
            message("You Lost! Press Q-Quit or C-Play Again", RED)
            your_score(Length_of_snake -1 )
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if x1_change == CELL_SIZE:
                        pass  # prevent reversing
                    else:
                        x1_change = -CELL_SIZE
                        y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    if x1_change == -CELL_SIZE:
                        pass
                    else:
                        x1_change = CELL_SIZE
                        y1_change = 0
                elif event.key == pygame.K_UP:
                    if y1_change == CELL_SIZE:
                        pass
                    else:
                        y1_change = -CELL_SIZE
                        x1_change = 0
                elif event.key == pygame.K_DOWN:
                    if y1_change == -CELL_SIZE:
                        pass
                    else:
                        y1_change = CELL_SIZE
                        x1_change = 0

        # Check boundaries
        if x1 >= WINDOW_WIDTH or x1 < 0 or y1 >= WINDOW_HEIGHT or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change

        screen.fill(BLUE)
        pygame.draw.rect(screen, RED, [foodx, foody, CELL_SIZE, CELL_SIZE])

        snake_Head = [x1, y1]
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        # Check for collision with self
        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(CELL_SIZE, snake_List)
        your_score(Length_of_snake -1 )

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, WINDOW_WIDTH - CELL_SIZE) / CELL_SIZE) * CELL_SIZE
            foody = round(random.randrange(0, WINDOW_HEIGHT - CELL_SIZE) / CELL_SIZE) * CELL_SIZE
            Length_of_snake += 1

        clock.tick(10)  # Control the speed (frames per second)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    gameLoop()
