import pygame
import math
import random
import sys
import json
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from collections import defaultdict

# ----- Constants -----
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
JUMP_POWER = -12
MAX_FALL_SPEED = 10
MOVE_SPEED = 4
BOOST_SPEED = 3

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
DARK_GRAY = (64, 64, 64)
LIGHT_BLUE = (173, 216, 230)
PINK = (255, 192, 203)

# ----- Enums -----
class EntityType(Enum):
    PLAYER = auto()
    ENEMY = auto()
    PROJECTILE = auto()
    ITEM = auto()
    PLATFORM = auto()
    EXPERIENCE = auto()
    HEART = auto()
    SAVE_POINT = auto()
    NPC = auto()
    PARTNER = auto()

class GameState(Enum):
    OVERWORLD = auto()
    BATTLE = auto()
    DIALOGUE = auto()
    MENU = auto()
    GAME_OVER = auto()

class BattleAction(Enum):
    JUMP = auto()
    HAMMER = auto()
    ITEM = auto()
    RUN = auto()
    SPECIAL = auto()

class WeaponType(Enum):
    POLAR_STAR = auto()
    FIREBALL = auto()
    BUBBLER = auto()
    BLADE = auto()
    MISSILE = auto()
    SPUR = auto()

# ----- Data Structures -----
@dataclass
class Vector2:
    x: float
    y: float

    def __add__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: float) -> "Vector2":
        return Vector2(self.x * scalar, self.y * scalar)

    def snap(self) -> "Vector2":
        return Vector2(round(self.x), round(self.y))

    def distance(self, other: "Vector2") -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

# ----- Base Classes -----
class Entity:
    def __init__(self, x: float, y: float, w: int, h: int, etype: EntityType):
        self.pos = Vector2(x, y).snap()
        self.old_pos = Vector2(x, y).snap()
        self.vel = Vector2(0, 0)
        self.width, self.height = w, h
        self.type = etype
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.color = WHITE
        self.flip_timer = 0
        self.is_flipped = False
        self.grounded = False

    def update(self, dt: float):
        if self.type not in [EntityType.PLATFORM, EntityType.SAVE_POINT]:
            self.old_pos = Vector2(self.pos.x, self.pos.y)
            
            # Apply gravity
            if not self.grounded:
                self.vel.y = min(self.vel.y + GRAVITY, MAX_FALL_SPEED)
            
            self.pos.y += self.vel.y
            self.pos.x += self.vel.x
            self.pos = self.pos.snap()

        if self.flip_timer > 0:
            self.flip_timer -= dt
            self.is_flipped = (self.flip_timer * 10) % 2 < 1

    def draw(self, surf: pygame.Surface, cam_x: float, cam_y: float):
        rect = pygame.Rect(self.pos.x - cam_x, self.pos.y - cam_y,
                           self.width, self.height)
        
        # Paper Mario style squash effect
        if self.is_flipped:
            rect.width = int(rect.width * 0.3)
            rect.x += (self.width - rect.width) // 2
        
        pygame.draw.rect(surf, self.color, rect)
        
        # Draw health bar for enemies
        if self.type == EntityType.ENEMY and self.hp < self.max_hp:
            back = pygame.Rect(rect.x, rect.y - 8, self.width, 4)
            fg = pygame.Rect(rect.x, rect.y - 8,
                             int(self.width * (self.hp / self.max_hp)), 4)
            pygame.draw.rect(surf, RED, back)
            pygame.draw.rect(surf, GREEN, fg)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)

    def damage(self, amount: int):
        self.hp -= amount
        self.flip_timer = 0.5
        if self.hp <= 0:
            self.alive = False

# ----- Cave Story Weapons -----
@dataclass
class Weapon:
    name: str
    type: WeaponType
    damage: int
    fire_rate: float
    max_ammo: int = -1
    ammo: int = -1
    level: int = 1
    exp: int = 0
    exp_required: List[int] = field(default_factory=lambda: [10, 20, 40])
    cooldown: float = 0

    def can_level_up(self) -> bool:
        return self.level < 3 and self.exp >= self.exp_required[self.level - 1]

    def level_up(self):
        if self.can_level_up():
            self.level += 1
            self.exp = 0
            self.damage = int(self.damage * 1.5)

    def add_exp(self, amount: int):
        if self.level < 3:
            self.exp += amount
            while self.can_level_up():
                self.level_up()

    def fire(self, x: float, y: float, dir: int) -> Optional['Projectile']:
        if self.cooldown > 0 or (self.ammo == 0):
            return None
        
        self.cooldown = self.fire_rate
        if self.ammo > 0:
            self.ammo -= 1
        
        return Projectile(x, y, dir, self.damage * self.level, self.type)

    def update(self, dt: float):
        self.cooldown = max(0, self.cooldown - dt)

