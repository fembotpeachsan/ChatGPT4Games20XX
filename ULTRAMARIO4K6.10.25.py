import pygame
import math
import random

# Initialize Pygame
pygame.init()

# --- CONSTANTS ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- COLORS ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
DARK_GREEN = (0, 100, 0)

# --- GAME SETTINGS ---
GRAVITY = 0.7
PLAYER_ACC = 0.8
PLAYER_FRICTION = -0.12
JUMP_STRENGTH = -15
ENEMY_SPEED = 1.5
LEVEL_WIDTH = 3200

# --- FONT ---
font = pygame.font.Font(None, 36)
menu_font = pygame.font.Font(None, 72)

# --- PLAYER ---
class Player:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.width = 32
        self.height = 44  # Small Mario height
        self.on_ground = False
        self.facing_right = True
        self.lives = 3
        self.coins = 0
        self.invulnerable_timer = 0
        self.animation_frame = 0
        self.state = 'small' # 'small', 'super', 'fire'
        self.is_dead = False
        
    def set_state(self, new_state):
        if self.state == 'small' and (new_state == 'super' or new_state == 'fire'):
            self.pos.y -= 22 # Grow upwards
            self.height = 66
        elif (self.state == 'super' or self.state == 'fire') and new_state == 'small':
             self.height = 44
        self.state = new_state
        self.invulnerable_timer = 60 # Brief invincibility after state change

    def jump(self):
        if self.on_ground:
            self.vel.y = JUMP_STRENGTH

    def take_damage(self):
        if self.invulnerable_timer > 0:
            return

        if self.state != 'small':
            self.set_state('small')
            self.invulnerable_timer = 120 # Longer invincibility after getting hit
        else:
            self.lives -= 1
            self.is_dead = True
            self.vel.y = -20 # Death bounce
            self.invulnerable_timer = 9999 # Invulnerable while dead
            
    def shoot(self, fireballs):
        if self.state == 'fire':
            direction = 1 if self.facing_right else -1
            fireballs.add(Fireball(self.pos.x + self.width // 2, self.pos.y + self.height // 2, direction))

    def update(self, platforms, enemies, coins, q_blocks, fireballs):
        if self.is_dead:
            self.pos += self.vel
            self.vel.y += GRAVITY
            return
            
        # --- INPUT ---
        self.acc = pygame.math.Vector2(0, GRAVITY)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acc.x = -PLAYER_ACC
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.acc.x = PLAYER_ACC
            self.facing_right = True

        # --- PHYSICS ---
        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += self.acc
        if abs(self.vel.x) < 0.1: self.vel.x = 0
        self.pos.x += self.vel.x + 0.5 * self.acc.x

        self.check_collisions_x(platforms + q_blocks)

        self.pos.y += self.vel.y
        self.on_ground = False
        self.check_collisions_y(platforms + q_blocks)
        
        # --- ENEMY COLLISIONS ---
        if self.invulnerable_timer <= 0:
            for enemy in enemies:
                if self.get_rect().colliderect(enemy.get_rect()):
                    if self.vel.y > 0 and self.get_rect().bottom < enemy.get_rect().centery:
                        enemy.stomp()
                        self.vel.y = JUMP_STRENGTH / 2
                    else:
                        self.take_damage()
        
        # --- COIN/ITEM COLLISIONS ---
        for coin in coins.copy():
            if self.get_rect().colliderect(coin.get_rect()):
                coins.remove(coin)
                self.coins += 1
        
        # --- TIMERS & ANIMATION ---
        if self.invulnerable_timer > 0: self.invulnerable_timer -= 1
        self.animation_frame = (self.animation_frame + 1) % 20

    def check_collisions_x(self, collidables):
        rect = self.get_rect()
        for item in collidables:
            if rect.colliderect(item.get_rect()):
                if self.vel.x > 0: # Moving right
                    self.pos.x = item.get_rect().left - self.width
                elif self.vel.x < 0: # Moving left
                    self.pos.x = item.get_rect().right
                self.vel.x = 0

    def check_collisions_y(self, collidables):
        rect = self.get_rect()
        for item in collidables:
            if rect.colliderect(item.get_rect()):
                if self.vel.y > 0: # Moving down
                    self.pos.y = item.get_rect().top - self.height
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0: # Moving up
                    self.pos.y = item.get_rect().bottom
                    self.vel.y = 0
                    # Hit a block from below
                    if isinstance(item, QBlock):
                        item.hit()


    def get_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)

    def draw(self, screen, camera_x):
        if self.invulnerable_timer > 0 and not self.is_dead:
            if self.invulnerable_timer % 10 < 5:
                return # Flash when invulnerable

        x = self.pos.x - camera_x
        shirt_color = RED
        overalls_color = BLUE
        if self.state == 'fire':
            shirt_color = WHITE
            overalls_color = RED
        
        # Body (overalls)
        pygame.draw.rect(screen, overalls_color, (x, self.pos.y + self.height * 0.4, self.width, self.height * 0.6))
        # Shirt
        pygame.draw.rect(screen, shirt_color, (x, self.pos.y + self.height * 0.3, self.width, self.height * 0.4))
        # Head/Hat/Face etc. are simplified for brevity for now. Main distinction is size and color
        pygame.draw.rect(screen, PINK, (x + 6, self.pos.y + 5, 20, 15)) # Face
        pygame.draw.rect(screen, RED, (x - 2, self.pos.y - 5, self.width + 4, self.height * 0.3)) # Hat

# --- WORLD OBJECTS ---
class Platform:
    def __init__(self, x, y, w, h, color=BROWN):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def get_rect(self): return self.rect
    def draw(self, screen, camera_x):
        pygame.draw.rect(screen, self.color, (self.rect.x - camera_x, self.rect.y, self.rect.w, self.rect.h))

class QBlock:
    def __init__(self, x, y, game, content='coin'):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.original_y = y
        self.game = game
        self.content = content # 'coin', 'fire_flower'
        self.active = True
        self.frame = 0
        self.is_hit = False

    def get_rect(self): return self.rect
    
    def hit(self):
        if not self.active: return
        self.active = False
        self.is_hit = True # Start animation
        if self.content == 'coin':
            self.game.player.coins += 1
        elif self.content == 'fire_flower':
            self.game.powerups.add(PowerUp(self.rect.x, self.rect.y - 40, 'fire_flower'))

    def update(self):
        if self.is_hit:
            self.rect.y -= 4
            if self.rect.y <= self.original_y - 12:
                self.is_hit = False
        elif not self.is_hit and self.rect.y < self.original_y:
            self.rect.y += 2
        
        self.frame = (self.frame + 1) % 60
    
    def draw(self, screen, camera_x):
        x = self.rect.x - camera_x
        if self.active:
            pygame.draw.rect(screen, ORANGE, self.rect.move(-camera_x, 0))
            if self.frame < 30: # Simple flicker for question mark
                text = font.render('?', True, WHITE)
                screen.blit(text, (x + 8, self.rect.y))
        else:
            pygame.draw.rect(screen, (100, 50, 20), self.rect.move(-camera_x, 0)) # Used block color

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type
        self.image = pygame.Surface((32, 32))
        self.image.set_colorkey(BLACK)
        if self.type == 'fire_flower':
             # Simple Fire Flower representation
            pygame.draw.circle(self.image, RED, (16,8), 8)
            pygame.draw.circle(self.image, YELLOW, (16,8), 4)
            pygame.draw.rect(self.image, GREEN, (14, 16, 4, 16))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, player):
        if self.rect.colliderect(player.get_rect()):
            player.set_state('fire')
            self.kill()

    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))

