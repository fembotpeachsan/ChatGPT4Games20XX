import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Game clock
clock = pygame.time.Clock()

# Pixel size for the level grid
PIXEL_SIZE = 20

# Define Kirby's overworld stages and positions
overworld = {
    1: {"name": "Stage 1", "position": (100, 150)},
    2: {"name": "Stage 2", "position": (300, 150)},
    3: {"name": "Stage 3", "position": (500, 150)},
    4: {"name": "Whispy Woods", "position": (320, 350)},
}

# Kirby starting position in overworld
kirby_position = [100, 150]

# Function to display text on screen
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

# Function to create a basic grid-based level
def create_level(stage):
    if stage == 1:
        return [
            "####################",
            "#                  #",
            "#      #####        #",
            "#                  #",
            "#     ###########   #",
            "#                  #",
            "#   ###             #",
            "#                  #",
            "#     #########  D  #",  # Door to next stage (D)
            "#                  #",
            "####################"
        ]
    elif stage == 2:
        return [
            "####################",
            "#                  #",
            "#                  #",
            "#   #########      #",
            "#                  #",
            "#         ####     #",
            "#   ###        D   #",  # Door to next stage (D)
            "#                  #",
            "#     #########    #",
            "#                  #",
            "####################"
        ]
    elif stage == 3:
        return [
            "####################",
            "#                  #",
            "#  #######         #",
            "#                  #",
            "#         ######## #",
            "#    ####          #",
            "#                  #",
            "#  ###########     #",
            "#              D   #",  # Door to Whispy Woods (D)
            "####################"
        ]
    elif stage == 4:  # Whispy Woods level
        return [
            "####################",
            "#                  #",
            "#                  #",
            "#        W         #",  # Whispy Woods (W)
            "#                  #",
            "#                  #",
            "#                  #",
            "#                  #",
            "#                  #",
            "####################"
        ]