# ----- Player & Partners -----
class Player(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 24, 32, EntityType.PLAYER)
        self.color = BLUE
        
        # Cave Story elements
        self.weapons: List[Weapon] = [
            Weapon("Polar Star", WeaponType.POLAR_STAR, 10, 0.2),
        ]
        self.current_weapon_idx = 0
        self.boost_fuel = 100
        
        # Paper Mario elements
        self.level = 1
        self.star_points = 0
        self.star_points_to_level = 100
        self.fp = 10
        self.max_fp = 10
        self.bp = 3  # Badge Points
        self.coins = 0
        self.badges: List['Badge'] = []
        self.inventory: List['Item'] = []
        self.partners: List['Partner'] = []
        self.current_partner_idx = 0
        
        # States
        self.facing_right = True
        self.can_jump = False
        self.inv_timer = 0
        self.paper_mode = False
        self.paper_flip_timer = 0

    @property
    def current_weapon(self) -> Weapon:
        return self.weapons[self.current_weapon_idx]

    def update(self, dt: float):
        super().update(dt)
        
        # Update boost fuel
        if self.boost_fuel < 100:
            self.boost_fuel = min(100, self.boost_fuel + 20 * dt)
        
        # Update invincibility
        self.inv_timer = max(0, self.inv_timer - dt)
        
        # Update paper flip
        if self.paper_flip_timer > 0:
            self.paper_flip_timer -= dt
            self.paper_mode = True
        else:
            self.paper_mode = False
        
        # Update current weapon
        self.current_weapon.update(dt)

    def draw(self, surf: pygame.Surface, cam_x: float, cam_y: float):
        if self.inv_timer <= 0 or int(self.inv_timer * 10) % 2 == 0:
            rect = pygame.Rect(self.pos.x - cam_x, self.pos.y - cam_y,
                               self.width, self.height)
            
            # Paper mode visual
            if self.paper_mode:
                rect.width = max(2, int(rect.width * abs(math.sin(self.paper_flip_timer * 10))))
                rect.x += (self.width - rect.width) // 2
            
            # Body
            pygame.draw.rect(surf, self.color, rect)
            
            # Hat (Mario style)
            hat = pygame.Rect(rect.x, rect.y - 4, rect.width, 6)
            pygame.draw.rect(surf, RED, hat)
            
            # Draw partner behind player
            if self.partners and self.current_partner_idx < len(self.partners):
                partner = self.partners[self.current_partner_idx]
                partner.draw(surf, cam_x, cam_y)

    def add_star_points(self, amount: int):
        self.star_points += amount
        while self.star_points >= self.star_points_to_level:
            self.star_points -= self.star_points_to_level
            self.level_up()

    def level_up(self):
        self.level += 1
        self.star_points_to_level = int(self.star_points_to_level * 1.2)
        # Player chooses what to upgrade
        self.max_hp += 5
        self.hp = self.max_hp

    def add_weapon(self, weapon: Weapon):
        for w in self.weapons:
            if w.type == weapon.type:
                return  # Already have this weapon
        self.weapons.append(weapon)

    def switch_weapon(self, direction: int):
        self.current_weapon_idx = (self.current_weapon_idx + direction) % len(self.weapons)

# ----- Partner System -----
@dataclass
class Partner:
    name: str
    hp: int
    max_hp: int
    abilities: List[str]
    color: Tuple[int, int, int]
    pos: Vector2
    following_distance: float = 50

    def update(self, player_pos: Vector2, dt: float):
        # Follow player with delay
        dx = player_pos.x - self.pos.x - self.following_distance
        dy = player_pos.y - self.pos.y
        
        if abs(dx) > 5:
            self.pos.x += dx * 0.1
        if abs(dy) > 5:
            self.pos.y += dy * 0.1

    def draw(self, surf: pygame.Surface, cam_x: float, cam_y: float):
        rect = pygame.Rect(self.pos.x - cam_x - 20, self.pos.y - cam_y,
                           20, 28)
        pygame.draw.rect(surf, self.color, rect)

