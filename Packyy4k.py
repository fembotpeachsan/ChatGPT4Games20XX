import pygame
import random
import tkinter as tk

# --- Constants ---

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
TILE_SIZE = 20  # Size of each grid square

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)


# --- Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE
        self.speed = TILE_SIZE
        self.direction = (0, 0) # (x_change, y_change)  e.g., (1, 0) is right

    def update(self, walls):
        # Store old position for collision handling
        old_x = self.rect.x
        old_y = self.rect.y

        # Move based on direction
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        
        if self.rect.left < 0:
            self.rect.right = SCREEN_WIDTH
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.left = 0

        # Check for collisions with walls
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                # Undo movement if collision
                self.rect.x = old_x
                self.rect.y = old_y
                break  # Stop checking after first collision



class Ghost(pygame.sprite.Sprite):
     def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE
        self.speed = TILE_SIZE
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)]) # Start with random dir

     def update(self, walls):
        # Store old position for collision handling
        old_x = self.rect.x
        old_y = self.rect.y

        # Move based on direction
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

        if self.rect.left < 0:
            self.rect.right = SCREEN_WIDTH
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.left = 0

        # Check for collisions with walls
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                # Undo movement and choose a new random direction
                self.rect.x = old_x
                self.rect.y = old_y
                self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                break


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class Dot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE // 4, TILE_SIZE // 4])  # Smaller dots
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)  # Center dot in tile


# --- Game Setup ---

def create_level(level_data):
    """Creates the game level based on a string representation."""
    walls = pygame.sprite.Group()
    dots = pygame.sprite.Group()
    player = None
    ghosts = pygame.sprite.Group()

    for row_index, row in enumerate(level_data.splitlines()):
        for col_index, cell in enumerate(row):
            if cell == "#":
                walls.add(Wall(col_index, row_index))
            elif cell == ".":
                dots.add(Dot(col_index, row_index))
            elif cell == "P":
                player = Player(col_index, row_index)
            elif cell == "R":
                ghosts.add(Ghost(col_index, row_index, RED))
            elif cell == "P":
                ghosts.add(Ghost(col_index, row_index, PINK))
            elif cell == "B":
                ghosts.add(Ghost(col_index, row_index, BLUE))
            elif cell == "O":
                ghosts.add(Ghost(col_index, row_index, ORANGE))


    return player, walls, dots, ghosts



def main():
    # --- Tkinter Window (minimal) ---
    root = tk.Tk()
    root.title("Pac-Man Starter")
    root.geometry("200x100")  # Small window, just for launch

    def start_game():
        root.destroy()  # Close Tkinter window
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man")
        clock = pygame.time.Clock()

        # Level data (VERY simplified - a proper level would be much larger)
        level_data = """
        ##############################
        #............##............#
        #.####.#####.##.#####.####.#
        #P####.#####.##.#####.####B#
        #.####.#####.##.#####.####.#
        #..........................#
        #.####.##.########.##.####.#
        #.####.##.########.##.####.#
        #......##....##....##......#
        ######.##### ## #####.######
        ######.####R    P####.######
        ######.##..........##.######
        ######.##.########.##.######
        #............##............#
        #.####.#####.##.#####.####.#
        #O####.......  .......####C#
        #.####.##.########.##.####.#
        #...........##............#
        ##############################
        """

        player, walls, dots, ghosts = create_level(level_data)
        all_sprites = pygame.sprite.Group()
        all_sprites.add(player, walls, dots, ghosts)

        score = 0
        font = pygame.font.Font(None, 36)  # Default system font

        running = True
        game_over = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if not game_over:
                         if event.key == pygame.K_LEFT:
                            player.direction = (-1, 0)
                         elif event.key == pygame.K_RIGHT:
                            player.direction = (1, 0)
                         elif event.key == pygame.K_UP:
                            player.direction = (0, -1)
                         elif event.key == pygame.K_DOWN:
                            player.direction = (0, 1)
                    elif event.key == pygame.K_r: # Restart
                       
                        player, walls, dots, ghosts = create_level(level_data)
                        all_sprites = pygame.sprite.Group()
                        all_sprites.add(player, walls, dots, ghosts)
                        score = 0
                        game_over = False
                    elif event.key == pygame.K_q:
                       running = False

                        

            if not game_over:

                player.update(walls)
                ghosts.update(walls)
            

                # Dot collision
                dots_collected = pygame.sprite.spritecollide(player, dots, True) # The 'True' removes the dot
                score += len(dots_collected) * 10 #example

                # Ghost collision check
                if pygame.sprite.spritecollideany(player, ghosts):
                   game_over = True


                # Win condition - no more dots
                if not dots:
                    game_over = True # You'd usually move to next level
                

            screen.fill(BLACK)

            # --- Drawing ---
            all_sprites.draw(screen)


            # Score display
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))

            if game_over:
                if not dots:
                    game_over_text = font.render("You Win!  Press R to restart or Q to quit", True, WHITE)
                else:
                    game_over_text = font.render("Game Over! Press R to restart or Q to quit", True, WHITE)

                text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(game_over_text, text_rect)


            pygame.display.flip()
            clock.tick(10) # Much slower for developing

        pygame.quit()

    start_button = tk.Button(root, text="Start Game", command=start_game)
    start_button.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
