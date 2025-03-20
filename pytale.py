import pygame
import sys
import random

# Setup
pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Undertale Battle System")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 128, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Fonts
font = pygame.font.SysFont('Arial', 18)
small_font = pygame.font.SysFont('Arial', 16)

# Battle box
battle_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 100)

# Player (soul) setup
player = pygame.Rect(WIDTH // 2 - 10, HEIGHT // 2, 20, 20)
player_speed = 4
player_color = (255, 0, 0)
player_hp = 20
max_hp = 20

# Enemy setup
enemy_pos = [WIDTH // 2, 120]
enemy_hp = 50
enemy_max_hp = 50

# Projectiles
projectiles = []
proj_timer = 0
battle_timer = 0  # Added timer for battle phase

# Game state
game_state = "MENU"
selected_option = 0
options = ['FIGHT', 'ACT', 'ITEM', 'MERCY']
fight_target = None

def draw_battle_ui():
    pygame.draw.rect(screen, WHITE, battle_box, 2)
    grid_rect = pygame.Rect(20, 20, WIDTH - 40, 180)
    pygame.draw.rect(screen, GREEN, grid_rect, 1)
    
    for x in range(1, 4):
        pygame.draw.line(screen, GREEN, (20 + x * (grid_rect.width // 3), 20), 
                        (20 + x * (grid_rect.width // 3), 20 + grid_rect.height))
    for y in range(1, 2):
        pygame.draw.line(screen, GREEN, (20, 20 + y * (grid_rect.height // 2)), 
                        (20 + grid_rect.width, 20 + y * (grid_rect.height // 2)))
    
    option_width = 110
    start_x = (WIDTH - (option_width * 4 + 30)) // 2
    symbols = ['⚔', '»', '♪', '×']
    
    for i, (text, symbol) in enumerate(zip(options, symbols)):
        rect = pygame.Rect(start_x + i * (option_width + 10), HEIGHT - 60, option_width, 40)
        color = YELLOW if i == selected_option else ORANGE
        pygame.draw.rect(screen, color, rect, 2)
        symbol_text = font.render(symbol, True, color)
        option_text = font.render(text, True, color)
        screen.blit(symbol_text, (rect.x + 10, rect.y + 10))
        screen.blit(option_text, (rect.x + 30, rect.y + 10))
    
    hp_text = small_font.render(f'LV 1    HP', True, WHITE)
    screen.blit(hp_text, (WIDTH // 2 - 70, HEIGHT - 90))
    hp_bar_width = int(30 * (player_hp / max_hp))
    pygame.draw.rect(screen, YELLOW, (WIDTH // 2 - 10, HEIGHT - 90, hp_bar_width, 18))
    hp_value = small_font.render(f'{player_hp} / {max_hp}', True, WHITE)
    screen.blit(hp_value, (WIDTH // 2 + 30, HEIGHT - 90))

def draw_enemy():
    x, y = enemy_pos[0], enemy_pos[1]
    # Head
    pygame.draw.rect(screen, WHITE, (x - 15, y - 20, 30, 20))
    # Eyes
    pygame.draw.rect(screen, BLACK, (x - 10, y - 15, 5, 5))
    pygame.draw.rect(screen, BLACK, (x + 5, y - 15, 5, 5))
    # Mouth
    pygame.draw.line(screen, BLACK, (x - 5, y - 5), (x + 5, y - 5), 2)  # Fixed line drawing
    # Body
    pygame.draw.rect(screen, WHITE, (x - 15, y, 30, 30))
    # Shoulders
    pygame.draw.polygon(screen, WHITE, [(x - 25, y), (x - 15, y - 10), (x - 5, y)])
    pygame.draw.polygon(screen, WHITE, [(x + 5, y), (x + 15, y - 10), (x + 25, y)])
    # Arms
    pygame.draw.line(screen, WHITE, (x - 15, y + 10), (x - 30, y + 40), 4)
    pygame.draw.line(screen, WHITE, (x + 15, y + 10), (x + 30, y + 40), 4)
    # Hands
    pygame.draw.line(screen, WHITE, (x - 30, y + 40), (x - 50, y + 60), 6)
    pygame.draw.circle(screen, WHITE, (x - 50, y + 60), 5)
    # Legs
    pygame.draw.rect(screen, WHITE, (x - 15, y + 30, 10, 20))
    pygame.draw.rect(screen, WHITE, (x + 5, y + 30, 10, 20))
    # Feet
    pygame.draw.rect(screen, WHITE, (x - 15, y + 50, 15, 10))
    pygame.draw.rect(screen, WHITE, (x + 5, y + 50, 15, 10))
    # Torso
    pygame.draw.polygon(screen, WHITE, [(x - 15, y), (x + 15, y), (x + 30, y + 40), (x - 30, y + 40)])
    # Scarf
    pygame.draw.rect(screen, ORANGE, (x - 15, y - 10, 30, 5))
    pygame.draw.line(screen, ORANGE, (x + 15, y - 5), (x + 25, y + 10), 3)  # Fixed line drawing
    # Belt
    pygame.draw.polygon(screen, WHITE, [(x - 15, y + 30), (x, y + 40), (x + 15, y + 30)])
    # HP display
    name_text = small_font.render(f"Royal Guard Papyrus  HP: {enemy_hp}/{enemy_max_hp}", True, WHITE)
    screen.blit(name_text, (WIDTH // 2 - 80, 30))

def update_player():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.left > battle_box.left + 5:
        player.x -= player_speed
    if keys[pygame.K_RIGHT] and player.right < battle_box.right - 5:
        player.x += player_speed
    if keys[pygame.K_UP] and player.top > battle_box.top + 5:
        player.y -= player_speed
    if keys[pygame.K_DOWN] and player.bottom < battle_box.bottom - 5:
        player.y += player_speed

def update_projectiles():
    global proj_timer, projectiles, player_hp, game_state
    proj_timer += 1
    if proj_timer > 30:
        proj_timer = 0
        new_proj = pygame.Rect(enemy_pos[0] - 4, enemy_pos[1] + 40, 8, 8)
        projectiles.append(new_proj)
    
    for proj in projectiles[:]:
        proj.y += 3
        if proj.colliderect(player):
            player_hp = max(0, player_hp - 1)
            projectiles.remove(proj)
            if player_hp <= 0:
                game_state = "GAME_OVER"
        elif proj.top > battle_box.bottom:
            projectiles.remove(proj)

def draw_fight_target():
    global fight_target
    if fight_target is None:
        fight_target = {"x": battle_box.left + 50, "speed": 3, "dir": 1}
    bar = pygame.Rect(battle_box.left, battle_box.top, battle_box.width, 20)
    pygame.draw.rect(screen, WHITE, bar, 2)
    target = pygame.Rect(fight_target["x"], bar.y + 2, 10, 16)
    pygame.draw.rect(screen, ORANGE, target)
    fight_target["x"] += fight_target["speed"] * fight_target["dir"]
    if fight_target["x"] <= bar.left or fight_target["x"] + 10 >= bar.right:
        fight_target["dir"] *= -1

def main():
    global game_state, selected_option, fight_target, enemy_hp, battle_timer
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state == "MENU":
                    if event.key == pygame.K_LEFT and selected_option > 0:
                        selected_option -= 1
                    elif event.key == pygame.K_RIGHT and selected_option < 3:
                        selected_option += 1
                    elif event.key == pygame.K_z:
                        if options[selected_option] == "FIGHT":
                            game_state = "FIGHT"
                            fight_target = None
                        elif options[selected_option] == "MERCY":
                            enemy_hp = 0
                            game_state = "WIN"  # Changed to WIN state for MERCY
                        else:
                            game_state = "BATTLE"
                            battle_timer = 0  # Reset battle timer
                elif game_state == "FIGHT" and event.key == pygame.K_z:
                    if fight_target is not None:  # Ensure fight_target exists
                        # Calculate damage based on how close to center the target is
                        center_x = battle_box.left + battle_box.width // 2
                        accuracy = 1.0 - min(1.0, abs(fight_target["x"] - center_x) / (battle_box.width / 2))
                        damage = max(1, int(20 * accuracy))
                        
                        enemy_hp = max(0, enemy_hp - damage)
                        
                        # Display damage text (optional)
                        damage_text = font.render(f"-{damage}", True, YELLOW)
                        screen.blit(damage_text, (enemy_pos[0], enemy_pos[1] - 30))
                        pygame.display.flip()
                        pygame.time.delay(300)  # Brief pause to show damage
                        
                        game_state = "BATTLE"
                        battle_timer = 0  # Reset battle timer
                        
                        if enemy_hp <= 0:
                            game_state = "WIN"

        # Update game logic based on game state
        if game_state == "BATTLE":
            update_player()
            update_projectiles()
            battle_timer += 1
            
            # After a set time, return to menu
            if battle_timer > 180:  # 3 seconds at 60 FPS
                game_state = "MENU"
                projectiles.clear()  # Clear any remaining projectiles
        
        # Check if enemy is defeated
        if enemy_hp <= 0 and game_state != "WIN" and game_state != "GAME_OVER":
            game_state = "WIN"
            
        # Draw everything
        screen.fill(BLACK)
        draw_battle_ui()
        
        # Only draw enemy if they're alive
        if enemy_hp > 0:
            draw_enemy()
        
        # Game state specific drawing
        if game_state == "BATTLE":
            for proj in projectiles:
                pygame.draw.rect(screen, WHITE, proj)
            pygame.draw.rect(screen, player_color, player)
        elif game_state == "FIGHT":
            draw_fight_target()
        elif game_state == "WIN":
            win_text = font.render("YOU WON!", True, GREEN)
            screen.blit(win_text, (WIDTH // 2 - 40, HEIGHT // 2 - 10))
            pygame.display.flip()
            pygame.time.delay(2000)  # 2 second delay
            running = False
        elif game_state == "GAME_OVER":
            game_over_text = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(game_over_text, (WIDTH // 2 - 50, HEIGHT // 2 - 10))
            pygame.display.flip()
            pygame.time.delay(2000)  # 2 second delay
            running = False
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