# ----- Projectiles -----
class Projectile(Entity):
    def __init__(self, x: float, y: float, direction: int, damage: int, wtype: WeaponType):
        size = 8 if wtype != WeaponType.MISSILE else 12
        super().__init__(x, y, size, size//2, EntityType.PROJECTILE)
        self.weapon_type = wtype
        self.vel.x = direction * self._get_speed()
        self.damage = damage
        self.lifetime = 2
        self.direction = direction
        self.color = self._get_color()

    def _get_speed(self) -> float:
        speeds = {
            WeaponType.POLAR_STAR: 12,
            WeaponType.FIREBALL: 8,
            WeaponType.BUBBLER: 10,
            WeaponType.BLADE: 15,
            WeaponType.MISSILE: 10,
            WeaponType.SPUR: 20
        }
        return speeds.get(self.weapon_type, 12)

    def _get_color(self) -> Tuple[int, int, int]:
        colors = {
            WeaponType.POLAR_STAR: YELLOW,
            WeaponType.FIREBALL: ORANGE,
            WeaponType.BUBBLER: LIGHT_BLUE,
            WeaponType.BLADE: WHITE,
            WeaponType.MISSILE: RED,
            WeaponType.SPUR: PURPLE
        }
        return colors.get(self.weapon_type, YELLOW)

    def update(self, dt: float):
        self.lifetime -= dt
        
        # Weapon-specific behaviors
        if self.weapon_type == WeaponType.FIREBALL:
            self.vel.y += GRAVITY * 0.5
        elif self.weapon_type == WeaponType.BUBBLER:
            self.vel.y = math.sin(self.lifetime * 10) * 3
        elif self.weapon_type == WeaponType.MISSILE:
            # Missiles accelerate
            self.vel.x *= 1.02
        
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y
        self.pos = self.pos.snap()
        
        if self.lifetime <= 0:
            self.alive = False

# ----- Enemies -----
class Enemy(Entity):
    def __init__(self, x: float, y: float, enemy_type: str):
        self.enemy_type = enemy_type
        self._setup_stats()
        super().__init__(x, y, self.width, self.height, EntityType.ENEMY)
        self.ai_timer = 0
        self.action_cooldown = 0
        self.patrol_direction = random.choice([-1, 1])

    def _setup_stats(self):
        stats = {
            "Critter": {"size": (16, 16), "hp": 20, "color": GREEN, "star_points": 1},
            "Bat": {"size": (20, 16), "hp": 30, "color": PURPLE, "star_points": 2},
            "Balrog": {"size": (48, 48), "hp": 300, "color": BROWN, "star_points": 20},
            "Flower": {"size": (24, 24), "hp": 50, "color": PINK, "star_points": 3},
            "Gaudi": {"size": (32, 32), "hp": 80, "color": DARK_GRAY, "star_points": 5}
        }
        
        enemy_stats = stats.get(self.enemy_type, stats["Critter"])
        self.width, self.height = enemy_stats["size"]
        self.hp = self.max_hp = enemy_stats["hp"]
        self.color = enemy_stats["color"]
        self.star_points_value = enemy_stats["star_points"]

    def update(self, dt: float, player: Player, platforms: List[Entity]):
        super().update(dt)
        self.ai_timer += dt
        
        # Enemy-specific AI
        if self.enemy_type == "Critter":
            self._critter_ai(dt)
        elif self.enemy_type == "Bat":
            self._bat_ai(dt, player)
        elif self.enemy_type == "Balrog":
            self._balrog_ai(dt, player)
        elif self.enemy_type == "Gaudi":
            self._gaudi_ai(dt, player)

    def _critter_ai(self, dt: float):
        # Hop around randomly
        if self.grounded and self.action_cooldown <= 0:
            self.vel.y = -8
            self.vel.x = random.choice([-2, 2])
            self.action_cooldown = random.uniform(1, 3)
        self.action_cooldown -= dt

    def _bat_ai(self, dt: float, player: Player):
        # Fly in sine wave pattern toward player
        dx = player.pos.x - self.pos.x
        self.vel.x = 2 if dx > 0 else -2
        self.vel.y = math.sin(self.ai_timer * 5) * 3

    def _balrog_ai(self, dt: float, player: Player):
        # Chase player aggressively
        if self.action_cooldown <= 0:
            dx = player.pos.x - self.pos.x
            if abs(dx) > 50:
                self.vel.x = 3 if dx > 0 else -3
            
            # Jump if player is above
            if player.pos.y < self.pos.y - 50 and self.grounded:
                self.vel.y = -12
                self.action_cooldown = 2
        
        self.action_cooldown = max(0, self.action_cooldown - dt)

    def _gaudi_ai(self, dt: float, player: Player):
        # Patrol and shoot projectiles
        if self.grounded:
            self.vel.x = self.patrol_direction * 2
        
        # Change direction at random
        if random.random() < 0.01:
            self.patrol_direction *= -1

    def drop_items(self) -> List['ExperienceOrb']:
        items = []
        # Drop experience orbs
        exp_amount = self.star_points_value * 5
        for _ in range(random.randint(1, 3)):
            items.append(ExperienceOrb(
                self.pos.x + random.randint(-20, 20),
                self.pos.y,
                exp_amount // 3
            ))
        
        # Chance to drop heart
        if random.random() < 0.2:
            items.append(Heart(self.pos.x, self.pos.y - 10))
        
        return items

# ----- Items & Pickups -----
class ExperienceOrb(Entity):
    def __init__(self, x: float, y: float, value: int):
        size = 8 if value < 10 else 12 if value < 20 else 16
        super().__init__(x, y, size, size, EntityType.EXPERIENCE)
        self.value = value
        self.color = YELLOW if value < 10 else ORANGE if value < 20 else RED
        self.vel.y = -random.uniform(3, 6)
        self.vel.x = random.uniform(-2, 2)
        self.bounce_count = 0
        self.lifetime = 10

    def update(self, dt: float):
        super().update(dt)
        self.lifetime -= dt
        
        if self.lifetime <= 0:
            self.alive = False
        
        # Fade effect
        if self.lifetime < 3:
            self.is_flipped = int(self.lifetime * 10) % 2 == 0

class Heart(Entity):
    def __init__(self, x: float, y: float, heal_amount: int = 20):
        super().__init__(x, y, 16, 16, EntityType.HEART)
        self.heal_amount = heal_amount
        self.color = RED
        self.float_timer = 0

    def update(self, dt: float):
        # Float up and down
        self.float_timer += dt
        self.pos.y = self.pos.y + math.sin(self.float_timer * 3) * 0.5

    def draw(self, surf: pygame.Surface, cam_x: float, cam_y: float):
        # Draw heart shape
        x, y = self.pos.x - cam_x, self.pos.y - cam_y
        
        # Simple heart using circles and triangle
        pygame.draw.circle(surf, self.color, (int(x + 4), int(y + 4)), 4)
        pygame.draw.circle(surf, self.color, (int(x + 12), int(y + 4)), 4)
        pygame.draw.polygon(surf, self.color, [
            (x + 8, y + 12),
            (x, y + 4),
            (x + 16, y + 4)
        ])

# ----- Battle System -----
class BattleSystem:
    def __init__(self, player: Player, enemy: Enemy):
        self.player = player
        self.enemy = enemy
        self.state = "player_turn"
        self.action_timer = 0
        self.selected_action = BattleAction.JUMP
        self.action_command_window = 0
        self.action_command_success = False
        self.damage_numbers: List[Dict] = []
        self.turn_count = 0

    def update(self, dt: float) -> Optional[str]:
        self.action_timer += dt
        
        # Update damage numbers
        for num in list(self.damage_numbers):
            num['lifetime'] -= dt
            num['y'] -= dt * 50
            if num['lifetime'] <= 0:
                self.damage_numbers.remove(num)
        
        # Handle states
        if self.state == "player_action":
            if self.action_timer > 0.5:  # Action command window
                self.execute_player_action()
                self.state = "enemy_turn"
                self.action_timer = 0
        
        elif self.state == "enemy_turn":
            if self.action_timer > 1:
                self.execute_enemy_action()
                self.state = "player_turn"
                self.action_timer = 0
                self.turn_count += 1
        
        # Check battle end
        if self.enemy.hp <= 0:
            return "victory"
        elif self.player.hp <= 0:
            return "defeat"
        
        return None

    def execute_player_action(self):
        base_damage = 0
        
        if self.selected_action == BattleAction.JUMP:
            base_damage = 5 + self.player.level * 2
            if self.action_command_success:
                base_damage = int(base_damage * 1.5)
        
        elif self.selected_action == BattleAction.HAMMER:
            base_damage = 8 + self.player.level * 3
            if self.action_command_success:
                base_damage = int(base_damage * 1.5)
        
        elif self.selected_action == BattleAction.SPECIAL:
            if self.player.fp >= 3:
                base_damage = 15 + self.player.level * 4
                self.player.fp -= 3
        
        self.enemy.damage(base_damage)
        self.add_damage_number(self.enemy.pos.x, self.enemy.pos.y, base_damage)

    def execute_enemy_action(self):
        damage = random.randint(3, 8)
        self.player.damage(damage)
        self.add_damage_number(self.player.pos.x, self.player.pos.y, damage)

    def add_damage_number(self, x: float, y: float, damage: int):
        self.damage_numbers.append({
            'x': x,
            'y': y,
            'damage': damage,
            'lifetime': 1.0
        })

    def handle_input(self, key):
        if self.state == "player_turn":
            if key == pygame.K_1:
                self.selected_action = BattleAction.JUMP
            elif key == pygame.K_2:
                self.selected_action = BattleAction.HAMMER
            elif key == pygame.K_3:
                self.selected_action = BattleAction.SPECIAL
            elif key == pygame.K_SPACE:
                self.state = "player_action"
                self.action_timer = 0
        
        elif self.state == "player_action":
            # Action command
            if 0.3 < self.action_timer < 0.7:
                self.action_command_success = True

# ----- Dialogue System -----
class DialogueSystem:
    def __init__(self):
        self.messages: List[str] = []
        self.current_message = 0
        self.char_index = 0
        self.char_timer = 0
        self.speaker = ""
        self.active = False
        self.font = pygame.font.Font(None, 24)

    def start_dialogue(self, speaker: str, messages: List[str]):
        self.speaker = speaker
        self.messages = messages
        self.current_message = 0
        self.char_index = 0
        self.char_timer = 0
        self.active = True

    def update(self, dt: float):
        if not self.active:
            return
        
        # Type out characters
        self.char_timer += dt
        if self.char_timer > 0.03:
            if self.char_index < len(self.messages[self.current_message]):
                self.char_index += 1
                self.char_timer = 0

    def handle_input(self, key):
        if not self.active:
            return
        
        if key == pygame.K_SPACE:
            if self.char_index < len(self.messages[self.current_message]):
                # Show full message
                self.char_index = len(self.messages[self.current_message])
            else:
                # Next message
                self.current_message += 1
                if self.current_message >= len(self.messages):
                    self.active = False
                else:
                    self.char_index = 0

    def draw(self, surf: pygame.Surface):
        if not self.active:
            return
        
        # Dialogue box
        box_rect = pygame.Rect(50, SCREEN_HEIGHT - 150, SCREEN_WIDTH - 100, 120)
        pygame.draw.rect(surf, BLACK, box_rect)
        pygame.draw.rect(surf, WHITE, box_rect, 3)
        
        # Speaker name
        if self.speaker:
            name_surf = self.font.render(self.speaker, True, YELLOW)
            surf.blit(name_surf, (box_rect.x + 20, box_rect.y + 10))
        
        # Message text
        current_text = self.messages[self.current_message][:self.char_index]
        y_offset = 40
        
        # Word wrap
        words = current_text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.font.size(test_line)[0] > box_rect.width - 40:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
            else:
                current_line.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for line in lines:
            text_surf = self.font.render(line, True, WHITE)
            surf.blit(text_surf, (box_rect.x + 20, box_rect.y + y_offset))
            y_offset += 25

# ----- Camera -----
class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0

    def update(self, target_x: float, target_y: float, level_width: int = 2000, level_height: int = 1200):
        # Set target
        self.target_x = max(0, min(target_x - SCREEN_WIDTH // 2, level_width - SCREEN_WIDTH))
        self.target_y = max(0, min(target_y - SCREEN_HEIGHT // 2, level_height - SCREEN_HEIGHT))
        
        # Smooth camera movement
        self.x += (self.target_x - self.x) * 0.1
        self.y += (self.target_y - self.y) * 0.1
        
        self.x = round(self.x)
        self.y = round(self.y)

# ----- HUD -----
class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 28)

    def draw_overworld(self, surf: pygame.Surface, player: Player):
        # HP Bar
        self._draw_bar(surf, 20, 20, 200, 16, player.hp, player.max_hp, RED, "HP")
        
        # FP Bar
        self._draw_bar(surf, 20, 40, 150, 12, player.fp, player.max_fp, BLUE, "FP")
        
        # Boost Bar
        self._draw_bar(surf, 20, 58, 150, 10, player.boost_fuel, 100, ORANGE, "BOOST")
        
        # Level & Star Points
        level_text = self.big_font.render(f"LV {player.level}", True, YELLOW)
        surf.blit(level_text, (20, 80))
        
        sp_text = self.font.render(f"SP: {player.star_points}/{player.star_points_to_level}", True, WHITE)
        surf.blit(sp_text, (20, 110))
        
        # Current Weapon
        weapon = player.current_weapon
        weapon_text = self.font.render(f"{weapon.name} L{weapon.level}", True, YELLOW)
        surf.blit(weapon_text, (SCREEN_WIDTH - 150, 20))
        
        if weapon.max_ammo > 0:
            ammo_text = self.font.render(f"Ammo: {weapon.ammo}/{weapon.max_ammo}", True, WHITE)
            surf.blit(ammo_text, (SCREEN_WIDTH - 150, 40))
        
        # Weapon EXP
        if weapon.level < 3:
            exp_needed = weapon.exp_required[weapon.level - 1]
            self._draw_bar(surf, SCREEN_WIDTH - 150, 60, 120, 8, 
                          weapon.exp, exp_needed, GREEN, "")
        
        # Coins
        coin_text = self.font.render(f"Coins: {player.coins}", True, YELLOW)
        surf.blit(coin_text, (SCREEN_WIDTH - 150, 80))
        
        # Partner
        if player.partners:
            partner = player.partners[player.current_partner_idx]
            partner_text = self.font.render(f"Partner: {partner.name}", True, WHITE)
            surf.blit(partner_text, (20, 140))

    def draw_battle(self, surf: pygame.Surface, battle: BattleSystem):
        # Player HP/FP
        self._draw_bar(surf, 50, 50, 150, 20, 
                      battle.player.hp, battle.player.max_hp, RED, "HP")
        self._draw_bar(surf, 50, 75, 120, 16, 
                      battle.player.fp, battle.player.max_fp, BLUE, "FP")
        
        # Enemy HP
        self._draw_bar(surf, SCREEN_WIDTH - 200, 50, 150, 20,
                      battle.enemy.hp, battle.enemy.max_hp, RED, 
                      battle.enemy.enemy_type)
        
        # Action menu
        if battle.state == "player_turn":
            menu_rect = pygame.Rect(50, SCREEN_HEIGHT - 200, 200, 150)
            pygame.draw.rect(surf, BLACK, menu_rect)
            pygame.draw.rect(surf, WHITE, menu_rect, 3)
            
            actions = ["1. Jump", "2. Hammer", "3. Special", "4. Item"]
            for i, action in enumerate(actions):
                color = YELLOW if i == battle.selected_action.value - 1 else WHITE
                text = self.font.render(action, True, color)
                surf.blit(text, (menu_rect.x + 20, menu_rect.y + 20 + i * 30))
        
        # Action command indicator
        elif battle.state == "player_action":
            if 0.3 < battle.action_timer < 0.7:
                text = self.big_font.render("PRESS SPACE!", True, YELLOW)
                rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                surf.blit(text, rect)
        
        # Damage numbers
        for num in battle.damage_numbers:
            text = self.big_font.render(str(num['damage']), True, RED)
            surf.blit(text, (num['x'], num['y']))

    def _draw_bar(self, surf: pygame.Surface, x: int, y: int, width: int, height: int,
                  current: float, maximum: float, color: Tuple, label: str):
        # Background
        back_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surf, DARK_GRAY, back_rect)
        
        # Foreground
        if maximum > 0:
            fg_width = int(width * (current / maximum))
            fg_rect = pygame.Rect(x, y, fg_width, height)
            pygame.draw.rect(surf, color, fg_rect)
        
        # Border
        pygame.draw.rect(surf, WHITE, back_rect, 2)
        
        # Label
        if label:
            text = self.font.render(f"{label} {int(current)}/{int(maximum)}", True, WHITE)
            surf.blit(text, (x + width + 10, y))

# ----- Main Game Class -----
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cave Story X Paper Mario")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = GameState.OVERWORLD
        self.running = True
        
        # Core systems
        self.player = Player(100, 300)
        self.camera = Camera()
        self.hud = HUD()
        self.dialogue = DialogueSystem()
        self.battle_system: Optional[BattleSystem] = None
        
        # Level entities
        self.platforms: List[Entity] = []
        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []
        self.items: List[Entity] = []
        self.npcs: List[Entity] = []
        
        # Initialize level
        self._create_level()
        
        # Add starting partner
        goombella = Partner("Goombella", 30, 30, ["Tattle", "Headbonk"], 
                           PINK, Vector2(50, 300))
        self.player.partners.append(goombella)

    def _create_level(self):
        # Platforms
        platform_data = [
            (0, 500, 400, 20),
            (450, 450, 200, 20),
            (700, 400, 300, 20),
            (200, 350, 150, 20),
            (400, 300, 100, 20),
            (600, 250, 200, 20),
            (900, 350, 200, 20),
            (0, 580, 1200, 20),  # Ground
            
            # Vertical platforms
            (300, 200, 20, 300),
            (600, 100, 20, 200),
            (1000, 200, 20, 300)
        ]
        
        for x, y, w, h in platform_data:
            plat = Entity(x, y, w, h, EntityType.PLATFORM)
            plat.color = BROWN
            self.platforms.append(plat)
        
        # Enemies
        enemy_spawns = [
            (400, 250, "Critter"),
            (600, 200, "Bat"),
            (800, 350, "Critter"),
            (900, 300, "Gaudi"),
            (1100, 300, "Balrog")
        ]
        
        for x, y, etype in enemy_spawns:
            self.enemies.append(Enemy(x, y, etype))
        
        # Save point
        save_point = Entity(150, 460, 32, 40, EntityType.SAVE_POINT)
        save_point.color = GREEN
        self.npcs.append(save_point)
        
        # NPCs
        npc = Entity(500, 260, 24, 32, EntityType.NPC)
        npc.color = PURPLE
        npc.name = "Curly"
        self.npcs.append(npc)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
            pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.OVERWORLD:
                    self._handle_overworld_input(event.key)
                elif self.state == GameState.DIALOGUE:
                    self.dialogue.handle_input(event.key)
                elif self.state == GameState.BATTLE:
                    if self.battle_system:
                        self.battle_system.handle_input(event.key)

    def _handle_overworld_input(self, key):
        # Weapon switching
        if key == pygame.K_q:
            self.player.switch_weapon(-1)
        elif key == pygame.K_e:
            self.player.switch_weapon(1)
        
        # Paper flip
        elif key == pygame.K_f:
            self.player.paper_flip_timer = 0.5
        
        # Interact
        elif key == pygame.K_x:
            self._check_interactions()

    def _check_interactions(self):
        # Check NPC interactions
        player_rect = self.player.get_rect()
        
        for npc in self.npcs:
            if player_rect.colliderect(npc.get_rect().inflate(20, 20)):
                if npc.type == EntityType.SAVE_POINT:
                    self.player.hp = self.player.max_hp
                    self.player.fp = self.player.max_fp
                    self.dialogue.start_dialogue("Save Point", 
                        ["Your game has been saved!", 
                         "HP and FP restored!"])
                    self.state = GameState.DIALOGUE
                elif npc.type == EntityType.NPC:
                    self.dialogue.start_dialogue(getattr(npc, 'name', 'NPC'),
                        ["Hello! I'm Curly Brace!", 
                         "Be careful of the enemies ahead!",
                         "Press K to shoot your weapon!"])
                    self.state = GameState.DIALOGUE

    def update(self, dt: float):
        if self.state == GameState.OVERWORLD:
            self._update_overworld(dt)
        
        elif self.state == GameState.DIALOGUE:
            self.dialogue.update(dt)
            if not self.dialogue.active:
                self.state = GameState.OVERWORLD
        
        elif self.state == GameState.BATTLE:
            if self.battle_system:
                result = self.battle_system.update(dt)
                if result == "victory":
                    # Give rewards
                    self.player.add_star_points(self.battle_system.enemy.star_points_value)
                    self.player.coins += random.randint(5, 15)
                    
                    # Drop items at enemy position
                    for item in self.battle_system.enemy.drop_items():
                        self.items.append(item)
                    
                    # Remove enemy
                    if self.battle_system.enemy in self.enemies:
                        self.enemies.remove(self.battle_system.enemy)
                    
                    self.battle_system = None
                    self.state = GameState.OVERWORLD
                
                elif result == "defeat":
                    self.state = GameState.GAME_OVER

    def _update_overworld(self, dt: float):
        # Handle input
        keys = pygame.key.get_pressed()
        
        # Movement
        self.player.vel.x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vel.x = -MOVE_SPEED
            self.player.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vel.x = MOVE_SPEED
            self.player.facing_right = True
        
        # Jumping
        if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and self.player.can_jump:
            self.player.vel.y = JUMP_POWER
            self.player.can_jump = False
        
        # Boost
        if keys[pygame.K_LSHIFT] and self.player.boost_fuel > 0:
            self.player.vel.y = -BOOST_SPEED
            self.player.boost_fuel -= 50 * dt
        
        # Shooting
        if keys[pygame.K_k]:
            proj_x = self.player.pos.x + (self.player.width if self.player.facing_right else 0)
            proj_y = self.player.pos.y + self.player.height // 2
            direction = 1 if self.player.facing_right else -1
            
            proj = self.player.current_weapon.fire(proj_x, proj_y, direction)
            if proj:
                self.projectiles.append(proj)
        
        # Update entities
        self.player.update(dt)
        self._handle_collisions()
        
        # Update partners
        for partner in self.player.partners:
            partner.update(self.player.pos, dt)
        
        # Update enemies
        for enemy in list(self.enemies):
            enemy.update(dt, self.player, self.platforms)
            
            # Check enemy collision with player (start battle)
            if enemy.get_rect().colliderect(self.player.get_rect()):
                if self.player.inv_timer <= 0 and not self.player.paper_mode:
                    self.battle_system = BattleSystem(self.player, enemy)
                    self.state = GameState.BATTLE
        
        # Update projectiles
        for proj in list(self.projectiles):
            proj.update(dt)
            
            if not proj.alive:
                self.projectiles.remove(proj)
                continue
            
            # Check projectile-enemy collision
            for enemy in self.enemies:
                if proj.get_rect().colliderect(enemy.get_rect()):
                    enemy.damage(proj.damage)
                    proj.alive = False
                    
                    # Add weapon experience
                    self.player.current_weapon.add_exp(5)
                    
                    # Drop items if enemy dies
                    if not enemy.alive:
                        for item in enemy.drop_items():
                            self.items.append(item)
                        self.enemies.remove(enemy)
                        self.player.add_star_points(enemy.star_points_value)
            
            # Check projectile-platform collision
            for plat in self.platforms:
                if proj.get_rect().colliderect(plat.get_rect()):
                    proj.alive = False
        
        # Update items
        for item in list(self.items):
            item.update(dt)
            
            if not item.alive:
                self.items.remove(item)
                continue
            
            # Check item pickup
            if item.get_rect().colliderect(self.player.get_rect()):
                if item.type == EntityType.EXPERIENCE:
                    self.player.current_weapon.add_exp(item.value)
                    self.items.remove(item)
                elif item.type == EntityType.HEART:
                    self.player.hp = min(self.player.max_hp, 
                                       self.player.hp + item.heal_amount)
                    self.items.remove(item)
        
        # Update camera
        self.camera.update(self.player.pos.x, self.player.pos.y)

    def _handle_collisions(self):
        # Reset grounded state
        self.player.grounded = False
        self.player.can_jump = False
        
        # Player-platform collision
        player_rect = self.player.get_rect()
        
        for platform in self.platforms:
            plat_rect = platform.get_rect()
            
            # Check if we're colliding
            if player_rect.colliderect(plat_rect):
                # Vertical collision (landing on platform)
                if self.player.old_pos.y + self.player.height <= platform.pos.y + 10:
                    self.player.pos.y = platform.pos.y - self.player.height
                    self.player.vel.y = 0
                    self.player.grounded = True
                    self.player.can_jump = True
                
                # Horizontal collision
                elif self.player.old_pos.x + self.player.width <= platform.pos.x:
                    self.player.pos.x = platform.pos.x - self.player.width
                elif self.player.old_pos.x >= platform.pos.x + platform.width:
                    self.player.pos.x = platform.pos.x + platform.width
        
        # Enemy-platform collision
        for enemy in self.enemies:
            enemy.grounded = False
            enemy_rect = enemy.get_rect()
            
            for platform in self.platforms:
                if enemy_rect.colliderect(platform.get_rect()):
                    if enemy.old_pos.y + enemy.height <= platform.pos.y + 10:
                        enemy.pos.y = platform.pos.y - enemy.height
                        enemy.vel.y = 0
                        enemy.grounded = True

    def draw(self):
        # Background
        self.screen.fill(BLACK)
        
        # Gradient sky
        for i in range(0, SCREEN_HEIGHT, 2):
            color_val = max(0, 60 - i // 10)
            pygame.draw.line(self.screen, (color_val, color_val, color_val + 20),
                           (0, i), (SCREEN_WIDTH, i))
        
        # Draw all entities
        for platform in self.platforms:
            platform.draw(self.screen, self.camera.x, self.camera.y)
        
        for npc in self.npcs:
            npc.draw(self.screen, self.camera.x, self.camera.y)
        
        for item in self.items:
            item.draw(self.screen, self.camera.x, self.camera.y)
        
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera.x, self.camera.y)
        
        for proj in self.projectiles:
            proj.draw(self.screen, self.camera.x, self.camera.y)
        
        self.player.draw(self.screen, self.camera.x, self.camera.y)
        
        # Draw HUD based on state
        if self.state == GameState.OVERWORLD:
            self.hud.draw_overworld(self.screen, self.player)
        elif self.state == GameState.BATTLE and self.battle_system:
            self.hud.draw_battle(self.screen, self.battle_system)
        
        # Draw dialogue
        if self.state == GameState.DIALOGUE:
            self.dialogue.draw(self.screen)
        
        # Game over screen
        if self.state == GameState.GAME_OVER:
            font = pygame.font.Font(None, 72)
            text = font.render("GAME OVER", True, RED)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, rect)

# ----- Main Entry Point -----
def main():
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