# --- ENEMIES & PROJECTILES ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type='goomba'):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.vel_x = -ENEMY_SPEED
        self.width, self.height = 32, 32
        self.state = 'walking' # walking, stomped
        self.stomp_timer = 0
        self.type = type
        self.animation_frame = 0

    def stomp(self):
        self.state = 'stomped'
        self.stomp_timer = 30 # Time before disappearing
        self.height = 16
        self.pos.y += 16
        
    def update(self, platforms):
        self.animation_frame = (self.animation_frame + 1) % 40
        if self.state == 'walking':
            self.pos.x += self.vel_x
            on_platform_edge = True
            for p in platforms:
                if p.get_rect().collidepoint(self.get_rect().midbottom[0], self.get_rect().midbottom[1] + 5):
                     on_platform_edge = (self.pos.x <= p.rect.x) or (self.pos.x + self.width >= p.rect.right)
                     break
            if on_platform_edge:
                self.vel_x *= -1

        elif self.state == 'stomped':
            self.stomp_timer -= 1
            if self.stomp_timer <= 0:
                self.kill() # Removes sprite from all groups

    def get_rect(self): return pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)

    def draw(self, screen, camera_x):
        x = self.pos.x - camera_x
        color = BROWN if self.type == 'goomba' else DARK_GREEN
        pygame.draw.ellipse(screen, color, (x, self.pos.y, self.width, self.height))
        # Feet animation for Goomba
        if self.type == 'goomba' and self.state == 'walking':
            foot_offset = 3 if self.animation_frame < 20 else -3
            pygame.draw.ellipse(screen, BLACK, (x + 3 + foot_offset, self.pos.y + 25, 8, 5))
            pygame.draw.ellipse(screen, BLACK, (x + 21 - foot_offset, self.pos.y + 25, 8, 5))

