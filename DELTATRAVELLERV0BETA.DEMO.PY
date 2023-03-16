import pygame
import sys
import random

pygame.init()

# Game Constants
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 144
SCALE = 3
WHITE = (255, 255, 255)
LIGHT_GREEN = (112, 208, 112)
DARK_GREEN = (56, 96, 56)
PLAYER_SIZE = 5
ENEMY_SIZE = 10
SKULL_SIZE = 8
ENEMY_HITS = 3
TP_MAX = 100
HP_MAX = 100

screen = pygame.display.set_mode((SCREEN_WIDTH * SCALE, SCREEN_HEIGHT * SCALE))
pygame.display.set_caption("DELTARUNE VS SPAMTON GBA")
clock = pygame.time.Clock()

# Game variables
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
skulls = []
enemy = [random.randint(20, SCREEN_WIDTH - 20), random.randint(20, SCREEN_HEIGHT - 20)]
enemy_health =  15
