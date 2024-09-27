import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 144
SCALE = 3
WHITE = (255, 255, 255)
LIGHT_GREEN = (112, 208, 112)
DARK_GREEN = (56, 96, 56)
PLAYER_COLOR = (0, 255, 255)
ENEMY_COLOR = (255, 0, 0)
SKULL_COLOR = (200, 200, 200)
PLAYER_SIZE = 10
ENEMY_SIZE = 20
SKULL_SIZE = 5
TP_MAX = 100
HP_MAX = 100

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH * SCALE, SCREEN_HEIGHT * SCALE))
pygame.display.set_caption("DELTATRAVELLER COMBAT SYSTEM")
clock = pygame.time.Clock()

# Game variables
party = {
    "FLAMES": {"pos": [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30], "hp": HP_MAX, "tp": 0, "color": (255, 255, 0), "action": None},
    "GUNBLAZER42": {"pos": [SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 30], "hp": HP_MAX, "tp": 0, "color": (0, 255, 0), "action": None},
    "Mochi": {"pos": [SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 30], "hp": HP_MAX, "tp": 0, "color": (255, 182, 193), "action": None}
}
enemy_pos = [SCREEN_WIDTH // 2, 20]
enemy_health = 15
skulls = []
turn = "enemy"  # Start with enemy turn
current_turn = "FLAMES"  # Start with FLAMES's turn
enemy_attack_time = 0
action_menu = ["Attack", "Defend", "Special"]
selected_action = 0

# Main game loop
def game_loop():
    global enemy_health, turn, enemy_attack_time, skulls, current_turn, selected_action

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Clear the screen
        screen.fill(DARK_GREEN)

        # Check if the game is over
        if all(party_member["hp"] <= 0 for party_member in party.values()):
            print("Party Defeated!")
            running = False

        if enemy_health <= 0:
            print("Enemy Defeated!")
            running = False

        # Handle player movement and input (during enemy's turn, they can dodge)
        keys = pygame.key.get_pressed()
        if turn == "enemy":
            for party_member in party.values():
                if keys[pygame.K_LEFT]:
                    party_member["pos"][0] -= 2
                if keys[pygame.K_RIGHT]:
                    party_member["pos"][0] += 2
                if keys[pygame.K_UP]:
                    party_member["pos"][1] -= 2
                if keys[pygame.K_DOWN]:
                    party_member["pos"][1] += 2

            # Limit player movement to screen bounds
            for party_member in party.values():
                party_member["pos"][0] = max(0, min(party_member["pos"][0], SCREEN_WIDTH - PLAYER_SIZE))
                party_member["pos"][1] = max(0, min(party_member["pos"][1], SCREEN_HEIGHT - PLAYER_SIZE))

        # Draw the party members and enemy
        for name, party_member in party.items():
            pygame.draw.rect(screen, party_member["color"], (party_member["pos"][0] * SCALE, party_member["pos"][1] * SCALE, PLAYER_SIZE * SCALE, PLAYER_SIZE * SCALE))

        pygame.draw.rect(screen, ENEMY_COLOR, (enemy_pos[0] * SCALE, enemy_pos[1] * SCALE, ENEMY_SIZE * SCALE, ENEMY_SIZE * SCALE))

        # Turn-based system
        if turn == "enemy":
            # Enemy shoots projectiles (skulls)
            if pygame.time.get_ticks() - enemy_attack_time > 1000:
                enemy_attack_time = pygame.time.get_ticks()
                skulls.append([random.randint(0, SCREEN_WIDTH - SKULL_SIZE), 0])

            # Move skulls downwards and check for collision with the party
            for skull in skulls:
                skull[1] += 2  # Skulls move downwards
                if skull[1] > SCREEN_HEIGHT:
                    skulls.remove(skull)
                pygame.draw.rect(screen, SKULL_COLOR, (skull[0] * SCALE, skull[1] * SCALE, SKULL_SIZE * SCALE, SKULL_SIZE * SCALE))

                # Collision detection with all party members
                for party_member in party.values():
                    if abs(skull[0] - party_member["pos"][0]) < PLAYER_SIZE and abs(skull[1] - party_member["pos"][1]) < PLAYER_SIZE:
                        party_member["hp"] -= 5  # Party member takes damage on collision
                        skulls.remove(skull)

            # Check if enemy attack phase is over
            if len(skulls) == 0 and pygame.time.get_ticks() - enemy_attack_time > 2000:
                turn = current_turn  # Switch to the current party member's turn

        elif turn != "enemy":
            # Display action menu
            draw_action_menu(screen, current_turn, selected_action)

            # Navigate action menu
            if keys[pygame.K_UP]:
                selected_action = max(0, selected_action - 1)
            if keys[pygame.K_DOWN]:
                selected_action = min(len(action_menu) - 1, selected_action + 1)

            # Select an action
            if keys[pygame.K_RETURN]:
                perform_action(current_turn, action_menu[selected_action])
                next_turn()

        # Display HP and TP for the party members and enemy HP
        draw_hp_tp(screen)

        # Update the display
        pygame.display.flip()
        clock.tick(60)

# Function to perform actions for each party member
def perform_action(member, action):
    global enemy_health
    if action == "Attack":
        print(f"{member} attacks!")
        enemy_health -= 3
        party[member]["tp"] += 10  # Gain TP for attacking
    elif action == "Defend":
        print(f"{member} defends!")
        # Add defend logic here (e.g., reduce damage next turn)
    elif action == "Special":
        print(f"{member} uses a special move!")
        # Add special move logic here

# Function to draw HP/TP bars and action menu
def draw_hp_tp(screen):
    font = pygame.font.SysFont(None, 24)

    # Display party HP/TP
    for i, (name, party_member) in enumerate(party.items()):
        hp_text = font.render(f"{name} HP: {party_member['hp']}/{HP_MAX}", True, WHITE)
        tp_text = font.render(f"{name} TP: {party_member['tp']}/{TP_MAX}", True, WHITE)
        screen.blit(hp_text, (10, SCREEN_HEIGHT * SCALE - 30 - i * 30))
        screen.blit(tp_text, (10, SCREEN_HEIGHT * SCALE - 60 - i * 30))

    # Display enemy HP
    enemy_hp_text = font.render(f"Enemy HP: {enemy_health}", True, WHITE)
    screen.blit(enemy_hp_text, (SCREEN_WIDTH * SCALE - 150, 10))

# Function to draw action menu
def draw_action_menu(screen, member, selected_action):
    font = pygame.font.SysFont(None, 24)
    menu_text = font.render(f"{member}'s Turn", True, WHITE)
    screen.blit(menu_text, (10, 10))

    for i, action in enumerate(action_menu):
        color = LIGHT_GREEN if i == selected_action else WHITE
        action_text = font.render(action, True, color)
        screen.blit(action_text, (10, 40 + i * 30))

# Switch turns between party members and the enemy
def next_turn():
    global turn, current_turn

    party_members = list(party.keys())
    current_index = party_members.index(current_turn)

    # Move to the next party member or enemy
    if current_index + 1 < len(party_members):
        current_turn = party_members[current_index + 1]
        turn = current_turn
    else:
        current_turn = party_members[0]  # Loop back to the first party member
        turn = "enemy"  # Switch to enemy turn

# Start the game loop
game_loop()