class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        pygame.draw.circle(self.image, ORANGE, (5, 5), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = pygame.math.Vector2(10 * direction, -5)
        self.bounce_count = 0
        
    def update(self, platforms, enemies):
        self.vel.y += GRAVITY
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y

        # Platform collision (bounce)
        for p in platforms:
            if self.rect.colliderect(p.get_rect()):
                self.rect.bottom = p.get_rect().top
                self.vel.y = -8 # Bounce
                self.bounce_count += 1

        # Enemy collision
        for enemy in enemies:
            if enemy.state == 'walking' and self.rect.colliderect(enemy.get_rect()):
                enemy.stomp()
                self.kill()

        # Despawn conditions
        if self.bounce_count > 3 or self.rect.y > SCREEN_HEIGHT + 50:
            self.kill()
            
    def draw(self, screen, camera_x):
        screen.blit(self.image, self.rect.move(-camera_x, 0))


# --- LEVEL DATA ---
LEVELS = {
    1: {
        'platforms': [(0, 550, 1200, 50), (1300, 550, 500, 50), (1900, 550, 1300, 50),
                      (200, 420, 100, 20), (500, 350, 100, 20), (800, 450, 40, 100, GREEN)],
        'q_blocks': [(350, 420, 'coin'), (382, 420, 'fire_flower'), (414, 420, 'coin'), (414, 280, 'coin')],
        'enemies': [(450, 518, 'goomba'), (600, 518, 'goomba'), (900, 518, 'goomba')],
        'coins': [(520, 310)],
        'flagpole': 3100
    },
    2: {
        'platforms': [(0, 550, 500, 50), (600, 450, 400, 20), (1100, 550, 1500, 50), (1200, 400, 50, 150, GREEN)],
        'q_blocks': [(200, 450, 'fire_flower'), (700, 350, 'coin'), (732, 350, 'coin')],
        'enemies': [(300, 518, 'goomba'), (750, 418, 'koopa'), (1300, 518, 'koopa'), (1400, 518, 'goomba')],
        'coins': [],
        'flagpole': 3100
    }
}

# --- GAME CLASS ---
class Game:
    def __init__(self, level_num, lives, coins):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ultra Mario World")
        self.clock = pygame.time.Clock()
        self.running = True
        self.status = "RUNNING"
        
        self.camera_x = 0
        self.load_level(level_num, lives, coins)

    def load_level(self, level_num, lives, coins):
        self.platforms = [Platform(*p) for p in LEVELS[level_num]['platforms']]
        self.q_blocks = [QBlock(q[0], q[1], self, content=q[2]) for q in LEVELS[level_num]['q_blocks']]
        self.enemies = pygame.sprite.Group([Enemy(e[0], e[1], type=e[2]) for e in LEVELS[level_num]['enemies']])
        self.coins = [Platform(c[0], c[1], 16, 16, YELLOW) for c in LEVELS[level_num]['coins']]
        
        self.player = Player(100, 400)
        self.player.lives = lives
        self.player.coins = coins

        self.fireballs = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        flag_x = LEVELS[level_num]['flagpole']
        self.flagpole = Platform(flag_x, 150, 10, 400, BLACK)
        self.flag = Platform(flag_x-20, 490, 40, 20, GREEN) # The actual flag part

    def update(self):
        # Update all sprites
        self.player.update(self.platforms, self.enemies, self.coins, self.q_blocks, self.fireballs)
        self.enemies.update(self.platforms)
        self.fireballs.update(self.platforms + self.q_blocks, self.enemies)
        self.powerups.update(self.player)
        for q in self.q_blocks: q.update()

        # Update camera
        target_camera = self.player.pos.x - SCREEN_WIDTH / 3
        self.camera_x += (target_camera - self.camera_x) * 0.1
        self.camera_x = max(0, min(self.camera_x, LEVEL_WIDTH - SCREEN_WIDTH))
        
        # Check death
        if self.player.is_dead and self.player.pos.y > SCREEN_HEIGHT + 100:
            if self.player.lives > 0:
                self.load_level(current_level, self.player.lives, self.player.coins) # Restart level
            else:
                self.status = "GAME_OVER"
                self.running = False
        
        # Check level win
        if self.player.get_rect().colliderect(self.flagpole.get_rect()):
            self.status = "LEVEL_COMPLETE"
            self.running = False

    def draw(self):
        self.screen.fill(SKY_BLUE)

        for p in self.platforms: p.draw(self.screen, self.camera_x)
        for q in self.q_blocks: q.draw(self.screen, self.camera_x)
        for c in self.coins: c.draw(self.screen, self.camera_x)
        self.flagpole.draw(self.screen, self.camera_x)
        self.flag.draw(self.screen, self.camera_x)
        
        # #### FIX START ####
        # The line `self.enemies.draw(...)` caused the crash because Enemy objects
        # are drawn procedurally and don't have a static `image` attribute.
        # It has been removed, leaving the correct manual loop below it.
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_x)
        # #### FIX END ####
        
        for fireball in self.fireballs: fireball.draw(self.screen, self.camera_x)
        for powerup in self.powerups: powerup.draw(self.screen, self.camera_x)

        self.player.draw(self.screen, self.camera_x)

        # Draw HUD
        hud_surface = pygame.Surface((SCREEN_WIDTH, 40), pygame.SRCALPHA)
        hud_surface.fill((0, 0, 0, 128))
        lives_text = font.render(f"LIVES: {self.player.lives}", True, WHITE)
        coins_text = font.render(f"COINS: {self.player.coins}", True, YELLOW)
        level_text = font.render(f"LEVEL: {current_level}", True, WHITE)
        hud_surface.blit(level_text, (10, 5))
        hud_surface.blit(lives_text, (150, 5))
        hud_surface.blit(coins_text, (300, 5))
        self.screen.blit(hud_surface, (0, 0))

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.status = "QUIT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.status = "QUIT"
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    if event.key == pygame.K_LCTRL:
                        self.player.shoot(self.fireballs)

            self.update()
            self.draw()
            self.clock.tick(FPS)
        return self.status

