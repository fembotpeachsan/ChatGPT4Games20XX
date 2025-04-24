import pygame
import sys
from nes_py.wrappers import JoypadSpace
import gym
import gym_super_mario_bros
from gym_super_mario_bros.actions import SIMPLE_MOVEMENT

# Initialize Pygame
pygame.init()

# Screen settings (adjusted to NES resolution)
SCREEN_WIDTH = 256  # NES native width
SCREEN_HEIGHT = 240  # NES native height
FPS = 60

# Setup Pygame screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros. 1 - Pygame Emulation")
clock = pygame.time.Clock()

# Create the game environment
# Replace 'smb1.nes' with the actual path to your SMB1 ROM if different
env = gym.make('SuperMarioBros-v0')  # gym_super_mario_bros provides SMB1
env = JoypadSpace(env, SIMPLE_MOVEMENT)  # Use simple movement controls

# Reset the environment to start the game
state = env.reset()

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get keyboard input and map to NES controls
    keys = pygame.key.get_pressed()
    action = 0  # Default: no action
    if keys[pygame.K_RIGHT]:
        action = 1  # Move right
    if keys[pygame.K_LEFT]:
        action = 2  # Move left
    if keys[pygame.K_UP]:
        action = 5  # Jump
    if keys[pygame.K_RIGHT] and keys[pygame.K_a]:
        action = 3  # Run right
    if keys[pygame.K_LEFT] and keys[pygame.K_a]:
        action = 4  # Run left

    # Step the environment with the chosen action
    state, reward, done, info = env.step(action)

    # Render the frame to a Pygame surface
    # nes-py renders the frame as a numpy array; convert it to a Pygame surface
    frame = pygame.surfarray.make_surface(state.swapaxes(0, 1))
    screen.blit(frame, (0, 0))

    # Update the display
    pygame.display.flip()
    clock.tick(FPS)

    # Reset the game if Mario dies or completes the level
    if done:
        state = env.reset()

# Cleanup
env.close()
pygame.quit()
sys.exit()