# Function to render the grid-based level
def draw_level(level):
    for y, row in enumerate(level):
        for x, char in enumerate(row):
            if char == '#':  # If it's a wall or obstacle
                pygame.draw.rect(screen, (255, 255, 255), (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
            elif char == 'W':  # Whispy Woods indicator
                pygame.draw.rect(screen, (0, 255, 0), (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
            elif char == 'D':  # Door (warp point)
                pygame.draw.rect(screen, (0, 0, 255), (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))

# Function to handle warps (doorways to other stages)
def check_warp(kirby_x, kirby_y, stage):
    level = create_level(stage)
    if level[kirby_y][kirby_x] == 'D':
        return True  # Warp detected, proceed to next stage
    return False

# Function to handle Whispy Woods boss fight
def whispy_woods_boss(kirby_x, kirby_y):
    font = pygame.font.Font(None, 36)
    playing_stage = True
    boss_hp = 5
    apples = []
    apple_timer = 0

    while playing_stage:
        screen.fill((0, 0, 0))  # Clear screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Handle Kirby movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and kirby_x > 1:
            kirby_x -= 1
        if keys[pygame.K_RIGHT] and kirby_x < 18:
            kirby_x += 1
        if keys[pygame.K_UP] and kirby_y > 1:
            kirby_y -= 1
        if keys[pygame.K_DOWN] and kirby_y < 9:
            kirby_y += 1

        # Draw Kirby as a pink square
        pygame.draw.rect(screen, (255, 105, 180), (kirby_x * PIXEL_SIZE, kirby_y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))

        # Draw Whispy Woods (as a green square)
        pygame.draw.rect(screen, (0, 255, 0), (9 * PIXEL_SIZE, 3 * PIXEL_SIZE, PIXEL_SIZE, 3 * PIXEL_SIZE))

        # Display boss HP
        draw_text(f"Whispy Woods HP: {boss_hp}", font, (255, 255, 255), screen, 100, 20)

        # Apple falling mechanic
        apple_timer += 1
        if apple_timer > 30:  # Drop an apple every half-second
            apples.append([random.randint(1, 18), 3])
            apple_timer = 0

        # Move apples down and check for collision with Kirby
        for apple in apples:
            pygame.draw.rect(screen, (255, 0, 0), (apple[0] * PIXEL_SIZE, apple[1] * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
            apple[1] += 1
            if apple[1] > 9:  # Remove apples that fall off-screen
                apples.remove(apple)
            if apple[0] == kirby_x and apple[1] == kirby_y:  # Kirby hit by apple
                draw_text("You got hit by an apple!", font, (255, 0, 0), screen, 100, 200)
                pygame.display.update()
                pygame.time.wait(1000)
                return False  # End boss fight if hit

        # Simulate damaging Whispy Woods (press Enter)
        if keys[pygame.K_RETURN]:
            boss_hp -= 1
            if boss_hp == 0:
                playing_stage = False  # Boss defeated

        pygame.display.update()
        clock.tick(30)

    return True  # Boss defeated

# Function to handle stage gameplay (dynamically generated pixel levels)
def stage_gameplay(stage):
    font = pygame.font.Font(None, 36)
    playing_stage = True

    # Create the dynamic level for the current stage
    level = create_level(stage)
    kirby_x, kirby_y = 1, 1  # Kirby's starting grid position (inside the level grid)

    while playing_stage:
        screen.fill((0, 0, 0))  # Clear screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Handle Kirby movement with collision detection
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and level[kirby_y][kirby_x - 1] != '#':
            kirby_x -= 1
        if keys[pygame.K_RIGHT] and level[kirby_y][kirby_x + 1] != '#':
            kirby_x += 1
        if keys[pygame.K_UP] and level[kirby_y - 1][kirby_x] != '#':
            kirby_y -= 1
        if keys[pygame.K_DOWN] and level[kirby_y + 1][kirby_x] != '#':
            kirby_y += 1

        # Draw the level
        draw_level(level)

        # Draw Kirby as a pink square
        pygame.draw.rect(screen, (255, 105, 180), (kirby_x * PIXEL_SIZE, kirby_y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))

        # Check if Kirby has reached a warp point (door)
        if check_warp(kirby_x, kirby_y, stage):
            playing_stage = False  # Move to the next stage

        # Display stage info
        draw_text(f"Playing {overworld[stage]['name']}", font, (255, 255, 255), screen, 100, 200)

        # If it's the boss stage (Whispy Woods), handle the boss fight
        if stage == 4:
            if not whispy_woods_boss(kirby_x, kirby_y):
                draw_text("You Lost to Whispy Woods!", font, (255, 0, 0), screen, 100, 200)
                pygame.display.update()
                pygame.time.wait(2000)
                return  # End the game or restart the overworld
            else:
                draw_text("Whispy Woods Defeated!", font, (0, 255, 0), screen, 100, 200)
                pygame.display.update()
                pygame.time.wait(2000)
                playing_stage = False  # Boss defeated

        pygame.display.update()
        clock.tick(30)

# Main game loop
def main():
    font = pygame.font.Font(None, 36)
    stage = 1  # Start from Stage 1
    running = True
    in_stage = False

    while running:
        screen.fill((0, 0, 0))  # Clear screen

        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Handle movement input in the overworld
        if not in_stage:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                kirby_position[0] -= 5
            if keys[pygame.K_RIGHT]:
                kirby_position[0] += 5
            if keys[pygame.K_UP]:
                kirby_position[1] -= 5
            if keys[pygame.K_DOWN]:
                kirby_position[1] += 5

            # Check if Kirby reaches a stage point
            for stage_num, stage_info in overworld.items():
                stage_pos = stage_info["position"]
                if abs(kirby_position[0] - stage_pos[0]) < 30 and abs(kirby_position[1] - stage_pos[1]) < 30:
                    stage = stage_num

            # Draw the overworld map (text-based)
            draw_text("Kirby's Adventure - Overworld", font, (255, 255, 255), screen, 200, 50)
            for stage_num, stage_info in overworld.items():
                draw_text(f"{stage_info['name']}", font, (255, 255, 255), screen, *stage_info["position"])

            # Display Kirby's position
            draw_text("Kirby", font, (255, 255, 255), screen, kirby_position[0], kirby_position[1])

            # If Kirby reaches a stage
            if stage:
                draw_text(f"Press Enter to Enter {overworld[stage]['name']}", font, (0, 255, 0), screen, 150, 400)
                if pygame.key.get_pressed()[pygame.K_RETURN]:
                    in_stage = True  # Enter the stage

        else:
            # Stage gameplay with dynamic levels
            stage_gameplay(stage)
            in_stage = False  # Return to overworld when stage ends
            if stage < 4:
                stage += 1  # Automatically move to the next stage after a warp

        pygame.display.update()
        clock.tick(30)  # Cap the frame rate at 30 FPS

if __name__ == "__main__":
    main()