# --- MENU AND GAME STATES ---
def show_main_menu(screen):
    options = ["Start Game", "Quit"]
    selected = 0
    while True:
        screen.fill(SKY_BLUE)
        title_text = menu_font.render("Ultra Mario World", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
        
        for i, option in enumerate(options):
            color = YELLOW if i == selected else WHITE
            text = font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300 + i * 50))

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected == 0: return "START"
                    if selected == 1: return "QUIT"
                elif event.key == pygame.K_ESCAPE:
                    return "QUIT"

def show_end_screen(screen, message, final_coins):
    screen.fill(BLACK)
    msg_text = menu_font.render(message, True, RED if "OVER" in message else GREEN)
    score_text = font.render(f"Final Coins: {final_coins}", True, WHITE)
    prompt_text = font.render("Press any key to return to menu", True, WHITE)
    screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, 200))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))
    screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 400))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                waiting = False

# --- MAIN CONTROLLER ---
if __name__ == "__main__":
    main_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    current_level = 1
    player_lives, player_coins = 3, 0

    while True:
        menu_choice = show_main_menu(main_screen)
        
        if menu_choice == "QUIT":
            break
        
        if menu_choice == "START":
            # Reset game stats for a new game
            current_level = 1
            player_lives, player_coins = 3, 0
            
            while current_level <= len(LEVELS):
                game = Game(current_level, player_lives, player_coins)
                game_status = game.run()

                if game_status == "QUIT":
                    break # Exit to main menu loop
                
                player_lives = game.player.lives
                player_coins = game.player.coins

                if game_status == "GAME_OVER":
                    show_end_screen(main_screen, "GAME OVER", player_coins)
                    break # Exit to main menu loop
                
                if game_status == "LEVEL_COMPLETE":
                    current_level += 1
            
            else: # This 'else' belongs to the 'while' loop, runs if it completes without break
                 show_end_screen(main_screen, "YOU WIN!", player_coins)

    pygame.quit()
