#!/usr/bin/env python3
"""
Cave Story x Paper Mario Fusion Engine
2D platformer with Paper Mario HUD and Cave Story mechanics
"""

import pygame
import math
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
JUMP_POWER = -15
MAX_FALL_SPEED = 12
TILE_SIZE = 32

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
DARK_GRAY = (64, 64, 64)

class EntityType(Enum):
    PLAYER = "PLAYER"
    ENEMY = "ENEMY"
    PROJECTILE = "PROJECTILE"
    ITEM = "ITEM"
    PLATFORM = "PLATFORM"
    POWERUP = "POWERUP"

@dataclass
class Vector2:
    x: float
    y: float
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

class Entity:
    def __init__(self, x: float, y: float, width: int, height: int, entity_type: EntityType):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.width = width
        self.height = height
        self.entity_type = entity_type
        self.hp = 100
        self.max_hp = 100
        self.flip_timer = 0
        self.is_flipped = False
        self.color = WHITE
        self.alive = True
        
    def update(self, dt: float):
        # Paper Mario flip animation on damage
        if self.flip_timer > 0:
            self.flip_timer -= dt
            self.is_flipped = (self.flip_timer * 10) % 2 < 1
        
        # Physics
        if self.entity_type != EntityType.PLATFORM:
            self.vel.y += GRAVITY
            self.vel.y = min(self.vel.y, MAX_FALL_SPEED)
            self.pos.x += self.vel.x
            self.pos.y += self.vel.y
        
    def get_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
    
    def draw(self, screen, camera):
        rect = pygame.Rect(self.pos.x - camera.x, self.pos.y - camera.y, self.width, self.height)
        
        if self.is_flipped:
            # Paper flip effect - make it thin
            rect.width = max(2, rect.width // 4)
            rect.x += self.width // 2 - rect.width // 2
            
        pygame.draw.rect(screen, self.color, rect)
        
        # HP bar for enemies
        if self.entity_type == EntityType.ENEMY and self.hp < self.max_hp:
            bar_rect = pygame.Rect(self.pos.x - camera.x, self.pos.y - camera.y - 10, self.width, 4)
            pygame.draw.rect(screen, RED, bar_rect)
            bar_rect.width = int(bar_rect.width * (self.hp / self.max_hp))
            pygame.draw.rect(screen, GREEN, bar_rect)
    
    def take_damage(self, damage: int):
        self.hp -= damage
        self.flip_timer = 0.5  # Paper flip effect
        if self.hp <= 0:
            self.alive = False

class Player(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 24, 32, EntityType.PLAYER)
        self.color = BLUE
        self.level = 1
        self.exp = 0
        self.max_exp = 100
        self.weapon_level = 1
        self.can_jump = False
        self.facing_right = True
        self.boost_fuel = 100.0
        self.max_boost = 100.0
        self.invulnerable_timer = 0
        
    def update(self, dt: float):
        super().update(dt)
        
        # Regenerate boost slowly
        if self.boost_fuel < self.max_boost:
            self.boost_fuel = min(self.max_boost, self.boost_fuel + 20 * dt)
            
        # Invulnerability frames
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
            
    def draw(self, screen, camera):
        # Draw with flashing when invulnerable
        if self.invulnerable_timer <= 0 or int(self.invulnerable_timer * 10) % 2 == 0:
            rect = pygame.Rect(self.pos.x - camera.x, self.pos.y - camera.y, self.width, self.height)
            
            if self.is_flipped:
                # Paper flip effect
                rect.width = max(2, rect.width // 4)
                rect.x += self.width // 2 - rect.width // 2
            
            # Draw Quote-like character
            pygame.draw.rect(screen, self.color, rect)
            
            # Draw cap/hat
            hat_rect = pygame.Rect(rect.x, rect.y - 4, rect.width, 8)
            pygame.draw.rect(screen, RED, hat_rect)
            
            # Draw face direction indicator
            eye_x = rect.x + (rect.width - 4 if self.facing_right else 4)
            eye_rect = pygame.Rect(eye_x, rect.y + 8, 4, 4)
            pygame.draw.rect(screen, WHITE, eye_rect)
            
    def add_exp(self, amount):
        self.exp += amount
        while self.exp >= self.max_exp:
            self.exp -= self.max_exp
            self.level += 1
            self.max_exp = int(self.max_exp * 1.5)
            self.max_hp += 10
            self.hp = self.max_hp

class Projectile(Entity):
    def __init__(self, x: float, y: float, direction: int, damage: int, proj_type="polar_star"):
        super().__init__(x, y, 8, 4, EntityType.PROJECTILE)
        self.vel.x = direction * 12
        self.vel.y = 0
        self.damage = damage
        self.lifetime = 2.0
        self.proj_type = proj_type
        self.color = YELLOW if proj_type == "polar_star" else ORANGE
        
    def update(self, dt: float):
        self.lifetime -= dt
        self.pos.x += self.vel.x
        
        # Different projectile behaviors
        if self.proj_type == "fireball":
            self.vel.y += GRAVITY * 0.3
            self.pos.y += self.vel.y
        elif self.proj_type == "bubbler":
            self.vel.y = math.sin(self.lifetime * 10) * 2
            self.pos.y += self.vel.y
            
        if self.lifetime <= 0:
            self.alive = False
            
    def draw(self, screen, camera):
        rect = pygame.Rect(self.pos.x - camera.x, self.pos.y - camera.y, self.width, self.height)
        
        if self.proj_type == "polar_star":
            pygame.draw.rect(screen, self.color, rect)
        elif self.proj_type == "fireball":
            pygame.draw.circle(screen, self.color, 
                             (int(rect.x + rect.width//2), int(rect.y + rect.height//2)), 
                             self.width//2)
        elif self.proj_type == "bubbler":
            pygame.draw.circle(screen, BLUE, 
                             (int(rect.x + rect.width//2), int(rect.y + rect.height//2)), 
                             self.width//2)
            pygame.draw.circle(screen, WHITE, 
                             (int(rect.x + rect.width//2 - 2), int(rect.y + rect.height//2 - 2)), 
                             2)

class Enemy(Entity):
    def __init__(self, x: float, y: float, enemy_type: str):
        if enemy_type == "Balrog":
            super().__init__(x, y, 48, 64, EntityType.ENEMY)
            self.hp = 300
            self.max_hp = 300
            self.color = PURPLE
            self.exp_value = 50
        elif enemy_type == "Critter":
            super().__init__(x, y, 24, 24, EntityType.ENEMY)
            self.hp = 20
            self.max_hp = 20
            self.color = GREEN
            self.exp_value = 5
        else:
            super().__init__(x, y, 32, 32, EntityType.ENEMY)
            self.hp = 50
            self.max_hp = 50
            self.color = RED
            self.exp_value = 10
            
        self.enemy_type = enemy_type
        self.ai_timer = 0
        self.jump_cooldown = 0
        
    def update(self, dt: float, player: Player, platforms: List[Entity]):
        super().update(dt)
        self.ai_timer += dt
        
        # Simple AI
        if self.enemy_type == "Critter":
            # Hop around
            if self.jump_cooldown <= 0 and abs(self.vel.y) < 0.1:
                self.vel.y = -8
                self.vel.x = random.choice([-2, 2])
                self.jump_cooldown = random.uniform(1, 3)
            self.jump_cooldown -= dt
            
        elif self.enemy_type == "Balrog":
            # Chase player
            if self.ai_timer > 1:
                dx = player.pos.x - self.pos.x
                if abs(dx) > 50:
                    self.vel.x = 3 if dx > 0 else -3
                else:
                    self.vel.x = 0
                    
                # Jump if player is above
                if player.pos.y < self.pos.y - 50 and self.jump_cooldown <= 0:
                    self.vel.y = -12
                    self.jump_cooldown = 2
                    
                self.jump_cooldown -= dt
        
    def draw(self, screen, camera):
        super().draw(screen, camera)
        
        # Draw enemy-specific features
        rect = pygame.Rect(self.pos.x - camera.x, self.pos.y - camera.y, self.width, self.height)
        
        if self.enemy_type == "Balrog":
            # Draw eyes
            eye_y = rect.y + 10
            pygame.draw.circle(screen, WHITE, (rect.x + 12, eye_y), 6)
            pygame.draw.circle(screen, WHITE, (rect.x + rect.width - 12, eye_y), 6)
            pygame.draw.circle(screen, BLACK, (rect.x + 12, eye_y), 3)
            pygame.draw.circle(screen, BLACK, (rect.x + rect.width - 12, eye_y), 3)

class Weapon:
    def __init__(self, name: str, damage: int, fire_rate: float):
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate
        self.cooldown = 0
        self.level = 1
        self.ammo = -1  # -1 means infinite
        
    def fire(self, x: float, y: float, direction: int) -> Optional[Projectile]:
        if self.cooldown <= 0 and (self.ammo == -1 or self.ammo > 0):
            self.cooldown = self.fire_rate
            if self.ammo > 0:
                self.ammo -= 1
                
            proj_type = "polar_star"
            if self.name == "Fireball":
                proj_type = "fireball"
            elif self.name == "Bubbler":
                proj_type = "bubbler"
                
            return Projectile(x, y, direction, self.damage * self.level, proj_type)
        return None
    
    def update(self, dt: float):
        self.cooldown = max(0, self.cooldown - dt)

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        
    def update(self, target_x, target_y):
        # Smooth camera following
        self.x += (target_x - SCREEN_WIDTH // 2 - self.x) * 0.1
        self.y += (target_y - SCREEN_HEIGHT // 2 - self.y) * 0.1
        
        # Keep camera in bounds
        self.x = max(0, self.x)
        self.y = max(0, self.y)

class PaperMarioHUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        
    def draw(self, screen, player: Player, weapon: Weapon):
        # Paper Mario style HP display
        hp_bg = pygame.Rect(20, 20, 200, 40)
        pygame.draw.rect(screen, BLACK, hp_bg)
        pygame.draw.rect(screen, WHITE, hp_bg, 3)
        
        # HP text
        hp_text = self.font.render("HP", True, WHITE)
        screen.blit(hp_text, (30, 30))
        
        # HP bar
        hp_bar_bg = pygame.Rect(60, 30, 130, 20)
        pygame.draw.rect(screen, DARK_GRAY, hp_bar_bg)
        hp_bar = pygame.Rect(60, 30, int(130 * (player.hp / player.max_hp)), 20)
        pygame.draw.rect(screen, RED, hp_bar)
        
        # HP numbers
        hp_numbers = self.font.render(f"{player.hp}/{player.max_hp}", True, WHITE)
        screen.blit(hp_numbers, (80, 32))
        
        # Boost gauge (Cave Story style)
        boost_bg = pygame.Rect(20, 70, 200, 30)
        pygame.draw.rect(screen, BLACK, boost_bg)
        pygame.draw.rect(screen, WHITE, boost_bg, 3)
        
        boost_text = self.font.render("BOOST", True, WHITE)
        screen.blit(boost_text, (25, 75))
        
        boost_bar_bg = pygame.Rect(80, 75, 110, 20)
        pygame.draw.rect(screen, DARK_GRAY, boost_bar_bg)
        boost_bar = pygame.Rect(80, 75, int(110 * (player.boost_fuel / player.max_boost)), 20)
        pygame.draw.rect(screen, ORANGE, boost_bar)
        
        # Level/EXP (Paper Mario style)
        level_bg = pygame.Rect(20, 110, 200, 60)
        pygame.draw.rect(screen, BLACK, level_bg)
        pygame.draw.rect(screen, WHITE, level_bg, 3)
        
        level_text = self.big_font.render(f"LV {player.level}", True, YELLOW)
        screen.blit(level_text, (30, 115))
        
        # EXP bar
        exp_bar_bg = pygame.Rect(30, 145, 180, 15)
        pygame.draw.rect(screen, DARK_GRAY, exp_bar_bg)
        exp_bar = pygame.Rect(30, 145, int(180 * (player.exp / player.max_exp)), 15)
        pygame.draw.rect(screen, BLUE, exp_bar)
        
        exp_text = self.font.render(f"EXP: {player.exp}/{player.max_exp}", True, WHITE)
        screen.blit(exp_text, (35, 145))
        
        # Weapon display (Cave Story style)
        weapon_bg = pygame.Rect(SCREEN_WIDTH - 220, 20, 200, 80)
        pygame.draw.rect(screen, BLACK, weapon_bg)
        pygame.draw.rect(screen, WHITE, weapon_bg, 3)
        
        weapon_name = self.font.render(weapon.name, True, YELLOW)
        screen.blit(weapon_name, (SCREEN_WIDTH - 210, 30))
        
        weapon_level = self.font.render(f"Level {weapon.level}", True, WHITE)
        screen.blit(weapon_level, (SCREEN_WIDTH - 210, 55))
        
        if weapon.ammo >= 0:
            ammo_text = self.font.render(f"Ammo: {weapon.ammo}", True, WHITE)
            screen.blit(ammo_text, (SCREEN_WIDTH - 210, 75))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cave Story x Paper Mario")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game objects
        self.player = Player(100, 300)
        self.camera = Camera()
        self.hud = PaperMarioHUD()
        self.weapon = Weapon("Polar Star", 10, 0.2)
        
        # Entity lists
        self.platforms = []
        self.enemies = []
        self.projectiles = []
        self.particles = []
        
        # Create level
        self._create_level()
        
    def _create_level(self):
        # Create platforms
        platform_data = [
            (0, 500, 300, 100),
            (350, 450, 200, 150),
            (600, 400, 300, 200),
            (200, 350, 150, 20),
            (400, 300, 100, 20),
            (550, 250, 150, 20),
            (750, 350, 200, 20),
            (0, 600, 1000, 100),  # Ground
        ]
        
        for x, y, w, h in platform_data:
            platform = Entity(x, y, w, h, EntityType.PLATFORM)
            platform.color = BROWN
            self.platforms.append(platform)
            
        # Add enemies
        self.enemies.append(Enemy(400, 250, "Critter"))
        self.enemies.append(Enemy(600, 200, "Critter"))
        self.enemies.append(Enemy(750, 300, "Balrog"))
        
    def handle_events(self):
        keys = pygame.key.get_pressed()
        
        # Player movement
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player.vel.x = -5
            self.player.facing_right = False
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player.vel.x = 5
            self.player.facing_right = True
        else:
            self.player.vel.x *= 0.8  # Friction
            
        # Jump
        if (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]) and self.player.can_jump:
            self.player.vel.y = JUMP_POWER
            self.player.can_jump = False
            
        # Boost (Cave Story jetpack)
        if keys[pygame.K_LSHIFT] and self.player.boost_fuel > 0:
            self.player.vel.y = min(self.player.vel.y, -3)
            self.player.boost_fuel -= 30 / FPS
            
            # Boost particles
            for _ in range(2):
                particle = Entity(
                    self.player.pos.x + self.player.width // 2 + random.randint(-5, 5),
                    self.player.pos.y + self.player.height,
                    4, 4, EntityType.PROJECTILE
                )
                particle.color = ORANGE
                particle.vel.y = random.uniform(2, 5)
                particle.vel.x = random.uniform(-1, 1)
                particle.lifetime = 0.5
                self.particles.append(particle)
            
        # Shoot
        if keys[pygame.K_k]:
            projectile = self.weapon.fire(
                self.player.pos.x + (self.player.width if self.player.facing_right else 0),
                self.player.pos.y + self.player.height // 2,
                1 if self.player.facing_right else -1
            )
            if projectile:
                self.projectiles.append(projectile)
                
        # Weapon switching (1-3 keys)
        if keys[pygame.K_1]:
            self.weapon = Weapon("Polar Star", 10, 0.2)
        elif keys[pygame.K_2]:
            self.weapon = Weapon("Fireball", 15, 0.3)
        elif keys[pygame.K_3]:
            self.weapon = Weapon("Bubbler", 8, 0.15)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
    def update(self, dt):
        # Update player
        self.player.update(dt)
        
        # Platform collision for player
        self.player.can_jump = False
        player_rect = self.player.get_rect()
        
        for platform in self.platforms:
            plat_rect = platform.get_rect()
            if player_rect.colliderect(plat_rect):
                # Landing on top
                if self.player.vel.y > 0 and player_rect.bottom - 10 < plat_rect.top:
                    self.player.pos.y = plat_rect.top - self.player.height
                    self.player.vel.y = 0
                    self.player.can_jump = True
                # Hit from below
                elif self.player.vel.y < 0 and player_rect.top > plat_rect.bottom - 10:
                    self.player.pos.y = plat_rect.bottom
                    self.player.vel.y = 0
                # Side collision
                elif player_rect.centerx < plat_rect.centerx and self.player.vel.x > 0:
                    self.player.pos.x = plat_rect.left - self.player.width
                    self.player.vel.x = 0
                elif player_rect.centerx > plat_rect.centerx and self.player.vel.x < 0:
                    self.player.pos.x = plat_rect.right
                    self.player.vel.x = 0
                    
        # Update enemies
        for enemy in self.enemies[:]:
            if not enemy.alive:
                # Create exp orbs
                for _ in range(3):
                    orb = Entity(
                        enemy.pos.x + random.randint(0, enemy.width),
                        enemy.pos.y + random.randint(0, enemy.height),
                        8, 8, EntityType.ITEM
                    )
                    orb.color = YELLOW
                    orb.vel.y = -random.uniform(2, 5)
                    orb.vel.x = random.uniform(-2, 2)
                    orb.exp_value = enemy.exp_value // 3
                    self.particles.append(orb)
                self.enemies.remove(enemy)
                continue
                
            enemy.update(dt, self.player, self.platforms)
            
            # Platform collision for enemies
            enemy_rect = enemy.get_rect()
            for platform in self.platforms:
                plat_rect = platform.get_rect()
                if enemy_rect.colliderect(plat_rect):
                    if enemy.vel.y > 0 and enemy_rect.bottom - 10 < plat_rect.top:
                        enemy.pos.y = plat_rect.top - enemy.height
                        enemy.vel.y = 0
                        
            # Check collision with player
            if enemy_rect.colliderect(player_rect) and self.player.invulnerable_timer <= 0:
                self.player.take_damage(20)
                self.player.invulnerable_timer = 1.5
                # Knockback
                if self.player.pos.x < enemy.pos.x:
                    self.player.vel.x = -10
                else:
                    self.player.vel.x = 10
                self.player.vel.y = -5
                
        # Update projectiles
        for proj in self.projectiles[:]:
            proj.update(dt)
            if not proj.alive:
                self.projectiles.remove(proj)
                continue
                
            proj_rect = proj.get_rect()
            
            # Check collision with enemies
            for enemy in self.enemies:
                if proj_rect.colliderect(enemy.get_rect()):
                    enemy.take_damage(proj.damage)
                    proj.alive = False
                    # Add hit effect
                    for _ in range(5):
                        particle = Entity(
                            proj.pos.x + random.randint(-5, 5),
                            proj.pos.y + random.randint(-5, 5),
                            3, 3, EntityType.PROJECTILE
                        )
                        particle.color = WHITE
                        particle.vel.x = random.uniform(-3, 3)
                        particle.vel.y = random.uniform(-3, 3)
                        particle.lifetime = 0.3
                        self.particles.append(particle)
                    break
                    
            # Check collision with platforms
            for platform in self.platforms:
                if proj_rect.colliderect(platform.get_rect()):
                    proj.alive = False
                    break
                    
        # Update particles and exp orbs
        for particle in self.particles[:]:
            if hasattr(particle, 'lifetime'):
                particle.lifetime -= dt
                if particle.lifetime <= 0:
                    self.particles.remove(particle)
                    continue
                    
            particle.update(dt)
            
            # Exp orbs are attracted to player
            if particle.entity_type == EntityType.ITEM and hasattr(particle, 'exp_value'):
                dx = self.player.pos.x - particle.pos.x
                dy = self.player.pos.y - particle.pos.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < 100:  # Attraction range
                    particle.vel.x += dx / dist * 2
                    particle.vel.y += dy / dist * 2
                    
                if dist < 20:  # Collection range
                    self.player.add_exp(particle.exp_value)
                    self.particles.remove(particle)
                    # Level up weapon too
                    if self.weapon.level < 3 and random.random() < 0.3:
                        self.weapon.level += 1
                        self.weapon.damage = int(self.weapon.damage * 1.5)
                    
        # Update weapon
        self.weapon.update(dt)
        
        # Update camera
        self.camera.update(self.player.pos.x, self.player.pos.y)
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw background
        for i in range(0, SCREEN_HEIGHT, 50):
            color = (20, 20, 40 - i // 20)
            pygame.draw.rect(self.screen, color, (0, i, SCREEN_WIDTH, 50))
        
        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen, self.camera)
            
        # Draw particles (behind entities)
        for particle in self.particles:
            if hasattr(particle, 'lifetime'):
                particle.draw(self.screen, self.camera)
                
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)
            
        # Draw projectiles
        for proj in self.projectiles:
            proj.draw(self.screen, self.camera)
            
        # Draw exp orbs
        for particle in self.particles:
            if particle.entity_type == EntityType.ITEM:
                rect = pygame.Rect(
                    particle.pos.x - self.camera.x,
                    particle.pos.y - self.camera.y,
                    particle.width, particle.height
                )
                pygame.draw.circle(self.screen, particle.color, 
                                 (rect.x + rect.width//2, rect.y + rect.height//2),
                                 particle.width//2)
                
        # Draw player
        self.player.draw(self.screen, self.camera)
        
        # Draw HUD
        self.hud.draw(self.screen, self.player, self.weapon)
        
        # Game over screen
        if self.player.hp <= 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.hud.big_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
            
        pygame.display.flip()
        
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
